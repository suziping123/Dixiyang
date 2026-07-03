package com.dixiyang.server.Service.impl;

import com.dixiyang.server.Entity.ChatSession;
import com.dixiyang.server.Mapper.ChatSessionMapper;
import com.dixiyang.server.Service.ChatContentFileService;
import com.dixiyang.server.Service.IChatSessionService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.request.ChatRequest;
import dev.langchain4j.model.chat.response.ChatResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

@Slf4j
@Service
public class ChatSessionServiceImpl extends ServiceImpl<ChatSessionMapper, ChatSession> implements IChatSessionService {

    @Autowired
    private ChatContentFileService fileService;

    @Autowired
    private ChatModel chatModel;

    @Override
    public List<ChatSession> getSessionsByUser(Long userId, Long novelId) {
        LambdaQueryWrapper<ChatSession> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatSession::getUserId, userId)
               .eq(ChatSession::getNovelId, novelId)
               .orderByDesc(ChatSession::getUpdateTime);
        return this.list(wrapper);
    }

    @Override
    public List<Map<String, Object>> getSessionMessages(String sessionId, Long userId) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null) return Collections.emptyList();
        return fileService.readChain(session.getHeadPath());
    }

    @Override
    public boolean appendMessages(Long userId, Long novelId, String sessionId, List<Map<String, Object>> messages) {
        if (messages == null || messages.isEmpty()) return true;

        LambdaQueryWrapper<ChatSession> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatSession::getSessionId, sessionId)
               .eq(ChatSession::getUserId, userId);
        ChatSession session = this.getOne(wrapper);

        String headPath;
        boolean isNew = session == null;

        if (isNew) {
            headPath = fileService.append(userId, sessionId, null, messages, "新对话");
            session = new ChatSession();
            session.setUserId(userId);
            session.setNovelId(novelId);
            session.setSessionId(sessionId);
            session.setHeadPath(headPath);
            session.setTitle("新对话");
            session.setCreateTime(LocalDateTime.now());
            session.setUpdateTime(LocalDateTime.now());
            return this.save(session);
        } else {
            headPath = fileService.append(userId, sessionId, session.getHeadPath(), messages, null);
            session.setHeadPath(headPath);
            session.setUpdateTime(LocalDateTime.now());
            if (session.getTitle() == null) {
                fileService.updateTitle(headPath, "新对话");
                session.setTitle("新对话");
            }
            return this.updateById(session);
        }
    }

    @Override
    public boolean deleteSession(String sessionId, Long userId) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null) return false;
        if (session.getHeadPath() != null) {
            fileService.deleteChain(session.getHeadPath());
            fileService.deleteSessionDir(userId, sessionId);
        }
        return this.removeById(session.getId());
    }

    @Override
    public boolean updateTitle(String sessionId, Long userId, String title) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null) return false;
        session.setTitle(title);
        if (session.getHeadPath() != null) {
            fileService.updateTitle(session.getHeadPath(), title);
        }
        return this.updateById(session);
    }

    @Override
    public List<Map<String, Object>> getSessionMessagesWithEdits(String sessionId, Long userId) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null) return Collections.emptyList();
        List<Map<String, Object>> messages = fileService.readChain(session.getHeadPath());
        return fileService.mergeEdits(messages, userId, sessionId);
    }

    @Override
    public boolean editMessage(Long userId, String sessionId, int messageIndex, String role, String newContent) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null || session.getHeadPath() == null) return false;

        // 1. 直接修改链文件中该消息的内容
        List<Map<String, Object>> updated = fileService.replaceMessageInChain(session.getHeadPath(), messageIndex, newContent);
        if (updated == null || messageIndex >= updated.size()) return false;

        // 2. 记录修正到 edits.json（供 AI 后续学习）
        Map<String, Object> target = updated.get(messageIndex);
        Map<String, Object> record = new LinkedHashMap<>();
        record.put("messageIndex", messageIndex);
        record.put("role", role != null ? role : target.get("role"));
        record.put("editedContent", newContent);
        record.put("timestamp", LocalDateTime.now().toString());
        record.put("version", target.get("version") instanceof Number ? ((Number) target.get("version")).intValue() : 1);
        record.put("originalContent", target.get("originalContent") != null ? target.get("originalContent") : "");

        fileService.addEditRecord(userId, sessionId, record);
        log.info("编辑消息: sessionId={}, index={}", sessionId, messageIndex);

        // 3. 异步提取修正要点（不阻塞响应）
        int editIndex = fileService.readEdits(userId, sessionId).size() - 1;
        String original = record.get("originalContent") != null ? (String) record.get("originalContent") : "";
        extractKeyPointsAsync(userId, sessionId, editIndex, original, newContent);

        return true;
    }

    /**
     * 异步调用 LLM 提取编辑修正的要点和错误类型
     */
    private void extractKeyPointsAsync(Long userId, String sessionId, int editIndex,
                                        String originalContent, String editedContent) {
        if (originalContent.isBlank() || editedContent.isBlank()) return;

        CompletableFuture.runAsync(() -> {
            try {
                String prompt = """
                    你是修正要点提取器。对比以下 AI 原始输出和用户修正后的内容，提取修正要点。

                    AI 原始输出：%s

                    用户修正后：%s

                    请返回 JSON（不要 markdown 包裹）：
                    {"keyPoint":"一句话总结修正要点（30字以内）","errorType":"错误类型"}

                    错误类型只能是以下之一：
                    - FACT_ERROR（事实/数据错误）
                    - SETTING_VIOLATION（违背设定）
                    - TONE_WRONG（语气/风格不对）
                    - TOO_LONG（太啰嗦）
                    - OFF_TOPIC（答非所问）
                    - OTHER（其他）

                    只返回 JSON，不要任何解释。""".formatted(
                        originalContent.length() > 500 ? originalContent.substring(0, 500) : originalContent,
                        editedContent.length() > 500 ? editedContent.substring(0, 500) : editedContent);

                ChatResponse response = chatModel.chat(ChatRequest.builder()
                    .messages(
                        SystemMessage.from("你是修正要点提取器，只返回 JSON。"),
                        UserMessage.from(prompt)
                    )
                    .build());

                String text = response.aiMessage().text().trim();
                // 解析 JSON
                if (text.contains("keyPoint") && text.contains("errorType")) {
                    String keyPoint = extractJsonField(text, "keyPoint");
                    String errorType = extractJsonField(text, "errorType");
                    if (keyPoint != null && errorType != null) {
                        fileService.updateEditKeyPoint(userId, sessionId, editIndex, keyPoint, errorType);
                        log.info("修正要点提取成功: sessionId={}, keyPoint={}", sessionId, keyPoint);
                    }
                }
            } catch (Exception e) {
                log.warn("修正要点提取失败: sessionId={}, error={}", sessionId, e.getMessage());
            }
        });
    }

    private String extractJsonField(String json, String field) {
        String marker = "\"" + field + "\"";
        int start = json.indexOf(marker);
        if (start < 0) return null;
        start = json.indexOf("\"", start + marker.length() + 1);
        if (start < 0) return null;
        int end = json.indexOf("\"", start + 1);
        if (end < 0) return null;
        return json.substring(start + 1, end);
    }

    @Override
    public String buildEditContextPrompt(Long userId, String sessionId) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null) return "";
        return fileService.buildEditsPrompt(userId, sessionId);
    }

    @Override
    public boolean truncateSessionChain(Long userId, String sessionId, int keepCount) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null || session.getHeadPath() == null) return false;
        String newHead = fileService.truncateChain(session.getHeadPath(), keepCount);
        session.setHeadPath(newHead);
        session.setUpdateTime(LocalDateTime.now());
        return this.updateById(session);
    }

    @Override
    public String generateAndUpdateTitle(String sessionId, Long userId) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null) return null;

        List<Map<String, Object>> messages = fileService.readChain(session.getHeadPath());
        if (messages == null || messages.isEmpty()) return null;

        StringBuilder conversation = new StringBuilder();
        int count = 0;
        for (Map<String, Object> msg : messages) {
            String role = (String) msg.get("role");
            String content = (String) msg.get("content");
            if (role != null && content != null) {
                conversation.append("user".equals(role) ? "用户：" : "AI：")
                    .append(content).append("\n");
                count++;
                if (count >= 2) break;
            }
        }

        String prompt = "你是一个对话标题生成器。请用 3-8 个字概括以下对话的主题，直接返回标题，不要任何解释、标点或引号。\n\n对话：\n" + conversation;

        try {
            ChatResponse response = chatModel.chat(ChatRequest.builder()
                .messages(
                    SystemMessage.from("你是对话标题生成器，只返回标题。"),
                    UserMessage.from(prompt)
                )
                .build());
            String title = response.aiMessage().text();
            if (title == null || title.isBlank()) return null;
            title = title.trim().replace("\"", "").replace("'", "");

            session.setTitle(title);
            this.updateById(session);
            if (session.getHeadPath() != null) {
                fileService.updateTitle(session.getHeadPath(), title);
            }
            log.info("AI 标题生成成功: sessionId={}, title={}", sessionId, title);
            return title;
        } catch (Exception e) {
            log.error("AI 标题生成失败: sessionId={}, error={}", sessionId, e.getMessage());
            return null;
        }
    }

    /**
     * 检查是否需要摘要：消息超过 12 条时，取前 6 条生成摘要并截断
     */
    public void maybeSummarize(Long userId, String sessionId) {
        ChatSession session = findOwnedSession(sessionId, userId);
        if (session == null || session.getHeadPath() == null) return;

        Map<String, Object> existing = fileService.readSummary(userId, sessionId);
        int summarizedCount = existing.get("lastMessageIndex") instanceof Number
            ? ((Number) existing.get("lastMessageIndex")).intValue() : 0;

        List<Map<String, Object>> messages = fileService.readChain(session.getHeadPath());
        if (messages == null) return;

        int totalMessages = messages.size();
        if (totalMessages < 12 || (totalMessages - summarizedCount) < 6) return;

        CompletableFuture.runAsync(() -> {
            try {
                List<Map<String, Object>> toSummarize = messages.subList(0, Math.min(6, messages.size()));
                StringBuilder conversation = new StringBuilder();
                for (Map<String, Object> msg : toSummarize) {
                    String role = "user".equals(msg.get("role")) ? "用户" : "AI";
                    String content = (String) msg.get("content");
                    if (content != null) {
                        conversation.append(role).append("：")
                            .append(content.length() > 200 ? content.substring(0, 200) + "..." : content)
                            .append("\n");
                    }
                }

                String prevSummary = existing.get("summary") != null ? (String) existing.get("summary") : "";
                String prompt = "请用 3-5 句话概括以下对话的核心内容（设定讨论、创作内容、关键决定）。直接返回摘要，不要解释。\n\n"
                    + (prevSummary.isEmpty() ? "" : "之前的摘要：" + prevSummary + "\n\n")
                    + "新对话内容：\n" + conversation;

                ChatResponse response = chatModel.chat(ChatRequest.builder()
                    .messages(
                        SystemMessage.from("你是对话摘要生成器，只返回摘要文本。"),
                        UserMessage.from(prompt)
                    )
                    .build());

                String summary = response.aiMessage().text();
                if (summary != null && !summary.isBlank()) {
                    fileService.saveSummary(userId, sessionId, summary.trim(), 6);
                    String newHead = fileService.truncateAfterSummary(session.getHeadPath(), 6);
                    if (newHead != null) {
                        session.setHeadPath(newHead);
                        this.updateById(session);
                    }
                    log.info("对话摘要生成成功: sessionId={}", sessionId);
                }
            } catch (Exception e) {
                log.warn("对话摘要生成失败: sessionId={}, error={}", sessionId, e.getMessage());
            }
        });
    }

    @Override
    public Map<String, Object> getSummary(Long userId, String sessionId) {
        return fileService.readSummary(userId, sessionId);
    }

    private ChatSession findOwnedSession(String sessionId, Long userId) {
        LambdaQueryWrapper<ChatSession> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatSession::getSessionId, sessionId)
               .eq(ChatSession::getUserId, userId);
        return this.getOne(wrapper);
    }
}
