package com.dixiyang.server.Controller;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.VO.NovelVO;
import com.dixiyang.server.Entity.dto.NovelDTO;
import com.dixiyang.server.Entity.dto.PasswordDTO;
import com.dixiyang.server.Entity.dto.UserUpdateDTO;
import com.dixiyang.server.Entity.dto.BackgroundConfigDTO;
import com.dixiyang.server.Service.NovelService;
import com.dixiyang.server.Service.UserService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

/**
 * @author SuZiPing
 * @version 1.0
 */
@RestController
@RequestMapping("/user")
@Tag( name = "用户修改相关模块")
public class UserController {
    @Autowired
    private UserService userService;
    @Autowired
    private NovelService novelService;

    @PostMapping("/update")
    public Result update(@RequestBody UserUpdateDTO dto) {
        return userService.updateUser(dto);
    }

    @PostMapping("/password")
    public Result<?> changePassword(@RequestBody PasswordDTO dto) {
        return userService.changePassword(dto);
    }

    // 新增：获取当前用户信息
    @GetMapping("/info")
    public Result getUserInfo() {
        return userService.getCurrentUserInfo();
    }
}
