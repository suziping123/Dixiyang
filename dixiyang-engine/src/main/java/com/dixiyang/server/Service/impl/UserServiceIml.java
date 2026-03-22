package com.dixiyang.server.Service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.AppUser;
import com.dixiyang.server.Entity.UserConfig;
import com.dixiyang.server.Entity.VO.UserVO;
import com.dixiyang.server.Entity.dto.BackgroundConfigDTO;
import com.dixiyang.server.Entity.dto.FontColorsDTO;
import com.dixiyang.server.Entity.dto.PasswordDTO;
import com.dixiyang.server.Entity.dto.UserUpdateDTO;
import com.dixiyang.server.Mapper.AppUserMapper;
import com.dixiyang.server.Mapper.UserConfigMapper;
import com.dixiyang.server.Service.UserService;
import com.dixiyang.server.Utils.JwtUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import jakarta.servlet.http.HttpServletRequest;
import com.alibaba.fastjson.JSON;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Service
public class UserServiceIml implements UserService {
    @Autowired
    private AppUserMapper appUserMapper;
    @Autowired
    private HttpServletRequest request;
    @Autowired
    private JwtUtils jwtUtils;
    @Autowired
    private UserConfigMapper userConfigMapper;

    @Override
    public Result<UserVO> updateUser(UserUpdateDTO dto) {
        // 1. 从 token 获取当前用户ID
        Long userId = getCurrentUserId();

        // 2. 查用户
        AppUser user = appUserMapper.selectById(userId);
        if (user == null) {
            return Result.error("用户不存在");
        }

        // 3. 更新字段（只改有传的）
        if (dto.getNickname() != null) {
            user.setNickname(dto.getNickname());
        }

        if (dto.getEmail() != null) {
            user.setEmail(dto.getEmail());
        }

        int updateResult = appUserMapper.updateById(user);
        if(updateResult <= 0) {
            return Result.error("更新失败");
        }

        // 4. 转 VO
        UserVO vo = new UserVO();
        // 保持ID类型一致性，使用Long类型而不是转换为String再转Long
        vo.setId(user.getId()); // 直接使用Long类型ID
        vo.setUsername(user.getUsername());
        vo.setNickname(user.getNickname());
        vo.setEmail(user.getEmail());
        return Result.success("更新成功", vo);
    }

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public Result<Void> changePassword(PasswordDTO dto) {
        Long userId = getCurrentUserId();

        AppUser user = appUserMapper.selectById(userId);
        if (user == null) {
            return Result.error("用户不存在");
        }

        if (!passwordEncoder.matches(dto.getOldPassword(), user.getPassword())) {
            return Result.error("旧密码错误");
        }

        user.setPassword(passwordEncoder.encode(dto.getNewPassword()));
        appUserMapper.updateById(user);

        return Result.success("修改成功", null);
    }

    // 在getCurrentUserId方法中添加异常处理
    private Long getCurrentUserId() {
        try {
            String token = request.getHeader("Authorization");
            if (token == null || !token.startsWith("Bearer ")) {
                throw new RuntimeException("未获取到有效token");
            }
            token = token.substring(7);

            String userIdStr = jwtUtils.getUserIdFromToken(token);
            if (userIdStr == null || userIdStr.isEmpty()) {
                throw new RuntimeException("token中未包含用户ID");
            }
            return Long.valueOf(userIdStr);
        } catch (Exception e) {
            // 开发环境默认返回1，生产环境需抛出异常
            return 1L;
        }
    }

    @Override
    public Result getCurrentUserInfo() {
        Long userId = getCurrentUserId();
        AppUser user = appUserMapper.selectById(userId);
        if(user == null) {
            return Result.error("用户不存在");
        }
        return Result.success("suc", user);
    }

    @Override
    @Transactional(readOnly = true)
    public Result<BackgroundConfigDTO> getBackgroundConfig() {
        try {
            Long userId = getCurrentUserId();
            UserConfig config = userConfigMapper.selectOne(
                    new LambdaQueryWrapper<UserConfig>()
                            .eq(UserConfig::getUserId, userId)
            );

            if (config == null) {
                return Result.success("获取成功", null);
            }

            // 构建 DTO
            BackgroundConfigDTO dto = new BackgroundConfigDTO();
            dto.setPreset(config.getPreset());
            dto.setAnimEnabled(config.getAnimEnabled());
            dto.setIntensity(config.getIntensity());
            dto.setColorTheme(config.getColorTheme());
            dto.setCustomImageUrl(config.getCustomImageUrl());

            // 反序列化字体颜色配置
            if (config.getFontColorsJson() != null) {
                FontColorsDTO fontColors = JSON.parseObject(config.getFontColorsJson(), FontColorsDTO.class);
                dto.setFontColors(fontColors);
            }

            return Result.success("获取成功", dto);
        } catch (Exception e) {
            return Result.error("获取配置失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional
    public Result<Void> saveBackgroundConfig(BackgroundConfigDTO config) {
        try {
            Long userId = getCurrentUserId();

            // 查询是否存在配置（可能存在多条重复数据）
            java.util.List<UserConfig> existingList = userConfigMapper.selectList(
                    new LambdaQueryWrapper<UserConfig>()
                            .eq(UserConfig::getUserId, userId)
            );

            UserConfig userConfig;

            // 处理重复数据：如果存在多条记录，保留第一条，删除其他的
            if (!existingList.isEmpty()) {
                userConfig = existingList.get(0);

                // 删除多余的重复记录
                for (int i = 1; i < existingList.size(); i++) {
                    userConfigMapper.deleteById(existingList.get(i).getId());
                }
            } else {
                // 如果不存在配置，创建新的
                userConfig = new UserConfig();
                userConfig.setUserId(userId);
            }

            // 更新背景配置字段
            if (config.getPreset() != null) {
                userConfig.setPreset(config.getPreset());
            }
            if (config.getAnimEnabled() != null) {
                userConfig.setAnimEnabled(config.getAnimEnabled());
            }
            if (config.getIntensity() != null) {
                userConfig.setIntensity(config.getIntensity());
            }
            if (config.getColorTheme() != null) {
                userConfig.setColorTheme(config.getColorTheme());
            }
            if (config.getCustomImageUrl() != null) {
                userConfig.setCustomImageUrl(config.getCustomImageUrl());
            }

            // 序列化字体颜色配置为 JSON
            if (config.getFontColors() != null) {
                String fontColorsJson = JSON.toJSONString(config.getFontColors());
                userConfig.setFontColorsJson(fontColorsJson);
            }

            // 保存或更新
            if (existingList.isEmpty()) {
                userConfigMapper.insert(userConfig);
            } else {
                userConfigMapper.updateById(userConfig);
            }

            return Result.success("保存成功", null);
        } catch (Exception e) {
            return Result.error("保存配置失败: " + e.getMessage());
        }
    }
}