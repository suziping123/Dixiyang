package com.dixiyang.server.Utils;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 轻量 .env 读取器（与 DixyangFast config.py 的 load_dotenv 对齐）。
 * 仅在 Spring 环境变量缺失时兜底，绝不覆盖已有环境变量。
 */
public final class DotEnv {
    private static Map<String, String> cache;

    private DotEnv() {
    }

    /**
     * 按顺序取第一个非空 key，找不到返回 null
     */
    public static synchronized String get(String... keys) {
        if (cache == null) {
            cache = load();
        }
        for (String key : keys) {
            String v = cache.get(key);
            if (v != null && !v.isBlank()) {
                return v;
            }
        }
        return null;
    }

    private static Map<String, String> load() {
        Map<String, String> map = new HashMap<>();
        // 依次尝试：启动目录 / 上级（dixiyang-engine 内启动）/ 上上级（根目录启动）
        List<String> candidates = List.of(".env", "../.env", "../../.env");
        for (String candidate : candidates) {
            Path path = Paths.get(candidate);
            if (Files.exists(path)) {
                parse(path, map);
                break;
            }
        }
        return map;
    }

    private static void parse(Path path, Map<String, String> map) {
        try {
            for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {
                String trimmed = line.trim();
                if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                    continue;
                }
                int eq = trimmed.indexOf('=');
                if (eq <= 0) {
                    continue;
                }
                String key = trimmed.substring(0, eq).trim();
                String value = trimmed.substring(eq + 1).trim();
                if (value.length() >= 2
                        && ((value.startsWith("\"") && value.endsWith("\""))
                        || (value.startsWith("'") && value.endsWith("'")))) {
                    value = value.substring(1, value.length() - 1);
                }
                map.put(key, value);
            }
        } catch (IOException e) {
            // 读取失败按无 .env 处理
        }
    }
}
