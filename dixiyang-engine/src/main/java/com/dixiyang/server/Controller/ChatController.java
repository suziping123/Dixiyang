package com.dixiyang.server.Controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.dixiyang.server.Entity.NovelCharacter;
import com.dixiyang.server.Entity.StoryNode;
import com.dixiyang.server.Entity.dto.ChatRequest;
import com.dixiyang.server.Service.IChatSessionService;
import com.dixiyang.server.Service.INovelCharacterService;
import com.dixiyang.server.Service.IStoryNodeService;
import com.dixiyang.server.Service.RagService;
import com.dixiyang.server.Service.chat.agent.ConversationMode;
import com.dixiyang.server.Service.chat.agent.FileBasedChatMemoryStore;
import com.dixiyang.server.Service.chat.agent.PromptTemplates;
import dev.langchain4j.data.message.*;
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

/**
 * AI 聊天控制器（LangChain4j 版）
 * 使用 PromptTemplate + ChatMemory 自动化调度
 */
@Tag(name = "聊天模块")
@RestController
@Slf4j
public class ChatController {

    private final ChatModel chatModel;
    private final StreamingChatModel streamingChatModel;
    private final ChatMemoryProvider chatMemoryProvider;
    private final FileBasedChatMemoryStore memoryStore;
    private final RagService ragService;
    private final INovelCharacterService characterService;
    private final IStoryNodeService storyNodeService;
    private final IChatSessionService chatSessionService;
    private final boolean ragEnabled;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final String THINKING_START = "<thinking>";
    private static final String THINKING_END = "</thinking>";

    public ChatController(ChatModel chatModel,
                          StreamingChatModel streamingChatModel,
                          ChatMemoryProvider chatMemoryProvider,
                          FileBasedChatMemoryStore memoryStore,
                          @Autowired(required = false) RagService ragService,
                          INovelCharacterService characterService,
                          IStoryNodeService storyNodeService,
                          IChatSessionService chatSessionService) {
        this.chatModel = chatModel;
        this.streamingChatModel = streamingChatModel;
        this.chatMemoryProvider = chatMemoryProvider;
        this.memoryStore = memoryStore;
        this.ragService = ragService;
        this.characterService = characterService;
        this.storyNodeService = storyNodeService;
        this.chatSessionService = chatSessionService;
        this.ragEnabled = (ragService != null);
        if (!ragEnabled) {
            log.warn("RAG 功能已禁用（ChromaDB 未配置），仅使用数据库上下文");
        }
    }

    // ==================== 接口入口 ====================

    @GetMapping("/chat")
    public String chatGet(@RequestParam String message,
                          @RequestParam(defaultValue = "true") boolean useRag) {
        ChatRequest req = new ChatRequest();
        req.setMessage(message);
        req.setUseRag(useRag);
        return chatSync(req);
    }

    @PostMapping("/chat")
    public String chatPost(@RequestBody ChatRequest request) {
        return chatSync(request);
    }

    @PostMapping("/chat/stream")
    public SseEmitter chatStream(@RequestBody ChatRequest request) {
        SseEmitter emitter = new SseEmitter(1800000L);
        ExecutorService executor = Executors.newSingleThreadExecutor();

        executor.execute(() -> {
            try {
                Long userId = getUserIdFromAuth();
                String sessionId = request.getSessionId();
                ConversationMode mode = ConversationMode.fromString(request.getConversationMode());

                // 1. 构建 System Prompt（用 PromptTemplate）
                String systemPrompt = PromptTemplates.buildSystemPrompt(mode, request.getCustomSystemPrompt());

                // 2. 构建 User Prompt（用 PromptTemplate）
                String fixedContext = buildFixedContext(request);
                String edits = (userId != null && sessionId != null)
                    ? chatSessionService.buildEditContextPrompt(userId, sessionId) : "";
                String userPrompt = PromptTemplates.buildUserPrompt(fixedContext, "", edits, request.getMessage());

                log.info("对话模式: {} | sessionId={}", mode.name(), sessionId);

                // 3. 流式调用 LLM
                dev.langchain4j.model.chat.request.ChatRequest chatReq = dev.langchain4j.model.chat.request.ChatRequest.builder()
                    .messages(
                        SystemMessage.from(systemPrompt),
                        UserMessage.from(userPrompt)
                    )
                    .build();

                StringBuilder buf = new StringBuilder();
                AtomicReference<String> state = new AtomicReference<>("INIT");
                StringBuilder fullResponse = new StringBuilder();
                StringBuilder thinkingResponse = new StringBuilder();
                CountDownLatch latch = new CountDownLatch(1);

                streamingChatModel.chat(chatReq, new dev.langchain4j.model.chat.response.StreamingChatResponseHandler() {
                    @Override
                    public void onPartialResponse(String partialResponse) {
                        fullResponse.append(partialResponse);
                        buf.append(partialResponse);
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
                    }

                    @Override
                    public void onCompleteResponse(ChatResponse response) {
                        String remaining = buf.toString();
                        if (!remaining.isEmpty()) {
                            String cur = state.get();
                            sendEvent(emitter, "THINKING".equals(cur) ? "thinking" : "content", remaining);
                        }
                        sendEvent(emitter, "done", null);
                        try { emitter.complete(); } catch (Exception ignored) {}

                        // 保存消息到链文件
                        saveMessages(userId, sessionId, request, fullResponse.toString(), thinkingResponse.toString());
                        // 清除 ChatMemory 缓存，下次请求重新加载
                        memoryStore.invalidateCache(sessionId);
                        latch.countDown();
                    }

                    @Override
                    public void onError(Throwable error) {
                        log.error("AI 流式调用失败: {}", error.getMessage());
                        sendEvent(emitter, "error", "AI 调用失败: " + error.getMessage());
                        sendEvent(emitter, "done", null);
                        try { emitter.complete(); } catch (Exception ignored) {}
                        latch.countDown();
                    }
                });

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

    @PostMapping("/chat/regenerate")
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
                chatSessionService.truncateSessionChain(finalUserId, sessionId, messageIndex);
                memoryStore.invalidateCache(sessionId);
                chatStream(request);
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

    // ==================== 同步聊天 ====================

    private String chatSync(ChatRequest request) {
        try {
            Long userId = getUserIdFromAuth();
            String sessionId = request.getSessionId();
            ConversationMode mode = ConversationMode.fromString(request.getConversationMode());

            String systemPrompt = PromptTemplates.buildSystemPrompt(mode, request.getCustomSystemPrompt());
            String fixedContext = buildFixedContext(request);
            String edits = (userId != null && sessionId != null)
                ? chatSessionService.buildEditContextPrompt(userId, sessionId) : "";
            String userPrompt = PromptTemplates.buildUserPrompt(fixedContext, "", edits, request.getMessage());

            dev.langchain4j.model.chat.request.ChatRequest chatReq = dev.langchain4j.model.chat.request.ChatRequest.builder()
                .messages(
                    SystemMessage.from(systemPrompt),
                    UserMessage.from(userPrompt)
                )
                .build();

            ChatResponse response = chatModel.chat(chatReq);
            String content = response.aiMessage().text();

            saveMessages(userId, sessionId, request, content, "");
            memoryStore.invalidateCache(sessionId);
            return content;
        } catch (Exception e) {
            log.error("同步聊天失败: {}", e.getMessage(), e);
            return "生成失败：" + e.getMessage();
        }
    }

    // ==================== 固定上下文构建（只构建设定部分，其余交给 PromptTemplate） ====================

    private String buildFixedContext(ChatRequest request) {
        StringBuilder sb = new StringBuilder();

        if (Boolean.TRUE.equals(request.getIncludeCharacters())
                && request.getCharacterIds() != null && !request.getCharacterIds().isEmpty()) {
            List<NovelCharacter> characters = characterService.listByIds(request.getCharacterIds());
            if (!characters.isEmpty()) {
                sb.append("== 角色卡 ==\n");
                for (NovelCharacter c : characters) {
                    sb.append("【").append(c.getName()).append("】\n");
                    if (c.getGender() != null) sb.append("性别：").append(c.getGender()).append("\n");
                    if (c.getAppearance() != null) sb.append("外貌：").append(c.getAppearance()).append("\n");
                    if (c.getPersonality() != null) sb.append("性格：").append(c.getPersonality()).append("\n");
                    if (c.getBackground() != null) sb.append("背景：").append(c.getBackground()).append("\n");
                    if (c.getExtra() != null && !c.getExtra().isEmpty()) sb.append("自定义：").append(c.getExtra()).append("\n");
                    sb.append("\n");
                }
            }
        }

        if (Boolean.TRUE.equals(request.getIncludeStory())
                && request.getStoryNodeIds() != null && !request.getStoryNodeIds().isEmpty()) {
            List<StoryNode> nodes = storyNodeService.listByIds(request.getStoryNodeIds());
            if (!nodes.isEmpty()) {
                sb.append("== 故事节点 ==\n");
                for (StoryNode n : nodes) {
                    sb.append("【").append(n.getTitle()).append("】\n");
                    if (n.getEventDate() != null) sb.append("时间：").append(n.getEventDate()).append("\n");
                    if (n.getEventType() != null) sb.append("类型：").append(n.getEventType()).append("\n");
                    if (n.getImportance() != null) sb.append("重要性：").append(n.getImportance()).append("\n");
                    if (n.getCharacterNames() != null) sb.append("关联角色：").append(n.getCharacterNames()).append("\n");
                    if (n.getTags() != null) sb.append("标签：").append(n.getTags()).append("\n");
                    if (n.getContent() != null) sb.append("内容：").append(n.getContent()).append("\n");
                    sb.append("\n");
                }
            }
        }

        return sb.toString();
    }

    // ==================== 消息保存 ====================

    private void saveMessages(Long userId, String sessionId, ChatRequest request, String content, String thinking) {
        if (userId == null || sessionId == null || sessionId.isBlank()) return;
        try {
            List<Map<String, Object>> msgs = new ArrayList<>();
            Map<String, Object> userMsg = new LinkedHashMap<>();
            userMsg.put("role", "user");
            userMsg.put("content", request.getMessage());
            userMsg.put("createTime", LocalDateTime.now().toString());
            msgs.add(userMsg);

            Map<String, Object> aiMsg = new LinkedHashMap<>();
            aiMsg.put("role", "assistant");
            aiMsg.put("content", content);
            if (thinking != null && !thinking.isBlank()) aiMsg.put("thinking", thinking);
            aiMsg.put("createTime", LocalDateTime.now().toString());
            msgs.add(aiMsg);

            chatSessionService.appendMessages(userId, request.getNovelId(), sessionId, msgs);
            chatSessionService.maybeSummarize(userId, sessionId);
            log.info("保存消息: sessionId={}, content长度={}", sessionId, content.length());
        } catch (Exception e) {
            log.warn("保存消息失败: {}", e.getMessage());
        }
    }

    // ==================== 工具方法 ====================

    private void sendEvent(SseEmitter emitter, String type, String delta) {
        try {
            Map<String, Object> evt = new HashMap<>();
            evt.put("type", type);
            if (delta != null) evt.put("delta", delta);
            emitter.send(SseEmitter.event().name("message").data(objectMapper.writeValueAsString(evt)));
        } catch (IllegalStateException ignored) {
        } catch (java.io.IOException e) {
            log.debug("客户端断开 SSE: {}", e.getMessage());
        } catch (Exception e) {
            log.warn("发送 SSE 事件异常: {}", e.getMessage());
        }
    }

    private Long getUserIdFromAuth() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || auth.getPrincipal() == null) return null;
        try { return Long.parseLong(auth.getPrincipal().toString()); }
        catch (NumberFormatException e) { return null; }
    }
}
