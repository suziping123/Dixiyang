/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-18 16:18:22
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-21
 * @FilePath: \dixiyang-vue\Dixiyang-vue3\src\api\types.ts
 * @Description: 前后端通信的类型定义
 */
export interface UserInfo {
  id: string;
  username: string;
  email: string;
  nickname?: string;
}

export interface LoginResponse {
  code: number;
  msg: string;
  data: {
    token: string;
    user: UserInfo;
  };
}

export interface RegisterResponse {
  code: number;
  msg: string;
  data: {
    token: string;
    user: UserInfo;
  };
}

/**
 * 字体颜色配置类型
 * 用于自定义文字颜色
 */
export interface FontColorsDTO {
  textPrimary: string;      // 主要文本颜色 (e.g., "#ffffff")
  textSecondary: string;    // 次要文本颜色 (e.g., "rgba(255, 255, 255, 0.7)")
  textMuted: string;        // 弱化文本颜色
  textDisabled: string;     // 禁用文本颜色
}

/**
 * 背景与颜色配置类型
 * 用于保存用户的背景预设和自定义颜色配置
 */
export interface BackgroundConfigDTO {
  preset?: string;          // 'dynamic' | 'static' | 'gradient' | 'grid' | 'minimal' | 'custom'
  animEnabled?: boolean;    // 是否启用动画
  intensity?: number;       // 背景强度 (0-100)
  colorTheme?: string;      // 'purple' | 'blue' | 'cyan'
  customImageUrl?: string;  // 自定义背景图片 URL
  fontColors?: FontColorsDTO; // 自定义字体颜色配置
}

