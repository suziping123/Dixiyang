package com.dixiyang.server.Config;

import com.dixiyang.server.Service.chat.agent.ChatService;
import com.dixiyang.server.Service.chat.agent.IntentAnalysisService;
import com.dixiyang.server.Service.chat.agent.KnowledgeSearchTool;
import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;
import dev.langchain4j.service.AiServices;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * LangChain4j 配置类
 * 配置 ChatModel、AiServices
 */
@Configuration
public class LangChain4jConfig {

    @Value("${spring.ai.openai.api-key:}")
    private String apiKey;

    @Value("${spring.ai.openai.base-url:https://api.deepseek.com}")
    private String baseUrl;

    @Value("${spring.ai.openai.chat.options.model:deepseek-chat}")
    private String modelName;

    /**
     * ChatModel - 使用 DeepSeek API（兼容 OpenAI 格式）
     */
    @Bean
    public ChatModel chatModel() {
        return OpenAiChatModel.builder()
            .apiKey(apiKey)
            .baseUrl(baseUrl)
            .modelName(modelName)
            .temperature(0.7)
            .build();
    }

    /**
     * StreamingChatModel - 流式输出
     */
    @Bean
    public StreamingChatModel streamingChatModel() {
        return OpenAiStreamingChatModel.builder()
            .apiKey(apiKey)
            .baseUrl(baseUrl)
            .modelName(modelName)
            .temperature(0.7)
            .build();
    }

    /**
     * ChatMemoryProvider - 按 sessionId 隔离对话记忆
     */
    @Bean
    public ChatMemoryProvider chatMemoryProvider() {
        return memoryId -> MessageWindowChatMemory.withMaxMessages(50);
    }

    /**
     * ChatService - 主对话服务（带工具调用）
     */
    @Bean
    public ChatService chatService(ChatModel chatModel, KnowledgeSearchTool knowledgeSearchTool,
                                    ChatMemoryProvider chatMemoryProvider) {
        return AiServices.builder(ChatService.class)
            .chatModel(chatModel)
            .chatMemoryProvider(chatMemoryProvider)
            .tools(knowledgeSearchTool)
            .build();
    }

    /**
     * IntentAnalysisService - 意图识别服务（不带工具）
     */
    @Bean
    public IntentAnalysisService intentAnalysisService(ChatModel chatModel) {
        return AiServices.builder(IntentAnalysisService.class)
            .chatModel(chatModel)
            .build();
    }
}
