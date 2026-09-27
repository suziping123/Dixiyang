package com.dixiyang.server.Entity.dto;

import lombok.Data;
import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * 背景与颜色配置 DTO
 * 用于前端和后端之间传输用户背景配置和字体颜色配置
 *
 * @author SuZiPing
 * @version 1.0
 */
@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class BackgroundConfigDTO {
  /**
   * 背景预设：dynamic | static | gradient | grid | minimal | custom
   */
  private String preset;

  /**
   * 是否启用动画
   */
  private Boolean animEnabled;

  /**
   * 背景强度 (0-100)
   */
  private Integer intensity;

  /**
   * 颜色主题：purple | blue | cyan
   */
  private String colorTheme;

  /**
   * 自定义背景图片 URL（base64 或 文件URL）
   */
  private String customImageUrl;

  /**
   * 自定义字体颜色配置
   * 包含 textPrimary, textSecondary, textMuted, textDisabled
   */
  private FontColorsDTO fontColors;
}