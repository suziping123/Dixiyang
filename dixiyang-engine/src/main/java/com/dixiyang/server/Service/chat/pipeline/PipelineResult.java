package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;

public record PipelineResult(
    String content,
    String thinking,
    List<ToolTrace> toolTraces,
    ConversationState state
) {
    public record ToolTrace(
        String tool,
        Tool.ToolInput input,
        Tool.ToolResult output,
        long latencyMs
    ) {}
}