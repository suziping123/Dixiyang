package com.dixiyang.server.Service.chat.agent;

import dev.langchain4j.model.input.PromptTemplate;

import java.util.Map;

/**
 * 所有 Prompt 模板的统一管理
 * 使用 LangChain4j PromptTemplate，消除手写字符串拼接
 */
public final class PromptTemplates {

    private PromptTemplates() {}

    // ==================== System Prompt 模板 ====================

    private static final String BASE_RULES = """
        你是小说创作助手。严格遵循以下规则：
        1. 角色信息必须与【固定设定】中的角色卡完全一致
        2. 故事事件必须与【固定设定】中的故事节点一致
        3. 设定中没有的信息不能凭空编造，必须明确说"设定中没有这个信息"
        4. 如果用户要求写与设定矛盾的内容，拒绝并说明原因
        """;

    public static final PromptTemplate SYSTEM_PROMPT = PromptTemplate.from(BASE_RULES + """

        【对话模式：{{mode}}】
        {{modeInstruction}}
        {{customInstruction}}
        """);

    // ==================== 模式指令 ====================

    public static final Map<ConversationMode, String> MODE_INSTRUCTIONS = Map.of(
        ConversationMode.WRITE, "按设定创作剧情、对话、描写、续写。严格基于固定设定，不自由发挥。",
        ConversationMode.DISCUSS, "只回答关于角色、世界观、大纲的设定问题。不要创作内容。如果用户要求创作，提醒他切换到创作模式。",
        ConversationMode.ANALYZE, "分析角色性格、剧情逻辑、世界观一致性。给出有依据的分析。请输出 <thinking> 分析过程，再给结论。",
        ConversationMode.BRAINSTORM, "帮用户发散思考、寻找创作灵感。可以提出多种可能性。请输出 <thinking> 思考过程，再给建议。",
        ConversationMode.ASK, "快速精准回答用户问题，简短不啰嗦。"
    );

    // ==================== User Prompt 模板 ====================

    public static final PromptTemplate USER_PROMPT = PromptTemplate.from("""
        {{fixedContext}}
        {{history}}
        {{edits}}

        【用户本轮输入】
        {{userMessage}}
        """);

    // ==================== 修正要点提取模板 ====================

    public static final PromptTemplate KEYPOINT_EXTRACT = PromptTemplate.from("""
        你是修正要点提取器。对比以下 AI 原始输出和用户修正后的内容，提取修正要点。

        AI 原始输出：{{original}}

        用户修正后：{{edited}}

        请返回 JSON（不要 markdown 包裹）：
        {"keyPoint":"一句话总结修正要点（30字以内）","errorType":"错误类型"}

        错误类型只能是以下之一：
        - FACT_ERROR（事实/数据错误）
        - SETTING_VIOLATION（违背设定）
        - TONE_WRONG（语气/风格不对）
        - TOO_LONG（太啰嗦）
        - OFF_TOPIC（答非所问）
        - OTHER（其他）

        只返回 JSON，不要任何解释。
        """);

    // ==================== 标题生成模板 ====================

    public static final PromptTemplate TITLE_GENERATE = PromptTemplate.from("""
        你是一个对话标题生成器。请用 3-8 个字概括以下对话的主题，直接返回标题，不要任何解释、标点或引号。

        对话：
        {{conversation}}
        """);

    // ==================== 历史摘要模板 ====================

    public static final PromptTemplate HISTORY_SUMMARIZE = PromptTemplate.from("""
        请用 3-5 句话概括以下对话的核心内容（设定讨论、创作内容、关键决定）。直接返回摘要，不要解释。

        {{previousSummary}}

        新对话内容：
        {{conversation}}
        """);

    // ==================== 便捷方法 ====================

    /**
     * 构建 System Prompt
     */
    public static String buildSystemPrompt(ConversationMode mode, String customInstruction) {
        return SYSTEM_PROMPT.apply(Map.of(
            "mode", mode.label,
            "modeInstruction", MODE_INSTRUCTIONS.get(mode),
            "customInstruction", customInstruction != null && !customInstruction.isBlank()
                ? "\n【用户自定义指令】\n" + customInstruction : ""
        )).text();
    }

    /**
     * 构建 User Prompt
     */
    public static String buildUserPrompt(String fixedContext, String history, String edits, String userMessage) {
        return USER_PROMPT.apply(Map.of(
            "fixedContext", fixedContext.isEmpty() ? "" : "【固定设定·不可违背】\n" + fixedContext + "\n\n",
            "history", history.isEmpty() ? "" : "【对话历史】\n" + history + "\n\n",
            "edits", edits.isBlank() ? "" : edits + "\n\n",
            "userMessage", userMessage
        )).text();
    }

    /**
     * 构建修正要点提取 Prompt
     */
    public static String buildKeyPointPrompt(String original, String edited) {
        return KEYPOINT_EXTRACT.apply(Map.of(
            "original", original.length() > 500 ? original.substring(0, 500) : original,
            "edited", edited.length() > 500 ? edited.substring(0, 500) : edited
        )).text();
    }
}
