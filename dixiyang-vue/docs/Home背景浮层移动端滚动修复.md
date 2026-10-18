# Home 背景浮层移动端无法滚动修复

> 版本：v1.0 ｜ 日期：2026-10-16 ｜ 类型：🐛 移动端 Bug 修复（前端）

## 1. 需求（用户原话）

> home 页面在移动端，选择背景图片的那个小页面手机无法上下滑动选择背景（可以上下滑动底层）你排查一下原因并解决

即：`/home` 顶栏「背景」按钮弹出的**背景选择浮层**里，手指上下滑动**滚不动浮层**，反而把**底层页面**滚动了 → 列表下半部分（含「不使用背景 / 上传背景」和后面的自定义背景）**永远选不到**。

影响面不止首页：`BackgroundControl mode="compact"` 同时被 `NovelPageHeader.vue` 使用（小说编辑页等页头），**所有带缺省视图的页面同病**；桌面端背景图多时（列表超过一屏）同样超屏不可达。

## 2. 根因（CDP 实证，非推断）

探针：headless Chrome（9222）新建标签 → `Emulation.setDeviceMetricsOverride(375×812, mobile)` → 登录态进入 → `Page.reload` → 点开浮层，读几何与计算样式。

> 首轮取证用的是**本地可校验 token**（当时为省掉登录步骤）；按新规范已改成**测试账号 `admin123/123456` 真实登录**（见 §5.1，规范见 [开发环境与测试账号.md](../docs/开发环境与测试账号.md)）。

| 取证项 | 修复前实测 | 结论 |
|---|---|---|
| 浮层（`.bg-compact-popper`）尺寸 | 21 张卡时 `h=1161.3px`，`bottom=1316.4`（视口 812） | **超出视口 504px** |
| 浮层计算样式 | `overflow-y: visible`、`max-height: none`、`clientH == scrollH == 1159` | **自身不可滚** |
| 面板（`.compact-panel`） | `overflow-y: visible`，`scrollHeight == clientHeight` | 无滚动容器 |
| 浮层定位 | `position: absolute; inset: 114.5px auto auto 20px`（挂在 **`position: sticky` 的 `.topbar`** 内，EP `teleported=false`） | 浮层**锚定在吸顶栏**：滚动页面它纹丝不动（多次采样 `popperTop` 恒 114.5） |
| 真实触摸（`Input.dispatchTouchEvent`，走合成器）在浮层内上滑 160px | `window.scrollY: 0 → 186`，面板 `scrollTop: 0 → 0` | **手指在浮层上滑动被浏览器"漏"给最近的可滚动祖先 = 文档 → 滚底层页面** |

**一句话根因**：浮层高度 = 卡片数 × 行高，**无上限**也不行内滚；而它锚在 sticky 顶栏上，超屏部分**既看不到也够不着**，手势还被"漏"去滚底层 —— 与用户描述完全一致（"可以上下滑动底层"）。

> 关键点：**手势不滚浮层**不是 `pointer-events` / `touch-action` 问题，而是**浮层里根本没有可滚动容器**，浏览器按规则把滚动交给文档。

## 3. 方案

给 compact 弹层加「**限高 + 内滚 + 滚动不外溢**」，桌面/移动共治（极小改动，不动模板与结构）：

```css
/* BackgroundControl.vue 的全局 <style> 块（popper 容器由 EP 生成，不能用 scoped） */
.bg-compact-popper {
  display: flex;
  flex-direction: column;
  max-height: min(68vh, 640px);   /* 桌面：不再随卡片数无限增高 */
  max-width: calc(100vw - 24px);  /* 极窄屏（<354px）不横向溢出 */
}
.bg-compact-popper .compact-panel {
  min-height: 0;                  /* flex 子项必须可收缩，否则内部 overflow 不生效 */
  overflow-y: auto;
  overscroll-behavior: contain;   /* 滑到边界不把滚动"传染"给底层页面 */
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}
@media (max-width: 768px) {
  .bg-compact-popper {
    max-height: min(70vh, calc(100vh - 190px));
    max-height: min(70dvh, calc(100dvh - 190px)); /* dvh 随地址栏收缩，留足上方 190px */
  }
}
```

**设计取舍与利弊**

| 方案 | 取舍 |
|---|---|
| ✅ **限高 + 内滚（已采用）** | 改动仅 CSS 20 行、桌面移动共治、不碰模板与 EP 定位；代价：浮层内多一条滚动条，长列表需在浮层内滚动 |
| ❌ 移动端改「固定贴底抽屉」 | 需覆写 EP 内联 `position/inset/transform` + 自造遮罩 + 处理点外关闭，风险与工作量数倍于收益（与本 bug 无关的交互重做） |
| ❌ 只把移动端网格改 3 列压矮 | 治标不治本（背景再多仍超屏），且卡片压到 ~95px 观感变差 |
| ⚠️ 关键细节：**不用 `overflow: hidden` 裁 popper** | 会让 EP 的 `.el-popper__arrow`（定位在盒子外）被裁掉；滚动下沉到内层 `.compact-panel`，箭头与标题保持固定 |

`dvh` 的作用：真机地址栏展开时 `100vh` 比可视高度大，纯 vh 限高可能顶出屏幕并触发 EP 上翻 → 顶部不可达；用 `100dvh - 190px` 按**真实可视高度**限高，保证浮层始终落在触发行下方。

## 4. 改动文件

| 文件 | 改动 |
|---|---|
| `dixiyang-vue/Dixiyang-vue3/src/components/BackgroundControl.vue` | 全局 `<style>` 块：`.bg-compact-popper` 增 `display:flex/flex-direction:column/max-height/max-width`；新增 `.bg-compact-popper .compact-panel` 内滚 + `overscroll-behavior: contain`；新增 `@media (max-width:768px)` 限高（dvh） |

无模板/JS/接口改动；`mode="full"`（设置页）不受影响（该分支不渲染 popover）。

## 5. 验证（CDP，修复后复测）

探针脚本（临时文件，未入库）：`probe-bg-touch.mjs`（真实触摸）、`probe-bg-fixed.mjs`（全量断言）、`probe-bg-desktop.mjs`（桌面回归）；真实账号复验用 `probe-bg-real-account.mjs` / `probe-bg-real-account2.mjs` / `probe-bg-finalize.mjs`。

| # | 用例 | 修复前 | 修复后 |
|---|---|---|---|
| 1 | 375×812、21 张卡：浮层不超屏 | ❌ `bottom=1316.4 / 812` | ✅ `h=568.4`、`bottom=723.5 / 812` |
| 2 | 浮层不横溢 | — | ✅ `right=350 / 375` |
| 3 | 浮层内真实触摸上滑 | ❌ `panel 0`、**`win 0→186`** | ✅ `panel 0→385`、**`win 0`** |
| 4 | 滚到底继续上滑（`overscroll-behavior`） | — | ✅ `panel=593/593`（到底）、`win 0` |
| 5 | 顶部下拉 | — | ✅ `win 0` |
| 6 | 滚动后点选背景 | — | ✅ 点「梁俊杰2309021115」→ 选中态 + `bgImageId` 落库 |
| 7 | 桌面 1440×900、21 张卡 | ❌ 超屏 | ✅ `bottom=779/900`、`max-height: 612px`、可滚、滚轮到底不穿透页面（`win 0`） |
| 8 | 桌面双列网格未变 | — | ✅ `140px 140px` |
| 9 | 控制台错误 | — | ✅ 0 |
| 10 | 375 + 1440 截图肉眼复核 | — | ✅ 浮层收回视口内、卡片正常、无截断异常 |

**汇总：移动端 8/8 + 桌面 3/3 PASS**（脚本对"点第二次把浮层点关"的测量误报已单独复测排除）。

### 5.1 真实测试账号复验（2026-10-16，替代假 token）

按新规范用测试账号 **`admin123 / 123456`** 走 `POST /api/auth/login` 真实登录（写 `token/username/userId/nickname/email/role` 六键）后复测，**不拦任何接口、无假数据**：

| # | 用例 | 结果 |
|---|---|---|
| 1 | 真实登录 → 进 `/home` | ✅ `userId=4`、路由 `/home`、顶栏渲染、昵称 `admin123` |
| 2 | 真实数据背景列表（9 张卡：7 内置 + 不使用 + 上传） | ✅ 渲染正常，0 控制台错误 |
| 3 | 375×667（小屏局促）：浮层不超屏 + 内可滚 | ✅ `bottom=614.7/667`、`clientH=437 / scrollH=528`、`overflow-y=auto` |
| 4 | 375×667 真实触摸上滑 | ✅ `panel 0→90`、**`window.scrollY` 恒 0** |
| 5 | 滚到底继续上滑（不穿透） | ✅ `panel=90/91`（到底）、`win 0` |
| 6 | 滚到底后尾部「上传背景」完整可见 | ✅ `top=509 / bottom=599 / vh=667` |
| 7 | 滚动后点选背景（功能链路） | ✅ 点未选中卡 → 选中 + 背景层生效；再点已选中卡 → 取消（既定语义）；复原账号原选中项 |
| 8 | 375×812 竖屏 | ✅ `bottom=712.6/812`、`right=350/375`（不横溢） |
| 9 | 桌面 1440×900 | ✅ `bottom=724.5/900`、`max-height=612px`、双列 `145px 145px` |
| 10 | 控制台错误 | ✅ 0 |

**关键差别**：真实账号只有内置背景（`customBgs` 为 0），9 张卡在 812 高度下不足以超屏（内容 ≈557px < 限高 568px），故**用 375×667 小屏取证"可滚"**（`scrollH=528 > clientH=437`）；375×812 与桌面 1440 用于回归"不超屏"。


## 6. 已知问题 / 注意

1. **探针副作用（开发浏览器）**：首轮取证用假 token 并写了本地缓存 —— `dixiyang_custom_bgs` 曾被探针置空、`dixiyang_theme_config.bgImageId` 被探针点选改写。二者都是**本地缓存**（真值以后端为准，`loadFromServer()` 会覆盖）；**已用真实账号 `admin123` 复验收尾**：登录后由服务器数据刷新、探针点选改动的背景已复原并确认服务端一致（`GET /userConfig/background` → `backgroundId=梁俊杰2309021115`、`customBgs=[]`），探针标签全部关闭。首轮假 token 与假接口响应**未写入后端**。
2. **dev 浏览器现状**：收尾后该浏览器停在 `admin123` 的真实登录态（token 有效期 7 天），供后续复验直接使用；若要换回自己的账号，直接退出登录重登即可（同账号重复登录会触发风控，见下）。
3. **未覆盖**：真机浏览器地址栏动态伸缩下的极限场景（`dvh` 已按规范处理，但未做真机走查）；EP 若因空间不足把浮层上翻，仍以限高保证可滚（顶部不会被裁）。
4. **同类风险（后续可选）**：其它"以卡片列表为内容的 EP popover / 抽屉"（如散落的窄浮层）若有同类"内容无上限"的情形，可套用同一模式（限高 + 内滚 + `overscroll-behavior: contain`）。
