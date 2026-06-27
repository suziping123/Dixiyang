package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("story_node")
public class StoryNode {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("novel_id")
    private Long novelId;

    @TableField("timeline_id")
    private Long timelineId;

    @TableField("title")
    private String title;

    @TableField("content")
    private String content;

    @TableField("create_time")
    private LocalDateTime createTime;

    @TableField("vector_id")
    private String vectorId;

    @TableField("event_date")
    private String eventDate;

    @TableField("event_type")
    private String eventType;

    @TableField("importance")
    private Integer importance;

    @TableField("character_names")
    private String characterNames;

    @TableField("tags")
    private String tags;
}
