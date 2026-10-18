# RAG 聊天消息导出菜单（2026-10-12）

## 需求

RAG 助手页（`/rag-assistant`）的消息操作原来只有单个「总结为设定」按钮，需要扩展为多出口：
- 多选项（下拉菜单形式）：复制 / 存便签 / 总结为设定 / **转发到广场**；
- 转发广场支持「存草稿」和「立即发布」两条路；
- AI 可生成**候选标题 + 标签**（点击一键应用，不自动落库）；
- 图标全部手绘 SVG（`fill=currentColor`，与现有 action-btn 同风格），**不用 AI 味重的 sparkle 魔棒类图标**。

## 方案

### 交互

`ChatMessage.vue` assistant 消息尾部 3 按钮 → **重新生成 / 编辑回答 / 导出▾**。导出按钮点开手写下拉菜单（4 项，图标 + 文字）：

| 菜单项 | 实现 | 说明 |
|---|---|---|
| 复制文本 | `navigator.clipboard.writeText` | 失败给手动选择提示 |
| 存为便签 | `stickyStore.create` 直接落库 | 截断 5000（便签 maxLength）、随机纸色、随机落在视口中下部（避开右下素材池）；先 `fetch()` 兜底未加载态 |
| 总结为设定 | 原 `CharacterSettingsDialog` 流程不变 | 事件改由菜单项触发 |
| 转发到广场 | 新组件 `ForwardToPlazaDialog` | 见下 |

- 菜单为**手写 popover**（非 el-dropdown）：EP 默认样式与现有手绘图标风格不搭；点菜单外关闭（capture 阶段 document click + `contains` 判断）。
- **导出的文本优先当前浏览中的历史版本**（`browseIndexOf`/`browseSourceOf` 取 paired/versions 对应格），否则当前内容——与气泡显示一致。
- 流式中的消息（isStreaming）不出导出按钮（与重新生成等一致）。

### ForwardToPlazaDialog（新组件）

- 标题输入 +「AI 候选」按钮（手动重跑）；打开时自动静默跑一次候选（失败不打扰）。
- 候选区（虚线高亮框）：候选标题点击应用；候选标签 chips 点击逐个 `+`/`✓` 切换；「一键应用」全上。
- 分区下拉（默认 `setting` 设定，与广场 5 分类一致）+ 标签多选（`allow-create` 回车创建，限 5）+ 正文 textarea（初值 = 消息原文，可编辑，限 20000）。
- footer：取消 / **存草稿** / **立即发布**。
  - 存草稿：`createDraft` → toast「已存入广场草稿箱」。
  - 立即发布：`createDraft` → `publishDraft(id, previewed=true)`（后端强制 `请先预览附件`，本弹窗即预览语义）→ toast「已发布到广场」；发布失败时草稿已存，提示去广场重发。
- 移动端：复用 main.css 全局贴底抽屉（width 640px 会被全局 100% !important 压掉），`meta-row` 单列化，输入字号由全局 16px 规则兜底。

### 后端新增

- `POST /idea/aiSuggest`（`routers/idea.py`）：入参 `{content}`（截断 4000），`call_llm`(temperature 0.4, max_tokens 200) + JSON 清理解析（照抄 `extractSettings` 套路），返回 `{title, tags}`（tags 去空、限 5）；需登录。
- prompt 模板 `build_idea_meta_prompt`（`prompt_templates.py`）：要求标题 8-20 字、禁出现「AI/回答/总结」字样，标签 3-5 个 2-6 字中文。

## 改动文件

- `dixiyang-vue/Dixiyang-vue3/src/components/chat/ChatMessage.vue`（导出下拉菜单 + 3 个新 emits：copyText/saveNote/forwardPlaza；删旧单按钮；清 `.extract-btn` 残留 CSS）
- `dixiyang-vue/Dixiyang-vue3/src/components/idea/ForwardToPlazaDialog.vue`（新建）
- `dixiyang-vue/Dixiyang-vue3/src/views/RagAssistantView.vue`（3 个 handler + 弹窗挂载 + `exportTextOf` 浏览版本感知）
- `DixyangFast/src/dixiyang/routers/idea.py`（`/idea/aiSuggest` 端点 + `AiSuggestReq`）
- `DixyangFast/src/dixiyang/services/prompt_templates.py`（`_IDEA_META_TEMPLATE`）

## 已知问题

- `ForwardToPlazaDialog` 的 `content` prop 与正文变量重名会被 `vue/no-dupe-keys` 拦截，正文内部变量命名为 `body`（首轮 ESLint 实测抓到，已修）。
- 存草稿与立即发布共用 `saveDraft()`：立即发布路径是「先建草稿再 publish」，若 publish 失败草稿仍在（提示去广场重发），不回滚草稿。
- 后端 `/idea/aiSuggest` 依赖 DeepSeek key；无 key 时返回 `生成失败`，前端弹错误 toast，功能不阻塞（候选是可选项）。

## 验证方式

- 前端：`npm run type-check` 0 错；`npx eslint` 三文件 0 错；`npm run build` EXIT=0。
- 后端：`uv run --no-sync python -c "ast.parse(...)"` 语法 OK。
- 手动建议：① hover AI 回答 → 导出▾ 菜单出现 4 项、点外关闭；② 复制→剪贴板有内容；③ 存便签→灵感墙出现新便签；④ 总结为设定→原弹窗正常；⑤ 转发广场→弹窗打开自动出候选→一键应用→存草稿/立即发布→广场可见；⑥ 375 宽弹窗贴底、菜单项触控 ≥44px。

---

*文档版本: v1.0 — 2026-10-12 创建*
