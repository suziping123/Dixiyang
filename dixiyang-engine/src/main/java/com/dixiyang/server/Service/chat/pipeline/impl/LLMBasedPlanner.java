package com.dixiyang.server.Service.chat.pipeline.impl;

import com.dixiyang.server.Service.chat.pipeline.*;
import com.dixiyang.server.Service.chat.pipeline.PlannerInput;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Component
@Slf4j
public class LLMBasedPlanner implements Planner {

    private final ChatClient chatClient;
    private final ObjectMapper mapper = new ObjectMapper();

    public LLMBasedPlanner(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    @Override
    public ExecutionPlan plan(com.dixiyang.server.Service.chat.pipeline.PlannerInput input) {
        if (input.profile() != ExecutionProfile.DEEP) {
            return new ExecutionPlan(List.of());
        }

        String historyStr = input.history() != null ? input.history().stream()
            .limit(4)
            .map(m -> ("user".equals(m.role()) ? "用户" : "AI") + "：" + m.content())
            .collect(Collectors.joining("\n")) : "（无）";

        String toolsDesc = input.availableTools().stream()
            .map(t -> t.name() + ": " + t.description())
            .collect(Collectors.joining("\n"));

        String editMem = input.editMemory().records().isEmpty() ? "（无）" 
            : input.editMemory().records().stream()
                .map(r -> "错误=" + r.errorType() + " 正确=" + r.correct())
                .collect(Collectors.joining("; "));

        String prompt = """
            你是任务规划器。根据用户输入和可用工具，生成执行计划（JSON 数组）。
            每项：order(步骤号), tool(工具名), input{query,type,topK}, rationale(理由)。最多 3 步。
            
            用户输入：%s
            历史：%s
            可用工具：%s
            修正记忆：%s
            
            示例：
            [{"order":1,"tool":"knowledge_search","input":{"query":"主角性格","type":"character","topK":5},"rationale":"查角色卡"}]
            """.formatted(input.userInput(), historyStr, toolsDesc, editMem);

        try {
            String json = chatClient.prompt(prompt)
                .options(OpenAiChatOptions.builder().maxTokens(512).build())
                .call().content();
            List<ExecutionPlan.PlanStep> steps = parseSteps(json);
            return new ExecutionPlan(steps);
        } catch (Exception e) {
            log.warn("Planner 失败，用默认单步: {}", e.getMessage());
            return new ExecutionPlan(List.of(new ExecutionPlan.PlanStep(1, "knowledge_search",
                new Tool.ToolInput(input.userInput(), "", 5), "默认检索")));
        }
    }

    private List<ExecutionPlan.PlanStep> parseSteps(String json) {
        List<ExecutionPlan.PlanStep> steps = new ArrayList<>();
        try {
            JsonNode node = mapper.readTree(json.trim());
            if (node.isArray()) {
                for (JsonNode s : node) {
                    int order = s.has("order") ? s.get("order").asInt() : steps.size() + 1;
                    String tool = s.has("tool") ? s.get("tool").asText() : "knowledge_search";
                    JsonNode in = s.has("input") ? s.get("input") : mapper.createObjectNode();
                    Tool.ToolInput input = new Tool.ToolInput(
                        in.has("query") ? in.get("query").asText() : "",
                        in.has("type") ? in.get("type").asText() : "",
                        in.has("topK") ? in.get("topK").asInt() : 5
                    );
                    String rationale = s.has("rationale") ? s.get("rationale").asText() : "";
                    steps.add(new ExecutionPlan.PlanStep(order, tool, input, rationale));
                }
            }
        } catch (Exception e) {
            log.debug("Parse steps failed: {}", e.getMessage());
        }
        return steps;
    }
}