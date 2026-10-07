# RAG 对话头像图标替换

> 最后更新: 2026-10-06
> 范围: 前端 `dixiyang-vue/Dixiyang-vue3`

## 一、需求

对话消息头像使用 emoji（👤/🤖），AI 味道过浓，替换为 Element Plus 图标（与页面现有图标体系一致）。

## 二、方案

| 位置 | 原 | 现 |
|------|----|----|
| `ChatMessage.vue` 用户头像 | `👤` | `<el-icon><UserFilled /></el-icon>` |
| `ChatMessage.vue` 助手头像 | `🤖` | `<el-icon><MagicStick /></el-icon>` |
| `RagAssistantView.vue` 等待首 token 加载气泡 | `🤖` | `<el-icon><MagicStick /></el-icon>` |

- 头像底色不变（助手蓝 `rgba(59,130,246,.2)`、用户紫 `rgba(168,85,247,.2)`），图标补同色系文字色（`--neon-cyan` / `--neon-purple`）融入玻璃质感。
- `el-icon` 继承头像 `font-size: 1.2rem`，无需额外尺寸规则。

## 三、改动文件

- `src/components/chat/ChatMessage.vue`：模板 2 处、import 补 `UserFilled/MagicStick`、样式 2 处加 color
- `src/views/RagAssistantView.vue`：加载气泡模板 1 处、样式 1 处加 color（`MagicStick` 原本已 import）

## 四、验证

- 全仓 grep `🤖|👤` → 0 残留
- `npm run type-check`：`ChatMessage.vue` 零错误；其余报错均为既有遗留（localImages/storyMappings/RagAssistantView 185,204/TimelineView，与本改动无关）
- Vite 模块编译：`ChatMessage.vue`、`RagAssistantView.vue` 均 200，图标 import 正常

## 五、已知问题

- 对话完成后的"加载气泡闪现"时序（`useChatStream.ts` 的 `sendMessage` 在收尾请求期间 `isStreaming` 仍为 true）本轮未改动；如复现，按既有分析将 `isStreaming` 置 false 提前到推入回答消息之后修复。
