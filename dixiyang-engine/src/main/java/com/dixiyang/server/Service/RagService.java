package com.dixiyang.server.Service;

import com.dixiyang.server.Config.ChromaConfig;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
@Slf4j
public class RagService {

    private static final String DEFAULT_TENANT = "default_tenant";
    private static final String DEFAULT_DATABASE = "default_database";

    private final ChromaConfig chromaConfig;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private String collectionId;

    public RagService(ChromaConfig chromaConfig) {
        this.chromaConfig = chromaConfig;
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
        this.collectionId = null;
    }

    private String getApiBase() {
        return "http://" + chromaConfig.getHost() + ":" + chromaConfig.getPort() + "/api/v2";
    }

    private String getCollectionsBase() {
        return getApiBase() + "/tenants/" + DEFAULT_TENANT + "/databases/" + DEFAULT_DATABASE + "/collections";
    }

    private String getCollectionId() {
        if (collectionId != null) return collectionId;
        try {
            String listUrl = getCollectionsBase();
            JsonNode resp = restTemplate.getForObject(listUrl, JsonNode.class);
            if (resp != null && resp.isArray()) {
                String targetName = chromaConfig.getCollectionName();
                for (JsonNode col : resp) {
                    if (col.has("name") && targetName.equals(col.get("name").asText())) {
                        collectionId = col.get("id").asText();
                        return collectionId;
                    }
                }
                if (resp.size() > 0) {
                    collectionId = resp.get(0).get("id").asText();
                }
            }
        } catch (Exception e) {
            log.warn("ChromaDB 连接失败: {}", e.getMessage());
        }
        return collectionId;
    }

    private float[] getEmbedding(String text) {
        try {
            String embedUrl = "http://localhost:8085/api/rag/embed";
            ObjectNode req = objectMapper.createObjectNode();
            req.put("text", text);
            JsonNode resp = restTemplate.postForObject(embedUrl, req, JsonNode.class);
            if (resp != null && resp.has("embedding")) {
                JsonNode arr = resp.get("embedding");
                float[] emb = new float[arr.size()];
                for (int i = 0; i < arr.size(); i++) {
                    emb[i] = (float) arr.get(i).asDouble();
                }
                return emb;
            }
        } catch (Exception e) {
            log.warn("调用 Python embedding 服务失败: {}", e.getMessage());
        }
        return null;
    }

    public Map<String, Object> getStats() {
        Map<String, Object> stats = new LinkedHashMap<>();
        try {
            String listUrl = getCollectionsBase();
            JsonNode collections = restTemplate.getForObject(listUrl, JsonNode.class);
            int totalCollections = 0;
            List<Map<String, Object>> details = new ArrayList<>();
            if (collections != null && collections.isArray()) {
                totalCollections = collections.size();
                for (JsonNode col : collections) {
                    Map<String, Object> info = new LinkedHashMap<>();
                    info.put("name", col.get("name").asText());
                    info.put("id", col.get("id").asText());
                    String cid = col.get("id").asText();
                    try {
                        String countUrl = listUrl + "/" + cid + "/count";
                        long count = restTemplate.getForObject(countUrl, Long.class);
                        info.put("count", count);
                    } catch (Exception e) {
                        info.put("count", 0);
                    }
                    details.add(info);
                }
            }
            stats.put("total_collections", totalCollections);
            stats.put("embedding_model", "BAAI/bge-m3");
            stats.put("embedding_dimension", 1024);
            stats.put("collection_details", details);
            stats.put("connected", true);
        } catch (Exception e) {
            log.warn("ChromaDB 连接失败: {}", e.getMessage());
            stats.put("connected", false);
            stats.put("error", e.getMessage());
        }
        return stats;
    }

    public long getCollectionCount() {
        String colId = getCollectionId();
        if (colId == null) return 0;
        try {
            String url = getCollectionsBase() + "/" + colId + "/count";
            Long count = restTemplate.getForObject(url, Long.class);
            return count != null ? count : 0;
        } catch (Exception e) {
            log.warn("获取集合数量失败: {}", e.getMessage());
            return 0;
        }
    }

    public Map<String, Object> getDocuments(int page, int pageSize) {
        Map<String, Object> result = new LinkedHashMap<>();
        String colId = getCollectionId();
        if (colId == null) {
            result.put("error", "ChromaDB 未连接");
            return result;
        }
        try {
            ObjectNode body = objectMapper.createObjectNode();
            body.put("limit", pageSize);
            body.put("offset", (page - 1) * pageSize);
            ArrayNode include = body.putArray("include");
            include.add("documents").add("metadatas");

            String url = getCollectionsBase() + "/" + colId + "/get";
            JsonNode resp = restTemplate.postForObject(url, body, JsonNode.class);

            if (resp != null) {
                result.put("ids", resp.get("ids"));
                JsonNode docs = resp.get("documents");
                result.put("documents", docs != null ? docs : objectMapper.createArrayNode());
                JsonNode metas = resp.get("metadatas");
                result.put("metadatas", metas != null ? metas : objectMapper.createArrayNode());
            }
            result.put("page", page);
            result.put("page_size", pageSize);
        } catch (Exception e) {
            log.warn("查询文档列表失败: {}", e.getMessage());
            result.put("error", e.getMessage());
        }
        return result;
    }

    public Map<String, Object> search(String query, int topK) {
        Map<String, Object> result = new LinkedHashMap<>();
        String colId = getCollectionId();
        if (colId == null) {
            result.put("error", "ChromaDB 未连接");
            return result;
        }

        float[] emb = getEmbedding(query);
        if (emb == null) {
            result.put("error", "无法获取 embedding，请确保 Python 后端已启动（端口 8085）");
            return result;
        }

        try {
            // 宽召回：多取 4 倍候选，供 reranker 精排
            int recallK = Math.min(topK * 4, 100);

            ObjectNode body = objectMapper.createObjectNode();
            ArrayNode queryEmbs = body.putArray("query_embeddings");
            ArrayNode embArr = queryEmbs.addArray();
            for (float v : emb) {
                embArr.add(v);
            }
            body.put("n_results", recallK);
            ArrayNode include = body.putArray("include");
            include.add("documents").add("metadatas").add("distances");

            String url = getCollectionsBase() + "/" + colId + "/query";
            JsonNode resp = restTemplate.postForObject(url, body, JsonNode.class);

            if (resp != null && resp.has("documents") && resp.get("documents").isArray()
                    && resp.get("documents").size() > 0) {
                JsonNode docs = resp.get("documents").get(0);
                JsonNode metas = resp.get("metadatas").get(0);
                JsonNode dists = resp.get("distances").get(0);
                JsonNode ids = resp.get("ids").get(0);

                // 构建候选列表
                List<String> docTexts = new ArrayList<>();
                List<Map<String, Object>> items = new ArrayList<>();
                for (int i = 0; i < docs.size(); i++) {
                    docTexts.add(docs.get(i).asText());
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("id", ids.get(i).asText());
                    item.put("content", docs.get(i).asText());
                    if (metas != null && i < metas.size() && !metas.get(i).isNull()) {
                        item.put("metadata", metas.get(i));
                    }
                    if (dists != null && i < dists.size()) {
                        item.put("score", 1.0 - dists.get(i).asDouble());
                    }
                    items.add(item);
                }

                // 调用 reranker 精排
                List<Integer> ranked = rerankResults(query, docTexts);

                // 按 rerank 顺序重排并取 topK
                List<Map<String, Object>> rerankedItems = new ArrayList<>();
                for (int idx : ranked) {
                    if (idx < items.size()) {
                        rerankedItems.add(items.get(idx));
                    }
                    if (rerankedItems.size() >= topK) break;
                }

                result.put("results", rerankedItems);
            }
            result.put("query", query);
        } catch (Exception e) {
            log.warn("向量检索失败: {}", e.getMessage());
            result.put("error", e.getMessage());
        }
        return result;
    }

    /**
     * 调用 Python reranker 服务精排
     */
    private List<Integer> rerankResults(String query, List<String> documents) {
        List<Integer> defaultOrder = new ArrayList<>();
        for (int i = 0; i < documents.size(); i++) defaultOrder.add(i);
        if (documents.size() <= 1) return defaultOrder;

        try {
            String rerankUrl = "http://localhost:8085/api/rag/rerank";
            ObjectNode req = objectMapper.createObjectNode();
            req.put("query", query);
            req.put("top_k", documents.size());
            ArrayNode docsArr = req.putArray("documents");
            for (String doc : documents) {
                docsArr.add(doc);
            }

            JsonNode resp = restTemplate.postForObject(rerankUrl, req, JsonNode.class);
            if (resp != null && resp.has("results")) {
                JsonNode results = resp.get("results");
                // 构建文档到索引的映射
                Map<String, Integer> docToIdx = new HashMap<>();
                for (int i = 0; i < documents.size(); i++) {
                    docToIdx.put(documents.get(i), i);
                }
                List<Integer> ranked = new ArrayList<>();
                for (JsonNode r : results) {
                    String content = r.get("content").asText();
                    if (docToIdx.containsKey(content)) {
                        ranked.add(docToIdx.get(content));
                    }
                }
                return ranked;
            }
        } catch (Exception e) {
            log.warn("Reranker 调用失败，回退到原始顺序: {}", e.getMessage());
        }
        return defaultOrder;
    }
}
