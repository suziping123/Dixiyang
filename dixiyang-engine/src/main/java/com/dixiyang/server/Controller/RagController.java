package com.dixiyang.server.Controller;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Service.RagService;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Tag(name = "RAG 向量库")
@RestController
@RequestMapping("/rag")
@Slf4j
public class RagController {

    private final RagService ragService;

    @Autowired
    public RagController(RagService ragService) {
        this.ragService = ragService;
    }

    @GetMapping("/stats")
    public Result<Map<String, Object>> getStats() {
        Map<String, Object> stats = ragService.getStats();
        return Result.success(stats);
    }

    @GetMapping("/count")
    public Result<Long> getCount() {
        long count = ragService.getCollectionCount();
        return Result.success(count);
    }

    @GetMapping("/documents")
    public Result<Map<String, Object>> getDocuments(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int pageSize) {
        Map<String, Object> docs = ragService.getDocuments(page, pageSize);
        return Result.success(docs);
    }

    @PostMapping("/search")
    public Result<Map<String, Object>> search(
            @RequestParam String query,
            @RequestParam(defaultValue = "5") int topK) {
        Map<String, Object> results = ragService.search(query, topK);
        return Result.success(results);
    }
}
