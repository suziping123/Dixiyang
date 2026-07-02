package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;
import java.util.Map;

public record PromptContext(
    String systemPrompt,
    Map<String, String> fixedContext,
    List<Message> history,
    EditMemory editMemory,
    List<Tool.ToolResult> toolResults,
    String userInput,
    ExecutionProfile profile
) {
    public record Message(
        String role,
        String content,
        String thinking
    ) {}
}