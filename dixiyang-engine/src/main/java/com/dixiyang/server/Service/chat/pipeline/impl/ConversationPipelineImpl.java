package com.dixiyang.server.Service.chat.pipeline.impl;

import com.dixiyang.server.Entity.ChatSession;
import com.dixiyang.server.Mapper.ChatSessionMapper;
import com.dixiyang.server.Service.ChatContentFileService;
import com.dixiyang.server.Service.IChatSessionService;
import com.dixiyang.server.Service.INovelCharacterService;
import com.dixiyang.server.Service.IStoryNodeService;
import com.dixiyang.server.Service.chat.pipeline.*;
import com.dixiyang.server.Service.chat.pipeline.IntentAnalyzer.IntentResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Slf4j
public class ConversationPipelineImpl implements ConversationPipeline {

    private final ChatClient chatClient;
    private final IntentAnalyzer intentAnalyzer;
    private final Planner planner;
    private final PromptBuilder promptBuilder;
    private final List<Tool> tools;
    private final ChatContentFileService fileService;
    private final IChatSessionService chatSessionService;
    private final INovelCharacterService characterService;
    private final IStoryNodeService storyNodeService;

    @Autowired
    public ConversationPipelineImpl(ChatClient.Builder builder,
                                     IntentAnalyzer intentAnalyzer,
                                     Planner planner,
                                     PromptBuilder promptBuilder,
                                     List<Tool> tools,
                                     ChatContentFileService fileService,
                                     IChatSessionService chatSessionService,
                                     INovelCharacterService characterService,
                                     IStoryNodeService storyNodeService) {
        this.chatClient = builder.build();
        this.intentAnalyzer = intentAnalyzer;
        this.planner = planner;
        this.promptBuilder = promptBuilder;
        this.tools = tools;
        this.fileService = fileService;
        this.chatSessionService = chatSessionService;
        this.characterService = characterService;
        this.storyNodeService = storyNodeService;
    }

    @Override
    @Transactional
    public PipelineResult execute(ConversationRequest request) {
        long startTime = System.currentTimeMillis();

        // 1. 读取会话历史
        List<PromptContext.Message> history = readHistory(request.sessionId(), request.userId());

        // 2. 意图识别
        IntentResult intentResult = intentAnalyzer.analyze(new IntentAnalyzer.IntentInput(request.message(), history));
        log.info("Intent: {} | Goal: {}", intentResult.intent(), intentResult.goal());

        // 3. 构建固定上下文（角色/大纲/节点）
        Map<String, String> fixedContext = buildFixedContext(request);

        // 4. 读取编辑记忆
        EditMemory editMemory = readEditMemory(request.userId(), request.sessionId());

        // 5. 规划（仅 DEEP）
        ExecutionPlan plan = (request.profile() == ExecutionProfile.DEEP)
            ? planner.plan(new PlannerInput(
                request.message(),
                SYSTEM_PROMPTS.get(request.profile()),
                history,
                editMemory,
                tools,
                request.profile()
            ))
            : new ExecutionPlan(List.of());

        // 6. 执行工具调用（按计划或按需）
        List<Tool.ToolResult> toolResults = new ArrayList<>();
        List<PipelineResult.ToolTrace> toolTraces = new ArrayList<>();

        if (request.profile().allowTools) {
            int maxRounds = request.profile().maxToolRounds;
            for (int round = 0; round < maxRounds; round++) {
                // 构建当前 PromptContext 用于工具判断
                PromptContext ctxForTool = buildPromptContext(
                    request, history, fixedContext, editMemory, toolResults, intentResult.intent()
                );
                String prompt = promptBuilder.build(ctxForTool);

                // 让 LLM 决定是否调用工具（通过 Function Calling）
                // 这里简化：按计划执行，或在 BALANCED 下做一次检索
                if (!plan.steps().isEmpty() && round < plan.steps().size()) {
                    ExecutionPlan.PlanStep step = plan.steps().get(round);
                    Tool tool = findTool(step.tool());
                    if (tool != null) {
                        long t0 = System.currentTimeMillis();
                        Tool.ToolResult result = tool.execute(step.input());
                        toolResults.add(result);
                        toolTraces.add(new PipelineResult.ToolTrace(step.tool(), step.input(), result, System.currentTimeMillis() - t0));
                        continue;
                    }
                }
                // BALANCED: 没有计划时，做一次通用检索
                if (request.profile() == ExecutionProfile.BALANCED && round == 0 && toolResults.isEmpty()) {
                    Tool tool = findTool("knowledge_search");
                    if (tool != null) {
                        Tool.ToolInput input = new Tool.ToolInput(request.message(), null, 5);
                        long t0 = System.currentTimeMillis();
                        Tool.ToolResult result = tool.execute(input);
                        toolResults.add(result);
                        toolTraces.add(new PipelineResult.ToolTrace("knowledge_search", input, result, System.currentTimeMillis() - t0));
                    }
                }
                break; // 简化：单轮工具调用
            }
        }

        // 7. 构建最终 Prompt 并调用 LLM
        PromptContext finalCtx = buildPromptContext(request, history, fixedContext, editMemory, toolResults, intentResult.intent());
        String finalPrompt = promptBuilder.build(finalCtx);

        String content = "";
        String thinking = "";
        try {
            if (request.profile().showThinking) {
                // 使用流式获取 thinking + content
                var flux = chatClient.prompt(finalPrompt)
                    .options(OpenAiChatOptions.builder().maxTokens(request.profile().maxTokens).build())
                    .stream().content();
                StringBuilder full = new StringBuilder();
                StringBuilder think = new StringBuilder();
                boolean inThinking = false;
                for (String token : flux.toIterable()) {
                    full.append(token);
                    if (!inThinking && full.toString().contains("<thinking>")) {
                        inThinking = true;
                        int idx = full.indexOf("<thinking>");
                        String before = full.substring(0, idx);
                        if (!before.isBlank()) content = before;
                        full.setLength(0);
                        full.append(full.toString().substring(idx + "<thinking>".length()));
                    }
                    if (inThinking) {
                        String s = full.toString();
                        int endIdx = s.indexOf("</thinking>");
                        if (endIdx >= 0) {
                            think.append(s.substring(0, endIdx));
                            full.setLength(0);
                            full.append(s.substring(endIdx + "</thinking>".length()));
                            inThinking = false;
                            break;
                        } else if (s.length() > 20) {
                            think.append(s.substring(0, s.length() - 20));
                            full.setLength(0);
                            full.append(s.substring(s.length() - 20));
                        }
                    } else if (full.length() > 0) {
                        content = full.toString();
                        full.setLength(0);
                    }
                }
                if (!inThinking && full.length() > 0) content = full.toString();
                thinking = think.toString();
            } else {
                content = chatClient.prompt(finalPrompt)
                    .options(OpenAiChatOptions.builder().maxTokens(request.profile().maxTokens).build())
                    .call().content();
            }
        } catch (Exception e) {
            log.error("LLM call failed", e);
            content = "生成失败：" + e.getMessage();
        }

        // 8. 保存到会话
        saveToSession(request, content, thinking);

        // 9. 更新 ConversationState
        ConversationState state = buildState(request, intentResult, toolResults);

        log.info("Pipeline completed in {}ms, tools={}, thinking={}", 
            System.currentTimeMillis() - startTime, toolTraces.size(), thinking.length());

        return new PipelineResult(content, thinking, toolTraces, state);
    }

    private List<PromptContext.Message> readHistory(String sessionId, String userId) {
        List<Map<String, Object>> msgs = chatSessionService.getSessionMessagesWithEdits(sessionId, Long.parseLong(userId));
        return msgs.stream()
            .map(m -> new PromptContext.Message(
                (String) m.get("role"),
                (String) m.get("content"),
                m.get("thinking") != null ? String.valueOf(m.get("thinking")) : null
            ))
            .collect(Collectors.toList());
    }

    private Map<String, String> buildFixedContext(ConversationRequest req) {
        Map<String, String> ctx = new LinkedHashMap<>();
        if (req.includeCharacters() && req.characterIds() != null && !req.characterIds().isEmpty()) {
            var chars = characterService.listByIds(req.characterIds());
            StringBuilder sb = new StringBuilder();
            for (var c : chars) {
                sb.append("【").append(c.getName()).append("】\n");
                if (c.getAppearance() != null) sb.append("外貌：").append(c.getAppearance()).append("\n");
                if (c.getPersonality() != null) sb.append("性格：").append(c.getPersonality()).append("\n");
                if (c.getBackground() != null) sb.append("背景：").append(c.getBackground()).append("\n");
                sb.append("\n");
            }
            ctx.put("角色卡", sb.toString());
        }
        if (req.includeStory() && req.storyNodeIds() != null && !req.storyNodeIds().isEmpty()) {
            var nodes = storyNodeService.listByIds(req.storyNodeIds());
            StringBuilder sb = new StringBuilder();
            for (var n : nodes) {
                sb.append("【").append(n.getTitle()).append("】\n");
                if (n.getContent() != null) sb.append(n.getContent()).append("\n");
                sb.append("\n");
            }
            ctx.put("故事节点", sb.toString());
        }
        return ctx;
    }

    private EditMemory readEditMemory(String userId, String sessionId) {
        String editsPrompt = chatSessionService.buildEditContextPrompt(Long.parseLong(userId), sessionId);
        if (editsPrompt.isBlank()) return EditMemory.empty();
        // 简化：直接包装为一条记录
        return new EditMemory(List.of(new EditMemory.EditRecord(-1, "历史修正", editsPrompt, "")));
    }

    private PromptContext buildPromptContext(ConversationRequest req,
                                              List<PromptContext.Message> history,
                                              Map<String, String> fixedContext,
                                              EditMemory editMemory,
                                              List<Tool.ToolResult> toolResults,
                                              IntentAnalyzer.Intent intent) {
        String systemPrompt = SYSTEM_PROMPTS.getOrDefault(req.profile(), SYSTEM_PROMPTS.get(ExecutionProfile.BALANCED));
        return new PromptContext(
            systemPrompt,
            fixedContext,
            history,
            editMemory,
            toolResults,
            req.message(),
            req.profile()
        );
    }

    private void saveToSession(ConversationRequest req, String content, String thinking) {
        List<Map<String, Object>> msgs = new ArrayList<>();
        Map<String, Object> userMsg = new LinkedHashMap<>();
        userMsg.put("role", "user");
        userMsg.put("content", req.message());
        userMsg.put("createTime", LocalDateTime.now().toString());
        msgs.add(userMsg);

        Map<String, Object> aiMsg = new LinkedHashMap<>();
        aiMsg.put("role", "assistant");
        aiMsg.put("content", content);
        if (!thinking.isBlank()) aiMsg.put("thinking", thinking);
        aiMsg.put("createTime", LocalDateTime.now().toString());
        msgs.add(aiMsg);

        chatSessionService.appendMessages(Long.parseLong(req.userId()), null, req.sessionId(), msgs);
    }

    private ConversationState buildState(ConversationRequest req, IntentResult intentResult, List<Tool.ToolResult> toolResults) {
        Map<String, Object> knowledge = new HashMap<>();
        for (int i = 0; i < toolResults.size(); i++) {
            knowledge.put("tool_" + i, toolResults.get(i).metadata());
        }
        return new ConversationState(
            intentResult.goal(),
            null, null, null,
            knowledge,
            List.of(),
            Map.of("intent", intentResult.intent().name(), "rationale", intentResult.rationale())
        );
    }

    private static final Map<ExecutionProfile, String> SYSTEM_PROMPTS = Map.of(
        ExecutionProfile.FAST, """
            你是小说创作助手。严格遵循【固定设定】与【对话历史】创作，不自造设定，不违背前文。
            直接给出创作结果，简练、沉浸感强。
            """,
        ExecutionProfile.BALANCED, """
            你是小说创作助手。严格遵循【固定设定】与【对话历史】创作。
            你可以使用 knowledge_search 工具查阅设定细节。
            先思考，再给出创作结果。
            """,
        ExecutionProfile.DEEP, """
            你是资深小说创作专家。严格遵循【固定设定】与【对话历史】创作。
            你拥有 knowledge_search 工具，可多轮检索角色/大纲/世界观/章节。
            请输出 <thinking> 思考过程，再给最终创作。思考要包含：意图分析、检索策略、推理链路。
            """
    );

    private static final Map<ExecutionProfile, String> TASK_INSTRUCTIONS = Map.of(
        ExecutionProfile.FAST, "直接给创作结果。",
        ExecutionProfile.BALANCED, "先简要思考（可选），再给结果。",
        ExecutionProfile.DEEP, "必须输出 <thinking> 完整思考过程，再给最终结果。"
    );

    private Tool findTool(String name) {
        return tools.stream().filter(t -> t.name().equals(name)).findFirst().orElse(null);
    }
}