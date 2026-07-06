package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.UserConfig;
import com.dixiyang.server.Mapper.UserConfigMapper;
import com.dixiyang.server.Utils.StorageService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/userConfig")
@Tag(name = "用户配置模块")
public class UserConfigController {

    private static final String SUBDIR = "user";

    @Autowired
    private UserConfigMapper userConfigMapper;

    @Autowired
    private StorageService storageService;

    /**
     * 获取当前用户的背景配置
     */
    @GetMapping("/background")
    public Result<Map<String, Object>> getBackgroundConfig(@RequestParam Long userId) {
        UserConfig config = getConfigOrCreate(userId);
        Map<String, Object> data = new java.util.HashMap<>();
        data.put("userId", config.getUserId());
        data.put("backgroundId", config.getBackgroundId());
        // 解引用 __file__: 路径，返回实际 JSON 内容
        data.put("customBgs", storageService.loadJsonAsString(SUBDIR + "/customBgs", userId, config.getCustomBgs()));
        data.put("fontColorsJson", storageService.loadJson(SUBDIR + "/fontColors", userId, config.getFontColorsJson()));
        return Result.success(data);
    }

    /**
     * 更新背景配置（backgroundId + customBgs）
     */
    @PostMapping("/background")
    public Result<Void> updateBackgroundConfig(@RequestBody UserConfig dto) {
        if (dto.getUserId() == null || dto.getUserId() <= 0) {
            return Result.error("无效的userId");
        }
        UserConfig existing = getConfigOrCreate(dto.getUserId());
        if (dto.getBackgroundId() != null) existing.setBackgroundId(dto.getBackgroundId());
        if (dto.getCustomBgs() != null) {
            // customBgs 可能是 JSON 字符串，存文件
            String ref = storageService.saveJsonString(SUBDIR + "/customBgs", dto.getUserId(), dto.getCustomBgs());
            existing.setCustomBgs(ref);
        }
        userConfigMapper.updateById(existing);
        return Result.success(null);
    }

    /**
     * 获取字体颜色配置
     * GET /api/userConfig/fontColors?userId=1
     */
    @GetMapping("/fontColors")
    public Result<Object> getFontColors(@RequestParam Long userId) {
        UserConfig config = getConfigOrCreate(userId);
        Object data = storageService.loadJson(SUBDIR + "/fontColors", userId, config.getFontColorsJson());
        return Result.success(data);
    }

    /**
     * 更新字体颜色配置
     * POST /api/userConfig/fontColors
     */
    @PostMapping("/fontColors")
    public Result<Void> updateFontColors(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(body.get("userId").toString());
        Object colors = body.get("colors");
        if (userId == null || colors == null) {
            return Result.error("参数不完整");
        }
        UserConfig config = getConfigOrCreate(userId);
        String ref = storageService.saveJson(SUBDIR + "/fontColors", userId, (Map<String, Object>) colors);
        config.setFontColorsJson(ref);
        userConfigMapper.updateById(config);
        return Result.success(null);
    }

    private UserConfig getConfigOrCreate(Long userId) {
        UserConfig config = userConfigMapper.selectOne(
                new LambdaQueryWrapper<UserConfig>()
                        .eq(UserConfig::getUserId, userId));
        if (config == null) {
            config = new UserConfig();
            config.setUserId(userId);
            userConfigMapper.insert(config);
        }
        return config;
    }
}
