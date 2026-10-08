package com.dixiyang.server.Service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Entity.AppUser;
import com.dixiyang.server.Entity.VO.UserVO;
import com.dixiyang.server.Entity.dto.AuthDTO;
import com.dixiyang.server.Mapper.AppUserMapper;
import com.dixiyang.server.Service.AuthService;
import com.dixiyang.server.Service.EmailCodeService;
import com.dixiyang.server.Utils.JwtUtils;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import com.dixiyang.server.Common.Result;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Slf4j
@Service
public class AuthServiceImpl implements AuthService {
    // 风控窗口（分钟）：窗口内成功登录达 RISK_LOGIN_LIMIT 次后，密码登录必须验证码
    private static final int RISK_WINDOW_MINUTES = 10;
    private static final int RISK_LOGIN_LIMIT = 3;

    @Autowired
    private AppUserMapper appUserMapper;//注入Mapper

//    写一个工具类来处理JWT和密码的加密
    @Autowired
    private JwtUtils jwtUtils;
    @Autowired
    private PasswordEncoder passwordEncoder;//这里用的是BCryptPasswordEncoder
    @Autowired
    private EmailCodeService emailCodeService;

    @Override
    public Result login(String username, String password) {
//        MyBatis-Plus动态搜索
//        创建一个LambdaQueryWrapper，指定查询条件
        LambdaQueryWrapper<AppUser> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(AppUser::getUsername, username);
//        执行查询：BaseMapper的selectOne
        AppUser appUser = appUserMapper.selectOne(queryWrapper);
//        如果用户不在
        if  (appUser == null) {
            log.warn("登录失败：用户不存在, username={}", username);
            return Result.error("用户名不存在");
        }
//        在java中对比密码(Significant!!!)
//        使用passwdEncoder的matches方法来对比前端传来的没问和数据库查出来的加密串
        if  (!passwordEncoder.matches(password, appUser.getPassword())) {
            return Result.error("用户名或密码错误");
        }

//        风控：短时间内频繁顶号登录，强制改用邮箱验证码登录
        if (Boolean.TRUE.equals(appUser.getRequireCode())) {
            log.warn("登录被风控拦截（需验证码）: username={}", username);
            return Result.error("登录过于频繁，请使用邮箱验证码登录");
        }

//        单点登录：生成新会话号覆盖旧值，旧设备下次请求即被踢出
        String sessionId = newSessionId();
        appUser.setSessionId(sessionId);
        recordLoginRisk(appUser);
        appUserMapper.updateById(appUser);

//        校验通过，生成token
        String token = jwtUtils.generateToken(appUser.getId().toString(), sessionId);
//       【解决泄露风险】手动挑选字段给前端 或者用 UserVO
        UserVO userVO = buildUserVO(appUser);

//        但会结果（Token和抹除密码后的用户对象）
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", userVO);

        return Result.success(data);
    }

    @Override
    public Result loginByCode(String email, String code) {
        if (email == null || email.isBlank()) {
            return Result.error("邮箱不能为空");
        }
//        先校验验证码（一次性：通过即消费）
        if (!emailCodeService.verifyCode(email, "LOGIN", code)) {
            return Result.error("验证码错误或已过期");
        }
        LambdaQueryWrapper<AppUser> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(AppUser::getEmail, email);
        AppUser appUser = appUserMapper.selectOne(queryWrapper);
        if (appUser == null) {
            return Result.error("该邮箱未注册");
        }

//        验证码登录通过风控 → 顶号 + 解除强制验证码 + 重置窗口
        String sessionId = newSessionId();
        appUser.setSessionId(sessionId);
        appUser.setRequireCode(false);
        appUser.setLoginCount(0);
        appUser.setLoginWindowStart(LocalDateTime.now(ZoneOffset.UTC));
        appUserMapper.updateById(appUser);

        String token = jwtUtils.generateToken(appUser.getId().toString(), sessionId);
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", buildUserVO(appUser));
        return Result.success(data);
    }

    @Override
    public Result<Void> sendCode(String email, String purpose) {
        return emailCodeService.sendCode(email, purpose);
    }

    /**
     * 记录一次成功登录：窗口内计数，达阈值则置强制验证码标记
     * 时间统一用 UTC，保证与 Python 端共表可比
     */
    private void recordLoginRisk(AppUser user) {
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
        LocalDateTime start = user.getLoginWindowStart();
        int prev = user.getLoginCount() == null ? 0 : user.getLoginCount();
        int count = (start == null || !start.isAfter(now.minusMinutes(RISK_WINDOW_MINUTES))) ? 1 : prev + 1;
        user.setLoginCount(count);
        user.setLoginWindowStart(now);
        if (count >= RISK_LOGIN_LIMIT) {
            user.setRequireCode(true);
        }
    }

    private String newSessionId() {
        return UUID.randomUUID().toString().replace("-", "");
    }

    private UserVO buildUserVO(AppUser appUser) {
        UserVO userVO = new UserVO();
        userVO.setId(appUser.getId());
        userVO.setUsername(appUser.getUsername());
        userVO.setNickname(appUser.getNickname()); // 数据库查出来的昵称
        userVO.setEmail(appUser.getEmail());
        return userVO;
    }

    @Override
    public Result register(AuthDTO reg) {
//        检查用户是否存在
        LambdaQueryWrapper<AppUser> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(AppUser::getUsername, reg.getUsername());
        if (appUserMapper.selectOne(queryWrapper) != null) {
            return Result.error("该用户名已存在，请换一个名称");
        }

//        构造实体并加密密码
        AppUser newUser = new AppUser();
        newUser.setUsername(reg.getUsername());
        newUser.setNickname(reg.getNickname());
        newUser.setEmail(reg.getEmail());
//        记得加密
        String password = passwordEncoder.encode(reg.getPassword());
        newUser.setPassword(password);
        appUserMapper.insert(newUser);
        return Result.success("注册成功！！！");
    }
}
