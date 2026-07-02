package com.dixiyang.server.Service.chat.agent;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;

/**
 * 对话服务 - LangChain4j AiService
 * 自动管理对话历史、工具调用、Prompt 构建
 */
public interface ChatService {

    @SystemMessage("""
        你是小说创作助手。你具备以下能力：
        - 创作：按设定写剧情/对话/描写/续写
        - 讨论：回答关于角色、世界观、大纲的设定问题
        - 分析：分析角色性格、剧情逻辑、世界观一致性
        - 检索：使用 knowledge_search 工具查阅设定细节

        严格遵循【固定设定】与【对话历史】。
        根据用户意图切换模式：用户问设定就讨论设定，用户要创作就写内容。不要答非所问。
        【核心规则】对于设定、数据、细节不确定时，明确说"我不确定"或反问用户，不要编造。
        """)
    @UserMessage("{{userMessage}}")
    String chat(@MemoryId String sessionId, @UserMessage String userMessage);
}
