package com.dixiyang.server.Service.chat.pipeline;

public enum ExecutionProfile {
    FAST(
        "快速创作",
        "仅用固定设定+历史上下文直接生成，不走检索、不显示思考、不规划",
        512, false, 0, false, false
    ),
    BALANCED(
        "均衡模式（推荐）",
        "意图识别→按需检索1次→生成，适合大多数创作/问答场景",
        2048, true, 1, false, false
    ),
    DEEP(
        "深度创作",
        "意图识别→规划器拆解步骤→多轮检索(≤3次)→显示思考过程→生成",
        4096, true, 3, true, true
    );

    public final String label;
    public final String description;
    public final int maxTokens;
    public final boolean allowTools;
    public final int maxToolRounds;
    public final boolean showThinking;
    public final boolean allowPlanner;

    ExecutionProfile(String label, String description, int maxTokens,
                     boolean allowTools, int maxToolRounds,
                     boolean showThinking, boolean allowPlanner) {
        this.label = label;
        this.description = description;
        this.maxTokens = maxTokens;
        this.allowTools = allowTools;
        this.maxToolRounds = maxToolRounds;
        this.showThinking = showThinking;
        this.allowPlanner = allowPlanner;
    }
}