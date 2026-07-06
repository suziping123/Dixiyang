package com.dixiyang.server.Controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.dixiyang.server.Entity.NovelCharacter;
import com.dixiyang.server.Entity.StoryNode;
import com.dixiyang.server.Entity.dto.ChatRequest;
import com.dixiyang.server.Service.IChatSessionService;
import com.dixiyang.server.Service.INovelCharacterService;
import com.dixiyang.server.Service.IStoryNodeService;
import com.dixiyang.server.Service.RagService;
import com.dixiyang.server.Utils.StorageService;
import com.dixiyang.server.Service.chat.agent.ConversationMode;
import com.dixiyang.server.Service.chat.agent.FileBasedChatMemoryStore;
import com.dixiyang.server.Service.chat.agent.KnowledgeSearchTool;
import com.dixiyang.server.Service.chat.agent.PromptTemplates;
import dev.langchain4j.agent.tool.ToolExecutionRequest;
import dev.langchain4j.agent.tool.ToolSpecification;
import dev.langchain4j.agent.tool.ToolSpecifications;
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
    private final KnowledgeSearchTool knowledgeSearchTool;
    private final List<ToolSpecification> toolSpecifications;
    private final INovelCharacterService characterService;
    private final IStoryNodeService storyNodeService;
    private final IChatSessionService chatSessionService;
    private final StorageService storageService;
    private final boolean ragEnabled;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final String THINKING_START = "<thinking>";
    private static final String THINKING_END = "</thinking>";
    private static final int MAX_TOOL_ROUNDS = 5;

    public ChatController(ChatModel chatModel,
                          StreamingChatModel streamingChatModel,
                          ChatMemoryProvider chatMemoryProvider,
                          FileBasedChatMemoryStore memoryStore,
                          @Autowired(required = false) RagService ragService,
                          @Autowired(required = false) KnowledgeSearchTool knowledgeSearchTool,
                          INovelCharacterService characterService,
                          IStoryNodeService storyNodeService,
                          IChatSessionService chatSessionService,
                          StorageService storageService) {
        this.chatModel = chatModel;
        this.streamingChatModel = streamingChatModel;
        this.chatMemoryProvider = chatMemoryProvider;
        this.memoryStore = memoryStore;
        this.ragService = ragService;
        this.knowledgeSearchTool = knowledgeSearchTool;
        this.characterService = characterService;
        this.storyNodeService = storyNodeService;
        this.chatSessionService = chatSessionService;
        this.storageService = storageService;
        this.ragEnabled = (ragService != null);
        this.toolSpecifications = (knowledgeSearchTool != null)
            ? ToolSpecifications.toolSpecificationsFrom(knowledgeSearchTool)
            : List.of();
        if (!ragEnabled) {
            log.warn("RAG 功能已禁用（ChromaDB 未配置），仅使用数据库上下文");
        }
        if (!toolSpecifications.isEmpty()) {
            log.info("工具调用已启用: {} 个工具", toolSpecifications.size());
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

                String systemPrompt = PromptTemplates.buildSystemPrompt(mode, request.getCustomSystemPrompt());
                String fixedContext = buildFixedContext(request);
                String edits = (userId != null && sessionId != null)
                    ? chatSessionService.buildEditContextPrompt(userId, sessionId) : "";
                String userPrompt = PromptTemplates.buildUserPrompt(fixedContext, "", edits, request.getMessage());

                log.info("对话模式: {} | sessionId={} | tools={}", mode.name(), sessionId, toolSpecifications.size());

                List<ChatMessage> messages = new ArrayList<>();
                messages.add(SystemMessage.from(systemPrompt));
                messages.add(UserMessage.from(userPrompt));

                streamWithToolLoop(messages, emitter, request, userId, sessionId);
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

    /**
     * 流式 Agent 循环：LLM → 工具调用 → 执行工具 → 结果回传 → 再次 LLM → ...
     */
    private void streamWithToolLoop(List<ChatMessage> messages, SseEmitter emitter,
                                     ChatRequest request, Long userId, String sessionId) {
        // 是否有工具可用
        boolean useTools = !toolSpecifications.isEmpty();

        dev.langchain4j.model.chat.request.ChatRequest.Builder builder =
            dev.langchain4j.model.chat.request.ChatRequest.builder()
                .messages(messages);
        if (useTools) {
            builder.toolSpecifications(toolSpecifications);
        }
        dev.langchain4j.model.chat.request.ChatRequest chatReq = builder.build();

        StringBuilder buf = new StringBuilder();
        AtomicReference<String> state = new AtomicReference<>("INIT");
        StringBuilder fullResponse = new StringBuilder();
        StringBuilder thinkingResponse = new StringBuilder();
        AtomicReference<List<ToolExecutionRequest>> toolCallsRef = new AtomicReference<>(new ArrayList<>());
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
            public void onPartialToolCall(dev.langchain4j.model.chat.response.PartialToolCall partialToolCall) {
                // DeepSeek 流式 tool call 可能分块到达，此处暂不处理（DeepSeek 通常一次性返回完整 tool call）
            }

            @Override
            public void onCompleteToolCall(dev.langchain4j.model.chat.response.CompleteToolCall completeToolCall) {
                toolCallsRef.get().add(completeToolCall.toolExecutionRequest());
                log.info("LLM 请求工具调用: {}({})",
                    completeToolCall.toolExecutionRequest().name(),
                    completeToolCall.toolExecutionRequest().arguments());
            }

            @Override
            public void onCompleteResponse(ChatResponse response) {
                // 刷出残留 buffer
                String remaining = buf.toString();
                if (!remaining.isEmpty()) {
                    String cur = state.get();
                    sendEvent(emitter, "THINKING".equals(cur) ? "thinking" : "content", remaining);
                }

                List<ToolExecutionRequest> toolCalls = toolCallsRef.get();
                if (!toolCalls.isEmpty()) {
                    // 有工具调用 → 执行工具 → 追加结果 → 重新调用 LLM
                    handleToolCallsAndReinvoke(toolCalls, messages, fullResponse.toString(),
                        thinkingResponse.toString(), emitter, request, userId, sessionId);
                    latch.countDown();
                } else {
                    // 无工具调用 → 正常结束
                    sendEvent(emitter, "done", null);
                    try { emitter.complete(); } catch (Exception ignored) {}

                    saveMessages(userId, sessionId, request, fullResponse.toString(), thinkingResponse.toString());
                    memoryStore.invalidateCache(sessionId);
                    latch.countDown();
                }
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

        try { latch.await(); } catch (InterruptedException ignored) { Thread.currentThread().interrupt(); }
    }

    /**
     * 处理工具调用：执行工具 → 追加结果到消息 → 重新流式调用 LLM
     */
    private void handleToolCallsAndReinvoke(List<ToolExecutionRequest> toolCalls,
                                             List<ChatMessage> history,
                                             String contentSoFar, String thinkingSoFar,
                                             SseEmitter emitter, ChatRequest request,
                                             Long userId, String sessionId) {
        // 限制工具调用轮数，防止无限循环
        long toolRoundCount = history.stream().filter(m -> m instanceof ToolExecutionResultMessage).count() / 2;
        if (toolRoundCount >= MAX_TOOL_ROUNDS) {
            log.warn("工具调用超过 {} 轮，停止", MAX_TOOL_ROUNDS);
            sendEvent(emitter, "done", null);
            try { emitter.complete(); } catch (Exception ignored) {}
            return;
        }

        // 追加 AI 的工具调用消息（如果有文本内容也要保留）
        if (!contentSoFar.isEmpty() || !thinkingSoFar.isEmpty()) {
            StringBuilder aiText = new StringBuilder();
            if (!thinkingSoFar.isEmpty()) aiText.append("<thinking>").append(thinkingSoFar).append("</thinking>");
            if (!contentSoFar.isEmpty()) aiText.append(contentSoFar);
            history.add(AiMessage.from(aiText.toString(), toolCalls));
        } else {
            history.add(AiMessage.from(toolCalls));
        }

        // 执行每个工具调用
        for (ToolExecutionRequest toolCall : toolCalls) {
            String result = executeTool(toolCall);
            history.add(ToolExecutionResultMessage.from(
                toolCall.id(), toolCall.name(), result));
            log.info("工具执行完成: {} → {} 字符", toolCall.name(), result.length());
        }

        // 异步重新调用 LLM（避免递归栈溢出）
        ExecutorService toolExecutor = Executors.newSingleThreadExecutor();
        toolExecutor.execute(() -> {
            try {
                sendEvent(emitter, "toolExecuting", "检索完成，正在生成回答...");
                streamWithToolLoop(history, emitter, request, userId, sessionId);
            } finally {
                toolExecutor.shutdown();
            }
        });
    }

    /**
     * 执行工具调用，返回结果字符串
     */
    private String executeTool(ToolExecutionRequest toolCall) {
        try {
            String name = toolCall.name();
            String args = toolCall.arguments();
            if (knowledgeSearchTool != null && "knowledge_search".equals(name)) {
                var argsNode = objectMapper.readTree(args);
                String query = argsNode.has("query") ? argsNode.get("query").asText() : "";
                int topK = argsNode.has("top_k") ? argsNode.get("top_k").asInt(5) : 5;
                String docType = argsNode.has("doc_type") ? argsNode.get("doc_type").asText(null) : null;
                return knowledgeSearchTool.search(query, docType, topK);
            } else if (knowledgeSearchTool != null && "knowledge_search_detailed".equals(name)) {
                var argsNode = objectMapper.readTree(args);
                String query = argsNode.has("query") ? argsNode.get("query").asText() : "";
                int topK = argsNode.has("top_k") ? argsNode.get("top_k").asInt(5) : 5;
                String docType = argsNode.has("type") ? argsNode.get("type").asText(null) : null;
                return knowledgeSearchTool.search(query, docType, topK);
            }
            return "未知工具: " + name;
        } catch (Exception e) {
            log.error("工具执行失败: {}", e.getMessage(), e);
            return "工具执行失败: " + e.getMessage();
        }
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

            List<ChatMessage> messages = new ArrayList<>();
            messages.add(SystemMessage.from(systemPrompt));
            messages.add(UserMessage.from(userPrompt));

            // Agent 循环：工具调用最多 MAX_TOOL_ROUNDS 轮
            for (int round = 0; round <= MAX_TOOL_ROUNDS; round++) {
                var builder = dev.langchain4j.model.chat.request.ChatRequest.builder()
                    .messages(messages);
                if (!toolSpecifications.isEmpty()) {
                    builder.toolSpecifications(toolSpecifications);
                }

                ChatResponse response = chatModel.chat(builder.build());
                AiMessage aiMsg = response.aiMessage();

                // 无工具调用 → 直接返回
                if (aiMsg.toolExecutionRequests() == null || aiMsg.toolExecutionRequests().isEmpty()) {
                    String content = aiMsg.text() != null ? aiMsg.text() : "";
                    saveMessages(userId, sessionId, request, content, "");
                    memoryStore.invalidateCache(sessionId);
                    return content;
                }

                // 有工具调用 → 执行工具 → 追加结果 → 继续循环
                log.info("同步聊天工具调用轮次 {}: {} 个工具", round + 1, aiMsg.toolExecutionRequests().size());
                messages.add(aiMsg);
                for (ToolExecutionRequest toolCall : aiMsg.toolExecutionRequests()) {
                    String result = executeTool(toolCall);
                    messages.add(ToolExecutionResultMessage.from(toolCall.id(), toolCall.name(), result));
                }
            }

            // 超过最大轮数
            String fallback = "抱歉，检索过程过长，请简化问题后重试。";
            saveMessages(userId, sessionId, request, fallback, "");
            return fallback;
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
                    if (c.getExtra() != null && !c.getExtra().isEmpty()) {
                        try {
                            var extraData = storageService.loadJson("character", c.getId(), c.getExtra());
                            if (extraData != null) sb.append("自定义：").append(objectMapper.writeValueAsString(extraData)).append("\n");
                        } catch (Exception e) {
                            sb.append("自定义：").append(c.getExtra()).append("\n");
                        }
                    }
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
