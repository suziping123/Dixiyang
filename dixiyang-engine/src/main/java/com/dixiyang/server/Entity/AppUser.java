package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * @author SuZiPing
 * @version 1.0

 * 用户实体类 (对应 app_user 表)
 */
@Data
@TableName("app_user")
public class AppUser {
//    主键：bigint，NN，Key
    @TableId(type = IdType.AUTO)//设置主键自增
    private Long id;
//    字段：username，varchar(50)，NN
    private String username;
//    字段：passwd，varchar(255)，NN
    private String password;
//    可空字段：email，varchar(100)
    private String email;
//    可变字段：nickname varchar(50)
    private String nickname;
//    字段：create_time，datetime，注意要开启驼峰命名转化为下划线命名
    private LocalDateTime createTime;
//    用户背景配置（JSON）：存储背景预设、主题、强度等
    private String bgConfig;
}
