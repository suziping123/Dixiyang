package com.dixiyang.server.Service.chat.pipeline.impl;

import com.dixiyang.server.Service.RagService;
import com.dixiyang.server.Service.chat.pipeline.Tool;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component
public class KnowledgeSearchTool implements Tool {

    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(KnowledgeSearchTool.class);
    private final RagService ragService;

    public KnowledgeSearchTool(RagService ragService) {
        this.ragService = ragService;
    }

    @Override
    public String name() {
        return "knowledge_search";
    }

    @Override
    public String description() {
        return "搜索小说知识库（角色/世界观/大纲/参考资料）。当你需要查阅设定细节时调用。";
    }

    @Override
    public ToolSchema schema() {
        Map<String, Object> params = new HashMap<>();
        params.put("type", "object");
        Map<String, Object> props = new HashMap<>();
        props.put("query", Map.of("type", "string", "description", "搜索查询，用自然语言描述你需要什么资料"));
        props.put("type", Map.of("type", "string", "description", "知识类型：character/worldbuilding/outline/reference，不填则全搜"));
        props.put("topK", Map.of("type", "integer", "description", "返回条数，默认5"));
        params.put("properties", props);
        params.put("required", List.of("query"));
        return new ToolSchema(params, "{\"query\":\"主角性格特点\",\"type\":\"character\",\"topK\":3}");
    }

    @Override
    public ToolResult execute(ToolInput input) {
        long start = System.currentTimeMillis();
        try {
            Map<String, Object> result = ragService.search(input.query(), input.topK() > 0 ? input.topK() : 5);
            Object resultsObj = result.get("results");
            if (resultsObj instanceof List<?> results && !results.isEmpty()) {
                List<String> filtered = results.stream()
                    .filter(r -> r instanceof Map)
                    .map(r -> (Map<?, ?>) r)
                    .filter(m -> input.type() == null || input.type().isBlank() || matchesType(m, input.type()))
                    .map(m -> {
                        String content = String.valueOf(m.get("content"));
                        Object meta = m.get("metadata");
                        String source = "";
                        if (meta instanceof Map<?, ?> mm) {
                            Object bookTitle = mm.get("book_title");
                            Object src = mm.get("source");
                            source = bookTitle != null ? String.valueOf(bookTitle) : (src != null ? String.valueOf(src) : "");
                        }
                        return (source.isEmpty() ? "" : "[" + source + "] ") + content;
                    })
                    .collect(Collectors.toList());

                String content = filtered.isEmpty() ? "未检索到相关资料" : String.join("\n---\n", filtered);
                Map<String, Object> meta = new HashMap<>();
                meta.put("count", filtered.size());
                meta.put("latencyMs", System.currentTimeMillis() - start);
                return new Tool.ToolResult(content, meta);
            }
            return new Tool.ToolResult("未检索到相关资料", Map.of("count", 0, "latencyMs", System.currentTimeMillis() - start));
        } catch (Exception e) {
            log.error("Knowledge search failed", e);
            return new Tool.ToolResult("检索失败: " + e.getMessage(), Map.of("error", true, "latencyMs", System.currentTimeMillis() - start));
        }
    }

    private boolean matchesType(Map<?, ?> metadata, String type) {
        Object metaType = metadata.get("type");
        if (metaType != null) return type.equalsIgnoreCase(String.valueOf(metaType));
        Object source = metadata.get("source");
        return source != null && String.valueOf(source).toLowerCase().contains(type.toLowerCase());
    }
}