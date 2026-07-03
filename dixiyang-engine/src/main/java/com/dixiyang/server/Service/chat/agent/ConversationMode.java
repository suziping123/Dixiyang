package com.dixiyang.server.Service.chat.agent;

/**
 * 对话模式 - 用户每轮对话前明确指定
 * 替代旧的 ExecutionProfile（处理深度），改为行为意图控制
 */
public enum ConversationMode {

    WRITE(
        "✍️ 创作", "按设定写剧情/对话/描写/续写",
        8192, false
    ),
    DISCUSS(
        "💬 讨论", "只回答设定相关问题，不创作内容",
        2048, false
    ),
    ANALYZE(
        "🔍 分析", "分析角色性格、剧情逻辑、世界观一致性",
        4096, true
    ),
    BRAINSTORM(
        "💡 头脑风暴", "发散讨论，寻找创作灵感",
        4096, true
    ),
    ASK(
        "❓ 提问", "快速精准回答，不啰嗦",
        1024, false
    );

    public final String label;
    public final String description;
    public final int maxTokens;
    public final boolean showThinking;

    ConversationMode(String label, String description, int maxTokens, boolean showThinking) {
        this.label = label;
        this.description = description;
        this.maxTokens = maxTokens;
        this.showThinking = showThinking;
    }

    public static ConversationMode fromString(String value) {
        if (value == null) return WRITE;
        try {
            return valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            return WRITE;
        }
    }
}
