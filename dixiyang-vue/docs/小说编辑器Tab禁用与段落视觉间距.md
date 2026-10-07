# 小说编辑器 Tab 禁用与段落视觉间距

- **日期**: 2026-10-07
- **状态**: 已完成
- **涉及模块**: 小说编辑页（`novel-editor` 章节编辑器）

## 需求

用户反馈的三个问题：

1. **图标重复**：章节树「新建卷」按钮与编辑页「切换侧栏」按钮使用相同图标，难以区分。
2. **Tab 未禁用**：Tab 键每次仍产生缩进效果（光标在段尾，缩进却加在段首）。要求 Tab **彻底废掉**（不缩进、不移焦点）；段首缩进（`text-indent: 2em`）已生效需**保留**，折行文字自然下移顶格。
3. **回车段落间距**：回车分段后需在**视觉上**空出一段，但**不向文档写入空行**（内容仍是单个 `\n`）。

## 方案

### 1. 图标区分（纯 path 替换）

| 按钮 | 文件 | 新图标 |
|------|------|--------|
| 新建卷 | `ChapterTree.vue` | MDI `folder-plus-outline`（文件夹 + 加号） |
| 切换侧栏 | `NovelEditorView.vue` | 右侧面板图标 `M3 4h18v16H3V4zM5 6v12h14V6H5zM15 6h4v12h-4z`（`fill-rule="evenodd"`） |

### 2. Keymap：禁用 Tab 与缩进快捷键（`ChapterEditor.vue`）

CodeMirror6 关键机制（已核实 `buildKeymap`/`runHandlers` 源码）：**同 key 的命令按 keymap 数组顺序 `push`，依序执行、首个返回 `true` 者胜出**。因此自定义绑定必须放在 `...defaultKeymap` **之前**：

| 绑定 | 行为 | 覆盖的默认行为 |
|------|------|------|
| `Tab` + `Shift-Tab` | 有幽灵文本 → `accept-ghost`；否则 `return true` 吞掉 | 无（禁用后 Tab 不缩进、不移焦；Shift-Tab 若不吞会走浏览器默认移焦） |
| `Enter` + `Shift-Enter` | `insertNewline`（纯换行） | standardKeymap 的 `insertNewlineAndIndent`（会按语言缩进规则复制行首缩进） |
| `Mod-[` / `Mod-]` / `Mod-Alt-\` | `run: () => true` 吞掉 | `indentLess` / `indentMore` / `indentSelection` |

同时删除 `indentWithTab` 残留调用（import 已先行移除，不删则类型检查必挂）。

**键盘逃逸口（保留 CM6 内置，均已核实生效）**：

- `Ctrl-m`（mac 为 `Shift-Alt-m`）→ `toggleTabFocusMode`，常驻切换「Tab 用于移出编辑器」。
- `Esc` 后 **2 秒内**按 `Tab` → 移出编辑器（`handlers.keydown` 设置 2s 窗口）；注意**有幽灵文本时首次 Esc 被补全取消占用**，需再按一次 Esc 才会开启窗口。

### 3. 段落视觉间距（纯 CSS，不写入文档）

```js
'.cm-line': {
  textIndent: '2em',          // 段首缩进（保留）
  padding: '0 4px 1.95em',    // 底部 1.95em ≈ 33px = 一个空行（行高 1.95 × 17px）
}
```

**为何必须用 `padding` 而不能用 `margin`**（已核实 CM6 测量源码 `@codemirror/view/dist/index.js`）：

- 行高/位置测量基于 `child.dom.getBoundingClientRect()`（`:3329`、`:3383`）：`padding` **计入** rect，高度模型与 DOM 自洽；`margin` **不计入** rect，会导致 CM6 高度模型与实际 DOM 漂移 → 光标、选区错位。
- 选区绘制走 `coordsAtPos`（文本 rect）+ 跨块补间矩形，段间距在跨段选中时会被正确覆盖。
- `defaultLineHeight` 随之变为 ~66px，这正是「每行含间距」的真实行高，测量与估算**自洽**；副作用仅剩：视口外点击的 imprecise fallback（`posAtCoordsImprecise`）偏差、`.cm-activeLine` 当前行高亮连带段间距一起高亮（块级效果，可接受）。
- `text-indent` 只作用于段落首行，折行后续行顶格（既有行为，未改）。

## 改动文件

| 文件 | 改动 |
|------|------|
| `dixiyang-vue/Dixiyang-vue3/src/components/novel-editor/ChapterEditor.vue` | keymap 前置覆盖（Tab/Enter/缩进快捷键）+ `.cm-line` padding 段间距 |
| `dixiyang-vue/Dixiyang-vue3/src/components/novel-editor/ChapterTree.vue` | 新建卷 icon → folder-plus |
| `dixiyang-vue/Dixiyang-vue3/src/views/NovelEditorView.vue` | 切换侧栏 icon → 右侧面板 |

## 已知问题

- Tab/Shift-Tab 无法再移出编辑器，须用 `Ctrl-m` 或 `Esc`→`Tab`（2 秒窗口）。
- 有幽灵文本时首次 Esc 只取消补全，第二次 Esc 才开启 Tab 移焦窗口。
- 当前行高亮覆盖整个段落块（含视觉间距）。
- 仓库存在**与本次无关的既有报错**：type-check 9 处（`localImages.ts`/`storyMappings.ts`/`RagAssistantView.vue`/`TimelineView.vue`）、lint 8 处（`ragApi.ts`/`TimelineView.vue`/`characterApi.ts`/`localImages.ts`/`novelApi.ts`/`HomeView.vue`/`useChatStream.ts`），均不在本次改动文件内。

## 验证方式

```bash
cd dixiyang-vue/Dixiyang-vue3
npm run type-check   # 本次改动文件 0 错误（仅既有报错，见上）
npm run lint         # 本次改动文件 0 报错（仅既有 8 处）
```

手工清单：

1. Tab / Shift-Tab：光标处无缩进、焦点不移动；幽灵文本存在时按 Tab 接受补全。
2. `Ctrl-[` / `Ctrl-]` / `Ctrl-Alt-\`：无任何缩进变化。
3. 回车：新行从段首开始（无继承缩进）；文档中仅新增一个 `\n`（无空行）。
4. 视觉：相邻段落间空出约一行；光标点击定位、拖选、行号对齐均无错位。
5. 图标：「新建卷」显示文件夹+加号，「切换侧栏」显示右侧面板图标。
