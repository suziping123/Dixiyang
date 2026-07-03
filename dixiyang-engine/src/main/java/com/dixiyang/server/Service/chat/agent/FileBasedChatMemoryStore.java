package com.dixiyang.server.Service.chat.agent;

import com.dixiyang.server.Service.ChatContentFileService;
import com.dixiyang.server.Entity.ChatSession;
import com.dixiyang.server.Mapper.ChatSessionMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.store.memory.chat.ChatMemoryStore;
import lombok.extern.slf4j.Slf4j;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 基于链文件的 ChatMemoryStore 实现
 * 自动将 LangChain4j ChatMemory 与 storage/chat 链文件同步
 */
@Slf4j
public class FileBasedChatMemoryStore implements ChatMemoryStore {

    private final ChatContentFileService fileService;
    private final ChatSessionMapper sessionMapper;
    private final ConcurrentHashMap<String, List<ChatMessage>> cache = new ConcurrentHashMap<>();

    public FileBasedChatMemoryStore(ChatContentFileService fileService, ChatSessionMapper sessionMapper) {
        this.fileService = fileService;
        this.sessionMapper = sessionMapper;
    }

    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        String sessionId = memoryId.toString();
        return cache.computeIfAbsent(sessionId, this::loadFromChain);
    }

    @Override
    public void updateMessages(Object memoryId, List<ChatMessage> messages) {
        String sessionId = memoryId.toString();
        cache.put(sessionId, new ArrayList<>(messages));
        // 同步到链文件（保留最后一条 AI 消息用于链文件存储）
        syncToChain(sessionId, messages);
    }

    @Override
    public void deleteMessages(Object memoryId) {
        String sessionId = memoryId.toString();
        cache.remove(sessionId);
    }

    /**
     * 从链文件加载历史消息到 ChatMemory
     */
    private List<ChatMessage> loadFromChain(String sessionId) {
        List<ChatMessage> result = new ArrayList<>();
        try {
            ChatSession session = findSession(sessionId);
            if (session == null || session.getHeadPath() == null) return result;

            List<Map<String, Object>> messages = fileService.readChain(session.getHeadPath());
            if (messages == null) return result;

            for (Map<String, Object> msg : messages) {
                String role = (String) msg.get("role");
                String content = (String) msg.get("content");
                if (role == null || content == null) continue;

                switch (role) {
                    case "user" -> result.add(UserMessage.from(content));
                    case "assistant" -> result.add(AiMessage.from(content));
                }
            }
            log.debug("ChatMemory 加载: sessionId={}, messages={}", sessionId, result.size());
        } catch (Exception e) {
            log.warn("ChatMemory 加载失败: sessionId={}", sessionId, e);
        }
        return result;
    }

    /**
     * 将 ChatMemory 中的消息同步到链文件
     */
    private void syncToChain(String sessionId, List<ChatMessage> messages) {
        try {
            ChatSession session = findSession(sessionId);
            if (session == null) return;

            // 找到链文件中已有的消息数量
            List<Map<String, Object>> existing = fileService.readChain(session.getHeadPath());
            int existingCount = existing != null ? existing.size() : 0;

            // 只同步新增的消息
            if (messages.size() > existingCount) {
                List<ChatMessage> newMessages = messages.subList(existingCount, messages.size());
                List<Map<String, Object>> toSave = new ArrayList<>();
                for (ChatMessage msg : newMessages) {
                    Map<String, Object> map = new LinkedHashMap<>();
                    if (msg instanceof UserMessage um) {
                        map.put("role", "user");
                        map.put("content", um.singleText());
                    } else if (msg instanceof AiMessage am) {
                        map.put("role", "assistant");
                        map.put("content", am.text());
                    }
                    if (!map.isEmpty()) {
                        map.put("createTime", java.time.LocalDateTime.now().toString());
                        toSave.add(map);
                    }
                }
                if (!toSave.isEmpty()) {
                    fileService.append(session.getUserId(), sessionId, session.getHeadPath(), toSave, session.getTitle());
                }
            }
        } catch (Exception e) {
            log.warn("ChatMemory 同步到链文件失败: sessionId={}", sessionId, e);
        }
    }

    private ChatSession findSession(String sessionId) {
        LambdaQueryWrapper<ChatSession> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatSession::getSessionId, sessionId);
        return sessionMapper.selectOne(wrapper);
    }

    /**
     * 清除指定会话的缓存（编辑消息后调用）
     */
    public void invalidateCache(String sessionId) {
        cache.remove(sessionId);
    }
}
