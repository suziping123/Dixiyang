/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-23 13:14:02
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-23 14:35:57
 * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Entity\NovelCharacter.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import java.util.Map; // 解决找不到 Map 的问题

import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("novel_character")
public class NovelCharacter {
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("novel_id")
    private Long novelId;

    @TableField("name")
    private String name;

    @TableField("gender")
    private String gender;

    @TableField("age")
    private Integer age;

    @TableField("appearance")
    private String appearance;

    @TableField("background")
    private String background;

    @TableField("personality")
    private String personality;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> extra;

    @TableField(value = "create_time", fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
