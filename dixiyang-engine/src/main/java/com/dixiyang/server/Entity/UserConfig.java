package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 用户背景配置实体（扩展）
 */
@Data
@TableName("user_config")
public class UserConfig {
    private Long id;
    private Long userId;
    private String preset;
    private Boolean animEnabled;
    private Integer intensity;
    private String colorTheme;
    private String customImageUrl;

    /**
     * 使用 JSON 字段存储字体颜色配置
     * 数据库字段类型: JSON
     * 示例值: {"textPrimary":"#ffffff","textSecondary":"rgba(255,255,255,0.7)","textMuted":"rgba(255,255,255,0.5)","textDisabled":"rgba(255,255,255,0.3)"}
     */
    @com.alibaba.fastjson.annotation.JSONField(serialize = true)
    private String fontColorsJson;

    // ...getter/setter可以由Data这个注解结合框架自动上次那个哼
}