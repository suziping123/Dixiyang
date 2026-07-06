package com.dixiyang.server.Utils;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

/**
 * 统一存储服务
 * DB 只存路径引用（__file__:character/10.json），实际数据存文件系统
 * 与 Python 端 storage_service.py 保持一致
 */
@Slf4j
@Component
public class StorageService {

    private final ObjectMapper mapper = new ObjectMapper();

    @Value("${app.chat.storage-path:/home/lijiajia/项目/Dixiyang/uploads/storage/chat}")
    private String chatBaseDir;

    // storage/chat/../character/ → 即 storage/character/
    private String getStorageRoot() {
        return Paths.get(chatBaseDir).getParent().toString();
    }

    /**
     * 保存 JSON 到文件系统，返回 DB 引用值
     */
    public String saveJson(String subdir, Long recordId, Map<String, Object> data) {
        if (data == null || data.isEmpty()) return null;
        try {
            String root = getStorageRoot();
            Path dirPath = Paths.get(root, subdir);
            Files.createDirectories(dirPath);
            Path filePath = dirPath.resolve(recordId + ".json");
            String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(data);
            Files.writeString(filePath, json);
            log.info("JSON 存入文件: {}", filePath);
            return "__file__:" + subdir + "/" + recordId + ".json";
        } catch (IOException e) {
            log.error("存储 JSON 失败: subdir={}, id={}", subdir, recordId, e);
            throw new RuntimeException("存储失败: " + e.getMessage());
        }
    }

    /**
     * 保存 JSON 字符串到文件系统（用于 customBgs 等已经是字符串的字段）
     */
    public String saveJsonString(String subdir, Long recordId, String jsonStr) {
        if (jsonStr == null || jsonStr.isBlank()) return null;
        // 如果已经是文件引用，直接返回
        if (jsonStr.startsWith("__file__:")) return jsonStr;
        try {
            // 验证是合法 JSON
            Map<String, Object> data = mapper.readValue(jsonStr, new TypeReference<>() {});
            return saveJson(subdir, recordId, data);
        } catch (Exception e) {
            log.warn("解析 JSON 失败，存为原始字符串: {}", e.getMessage());
            // 非 JSON 字符串直接返回原值
            return jsonStr;
        }
    }

    /**
     * 加载 JSON：自动判断是文件引用还是 JSON 字符串
     * 返回解析后的 Object（Map 或 List），null 表示无数据
     */
    public Object loadJson(String subdir, Long recordId, String dbValue) {
        if (dbValue == null || dbValue.isBlank()) return null;

        try {
            if (dbValue.startsWith("__file__:")) {
                String relPath = dbValue.replace("__file__:", "");
                Path filePath = Paths.get(getStorageRoot(), relPath);
                if (!Files.exists(filePath)) {
                    log.warn("文件不存在: {}", filePath);
                    return null;
                }
                return mapper.readValue(filePath.toFile(), new TypeReference<>() {});
            }
            return mapper.readValue(dbValue, new TypeReference<>() {});
        } catch (Exception e) {
            log.error("加载 JSON 失败: subdir={}, id={}", subdir, recordId, e);
            return null;
        }
    }

    /**
     * 加载 JSON 并返回 JSON 字符串（用于前端需要字符串的场景）
     */
    public String loadJsonAsString(String subdir, Long recordId, String dbValue) {
        if (dbValue == null || dbValue.isBlank()) return null;
        try {
            if (dbValue.startsWith("__file__:")) {
                String relPath = dbValue.replace("__file__:", "");
                Path filePath = Paths.get(getStorageRoot(), relPath);
                if (!Files.exists(filePath)) return null;
                return Files.readString(filePath);
            }
            return dbValue;
        } catch (Exception e) {
            log.error("加载 JSON 字符串失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 删除 JSON 文件
     */
    public void deleteJson(String dbValue) {
        if (dbValue == null || !dbValue.startsWith("__file__:")) return;
        try {
            String relPath = dbValue.replace("__file__:", "");
            Path filePath = Paths.get(getStorageRoot(), relPath);
            Files.deleteIfExists(filePath);
            log.info("已删除文件: {}", filePath);
        } catch (IOException e) {
            log.warn("删除文件失败: {}", e.getMessage());
        }
    }

    /**
     * 判断 dbValue 是否为文件引用
     */
    public boolean isFileReference(String dbValue) {
        return dbValue != null && dbValue.startsWith("__file__:");
    }
}
