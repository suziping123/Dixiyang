package com.dixiyang.server.Service.chat.pipeline.impl;

import com.dixiyang.server.Service.chat.pipeline.IntentAnalyzer;
import com.dixiyang.server.Service.chat.pipeline.PromptContext;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.stereotype.Component;
import java.util.stream.Collectors;

@Component
@Slf4j
public class LLMBasedIntentAnalyzer implements IntentAnalyzer {

    private final ChatClient chatClient;

    public LLMBasedIntentAnalyzer(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    @Override
    public IntentResult analyze(IntentInput input) {
        String historyStr = input.history() != null ? input.history().stream()
            .limit(6)
            .map(m -> ("user".equals(m.role()) ? "用户" : "AI") + "：" + m.content())
            .collect(Collectors.joining("\n")) : "（无）";

        String prompt = """
            判定本轮对话意图，仅返回 JSON，不要任何解释。
            
            意图类型：
            - CREATIVE_WRITING：用户要你按设定/前文写剧情/对话/描写/续写
            - SETTING_DISCUSSION：用户要讨论/确定/修改角色/世界观/大纲设定
            - BRAINSTORMING：用户想发散讨论、寻找灵感、探讨可能性
            - KNOWLEDGE_QUERY：用户明确要查阅资料/设定集/参考书
            - EDIT_CORRECTION：用户在纠正你上一轮的回答
            
            历史（最近6条）：
            %s
            
            本轮输入：%s
            
            返回格式：
            {"intent":"类型","goal":"用户真正想完成什么（一句话）","rationale":"判断理由（一句话）"}
            """.formatted(historyStr, input.userInput());

        try {
            String resp = chatClient.prompt(prompt)
                .options(OpenAiChatOptions.builder().maxTokens(256).build())
                .call().content();
            log.debug("Intent analysis: {}", resp);
            return parse(resp);
        } catch (Exception e) {
            log.warn("Intent analysis failed, default CREATIVE_WRITING: {}", e.getMessage());
            return new IntentResult(Intent.CREATIVE_WRITING, "创作内容", "默认");
        }
    }

    private IntentResult parse(String json) {
        try {
            var node = new com.fasterxml.jackson.databind.ObjectMapper().readTree(json);
            Intent intent = Intent.valueOf(node.get("intent").asText());
            String goal = node.has("goal") ? node.get("goal").asText() : "";
            String rationale = node.has("rationale") ? node.get("rationale").asText() : "";
            return new IntentResult(intent, goal, rationale);
        } catch (Exception e) {
            return new IntentResult(Intent.CREATIVE_WRITING, "创作内容", "解析失败");
        }
    }
}