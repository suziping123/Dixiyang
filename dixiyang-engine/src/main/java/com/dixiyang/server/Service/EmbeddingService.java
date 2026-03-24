package com.dixiyang.server.Service;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 向量嵌入服务
 * 负责将文本转换为向量并存入 Qdrant 向量数据库
 */
@Service
public class EmbeddingService {

    private final VectorStore vectorStore;

    // 利用 Spring 的构造注入 VectorStore
    public EmbeddingService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    /**
     * 生成文本的向量嵌入并存储到向量数据库
     * @param content 文本内容
     * @return 向量ID（Document ID）
     */
    public String generateEmbedding(String content) {
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
        vectorStore.delete(List.of(vectorId));
    }

    /**
     * 相似度搜索
     * @param query 搜索查询
     * @return 相似的文档列表
     */
    public List<Document> similaritySearch(String query) {
        return vectorStore.similaritySearch(query);
    }
}