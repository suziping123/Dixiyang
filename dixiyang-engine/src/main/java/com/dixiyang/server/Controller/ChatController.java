    /*
    * @Author: suziping123 yunzhiming123@gmail.com
    * @Date: 2026-03-17 22:24:29
    * @LastEditors: suziping123 yunzhiming123@gmail.com
    * @LastEditTime: 2026-03-23 20:59:51
    * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Controller\ChatController.java
    * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
    */
    package com.dixiyang.server.Controller;

    import lombok.extern.slf4j.Slf4j;
    import org.springframework.ai.chat.client.ChatClient;
    import org.springframework.ai.document.Document;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.PostMapping;
    import org.springframework.web.bind.annotation.RequestBody;
    import org.springframework.web.bind.annotation.RequestParam;
    import org.springframework.web.bind.annotation.RestController;
    import io.swagger.v3.oas.annotations.tags.Tag;
    import com.dixiyang.server.Service.EmbeddingService;
    import com.dixiyang.server.Service.INovelCharacterService;
    import com.dixiyang.server.Service.IStoryNodeService;
    import com.dixiyang.server.Entity.NovelCharacter;
    import com.dixiyang.server.Entity.StoryNode;
    import com.dixiyang.server.Entity.dto.ChatRequest;

    import java.util.List;
    import java.util.stream.Collectors;

    /**
     * AI 聊天控制器
     * 基于 RAG (检索增强生成) 实现与大语言模型的对话
     * 流程：用户提问 -> 向量检索相关上下文 -> 结合上下文提问 AI
     */
    @Tag(name = "聊天模块")
    @RestController
    @Slf4j
    public class ChatController {
        
        private final ChatClient chatClient;
        private final EmbeddingService embeddingService;
        private final INovelCharacterService characterService;
        private final IStoryNodeService storyNodeService;
        private final boolean ragEnabled;

        // 注入所需依赖（EmbeddingService 为可选）
        public ChatController(ChatClient.Builder builder, 
                            @Autowired(required = false) EmbeddingService embeddingService,
                            INovelCharacterService characterService,
                            IStoryNodeService storyNodeService) {
            this.chatClient = builder.build();
            this.embeddingService = embeddingService;
            this.characterService = characterService;
            this.storyNodeService = storyNodeService;
            this.ragEnabled = (embeddingService != null);
            if (!ragEnabled) {
                log.warn("⚠️ RAG 功能已禁用（向量存储未配置），仅使用数据库上下文");
            }
        }

        /**
         * RAG 聊天接口（GET 方式，适用于短文本）
         * @param message 用户提问
         * @param useRag 是否启用 RAG 检索（默认 true）
         * @return AI 回答
         */
        @GetMapping("/chat")
        public String chatGet(@RequestParam String message,
                            @RequestParam(defaultValue = "true") boolean useRag) {
            return processChat(message, useRag);
        }

        /**
         * RAG 聊天接口（POST 方式，推荐使用 - 支持传 ID 从数据库构建上下文）
         * @param request 聊天请求，可包含：message、useRag、characterIds、storyNodeIds 等
         * @return AI 回答
         */
        @PostMapping("/chat")
        public String chatPost(@RequestBody ChatRequest request) {
            return processChat(request);
        }

        /**
         * 处理聊天请求的核心逻辑（新版本 DTO）
         */
        private String processChat(ChatRequest request) {
            // 1. 构建数据库上下文（根据 ID 查询获取完整数据）
            String dbContext = buildContextFromDatabase(request);
            
            // 2. 构建最终的 Prompt
            String finalMessage = request.getMessage();
            String fullPrompt = finalMessage;
            
            if (dbContext != null && !dbContext.isEmpty()) {
                fullPrompt = dbContext + "\n\n用户需求：" + finalMessage;
            }
            
            // 3. RAG 检索增强（可选）
            if (ragEnabled && request.getUseRag() != null && request.getUseRag()) {
                try {
                    List<Document> relatedDocs = embeddingService.similaritySearch(finalMessage);
                    
                    if (!relatedDocs.isEmpty()) {
                        String ragContext = relatedDocs.stream()
                                .map(Document::getText)
                                .collect(Collectors.joining("\n---\n"));
                        
                        fullPrompt = String.format(
                                "【参考资料】\n%s\n\n%s\n\n用户需求：%s\n\n请基于以上信息回答用户的问题。如果参考资料与问题相关，请重点参考；如不相关，可忽略。",
                                ragContext, dbContext, finalMessage
                        );
                    }
                } catch (Exception e) {
                    log.error("RAG 检索失败，仅使用数据库上下文: {}", e.getMessage(), e);
                    // 继续使用仅数据库上下文的模式
                }
            }
            
            // 4. 调用 AI 服务
            try {
                return chatClient.prompt(fullPrompt).call().content();
            } catch (Exception e) {
                System.out.println("AI 服务调用失败，返回模拟响应: " + e.getMessage());
                e.printStackTrace();
                return generateMockResponse(fullPrompt);
            }
        }

        /**
         * 从数据库构建上下文信息（推荐架构：前端传 ID，后端查数据）
         */
        private String buildContextFromDatabase(ChatRequest request) {
            StringBuilder context = new StringBuilder();
            
            // 包含角色信息
            if (request.getIncludeCharacters() != null && request.getIncludeCharacters() 
                    && request.getCharacterIds() != null && !request.getCharacterIds().isEmpty()) {
                List<NovelCharacter> characters = characterService.listByIds(request.getCharacterIds());
                
                if (!characters.isEmpty()) {
                    context.append("【角色信息】\n");
                    for (NovelCharacter charac : characters) {
                        context.append("- ").append(charac.getName());
                        context.append("（").append(charac.getGender() != null ? charac.getGender() : "性别未知");
                        context.append("，").append(charac.getAge() != null ? charac.getAge() + "岁" : "年龄未知").append("）:\n");
                        if (charac.getAppearance() != null) context.append("  * 外貌：").append(charac.getAppearance()).append("\n");
                        if (charac.getPersonality() != null) context.append("  * 性格：").append(charac.getPersonality()).append("\n");
                        if (charac.getBackground() != null) context.append("  * 背景：").append(charac.getBackground()).append("\n");
                    }
                    context.append("\n");
                }
            }
            
            // 包含故事节点
            if (request.getIncludeStory() != null && request.getIncludeStory() 
                    && request.getStoryNodeIds() != null && !request.getStoryNodeIds().isEmpty()) {
                List<StoryNode> nodes = storyNodeService.listByIds(request.getStoryNodeIds());
                
                if (!nodes.isEmpty()) {
                    context.append("【故事节点】\n");
                    for (StoryNode node : nodes) {
                        context.append("- ").append(node.getTitle()).append(":\n");
                        if (node.getContent() != null) context.append("  内容：").append(node.getContent()).append("\n");
                    }
                    context.append("\n");
                }
            }
            
            return context.toString();
        }

        /**
         * 兼容旧版接口：纯文本消息
         */
        private String processChat(String message, boolean useRag) {
            ChatRequest request = new ChatRequest();
            request.setMessage(message);
            request.setUseRag(useRag);
            return processChat(request);
        }

        /**
         * 生成模拟响应（用于 AI 服务不可用时的演示）
         */
        private String generateMockResponse(String message) {
            // 简单的角色分析模拟
            if (message.contains("分析") && (message.contains("性格") || message.contains("角色"))) {
                return "【模拟响应 - AI 服务暂时不可用】\n\n" +
                    "注：此为模拟响应，实际 AI 服务恢复后将提供更专业的分析。";
            }
            
            return "【模拟响应 - AI 服务暂时不可用】\n\n" +
                "系统已收到您的请求：\n「" + (message.length() > 100 ? message.substring(0, 100) + "..." : message) + "」\n\n" +
                "由于 AI 服务临时限制，无法提供实时回答。\n" +
                "请稍后重试，或检查系统配置。";
        }
    }