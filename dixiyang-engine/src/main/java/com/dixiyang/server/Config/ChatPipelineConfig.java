package com.dixiyang.server.Config;

import com.dixiyang.server.Service.chat.pipeline.*;
import com.dixiyang.server.Service.chat.pipeline.impl.*;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class ChatPipelineConfig {

    @Bean
    public IntentAnalyzer intentAnalyzer(ChatClient.Builder builder) {
        return new LLMBasedIntentAnalyzer(builder);
    }

    @Bean
    public Planner planner(ChatClient.Builder builder) {
        return new LLMBasedPlanner(builder);
    }

    @Bean
    public PromptBuilder promptBuilder() {
        return new DefaultPromptBuilder();
    }

    @Bean
    public KnowledgeSearchTool knowledgeSearchTool(com.dixiyang.server.Service.RagService ragService) {
        return new KnowledgeSearchTool(ragService);
    }

    @Bean
    public List<Tool> tools(KnowledgeSearchTool knowledgeSearchTool) {
        return List.of(knowledgeSearchTool);
    }

    @Bean
    public ConversationPipeline conversationPipeline(
            ChatClient.Builder builder,
            IntentAnalyzer intentAnalyzer,
            Planner planner,
            PromptBuilder promptBuilder,
            List<Tool> tools,
            com.dixiyang.server.Service.ChatContentFileService fileService,
            com.dixiyang.server.Service.IChatSessionService chatSessionService,
            com.dixiyang.server.Service.INovelCharacterService characterService,
            com.dixiyang.server.Service.IStoryNodeService storyNodeService) {
        return new ConversationPipelineImpl(
            builder, intentAnalyzer, planner, promptBuilder, tools,
            fileService, chatSessionService, characterService, storyNodeService
        );
    }
}