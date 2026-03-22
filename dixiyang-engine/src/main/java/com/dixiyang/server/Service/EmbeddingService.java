package com.dixiyang.server.Service;

import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.stereotype.Service;

@Service
public class EmbeddingService {

    private final EmbeddingModel embeddingModel;

    // 这里利用 Spring 的构造注入，Spring 会自动把配置文件里的 OpenAI/DashScope EmbeddingModel 传进来
    public EmbeddingService(EmbeddingModel embeddingModel) {
        this.embeddingModel = embeddingModel;
    }

    public float[] getVector(String text) {
        // embed 方法返回 float[]，这是存入 Qdrant 的标准格式
        return embeddingModel.embed(text);
    }
}