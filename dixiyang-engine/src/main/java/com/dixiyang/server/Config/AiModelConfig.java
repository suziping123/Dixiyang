/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-24 11:09:30
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-24 11:15:15
 * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Config\AiModelConfig.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server.Config;

import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.ollama.OllamaEmbeddingModel;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

/**
 * AI 模型配置类
 * 解决多 AI 提供方（Ollama + DeepSeek）的冲突问题
 *
 * 架构设计：
 * - 聊天（Chat）：使用 DeepSeek（OpenAiChatModel）- 云端大模型能力强
 * - 向量化（Embedding）：使用 Ollama（OllamaEmbeddingModel）- 本地免费，nomic-embed-text 效果好
 */
@Configuration
public class AiModelConfig {

    /**
     * 优先使用 Ollama 作为向量化模型
     * 仅当 Ollama 启用时才创建此 Bean
     */
    @Bean
    @Primary
    @ConditionalOnBean(OllamaEmbeddingModel.class)
    public EmbeddingModel primaryEmbeddingModel(OllamaEmbeddingModel ollamaEmbeddingModel) {
        return ollamaEmbeddingModel;
    }

    /**
     * 优先使用 DeepSeek 作为聊天模型
     * ChatClient 默认会使用 @Primary 的 ChatModel，这里指定使用 OpenAiChatModel（DeepSeek 兼容）
     */
    @Bean
    @Primary
    public ChatModel primaryChatModel(OpenAiChatModel openAiChatModel) {
        return openAiChatModel;
    }
}
