package com.dixiyang.server.Entity.dto;

import lombok.Data;
import java.util.List;

/**
 * 聊天请求 DTO
 * 优化架构：前端仅传递 ID 引用，后端从数据库获取完整数据
 */
@Data
public class ChatRequest {
    // 用户问题
    private String message;
    // 是否启用 RAG 检索
    private Boolean useRag = true;
    // 小说 ID
    private Long novelId;
    // 选中的角色 ID 列表
    private List<Long> characterIds;
    // 选中的故事节点 ID 列表
    private List<Long> storyNodeIds;
    // 是否包含角色信息
    private Boolean includeCharacters = true;
    // 是否包含故事节点
    private Boolean includeStory = true;
    // 会话ID（用于编辑上下文注入、重新生成等）
    private String sessionId;
    // 重新生成时指定消息索引（-1 表示普通对话）
    private Integer regenerateIndex = -1;
    // 对话模式：WRITE/DISCUSS/ANALYZE/BRAINSTORM/ASK（默认 WRITE）
    private String conversationMode = "WRITE";
    // 用户自定义创造性（0.0-1.0）
    private Double temperature;
    // 用户自定义最大输出长度
    private Integer maxTokens;
    // 用户自定义 system prompt 追加
    private String customSystemPrompt;
}