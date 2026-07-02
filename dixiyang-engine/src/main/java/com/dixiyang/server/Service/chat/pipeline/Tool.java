package com.dixiyang.server.Service.chat.pipeline;

import java.util.Map;

public interface Tool {
    String name();
    String description();
    ToolSchema schema();
    ToolResult execute(ToolInput input);

    record ToolSchema(
        Map<String, Object> parameters,
        String example
    ) {}

    record ToolInput(
        String query,
        String type,
        int topK
    ) {}

    record ToolResult(
        String content,
        Map<String, Object> metadata
    ) {}
}