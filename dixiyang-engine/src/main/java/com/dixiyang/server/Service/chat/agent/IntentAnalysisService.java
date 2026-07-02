package com.dixiyang.server.Service.chat.agent;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

/**
 * 意图识别服务 - LangChain4j AiService
 * 自动解析用户意图，返回结构化结果
 */
public interface IntentAnalysisService {

    @SystemMessage("""
        判定本轮对话意图，仅返回 JSON，不要任何解释。

        意图类型：
        - CREATIVE_WRITING：用户要你按设定/前文写剧情/对话/描写/续写
        - SETTING_DISCUSSION：用户要讨论/确定/修改角色/世界观/大纲设定
        - BRAINSTORMING：用户想发散讨论、寻找灵感、探讨可能性
        - KNOWLEDGE_QUERY：用户明确要查阅资料/设定集/参考书
        - EDIT_CORRECTION：用户在纠正你上一轮的回答

        返回格式：
        {"intent":"类型","goal":"用户真正想完成什么（一句话）","rationale":"判断理由（一句话）"}
        """)
    @UserMessage("历史：{{history}}\n\n本轮输入：{{input}}")
    IntentResult analyze(@V("history") String history, @V("input") String input);

    record IntentResult(String intent, String goal, String rationale) {}
}
