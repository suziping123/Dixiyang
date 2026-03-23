package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("timeline")
public class Timeline {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("novel_id")
    private Long novelId;

    @TableField("name")
    private String name;

    @TableField("parent_id")
    private Long parentId;

    @TableField("description")
    private String description;

    @TableField("create_time")
    private LocalDateTime createTime;
}
