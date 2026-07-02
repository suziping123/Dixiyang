package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;

public record PlannerInput(
    String userInput,
    String systemPrompt,
    List<PromptContext.Message> history,
    EditMemory editMemory,
    List<Tool> availableTools,
    ExecutionProfile profile
) {}