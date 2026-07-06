package com.dixiyang.server.Service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
public class ChatContentFileService {

    private final ObjectMapper mapper = new ObjectMapper();
    private final ConcurrentHashMap<String, Object> locks = new ConcurrentHashMap<>();

    @Value("${app.chat.storage-path:/home/lijiajia/项目/Dixiyang/uploads/storage/chat}")
    private String baseDir;

    @Value("${app.chat.max-file-size:102400}")
    private long maxFileSize;

    private Object getLock(Long userId, String sessionId) {
        return locks.computeIfAbsent(userId + ":" + sessionId, k -> new Object());
    }

    /**
     * 解析 __file__: 前缀，返回实际文件路径
     * head_path 格式: __file__:chat/{userId}/{sessionId}/{file}.json
     * 相对于 storage 根目录（baseDir 的父目录）
     */
    private String resolvePath(String ref) {
        if (ref != null && ref.startsWith("__file__:")) {
            String relPath = ref.substring("__file__:".length());
            // baseDir = storage/chat, storage 根 = baseDir 的 parent
            String storageRoot = Paths.get(baseDir).getParent().toString();
            return Paths.get(storageRoot, relPath).toString();
        }
        return ref;
    }

    /**
     * 构建 __file__: 格式的引用路径
     */
    private String toRef(String absPath) {
        if (absPath == null) return null;
        String storageRoot = Paths.get(baseDir).getParent().toString();
        String prefix = storageRoot + "/";
        if (absPath.startsWith(prefix)) {
            return "__file__:" + absPath.substring(prefix.length());
        }
        return absPath;
    }

    public String append(Long userId, String sessionId, String headPath, List<Map<String, Object>> messages, String title) {
        synchronized (getLock(userId, sessionId)) {
            try {
                String dirPath = baseDir + "/" + userId + "/" + sessionId;
                Files.createDirectories(Paths.get(dirPath));

                if (headPath == null || headPath.isBlank()) {
                    String fileName = System.currentTimeMillis() + "_" + (int)(Math.random() * 10000) + ".json";
                    String newPath = dirPath + "/" + fileName;
                    Map<String, Object> data = new LinkedHashMap<>();
                    if (title != null) data.put("title", title);
                    data.put("messages", messages);
                    data.put("next", null);
                    writeFile(newPath, data);
                    return toRef(newPath);
                }

                String resolved = resolvePath(headPath);
                String tailPath = findTail(resolved);
                Map<String, Object> tail = readFile(tailPath);
                if (tail == null) return headPath;

                @SuppressWarnings("unchecked")
                List<Map<String, Object>> existing = (List<Map<String, Object>>) tail.get("messages");
                List<Map<String, Object>> merged = new ArrayList<>(existing != null ? existing : Collections.emptyList());
                merged.addAll(messages);

                // Preserve title from first file when updating tail
                String firstTitle = readTitle(resolved);
                Map<String, Object> updated = new LinkedHashMap<>();
                updated.put("messages", merged);
                updated.put("next", tail.get("next"));

                String serialized = mapper.writeValueAsString(updated);
                if (serialized.length() <= maxFileSize) {
                    writeFile(tailPath, updated);
                    return headPath;
                }

                String newPath = dirPath + "/" + System.currentTimeMillis() + "_" + (int)(Math.random() * 10000) + ".json";
                Map<String, Object> newData = new LinkedHashMap<>();
                newData.put("messages", messages);
                newData.put("next", null);
                writeFile(newPath, newData);

                String newFileName = Paths.get(newPath).getFileName().toString();
                tail.put("next", newFileName);
                writeFile(tailPath, tail);
                return headPath;

            } catch (IOException e) {
                log.error("追加聊天内容失败: userId={}, sessionId={}", userId, sessionId, e);
                return headPath;
            }
        }
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> readChain(String headPath) {
        if (headPath == null || headPath.isBlank()) return Collections.emptyList();
        String resolved = resolvePath(headPath);
        List<Map<String, Object>> all = new ArrayList<>();
        String current = resolved;
        while (current != null) {
            Map<String, Object> data = readFile(current);
            if (data == null) break;

            if (data.containsKey("messages")) {
                List<Map<String, Object>> msgs = (List<Map<String, Object>>) data.get("messages");
                if (msgs != null) all.addAll(msgs);
                String next = (String) data.get("next");
                current = (next != null) ? Paths.get(current).getParent().resolve(next).toString() : null;
            } else if (data.containsKey("content")) {
                Map<String, Object> msg = new LinkedHashMap<>();
                msg.put("role", "assistant");
                msg.put("content", data.getOrDefault("content", ""));
                msg.put("thinking", data.get("thinking"));
                msg.put("createTime", data.getOrDefault("createTime", ""));
                all.add(msg);
                break;
            } else {
                break;
            }
        }
        return all;
    }

    public boolean deleteChain(String headPath) {
        if (headPath == null || headPath.isBlank()) return true;
        String resolved = resolvePath(headPath);
        String current = resolved;
        boolean allOk = true;
        while (current != null) {
            Map<String, Object> data = readFile(current);
            try {
                Files.deleteIfExists(Paths.get(current));
            } catch (IOException e) {
                log.error("删除文件失败: {}", current, e);
                allOk = false;
            }
            String next = data != null ? (String) data.get("next") : null;
            current = (next != null && !next.isBlank()) ? Paths.get(current).getParent().resolve(next).toString() : null;
        }
        return allOk;
    }

    public boolean deleteSessionDir(Long userId, String sessionId) {
        String dirPath = baseDir + "/" + userId + "/" + sessionId;
        try {
            File dir = new File(dirPath);
            if (dir.exists()) {
                File[] files = dir.listFiles();
                if (files != null) {
                    for (File f : files) f.delete();
                }
                return dir.delete();
            }
            return true;
        } catch (Exception e) {
            log.error("删除会话目录失败: {}", dirPath, e);
            return false;
        }
    }

    private String findTail(String headPath) {
        String current = headPath;
        int maxDepth = 10000;
        int depth = 0;
        while (current != null && depth < maxDepth) {
            Map<String, Object> data = readFile(current);
            if (data == null) break;
            String next = (String) data.get("next");
            if (next == null || next.isBlank()) return current;
            current = Paths.get(current).getParent().resolve(next).toString();
            depth++;
        }
        return current;
    }

    public boolean updateTitle(String headPath, String title) {
        if (headPath == null || headPath.isBlank()) return false;
        String resolved = resolvePath(headPath);
        Map<String, Object> data = readFile(resolved);
        if (data == null) return false;
        if (title != null) {
            data.put("title", title);
        } else {
            data.remove("title");
        }
        try {
            writeFile(resolved, data);
            return true;
        } catch (IOException e) {
            log.error("更新标题失败: {}", headPath, e);
            return false;
        }
    }

    public String readTitle(String headPath) {
        if (headPath == null || headPath.isBlank()) return null;
        String resolved = resolvePath(headPath);
        Map<String, Object> data = readFile(resolved);
        return data != null ? (String) data.get("title") : null;
    }

    public void writeFile(String path, Object data) throws IOException {
        mapper.writerWithDefaultPrettyPrinter().writeValue(new File(path), data);
    }

    private Map<String, Object> readFile(String path) {
        try {
            File file = new File(path);
            if (!file.exists()) return null;
            return mapper.readValue(file, Map.class);
        } catch (IOException e) {
            log.error("读取文件失败: {}", path, e);
            return null;
        }
    }

    // ========== 链截断（用于重新生成） ==========
    /**
     * 保留链中前 keepCount 条消息，删除后续所有链文件并重写末尾文件
     * @return 新的 headPath（不变）
     */
    public String truncateChain(String headPath, int keepCount) {
        if (headPath == null || headPath.isBlank() || keepCount < 0) return headPath;
        String resolved = resolvePath(headPath);
        // 1. 读取全链
        List<ChainFileEntry> entries = walkChain(resolved);
        if (entries.isEmpty()) return headPath;

        int totalMessages = 0;
        for (ChainFileEntry entry : entries) {
            totalMessages += entry.messageCount;
        }
        if (keepCount >= totalMessages) return headPath; // 无需截断

        // 2. 找到截断点所在的文件
        int accumulated = 0;
        String lastKeptFile = null;
        List<String> toDelete = new ArrayList<>();
        boolean truncating = false;

        for (int i = 0; i < entries.size(); i++) {
            ChainFileEntry entry = entries.get(i);
            if (truncating) {
                toDelete.add(entry.filePath);
                continue;
            }
            int nextAccumulated = accumulated + entry.messageCount;
            if (nextAccumulated > keepCount) {
                // 截断点在此文件内
                int keepInFile = keepCount - accumulated;
                List<Map<String, Object>> keptMessages = entry.messages.subList(0, keepInFile);
                Map<String, Object> rewritten = new LinkedHashMap<>();
                rewritten.put("messages", keptMessages);
                rewritten.put("next", null);
                try {
                    writeFile(entry.filePath, rewritten);
                } catch (IOException e) {
                    log.error("重写截断文件失败: {}", entry.filePath, e);
                    return headPath;
                }
                lastKeptFile = entry.filePath;
                truncating = true;
                // 后续文件标记删除
                for (int j = i + 1; j < entries.size(); j++) {
                    toDelete.add(entries.get(j).filePath);
                }
            } else {
                // 整个文件保留，但清空next为后面可能删文件做准备
                lastKeptFile = entry.filePath;
                accumulated = nextAccumulated;
            }
        }

        // 3. 更新最后一个保留文件的next为null
        if (lastKeptFile != null) {
            Map<String, Object> lastData = readFile(lastKeptFile);
            if (lastData != null) {
                lastData.put("next", null);
                try {
                    writeFile(lastKeptFile, lastData);
                } catch (IOException e) {
                    log.error("更新末文件next=null失败: {}", lastKeptFile, e);
                }
            }
        }

        // 4. 删除截断后的文件
        for (String path : toDelete) {
            try {
                Files.deleteIfExists(Paths.get(path));
                log.info("删除截断链文件: {}", path);
            } catch (IOException e) {
                log.warn("删除截断链文件失败: {}", path, e);
            }
        }

        return headPath;
    }

    // ========== 链中消息替换（直接修改，用于编辑） ==========
    /**
     * 替换链中指定索引的消息内容，不改变文件结构
     * @return 更新后的完整消息列表
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> replaceMessageInChain(String headPath, int messageIndex, String newContent) {
        if (headPath == null || headPath.isBlank() || messageIndex < 0) return null;
        String resolved = resolvePath(headPath);

        List<ChainFileEntry> entries = walkChain(resolved);
        int accumulated = 0;

        for (ChainFileEntry entry : entries) {
            int nextAccumulated = accumulated + entry.messageCount;
            if (messageIndex < nextAccumulated) {
                int localIdx = messageIndex - accumulated;
                Map<String, Object> msg = entry.messages.get(localIdx);
                msg.put("content", newContent);
                msg.put("edited", true);
                msg.put("version", msg.get("version") instanceof Number ? ((Number) msg.get("version")).intValue() + 1 : 1);
                entry.messages.set(localIdx, msg);

                Map<String, Object> fileData = readFile(entry.filePath);
                if (fileData != null) {
                    fileData.put("messages", entry.messages);
                    try {
                        writeFile(entry.filePath, fileData);
                    } catch (IOException e) {
                        log.error("重写编辑文件失败: {}", entry.filePath, e);
                        return null;
                    }
                }

                // 返回完整消息列表（含更新）
                List<Map<String, Object>> all = new ArrayList<>();
                for (ChainFileEntry e : entries) all.addAll(e.messages);
                return all;
            }
            accumulated = nextAccumulated;
        }
        return null;
    }

    // ========== edits.json 操作（编辑修正记录） ==========

    public String getEditsFilePath(Long userId, String sessionId) {
        return baseDir + "/" + userId + "/" + sessionId + "/edits.json";
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> readEdits(Long userId, String sessionId) {
        File f = new File(getEditsFilePath(userId, sessionId));
        if (!f.exists()) return Collections.emptyList();
        try {
            Map<String, Object> data = mapper.readValue(f, Map.class);
            Object edits = data.get("edits");
            return edits instanceof List ? (List<Map<String, Object>>) edits : Collections.emptyList();
        } catch (IOException e) {
            log.error("读取edits.json失败: userId={}, sessionId={}", userId, sessionId, e);
            return Collections.emptyList();
        }
    }

    public void addEditRecord(Long userId, String sessionId, Map<String, Object> record) {
        File f = new File(getEditsFilePath(userId, sessionId));
        List<Map<String, Object>> edits = new ArrayList<>();
        if (f.exists()) {
            edits.addAll(readEdits(userId, sessionId));
        }
        edits.add(record);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("edits", edits);
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(f, data);
            log.info("edits.json已更新: userId={}, sessionId={}, index={}",
                userId, sessionId, record.get("messageIndex"));
        } catch (IOException e) {
            log.error("写入edits.json失败: userId={}, sessionId={}", userId, sessionId, e);
        }
    }

    /**
     * 构建注入到AI prompt的修正记录上下文（结构化要点格式）
     */
    public String buildEditsPrompt(Long userId, String sessionId) {
        List<Map<String, Object>> edits = readEdits(userId, sessionId);
        if (edits.isEmpty()) return "";

        StringBuilder sb = new StringBuilder();
        sb.append("\n【修正要点·必须避免重复犯错】\n");
        for (Map<String, Object> edit : edits) {
            String keyPoint = (String) edit.get("keyPoint");
            String errorType = (String) edit.get("errorType");
            if (keyPoint != null && !keyPoint.isBlank()) {
                String tag = errorType != null ? "[" + errorType + "]" : "[修正]";
                sb.append("- ").append(tag).append(" ").append(keyPoint).append("\n");
            } else {
                // 兼容旧格式：没有 keyPoint 时用 editedContent
                String edited = (String) edit.get("editedContent");
                if (edited != null && !edited.isBlank()) {
                    sb.append("- [修正] ").append(edited.length() > 100 ? edited.substring(0, 100) + "..." : edited).append("\n");
                }
            }
        }
        sb.append("请严格遵守以上修正要点，在本次回答中避免重复犯错。");
        return sb.toString();
    }

    /**
     * 更新指定编辑记录的 keyPoint 和 errorType（LLM 异步提取后调用）
     */
    @SuppressWarnings("unchecked")
    public void updateEditKeyPoint(Long userId, String sessionId, int editIndex, String keyPoint, String errorType) {
        List<Map<String, Object>> edits = readEdits(userId, sessionId);
        if (editIndex < 0 || editIndex >= edits.size()) return;

        Map<String, Object> edit = new LinkedHashMap<>(edits.get(editIndex));
        edit.put("keyPoint", keyPoint);
        edit.put("errorType", errorType);
        edits.set(editIndex, edit);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("edits", edits);
        try {
            File f = new File(getEditsFilePath(userId, sessionId));
            mapper.writerWithDefaultPrettyPrinter().writeValue(f, data);
            log.info("edits.json keyPoint 已更新: sessionId={}, index={}", sessionId, editIndex);
        } catch (IOException e) {
            log.error("更新 edits.json keyPoint 失败: sessionId={}", sessionId, e);
        }
    }

    /**
     * 将 edits.json 的修正合并到消息列表中（返回新列表，不改原数据）
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> mergeEdits(List<Map<String, Object>> messages, Long userId, String sessionId) {
        List<Map<String, Object>> edits = readEdits(userId, sessionId);
        if (edits.isEmpty()) return messages;

        List<Map<String, Object>> result = new ArrayList<>(messages);
        for (Map<String, Object> edit : edits) {
            int idx = edit.get("messageIndex") instanceof Number ? ((Number) edit.get("messageIndex")).intValue() : -1;
            if (idx >= 0 && idx < result.size()) {
                Map<String, Object> msg = new LinkedHashMap<>(result.get(idx));
                msg.put("content", edit.get("editedContent"));
                msg.put("edited", true);
                msg.put("version", edit.get("version"));
                result.set(idx, msg);
            }
        }
        return result;
    }

    // ========== 内部辅助 ==========

    /** 链文件条目（walkChain 用） */
    // ==================== 历史摘要 ====================

    private String getSummaryFilePath(Long userId, String sessionId) {
        return baseDir + "/" + userId + "/" + sessionId + "/summary.json";
    }

    /**
     * 读取历史摘要
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> readSummary(Long userId, String sessionId) {
        File f = new File(getSummaryFilePath(userId, sessionId));
        if (!f.exists()) return Collections.emptyMap();
        try {
            return mapper.readValue(f, Map.class);
        } catch (IOException e) {
            log.error("读取 summary.json 失败: sessionId={}", sessionId, e);
            return Collections.emptyMap();
        }
    }

    /**
     * 保存/更新历史摘要
     */
    public void saveSummary(Long userId, String sessionId, String summary, int lastMessageIndex) {
        synchronized (getLock(userId, sessionId)) {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("summary", summary);
            data.put("lastMessageIndex", lastMessageIndex);
            data.put("updatedAt", java.time.LocalDateTime.now().toString());
            try {
                File f = new File(getSummaryFilePath(userId, sessionId));
                f.getParentFile().mkdirs();
                mapper.writerWithDefaultPrettyPrinter().writeValue(f, data);
                log.info("summary.json 已更新: sessionId={}, lastMessageIndex={}", sessionId, lastMessageIndex);
            } catch (IOException e) {
                log.error("写入 summary.json 失败: sessionId={}", sessionId, e);
            }
        }
    }

    /**
     * 删除已摘要的早期消息，保留 lastMessageIndex 之后的消息
     */
    public String truncateAfterSummary(String headPath, int keepFromIndex) {
        return truncateChain(headPath, keepFromIndex);
    }

    // ==================== 内部类 ====================

    private static class ChainFileEntry {
        String filePath;
        List<Map<String, Object>> messages;
        int messageCount;

        ChainFileEntry(String filePath, List<Map<String, Object>> messages) {
            this.filePath = filePath;
            this.messages = messages;
            this.messageCount = messages != null ? messages.size() : 0;
        }
    }

    @SuppressWarnings("unchecked")
    private List<ChainFileEntry> walkChain(String headPath) {
        List<ChainFileEntry> entries = new ArrayList<>();
        String current = headPath;
        while (current != null) {
            Map<String, Object> data = readFile(current);
            if (data == null) break;
            Object msgs = data.get("messages");
            if (msgs instanceof List) {
                entries.add(new ChainFileEntry(current, (List<Map<String, Object>>) msgs));
                String next = (String) data.get("next");
                current = (next != null && !next.isBlank()) ? Paths.get(current).getParent().resolve(next).toString() : null;
            } else {
                break;
            }
        }
        return entries;
    }
}
