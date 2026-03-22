package com.dixiyang.server.Entity.dto;
import lombok.Data;

/**
 * 字体颜色配置 DTO
 * 全局统一的文字颜色管理系统
 * 用于前端和后端之间传输用户自定义的字体颜色配置
 *
 * @author SuZiPing
 * @version 1.0
 */
@Data
public class FontColorsDTO {
    /**
     * 主要文本颜色（十六进制或rgba格式）
     * 用于标题、主要内容等最高优先级文本
     * 示例: "#ffffff" 或 "rgba(255, 255, 255, 1)"
     */
    private String textPrimary;

    /**
     * 次要文本颜色
     * 用于副标题、说明文本等次级内容
     * 示例: "rgba(255, 255, 255, 0.7)"
     */
    private String textSecondary;

    /**
     * 弱化文本颜色
     * 用于提示、辅助信息等弱化内容
     * 示例: "rgba(255, 255, 255, 0.5)"
     */
    private String textMuted;

    /**
     * 禁用文本颜色
     * 用于禁用状态的文本或不可交互的元素
     * 示例: "rgba(255, 255, 255, 0.3)"
     */
    private String textDisabled;

    /**
     * 描述文本颜色（可选）
     * 用于小说描述、摘要等描述性文本
     * 示例: "#e8e88e" 或 "rgba(232, 232, 142, 1)"
     */
    private String descriptionColor;

    /**
     * 链接文本颜色（可选）
     * 用于可点击的链接文本
     * 示例: "#3b82f6" 或 "rgba(59, 130, 246, 1)"
     */
    private String linkColor;

    /**
     * 强调文本颜色（可选）
     * 用于需要强调的内容
     * 示例: "#ff6b6b" 或 "rgba(255, 107, 107, 1)"
     */
    private String accentColor;
}