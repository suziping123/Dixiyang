package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;

public interface ConversationPipeline {
    PipelineResult execute(ConversationRequest request);
}

record ConversationRequest(
    String userId,
    String sessionId,
    String message,
    ExecutionProfile profile,
    List<Long> characterIds,
    List<Long> storyNodeIds,
    boolean includeCharacters,
    boolean includeStory
) {}

record PipelineResult(
    String content,
    String thinking,
    List<ToolTrace> toolTraces,
    ConversationState state
) {}

record ToolTrace(
    String tool,
    ToolInput input,
    ToolResult output,
    long latencyMs
) {}

record ToolInput(
    String query,
    String type,
    int topK
) {}

record ToolResult(
    String content,
    java.util.Map<String, Object> metadata
) {}