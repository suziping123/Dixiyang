    /*
    * @Author: suziping123 yunzhiming123@gmail.com
    * @Date: 2026-03-17 22:24:29
    * @LastEditors: suziping123 yunzhiming123@gmail.com
    * @LastEditTime: 2026-03-23 20:59:51
    * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Controller\ChatController.java
    * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
    */
package com.dixiyang.server.Controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.document.Document;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import io.swagger.v3.oas.annotations.tags.Tag;
import com.dixiyang.server.Service.EmbeddingService;
import com.dixiyang.server.Service.INovelCharacterService;
import com.dixiyang.server.Service.IChatSessionService;
import com.dixiyang.server.Service.IStoryNodeService;
import com.dixiyang.server.Entity.NovelCharacter;
import com.dixiyang.server.Entity.StoryNode;
import com.dixiyang.server.Entity.dto.ChatRequest;

import reactor.core.publisher.Flux;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicReference;

    /**
     * AI 聊天控制器
     * 基于 RAG (检索增强生成) 实现与大语言模型的对话
     * 流程：用户提问 -> 向量检索相关上下文 -> 结合上下文提问 AI
     */
    @Tag(name = "聊天模块")
    @RestController
    @Slf4j
    public class ChatController {
        
        private final ChatClient chatClient;
        private final EmbeddingService embeddingService;
        private final INovelCharacterService characterService;
        private final IStoryNodeService storyNodeService;
        private final IChatSessionService chatSessionService;
        private final boolean ragEnabled;
        private final ObjectMapper objectMapper = new ObjectMapper();

        private String toJson(Map<String, Object> map) {
            try { return objectMapper.writeValueAsString(map); }
            catch (JsonProcessingException e) { return "{}"; }
        }

        // 注入所需依赖（EmbeddingService 为可选）
        public ChatController(ChatClient.Builder builder, 
                            @Autowired(required = false) EmbeddingService embeddingService,
                            INovelCharacterService characterService,
                            IStoryNodeService storyNodeService,
                            IChatSessionService chatSessionService) {
            this.chatClient = builder.build();
            this.embeddingService = embeddingService;
            this.characterService = characterService;
            this.storyNodeService = storyNodeService;
            this.chatSessionService = chatSessionService;
            this.ragEnabled = (embeddingService != null);
            if (!ragEnabled) {
                log.warn("⚠️ RAG 功能已禁用（向量存储未配置），仅使用数据库上下文");
            }
        }

        /**
         * RAG 聊天接口（GET 方式，适用于短文本）
         * @param message 用户提问
         * @param useRag 是否启用 RAG 检索（默认 true）
         * @return AI 回答
         */
        @GetMapping("/chat")
        public String chatGet(@RequestParam String message,
                            @RequestParam(defaultValue = "true") boolean useRag) {
            return processChat(message, useRag);
        }

        /**
         * RAG 聊天接口（POST 方式，推荐使用 - 支持传 ID 从数据库构建上下文）
         * @param request 聊天请求，可包含：message、useRag、characterIds、storyNodeIds 等
         * @return AI 回答
         */
        @PostMapping("/chat")
        public String chatPost(@RequestBody ChatRequest request) {
            return processChat(request);
        }

        private static final String THINKING_START = "<thinking>";
        private static final String THINKING_END = "</thinking>";

        private void sendEvent(SseEmitter emitter, String type, String delta) {
            try {
                Map<String, Object> evt = new HashMap<>();
                evt.put("type", type);
                if (delta != null) evt.put("delta", delta);
                emitter.send(SseEmitter.event().name("message").data(toJson(evt)));
            } catch (Exception ignored) {}
        }

        /**
         * RAG 流式聊天接口 (SSE) — 真流式
         * 使用 ChatClient.stream() 获得 Flux<String>，逐 token 推 SSE
         * 实时检测 <thinking> 标签，拆分 thinking/content 两路事件
         */
        @PostMapping(value = "/chat/stream")
        public SseEmitter chatStream(@RequestBody ChatRequest request) {
            SseEmitter emitter = new SseEmitter(1800000L);
            ExecutorService executor = Executors.newSingleThreadExecutor();

            executor.execute(() -> {
                try {
                    String fullPrompt = buildFullPrompt(request);

                    // 真流式：Flux<String> 逐 token 推送
                    Flux<String> flux = chatClient.prompt(fullPrompt).stream().content();
                    CountDownLatch latch = new CountDownLatch(1);

                    StringBuilder buf = new StringBuilder();
                    AtomicReference<String> state = new AtomicReference<>("INIT");

                    flux.subscribe(
                        token -> {
                            buf.append(token);
                            String cur = state.get();

                            // --- INIT: 检测 <thinking> 开始 ---
                            if ("INIT".equals(cur)) {
                                String s = buf.toString();
                                int startTagIdx = s.indexOf(THINKING_START);
                                if (startTagIdx >= 0) {
                                    String beforeTag = s.substring(0, startTagIdx);
                                    if (!beforeTag.isEmpty()) sendEvent(emitter, "content", beforeTag);
                                    buf.setLength(0);
                                    buf.append(s.substring(startTagIdx + THINKING_START.length()));
                                    state.set("THINKING");
                                } else if (s.length() > 64) {
                                    // 积累够了还没出现 thinking 标签，当作纯内容
                                    sendEvent(emitter, "content", s);
                                    buf.setLength(0);
                                    state.set("CONTENT");
                                }
                            }

                            // --- THINKING: 检测 </thinking> 结束，推送 thinking 事件 ---
                            if ("THINKING".equals(state.get())) {
                                String s = buf.toString();
                                int endTagIdx = s.indexOf(THINKING_END);
                                if (endTagIdx >= 0) {
                                    String think = s.substring(0, endTagIdx);
                                    if (!think.isEmpty()) sendEvent(emitter, "thinking", think);
                                    buf.setLength(0);
                                    buf.append(s.substring(endTagIdx + THINKING_END.length()));
                                    state.set("CONTENT");
                                } else if (s.length() > THINKING_END.length()) {
                                    // 安全推送：保留末尾可能匹配标签的字符
                                    String safe = s.substring(0, s.length() - THINKING_END.length());
                                    if (!safe.isEmpty()) {
                                        sendEvent(emitter, "thinking", safe);
                                        buf.setLength(0);
                                        buf.append(s.substring(s.length() - THINKING_END.length()));
                                    }
                                }
                            }

                            // --- CONTENT: 直接推送 content 事件 ---
                            if ("CONTENT".equals(state.get()) && buf.length() > 0) {
                                sendEvent(emitter, "content", buf.toString());
                                buf.setLength(0);
                            }
                        },
                        error -> {
                            log.error("AI 流式调用失败: {}", error.getMessage());
                            sendEvent(emitter, "error", "AI 调用失败: " + error.getMessage());
                            sendEvent(emitter, "done", null);
                            try { emitter.complete(); } catch (Exception ignored) {}
                            latch.countDown();
                        },
                        () -> {
                            String remaining = buf.toString();
                            if (!remaining.isEmpty()) {
                                String cur = state.get();
                                sendEvent(emitter, "THINKING".equals(cur) ? "thinking" : "content", remaining);
                            }
                            sendEvent(emitter, "done", null);
                            try { emitter.complete(); } catch (Exception ignored) {}
                            latch.countDown();
                        }
                    );

                    latch.await();

                } catch (Exception e) {
                    log.error("流式聊天异常: {}", e.getMessage(), e);
                    sendEvent(emitter, "error", "流式聊天异常: " + e.getMessage());
                    try { emitter.complete(); } catch (Exception ignored) {}
                } finally {
                    executor.shutdown();
                }
            });

            return emitter;
        }

        private String buildFullPrompt(ChatRequest request) {
            String dbContext = buildContextFromDatabase(request);
            String finalMessage = request.getMessage();
            String fullPrompt = finalMessage;

            if (dbContext != null && !dbContext.isEmpty()) {
                fullPrompt = dbContext + "\n\n用户需求：" + finalMessage;
            }

            if (ragEnabled && request.getUseRag() != null && request.getUseRag()) {
                try {
                    List<Document> relatedDocs = embeddingService.similaritySearch(finalMessage);
                    if (!relatedDocs.isEmpty()) {
                        String ragContext = relatedDocs.stream()
                                .map(Document::getText)
                                .collect(Collectors.joining("\n---\n"));
                        fullPrompt = String.format(
                                "【参考资料】\n%s\n\n%s\n\n用户需求：%s\n\n请基于以上信息回答用户的问题。如果参考资料与问题相关，请重点参考；如不相关，可忽略。",
                                ragContext, dbContext, finalMessage
                        );
                    }
                } catch (Exception e) {
                    log.error("RAG 检索失败: {}", e.getMessage(), e);
                }
            }

            String sessionId = request.getSessionId();
            if (sessionId != null && !sessionId.isBlank()) {
                try {
                    Authentication auth = SecurityContextHolder.getContext().getAuthentication();
                    if (auth != null && auth.getPrincipal() != null) {
                        Long uid = Long.parseLong(auth.getPrincipal().toString());
                        String editsPrompt = chatSessionService.buildEditContextPrompt(uid, sessionId);
                        if (!editsPrompt.isBlank()) {
                            fullPrompt = fullPrompt + "\n\n" + editsPrompt;
                        }
                    }
                } catch (Exception e) {
                    log.warn("注入编辑上下文失败: {}", e.getMessage());
                }
            }

            return fullPrompt;
        }

        /**
         * 重新生成指定消息（SSE 真流式）
         * 截断链 → 构建上下文 → Flux 逐 token 推 SSE → 完成时追加新回答
         */
        @PostMapping(value = "/chat/regenerate")
        public SseEmitter regenerate(@RequestBody ChatRequest request) {
            SseEmitter emitter = new SseEmitter(1800000L);

            Long userId = getUserIdFromAuth();
            if (userId == null) {
                sendEvent(emitter, "error", "未登录");
                try { emitter.complete(); } catch (Exception ignored) {}
                return emitter;
            }

            String sessionId = request.getSessionId();
            int messageIndex = request.getRegenerateIndex() != null ? request.getRegenerateIndex() : -1;
            if (sessionId == null || sessionId.isBlank() || messageIndex < 0) {
                sendEvent(emitter, "error", "参数不完整：需要 sessionId 和 regenerateIndex");
                try { emitter.complete(); } catch (Exception ignored) {}
                return emitter;
            }

            Long finalUserId = userId;
            ExecutorService executor = Executors.newSingleThreadExecutor();

            executor.execute(() -> {
                try {
                    // 1. 截断链
                    chatSessionService.truncateSessionChain(finalUserId, sessionId, messageIndex);

                    // 2. 构建上下文
                    List<Map<String, Object>> history = chatSessionService.getSessionMessages(sessionId, finalUserId);
                    StringBuilder ctx = new StringBuilder();
                    if (history != null) {
                        for (Map<String, Object> msg : history) {
                            String role = "user".equals(msg.get("role")) ? "用户" : "AI";
                            String content = (String) msg.get("content");
                            if (content != null) ctx.append(role).append("：").append(content).append("\n\n");
                        }
                    }

                    String editsPrompt = chatSessionService.buildEditContextPrompt(finalUserId, sessionId);
                    if (!editsPrompt.isBlank()) ctx.append(editsPrompt).append("\n\n");

                    String dbContext = buildContextFromDatabase(request);
                    String finalMessage = request.getMessage();
                    String fullPrompt = ctx + "用户需求：" + (finalMessage != null ? finalMessage : "");

                    if (dbContext != null && !dbContext.isEmpty()) {
                        fullPrompt = dbContext + "\n\n" + fullPrompt;
                    }

                    if (ragEnabled && request.getUseRag() != null && request.getUseRag()) {
                        try {
                            List<Document> relatedDocs = embeddingService.similaritySearch(finalMessage != null ? finalMessage : "");
                            if (!relatedDocs.isEmpty()) {
                                String rag = relatedDocs.stream().map(Document::getText).collect(Collectors.joining("\n---\n"));
                                fullPrompt = String.format("【参考资料】\n%s\n\n%s\n\n用户需求：%s", rag, dbContext, finalMessage);
                            }
                        } catch (Exception e) { log.error("RAG 失败: {}", e.getMessage()); }
                    }

                    // 3. 真流式调用 AI
                    Flux<String> flux = chatClient.prompt(fullPrompt).stream().content();
                    CountDownLatch latch = new CountDownLatch(1);

                    StringBuilder buf = new StringBuilder();
                    AtomicReference<String> state = new AtomicReference<>("INIT");
                    StringBuilder fullResponse = new StringBuilder();

                    flux.subscribe(
                        token -> {
                            fullResponse.append(token);
                            buf.append(token);
                            String cur = state.get();

                            if ("INIT".equals(cur)) {
                                String s = buf.toString();
                                int idx = s.indexOf(THINKING_START);
                                if (idx >= 0) {
                                    String before = s.substring(0, idx);
                                    if (!before.isEmpty()) sendEvent(emitter, "content", before);
                                    buf.setLength(0);
                                    buf.append(s.substring(idx + THINKING_START.length()));
                                    state.set("THINKING");
                                } else if (s.length() > 64) {
                                    sendEvent(emitter, "content", s);
                                    buf.setLength(0);
                                    state.set("CONTENT");
                                }
                            }

                            if ("THINKING".equals(state.get())) {
                                String s = buf.toString();
                                int idx = s.indexOf(THINKING_END);
                                if (idx >= 0) {
                                    String think = s.substring(0, idx);
                                    if (!think.isEmpty()) sendEvent(emitter, "thinking", think);
                                    buf.setLength(0);
                                    buf.append(s.substring(idx + THINKING_END.length()));
                                    state.set("CONTENT");
                                } else if (s.length() > THINKING_END.length()) {
                                    String safe = s.substring(0, s.length() - THINKING_END.length());
                                    if (!safe.isEmpty()) {
                                        sendEvent(emitter, "thinking", safe);
                                        buf.setLength(0);
                                        buf.append(s.substring(s.length() - THINKING_END.length()));
                                    }
                                }
                            }

                            if ("CONTENT".equals(state.get()) && buf.length() > 0) {
                                sendEvent(emitter, "content", buf.toString());
                                buf.setLength(0);
                            }
                        },
                        error -> {
                            sendEvent(emitter, "error", "AI 调用失败: " + error.getMessage());
                            sendEvent(emitter, "done", null);
                            try { emitter.complete(); } catch (Exception ignored) {}
                            latch.countDown();
                        },
                        () -> {
                            String remaining = buf.toString();
                            if (!remaining.isEmpty()) {
                                sendEvent(emitter, "THINKING".equals(state.get()) ? "thinking" : "content", remaining);
                            }
                            sendEvent(emitter, "done", null);
                            try { emitter.complete(); } catch (Exception ignored) {}

                            // 4. 保存新回答到链
                            String clean = fullResponse.toString()
                                .replace(THINKING_START, "").replace(THINKING_END, "");
                            List<Map<String, Object>> msgs = new ArrayList<>();
                            Map<String, Object> m = new LinkedHashMap<>();
                            m.put("role", "assistant"); m.put("content", clean);
                            m.put("createTime", LocalDateTime.now().toString());
                            msgs.add(m);
                            chatSessionService.appendMessages(finalUserId, request.getNovelId(), sessionId, msgs);

                            latch.countDown();
                        }
                    );

                    latch.await();
                } catch (Exception e) {
                    log.error("重新生成异常: {}", e.getMessage(), e);
                    sendEvent(emitter, "error", "重新生成失败: " + e.getMessage());
                    try { emitter.complete(); } catch (Exception ignored) {}
                } finally {
                    executor.shutdown();
                }
            });

            return emitter;
        }

        private Long getUserIdFromAuth() {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth == null || auth.getPrincipal() == null) return null;
            try { return Long.parseLong(auth.getPrincipal().toString()); }
            catch (NumberFormatException e) { return null; }
        }

        /**
         * 处理聊天请求的核心逻辑（新版本 DTO）
         */
        private String processChat(ChatRequest request) {
            // 1. 构建数据库上下文（根据 ID 查询获取完整数据）
            String dbContext = buildContextFromDatabase(request);
            
            // 2. 构建最终的 Prompt
            String finalMessage = request.getMessage();
            String fullPrompt = finalMessage;
            
            if (dbContext != null && !dbContext.isEmpty()) {
                fullPrompt = dbContext + "\n\n用户需求：" + finalMessage;
            }
            
            // 3. RAG 检索增强（可选）
            if (ragEnabled && request.getUseRag() != null && request.getUseRag()) {
                try {
                    List<Document> relatedDocs = embeddingService.similaritySearch(finalMessage);
                    
                    if (!relatedDocs.isEmpty()) {
                        String ragContext = relatedDocs.stream()
                                .map(Document::getText)
                                .collect(Collectors.joining("\n---\n"));
                        
                        fullPrompt = String.format(
                                "【参考资料】\n%s\n\n%s\n\n用户需求：%s\n\n请基于以上信息回答用户的问题。如果参考资料与问题相关，请重点参考；如不相关，可忽略。",
                                ragContext, dbContext, finalMessage
                        );
                    }
                } catch (Exception e) {
                    log.error("RAG 检索失败，仅使用数据库上下文: {}", e.getMessage(), e);
                    // 继续使用仅数据库上下文的模式
                }
            }
            
            // 4. 调用 AI 服务
            try {
                return chatClient.prompt(fullPrompt).call().content();
            } catch (Exception e) {
                System.out.println("AI 服务调用失败，返回模拟响应: " + e.getMessage());
                e.printStackTrace();
                return generateMockResponse(fullPrompt);
            }
        }

        /**
         * 从数据库构建上下文信息（推荐架构：前端传 ID，后端查数据）
         */
        private String buildContextFromDatabase(ChatRequest request) {
            StringBuilder context = new StringBuilder();
            
            // 包含角色信息
            if (request.getIncludeCharacters() != null && request.getIncludeCharacters() 
                    && request.getCharacterIds() != null && !request.getCharacterIds().isEmpty()) {
                List<NovelCharacter> characters = characterService.listByIds(request.getCharacterIds());
                
                if (!characters.isEmpty()) {
                    context.append("【角色信息】\n");
                    for (NovelCharacter charac : characters) {
                        context.append("- ").append(charac.getName());
                        context.append("（").append(charac.getGender() != null ? charac.getGender() : "性别未知");
                        context.append("，").append(charac.getAge() != null ? charac.getAge() + "岁" : "年龄未知").append("）:\n");
                        if (charac.getAppearance() != null) context.append("  * 外貌：").append(charac.getAppearance()).append("\n");
                        if (charac.getPersonality() != null) context.append("  * 性格：").append(charac.getPersonality()).append("\n");
                        if (charac.getBackground() != null) context.append("  * 背景：").append(charac.getBackground()).append("\n");
                    }
                    context.append("\n");
                }
            }
            
            // 包含故事节点
            if (request.getIncludeStory() != null && request.getIncludeStory() 
                    && request.getStoryNodeIds() != null && !request.getStoryNodeIds().isEmpty()) {
                List<StoryNode> nodes = storyNodeService.listByIds(request.getStoryNodeIds());
                
                if (!nodes.isEmpty()) {
                    context.append("【故事节点】\n");
                    for (StoryNode node : nodes) {
                        context.append("- ").append(node.getTitle()).append(":\n");
                        if (node.getContent() != null) context.append("  内容：").append(node.getContent()).append("\n");
                    }
                    context.append("\n");
                }
            }
            
            return context.toString();
        }

        /**
         * 兼容旧版接口：纯文本消息
         */
        private String processChat(String message, boolean useRag) {
            ChatRequest request = new ChatRequest();
            request.setMessage(message);
            request.setUseRag(useRag);
            return processChat(request);
        }

        /**
         * 生成模拟响应（用于 AI 服务不可用时的演示）
         */
        private String generateMockResponse(String message) {
            // 简单的角色分析模拟
            if (message.contains("分析") && (message.contains("性格") || message.contains("角色"))) {
                return "【模拟响应 - AI 服务暂时不可用】\n\n" +
                    "注：此为模拟响应，实际 AI 服务恢复后将提供更专业的分析。";
            }
            
            return "【模拟响应 - AI 服务暂时不可用】\n\n" +
                "系统已收到您的请求：\n「" + (message.length() > 100 ? message.substring(0, 100) + "..." : message) + "」\n\n" +
                "由于 AI 服务临时限制，无法提供实时回答。\n" +
                "请稍后重试，或检查系统配置。";
        }
    }