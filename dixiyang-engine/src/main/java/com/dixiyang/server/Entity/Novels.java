package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.extension.activerecord.Model;
import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.util.Date;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Data
@TableName("novel")
public class Novels extends Model {
    @TableId(type = IdType.AUTO)
    private Long id;        // 对应 bigint

    @TableField(value = "user_id", insertStrategy = FieldStrategy.NOT_NULL) // 强制插入该字段，这里是
    private Long userId;    // 用户ID（必须赋值）


    private String title;

    @TableField("pen_name") // 数据库字段pen_name映射
    private String penName;

    private String description;

    @TableField("cover_url") // 数据库字段cover_url映射
    private String coverUrl;

    @TableField(value = "create_time", fill = FieldFill.INSERT) // 插入时自动填充
    private Date createTime;

    @TableField(value = "update_time", fill = FieldFill.INSERT_UPDATE) // 插入/更新自动填充
    private Date updateTime;
//    @Version
//    private Integer version;一般是读多写少
//    @TableLogic
//    private Integer deleted; // 逻辑删除字段，0表示未删除，1表示已删除// 旧版兼容：加 fill = INSERT，手动填充默认值
//    @TableField(fill = FieldFill.INSERT)
//    private Integer deleted; // 不再加 @TableLogic，避免版本冲突
}
