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
import com.dixiyang.server.Service.RagService;
import com.dixiyang.server.Service.INovelCharacterService;
import com.dixiyang.server.Service.IChatSessionService;
import com.dixiyang.server.Service.IStoryNodeService;
import com.dixiyang.server.Service.chat.pipeline.*;
import com.dixiyang.server.Service.chat.pipeline.IntentAnalyzer.IntentResult;
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
        private final RagService ragService;
        private final INovelCharacterService characterService;
        private final IStoryNodeService storyNodeService;
        private final IChatSessionService chatSessionService;
        private final IntentAnalyzer intentAnalyzer;
        private final PromptBuilder promptBuilder;
        private final List<Tool> tools;
        private final boolean ragEnabled;
        private final ObjectMapper objectMapper = new ObjectMapper();

        private String toJson(Map<String, Object> map) {
            try { return objectMapper.writeValueAsString(map); }
            catch (JsonProcessingException e) { return "{}"; }
        }

        // 注入所需依赖（RagService 为可选，ChromaDB 未连接时禁用 RAG）
        public ChatController(ChatClient.Builder builder, 
                            @Autowired(required = false) RagService ragService,
                            INovelCharacterService characterService,
                            IStoryNodeService storyNodeService,
                            IChatSessionService chatSessionService,
                            IntentAnalyzer intentAnalyzer,
                            PromptBuilder promptBuilder,
                            List<Tool> tools) {
            this.chatClient = builder.build();
            this.ragService = ragService;
            this.characterService = characterService;
            this.storyNodeService = storyNodeService;
            this.chatSessionService = chatSessionService;
            this.intentAnalyzer = intentAnalyzer;
            this.promptBuilder = promptBuilder;
            this.tools = tools;
            this.ragEnabled = (ragService != null);
            if (!ragEnabled) {
                log.warn("⚠️ RAG 功能已禁用（ChromaDB 未配置），仅使用数据库上下文");
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
                    // 解析 profile
                    ExecutionProfile profile = ExecutionProfile.BALANCED;
                    try {
                        profile = ExecutionProfile.valueOf(request.getProfile() != null ? request.getProfile() : "BALANCED");
                    } catch (IllegalArgumentException ignored) {}

                    // 构建 Pipeline 上下文
                    String fullPrompt = buildPromptWithPipeline(request, profile);

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
                    Map<String, Object> ragResult = ragService.search(finalMessage, 5);
                    Object resultsObj = ragResult.get("results");
                    if (resultsObj instanceof List<?> results && !results.isEmpty()) {
                        String ragContext = results.stream()
                                .map(r -> {
                                    if (r instanceof Map<?, ?> m) {
                                        String content = String.valueOf(m.get("content"));
                                        Object meta = m.get("metadata");
                                        String source = "";
                                        if (meta instanceof Map<?, ?> mm) {
                                            Object bookTitle = mm.get("book_title");
                                            Object sourceObj = mm.get("source");
                                            source = bookTitle != null ? String.valueOf(bookTitle)
                                                    : (sourceObj != null ? String.valueOf(sourceObj) : "");
                                        }
                                        return (source.isEmpty() ? "" : "[" + source + "] ") + content;
                                    }
                                    return String.valueOf(r);
                                })
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
         * 使用 Pipeline 组件构建 Prompt（意图识别 + 工具调用 + 结构化 Prompt）
         */
        private String buildPromptWithPipeline(ChatRequest request, ExecutionProfile profile) {
            Long userId = getUserIdFromAuth();
            String userIdStr = userId != null ? String.valueOf(userId) : null;

            // 1. 读取历史
            List<PromptContext.Message> history = new ArrayList<>();
            if (request.getSessionId() != null && !request.getSessionId().isBlank() && userId != null) {
                List<Map<String, Object>> msgs = chatSessionService.getSessionMessagesWithEdits(request.getSessionId(), userId);
                if (msgs != null) {
                    history = msgs.stream()
                        .map(m -> new PromptContext.Message(
                            (String) m.get("role"),
                            (String) m.get("content"),
                            m.get("thinking") != null ? String.valueOf(m.get("thinking")) : null
                        ))
                        .collect(Collectors.toList());
                }
            }

            // 2. 意图识别（BALANCED/DEEP）
            IntentResult intentResult = null;
            if (profile != ExecutionProfile.FAST) {
                try {
                    intentResult = intentAnalyzer.analyze(new IntentAnalyzer.IntentInput(request.getMessage(), history));
                    log.info("Intent: {} | Goal: {}", intentResult.intent(), intentResult.goal());
                } catch (Exception e) {
                    log.warn("意图识别失败: {}", e.getMessage());
                }
            }

            // 3. 构建固定上下文
            Map<String, String> fixedContext = buildFixedContextFromRequest(request);

            // 4. 读取编辑记忆
            EditMemory editMemory = EditMemory.empty();
            if (userId != null && request.getSessionId() != null) {
                String editsPrompt = chatSessionService.buildEditContextPrompt(userId, request.getSessionId());
                if (!editsPrompt.isBlank()) {
                    editMemory = new EditMemory(List.of(new EditMemory.EditRecord(-1, "历史修正", editsPrompt, "")));
                }
            }

            // 5. 工具调用（BALANCED/DEEP）
            List<Tool.ToolResult> toolResults = new ArrayList<>();
            if (profile.allowTools) {
                int maxRounds = profile.maxToolRounds;
                for (int round = 0; round < maxRounds; round++) {
                    // BALANCED: 没有计划时，做一次通用检索
                    if (profile == ExecutionProfile.BALANCED && round == 0 && toolResults.isEmpty()) {
                        Tool tool = tools.stream().filter(t -> t.name().equals("knowledge_search")).findFirst().orElse(null);
                        if (tool != null) {
                            Tool.ToolInput input = new Tool.ToolInput(request.getMessage(), null, 5);
                            Tool.ToolResult result = tool.execute(input);
                            toolResults.add(result);
                        }
                    }
                    break; // 简化：单轮工具调用
                }
            }

            // 6. 构建最终 Prompt
            IntentAnalyzer.Intent intent = intentResult != null ? intentResult.intent() : IntentAnalyzer.Intent.CREATIVE_WRITING;
            String systemPrompt = switch (profile) {
                case FAST -> "你是小说创作助手。严格遵循【固定设定】与【对话历史】创作，不自造设定，不违背前文。直接给出创作结果，简练、沉浸感强。";
                case BALANCED -> "你是小说创作助手。严格遵循【固定设定】与【对话历史】创作。你可以使用 knowledge_search 工具查阅设定细节。先思考，再给出创作结果。";
                case DEEP -> "你是资深小说创作专家。严格遵循【固定设定】与【对话历史】创作。你拥有 knowledge_search 工具，可多轮检索角色/大纲/世界观/章节。请输出 <thinking> 思考过程，再给最终创作。思考要包含：意图分析、检索策略、推理链路。";
            };

            PromptContext ctx = new PromptContext(
                systemPrompt,
                fixedContext,
                history,
                editMemory,
                toolResults,
                request.getMessage(),
                profile
            );

            return promptBuilder.build(ctx);
        }

        /**
         * 从 ChatRequest 构建固定上下文（角色/故事节点）
         */
        private Map<String, String> buildFixedContextFromRequest(ChatRequest request) {
            Map<String, String> fixedContext = new LinkedHashMap<>();
            if (request.getIncludeCharacters() != null && request.getIncludeCharacters()
                    && request.getCharacterIds() != null && !request.getCharacterIds().isEmpty()) {
                List<NovelCharacter> characters = characterService.listByIds(request.getCharacterIds());
                if (!characters.isEmpty()) {
                    StringBuilder sb = new StringBuilder();
                    for (NovelCharacter c : characters) {
                        sb.append("【").append(c.getName()).append("】\n");
                        if (c.getAppearance() != null) sb.append("外貌：").append(c.getAppearance()).append("\n");
                        if (c.getPersonality() != null) sb.append("性格：").append(c.getPersonality()).append("\n");
                        if (c.getBackground() != null) sb.append("背景：").append(c.getBackground()).append("\n");
                        sb.append("\n");
                    }
                    fixedContext.put("角色卡", sb.toString());
                }
            }
            if (request.getIncludeStory() != null && request.getIncludeStory()
                    && request.getStoryNodeIds() != null && !request.getStoryNodeIds().isEmpty()) {
                List<StoryNode> nodes = storyNodeService.listByIds(request.getStoryNodeIds());
                if (!nodes.isEmpty()) {
                    StringBuilder sb = new StringBuilder();
                    for (StoryNode n : nodes) {
                        sb.append("【").append(n.getTitle()).append("】\n");
                        if (n.getContent() != null) sb.append(n.getContent()).append("\n");
                        sb.append("\n");
                    }
                    fixedContext.put("故事节点", sb.toString());
                }
            }
            return fixedContext;
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

                    // 2. 解析 profile 并构建 Pipeline 上下文
                    ExecutionProfile profile = ExecutionProfile.BALANCED;
                    try {
                        profile = ExecutionProfile.valueOf(request.getProfile() != null ? request.getProfile() : "BALANCED");
                    } catch (IllegalArgumentException ignored) {}
                    String fullPrompt = buildPromptWithPipeline(request, profile);

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
         * 将前端 ChatRequest 转换为 Pipeline ConversationRequest
         */
        private ConversationRequest toConversationRequest(ChatRequest request) {
            Long userId = getUserIdFromAuth();
            ExecutionProfile profile = ExecutionProfile.BALANCED;
            try {
                profile = ExecutionProfile.valueOf(request.getProfile() != null ? request.getProfile() : "BALANCED");
            } catch (IllegalArgumentException ignored) {}
            return new ConversationRequest(
                userId != null ? String.valueOf(userId) : null,
                request.getSessionId(),
                request.getMessage(),
                profile,
                request.getCharacterIds(),
                request.getStoryNodeIds(),
                request.getIncludeCharacters() != null ? request.getIncludeCharacters() : true,
                request.getIncludeStory() != null ? request.getIncludeStory() : true
            );
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
                    Map<String, Object> ragResult = ragService.search(finalMessage, 5);
                    Object resultsObj = ragResult.get("results");
                    if (resultsObj instanceof List<?> results && !results.isEmpty()) {
                        String ragContext = results.stream()
                                .map(r -> {
                                    if (r instanceof Map<?, ?> m) {
                                        String content = String.valueOf(m.get("content"));
                                        Object meta = m.get("metadata");
                                        String source = "";
                                        if (meta instanceof Map<?, ?> mm) {
                                            Object bookTitle = mm.get("book_title");
                                            Object sourceObj = mm.get("source");
                                            source = bookTitle != null ? String.valueOf(bookTitle)
                                                    : (sourceObj != null ? String.valueOf(sourceObj) : "");
                                        }
                                        return (source.isEmpty() ? "" : "[" + source + "] ") + content;
                                    }
                                    return String.valueOf(r);
                                })
                                .collect(Collectors.joining("\n---\n"));
                        fullPrompt = String.format(
                                "【参考资料】\n%s\n\n%s\n\n用户需求：%s\n\n请基于以上信息回答用户的问题。如果参考资料与问题相关，请重点参考；如不相关，可忽略。",
                                ragContext, dbContext, finalMessage
                        );
                    }
                } catch (Exception e) {
                    log.error("RAG 检索失败，仅使用数据库上下文: {}", e.getMessage(), e);
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