package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;

public interface IntentAnalyzer {
    IntentResult analyze(IntentInput input);

    record IntentInput(
        String userInput,
        List<PromptContext.Message> history
    ) {}

    record IntentResult(
        Intent intent,
        String goal,
        String rationale
    ) {}

    enum Intent {
        CREATIVE_WRITING,
        SETTING_DISCUSSION,
        BRAINSTORMING,
        KNOWLEDGE_QUERY,
        EDIT_CORRECTION
    }
}