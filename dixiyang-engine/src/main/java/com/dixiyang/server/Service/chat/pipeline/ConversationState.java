package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;
import java.util.Map;

public record ConversationState(
    String currentGoal,
    String currentChapter,
    String currentScene,
    Long currentCharacterId,
    Map<String, Object> activeKnowledge,
    List<String> pendingTasks,
    Map<String, Object> custom
) {
    public static ConversationState empty() {
        return new ConversationState(null, null, null, null, Map.of(), List.of(), Map.of());
    }
}