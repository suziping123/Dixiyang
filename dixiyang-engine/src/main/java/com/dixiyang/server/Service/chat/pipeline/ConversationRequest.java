package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;

public record ConversationRequest(
    String userId,
    String sessionId,
    String message,
    ExecutionProfile profile,
    List<Long> characterIds,
    List<Long> storyNodeIds,
    boolean includeCharacters,
    boolean includeStory
) {}