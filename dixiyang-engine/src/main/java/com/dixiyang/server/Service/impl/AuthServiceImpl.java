package com.dixiyang.server.Service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Entity.AppUser;
import com.dixiyang.server.Entity.EmailVerificationCode;
import com.dixiyang.server.Entity.VO.UserVO;
import com.dixiyang.server.Entity.dto.AuthDTO;
import com.dixiyang.server.Entity.dto.VerifyCodeDTO;
import com.dixiyang.server.Mapper.AppUserMapper;
import com.dixiyang.server.Mapper.EmailVerificationCodeMapper;
import com.dixiyang.server.Service.AuthService;
import com.dixiyang.server.Service.EmailService;
import com.dixiyang.server.Utils.JwtUtils;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import com.dixiyang.server.Common.Result;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class AuthServiceImpl implements AuthService {
    @Autowired
    private AppUserMapper appUserMapper;
    @Autowired
    private EmailVerificationCodeMapper codeMapper;
    @Autowired
    private EmailService emailService;
    @Autowired
    private JwtUtils jwtUtils;
    @Autowired
    private PasswordEncoder passwordEncoder;

    private static final SecureRandom RANDOM = new SecureRandom();
    private static final long CODE_EXPIRE_MINUTES = 5;
    private static final long RATE_LIMIT_SECONDS = 60;

    @Override
    public Result<?> login(String username, String password) {
        LambdaQueryWrapper<AppUser> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(AppUser::getUsername, username);
        AppUser appUser = appUserMapper.selectOne(queryWrapper);
        if (appUser == null) {
            log.warn("登录失败：用户不存在, username={}", username);
            return Result.error("用户名不存在");
        }
        if (!passwordEncoder.matches(password, appUser.getPassword())) {
            return Result.error("用户名或密码错误");
        }
        String token = jwtUtils.generateToken(appUser.getId().toString());
        UserVO userVO = new UserVO();
        userVO.setId(appUser.getId());
        userVO.setUsername(appUser.getUsername());
        userVO.setNickname(appUser.getNickname());
        userVO.setEmail(appUser.getEmail());

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", userVO);
        return Result.success(data);
    }

    @Override
    public Result<?> register(AuthDTO reg) {
        LambdaQueryWrapper<AppUser> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(AppUser::getUsername, reg.getUsername());
        if (appUserMapper.selectOne(queryWrapper) != null) {
            return Result.error("该用户名已存在，请换一个名称");
        }
        AppUser newUser = new AppUser();
        newUser.setUsername(reg.getUsername());
        newUser.setNickname(reg.getNickname());
        newUser.setEmail(reg.getEmail());
        String password = passwordEncoder.encode(reg.getPassword());
        newUser.setPassword(password);
        appUserMapper.insert(newUser);
        return Result.success("注册成功！！！");
    }

    @Override
    public Result<?> sendCode(String email, String purpose) {
        if (email == null || email.isBlank()) {
            return Result.error("邮箱不能为空");
        }
        if (!"LOGIN".equals(purpose) && !"REGISTER".equals(purpose)) {
            return Result.error("用途参数无效");
        }

        // 60秒限流：检查上次发送时间
        LambdaQueryWrapper<EmailVerificationCode> rateQuery = new LambdaQueryWrapper<>();
        rateQuery.eq(EmailVerificationCode::getEmail, email)
                .eq(EmailVerificationCode::getPurpose, purpose)
                .orderByDesc(EmailVerificationCode::getCreatedAt)
                .last("LIMIT 1");
        EmailVerificationCode lastRecord = codeMapper.selectOne(rateQuery);
        if (lastRecord != null && lastRecord.getCreatedAt() != null) {
            long secondsSinceLast = java.time.Duration.between(lastRecord.getCreatedAt(), LocalDateTime.now()).getSeconds();
            if (secondsSinceLast < RATE_LIMIT_SECONDS) {
                return Result.error("请" + (RATE_LIMIT_SECONDS - secondsSinceLast) + "秒后重试");
            }
        }

        // 生成6位验证码
        String code = String.format("%06d", RANDOM.nextInt(1000000));
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime expireTime = now.plusMinutes(CODE_EXPIRE_MINUTES);

        // UPSERT：存在则更新，不存在则插入
        LambdaQueryWrapper<EmailVerificationCode> existQuery = new LambdaQueryWrapper<>();
        existQuery.eq(EmailVerificationCode::getEmail, email)
                .eq(EmailVerificationCode::getPurpose, purpose);
        EmailVerificationCode existing = codeMapper.selectOne(existQuery);

        if (existing != null) {
            existing.setCode(code);
            existing.setExpireTime(expireTime);
            existing.setUsed(false);
            existing.setCreatedAt(now);
            codeMapper.updateById(existing);
        } else {
            EmailVerificationCode record = new EmailVerificationCode();
            record.setEmail(email);
            record.setCode(code);
            record.setPurpose(purpose);
            record.setExpireTime(expireTime);
            record.setUsed(false);
            record.setCreatedAt(now);
            codeMapper.insert(record);
        }

        // 异步发送邮件
        emailService.sendVerificationCode(email, code);
        log.info("验证码已生成: email={}, purpose={}", email, purpose);
        return Result.success("验证码已发送");
    }

    @Override
    public Result<?> loginByCode(VerifyCodeDTO dto) {
        if (dto.getEmail() == null || dto.getEmail().isBlank()) {
            return Result.error("邮箱不能为空");
        }
        if (dto.getCode() == null || dto.getCode().isBlank()) {
            return Result.error("验证码不能为空");
        }

        // 查询有效验证码
        LambdaQueryWrapper<EmailVerificationCode> query = new LambdaQueryWrapper<>();
        query.eq(EmailVerificationCode::getEmail, dto.getEmail())
                .eq(EmailVerificationCode::getPurpose, "LOGIN")
                .eq(EmailVerificationCode::getUsed, false)
                .orderByDesc(EmailVerificationCode::getCreatedAt)
                .last("LIMIT 1");
        EmailVerificationCode record = codeMapper.selectOne(query);

        if (record == null) {
            return Result.error("请先获取验证码");
        }
        if (record.getExpireTime().isBefore(LocalDateTime.now())) {
            return Result.error("验证码已过期，请重新获取");
        }
        if (!record.getCode().equals(dto.getCode())) {
            return Result.error("验证码错误");
        }

        // 标记已使用
        record.setUsed(true);
        codeMapper.updateById(record);

        // 查找用户
        LambdaQueryWrapper<AppUser> userQuery = new LambdaQueryWrapper<>();
        userQuery.eq(AppUser::getEmail, dto.getEmail());
        AppUser user = appUserMapper.selectOne(userQuery);
        if (user == null) {
            return Result.error("该邮箱未注册");
        }

        String token = jwtUtils.generateToken(user.getId().toString());
        UserVO userVO = new UserVO();
        userVO.setId(user.getId());
        userVO.setUsername(user.getUsername());
        userVO.setNickname(user.getNickname());
        userVO.setEmail(user.getEmail());

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", userVO);
        return Result.success(data);
    }

    @Override
    public Result<?> registerByCode(AuthDTO reg, String code) {
        if (reg.getEmail() == null || reg.getEmail().isBlank()) {
            return Result.error("邮箱不能为空");
        }
        if (code == null || code.isBlank()) {
            return Result.error("验证码不能为空");
        }
        if (reg.getUsername() == null || reg.getUsername().isBlank()) {
            return Result.error("用户名不能为空");
        }
        if (reg.getPassword() == null || reg.getPassword().length() < 6) {
            return Result.error("密码长度至少为6位");
        }

        // 校验验证码
        LambdaQueryWrapper<EmailVerificationCode> query = new LambdaQueryWrapper<>();
        query.eq(EmailVerificationCode::getEmail, reg.getEmail())
                .eq(EmailVerificationCode::getPurpose, "REGISTER")
                .eq(EmailVerificationCode::getUsed, false)
                .orderByDesc(EmailVerificationCode::getCreatedAt)
                .last("LIMIT 1");
        EmailVerificationCode record = codeMapper.selectOne(query);

        if (record == null) {
            return Result.error("请先获取验证码");
        }
        if (record.getExpireTime().isBefore(LocalDateTime.now())) {
            return Result.error("验证码已过期，请重新获取");
        }
        if (!record.getCode().equals(code)) {
            return Result.error("验证码错误");
        }

        // 标记已使用
        record.setUsed(true);
        codeMapper.updateById(record);

        // 检查用户名
        LambdaQueryWrapper<AppUser> existQuery = new LambdaQueryWrapper<>();
        existQuery.eq(AppUser::getUsername, reg.getUsername());
        if (appUserMapper.selectOne(existQuery) != null) {
            return Result.error("该用户名已存在");
        }

        // 创建用户
        AppUser newUser = new AppUser();
        newUser.setUsername(reg.getUsername());
        newUser.setNickname(reg.getNickname() != null ? reg.getNickname() : reg.getUsername());
        newUser.setEmail(reg.getEmail());
        newUser.setPassword(passwordEncoder.encode(reg.getPassword()));
        appUserMapper.insert(newUser);

        return Result.success("注册成功");
    }
}
