package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;

@Data
@TableName("novel_relation")
public class NovelRelation {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("novel_id")
    private Long novelId;

    @TableField("related_novel_id")
    private Long relatedNovelId;

    @TableField("relation_type")
    private String relationType;

    @TableField("description")
    private String description;
}
