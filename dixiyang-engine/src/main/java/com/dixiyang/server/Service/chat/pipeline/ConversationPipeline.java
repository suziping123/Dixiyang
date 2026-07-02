package com.dixiyang.server.Service.chat.pipeline;

public interface ConversationPipeline {
    PipelineResult execute(ConversationRequest request);
}