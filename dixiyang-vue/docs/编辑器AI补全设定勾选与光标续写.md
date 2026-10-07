# 编辑器 AI 补全：设定勾选与光标处接续

> 日期：2026-10-06 ｜ 关联：[卷章节与AI补全接口](../../DixyangFast/docs/卷章节与AI补全接口.md)

## 1. 需求

1. 写章节时 AI 补全可**可选**结合当时的时间线、角色背景等设定生成（不带则维持原行为）。
2. 生成结果必须是**光标处的接续**，而不是把已有内容整段复述返回（本地 27B 模型实测会复述前文）。
3. 自动补全从"光标距文末 30 字内"**放宽到任意位置**（光标在哪停顿就在哪接续）。

## 2. 方案

### 前端（细粒度勾选）
- 新增 `AIContextPanel.vue`：「设定上下文」开关 + 三组 chips（角色/时间线/事件，事件按 eventDate 升序），组内滚动、计数、全选/清空；开关与勾选按 `novelId` 存 localStorage（`aiCtxEnabled_*` / `aiCtxSel_*`），默认关、全不勾。
- `useAICompletion.ts`：删 `NEAR_END_CHARS`（任意位置自动触发，保留 700ms 停顿 + 3s 冷却）；`CompletionSource` 新增 `getContext()`，POST `/ai/completion` 携带 `novelId + characterIds + storyNodeIds + timelineIds`。
- `NovelEditorView.vue`：onMounted 并行拉取 `/novelCharacter/all` `/timeline/all` `/storyNode/all`（失败不阻塞编辑），经 `ChapterSidebar` 的 `ai-context` slot 渲染面板，`bindAI` 注入 `getContext`（面板未就绪时空数组兜底）。

### 后端（组装与防复述）
- `routers/ai.py`：`CompletionReq` 加 `novelId/characterIds/storyNodeIds/timelineIds`（各钳 ≤50），透传 `CompletionContext`。
- `services/completion/__init__.py`：
  - `_build_setting_context()`：复用 `chat_service.build_fixed_context(character_ids, story_node_ids)` 查角色卡与事件 + 按 id 查 `timeline` 拼 `[时间线]` 条目，**总截断 1500 字符**；组装异常只记日志不阻塞补全。
  - system prompt 强化"严禁复述/重写光标前已有内容"，user prompt 尾部同步强调"只输出接续增量"。
  - `_strip_repetition()`：返回文本与 `cursor_before` 尾部重叠 ≥6 字符 → 截掉重叠前缀；截后为空 = `data:null`（无补全），杜绝"整段复述返回"。

## 3. 改动文件

| 端 | 文件 |
|----|------|
| 前端 | `src/components/novel-editor/AIContextPanel.vue`（新）、`src/composables/useAICompletion.ts`、`src/views/NovelEditorView.vue`、`src/components/novel-editor/ChapterSidebar.vue`（slot） |
| 后端 | `DixyangFast/src/dixiyang/routers/ai.py`、`services/completion/base.py`、`services/completion/__init__.py` |

## 4. 已知问题

- 章节无时间属性字段，"当时的时间线"无法自动推断，只能由用户勾选（本期方案即如此）。
- 防复述阈值为"文本前缀与前文尾部完全匹配 ≥6 字符"，若模型换一种措辞复述则拦不住（仍受 prompt 约束 + maxTokens 80 双重限制）。
- 设定上下文查库为同步执行（单请求 ≤150 条查询内，耗时可忽略）；无用户级限流（沿用现状）。

## 5. 验证方式

- 后端：`compileall` EXIT=0；单测 `_build_setting_context/_strip_repetition/_build_completion_prompt` ALL PASS；8085 测试实例 curl `/ai/completion` 带/不带 ids 均 200 返回真续写（本地 Ternary-Bonsai-2-27B）。
- 前端：`npm run type-check` 改动文件零新错误（既有的 localImages/storyMappings/RagAssistantView/TimelineView 9 处不变）；`oxlint` + `eslint` 改动 4 文件 0 错误。
- 手测点：① 任意位置停顿 700ms 出幽灵文本 ② 开关+勾选后补全贴合设定 ③ 不再复述光标前文 ④ 关闭开关/不勾选=旧行为 ⑤ Tab 接受插光标处、Esc 取消。
