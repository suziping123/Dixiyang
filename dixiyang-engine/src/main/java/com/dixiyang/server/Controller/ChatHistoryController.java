package com.dixiyang.server.Controller;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.ChatSession;
import com.dixiyang.server.Service.IChatSessionService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/chatHistory")
@Tag(name = "聊天历史模块")
public class ChatHistoryController {

    @Autowired
    private IChatSessionService chatSessionService;

    @GetMapping("/sessions")
    public Result<List<ChatSession>> getSessions(
            @RequestParam Long novelId,
            Authentication auth) {
        Long userId = getUserId(auth);
        if (userId == null) return Result.error("未登录");
        List<ChatSession> sessions = chatSessionService.getSessionsByUser(userId, novelId);
        return Result.success("获取成功", sessions);
    }

    @GetMapping("/session/{sessionId}")
    public Result<List<Map<String, Object>>> getSession(
            @PathVariable String sessionId,
            Authentication auth) {
        Long userId = getUserId(auth);
        if (userId == null) return Result.error("未登录");
        List<Map<String, Object>> messages = chatSessionService.getSessionMessagesWithEdits(sessionId, userId);
        return Result.success("获取成功", messages);
    }

    @PostMapping("/batchSave")
    public Result<String> batchSave(@RequestBody Map<String, Object> body, Authentication auth) {
        Long userId = getUserId(auth);
        if (userId == null) return Result.error("未登录");
        String sessionId = (String) body.get("sessionId");
        Number novelIdNum = body.get("novelId") instanceof Number ? (Number) body.get("novelId") : null;
        Long novelId = novelIdNum != null ? novelIdNum.longValue() : null;
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> messages = (List<Map<String, Object>>) body.get("messages");
        if (sessionId == null || messages == null) {
            return Result.error("参数不完整");
        }
        chatSessionService.appendMessages(userId, novelId, sessionId, messages);
        return Result.success("保存成功");
    }

    @PutMapping("/message/{sessionId}")
    public Result<String> editMessage(
            @PathVariable String sessionId,
            @RequestBody Map<String, Object> body,
            Authentication auth) {
        Long userId = getUserId(auth);
        if (userId == null) return Result.error("未登录");
        int messageIndex = body.get("messageIndex") instanceof Number ? ((Number) body.get("messageIndex")).intValue() : -1;
        String role = (String) body.get("role");
        String newContent = (String) body.get("content");
        if (messageIndex < 0 || newContent == null) return Result.error("参数不完整");
        boolean ok = chatSessionService.editMessage(userId, sessionId, messageIndex, role, newContent);
        return ok ? Result.success("编辑成功") : Result.error("编辑失败");
    }

    @PostMapping("/generate-title/{sessionId}")
    public Result<String> generateTitle(
            @PathVariable String sessionId,
            Authentication auth) {
        Long userId = getUserId(auth);
        if (userId == null) return Result.error("未登录");
        String title = chatSessionService.generateAndUpdateTitle(sessionId, userId);
        if (title == null) return Result.error("标题生成失败");
        return Result.success("标题生成成功", title);
    }

    @DeleteMapping("/session/{sessionId}")
    public Result<String> deleteSession(
            @PathVariable String sessionId,
            Authentication auth) {
        Long userId = getUserId(auth);
        if (userId == null) return Result.error("未登录");
        chatSessionService.deleteSession(sessionId, userId);
        return Result.success("删除成功");
    }

    private Long getUserId(Authentication auth) {
        if (auth == null || auth.getPrincipal() == null) return null;
        try {
            return Long.parseLong(auth.getPrincipal().toString());
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
