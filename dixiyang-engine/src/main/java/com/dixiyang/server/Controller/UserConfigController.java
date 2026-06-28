package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.UserConfig;
import com.dixiyang.server.Mapper.UserConfigMapper;
import io.swagger.v3.oas.annotations.tags.Tag;
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
        UserConfig config = userConfigMapper.selectOne(
                new LambdaQueryWrapper<UserConfig>()
                        .eq(UserConfig::getUserId, userId));
        if (config == null) {
            config = new UserConfig();
            config.setUserId(userId);
            userConfigMapper.insert(config);
        }
        return Result.success(config);
    }

    /**
     * 更新背景配置（backgroundId + customBgs）
     */
    @PostMapping("/background")
    public Result<Void> updateBackgroundConfig(@RequestBody UserConfig dto) {
        if (dto.getUserId() == null) return Result.error("userId不能为空");

        UserConfig existing = userConfigMapper.selectOne(
                new LambdaQueryWrapper<UserConfig>()
                        .eq(UserConfig::getUserId, dto.getUserId()));

        if (existing == null) {
            existing = new UserConfig();
            existing.setUserId(dto.getUserId());
            existing.setBackgroundId(dto.getBackgroundId());
            existing.setCustomBgs(dto.getCustomBgs());
            userConfigMapper.insert(existing);
        } else {
            if (dto.getBackgroundId() != null) existing.setBackgroundId(dto.getBackgroundId());
            if (dto.getCustomBgs() != null) existing.setCustomBgs(dto.getCustomBgs());
            userConfigMapper.updateById(existing);
        }

        return Result.success(null);
    }
}
