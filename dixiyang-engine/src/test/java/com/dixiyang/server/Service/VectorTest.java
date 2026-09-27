package com.dixiyang.server.Service;

import org.junit.jupiter.api.Test;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import org.springframework.ai.document.Document; // 必须是这个
import java.util.List;
import java.util.Map;

/**
 * @author SuZiPing
 * @version 1.0
 */
@SpringBootTest
class VectorTest {

    @Autowired
    private VectorStore vectorStore;

    @Test
    void testVectorStore() {
        // 1. 创建一些文档
        List<Document> documents = List.of(
                new Document("Spring AI 真是太好用了！", Map.of("category", "tech")),
                new Document("今天天气不错，适合写代码。", Map.of("category", "life"))
                );

        // 2. 存入 Qdrant (这一步会自动调用 Embedding 模型转换成向量)
        vectorStore.add(documents);

        System.out.println("写入成功！");

        // 3. 相似度搜索
        List<Document> results = vectorStore.similaritySearch("AI工具");
        results.forEach(doc -> System.out.println("搜索结果: " + doc.getContent()));
    }
}