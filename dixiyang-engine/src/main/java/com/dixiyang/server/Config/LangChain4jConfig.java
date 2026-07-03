package com.dixiyang.server.Config;

import com.dixiyang.server.Mapper.ChatSessionMapper;
import com.dixiyang.server.Service.ChatContentFileService;
import com.dixiyang.server.Service.chat.agent.ChatService;
import com.dixiyang.server.Service.chat.agent.FileBasedChatMemoryStore;
import com.dixiyang.server.Service.chat.agent.KnowledgeSearchTool;
import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * LangChain4j 配置类
 * 配置 ChatModel、ChatMemory、AiServices
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
     * ChatMemoryStore - 基于链文件的持久化存储
     */
    @Bean
    public ChatMemoryStore chatMemoryStore(ChatContentFileService fileService, ChatSessionMapper sessionMapper) {
        return new FileBasedChatMemoryStore(fileService, sessionMapper);
    }

    /**
     * ChatMemoryProvider - 按 sessionId 隔离对话记忆，使用持久化存储
     */
    @Bean
    public ChatMemoryProvider chatMemoryProvider(ChatMemoryStore chatMemoryStore) {
        return memoryId -> MessageWindowChatMemory.builder()
            .id(memoryId)
            .maxMessages(50)
            .chatMemoryStore(chatMemoryStore)
            .build();
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
}
