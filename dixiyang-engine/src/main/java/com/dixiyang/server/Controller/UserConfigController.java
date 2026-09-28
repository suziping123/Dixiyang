package com.dixiyang.server.Controller;

import com.alibaba.fastjson.JSON;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.UserConfig;
import com.dixiyang.server.Entity.dto.FontColorsDTO;
import com.dixiyang.server.Mapper.UserConfigMapper;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/userConfig")
@Tag(name = "用户配置模块")
public class UserConfigController {

    @Autowired
    private UserConfigMapper userConfigMapper;

    /**
     * 获取当前用户的背景配置
     */
    @GetMapping("/background")
    public Result<UserConfig> getBackgroundConfig(@RequestParam Long userId) {
        return Result.success(getOrCreate(userId));
    }

    /**
     * 更新背景配置（backgroundId + customBgs）
     */
    @PostMapping("/background")
    public Result<Void> updateBackgroundConfig(@RequestBody UserConfig dto) {
        if (dto.getUserId() == null || dto.getUserId() <= 0) {
            return Result.error("无效的userId");
        }

        UserConfig existing = getOrCreate(dto.getUserId());

        if (dto.getBackgroundId() != null) existing.setBackgroundId(dto.getBackgroundId());
        if (dto.getCustomBgs() != null) existing.setCustomBgs(dto.getCustomBgs());
        userConfigMapper.updateById(existing);

        return Result.success(null);
    }

    /**
     * 获取字体颜色配置（无配置时返回空对象，前端自行套默认值）
     */
    @GetMapping("/fontColors")
    public Result<FontColorsDTO> getFontColors(@RequestParam Long userId) {
        UserConfig config = getOrCreate(userId);
        String json = config.getFontColorsJson();
        FontColorsDTO colors = (json == null || json.isBlank())
                ? new FontColorsDTO()
                : JSON.parseObject(json, FontColorsDTO.class);
        return Result.success(colors);
    }

    /**
     * 保存字体颜色配置（前端 body: { userId, colors: {...} }）
     */
    @PostMapping("/fontColors")
    public Result<Void> saveFontColors(@RequestBody FontColorsPayload dto) {
        if (dto.getUserId() == null || dto.getUserId() <= 0) {
            return Result.error("无效的userId");
        }
        if (dto.getColors() == null) {
            return Result.error("缺少colors");
        }

        UserConfig existing = getOrCreate(dto.getUserId());
        existing.setFontColorsJson(JSON.toJSONString(dto.getColors()));
        userConfigMapper.updateById(existing);

        return Result.success(null);
    }

    /** 查询用户配置，不存在则初始化插入 */
    private UserConfig getOrCreate(Long userId) {
        UserConfig config = userConfigMapper.selectOne(
                new LambdaQueryWrapper<UserConfig>().eq(UserConfig::getUserId, userId));
        if (config == null) {
            config = new UserConfig();
            config.setUserId(userId);
            userConfigMapper.insert(config);
        }
        return config;
    }

    /** 保存字体颜色的请求体 */
    @Data
    public static class FontColorsPayload {
        private Long userId;
        private FontColorsDTO colors;
    }
}
