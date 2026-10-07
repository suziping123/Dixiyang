# Home 页头部精简与视觉去 AI 味

- **日期**: 2026-10-07
- **状态**: 已完成
- **涉及模块**: `/home` 首页（HomeView）
- **方向**: 保留暗色霓虹基调，只做头部精简 + 视觉打磨（用户确认）

## 需求

用户反馈 `/home` 页面「还是有点太不好了」，经确认聚焦两点：

1. **头部臃肿**：logo 100px + 3.5rem 渐变大标题 + glow 光条 + 副标题 + 大间距，首屏上半屏几乎全是标题区，作品网格要往下滚。
2. **整体视觉风格**：像 AI 生成的模板（motion-web `design-slop.md` 闸门命中）——紫蓝渐变、荧光装饰、色板发散、尺度断裂。

## 方案（对照 design-slop 闸门）

### ① 头部 → 单行顶栏

| 原状 | 现状 |
|------|------|
| `padding: 80px 120px` + 三个断点各一套固定覆盖 | `clamp(28px,5vh,64px) clamp(20px,5vw,64px)` 单一声明，断点覆盖全删 |
| logo 图 100px + `DIXIYANG ENGINE` 3.5rem 渐变字 + glow-line 光条 | 40px logo + 1.2rem 品牌字（负字距、单色，`ENGINE` 0.7rem accent 小字）单行排列 |
| 副标题 1.2rem + 荧光 text-shadow | 0.9rem 纯色小字副行 |
| `stage-header` 下距 60 + `section-title` 上距 50 | 32 + 24（合并塌缩后 32） |

顺带删除头部遗留的 **拖拽 demo 死代码**（`#div1` 落点 + `drag/drop/allowDrop` 三个函数）与未使用的 `SiliconAge` 导入。

### ② 去 AI 味

- **A4 紫蓝渐变全删**（原 5 处）：`ENGINE` 字 / logo 大字 / 小说标题渐变字 / 进入按钮渐变底（×2 状态）→ 分别改为单色 accent、纯色标题、`--accent-primary` 实底按钮
- **A5 装饰全删**（用户拍板「荧光全删」）：glow-line、card-glow 径向光晕、卡片底部渐变线、全部 text-shadow / drop-shadow 荧光、`✧` 装饰符（2 处）
- **A4 色板收敛为 蓝 + 青 + 中性**：角色按钮 hover 绿→青、时间线按钮 hover indigo→主蓝、统计高亮 indigo→主蓝、卡片/spinner 旧蓝 `#3b82f6`→`#4b8bf5`；删除红保留（语义）但降透明度
- hover 光晕改为 `filter: brightness(1.12)` / 边框变色；创建卡 hover 光晕改边框变青

### ③ 尺度与节奏

- `我的创作宇宙` 升为 display 级：`clamp(1.5rem, 2.4vw, 2rem)` / 800 字重（与 0.9rem 正文拉开 ~2–3 倍对比）
- 顺带删除 HomeView 内 `.floating-nav`/`.nav-item` **死样式**（FloatingNav 组件自有 scoped 样式，父组件 scoped 规则匹配不到子组件内部）

### 不动的部分

卡片 aspect-ratio 2/3、单击抽屉/双击翻转交互、gsap 入场与悬浮动画、FloatingNav、CreateCard、RAG 抽屉与知识球体结构。

## 改动文件

| 文件 | 改动 |
|------|------|
| `dixiyang-vue/Dixiyang-vue3/src/views/HomeView.vue` | 模板头部改单行顶栏、删装饰元素与拖拽 demo；scoped 样式整块重写（间距/渐变/荧光/色板/断点）；净删约 110 行 |

## 第二轮：结构补强（「太简单了」反馈）

用户反馈砍完装饰后页面显得空——按 design-slop 的结论「空是结构问题，不是装饰问题」，补结构而非补装饰：

### 编辑部式 Hero（不对称两栏）
- 左：`眉标（发丝线 + 创作台 WORKSPACE，accent 蓝）→ hero 标题 clamp(2rem, 3.6vw, 3.25rem)/900 → 欢迎语小字`
- 右：**大数字统计三联**——宇宙 / 角色 / 节点，`clamp(2.75rem, 5vw, 4.5rem)` 表格数字，标签 0.72rem 宽字距小字
- 数据为 `novels` 真实字段汇总（`computed` 求和），不引入杜撰指标（design-slop A8）

### 分节横规
- `全部作品 + flex 细线 + 计数徽章（pill）`——三种区块形态达成（Hero 不对称栏 / 横规分节 / 卡片网格），修复 A3「每段结构相同」

### 吸顶栏
- `topbar` 移出 header 成 `main-stage` 直属子元素，`position: sticky` + 负 margin 满幅出血（复用 `--stage-px` 变量）
- 滚动 >12px 出现玻璃底 + 发丝线（`.stuck`，scroll 监听 passive，卸载清理）
- 前置修复：`.engine-container` `overflow: hidden` → `overflow-x: clip`（拦横向溢出但不破坏 sticky）

### 卡片 hover 语义化
- 封面 `scale(1.04)`（hover = 「进入这个世界」）、边框 hover 变主蓝 50%——替代原玻璃边泛化 hover

### 尺度层级（自上而下）
`hero 3.25rem → 分节标题 2rem → 卡片标题 1.6rem → 正文 0.9rem`，大数字 4.5rem 为全页锚点（≈5× 正文）。

### 改动文件（第二轮）

| 文件 | 改动 |
|------|------|
| `dixiyang-vue/Dixiyang-vue3/src/views/HomeView.vue` | 模板加 Hero/横规/吸顶栏；script 加 `computed` 汇总与 scroll 监听；CSS 加 hero/横规/stuck/封面缩放，`overflow-x: clip` |

## 已知问题

- ~~首页品牌冲击力降低~~ → 第二轮已用 Hero 大数字统计 + 3.25rem 标题补偿。
- 死代码 `.bg-gradient-animation`（模板已无对应元素）暂留未删，与本次诉求无关。
- 仓库既有报错不变：type-check 9 处、lint 8 处（HomeView 三元表达式 `flippedCards...` 为既有）。
- 吸顶在部分浏览器若失效仅表现为「不吸顶」（正常滚走），无视觉破损。

## 验证方式

```bash
cd dixiyang-vue/Dixiyang-vue3
npm run type-check   # 无 HomeView 报错
npm run lint         # 无新增报错
npx vite build       # ✓ built
```

手工清单（对照 design-slop 静帧闸门）：

1. Hero：左标题区 + 右 宇宙/角色/节点 大数字（数值与列表实际一致，0 作品时显示 0）。
2. 滚动 >12px：顶栏浮出深色玻璃底 + 底部发丝线；回顶恢复透明。
3. 静帧无紫色/蓝色渐变字、无任何辉光/光条/荧光。
4. 色板只余蓝（主色）+ 青（高亮）+ 中性，删除红仅作语义。
5. 分节处「全部作品 —— 细线 —— (计数)」横规，与 Hero、网格三段形态各异。
6. hover 卡片：封面轻微推近 + 边框变主蓝；单击抽屉、双击翻转、进入创作、删除确认、悬浮动画行为不变。
7. 375 / 768 / 1440 宽度无横向滚动；移动端 Hero 纵向堆叠、统计行横排。
