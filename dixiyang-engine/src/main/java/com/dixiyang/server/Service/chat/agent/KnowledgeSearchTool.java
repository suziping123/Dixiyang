package com.dixiyang.server.Service.chat.agent;

import com.dixiyang.server.Service.RagService;
import dev.langchain4j.agent.tool.Tool;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * LangChain4j @Tool 知识检索工具
 * 自动注册到 AiServices，LLM 可自主决定何时调用
 */
@Component
@Slf4j
public class KnowledgeSearchTool {

    private final RagService ragService;

    public KnowledgeSearchTool(RagService ragService) {
        this.ragService = ragService;
    }

    @Tool(name = "knowledge_search", value = """
        搜索小说知识库（角色/世界观/大纲/参考资料）。
        当你需要查阅设定细节、角色信息、世界观设定、故事大纲时调用此工具。
        参数 query 用自然语言描述你需要什么资料，例如"主角的性格特点"、"世界观设定"等。
        """)
    public String search(String query) {
        return search(query, null, 5);
    }

    @Tool(name = "knowledge_search_detailed", value = """
        搜索小说知识库（带类型过滤）。
        type 可选值：character（角色）、worldbuilding（世界观）、outline（大纲）、reference（参考资料）。
        不填则全搜。topK 控制返回条数，默认5。
        """)
    public String search(String query, String type, int topK) {
        long start = System.currentTimeMillis();
        try {
            Map<String, Object> result = ragService.search(query, topK > 0 ? topK : 5);
            Object resultsObj = result.get("results");
            if (resultsObj instanceof List<?> results && !results.isEmpty()) {
                List<String> filtered = results.stream()
                    .filter(r -> r instanceof Map)
                    .map(r -> (Map<?, ?>) r)
                    .filter(m -> type == null || type.isBlank() || matchesType(m, type))
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

                log.info("知识检索: query={}, type={}, 结果数={}, 耗时={}ms", query, type, filtered.size(), System.currentTimeMillis() - start);
                return filtered.isEmpty() ? "未检索到相关资料" : String.join("\n---\n", filtered);
            }
            log.info("知识检索: query={}, 无结果, 耗时={}ms", query, System.currentTimeMillis() - start);
            return "未检索到相关资料";
        } catch (Exception e) {
            log.error("知识检索失败: query={}", query, e);
            return "检索失败: " + e.getMessage();
        }
    }

    private boolean matchesType(Map<?, ?> metadata, String type) {
        Object metaType = metadata.get("type");
        if (metaType != null) return type.equalsIgnoreCase(String.valueOf(metaType));
        Object source = metadata.get("source");
        return source != null && String.valueOf(source).toLowerCase().contains(type.toLowerCase());
    }
}
