package com.dixiyang.server.Service.impl;

import com.dixiyang.server.Entity.ChatSession;
import com.dixiyang.server.Mapper.ChatSessionMapper;
import com.dixiyang.server.Service.ChatContentFileService;
import com.dixiyang.server.Service.IChatSessionService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
public class ChatSessionServiceImpl extends ServiceImpl<ChatSessionMapper, ChatSession> implements IChatSessionService {

    @Autowired
    private ChatContentFileService fileService;

    @Autowired
    private ChatClient.Builder chatClientBuilder;

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
        // 记录原始内容用于 AI 学习
        record.put("originalContent", target.get("originalContent") != null ? target.get("originalContent") : "");

        fileService.addEditRecord(userId, sessionId, record);
        log.info("编辑消息: sessionId={}, index={}", sessionId, messageIndex);
        return true;
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
            String title = chatClientBuilder.build().prompt(prompt).call().content();
            if (title == null || title.isBlank()) return null;
            title = title.trim();

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

    private ChatSession findOwnedSession(String sessionId, Long userId) {
        LambdaQueryWrapper<ChatSession> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatSession::getSessionId, sessionId)
               .eq(ChatSession::getUserId, userId);
        return this.getOne(wrapper);
    }
}
