# 小说编辑页：背景图层叠修复 · 移动端抽屉 · 视觉与 AI 体验

> **适用范围**: `NovelEditorView.vue` 及 `components/novel-editor/*`
> **文档版本**: v1.0 ｜ **最后更新**: 2026-09-30

## 需求（用户反馈的 4 个问题）

1. **有背景图时"看不见但能点"**：`/novel-editor/{id}` 页面内容像被盖住，但鼠标仍能点击操作；无背景图时正常。
2. **视觉全黑无区分度**：不是要完全遮死背景图，而是"背景不影响创作"的前提下有层次（当时把背景整层遮死，且树/编辑区/侧栏全是 `#0d0d0f` 一片黑）。
3. **移动端没适配**：390px 视口三栏并排溢出、编辑区被挤没。
4. **AI 补全像死代码**：点"请求补全"无反应（空文档时静默 return）、mock 永远返回同一句、幽灵文本太淡看不见。

## 根因与方案

### 1. 背景图层叠（主根因，同 404 页历史问题）

| 元素 | 定位/层叠 | 结果 |
|------|----------|------|
| `#theme-bg`（`useBackgroundConfig.ts` 注入，`position:fixed; inset:0; z-index:0; pointer-events:none`，body 首子） | 定位层 | 画在上层 |
| `.editor-layout`（本页根容器，修复前 `position:static`） | 非定位 | 被整层压住 → 看不见 |
| `pointer-events:none` | — | 点击穿透 → **能点但看不见** |

- 无背景图时 `#theme-bg` 为 `display:none`，故"无背景图片没问题"。
- 全站普查：Home/Login/Timeline/RAG×2/角色/设置/落地页/404 根容器均有 `position:relative`，**唯独 `.editor-layout` 漏加**。
- **⚠️ 警告后续 agent：任何新增页面的根容器必须 `position: relative`，否则有背景图时整页被 `#theme-bg` 压住（看不见但可点）。先例：`docs/404页被背景图覆盖修复.md`。**

**修复**：`.editor-layout` 补 `position: relative`（带警告注释，NovelEditorView.vue 样式首段）。

### 2. 视觉层次（背景透出但不干扰创作）

| 层 | 做法 | 值 |
|----|------|----|
| 页面 scrim | 半透明深色，背景图朦胧透出；无背景图时叠在 body `#0d0d0f` 上视觉不变 | `rgba(13,13,15,0.72)` |
| 顶栏 | 玻璃条 | `rgba(10,10,12,0.55)` + `blur(14px)` |
| 左树 / 右侧栏 | 玻璃面板：背景透出但被 blur 糊掉，不影响读字 | `rgba(12,14,19,0.45)` + `blur(18px) saturate(1.15)` |
| 中间编辑区 | 浮起的"**稿纸**"卡片：比两侧亮一档 + 圆角 + 阴影，焦点所在 | `rgba(26,26,31,0.9)`、`margin:10px`、`radius-md`、`shadow 0 14px 44px` |

- 稿纸内状态栏改为内部分隔条 `rgba(0,0,0,0.22)`（不再用整块面板色）。
- 两侧栏边框统一 `--surface-glass-border`（原来 `--border-color`）。

### 3. 移动端（≤1024px）覆盖式抽屉

- `@media (max-width:1024px)`：`.col-tree/.col-sidebar` 改 `position:fixed`（`top:48px`、`width:min(82vw,300px)`、`z-index:40`），折叠态 `transform:translateX(±105%)` 滑出视口；替代桌面版 `width:0/opacity:0`。
- 遮罩 `.drawer-backdrop`（`inset:48px 0 0`、`z-index:35`）点击任意处收起；抽屉打开时左右互斥（`toggleTree/toggleSidebar`）。
- 顶栏窄屏（≤1024px）隐藏面包屑 `.topbar-center` 与 `.sync-badge`（右侧栏内有完整状态）、书名 46vw 截断。
- **`resize` 监听**：`breakpointOf(w)` 分 `mobile(<1024)/mid(<1440)/wide` 三档，**仅跨档位时**回默认折叠（不覆盖用户同档位内的手动切换）；由移动切回桌面时自动 `closeDrawers()` 清遮罩。
- 验证：390px `body.scrollWidth == innerWidth == 390`（修复前 650+ 横向溢出）。

### 4. 行内删除按钮可见性（`ChapterTree.vue`）

- 原 `.mini-btn` 常态 `opacity:0` 但 `pointer-events:auto`，`:focus` 也不显示 → 触屏/键盘"看不见但能点"。
- 修复：
  - `:focus-within`（行内）/ `:focus-visible`（按钮自身）→ `opacity:1`；
  - `@media (hover:none)` 触屏常显 `opacity:0.6`（触屏无 hover，用户确认取"常显半透明"方案）。

### 5. AI 补全体验（去"死代码感"）

> 链路本身是通的（CDP e2e：输入 → 点按钮 → `200` → ghost 出现）。问题在体验断点：

| 断点 | 修复 | 位置 |
|------|------|------|
| 空文档点"请求补全"静默 return，无任何反馈 | `triggerAI()`：空文档 `ElMessage.info('先写几句正文，AI 才能接着帮你续写')`；模板三处 `@ai-trigger` 改指它 | NovelEditorView.vue |
| 幽灵文本 `rgba(238,238,238,0.35)` 太淡看不见 | 改 `rgba(168,196,255,0.9)` + 蓝底 `rgba(75,139,245,0.12)` 圆角 + 虚线下划线 | ChapterEditor.vue `.cm-ghost-text` |
| mock 永远"屋里静悄悄的，什么声音也没有。"（2 句） | **后端去 mock**：mock Provider 与独立 `AI_*` 配置全部删除，补全改用真模型（复用 RAG 同款 `DEEPSEEK_*`） | `DixyangFast/src/.../completion/__init__.py`、`config.py` |

完整请求链（供排查）：侧栏按钮/Ctrl+Space → `triggerAI` → `useAICompletion.request(true)` → `POST /api/ai/completion` → 后端 `OpenAICompatibleProvider`（复用 `DEEPSEEK_*` 真模型）→ `ghostText` → ChapterEditor `SetGhostEffect` widget → Tab 接受 / Esc 取消 / 输入自动失效。

## 改动文件

| 文件 | 改动 |
|------|------|
| `dixiyang-vue/Dixiyang-vue3/src/views/NovelEditorView.vue` | `position:relative` + scrim 背景；顶栏玻璃；`.col-main` 稿纸卡片；抽屉/遮罩/resize/顶栏窄屏；`toggleTree/toggleSidebar/closeDrawers`；`triggerAI` |
| `dixiyang-vue/Dixiyang-vue3/src/components/novel-editor/ChapterTree.vue` | 玻璃背景；`.mini-btn` focus/触屏可见性 |
| `dixiyang-vue/Dixiyang-vue3/src/components/novel-editor/ChapterSidebar.vue` | 玻璃背景 |
| `dixiyang-vue/Dixiyang-vue3/src/components/novel-editor/ChapterEditor.vue` | ghost 样式加强；状态栏分隔条 |
| `DixyangFast/src/dixiyang/services/completion/__init__.py`、`config.py`、`routers/ai.py` | **去 mock**：mock Provider/独立 `AI_*` 配置删除，复用 `DEEPSEEK_*` 真模型；status 如实报 connected |
| `scripts/_probe-*.mjs`（verify-fix / visual-ai / empty-hint 等） | CDP 验证探针（本地工具，非运行时依赖） |

## 已知问题 / 取舍

- `type-check` 既有错误（`localImages.ts`/`storyMappings.ts`/`RagAssistantView`/`TimelineView`）与本次无关，本次涉及文件 0 新增错误。
- `backdrop-filter` 三处 blur（顶栏+双侧栏），老设备可能有合成开销；与 landing/首页玻璃风格一致，暂不降级。
- 无背景图时侧栏玻璃叠在 body 黑底上颜色更深一档，属预期（区分度来源是"稿纸亮一档"而非透明度）。
- CDP `Emulation.setEmulatedMedia` **无法模拟 `hover:none`**，触屏常显规则只做了 CSS 规则存在性验证，真机手感待实测。
- 探针调试中发现 Chrome `--headless` 外的实窗 renderer 偶发卡死（WS `Runtime.enable` 超时），处置：`/json/close` 旧 tab + `/json/new` 重建。

## 验证方式

```bash
# 构建与静态检查
cd dixiyang-vue/Dixiyang-vue3
npm run build-only        # ✓ 8.9s
npx oxlint src/views/NovelEditorView.vue src/components/novel-editor/*.vue   # ✓ 0
npm run type-check        # 仅既有 4 文件错误
```

CDP 探针（Chrome `--remote-debugging-port=9222`，dev server 5173 + 后端 8084 在跑）：

```bash
node scripts/_probe-verify-fix.mjs     # 背景图层叠 + 移动端抽屉 + mini-btn
node scripts/_probe-visual-ai.mjs      # scrim/玻璃/稿纸 computed 值 + ghost
node scripts/_probe-empty-hint.mjs     # 空文档点补全 → ElMessage 提示
```

手工验收清单：
1. 设置背景图 → `/novel-editor/{id}`：内容全部可见（背景朦胧透出），树/稿纸/侧栏三层分明；
2. 清除背景图 → 视觉近旧版但仍有稿纸层次；
3. 390px 视口：无横向滚动；点 ☰ 抽屉滑出 + 遮罩，点遮罩收起；顶栏无面包屑/badge；
4. 空章节点"请求补全" → 提示"先写几句正文…"；有文字 → ghost 蓝紫高亮出现，Tab 接受、Esc 取消；
5. 桌面 hover 章节行 → 删除按钮出现；Tab 键盘聚焦行 → 按钮可见。

---

*文档版本: v1.0 ｜ 维护者: Dixiyang Team*
