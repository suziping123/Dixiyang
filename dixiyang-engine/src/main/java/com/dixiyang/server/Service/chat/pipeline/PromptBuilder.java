package com.dixiyang.server.Service.chat.pipeline;

public interface PromptBuilder {
    String build(PromptContext context);
}