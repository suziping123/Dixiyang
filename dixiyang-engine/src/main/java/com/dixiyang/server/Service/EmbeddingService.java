package com.dixiyang.server.Service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 向量嵌入服务
 * 负责将文本转换为向量并存入 Qdrant 向量数据库
 * 注意：此服务为可选服务，需要 Ollama 和 Qdrant 支持
 */
@Service
@Slf4j
public class EmbeddingService {
    @Autowired(required = false)
    private final VectorStore vectorStore;
    private final boolean enabled;

    // 利用 Spring 的构造注入 VectorStore（可选）
    @Autowired(required = false)
    public EmbeddingService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
        this.enabled = (vectorStore != null);
        if (!enabled) {
            log.warn("⚠️ 向量存储服务未启用（Ollama/Qdrant 未配置），EmbeddingService 功能不可用");
        }
    }

    // 无参构造器，用于 VectorStore 不可用时
    public EmbeddingService() {
        this.vectorStore = null;
        this.enabled = false;
        log.warn("⚠️ 向量存储服务未启用（Ollama/Qdrant 未配置），EmbeddingService 功能不可用");
    }

    /**
     * 生成文本的向量嵌入并存储到向量数据库
     * @param content 文本内容
     * @return 向量ID（Document ID）
     */
    public String generateEmbedding(String content) {
        if (!enabled) {
            log.warn("向量存储服务未启用，无法生成 embedding");
            return null;
        }
        
        // 创建 Document 对象（Spring AI 1.0.0-M5 使用 builder 模式）
        Document document = Document.builder()
                .text(content)
                .metadata(Map.of("type", "story_node"))
                .build();
        
        // 存入向量数据库（自动调用 EmbeddingModel 生成向量）
        vectorStore.add(List.of(document));
        
        // 返回 Document ID 作为向量标识（使用 getId() 方法）
        return document.getId();
    }

    /**
     * 根据向量ID删除向量嵌入
     * @param vectorId 向量ID
     */
    public void deleteEmbedding(String vectorId) {
        if (!enabled) {
            log.warn("向量存储服务未启用，无法删除 embedding");
            return;
        }
        vectorStore.delete(List.of(vectorId));
    }

    /**
     * 相似度搜索
     * @param query 搜索查询
     * @return 相似的文档列表
     */
    public List<Document> similaritySearch(String query) {
        if (!enabled) {
            log.debug("向量存储服务未启用，返回空列表");
            return List.of();
        }
        return vectorStore.similaritySearch(query);
    }
}