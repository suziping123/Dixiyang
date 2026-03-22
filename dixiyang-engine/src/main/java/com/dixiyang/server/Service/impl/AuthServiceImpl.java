package com.dixiyang.server.Service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Entity.AppUser;
import com.dixiyang.server.Entity.VO.UserVO;
import com.dixiyang.server.Entity.dto.AuthDTO;
import com.dixiyang.server.Mapper.AppUserMapper;
import com.dixiyang.server.Service.AuthService;
import com.dixiyang.server.Utils.JwtUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import com.dixiyang.server.Common.Result;

import java.util.HashMap;
import java.util.Map;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Service
public class AuthServiceImpl implements AuthService {
    @Autowired
    private AppUserMapper appUserMapper;//注入Mapper

//    写一个工具类来处理JWT和密码的加密
    @Autowired
    private JwtUtils jwtUtils;
    @Autowired
    private PasswordEncoder passwordEncoder;//这里用的是BCryptPasswordEncoder

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
            return Result.error("用户名或密码错误");
        }
//        在java中对比密码(Significant!!!)
//        使用passwdEncoder的matches方法来对比前端传来的没问和数据库查出来的加密串
        if  (!passwordEncoder.matches(password, appUser.getPassword())) {
            System.out.println(password);
            System.out.println(passwordEncoder.encode(password));
            return Result.error("用户名或密码错误");
        }

//        校验通过，生成token
        String token = jwtUtils.generateToken(appUser.getId().toString());
//       【解决泄露风险】手动挑选字段给前端 或者用 UserVO
        UserVO userVO = new UserVO();
        userVO.setId(appUser.getId());
        userVO.setUsername(appUser.getUsername());
        userVO.setNickname(appUser.getNickname()); // 数据库查出来的昵称
        userVO.setEmail(appUser.getEmail());

//        但会结果（Token和抹除密码后的用户对象）
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", userVO);

        return Result.success(data);
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
