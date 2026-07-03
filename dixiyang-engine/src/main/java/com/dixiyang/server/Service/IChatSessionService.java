package com.dixiyang.server.Service;

import com.dixiyang.server.Entity.ChatSession;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;
import java.util.Map;

public interface IChatSessionService extends IService<ChatSession> {
    List<ChatSession> getSessionsByUser(Long userId, Long novelId);
    List<Map<String, Object>> getSessionMessages(String sessionId, Long userId);
    List<Map<String, Object>> getSessionMessagesWithEdits(String sessionId, Long userId);
    boolean appendMessages(Long userId, Long novelId, String sessionId, List<Map<String, Object>> messages);
    boolean deleteSession(String sessionId, Long userId);
    boolean updateTitle(String sessionId, Long userId, String title);
    String generateAndUpdateTitle(String sessionId, Long userId);
    boolean editMessage(Long userId, String sessionId, int messageIndex, String role, String newContent);
    String buildEditContextPrompt(Long userId, String sessionId);
    boolean truncateSessionChain(Long userId, String sessionId, int keepCount);
    Map<String, Object> getSummary(Long userId, String sessionId);
    void maybeSummarize(Long userId, String sessionId);
}
