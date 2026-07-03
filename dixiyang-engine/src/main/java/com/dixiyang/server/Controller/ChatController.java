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
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
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
 * 流程：用户指定模式 → 结构化 Prompt → LLM 流式输出
 */
@Tag(name = "聊天模块")
@RestController
@Slf4j
public class ChatController {

    private static final String SYSTEM_PROMPT_PREFIX = """
        你是小说创作助手。严格遵循以下规则：
        1. 角色信息必须与【固定设定】中的角色卡完全一致
        2. 故事事件必须与【固定设定】中的故事节点一致
        3. 设定中没有的信息不能凭空编造，必须明确说"设定中没有这个信息"
        4. 如果用户要求写与设定矛盾的内容，拒绝并说明原因

        根据下方【对话模式】决定你的行为：
        """;

    private static final String MODE_WRITE = """
        【对话模式：创作】
        按设定创作剧情、对话、描写、续写。严格基于固定设定，不自由发挥。
        """;
    private static final String MODE_DISCUSS = """
        【对话模式：讨论】
        只回答关于角色、世界观、大纲的设定问题。不要创作内容。
        如果用户要求创作，提醒他切换到创作模式。
        """;
    private static final String MODE_ANALYZE = """
        【对话模式：分析】
        分析角色性格、剧情逻辑、世界观一致性。给出有依据的分析。
        请输出 <thinking> 分析过程，再给结论。
        """;
    private static final String MODE_BRAINSTORM = """
        【对话模式：头脑风暴】
        帮用户发散思考、寻找创作灵感。可以提出多种可能性。
        请输出 <thinking> 思考过程，再给建议。
        """;
    private static final String MODE_ASK = """
        【对话模式：提问】
        快速精准回答用户问题，简短不啰嗦。
        """;

    private final ChatModel chatModel;
    private final StreamingChatModel streamingChatModel;
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
                          @Autowired(required = false) RagService ragService,
                          INovelCharacterService characterService,
                          IStoryNodeService storyNodeService,
                          IChatSessionService chatSessionService) {
        this.chatModel = chatModel;
        this.streamingChatModel = streamingChatModel;
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

                // 构建 Prompt
                String systemPrompt = buildSystemPrompt(request, mode);
                String userPrompt = buildUserPrompt(request);
                log.info("对话模式: {} | sessionId={}", mode.name(), sessionId);

                // 流式调用 LLM
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
                        saveMessages(userId, sessionId, request, fullResponse.toString(), thinkingResponse.toString());
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

            String systemPrompt = buildSystemPrompt(request, mode);
            String userPrompt = buildUserPrompt(request);

            dev.langchain4j.model.chat.request.ChatRequest chatReq = dev.langchain4j.model.chat.request.ChatRequest.builder()
                .messages(
                    SystemMessage.from(systemPrompt),
                    UserMessage.from(userPrompt)
                )
                .build();

            ChatResponse response = chatModel.chat(chatReq);
            String content = response.aiMessage().text();

            saveMessages(userId, sessionId, request, content, "");
            return content;
        } catch (Exception e) {
            log.error("同步聊天失败: {}", e.getMessage(), e);
            return "生成失败：" + e.getMessage();
        }
    }

    // ==================== Prompt 构建 ====================

    private String buildSystemPrompt(ChatRequest request, ConversationMode mode) {
        StringBuilder sb = new StringBuilder();
        sb.append(SYSTEM_PROMPT_PREFIX);

        // 模式指令
        sb.append(switch (mode) {
            case WRITE -> MODE_WRITE;
            case DISCUSS -> MODE_DISCUSS;
            case ANALYZE -> MODE_ANALYZE;
            case BRAINSTORM -> MODE_BRAINSTORM;
            case ASK -> MODE_ASK;
        });

        // 用户自定义 system prompt 追加
        if (request.getCustomSystemPrompt() != null && !request.getCustomSystemPrompt().isBlank()) {
            sb.append("\n【用户自定义指令】\n").append(request.getCustomSystemPrompt()).append("\n");
        }

        return sb.toString();
    }

    private String buildUserPrompt(ChatRequest request) {
        StringBuilder sb = new StringBuilder();

        String fixedContext = buildFixedContext(request);
        if (!fixedContext.isEmpty()) {
            sb.append("【固定设定·不可违背】\n").append(fixedContext).append("\n\n");
        }

        Long userId = getUserIdFromAuth();
        String history = buildHistoryString(request.getSessionId(), userId);
        if (!history.isEmpty()) {
            sb.append("【对话历史】\n").append(history).append("\n\n");
        }

        if (userId != null && request.getSessionId() != null) {
            String edits = chatSessionService.buildEditContextPrompt(userId, request.getSessionId());
            if (!edits.isBlank()) {
                sb.append(edits).append("\n\n");
            }
        }

        sb.append("【用户本轮输入】\n").append(request.getMessage());
        return sb.toString();
    }

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

    private String buildHistoryString(String sessionId, Long userId) {
        if (sessionId == null || sessionId.isBlank() || userId == null) return "";
        try {
            StringBuilder sb = new StringBuilder();

            // 1. 历史摘要（如果有）
            Map<String, Object> summary = chatSessionService.getSummary(userId, sessionId);
            String summaryText = summary.get("summary") instanceof String ? (String) summary.get("summary") : null;
            if (summaryText != null && !summaryText.isBlank()) {
                sb.append("【历史摘要】\n").append(summaryText).append("\n\n");
            }

            // 2. 近期消息
            List<Map<String, Object>> msgs = chatSessionService.getSessionMessagesWithEdits(sessionId, userId);
            if (msgs == null || msgs.isEmpty()) return sb.toString();

            // 如果有摘要，只取摘要之后的消息
            int skip = summary.get("lastMessageIndex") instanceof Number
                ? ((Number) summary.get("lastMessageIndex")).intValue() : 0;
            List<Map<String, Object>> recent = msgs.size() > skip ? msgs.subList(skip, msgs.size()) : msgs;

            if (!recent.isEmpty()) {
                if (summaryText != null) sb.append("【近期对话】\n");
                for (Map<String, Object> m : recent) {
                    String role = "user".equals(m.get("role")) ? "用户" : "AI";
                    String content = (String) m.get("content");
                    sb.append(role).append("：").append(content != null ? content : "").append("\n");
                }
            }

            return sb.toString();
        } catch (Exception e) {
            log.warn("读取历史失败: {}", e.getMessage());
            return "";
        }
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
            log.info("保存消息: sessionId={}, content长度={}", sessionId, content.length());

            // 异步检查是否需要摘要（不阻塞响应）
            chatSessionService.maybeSummarize(userId, sessionId);
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
