# 03 · CSS 视觉与主题系统

> [← 总目录](../README.md) ｜ 上一类：[02 Vue3 架构](./02-Vue3架构与状态管理.md) ｜ 下一类：[04 响应式适配](./04-响应式与移动端适配.md)

**这类面试考什么**：层叠上下文这类"原理级"坑（高频），design token 工程化，以及视觉还原能力。

---

## 1. 层叠上下文：页面背景被"吃掉"（⭐ 高频考点）

- **根因**：子元素 `position: absolute` 逃逸出父级 stacking context——父容器没建层叠上下文（缺 `position: relative`），absolute 定位参照跑到更外层，背景层反而盖在内容上/内容盖在背景上。
- **修法**：根容器补 `position: relative`，背景层 `z-index` 置底。**新建任何带背景层的页面/弹窗先查这条**。
- **实战 3 例**：点子库 `.idea-page`、404 页被全局背景图整层盖掉、小说编辑页背景图层叠。
- **面试话术**："`z-index` 不是全局数字比大小，它只在同一层叠上下文内比较——这是 absolute 定位『乱跑』类 bug 的统一根因。"
- **关键代码**（`src/views/IdeaLibraryView.vue` 真实，注意根容器上的警告注释——老工程师的"给后来者留路标"）：

```css
.idea-page {
  /* ⚠️ 警告后续 agent：新增页面根容器必须 position:relative，
     否则有背景图时整页被 #theme-bg 压住（看不见但可点）。
     先例：docs/404页被背景图覆盖修复.md、docs/小说编辑页背景图层叠与视觉AI修复.md */
  position: relative;
  min-height: 100vh;
}
```

**分析**：根因链——`.idea-page` 是 `position: static` → 它**自己不构成层叠上下文** → 子层 `position:absolute` 的定位与绘制上下文跑到最近的有定位祖先/根元素 → z-index 全局化比较，背景层反而赢。修复只需一行 `position: relative`，但**知道为什么要加**才是面试的区分点：`z-index` 只在"同一层叠上下文"内排序。

- 🔗 [点子库Demo实施记录](../../点子库Demo实施记录.md) §5 ｜ [404页被背景图覆盖修复](../../../dixiyang-vue/docs/404页被背景图覆盖修复.md) ｜ [小说编辑页背景图层叠与视觉AI修复](../../../dixiyang-vue/docs/小说编辑页背景图层叠与视觉AI修复.md)

## 2. backdrop-filter 双坑（⭐ 实测定位的经典案例）

- **坑 A — 输入控件"白雾蒙板"**：全局规则 `input, textarea { backdrop-filter: blur(10px) }` + 半透明底 → 输入框**聚焦时白雾、失焦消失**。EP 的 `select` 原生输入 `.el-select__input` 展开时命中该规则，把下层 placeholder 模糊成雾。
- **修法三层**：弹窗实底 `background: ... !important`（压文件尾全局规则）→ 弹窗内原生输入 `backdrop-filter: none !important` → 页面级 select 同治。**易错点**：EP popper teleport 到 `body`，必须用 `html .el-select__popper` 全局前缀，`html .el-dialog .el-option` 是错误选择器。
- **坑 B — 404/毛玻璃那类"看着像 z-index 其实是渲染层"问题**：靠 CDP `getComputedStyle` dump `backdropFilter` 实测取证，纠正了两轮肉眼误判。
- **面试话术**："毛玻璃类 bug 我不靠猜——CDP 打开聚焦态，把计算样式 dump 出来对照断言，一次定位到全局规则。"
- **关键代码**（`src/assets/main.css` 真实节选——**先看凶手，再看三层修复**）：

```css
/* ① 凶手：全局原生控件规则（137 行），任何 input/textarea/select 都命中 */
input, textarea, select {
  background: var(--surface-input);
  ...
  backdrop-filter: blur(10px);        /* ← 聚焦时把下层内容糊成白雾 */
}

/* ② 修复层1：弹窗实底（必须 !important，压过文件尾部同特异性的全局背景） */
html .el-dialog { background: #191c27 !important; backdrop-filter: none; }

/* ③ 修复层2：弹窗内控件关 blur（!important 压全局 137 行规则） */
html .el-dialog input, html .el-dialog textarea, html .el-dialog select {
  backdrop-filter: none !important;
}

/* ④ 修复层3：EP select 的原生输入框（popper teleport 到 body，不能用 .el-dialog 作用域！）
   实际类是 .el-select__input，不是 .el-option */
input.el-select__input, .el-input-number__input { backdrop-filter: none !important; }
```

**分析**（三层缺一不可的原因）：
- 全局规则是**元素选择器**（特异性 0,0,1），修复必须靠 `html .el-dialog`（0,1,1）+ `!important` 双保险——同特异性时**后到者胜**，而这份全局规则恰好在文件尾部，普通覆盖会输；
- **EP 的 popper/dropdown teleport 到 `body`**，物理上不在 `.el-dialog` 子树里 → `html .el-dialog .el-option` 是**永远匹配不到的错误选择器**，必须 `html .el-select__popper` 全局前缀——这是三层修复里最容易漏的一层（漏了就"下拉仍蒙板复燃"）。

- 🔗 [卡片毛玻璃底板与弹窗配色修复](../../../dixiyang-vue/docs/卡片毛玻璃底板与弹窗配色修复.md) ｜ [点子库Demo实施记录](../../点子库Demo实施记录.md)（蒙板复燃专项）

## 3. Design Token 主题体系（CSS 变量工程化）

- **知识点**：`--surface-* / --text-* / --accent-* / --radius-* / --dur-*` 一套变量驱动全站；**单主题（dark）** 下依然保留 token 层——换肤=改变量不改组件；旧变量名保留兼容（渐进迁移）。
- **面试话术**："token 的收益不在'多主题'，而在**改一处、全站生效 + 组件不感知配色细节**；老变量兼容是渐进式迁移的必要妥协。"
- 🔗 [dixiyang-vue/AGENTS.md](../../../dixiyang-vue/AGENTS.md)（主题系统章节）

## 4. 全局弹窗规范（去黑 + 实底 + 可读性）

- **知识点**：`el-dialog` 全局统一（配色/宽度/贴底抽屉），"不能全黑、也不能看不清"——用面板 token 分级（`--surface-glass` / `--surface-panel-strong`）替代拍脑袋取色；`ElMessageBox` 换 `el-dialog` 统一交互。
- 🔗 [弹窗面板全局化与去黑](../../../dixiyang-vue/docs/弹窗面板全局化与去黑.md) ｜ [设定上下文与弹窗样式统一](../../../dixiyang-vue/docs/设定上下文与弹窗样式统一.md)

## 5. 拟物质感与"去 AI 味"（视觉叙事）

- **知识点**：便签=5 色纸 + 随机微旋转 + 卷角 + 横格纸纹 + 投影，全 CSS 实现（`repeating-linear-gradient` 纸纹、`clip-path` 卷角）；"AI 味"的解法：克制用色、留白节奏、避免均质卡片阵。
- **面试话术**："拟物不是堆特效，是让视觉隐喻和功能一致——便签能拖、能钉、能划掉，纸的质感让交互不用说明书。"
- 🔗 [灵感墙便利贴实施记录](../../灵感墙便利贴实施记录.md) ｜ [Home页头部精简与视觉去AI味](../../../dixiyang-vue/docs/Home页头部精简与视觉去AI味.md) ｜ [落地页介绍页](../../落地页介绍页.md)

## 6. 层叠/阴影的性能意识

- **知识点**：`will-change` 只提升**合成有效**属性（`transform, opacity, filter`；`left/top` 无效还占内存）；拖拽 z-index 用语义值 210000 而非 20 亿魔数。
- 🔗 [灵感墙便利贴实施记录](../../灵感墙便利贴实施记录.md) §9（死代码与整理）

---
* [← 总目录](../README.md) ｜ 下一类：[04 响应式与移动端适配 →](./04-响应式与移动端适配.md)*
