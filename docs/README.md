# Dixiyang 项目文档索引

## 文档概述

本文档提供了 Dixiyang 项目所有技术文档的索引和简要说明，帮助开发者快速找到所需信息。

## 根目录文档

### 1. [系统总览](./系统总览.md)
**位置**: `docs/系统总览.md`

**内容**:
- 项目整体概述
- 技术栈介绍（前后端）
- 核心功能模块说明
- 数据库结构概览
- 项目架构特点
- 当前开发状态
- 存在的问题和改进方向
- 部署建议

**适用人群**: 项目负责人、新加入的开发者、产品经理

---

### 2. [前后端接口对照分析](./前后端接口对照分析.md)
**位置**: `docs/前后端接口对照分析.md`

**内容**:
- 前后端接口完整对照表
- 已实现接口清单
- 待实现接口清单
- 详细的功能模块分析
- 优先级建议
- 技术改进建议
- 整体评估

**适用人群**: 全栈开发者、技术负责人、项目经理

---

### 3. [功能完成状态](./功能完成状态.md)
**位置**: `docs/功能完成状态.md`

**内容**:
- 功能完成状态的详细说明
- 已完成/未完成功能清单（✅/⚠️/❌）
- 完成度统计（前端65%, 后端58%）
- 开发优先级（高/中/低）
- 文档使用指南
- 维护规范

**适用人群**: 所有团队成员

---

## 后端文档 (dixiyang-engine)

### 5. [后端开发指南](../dixiyang-engine/AGENTS.md)
**位置**: `dixiyang-engine/AGENTS.md`

**内容**:
- 后端项目概述
- 技术栈详情
- 项目结构说明
- 核心功能模块
- API 接口规范
- 开发规范
- 部署说明

**适用人群**: 后端开发者

---

### 6. [后端接口文档](../dixiyang-engine/docs/后端接口文档.md)
**位置**: `dixiyang-engine/docs/后端接口文档.md`

**内容**:
- 统一响应格式说明
- 认证相关接口详解
- 小说管理接口详解
- 角色管理接口详解
- RAG 聊天接口详解
- 故事节点接口详解
- 错误码说明
- 注意事项

**适用人群**: 前端开发者、API 调用者、测试人员

---

## 前端文档 (dixiyang-vue)

### 7. [前端开发指南](../dixiyang-vue/AGENTS.md)
**位置**: `dixiyang-vue/AGENTS.md`

**内容**:
- 前端项目概述
- 技术栈详情
- 项目结构说明
- 核心功能模块
- API 接口调用方式
- 状态管理说明
- 路由配置
- 组件设计原则
- 样式规范
- 开发规范
- 构建和部署

**适用人群**: 前端开发者

---

### 8. [前端接口需求文档](../dixiyang-vue/docs/前端接口需求文档.md)
**位置**: `dixiyang-vue/docs/前端接口需求文档.md`

**内容**:
- 认证相关接口需求
- 小说管理接口需求
- 角色管理接口需求
- RAG 助手接口需求
- 故事节点接口需求
- 文件上传接口需求
- 用户配置接口需求
- 时间线接口需求
- 接口一致性要求
- 待实现接口清单

**适用人群**: 后端开发者、API 设计者

---

### 8.1 [登录鉴权与表单回车](./登录鉴权与表单回车.md) ✨ 新增
**位置**: `docs/登录鉴权与表单回车.md`

**内容**:
- 未登录访问 `/home` 跳转登录、JWT `exp` 本地校验 + 401 兜底
- `enterSubmit(fn, $event)` 回车跳下一输入框 / 最后一框提交
- 登录、注册、角色、时间线、设置、封面等覆盖点
- 危险删除确认不响应回车
- 验证方式与手动验收清单

**适用人群**: 前端开发者、测试

---

### 8.2 [登录页背景视频资源修复](../dixiyang-vue/docs/登录页背景视频资源修复.md) ✨ 新增
**位置**: `dixiyang-vue/docs/登录页背景视频资源修复.md`

**内容**:
- Vite `Failed to resolve import "/videos/卡比.mp4"` 根因（`transformAssetUrls` 编译为 import、源文件只在 `dist/`）
- 修复：资源移入 `src/assets/videos/` + `@/assets/...` alias 引用
- 验证命令与产物确认；`*.mp4` gitignore、`type-check` 既有错误等待办

**适用人群**: 前端开发者

---

### 8.3 [设置页重构](../dixiyang-vue/docs/设置页重构.md) ✨ 新增
**位置**: `dixiyang-vue/docs/设置页重构.md`

**内容**:
- 6 阶段改造：设计 token、信息架构（4 分类）、外观组件精简、FloatingNav 图标统一、后端 fontColors 端点、文档
- 死设置删除清单、compact 背景弹层修复、`backgroundId: ""` 清除语义
- 第二轮 8 项体验修复：Python 改密码端点、全局字号 rem 生效、登录页/首页移动端适配、设置页 sticky 分类条与按钮统一、触屏浮动导航、背景图可读性
- 第三轮 6 项：改密码业务码判定、设置页 RAG 玻璃面板风、RAG 移动端左右抽屉、登录标题/表单内切换入口、SMTP 端口分支与失败真实回传
- 改动文件清单、既有 type-check 错误、验证方式（build-only / eslint / mvn compile）

**适用人群**: 前端开发者、后端开发者、测试

---

### 8.4 [移动端浮动导航防遮挡](../dixiyang-vue/docs/移动端浮动导航防遮挡.md) ✨ 新增（v1.2）
**位置**: `dixiyang-vue/docs/移动端浮动导航防遮挡.md`

**内容**:
- 触屏 FloatingNav 由左下角常驻横条改为 FAB 悬浮球 + 点击展开（含全屏遮罩拦截误触）
- FAB 触发条件扩展为「触屏 或 视口 ≤1024px」：桌面缩窗下 100px hover 热区挡按钮的问题一并解决
- RAG 页 ≤768px「历史/上下文」按钮居中，远离左缘
- 点遮罩 / 再点球 / 选导航项 / 路由切换均收起；>1024px 桌面 hover 模式不变
- 层级结构、已知问题、验证方式
- **v1.2 修复（2026-10-10）**：宽屏桌面左侧 100px×全高隐形热区**穿透**（`wrapper pointer-events:none` + `trigger` 接管 hover 且 30→16px 收窄误触 + 展开面板单独恢复可点），根治"挡页面左侧点击/一扫过就弹"；CDP 冒烟 18/18；**新发现 FloatingNav 双实例挂载**（App.vue + 8 view，待清理），详见文档 v1.2 章节

**适用人群**: 前端开发者、移动端测试

---

### 8.5 [悬浮球美化与适配修复](../dixiyang-vue/docs/悬浮球美化与适配修复.md) ✨ 新增
**位置**: `dixiyang-vue/docs/悬浮球美化与适配修复.md`

**内容**:
- 修复 FAB 模式两处布局回归：`top:50%` 未重置导致巨型胶囊、`left` 特异性被桌面规则抢走导致横条压球
- 悬浮球/横条纯 CSS 美化：内高光、呼吸光晕、双图标交叉过渡、按压波纹、条目 stagger
- safe-area 预留、Esc 收起、wrapper z-index 130（压过 RAG 抽屉 120）、reduced-motion 降级
- **v1.1**: 球位置迁至**右侧垂直居中**（避开首页知识球体/时间线图例），wrapper 改右侧全高锚点条 + `pointer-events:none`，横条向左展开、条目方向反转
- 已知取舍（抽屉与球重叠、遮罩盖抽屉）、验证方式

**适用人群**: 前端开发者、移动端测试

---

### 8.6 [表单内联校验与错误文案统一](../dixiyang-vue/docs/表单内联校验与错误文案统一.md) ✨ 新增
**位置**: `dixiyang-vue/docs/表单内联校验与错误文案统一.md`

**内容**:
- 抽象通用警告模板：`FieldError.vue`（输入框下方内联红字）+ `useFormValidation.ts`（字段级/跨字段校验）+ `errorText.ts`（错误文案映射）
- 登录页拆 `el-form/rules` 三处统一；补齐原缺失的 `nickname`/`code` 校验规则，删 18 处 `ElMessage.warning`
- 后端原始错误只进 console 不上屏（HTTP 接口 + RAG 聊天气泡）
- `confirmDelete` 标题去硬编码、`ElMessageBox` 全套玻璃美化（新增 `--warning` 语义 token）
- **v1.1**: 昵称/邮箱**脏值检测**——blur 未改动内容则不发 `/user/update`、不弹「更新成功」（`useUser.ts` 快照比对）

**适用人群**: 前端开发者

---

### 8.7 [更换邮箱验证码流程](../dixiyang-vue/docs/更换邮箱验证码流程.md) ✨ 新增
**位置**: `dixiyang-vue/docs/更换邮箱验证码流程.md`

**内容**:
- **需求**：改邮箱不该失焦即写库（`sXXXXXXXX@outlook.co` 曾直接成功）；须收得到新邮箱验证码才准改
- **根因**：`DixyangFast /user/update` 零校验；邮件验证码设施（`EmailVerificationCode`/SMTP）早已存在却从未接到改邮箱（purpose 白名单缺项）
- **后端**：purpose 白名单加 `CHG_EMAIL`（9 字符，兼容 `VARCHAR(10)` 无需改表）；`verify_change_email_code()` + 唯一性校验；**全部校验通过才落库**
- **前端**：邮箱从「blur 即存」剥离为更换流程（新邮箱 → 发码 60s 倒计时 → 输码 → 确认）；昵称仍失焦即存且只提交 `{ nickname }`

**适用人群**: 前端、后端开发者

---

### 8.8 [移动端响应式修复](../dixiyang-vue/docs/移动端响应式修复.md) ✨ 新增
**位置**: `dixiyang-vue/docs/移动端响应式修复.md`

**内容**:
- **角色管理**：删旧左侧导航 `margin-left` 残留（恢复居中）、卡片/字号降档、`el-dialog width=min(650px,92vw)` 修超宽挤掉按钮、删 scoped 够不到的死代码
- **主页**：顶栏 `min-width:300px` 与大字缩放；双列小卡 `.card-content 28→14px` + 字号降档，修内容溢出挤压底部三枚操作按钮
- **NovelPageHeader**：补齐此前为零的媒体查询（共用顶栏，3.5rem → 1.6rem）
- 全部改动包在媒体查询内，宽屏桌面零影响

**适用人群**: 前端开发者、移动端测试

---

### 8.9 [角色管理页移动端适配与美化](../dixiyang-vue/docs/角色管理页移动端适配与美化.md) ✨ 新增
**位置**: `dixiyang-vue/docs/角色管理页移动端适配与美化.md`

**内容**:
- **双列自适应**：`repeat(auto-fill, minmax(150px, 1fr))` 一条规则覆盖全部窄屏 —— 375 屏两列（每卡 ≈166px）、320 屏自动降单列；平板档 `280→240px`
- **单卡瘦身**：266px → 约 205px（−23%），信息一项不减；描述 `min-height:2.32em` 固定两行保证同排按钮对齐
- **移动端修复**：触屏去掉 sticky hover 位移改按压反馈；输入框 `font-size:16px` 防 iOS 聚焦缩放；长表单弹窗改**底部抽屉**（`margin: auto auto 0` 抵消 EP 默认 15vh + body 内滚动 + 安全区），删除确认框用 `.delete-dialog` 排除
- **美化**：圆角归 `--radius-md/sm` 两档、硬编码色值换 `--accent-soft/--danger-soft/--accent-purple`、动效统一 `--dur/--ease-out`、头像内描边、幽灵创建卡虚线描边 + 加号旋转、卡片上浮淡入错峰（最多 8 张）
- **零 JS 改动**：仅模板 2 处（`v-for` 补 `index` + 内联 `--i`、删卡弹窗加类）与样式表

**适用人群**: 前端开发者、移动端测试

---

### 8.10 [卡片毛玻璃底板与弹窗配色修复](../dixiyang-vue/docs/卡片毛玻璃底板与弹窗配色修复.md) ✨ 新增
**位置**: `dixiyang-vue/docs/卡片毛玻璃底板与弹窗配色修复.md`

**内容**:
- **取证方式**：Chrome CDP 探针 + 像素级测量（锐度/对比度/截图字节数），纠正前两轮的推断
- **卡片透明真因**：底板一直是 `rgba(255,255,255,.05)`，而 `backdrop-filter` **只模糊背后内容、不提供底色**；实测 `will-change`/`transform`/`position`/`overflow` 四种切换对结果**零影响**（旧判断方向错误）
- **弹窗全黑真因**：`main.css` 那条是 `!important`，而 **`!important` 优先于任何非 `!important` 声明、与特异性无关**（旧判断"复合选择器压过"错误），故修复需逐条补 `!important`
- **修复**：新增 `--surface-panel-strong: rgba(16,18,26,.52)`（实测白字对比度 18.9、背景摆幅比原值减半），全局 `.glass-card`（时间线+角色页共用）与角色卡、角色弹窗统一换用；补 `-webkit-backdrop-filter`、移除多余 `will-change`
- 影响面已核实：`HomeView`/`CreateCard` 各自 scoped `.glass-card` 不受影响；`.glass-sm/lg/xl` 未动

**适用人群**: 前端开发者、UI 排查

---

### 8.11 [弹窗面板全局化与去黑](../dixiyang-vue/docs/弹窗面板全局化与去黑.md) ✨ 新增
**位置**: `dixiyang-vue/docs/弹窗面板全局化与去黑.md`

**内容**:
- **需求**：弹窗不能"一块全黑"、也不能淡到看不清；不再逐页写样式，改全局 `.el-dialog` 全站复用（含此前无样式的「AI 设定助手」）
- **像素标定**：面板 `#0d0d0f`（L 0.0032）→ **`#222530` = rgb(34,37,48)**（L 0.0188，白字对比度 **15.27**），实测否掉"半透明玻璃"方案——亮衬底上会糊成一片白，白字对比度只剩 2.38~3.37 不合格
- **另修一个深层坑**：`main.ts` 里 `element-plus/dist/index.css` 在 `main.css` **之后**导入，同特异性时 EP 赢 → 标题色被 EP 的 `rgb(48,49,51)` 覆盖到几乎不可见；统一用 `html` 前缀提升特异性（不引入 `!important`）
- **范围**：8 个弹窗（角色创建/编辑/删除、时间线×3、换封面、AI设定助手、编辑回答）自动生效；移动端 ≤768 全站统一贴底抽屉；组件内约 120 行重复样式删除

**适用人群**: 前端开发者、UI 排查

---

### 8.12 [404页被背景图覆盖修复](../dixiyang-vue/docs/404页被背景图覆盖修复.md) ✨ 新增
**位置**: `dixiyang-vue/docs/404页被背景图覆盖修复.md`

**内容**:
- **根因**：背景图是 `#theme-bg`（`position:fixed; z-index:0`，body 首子节点），全站页面根容器靠 `position:relative` 画其之上，唯独 `.ld-404` 是非定位元素被整层压住
- **修复**：`.ld-404` 补 `position:relative`；`html:has(.ld-page)` 亮纸底规则扩展为同时匹配 `html:has(.ld-404)`
- 改动仅 2 处 CSS、零 JS；含既有 type-check 错误说明与验证命令

**适用人群**: 前端开发者

---

### 8.13 [小说卷章节API封装](../dixiyang-vue/docs/小说卷章节API封装.md) ✨ 新增
**位置**: `dixiyang-vue/docs/小说卷章节API封装.md`

**内容**:
- `types.ts` 末尾追加卷/章节/正文类型：`Volume`、`VolumeDTO`、`Chapter`、`ChapterDTO`、`ChapterContent`、`SaveContentResult`、`ConflictResult`
- 新增 `chapterApi.ts`：11 个函数覆盖卷 CRUD、章节 CRUD、正文读取/保存/冲突检测（`http + assertApiResponse`，返回 `Promise<ApiResponse<T>>`）
- 路径对齐 `DixyangFast` 的 `/volumes`、`/chapters` 路由；`novelId` 走路径参数、body 用 `Omit<ChapterDTO,'novel_id'>`

**适用人群**: 前端开发者

---

### 8.14 [章节草稿本地优先存储](../dixiyang-vue/docs/章节草稿本地优先存储.md) ✨ 新增
**位置**: `dixiyang-vue/docs/章节草稿本地优先存储.md`

**内容**:
- **需求**：章节编辑 Local First —— 先落本地 IndexedDB（800ms 防抖），再异步同步云端；断网不丢稿、不阻塞
- **`src/utils/draftDB.ts`**：原生 IndexedDB 封装（`dixiyang-drafts`/`chapters`，`keyPath: chapterId`，`novelId` 索引），单例 open、`settled` 防重复回调；IDB 不可用降级内存 Map（编辑器绝不崩溃，`getDraft` 永不 reject）
- **`src/composables/useChapterDraft.ts`**：`loadDraft` 本地优先（先 flush 上一章 pending 再读）、`scheduleSave` 防抖 800ms、`flushSave` 立即落盘、`markSynced` 清脏标记、`dispose` + `onScopeDispose` 自动清理、`wordCount` 去空白计字
- 改动文件、已知取舍（本地优先不处理服务端冲突）、验证命令与手工验收清单

**适用人群**: 前端开发者

---

### 8.15 [小说编辑页背景图层叠与视觉AI修复](../dixiyang-vue/docs/小说编辑页背景图层叠与视觉AI修复.md) ✨ 新增
**位置**: `dixiyang-vue/docs/小说编辑页背景图层叠与视觉AI修复.md`

**内容**:
- **⚠️ 核心警告**：有背景图时 `/novel-editor/{id}` 整页被 `#theme-bg`（fixed/z-index:0/pointer-events:none）压住 → 看不见但能点；根因是根容器 `.editor-layout` 缺 `position: relative`（全站唯一漏加者，同 404 页历史问题）。**后续新增页面根容器必须 `position:relative`**
- **视觉**：不遮死背景也不全黑——页面半透明 scrim（0.72）+ 顶栏/双侧栏玻璃（blur 18px）+ 中间"稿纸"浮起卡片（亮一档+圆角+阴影）
- **移动端 ≤1024px**：树/侧栏改 fixed 覆盖式抽屉 + 遮罩 + 左右互斥；顶栏窄屏收缩；`resize` 监听跨档位回默认（不覆盖手动切换）；390px 横向溢出修复
- **mini-btn**：`:focus-within/:focus-visible` 显示 + `@media(hover:none)` 触屏常显 0.6（修"看不见但能点"）
- **AI 补全去死代码感**：空文档触发给 ElMessage 提示、ghost 改蓝紫高亮+虚线下划线、**后端 mock/独立 `AI_*` 配置全部消灭**（改见条目 19）
- CDP 探针验证记录与手工验收清单

**适用人群**: 前端开发者、移动端测试、**所有新增页面的开发者（先读警告）**

---

### 8.16 [单点登录与登录风控](./单点登录与登录风控.md) ✨ 新增
**位置**: `docs/单点登录与登录风控.md`

**内容**:
- **顶号踢出**：`app_user.session_id` 单会话号 + JWT `sid` claim，登录覆盖写入、请求时比对；被踢端下次请求 401「账号已在其他设备登录」，前端提示并跳登录
- **登录风控**：10 分钟内登录 3 次 → 密码登录强制邮箱验证码（`require_code`），验证码登录解除；前端自动切验证码模式
- **双后端对齐**：Java 补齐 `send-code/login-by-code` 邮件验证码设施（`spring-boot-starter-mail` + `.env` 兜底）；Python 复用既有验证码体系；风控时间统一 UTC 共表可比
- 改动文件清单、双后端端到端 12/12 PASS 验证记录、已知问题（JWT 双密钥、Java 注册不验码、permitAll）

**适用人群**: 全栈开发者、测试

---

### 8.17 [RAG对话头像图标替换](../dixiyang-vue/docs/RAG对话头像图标替换.md) ✨ 新增
**位置**: `dixiyang-vue/docs/RAG对话头像图标替换.md`

**内容**:
- 对话头像 emoji 👤/🤖 替换为 Element Plus 图标：用户 `UserFilled`、助手 `MagicStick`（含等待首 token 加载气泡）
- 头像底色不变，图标补同系文字色（`--neon-cyan`/`--neon-purple`）；`el-icon` 继承既有字号
- 改动 2 文件、grep 零残留、type-check/vite 编译验证

**适用人群**: 前端开发者

---

### 8.18 [编辑器AI补全设定勾选与光标续写](../dixiyang-vue/docs/编辑器AI补全设定勾选与光标续写.md) ✨ 新增
**位置**: `dixiyang-vue/docs/编辑器AI补全设定勾选与光标续写.md`

**内容**:
- 「设定上下文」面板（开关 + 角色/时间线/事件三组 chips 细粒度勾选，按小说存 localStorage），勾选 ids 随 `/ai/completion` 传后端；后端复用 `build_fixed_context` + 查 timeline 表组装上下文（总截断 1500 字符）
- **防复述**：prompt 强化"严禁复述光标前内容" + `_strip_repetition` 截掉与前文尾部 ≥6 字重叠的返回文本（修本地模型整段复述返回问题）
- 自动补全去"距文末 30 字"限制 → 光标任意位置停顿 700ms 即出幽灵文本（700ms 停顿 + 3s 冷却保留）
- 改动 4 前端 + 3 后端文件；compileall/type-check/lint 全过，8085 实测带/不带 ids 均 200

**适用人群**: 前端开发者、后端开发者

---

### 8.19 [小说编辑器Tab禁用与段落视觉间距](../dixiyang-vue/docs/小说编辑器Tab禁用与段落视觉间距.md) ✨ 新增
**位置**: `dixiyang-vue/docs/小说编辑器Tab禁用与段落视觉间距.md`

**内容**:
- Tab/Shift-Tab 彻底废掉（有幽灵文本时接受补全，否则吞掉不缩进不移焦）；吞 `Mod-[`/`Mod-]`/`Mod-Alt-\` 缩进快捷键；`Enter` 改 `insertNewline` 覆盖 `insertNewlineAndIndent`（不复制行首缩进）——全部利用「同 key 按数组顺序先命中」前置在 `...defaultKeymap` 之前
- 回车段落间距纯 CSS：`.cm-line` 底部 `padding: 1.95em`（≈一个空行），**padding 计入 `getBoundingClientRect` 故 CM6 测量自洽，不能用 margin**；不向文档写入空行
- 键盘移出编辑器逃逸口：`Ctrl-m`（toggleTabFocusMode）与 `Esc`→`Tab` 2 秒窗口（有幽灵时 Esc 需按两次）
- 附带：新建卷 icon → folder-plus、切换侧栏 icon → 右侧面板（消除两按钮同图标）
- type-check/lint 验证通过（仅仓库既有报错，均不在改动文件内）

**适用人群**: 前端开发者

---

### 8.20 [设定上下文与弹窗样式统一](../dixiyang-vue/docs/设定上下文与弹窗样式统一.md) ✨ 新增
**位置**: `dixiyang-vue/docs/设定上下文与弹窗样式统一.md`

**内容**:
- 设定上下文标题 30px→0.78rem（根因：组件未设字号落全局 h3，scoped 跨不过组件边界）；去卡中卡融入侧栏；启用开关改纯色状态钮（灰=关/蓝点发光=开，状态文字只在 hover title）
- ElMessageBox 标题看不清根因：底色是 5% 白半透明玻璃，亮页上糊白 → 改 `--surface-dialog: #222530` 实底（对齐 el-dialog，白字对比度 15.3）
- 按钮复用时间线页 `.btn-icon` 玻璃语言：玻璃次钮 + accent 实底主钮；**修复死规则** `.is-danger`（EP 不给盒子加该类）→ 改 `:has(状态图标)` 激活危险红确认钮
- 影响面：全站 message-box 统一（EP css 后导入，规则均带 `!important`）；type-check/lint 本次文件 0 报错
- **后续**：新建 `DialogHost.vue`（Promise 化输入/确认/离开三态 el-dialog），NovelEditorView 5 处 ElMessageBox 全部换用，复用全局 `html .el-dialog` 样式 + 移动端底部抽屉响应式；顺带修复取消时 Promise 未捕获 rejection

**适用人群**: 前端开发者

---

### 8.21 [Home页头部精简与视觉去AI味](../dixiyang-vue/docs/Home页头部精简与视觉去AI味.md) ✨ 新增
**位置**: `dixiyang-vue/docs/Home页头部精简与视觉去AI味.md`

**内容**:
- 需求：`/home` 头部臃肿 + 整体像 AI 模板（用户确认方向：暗色基础打磨）
- 头部 → 单行顶栏：40px logo + 1.2rem 单色品牌字 + 0.9rem 小字副行；`80px/120px` 固定 padding → 三档 clamp；glow 光条、3.5rem 渐变大字、拖拽 demo 死代码全删
- design-slop 闸门修复：紫蓝渐变 ×5、荧光 text-shadow/drop-shadow、card-glow 光晕、`✧` 装饰符全删；色板收敛 **蓝+青+中性**（角色绿/时间线 indigo hover → 青/蓝，删除红保留）
- `我的创作宇宙` 升 display 级 `clamp(1.5rem,2.4vw,2rem)`；删 HomeView 内 `.floating-nav` 死样式；卡片/翻转/抽屉/动画结构不动
- **第二轮（「太简单了」反馈）**：编辑部式 Hero 不对称两栏（3.25rem 标题 + 宇宙/角色/节点大数字统计，真实字段汇总）、分节横规（标题+细线+计数徽章）、吸顶栏（sticky 负 margin 出血 + 滚动玻璃底，`overflow:hidden`→`clip` 解锁）、卡片 hover 封面推近+主蓝边；尺度层级 4.5rem→0.9rem ≈5×
- 验证：type-check/lint 无新增、`vite build` ✓

**适用人群**: 前端开发者

---

### 8.22 [主页宇宙分页与改密码提示修复](../dixiyang-vue/docs/主页宇宙分页与改密码提示修复.md) 🐛 修复
**位置**: `dixiyang-vue/docs/主页宇宙分页与改密码提示修复.md`

**内容**:
- **主页 10 个上限**：前端硬编码只拉第 1 页 + 参数 `pageSize`（驼峰）被 FastAPI 忽略（路由是 `page_size`，恒默认 10）+ 计数用 `novels.length`（封顶 10）→ 三重叠加导致第 11 个宇宙"消失"
- 修复：`page_size` 参数对齐、分页状态 + 「加载更多（x / total）」按钮（追加失败回退页码）、Hero/分节计数全部改用后端 `total`、删除同步 `total--`
- **改密码点击无反应（主根因）**：密码表单 `@submit.prevent` 是空处理器而按钮 `type="submit"` 无 @click → 点击触发 submit 被空转 prevent，`changePassword` 根本不执行（零请求零红字零 toast），仅末框回车可触发 → "时好时坏"；修复 = 按钮改 `type=button`+`@click` 直调 + 防重入。次根因：`errorText.ts` 关键词 `/密码/` 把「当前密码不正确」吞成登录文案「账号或密码不正确」→ EXACT 精确表补 4 条业务原文；按钮文案「保存信息」→「修改密码」
- 附带记录：登录风控（10 分钟 3 次锁密码登录）、单点登录踢号机制、测试账号残留（`codex_pwd_t1`/`codex_pg_t2`）
- **第二轮（「加载更多太逆天」反馈）**：删除×分页不自洽根因（本地 filter+total-- 估算 vs 服务端权威 offset → 删除后空页死循环 + 多页数据空洞）→ `realignList` 按已加载条数并行重拉前 N 页对齐 + `withListLock` 互斥锁 + 空页自动兜底 + 触底自动加载（IntersectionObserver 哨兵 200px 预载，与按钮双轨）+ `loadError` 失败重试态 + 移动端 44px 触摸目标
- 验证：API 实证旧参数恒 10 条→新参数正确分页、type-check/lint 无新增、`vite build` ✓

**适用人群**: 前端开发者、后端开发者

---

### 8.23 [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md) ✨ 新增
**位置**: `docs/RAG编辑消息版本切换与原文不落盘.md`

**内容**:
- `/rag-assistant` 编辑消息（AI 回答 + 用户提问）：改前原文**不落盘**（链文件去 `originalContent`、弹窗去「原始回答」对照、edits.json 去原文字段）、AI 修正学习**只注入 keyPoint 要点**
- 消息级版本模型：`versions[]` 只存改后快照 ≤6（= 最多改 6 次），气泡底部版本条 `‹ 当前·N个版本 ›` 左右浏览、恢复（不占配额）、删除（confirmDelete 确认、配额减一、删当前回退上一版、删空保 content）
- 新接口：`POST /chatHistory/restore-version/{sid}`、`DELETE /chatHistory/version/{sid}`；PUT 加 `truncateAfter`（用户提问编辑后链同步截断，修复刷新丢编辑/旧问答复现）
- 编辑入口配额满 6 拦截；中途 `displayContent` 未定义导致气泡全空白的回归已修复
- **第二轮（截图反馈）**：① 编辑提问后走 `sendStreamMessage` 重发通道导致同一提问本地+链各重复一份（"多个对话"）→ 改走 `regenerateMessage(idx+1)` 只生成回答；② emit 双参数被 Vue 内联 `$event` 截成第一个（消息序号）→ 第 2+ 条消息恢复/删除报「版本不存在」→ 改 emit 单参数 versionIndex + 守卫改长度判断；存量脏链不自动清洗（删会话重聊）
- **第三轮**：切换永远显示最新（versions 初版只存改后内容，改1次时与 content 相同）→ 改为编辑前快照改前内容，`versions=[原文,改1前,…]`、content 恒最新，删除与 content 解耦
- **第四轮**：切提问版本回答永远是最新 → 编辑提问三重截断把旧回答物理删除 → 新增回答 `paired` 成对存档（regenerate 请求体 `prevAnswerVersions` 携带旧回答写入链）、`browseMap` 提问↔回答浏览联动、恢复/删除成对编排（restore/delete 加 `field` 参数）；**旧会话已删回答无法找回需删会话重聊**
- **第五轮（截图反馈）**：① 同一回答**双写**（后端 `/chat/stream`、`/chat/regenerate` 写链 + 前端 `saveToBackend→batchSave` 又追加一份，链文件实证同秒两份、编辑只改其中一条致"一条有版本条一条没有"）→ 删除前端两处 `saveToBackend` 及函数，**后端为聊天唯一写入点**；② 已完成回答下 typing 指示器残留（`isStreaming` 复位被标题生成/会话刷新阻塞）→ push 后立即复位；③ 提问+回答双版本条冗余 → 版本条加 `role==='assistant'` 条件，**仅回答侧一个**、提问联动高亮；④ `editMessage`/`restore`/`delete` 不检查业务返回码（拦截器对 code≠200 也 resolve）→ 显式检查并中止；⑤ 后端 thinking 不再拼进 content（分开累计独立字段落链）
- 验证：后端逻辑单测全绿（第五轮链语义 15/15：追加/截断/快照/成对恢复删除/越界）、py_compile ✓、type-check 9/lint 8 基线无新增、`vite build` ✓

**适用人群**: 前端开发者、后端开发者

---

### 8.24 [RAG消息版本交互与接口规范](./RAG消息版本交互与接口规范.md) ✨ 新增（当前唯一契约）
**位置**: `docs/RAG消息版本交互与接口规范.md`

**内容**:
- 版本切换/删除功能的**唯一契约**：数据模型不变量（I1 成对等长 / I2 删除成对 / I3 铅笔独立 / I4 不重算）、格子模型（`k/M`，分母=历史+1 恒定）、渲染条件、切换（成对联动、AI 铅笔条互斥）、删除（成对删+跳最新）、API 契约（PUT/DELETE/废弃 restore/batchSave 造数入口）、边界与旧数据、测试用例矩阵
- 第七轮（"全乱"反馈）按"先文档后实现"重做：移除"恢复此版本"（切换即查看）、`pairBrowse`/`aiOwnBrowse` 双浏览态、AI 铅笔历史独立入口
- 第八轮（v1.37）：流式生成期间切换不显加载（隐藏流式区+自动滚动+旧回答延迟截断）、最新格 `M/M` 可删（`delete-current` 原子回退上一版）、`truncateAfter` 恒 false
- 验证：API 自动化 30/30 PASS（v1.36）+ 29/29 PASS（v1.37 增补 B0-B4）、type-check 9/lint 8 基线、build ✓

**适用人群**: 前端开发者、后端开发者、测试

---

### 8.25 [点子库与创意社区策划](./点子库与创意社区策划.md) ✨ 新增（策划评审稿 v1.1）
**位置**: `docs/点子库与创意社区策划.md`

**内容**:
- 新功能策划（待实施）：私有点子草稿 + 公开创意社区（帖子），**五分区**（点子灵感/角色/设定/时间线/技术分享）+ **四类结构化只读附件**（对话链/角色卡/设定集/时间线视图，发布时从现有数据复制为 `storage/community/.../attach_*.json`，原数据删除不影响）+ **角色附件一键导入到我的小说**（复制行+extra 文件、vector_id 置空）
- 互动：点赞/平铺评论/收藏/标签关联表筛选/热门排序（Redis ZSET `idea:hot` + 60s 计数回写 + 频控 + 降级回 DB）
- 数据库补强（v1.1）：时间统一 `create_time`、`idea_attachment` 多态附件表、`idea_post_tag` 关联表、评论 `Text`、组合索引、`app_user` 加 `avatar_url`/`pen_name`
- 技术：Python FastAPI 单栈 + MySQL 7 表 + Redis（前置 `pip install redis`）；API 契约 `/api/idea/*`、前端 6 组件、里程碑 P0-P3、测试计划
- **§8 功能路线图**：本期范围 / 二期候选（Chroma `idea_posts` 相似推荐、设定/时间线导入、投票征集、每日灵感、作者主页、存入知识库）/ 远期；同类产品调研依据（SillyTavern、DZMM、造物纪、饼次元、LitMemo、云作者等）

**适用人群**: 产品、前端开发者、后端开发者、测试

---

### 8.26 [项目清理记录](./项目清理记录.md) ✨ 新增
**位置**: `docs/项目清理记录.md`

**内容**:
- 2026-10-08 稳健版清理两批次的完整记录：批次1（提交 `aebe648`）删死代码/杂物/Java 空类并修坏路由；批次2 归档 daily-log（34 文件出库、本地保留）+ 修 docs README 全部 12 条断链（41/41 通过）+ 4 份过期文档勘误（功能完成状态、前后端接口对照、双端 AGENTS）
- 明确保留清单（Java 双栈、vitest、未调用端点等）与保留理由
- 验证方式（基线对比、grep 零引用、链接自动校验）与遗留问题

**适用人群**: 所有协作者（尤其首次 pull 前了解 daily-log 出库影响）

---

### 8.27 [点子库Demo实施记录](./点子库Demo实施记录.md) ✨ 新增
**位置**: `docs/点子库Demo实施记录.md`

**内容**:
- 点子库功能 Demo 全链路落地（策划 v1.1 契约）：后端 7 表 + 草稿→预览→发布→广场→互动→评论→角色卡附件导入全流程（API 测试 **40/40 PASS**）；前端 `IdeaLibraryView` 四 Tab + 编辑/详情双弹窗 + `/ideas` 路由 + 导航入口（CDP 冒烟 **SMOKE PASS**，控制台 0 错误）
- **Demo 裁剪差异表**：Redis 跳过（进程内存频控+实时热门）、`app_user` ALTER 跳过、附件仅接 chat_snapshot/character_card、前端 4 文件替代策划 6 组件
- **踩坑记录（先查文档的一课）**：背景层叠 `position:relative` 致命坑、`userId` 存储 key、无 chat 分区（对话快照挂 idea 区）、FloatingNav 各 view 自挂、`enterSubmit` 回车约定、code≠200 resolve 等 8 项
- **§10 第二轮（v1.1，2026-10-09）**：用户 5 问题修复（EP 浮层深色化、chat 段路径、频控 check/mark 分离+inline 错误条）+ 配图全链路（`idea_post_image`）+ 小红书瀑布流 + 来源对话级联；API 15/15 + 回归 40/40 + 冒烟 SMOKE2 PASS
- **§11 第三轮（v1.2，2026-10-09）**：用户 9 条反馈修复（① emoji 图标 → 自绘 `IdeaIcon.vue` ② 赞/藏弹跳动画 ③ 卡脚快捷赞藏 + 后端 `collectedByMe` ④ 768 断点移动端 + 横向溢出根因修复 ⑤ 卡片 `#171a24` 实底 ⑥ 弹窗蒙板 blur 根因修复 ⑦ 详情画廊置顶 ⑧ 下架帖编辑 `PostEditDialog.vue` + toggle 取消修复）；API 19/19 + 回归 40/40+15/15 + 冒烟 26/26 + 基线 9/8/build ✓
- **§12 第四轮（v1.3，2026-10-09）**：下架改来源（`sourceRef` 附件重建/清空移除/无效整体回滚，API 专项 **25/25**）+ **来源选择器抽共享组件 `SourcePicker.vue`**（根治"没复用写点子代码/回显不了"——`getNovelOptions` 的 `records` 分页口径踩坑 + `destroy-on-close` 防串数据 + `ensureReady` 懒加载防 401 炸 console）+ **配图拖拽排序 `useImageDragSort.ts`**（零依赖 Pointer Events，两弹窗接入，拖影/高亮/move 语义/封面跟随）；回归 40/40+15/15+19/19 + SMOKE3 **28/28** + 拖拽 **8/8** + 回显 **9/9**
- 已知问题：setting/timeline 导出未接、配图文件不回收等（`collectedByMe`、配图拖拽已落地）与后续路线

**适用人群**: 前端、后端、测试

---

### 8.28 [Redis与管理后台策划](./Redis与管理后台策划.md) ✨ 新增（策划评审稿 v1.0）
**位置**: `docs/Redis与管理后台策划.md`

**内容**:
- **Redis 落地实施**（衔接点子库策划 §4 设计）：现状（内存频控 `_limit_check/_limit_mark`、直写 DB 计数）、`services/idea_cache.py` 封装层 API（rate/count/hot/view_seen + 降级铁律 Redis 挂全回源 DB）、迁移分期 P0-P2（频控迁移 → 计数旁路 → 热门 ZSET → 浏览去重 → 60s 回写/10min 重建定时任务）
- **管理后台策划**（全新）：`app_user.role` 零破坏 ALTER、`require_admin` + 前端路由守卫、P0 四页面（仪表盘/用户管理/内容审核/举报 P1）、`/admin/*` API 草案、`src/views/AdminView.vue` 组件结构、M1-M5 里程碑
- 风险：管理员 SQL 手工开通、平台下架 vs 作者重新上架绕过约定、移动端不适配（明确不做）

**适用人群**: 产品、前后端开发者

---

### 8.29 [局域网访问与launch调试](./局域网访问与launch调试.md) ✨ 新增（v1.0）
**位置**: `docs/局域网访问与launch调试.md`

**内容**:
- **网线/USB 共享网络设备访问开发服务**：`vite.config.ts` 加 `server.host: true`（根因修复，监听 0.0.0.0）+ 新建 `.vscode/launch.json`（前端 Vite / 后端 FastAPI debugpy / 全栈 compound 一键启动，Trae/VS Code 通用）
- **踩坑**：launch 里给 npm 追加 `--host 0.0.0.0` 会被 npm 吞参、`0.0.0.0` 被 Vite 当 root 目录 → `vite.config.ts` 不加载 → `@` 别名/`/api` 代理全失效 → **页面全黑**；修法 = launch 不传 args，host 一律由 config 负责
- 防火墙 5173/8084 放行命令、`Network:` 日志取址、真机验证套路；debugpy attach_amd64.dll 警告为无害

**适用人群**: 前端、测试（真机调试）

---

### 8.30 [灵感墙便利贴实施记录](./灵感墙便利贴实施记录.md) ✨ 新增
**位置**: `docs/灵感墙便利贴实施记录.md`

**内容**:
- 拟物便利贴全站悬浮层：软木板纹理、图钉动画（钉入受压/拔钉上弹）、5 色纸、微旋转、卷角、投影
- 两态模型：浮动（全站可见可拖动）↔ 钉住（记 `pinned_route`，仅该路由显示、锁定、再点解锁）
- 素材池（📮 牛皮纸信箱）：拖入=投喂 `inPool=true` → 编辑器 AI 补全勾选 `noteIds` 注入 prompt，可取回
- 专用页面 `/inspiration`：软木板背景、工具条（新建/颜色/搜索/池口）、首次引导、空墙提示
- 后端：`sticky_note` 表 + 归一化坐标(%) + 正文文件存储 + 补全上下文 `[灵感]` 段组装（≤300 字/条、总≤1500 字）
- **v1.2 修复（2026-10-11）**：`done` 字段只加模型未补旧表（create_all 不给旧表加列）致查询/新建 500 → `main.py` lifespan 启动 inspect+ALTER 自动补列 + 一次性幂等补列脚本，详见文档 §1.2
- 验证：API 自动化 14/14 PASS、CDP UI 17/17 PASS（桌面 1440 + 移动 375 截图肉眼复核）、build ✓

**适用人群**: 前端开发者、后端开发者、测试

---

### 8.31 [广场真瀑布流与增量加载](./广场真瀑布流与无限滚动.md) ✨ 新增（v1.0）
**位置**: `docs/广场真瀑布流与无限滚动.md`

**内容**:
- 广场 Tab 从「CSS multi-column 伪瀑布流 + 页码器」改为「**手写短列优先真瀑布流 + 无限滚动**」：`relayout()` 短列优先算法（每卡进最矮列、绝对定位 left/top、各列首卡贴顶），`IntersectionObserver` 哨兵触底追加（12条/批）、`ResizeObserver` 高度变化 rAF 节流重排，删除广场页码器
- 后端游标分页：`/idea/posts` 增 `cursor` 参数，`new/like/hot` 真游标（元组比较/ZSET 名次）翻页**跳过 COUNT 全表**，响应 `{hasMore,nextCursor}`；`recommend` 内存排序每请求变分保留页码语义；损坏游标兜底当最后一页
- 仅改广场 Tab（草稿/我发布的/收藏保留页码器）；修复「首屏不足一屏时 IO 被 loading 挡掉不再触发」的填满视口兜底
- 验证：后端游标专项 **16/16 PASS**（三排序翻页不重不漏/分区过滤/损坏兜底）、CDP 冒烟 **16/16 PASS**（桌面 5 列各列贴顶、触底 36→49、移动端 375 双列无溢出）、type-check 9 / lint 2 基线不破

**适用人群**: 前端、后端、测试

---

### 8.32 [JobInterviews 前端面试知识索引](./JobInterviews/README.md) ✨ 新增
**位置**: `docs/JobInterviews/`（目录，19 个 MD，分 7 区）

**内容**:
- **Practical/**（原 8 类项目实战档案）：工程化 / Vue3 架构 / CSS 视觉 / 响应式 / 前后端协作 / 交互表单 / 性能稳定 / 排错方法论——每条 = 说明 + 真实代码引用（标注来源文件）+ 分析 + 面试话术 + 文档佐证
- **五领域面试常问**（前端 / Java 后端 / Python 后端 / 运维 / 实施），每领域两篇：
  - `01 项目已用`：问题 + 项目真实代码 + 定位/答法（JWT 过滤器单点登录、SseEmitter 流式状态机、FastAPI yield 依赖、启动自愈补列、乐观更新、短列瀑布流等）
  - `02 通用高频`：项目未直接涉及的必考题，配可背代码——前端 JS 语言基础（原型链三关系与手写 new/四种继承演进、this 四规则与手写 bind、深拷贝循环引用、事件委托、回流重绘读写分离、事件循环输出、防抖节流、Promise.all/竞态、Proxy 响应式、diff 与 key、CORS、浏览器缓存）+ Java（ConcurrentHashMap、线程池 7 参数、@Transactional 失效、B+树、Redis 三击、OOM）+ Python（GIL 三选型、装饰器、滑动窗口限流）+ 运维（Nginx SSE 三配、CI 流水线、现场排查）+ 实施（数据迁移对账 SQL、UAT/回滚预案模板）
- `JobInterviews/README.md` 总目录：分区导航 + 必读前置 + 面试使用建议；**238 条相对链接全量校验 0 死链**
- **问答对齐审查**（2026-10-15）：14 篇 Q&A 逐题审查"答法是否正面回应题眼"——重写 Frontend/01 Q2（乐观更新失败处理：原答案误以成功路径实现细节开篇，现改为失败兜底三策略（回滚/重试/自愈）+ 项目"故意不回滚"的真实取舍与源码佐证 + 强一致边界）；修正 Implementation/02 Q4 交叉引用文字；复验 238 链接 0 死链
- **事实核对审查**（2026-10-15，第二轮）：01 篇每处代码引用逐一对照真实源码、02 篇抽查技术论断，修正 12 处失实/瑕疵——① Frontend/01：Q1 handleUnauthorized 忠实化（/login 判断+置位顺序）、Q3 "三信号"改"双信号"（真实仅 moved+suppressClick）、Q6 补 current 焦点归一定义、Q8 unwrap 改真实行为（code===200+toast+返 null，6 处复制定义治理债）、Q9 改真实 draftDB API（putDraft/isDirty/clearDirtyByChapter，删虚构 syncQueue）；② Frontend/02 Q1 事件循环输出勘误（3 4 7 → **3 7 4**，then 链第二节入队晚于 await 恢复点）；③ Java/01：Q4 selectPage 标注改诚实（项目现为 Wrapper 全量查询）、Q5 response.py 路径修正、Q6 改项目真实 Spring Security `encode/matches`（原误用 jBCrypt API）、Q3 标注 AGENTS 方案收紧点；④ Python/01：Q5 schema 对齐真实（color 为 str+白名单、Literal 作演进讲法、Pydantic 默认值自动拷贝）、Q7 Result 默认值逐字对齐；复验 238 链接 0 死链
- **讲解风格修订："从基础讲起"取代"深挖"**（2026-10-15，用户反馈）：原"📐 原理深挖"被反馈"讲的不清楚、没有从基础讲起、覆盖不广"——讲解统一改为**先讲清楚基础（概念从零讲起）→ 关键机制拆解 → 延伸追问（同一知识面）**，不堆术语。完成范围：**Frontend/01 全部 9 题（整篇重写）＋ 五领域 02 篇共 42 题全部补"先讲清楚基础 + 延伸追问"**（Frontend 14 + Java 7 + Python 7 + 运维 7 + 实施 7；全库 51 处延伸追问，每题一处）；"深挖"字样全站清零（板块与链接标签均改为"延伸阅读/延伸追问"），239 链接 0 死链；附带修复 Frontend/01 Q1 两行 Tab 缩进、axios 拦截器执行顺序经 1.13.6 本地实测勘定（请求拦截器后注册先执行、响应拦截器先注册先执行）
- 适用人群: 求职者（前端/全栈/后端/运维/实施）、需要对外介绍项目的同学

---

### 8.33 [Home背景浮层移动端滚动修复](../dixiyang-vue/docs/Home背景浮层移动端滚动修复.md) 🐛 修复
**位置**: `dixiyang-vue/docs/Home背景浮层移动端滚动修复.md`

**内容**:
- **现象**：`/home` 顶栏「背景」浮层（`BackgroundControl mode="compact"`，小说页头共用）在手机上**滑不动**——手指在浮层上滑动反而**滚动底层页面**，下半部分背景（含「不使用背景/上传背景」）永远选不到
- **根因（CDP 实证）**：浮层高度 = 卡片数 × 行高**无上限**（21 张卡实测 `h=1161px`，超视口 504px）且 `overflow-y: visible` **自身不是滚动容器** → 浏览器把滚动交给最近可滚动祖先（文档）；又因 EP `teleported=false` + 挂在 `position: sticky` 的 `.topbar` 内，浮层**锚死在吸顶栏**（采样 `top` 恒 114.5），滚页面也不露出来
- **修复**：`.bg-compact-popper` 增 `display:flex/max-height:min(68vh,640px)/max-width:calc(100vw-24px)` + 内层 `.compact-panel` `overflow-y:auto` + `overscroll-behavior:contain` + `-webkit-overflow-scrolling:touch`；移动端限高改 `min(70dvh, calc(100dvh - 190px))`（dvh 随地址栏收缩，防顶出屏幕/上翻）；**不用 `overflow:hidden` 裁 popper**（会裁掉箭头的定位盒外部分）
- **验证**：CDP 真实触摸（`Input.dispatchTouchEvent`）移动端 **8/8** 十桌面 **3/3** PASS——浮层 1161→568px 收回视口、浮层内上滑 `panel 0→385` 且 `window.scrollY` 恒 0（修复前 0→**186**）、滚到底不穿透页面、滚动后仍可点选背景、桌面 1440 双列未变、控制台 0 错误 + 双端截图肉眼复核
- **副作用声明**：首轮探针在 dev 浏览器注入过假 token/假自定义背景缓存；**已用测试账号 `admin123/123456` 真实登录复验收尾**——服务器数据刷新本地缓存、改动的背景已复原（服务端 `backgroundId=梁俊杰2309021115` 已核对）、探针标签全部关闭；首轮假接口响应未写入后端
- **真实账号复验**：375×667 小屏 `panel 0→90` 且 `window.scrollY` 恒 0、滚到底不穿透、尾部「上传背景」完整可见、滚后仍可点选（选中/取消语义正确）、375×812 + 桌面 1440 不超屏、控制台 0 错误

**适用人群**: 前端开发者、测试

---

### 8.34 [开发环境与测试账号](../docs/开发环境与测试账号.md) 📌 规范
**位置**: `docs/开发环境与测试账号.md`

**内容**:
- **本地验证统一登录入口**：测试账号 `admin123 / 123456`（dev 库 `userId=4`）——CDP 探针 / UI 验收 / 接口回归**一律真实登录**取 token（`POST /api/auth/login` → 写 `token/username/userId/nickname/email/role` 六键，复刻 `UserStore.setLoginInfo`）
- **禁止伪造 token**（如 `demo.<base64>.demo`）：守卫能骗过，但一次 401 就被拦截器 `clearAuth()` 踢下线，并把假数据写进 localStorage 缓存污染后续验收（本项目踩过）
- 风控与顶号注意：10 分钟内第 3 次密码登录起强制邮箱验证码（探针应一次登录多次复用 token，7 天有效）；单点登录会顶号，**别拿他人在用账号做自动化登录**
- 同步登记进 `AGENTS.md` 第 12 条与 `docs/JobInterviews/Practical/08-排错方法论.md`（探针前置步骤）

**适用人群**: 前端/后端开发者、测试、AI Agent

---

### 8.35 [背景图端适配分类](../dixiyang-vue/docs/背景图端适配分类.md) 🔍 分析 + ✅ 功能落地
**位置**: `dixiyang-vue/docs/背景图端适配分类.md`

**内容**:
- **判定依据是裁剪数学**：背景 `center/cover` 全视口（桌面 ≈1.78 / 手机 ≈0.46）→ 桌面竖幅图只剩中间 `A/1.78`、手机横幅图只剩中间 `0.46/A`
- **22 张逐张结论**：上传背景 11（桌面优先 5 / 通用 2 / 移动优先 4）、上传封面 4（3 张方图可作 2:3 封面、1 张 16:9 横图建议改作背景）、内置背景 7（桌面优先 5 / 通用 1 / 移动优先 1）
- **两个易踩坑**：①「手机上够清 ≠ 桌面上够清」（手机只需 750px 长边、桌面要 1920px）；② 主体靠边的图不能跨端用（横图给手机只留中间 1/4）
- **v1.1 功能落地（§9）**：选择器**按当前端排序 + 「电脑/手机」角标**——新增纯函数 `src/utils/bgFit.ts`（4 个门槛常量可调）、`BgImageGrid` 缩略图 `@load` 读尺寸 → 排序/角标（零额外请求）、单测 10 例；CDP 实测 375 竖屏「手机优先」置顶、1440 横屏顺序反转、功能卡仍钉末尾、点选不受影响
- 附选图规则表（两端通用 3:2~16:10 主体居中 / 手机 9:16~9:20 竖图 / 桌面 16:9 起）、"形状分类 vs 系统口径（含清晰度门槛）"差异说明、未做项（手动改分类 / 双端两套背景 / 上传提示）

**适用人群**: 前端开发者、设计/内容维护

---

### 8.36 [FloatingNav手机端溢出修复](../dixiyang-vue/docs/FloatingNav手机端溢出修复.md) 🐛 修复
**位置**: `dixiyang-vue/docs/FloatingNav手机端溢出修复.md`

**内容**:
- **现象**：手机端 FAB 悬浮球展开后，末尾「设置」按钮**挤出胶囊右缘、压在悬浮球上**
- **根因（CDP 实测）**：横条条目是 `flex-shrink: 0` 的固定 44px，容器只有 `max-width: calc(100vw - 82px)`（只限容器不限内容）→ **admin 多一个「管理后台」= 6 项时 `scrollW 314 > clientW 289`，右溢出 +34px**（360 时 +49px；320 下即使用户 5 项也 +37px）
- **修复**：`<nav>` 注入 `--nav-count`（条目数）→ `.nav-item` 宽度改 `clamp(32px, 可用宽/条目数, 44px)`（高度仍 44px 保触控目标）；≤344px 极窄屏换行成 3×2 圆角面板（条目回到 44×44）
- **验证**：375/360/320 × 6 项 **14/14 PASS**——`overflow=0`、末条目落在胶囊内、不压球（间隙 8px）、页面无横向滚动、320 自动换行（`rows=2`）；375 5 项与 1440 桌面形态均未误伤；双端截图肉眼复核、控制台 0 错误

**适用人群**: 前端开发者、测试

---

### 8.36 [opencode 模型上下文覆盖](./opencode模型上下文覆盖.md) ⚙️ 环境
**位置**: `docs/opencode模型上下文覆盖.md`

**内容**:
- **需求**：免费模型 `opencode/deepseek-v4.1-flash-free` 上下文抬到 **1M**（对齐付费/Go 版 `deepseek-v4.1-flash` 的 1,000,000）
- **改法**：全局配置 `~/.config/opencode/opencode.json` 顶层加 V2 原生 `providers.opencode.models."deepseek-v4.1-flash-free".limit = { context: 1000000, output: 32000 }`（旧 V1 `provider` 块不动，两键可共存）
- **两个坑**：① `limit` 是**整体替换**不是深合并，`output` 必须一起写；② 改完要 `POST /api/location/reload` 才即时生效
- **验证**：`opencode api get /api/model` 复查 → `1000000/32000`（改前 200000/32000）✅
- **风险**：只改客户端预算，免费档网关若仍按 200K 截断则超限直接报错；回滚 = 删 `providers` 块或恢复 `opencode.json.bak.20261016-142755`

**适用人群**: AI Agent、使用免费模型的开发者

---

### 8.37 [管理后台独立化](./管理后台独立化.md) ✨ 新增（架构改造）
**位置**: `docs/管理后台独立化.md`

**内容**:
- **需求**：管理员不能用普通用户的方式访问后台（原为 SPA 内 `/admin` 路由 + 前端 role 判断）；FloatingNav 几乎全局呼出（App.vue + 8 视图双实例，登录/404 等页也显示）
- **方案**：Vite 多入口 `admin.html` 独立控制台（独立登录页/独立壳/hash 路由/独立 `admin_token` 存储键）；三层隔离——①入口隔离 ②会话隔离（新列 `admin_session_id`，登后台不顶用户端，双端可同时在线）③接口隔离（`require_admin` 仅收 `scope=admin` 后台 token，用户端 token 一律 403）
- **用户端清理**：删 `/admin` 路由与 `AdminView`/`adminApi`；FloatingNav 白名单化（仅 5 主页 `meta.showNav`）、剥 7 视图重复挂载、删 admin 导航项与死代码 `hideNav`
- **演示站**：`admin.html` 进 gh-pages 构建（mock 登录 + 登录页演示链接）；**竞态修复**——mock 适配器改"挂载前 await 安装"（此前带旧 token 直达会泄漏真实请求并被 401 清会话）
- **验证**：后端隔离 9 断言全绿（用户端 token→后台接口 403 / 双端互不顶号 / 降权即刻失效）；type-check 0 错 + 双入口构建 ✓ + 真实构建无 demo 泄漏；CDP navscan 8/8（5 主页=1 实例、非主页=0）+ 全链路截图复核
- **二期规划（§10）**：内容管理——广场/灵感墙列表、下架/恢复/删除、`admin_audit_log` 审计、API 草案与 M2.1-M2.4 里程碑
- **v2.0（同日第二轮，用户三条反馈 → 全落地）**：①**风格对齐**——控制台直引用户端设计系统（`main.css` token/玻璃/弹窗 + `#theme-bg` 背景层复用 + 玻璃侧栏/卡片 + 去 AI 味）；②**浏览器式多页签**——点菜单开签/仪表盘固定首签不可关/关当前签跳右邻/刷新保持（sessionStorage）/keep-alive 每签状态缓存（关签即丢）；③**内容管理落地**——广场管理（筛选/详情弹窗/下架·恢复/**硬删除级联**（评论/附件/配图文件）/评论治理）+ 灵感墙管理（列表/查看/删除）；`idea_post.admin_removed` 防"平台下架后作者自行恢复"绕过；验证：后端回归 **28/28** + CDP 全流程 **14/14**（0 JS 错误）+ type-check 0 错 + 双构建；后端接口契约：[DixyangFast/docs/管理后台内容管理接口.md](../DixyangFast/docs/管理后台内容管理接口.md)

**适用人群**: 前后端开发者、测试、运维

---

## 现有文档（已存在）

### 9. [后端开发技术文档](./后端开发技术文档.md)
**位置**: `docs/后端开发技术文档.md`

**内容**:
- 详细的后端技术架构
- 数据库结构详解
- 开发流程示例
- RAG 系统配置与使用
- 缓存系统配置与使用
- 最佳实践
- 常见问题与解决方案

**适用人群**: 后端开发者、系统架构师

---

### 10. [RAG 离线构建流程](./RAG离线构建流程.md) ✨ 新增
**位置**: `docs/RAG离线构建流程.md`

**内容**:
- MD 文档如何被向量化存入 ChromaDB（离线构建完整流程）
- MarkdownLoader 切分逻辑（按标题 + chunk_size）
- EmbeddingModel 编码流程（bge-m3 → 1024维向量）
- VectorDB 存储结构（ChromaDB collection.add）
- Java 后端如何调用 ChromaDB 做 RAG 检索（RagService → Python Embedding → ChromaDB query）
- ChatController 如何将 RAG 结果注入 AI Prompt
- Python Embedding 服务 API 说明
- ChromaDB HTTP API 说明
- 端口速查和调用关系图
- 完整代码位置索引

**适用人群**: 所有开发者、需要理解 RAG 流程的人

---

### 13. [Git 上传规划与执行记录](./git上传规划.md) ✨ 新增
**位置**: `docs/git上传规划.md`

**内容**:
- 上传/不上传文件清单与 `.gitignore` 拦截项
- 误跟踪清理（93M 模型缓存、docx）与 lock 文件策略
- 提交记录、已知问题与验证命令

**适用人群**: 需要提交代码、维护 `.gitignore` 的开发者

---

### 14. [分支重建与版本对齐](./分支重建与版本对齐.md)
**位置**: `docs/分支重建与版本对齐.md`

**内容**:
- **2026-10-08 双分支结构重建（现行约定）**：`main`+`java` 双分支定义、18 个积压提交分四批入库并推送、16 个 `_probe-*.mjs` 探针清理、`java` 分支名 9/28 被改名丢失的根因与恢复步骤
- 本地/远程独立历史的对齐过程（非 Java 全用 GitHub 版本）
- `java` 分支创建与 `dixiyang-engine/` 恢复、`.gitignore` 调整
- 未跟踪文件的保留/删除判定清单
- 切分支时 Java 目录行为说明与验证命令

**适用人群**: 需要切换分支、提交推送、维护 `.gitignore`、恢复 Java 模块的开发者

---

### 15. [motion-web 技能接入](./motion-web技能接入.md) ✨ 新增
**位置**: `docs/motion-web技能接入.md`

**内容**:
- 动效网页 Agent Skill（`motion-web-main/`）接入 opencode 与 Trae 的方案
- 4 处软链入口（`~/.agents/skills`、`~/.trae-cn/skills`、项目 `.agents/skills`、`.trae/skills`）
- Windows 修复：symlink 被 checkout 成文本文件 → 改建 Junction（含根因 `core.symlinks=false` 与验证命令）
- AGENTS.md 索引兜底、已知问题（Trae 软链解析未实测）、验证命令

**适用人群**: 使用 opencode / Trae 做动效网页开发的成员

---

### 16. [对外介绍落地页](./落地页介绍页.md) ✨ 新增
**位置**: `docs/落地页介绍页.md`

**内容**:
- `/` 免登录落地页（SPA 首页）**v2 单屏切换版**：暖纸编辑部视觉、`100dvh` 单屏 + 左缘索引 tablist + 6 面板、抽稿换页签名转场
- 三层 token / 自托管字体 / matchMedia 动效门控 / reduced-motion 完成态兜底 / ≤768px 纵向流降级
- 路由守卫 `meta.public` 白名单、几何+动效验证记录、已知基线问题

**适用人群**: 前端开发者、设计/动效维护者

---

### 17. [LLM 接入配置切换](../DixyangFast/docs/LLM接入配置切换.md) ✨ 新增
**位置**: `DixyangFast/docs/LLM接入配置切换.md`

**内容**:
- 临时切换到本地 `llama-kvmem`（`Ternary-Bonsai-2-27B-PTQ1_0.gguf`，端口 18200）
- `.env` 三件套（`DEEPSEEK_API_KEY/BASE_URL/MODEL`）配置与注释保留方式
- `load_dotenv(override=True)` 修复：Machine 级系统环境变量覆盖导致 401
- 切回 DeepSeek 的步骤、前置依赖与验证命令
- 已知问题（`_llm_cache` 不含 model、`.env` 不触发 reload）

**适用人群**: 维护 Python 后端、切换 LLM 供应商的开发者

---

### 18. [motion-web 技能库出库与同步](./技能库出库与同步.md) ✨ 新增
**位置**: `docs/技能库出库与同步.md`

**内容**:
- 技能从 GitHub 删除但**本地保留**、且**协作者 pull 不丢文件**的方案（`git rm --cached` + `.githooks` 自动本地化）
- `pre-merge-commit`（真 merge）/ `post-merge`（fast-forward pull）双 hook 机制
- `scripts/setup-hooks.ps1` 一次性配置、`scripts/restore-skills.ps1` 兜底恢复
- 协作者操作步骤、已知限制（hooks 需配置一次、全新 clone 需另取技能）、验证命令

**适用人群**: 所有克隆/拉取本仓库的协作者、维护 `.gitignore` 与 hooks 的开发者

---

### 19. [卷章节与AI补全接口](../DixyangFast/docs/卷章节与AI补全接口.md) ✨ 新增
**位置**: `DixyangFast/docs/卷章节与AI补全接口.md`

**内容**:
- 卷 `/volumes` 6 端点、章节 `/chapters` 6 章节元数据端点 + 正文文件存储 4 端点（读/冲突检测/保存/版本历史）
- 正文**不入 MySQL**：写 `books/{novelId}/chapters/{chapterId}/content.json`，DB 只存 `__file__:` 引用；版本历史 `versions/v{n}.json`；删除连带清理
- 保存冲突协议：版本变化且 hash 不同 → `hasConflict=true`，`force=true` 才覆盖
- 全部端点强制 `user_id` 归属校验（11 项越权攻击用例全拦）
- AI 补全 `/ai/status`、`/ai/completion`：**真模型**——mock Provider 与独立 `AI_*` 配置已全部删除，复用 RAG 同款 `DEEPSEEK_*`（一处配置同切）、超时降级、请求体截断约定

**适用人群**: 后端开发者、前端 API 对接者

---

### 20. [静态主页部署](./静态主页部署.md) ✨ 新增
**位置**: `docs/静态主页部署.md`

**内容**:
- 公网地址：https://suziping123.github.io/Dixiyang/ （落地页即 SPA 首页；`404.html` 兜底深链）
- GitHub Actions 自动部署：push `main` → `vite build --base=/Dixiyang/`（仅 CI 注入）→ `deploy-pages`；Pages Source 已设 GitHub Actions
- 排障：CI build 失败根因 = 登录页背景视频 `卡比.mp4` 被 `.gitignore` `*.mp4` 忽略未提交，`git add -f` 修复；worktree 干净复现法定位
- **演示模式（批 1-4）**：11 个登录后页面全量可逛——构建隔离（仅 CI `--mode gh-pages` 注入 `VITE_DEMO=1`）、axios adapter 短路 + SSE fetch 打桩 + 守卫放行 + 假 JWT；实测真实构建产物无 demo 代码泄漏（摇树生效），本地 dev/生产零影响
- 已知问题：og 绝对 URL 待补、单 chunk 9.4 MB 待分包、mock 需与真实接口同步演进

**适用人群**: 运维、前端开发者

---

### 21. [Linux 部署指南](./Linux部署指南.md) ✨ 新增
**位置**: `docs/Linux部署指南.md`

**内容**:
- **Docker Compose 全栈一键部署**：MySQL 8 + Redis 7 + Python FastAPI + Nginx(Vue)，宿主机只开放 8080
- Kubuntu/Ubuntu 从零安装 Docker、免 sudo、国内镜像加速
- `scripts/deploy-linux.sh`：自动生成 `.env`/数据库密码/JWT、构建启动、健康等待、创建管理员 `admin123/123456`
- 手动部署等价步骤、局域网访问与防火墙、端口修改
- 升级（`git pull` + `docker compose up -d --build`）、备份/恢复（mysqldump + uploads 卷）、彻底重置
- 数据卷说明、RAG 可选服务、原生开发模式、Caddy HTTPS
- 常见问题：权限、端口占用、构建慢、DB_PASSWORD 改后连不上、502、管理员权限、AI 401、SSE 不流式

**适用人群**: 运维、部署者、新加入的开发者

---

## 文档使用指南

### 对于新加入的开发者

1. **首先阅读**: [系统总览](./系统总览.md) - 了解项目全貌
2. **然后根据角色选择**:
   - 后端开发者: [后端开发指南](../dixiyang-engine/AGENTS.md) → [后端接口文档](../dixiyang-engine/docs/后端接口文档.md)
   - 前端开发者: [前端开发指南](../dixiyang-vue/AGENTS.md) → [前端接口需求文档](../dixiyang-vue/docs/前端接口需求文档.md)
3. **深入了解**: [后端开发技术文档](./后端开发技术文档.md) - 深入技术细节

### 对于 API 对接

1. **查看对照分析**: [前后端接口对照分析](./前后端接口对照分析.md) - 了解接口完成状态
2. **前端视角**: [前端接口需求文档](../dixiyang-vue/docs/前端接口需求文档.md) - 了解需要什么接口
3. **后端视角**: [后端接口文档](../dixiyang-engine/docs/后端接口文档.md) - 了解已实现的接口

### 对于项目管理

1. **整体评估**: [系统总览](./系统总览.md)
2. **进度跟踪**: [前后端接口对照分析](./前后端接口对照分析.md)
3. **技术规划**: [后端开发技术文档](./后端开发技术文档.md)

---

## 文档维护

### 更新频率

- **系统总览**: 每月更新或重大变更时更新
- **接口文档**: 每次接口变更时立即更新
- **开发指南**: 每季度审查更新
- **对照分析**: 每周更新（开发期间）

### 维护责任人

- **后端文档**: 后端开发团队
- **前端文档**: 前端开发团队
- **总体文档**: 技术负责人

### 文档规范

1. 使用 Markdown 格式
2. 包含版本号和最后更新时间
3. 提供清晰的目录结构
4. 包含代码示例时使用语法高亮
5. 重要信息使用加粗或引用块突出显示

---

## 快速导航

### 按功能模块

- **认证模块**: 
  - [后端接口文档 - 认证相关](../dixiyang-engine/docs/后端接口文档.md#认证相关接口)
  - [前端接口需求 - 认证相关](../dixiyang-vue/docs/前端接口需求文档.md#认证相关接口)

- **小说管理**: 
  - [后端接口文档 - 小说管理](../dixiyang-engine/docs/后端接口文档.md#小说管理接口)
  - [前端接口需求 - 小说管理](../dixiyang-vue/docs/前端接口需求文档.md#小说管理接口)

- **角色管理**: 
  - [后端接口文档 - 角色管理](../dixiyang-engine/docs/后端接口文档.md#角色管理接口)
  - [前端接口需求 - 角色管理](../dixiyang-vue/docs/前端接口需求文档.md#角色管理接口)

- **RAG 系统**: 
  - [RAG 离线构建流程](./RAG离线构建流程.md) ← 完整流程说明
  - [后端开发技术文档 - RAG 系统](./后端开发技术文档.md#rag-系统配置与使用)
  - [后端接口文档 - RAG 聊天](../dixiyang-engine/docs/后端接口文档.md#rag-聊天接口)

### 按技术主题

- **数据库**: [后端开发技术文档 - 数据库结构](./后端开发技术文档.md#数据库结构)
- **缓存**: [后端开发技术文档 - 缓存系统](./后端开发技术文档.md#缓存系统配置与使用)
- **安全**: [后端开发技术文档 - 安全最佳实践](./后端开发技术文档.md#安全最佳实践)
- **部署**: [后端开发指南 - 部署说明](../dixiyang-engine/AGENTS.md#部署说明)

---

## 反馈与建议

如果您发现文档中有错误、遗漏或需要改进的地方，请：

1. 在项目 Issue 中提交问题
2. 直接修改文档并提交 Pull Request
3. 联系文档维护责任人

---

## 版本变更记录

### v1.70 (2026-10-19)
- **清理**: [项目清理记录](项目清理记录.md) v1.1 批次4 — 删除根目录 `Temp/` 旧调试脚本 9 个（2026-10-13~14 一次性排查脚本，未跟踪）+ Obsidian 空 `未命名.base`；`.gitignore` 增加 `/Temp/` 防复发；同批提交 `docs/JobInterviews/.obsidian/workspace.json` 工作区状态

### v1.69 (2026-10-19)
- **新增**: [Linux 部署指南](Linux部署指南.md) — 用户要求「GitHub 下载后按说明书快速部署到另一台 Kubuntu 电脑」：① 新增 `docker-compose.yml` 四服务编排（MySQL 8 + Redis 7 + FastAPI + Nginx/Vue），仅对外暴露 8080，DB/Redis 不映射端口；② 新增 `deploy/backend.Dockerfile`（python:3.11-slim + uv sync --frozen + 非 root）、`deploy/frontend.Dockerfile`（node:22-alpine 构建 + nginx:1.27-alpine 托管）、`deploy/nginx.conf`（SPA 兜底、`/api` 反代、**SSE 关闭缓冲**、50m 上传）、`.dockerignore`（排除 .venv/node_modules/模型/上传数据）；③ 新增 `scripts/deploy-linux.sh` 一键脚本（自动生成随机 DB 密码/JWT、交互填 DeepSeek Key、构建启动、180s 健康等待、幂等创建管理员）；④ 新增 `DixyangFast/src/dixiyang/seed_admin.py`（支持 `--reset-password` 与风控解锁）；⑤ **依赖修复**：`pyproject.toml` 补 `pymysql/redis/python-dotenv/langchain-chroma/chromadb` 等运行时缺项（旧版全新机器 `uv sync` 后启动必失败），`DixyangFast/uv.lock` 纳入版本管理；⑥ `.env.example` 修正 SMTP 变量名并补部署参数；⑦ 新增 `start_backend.sh`；⑧ 旧文档纠偏：[Linux_Docker安装指南](Linux_Docker安装指南.md) 删除 Qdrant/Java 误导步骤、[Linux迁移指南](Linux迁移指南.md) 重写为 RAG 数据迁移；README 顶部新增「克隆后快速部署」。验证：Compose config ✓、前端生产构建 ✓、锁文件一致性 ✓（完整镜像构建受网络下载耗时限制未在本机跑完）

### v1.68 (2026-10-18)
- **修复**: [管理后台独立化](管理后台独立化.md) v2.1.2 — 用户例证"条形图超出屏幕、页签无滚动条"（准则12「实际→剪裁→展示」触发案例）：① grid 子项 `min-width:0` + 卡片 `overflow:hidden`——画布 min-content 把 375 视口**撑到 492 溢出屏幕**；② `EChart` `window.resize`→**ResizeObserver**（缩窄/页签往返画布回位，旧版卡旧宽度自锁）；③ 页签 `scrollbar-width:thin` 细滚动条不再隐藏；④ 滚轮纵向→横向映射（仅溢出时拦截）。验证 **10/10 PASS + 0 JS 错误**（375 最坏场景回放：视口不被撑宽 / 图表 `canvas≤box≤card≤视口` / 屏幕级溢出走查 0 / 滚轮可滚）+ 双端截图复核 + type-check 0 错 + 双构建 ✓

### v1.67 (2026-10-18)
- **修复+修订**: [管理后台独立化](管理后台独立化.md) v2.1 修订 — 用户复查指出"悬浮球直接复用控制台菜单的路径+图标，且图标语义错误（单个人/单本书）"：① `ADMIN_NAV_ITEMS` 改为**独立注册**（不再 `CONSOLE_PAGES.map` 派生，顺序/图标按移动端语义单独维护）② 新增自绘图标 `src/admin/icons.ts` 补 EP 库存缺口——**多个人**（用户管理，2 圆 2 径）、**多本书**（灵感墙管理，书架 4 矩形），广场管理换社区语义 `ChatDotSquare`，与用户端导航图标彻底区分 ③ 侧栏/页签图标同步换新（`CONSOLE_PAGES`）④ 验证：图标断言 **6/6 PASS + 0 JS 错误**（FAB 6 项标签 + 图形结构断言 + 侧栏/页签图标渲染）+ 双端截图肉眼复核 + type-check 0 错 + 双构建 ✓

### v1.66 (2026-10-18)
- **更新+实施**: [管理后台独立化](管理后台独立化.md) **v2.1** — 移动端复用悬浮球导航（用户反馈"admin 移动端适配不太行，可复用 floatingnav，注册项要换"）：① `FloatingNav` **注册项化**（新增 `items` prop + `FloatingNavItem` 类型：`icon/label/path/href/danger/key`；**不传 = 用户端默认 5 主页**，App.vue 零改动；新增 `href` 整页跳转 / `danger` 危险样式 / `select` 事件 / `navLabel` 无障碍标签）② 控制台窄屏/触屏（≤1024px 或触屏）**侧栏撤下**、导航交给悬浮球（`ADMIN_NAV_ITEMS` = 4 控制台页面 + 返回用户端 + 退出登录），桌面宽屏不挂载 ③ 内容区 `padding-right: 64px` 右侧避让悬浮球 + 页签关闭钮触控命中区放大 ④ 废弃"侧栏折顶栏"旧方案（改造前取证：顶栏仅 1/4 菜单可见）。验证：CDP 全流程 **18/18 PASS + 0 JS 错误**（移动端 13 + 用户端回归 3 + 桌面回归 2）、type-check 0 错、真实构建无 demo 泄漏 + gh-pages 双入口 ✓、截图肉眼复核

### v1.65 (2026-10-18)
- **更新+实施**: [管理后台独立化](管理后台独立化.md) **v2.0** — 用户反馈三条（"风格没对齐我的风格、文档没看、不像真实后台缺浏览器式多页签"）全落地：① 控制台**接入用户端设计系统**（直引 `main.css` token/玻璃/全局弹窗；复用 `#theme-bg` 背景层读同源缓存、自定义背景 URL 可用；玻璃侧栏/页签条/卡片；大数字锚点+计数动画；登录页去紫蓝径向光）；② **浏览器式多页签**（`menu.ts` 注册表 + `useAdminTabs` 状态机：开签/激活复用/固定首签不可关/关签跳右邻/sessionStorage 刷新保持/keep-alive 每签独立状态、关签即丢缓存）；③ **内容管理常规运营档**（广场：筛选/详情弹窗（正文/配图/附件/评论治理）/下架·恢复/**硬删除级联**（评论/点赞/收藏/标签行 + 正文/附件/本地上传配图文件）；灵感墙：筛选/列表/查看/删除；**平台下架 `admin_removed=1` 且作者恢复被拦截**）。验证：后端回归 **28/28 PASS**（真登录、测试账号用后还原）、CDP 全流程 **14/14 PASS + 0 JS 错误**（含状态缓存/邻签/刷新保持断言）+ 截图肉眼复核、type-check 0 错、真实构建无 demo 泄漏 + gh-pages 双入口；后端接口契约新增 [DixyangFast/docs/管理后台内容管理接口.md](../DixyangFast/docs/管理后台内容管理接口.md)（8 端点 + 级联规则）

### v1.64 (2026-10-18)
- **新增+改造**: [管理后台独立化](管理后台独立化.md) — 用户两条诉求（"管理员不能用普通用户的方式访问后台，现在集成在里面" + "FloatingNav 几乎全局呼出不正确"）落地：Vite 多入口 `admin.html` 独立控制台（独立登录页/hash 路由/独立 `admin_token` 键/console.css 自包含）+ **三层隔离**（入口：用户端删 `/admin` 路由与全部后台代码；会话：新列 `admin_session_id`——登后台不顶用户端、双端可同时在线；接口：`require_admin` 仅收 `scope=admin` 后台 token，用户端 token 一律 403）+ 用户端 FloatingNav 白名单化（仅 5 主页、修双实例挂载、删 admin 导航项与死代码 `hideNav`）+ 演示站接线（admin.html 进 gh-pages、mock 登录、登录页演示链接；mock 适配器改"挂载前 await 安装"修旧 token 直达竞态）。**验证**：后端隔离 9 断言全绿（用户token→后台 403/双端互不顶号/降权即刻失效/非管理员拒登）、type-check 0 错、双入口构建 ✓ 真实构建无 demo 泄漏、CDP navscan 8/8 + 全链路截图；二次规划（内容管理）见文档 §10

### v1.63 (2026-10-16)
- **新增**: [背景图端适配分类](../dixiyang-vue/docs/背景图端适配分类.md) v1.1 — 用户要求「把分类做成页面功能」，两问定形后落地（**选择器按当前端排序 + 「电脑/手机」角标**，单网格不撑高）：新增纯函数 `src/utils/bgFit.ts`（宽高比 + 清晰度门槛，4 个常量可调：竖图 A≤0.8 且长边≥750 → 手机；横图 A≥1.6 且长边≥1920 → 电脑，不够 1920 降级通用）、`BgImageGrid` 缩略图 `@load` 读原始尺寸 → 当前端组置顶 + 左上角标 + `title` 解释（**零额外请求**，功能卡仍钉末尾）、单测 `bgFit.spec.ts` 10 例；CDP 实测真实账号 375 竖屏「手机优先」置顶 / 1440 横屏顺序反转 / 角标 5+1 / 点选不受影响 / 浮层不超屏，`vue-tsc` 0 错 + eslint 0 错
- **修复**: [FloatingNav手机端溢出修复](../dixiyang-vue/docs/FloatingNav手机端溢出修复.md) — 用户报「手机端 settings 按钮溢出」：CDP 实测根因 = FAB 横条条目 `flex-shrink:0` 固定 44px + 容器只有 `max-width`（只限容器不限内容）→ **admin 6 项时 `scrollW 314 > clientW 289`、右溢出 34px 压在悬浮球上**（360 时 +49px、320 下 5 项即 +37px）；修复 = `<nav>` 注入 `--nav-count` + 条目宽 `clamp(32px, 可用宽/条目数, 44px)`（高度仍 44px）+ ≤344px 换行 3×2 面板；375/360/320 × 6 项 **14/14 PASS**（`overflow=0`、不压球、无横向滚动、320 自动换行）、375 5 项与 1440 桌面未误伤、双端截图复核

### v1.63 (2026-10-16)
- **新增**: [opencode 模型上下文覆盖](opencode模型上下文覆盖.md) — 用户要求「把免费的 DeepSeek V4.1 Flash Free 上下文弄成 Go 一样，1M」：全局配置 `~/.config/opencode/opencode.json` 顶层新增 V2 原生 `providers.opencode.models."deepseek-v4.1-flash-free".limit = { context: 1000000, output: 32000 }`（目录原值 200000/32000，付费版 1000000/384000）；两个坑记录在案（`limit` 整体替换非深合并 → `output` 必须一起写；改完需 `POST /api/location/reload`）；验证 `opencode api get /api/model` → **1000000/32000** ✅；风险：只改客户端预算/自动压缩触发点，免费档网关若仍按 200K 截断则超限直接报错（免费端点对非 opencode 客户端返回 `403 FreeTierError`，无法脚本探针），回滚 = 删 `providers` 块或恢复 `opencode.json.bak.20261016-142755`

### v1.62 (2026-10-16)
- **新增**: [开发环境与测试账号](开发环境与测试账号.md) — 用户拍板「以后用账号登录」：本地验证统一用测试账号 `admin123/123456` 真实登录（`POST /api/auth/login` → 六键写 localStorage），**禁止伪造 token**；同步写入 `AGENTS.md` 第 12 条（全局规则）与 [JobInterviews/Practical/08-排错方法论.md](JobInterviews/Practical/08-排错方法论.md) 探针前置步骤；按新规范用真实账号复验 [Home背景浮层移动端滚动修复](../dixiyang-vue/docs/Home背景浮层移动端滚动修复.md)（§5.1：375×667 `panel 0→90` 且 `window.scrollY` 恒 0、尾部卡可达、滚后可选、812/1440 不超屏、0 控制台错误），探针改动的背景已复原并核对服务端一致、探针标签已关闭
- **新增**: [背景图端适配分类](../dixiyang-vue/docs/背景图端适配分类.md) — 22 张图（上传背景 11 / 上传封面 4 / 内置背景 7）按 `center/cover` 裁剪数学逐张判定端适配：桌面优先 10、通用 3、移动优先 5、封面另判 4；给出选图规则（两端通用 3:2~16:10 主体居中、手机 9:16~9:20、桌面 16:9 起、封面 2:3）与三个可选功能方案（`fit` 标签 / 双端两套背景 / 上传提示）

### v1.61 (2026-10-16)
- **修复**: [Home背景浮层移动端滚动修复](../dixiyang-vue/docs/Home背景浮层移动端滚动修复.md) — 用户报「手机选背景的小页面滑不动、只能滑底层」：CDP 取证根因 = 浮层高度随卡片数**无上限**（21 张实测 1161px，超视口 504px）+ `overflow-y:visible` 本身不可滚 + EP `teleported=false` 把它锚在 **sticky 顶栏**内（滚页面不露出来）→ 手势被浏览器交给文档滚动；修复 = `.bg-compact-popper` 限高（桌面 `min(68vh,640px)`、移动 `min(70dvh, calc(100dvh - 190px))`）+ `.compact-panel` 内滚 + `overscroll-behavior:contain`（边界不传染底层）+ `max-width:calc(100vw-24px)`；仅 CSS、不动模板；CDP 真实触摸移动端 **8/8** + 桌面 **3/3** PASS（浮层内上滑 `panel 0→385`、`window.scrollY` 恒 0，修复前 0→186）、控制台 0 错误、双端截图复核

### v1.60 (2026-10-14)
- **新增**: [静态主页部署](静态主页部署.md) §演示模式 批 1-4 — GitHub Pages 静态站 11 个登录后页面全量可逛（登录/编辑器/角色/时间线/RAG 助手+知识库/点子库/灵感墙/设置/管理后台）：`src/utils/demo/`（adapter 短路 + SSE fetch 打桩 + 假 JWT + 守卫放行），**构建隔离**——仅 CI `--mode gh-pages` 注入 `VITE_DEMO=1`，实测真实构建产物无 demo 代码泄漏、本地 dev/生产行为零影响；每批 type-check 0 错 + build ✓ 后自动发布

### v1.59 (2026-10-14)
- **部署**: [静态主页部署](静态主页部署.md) — 落地页公网上线 GitHub Pages：**https://suziping123.github.io/Dixiyang/**。新增 `.github/workflows/deploy-pages.yml`（push main 自动 build `--base=/Dixiyang/` + `404.html` SPA 兜底 + deploy-pages 发布）；排障 CI build 失败 = `卡比.mp4`（32.4MB）被 `.gitignore` `*.mp4` 忽略未入库，`git add -f` 修复（用户拍板入库）；验证公网 200 三连（首页/资产/深链 fallback）+ workflow build/deploy 全绿

### v1.58 (2026-10-13)
- **调查+修复**: [灵感墙便利贴实施记录](灵感墙便利贴实施记录.md) §10 — ① 调查"便签没保存/显示/查询"：功能与数据实测**全通**（DB 2 行 ↔ 磁盘 2 文件 0 缺失），真因 = 10/11 `done` 缺列历史 500 + `stickyStore` 失败 `catch{}` 静默 + 看错目录（实为 `uploads/storage/sticky/`）；② 补上**确实缺失的定期清理**：新增 `sticky_cleanup.py`（每日+启动即跑，删孤儿 json 与空用户目录，DB 失败只做空目录防误删），`main.py` lifespan 注册，实跑清掉 10 个空目录 0 误删；③ 完成态交互：点正文=划掉 → 纸面右上**勾选圆钮（灰空心圈→黑底白勾）**，正文改回选中/置顶，空便签点勾给提示。验证：后端 import OK + sweep PASS + type-check 0 错

### v1.57 (2026-10-13)
- **新增**: [RAG聊天导出菜单](RAG聊天导出菜单.md) — RAG 助手消息「总结为设定」单按钮扩展为**导出▾下拉菜单**（手绘 SVG 图标）：复制文本 / 存为便签（`stickyStore.create` 直落库）/ 总结为设定（原流程不变）/ **转发到广场**（新组件 `ForwardToPlazaDialog`：AI 生成候选标题+标签一键应用、分区默认 setting、存草稿 / 立即发布双按钮）。后端新增 `POST /idea/aiSuggest`（`call_llm` + JSON 清理，照抄 extractSettings 套路）。验证：type-check 0 错 + ESLint 三文件 0 错 + build EXIT=0 + 后端 ast 语法 OK

### v1.56 (2026-10-12)
- **修复**: [前端type-check存量错误清零](前端type-check存量错误清零.md) — `npm run build` 恢复绿灯（EXIT=0），type-check **9 错 → 0 错**。9 处均为类型层告警（`noUncheckedIndexedAccess` 索引 undefined / DeepReadonly 数组赋 mutable prop），运行时均有保护：`localImages` `??` 收敛、`storyMappings` 去 `Record` 标注改字面量推断、`ChatMessage` 数组 prop 放宽 `readonly T[]`（组件内只读）、`TimelineView` `[0]?.id ?? null`。README 删除「用 build-only 绕过」说明与对应 FAQ。验证：type-check 0 错 + build EXIT=0 + ESLint 与 HEAD 基线对比零引入

### v1.55 (2026-10-12)
- **修复+整理**: [灵感墙便利贴实施记录](灵感墙便利贴实施记录.md) §9 四轮审查 — 修 3 Bug（① 拖拽松手补发 `click` 误触发 `toggleDone` 划掉内容 → `suppressClick` 抑制；② `moved` 不重置致单击误走拖拽保存逻辑、便签悬池口单击误投喂 → `onPointerDown` 重置；③ 编辑态 `z-index:1000 !important` 压掉 `bringToFront` 置顶 → 删规则）；死代码清理（`toolbarVisible` 类补绑激活、删 `Plus` import、删拖拽手柄残留注释、`will-change` 无效 left/top 收敛、拖拽 z-index 20 亿魔数改 210000）；`PoolWindow` 120ms body class 轮询改 `stickyStore.dragging` 状态直连；取回文案区分钉住态。验证：type-check 9 错基线不破 + vite build ✓ + eslint 0 错

### v1.54 (2026-10-12)
- **重写**: 根目录 [README.md](../README.md) 全面重写（新人克隆即可跑）— 修正三大致命缺口：① 新增「克隆后必做」：Git Hooks（`scripts/setup-hooks.ps1`，防 pull 删除本地技能文件）+ `.env` 创建（`cp .env.example .env`，4 项必填：DB_PASSWORD/DATABASE_URL/JWT_SECRET_KEY/DEEPSEEK_API_KEY）；② 架构勘误：**当前主后端是 Python FastAPI（DixyangFast/src/dixiyang/main.py，8084，`start_backend.bat` 一键，启动自动 create_all 建表）**，旧版 README 误写 Java 为主后端——dixiyang-engine 降级为"备用、与 Python 同端口二选一、不读 .env 只认系统环境变量"；③ 环境要求修正：Node 从 18+ 改为 package.json engines 实际要求（^20.19||≥22.12）；新增 Redis 可选章节（广场推荐缓存，未起自动降级）、前端打包已知问题（`npm run build` 含 type-check 存量错误 → 用 `build-only`）、FAQ 更新（8084 冲突/hooks/build 报错/Redis 降级）、文档导航改为真实存在链接（删除失效的 项目总体情况总结/向量库可视化指南）

### v1.53 (2026-10-10)
- **更新**: [移动端浮动导航防遮挡](../dixiyang-vue/docs/移动端浮动导航防遮挡.md) v1.2 — 宽屏桌面 FloatingNav「范围太大」修复：`.nav-wrapper` 100px×全高热区 `pointer-events:none` 穿透（不再挡页面左侧点击），`.nav-trigger` 接管 hover 且 30→16px 收窄误触，展开面板单独恢复可点（FAB 模式覆写不受影响）；CDP 冒烟 18/18 PASS、type-check 9 / eslint 0 基线不破；**新发现**：FloatingNav 双实例挂载（本次灵感墙改动在 `App.vue` 加全局挂载未删 8 个 view 旧挂载，渲染 2 套空转），待用户决定清理

### v1.52 (2026-10-10)
- **新增**: [广场真瀑布流与增量加载](./广场真瀑布流与无限滚动.md) — 广场 Tab 手写短列优先真瀑布流（替换 CSS multi-column 伪瀑布流，无第三方依赖）+ IntersectionObserver 无限滚动触底追加（删除页码器，新增"已经到底啦"终止态）；后端 `/idea/posts` 游标分页（`new/like/hot` 元组/ZSET 名次游标翻页不 COUNT 全表，`recommend` 保留页码）；仅改广场 Tab，草稿/我发布的/收藏保留页码器；后端游标专项 16/16 + CDP 冒烟 16/16 + 基线 9/2 不破

### v1.51 (2026-10-10)
- **新增**: [Redis优化效果对比](./Redis优化效果对比.md) + [ECharts接入(并入管理后台M1文档)](./管理后台M1.md) — ECharts 按需引入+暗色主题封装 `EChart.vue`；管理后台发帖趋势柱图&分区环图；RAG 三图重构为横向条形图；JMeter 压测（零思考时间、每态 3 轮×6000 预热后取样、0 错误）：**P95 368ms vs 1844ms（5×）**、吞吐中位 67.6 vs 39.6 req/s（+71%）、命中率 99.99%、降级 0 错误；文档含环境/数据规模/边界诚实声明（SQLite 放大效应、非容量测试、未做阶梯加压）

### v1.50 (2026-10-09)
- **新增**: [管理后台M1](./管理后台M1.md) + [综合推荐算法升级(并入广场综合推荐与Redis接入)](./广场综合推荐与Redis接入.md) — 后端：`app_user.role` 列(启动自动 ALTER)+`require_admin`+`/api/admin/stats|users|role`；前端 `/admin` AdminView(统计卡/分区chips/用户表格改角色)；综合推荐改为 Redis热度×时间衰减+点藏标签兴趣加成(近似ItemCF)，与最新/热门拉开区分度；uvicorn reload 默认关闭(Windows 启动 30s→2s)

### v1.49 (2026-10-09)
- **新增**: [广场综合推荐与Redis接入](./广场综合推荐与Redis接入.md) — 「点子库」更名「广场」（页面/导航/路由 title）；排序新增「综合推荐」为默认（后端 `sort in ("hot","recommend")` 走 Redis ZSET 热门榜优先路径）；Redis P0/P1 接入：`idea_cache.py` 新封装（频控 TTL/热门 ZSET 镜像+10min 重建/浏览 SETNX 600s 去重+60s Lua 原子回写 DB/3s 冷却降级回原路径），`main.py` lifespan 挂后台任务，连接串走环境变量 `REDIS_URL`（密码不入库，redis-py 强制 `protocol=2`）；局域网 host:true + adb auto-reverse + launch.json 三启动项（launch 传 `--host` 被 npm 吞参致全黑的坑）

### v1.48 (2026-10-09)
- **新增**: [局域网访问与launch调试](./局域网访问与launch调试.md) — `vite.config.ts host:true` + `.vscode/launch.json` 三启动项（Vite/debugpy/compound），网线 Linux 与 USB 共享安卓可访问 `http://10.24.142.24:5173`；含 launch 追加 `--host` 被 npm 吞参致页面全黑的踩坑与防火墙放行命令

### v1.47 (2026-10-09)
- **点子库第四轮**: [点子库Demo实施记录](./点子库Demo实施记录.md) 升级 **v1.3** — 用户两条反馈：① **下架编辑下拉没复用写点子/回显不了** → 抽共享组件 `SourcePicker.vue`（小说→角色/对话级联 + `echo()` 回显反查 + `records` 分页口径修正，两弹窗各删 ~90 行本地实现）+ PostEditDialog `:destroy-on-close`（`@open=init` 切帖不重跑的串数据隐患）+ `ensureReady()` 懒加载/失败重试（DraftEditor `v-if=modelValue` 弹窗可见才挂，页面加载不再发请求、未登录不炸 console）；后端 `sourceRef` 改来源首次全量验证（**新增 `test_idea_api_source.py` 25/25**：改源重建/无效角色·会话报错整体回滚/清空移除/空→再选恢复/tech 无害）；② **配图拖拽调顺序** → 手写零依赖 `useImageDragSort.ts`（Pointer Events、6px 阈值、pointer capture、拖影+drop 高亮、松手 move 语义、`touch-action:none` 触屏可用、首张封面），`PostEditDialog`/`DraftEditorDialog` 双接入（拖后 resetPreview）。验证：source **25/25** + round1 40/40 + round2 15/15 + round3 19/19 + SMOKE3 **28/28**（0 控制台错误）+ SMOKE2 PASS + `_smoke_ideas` PASS + 拖拽 **8/8** + 回显 **9/9**（idea/character CDP 实测）+ type-check/eslint/build ✓；踩坑 `getNovelOptions` 返回 `{records:[...]}`（非数组）写入根 AGENTS「前端三大必读」

### v1.46 (2026-10-09)
- **点子库第三轮**: [点子库Demo实施记录](./点子库Demo实施记录.md) 升级 **v1.2** + 新增 [Redis与管理后台策划](./Redis与管理后台策划.md) — 用户 9 条反馈：① **emoji 图标 AI 味** → 自绘线性 SVG `IdeaIcon.vue`（eye/heart/bubble/star/clip/edit/share）替换全站 👁👍💬⭐❤📎；② **赞/藏无动画** → `stat-bump`/`act-bump` keyframes + `:active` 缩放 + 实心填色；③ **卡脚快捷互动** → `.stat-btn` 乐观更新+回滚 + 后端 `_collected_set` 下发 `collectedByMe`（5 调用点）；④ **移动端** → 768 断点（FAB 避让/双列 150/chip 横滑）+ 横向溢出根因（`.filter-row` 内 `flex-shrink:0` 撑 572px→实测复原 375）；**④-b 真机观感补丁**（用户"没有任何适配"：断言绿但真机=单列大卡+Tab截断）→ 避让 88→64（球46+边14+缓冲4 精算，内容 297 双列 minmax 140）、tab-btn 收紧、筛选改 chips/排序**分组独占行组内横滑**（排序不再被挤出首屏），冒烟增补双列/Tab全见断言 **28/28** + 375 截图肉眼复核；⑤ **卡片融合** → `.idea-page`/`.detail-body` 作用域 `--surface-card:#171a24` 实底；⑥ **模糊蒙板根因** → 全局 `input{backdrop-filter:blur(10px)}`+控件 5% 半透明，修 `html .el-dialog` 控件实底 `#191c27 !important`+去 blur、`.el-overlay` 加深 0.62；**⑥-b 下拉复燃**（filterable select 原生 `input.el-select__input` 聚焦展开命中全局 blur → 白雾、失焦消失）→ 补 `html .el-dialog input,textarea,select` 通配去 blur + 页面级同治，CDP 实测 focus `backdropFilter:none`、两大坑总结写入根 `AGENTS.md`「前端两大高频坑」；⑦ **详情图置顶** → 画廊移到 tags 后；⑧ **下架为修改服务** → 新建 `PostEditDialog.vue` 双入口（详情操作栏+我发布的 edit-entry）+ `updatePost` API + 附带修 toggle 悬空收藏无法取消 bug（取消允许 removed、新增限 published）；⑨ **Redis+管理后台** → 出策划不写码（`Redis与管理后台策划.md` v1.0：idea_cache 封装/迁移分期 + role/require_admin/四页面/M1-M5）。验证：round3 **19/19** + round1 **40/40** + round2 **15/15** + 冒烟 **26/26**（0 控制台错误）+ 基线 type-check 9/lint 8/build ✓

### v1.45 (2026-10-09)
- **点子库第二轮**: [点子库Demo实施记录](./点子库Demo实施记录.md) 升级 **v1.1** + [点子库与创意社区策划](./点子库与创意社区策划.md) 升级 **v1.2** — 用户实测 5 问题修复与增强：① **EP 浮层白底蒙版**（`main.css` 错误选择器 `.el-option` → 重写 `.el-select__popper/.el-popper/.el-select-dropdown` 全局深色 `#222530`）；② **"会话不存在或已删除"**（`idea_export` 链目录漏 `chat` 段 + 前端切分区未清 sourceRef 双根因）；③ **失败也扣频控额度**（`_limited` 拆 `_limit_check`/`_limit_mark` 成功才打点、文案带剩余秒数 + 弹窗 inline 红色错误条双保险）；④ **配图全链路**（新表 `idea_post_image` 免 ALTER + `POST /upload/idea-image` MD5 去重 + 草稿 images 白名单清洗 + 列表 `images/coverUrl` + 编辑器 9 图网格首图封面 + 详情 `el-image` 画廊）；⑤ **小红书瀑布流**（CSS multi-column、3:4 封面卡、头像+❤卡脚）；⑥ **来源对话两级级联**（先选小说再选对话，`sessions?novelId=` 过滤）。验证：第二轮 API **15/15 PASS**（失败不扣额度/真实会话快照 messages=6/频控文案/图片流）+ 既有 **40/40 回归** + 基线 9/8/build ✓ + CDP 冒烟 **SMOKE2 PASS ×2**（popper bg=rgb(34,37,48)、级联、切分区清来源、错误条、0 控制台错误）+ 截图留证

### v1.44 (2026-10-08)
- **新增**: [点子库Demo实施记录](./点子库Demo实施记录.md) — 点子库 Demo 全链路完成：后端 `models/idea.py`（7 表）+ `idea_service/idea_export/routers/idea.py` + 可选鉴权 `get_optional_user_id`，API 全链路测试 **40/40 PASS**（草稿→预览拦截→发布→分区/搜索/标签/排序→浏览+1→点赞收藏→评论频控→下架恢复→角色卡附件→导入同名后缀/越权/频控→发帖频控）；前端 `ideaApi.ts` + `IdeaLibraryView`（广场/草稿/我的/收藏四 Tab）+ `DraftEditorDialog`（保存→预览→发布三步流）+ `PostDetailDialog`（附件/导入/互动/评论）+ `/ideas` 路由 + FloatingNav 入口；**先查文档一次性修 8 坑**（背景层叠 `position:relative` 致命坑、`userId` key、chat 分区误设、FloatingNav 漏挂、enterSubmit 约定、payload 笔误、列表串数据、`post.value&&` lint）；验证 type-check 9 / lint 8 基线、build ✓、CDP 冒烟 SMOKE PASS×2；README 登记 8.27

### v1.43 (2026-10-08)
- **策划扩展**: [点子库与创意社区策划](./点子库与创意社区策划.md) 升级 **v1.1** — 用户四项决策落地：① **五分区**（点子/角色/设定/时间线/技术，`idea_post.category`）+ **四类结构化附件**（`idea_attachment` 多态表替代单 snapshot_path；对话/角色/设定/时间线从现有表导出只读快照）+ **角色附件一键导入到我的小说**（复制行+extra、vector_id 置空，频控 10s）；② 数据库补强：时间统一 `create_time`（对齐全库/Java 惯例）、标签改 `idea_post_tag` 关联表、评论 `Text`、组合索引、`app_user` 加可空 `avatar_url`/`pen_name`；③ §8 功能路线图：ChromaDB（非 Qdrant）`idea_posts` 相似推荐、设定/时间线导入、投票征集、存入知识库等二期候选 + 同类产品调研依据（SillyTavern/DZMM/造物纪/饼次元/LitMemo/云作者）；④ Java 双栈保留、稳健版清理等决策同步落实（见 v1.42）

### v1.42 (2026-10-08)
- **清理**: [项目清理记录](./项目清理记录.md) — 稳健版项目清理两批次：① 代码批次 `aebe648`（-459 行）删 `colorUtils.ts`、assets 6 大图+2 logo（约14MB）、空文件、`md2docx.py`、Python 4 个死函数、Java 2 个零端点空 Controller，修 `NovelController` delete 路由缺斜杠（原 `/noveldelete` 不可达）；② 归档与文档批次：daily-log 一代原型 34 文件出库（`.gitignore`+`--cached`，本地保留）、docs README **12 条断链全修复（41/41）**、`功能完成状态.md`/`前后端接口对照分析.md`/双端 `AGENTS.md` 加勘误修正过期结论（NovelEditorView 已为完整编辑器、4 个 Controller 非空、9 个不存在文件移出目录树）；验证 type-check 9/lint 8 基线、py_compile、grep 零引用、链接校验 broken=0；README 登记 8.26

### v1.41 (2026-10-08)
- **新增**: [点子库与创意社区策划](./点子库与创意社区策划.md) — 新功能策划文档（本轮仅策划不写码）：私有草稿+社区发布双空间、对话只读快照（发布时复制链、预览强制确认、原对话删除不影响）、点赞/评论/收藏/标签/热门排序（用户确认全部纳入 MVP）；技术方案 Python FastAPI + MySQL 5 表 + Redis（计数/热门 ZSET/频控/降级回 DB，前置需装 redis-py）；含 API 契约、前端组件清单、P0-P3 里程碑、测试计划、风险表；README 登记 8.25

### v1.40 (2026-10-08)
- **删除**: RAG 助手页顶栏 — 需求"page-header 太麻烦，直接删掉"→ `RagAssistantView.vue` 删除顶部 `<header class="page-header">`（"RAG 智能创作助手"标题+副标题）及配套样式（`.page-header`/`.header-content`/`.page-title`/`.page-subtitle`、移动端媒体查询项），`.rag-container` 高度预算 `100vh-120px → 100vh-40px`（原 120px 为页眉预留）；聊天区直接满屏；type-check 9/lint 8 基线、build ✓、`page-header` 相关标识 0 残留

### v1.39 (2026-10-08)
- **修复**: [RAG消息版本交互与接口规范](./RAG消息版本交互与接口规范.md) 第十轮 — 反馈"现在都是流式了，为什么暂停不能停在流式状态？没加载出来就给个错误页"→ 停止语义从"恢复旧回答"改为**停在流式状态**：前端 `regenerateMessage`/`sendStreamMessage` 取消与失败统一原位替换为**已流出部分内容**，一字未出显示占位「未生成回答内容」；后端 `_save_pair`/`_save_reply` 三出口统一落盘（成功/`Exception`/`GeneratorExit`+`CancelledError` 取消），取消路径同步执行截断+追加（旧回答进 `paired` 存档不丢、I1 等长保持），占位句前后端同一 `STOP_TEXT` 保证刷新一致；实测 `test_v139_api.py` **8/8 PASS**（真 LLM 流 2s 断开）+ 回归 30/30+29/29、type-check 9/lint 8 基线、build ✓

### v1.38 (2026-10-08)
- **修复**: [RAG消息版本交互与接口规范](./RAG消息版本交互与接口规范.md) 第九轮 — 截图反馈"编辑提问后加载期间出现两个气泡（旧回答 + 三点），一个提问应该对应一个回答"→ v1.37 的"生成期间保留旧回答"是数据保留不是渲染保留：新增 `streamingHiddenIndex`，重新生成加载期**临时隐藏该条旧回答**（提问下只有流式气泡），成功原位替换/失败原位替换/取消恢复显示（数据始终不丢、本地与链一致）；浏览历史格时旧回答强制显示（成对切换可见）；type-check 9/lint 8 基线、build ✓

### v1.37 (2026-10-08)
- **修复**: [RAG消息版本交互与接口规范](./RAG消息版本交互与接口规范.md) 第八轮 — 两问题：① **生成中切换显示加载**（三点/逐字）→ 根因 `regenerateMessage` 开流前 `slice` 本地截断 + `chat.py` 开流即 `truncateChain`，生成期间只能画流式气泡 → 改为**旧回答延迟截断**（`_build_stream_messages` 内存排除 `regenerateIndex`、成功/异常保存前才截断）+ 前端去预截断、成功原位替换（引用校验防串会话）、Abort 不丢旧回答；浏览任一历史格时**隐藏底部流式区**（后台生成继续、切回 `M/M` 恢复）+ 切换自动滚动到目标消息；编辑保存 `truncateAfter` 恒 false；② **最新格 `2/2` 不能删** → 新端点 `POST delete-current/{sid}`（`target=pair` 提问+回答原子成对回退 / `self` AI 铅笔条自回退，消息不删除、可删到 `1/1`、pop 释放配额），ChatMessage 最新格删除按钮 + `deleteCurrent` emit；实测 `test_v137_api.py` **29/29 PASS** + 回归 30/30、type-check 9/lint 8 基线、build ✓；附带：测试连续登录触发 10 分钟 3 次风控已解锁账号

### v1.36 (2026-10-08)
- **新增+修复**: [RAG消息版本交互与接口规范](./RAG消息版本交互与接口规范.md)（新文档，本功能唯一契约）— 第七轮用户反馈"切换/恢复/删除全乱"后按"先写接口文档再按文档实现"重做：① **格子模型 `k/M`**（M=历史+1，分母恒定只随删除减一，最新=`M/M`，替代"当前 1/N"编号）；② **删除"恢复此版本"**（切换即查看，前端 `restoreVersion` 全移除、后端端点标废弃保留兼容）；③ **线性 ‹›**（向旧/向新、端点禁用不循环）；④ **删除=成对删提问+回答并跳回最新格**；⑤ **AI 铅笔历史独立入口**（AI 被铅笔编辑过时 AI 消息出独立条，`pairBrowse`/`aiOwnBrowse` 双状态互斥）；实测 API 自动化 **30/30 PASS**（登录 11111、造数/编辑/截断/配额/成对删/越界/restore 兼容）、type-check 9/lint 8 基线、build ✓

### v1.35 (2026-10-08)
- **修复**: [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md) 第六轮 — 截图反馈两问题：① **切换器位置**：版本条从 AI 消息改挂**用户消息**（"切换不应该在 AI 消息上面，应该在我发的消息上面"），AI 消息不出条、内容随 `browseMap` 联动切换+描边；② **计数不符**：显示"N个版本"（历史数 N）实际能切 N+1 格（当前+N历史）→ "看似只有两个却有3个" → `positionLabel` 总数含当前 = N+1（`当前 1/3 → 2/3 → 3/3`）与格数自洽；已知限制：仅编辑过 AI 回答未编辑过提问的会话暂无浏览入口；type-check 9/lint 8 基线、build ✓

### v1.34 (2026-10-08)
- **修复**: [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md) 第五轮 — 截图三问题根因：① **回答双写**（后端流完成写链 + 前端 batchSave 再追加，本地链文件实证同秒两份，版本操作只改其一）→ 删前端 `saveToBackend` 两处调用及函数，后端唯一写入；② **加载态残留**（`isStreaming` 复位被 generateTitle/loadSessions 阻塞 → typing 指示器挂在已完成回答下）→ push 后立即复位；③ **双版本条冗余** → 版本条仅回答侧渲染（`role==='assistant'`），提问随 browseIndex 联动；附带：`editMessage`/`restore`/`delete` 显式检查业务返回码（拦截器 code≠200 也 resolve 的静默分叉）、后端 thinking 拆独立字段不混 content；链语义单测 15/15、type-check 9/lint 8 基线、build ✓；历史重复消息不清洗（删测试会话重聊）

### v1.33 (2026-10-08)
- **修复**: [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md) 第四轮 — 切提问版本回答永远是最新：编辑提问时三重截断物理删除旧回答 → 新增回答 `paired` 与提问 versions 成对存档（`/chat/regenerate` 请求体 `prevAnswerVersions` 落链）、ChatMessage browseIndex 受控 + RagAssistantView `browseMap` 提问↔回答联动切换、恢复/删除按 `field` 参数成对编排；旧会话已删回答不可找回（删会话重聊）；后端 paired 单测全绿、type-check 9/lint 8 基线、build 通过

### v1.32 (2026-10-08)
- **修复**: [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md) 第三轮 — 版本切换永远显示最新：初版 versions 只存改后内容，改 1 次时 `versions[0]==content` → 改为**每次编辑前快照改前内容**（`versions=[原文,改1前,…]`、content 恒最新），删除与 content 解耦（不再回退）；切到历史即可见"改之前"的样子

### v1.31 (2026-10-08)
- **修复**: [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md) 第二轮 — 编辑提问重复对话（`sendStreamMessage` 重发把同一提问本地+链双写）→ 改走 `regenerateMessage(idx+1)` 只生成回答；恢复/删除「版本不存在」误报（Vue 内联 `$event` 只取 emit 第一个参数，消息序号被当 versionIndex 越界）→ emit 改单参数 versionIndex；存量脏链需删会话重聊

### v1.30 (2026-10-08)
- **新增**: [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md) — 编辑消息改前原文全部不落盘（链/edits.json/弹窗对照），AI 学习只存 keyPoint；消息级版本切换条（左右浏览/恢复/删除），上限 6 次、删 1 减 1 配额；用户提问编辑改持久化 + 后端链截断（修刷新丢编辑）；修复中途 `displayContent` 未定义致气泡空白回归

### v1.29 (2026-10-07)
- **修复**: [主页宇宙分页与改密码提示修复 第二轮](../dixiyang-vue/docs/主页宇宙分页与改密码提示修复.md) — 「加载更多」删除后空转死循环与多页数据空洞（本地估算 vs 服务端 offset 不一致）→ 删除后 `realignList` 并行重拉前 N 页对齐 + 列表互斥锁 + 空页自动兜底；触底自动加载（哨兵+按钮双轨）、加载失败可见重试、移动端 44px 触摸目标

### v1.28 (2026-10-07)
- **修复**: [主页宇宙分页与改密码提示修复](../dixiyang-vue/docs/主页宇宙分页与改密码提示修复.md) — 主页 10 个宇宙上限三重根因（只拉第 1 页 / `pageSize` 被 FastAPI 忽略恒默认 10 / 计数用已加载数）→ `page_size` 对齐 + 加载更多分页 + 计数改 `total`；设置页改密码点击无反应 = 按钮 `type=submit` 走空 `@submit.prevent` 处理器（changePassword 压根不执行）→ 改 `type=button` 直调 + 防重入，errorText 精确表补改密码文案防被 `/密码/` 关键词吞成登录提示；后端实测 6/6 稳定无偶发；提交 `186d2c6`

### v1.27 (2026-10-07)
- **新增**: [Home页头部精简与视觉去AI味](../dixiyang-vue/docs/Home页头部精简与视觉去AI味.md) — `/home` 单行顶栏（原 3.5rem 渐变大标题+光条+100px logo → 40px 紧凑品牌行，clamp 边距），design-slop 闸门修复：紫蓝渐变/荧光/装饰全删、色板收敛蓝+青+中性、区块标题升 display 级；卡片与交互结构不动
- **补充**: 同文档第二轮——「太简单了」反馈后补结构：编辑部式 Hero（3.25rem 标题 + 宇宙/角色/节点大数字统计，真实字段汇总）、分节横规（标题+细线+计数徽章）、吸顶玻璃栏（`overflow:hidden`→`clip` 解锁 sticky）、卡片 hover 封面推近+主蓝边；尺度层级 ≈5× 对比

### v1.26 (2026-10-07)
- **新增**: [设定上下文与弹窗样式统一](../dixiyang-vue/docs/设定上下文与弹窗样式统一.md) — 设定上下文标题字号对齐（全局 h3 30px 根因）+ 去卡中卡 + 启用开关改纯色状态钮（hover title 显示状态）；ElMessageBox 底色 5% 白半透明 → `#222530` 实底修标题对比度，按钮复用时间线页 `.btn-icon` 玻璃风格，`:has()` 激活此前从未生效的危险红确认钮
- **重构**: 新增 `DialogHost.vue`（Promise 化输入/确认/离开三态 el-dialog 宿主），小说编辑页 5 处 ElMessageBox 全部改用，复用全局 `html .el-dialog` 玻璃面板 + 移动端底部抽屉，与角色/时间线页写法统一；修复取消弹窗时 Promise 未捕获 rejection

### v1.25 (2026-10-07)
- **新增**: [小说编辑器Tab禁用与段落视觉间距](../dixiyang-vue/docs/小说编辑器Tab禁用与段落视觉间距.md) — Tab 彻底废掉（幽灵文本时仍接受补全）+ 吞三个缩进快捷键 + Enter 换 `insertNewline`；段落间距用 `.cm-line` 底部 padding 1.95em（纯视觉、不写入文档，margin 会致 CM6 光标错位故不可用）；新建卷/切换侧栏两按钮换不同图标

### v1.24 (2026-10-06)
- **新增**: [编辑器AI补全设定勾选与光标续写](../dixiyang-vue/docs/编辑器AI补全设定勾选与光标续写.md) — 编辑器补全支持细粒度勾选角色/时间线/事件作为上下文（`AIContextPanel` + `novelId/characterIds/storyNodeIds/timelineIds` 请求字段，后端 `build_fixed_context` 组装截断 1500 字）；防复述截重叠修"整段返回"；自动补全放宽到光标任意位置
- **修改**: [卷章节与AI补全接口](../DixyangFast/docs/卷章节与AI补全接口.md) — `/ai/completion` 请求体新增设定 ids 字段与防复述行为说明

### v1.23 (2026-10-06)
- **新增**: [RAG对话头像图标替换](../dixiyang-vue/docs/RAG对话头像图标替换.md) — 对话头像 emoji 👤/🤖 换 Element Plus 图标（用户 `UserFilled`、助手 `MagicStick`），补同系文字色
- **修复**: 单点登录与登录风控 — 撤销"无 sid 旧 token 一律 401"，改兼容放行（修复后端 reload 后旧登录态全被拒、聊天页报"请求失败，请稍后再试"的问题），顶号比对保留，双后端同规则

### v1.22 (2026-10-06)
- **新增**: [单点登录与登录风控](./单点登录与登录风控.md) — 同账号多端登录时后登录顶掉先登录者（`app_user.session_id` + JWT `sid`，请求时比对，被踢端 401 自动跳登录并提示）；10 分钟内登录 3 次后密码登录强制邮箱验证码并可解除；Java 端补齐 `/auth/send-code`、`/auth/login-by-code` 邮件验证码设施（共用 `email_verification_code` 表）；双后端端到端各 12/12 PASS

### v1.21 (2026-09-30)
- **修改**: [卷章节与AI补全接口](../DixyangFast/docs/卷章节与AI补全接口.md) — **AI 补全去 mock**：`mock_provider.py` 删除、`config.py` 独立 `AI_PROVIDER/AI_BASE_URL/AI_API_KEY/AI_MODEL/AI_TIMEOUT` 5 项删除、`BaseTimedProvider` 死代码删除；补全直接复用 RAG 同款 `DEEPSEEK_*`（与聊天一处配置同切，当前指向本地 Ternary-Bonsai-2-27B，6.5s 实测返回真续写）；`/ai/status` 的 `connected` 改为如实反映 key 存在性（不再假报就绪）

### v1.20 (2026-09-30)
- **新增**: [小说编辑页背景图层叠与视觉AI修复](../dixiyang-vue/docs/小说编辑页背景图层叠与视觉AI修复.md) — `.editor-layout` 补 `position:relative`（有背景图时整页被 `#theme-bg` 压住、看不见但能点，全站唯一漏加者；**警告：新页面根容器必须 relative**）；视觉改半透明 scrim + 玻璃侧栏 + "稿纸"浮起卡片（不再全黑无区分度）；≤1024px 树/侧栏覆盖式抽屉 + resize 跨档位监听；mini-btn focus/触屏可见；AI 补全空文档提示 + ghost 配色加强 + 后端 mock 文案池
- **新增**: [卷章节与AI补全接口](../DixyangFast/docs/卷章节与AI补全接口.md) — 卷/章节 CRUD、正文文件存储与冲突协议、版本历史、AI 补全端点与 Provider 切换、越权校验说明

### v1.19 (2026-09-30)
- **新增**: [章节草稿本地优先存储](../dixiyang-vue/docs/章节草稿本地优先存储.md) — `draftDB.ts`（原生 IndexedDB + 内存降级）与 `useChapterDraft.ts`（本地优先加载、800ms 防抖自动保存、markSynced 清脏、dispose 自动清理）

### v1.18 (2026-09-30)
- **修复**: [404页被背景图覆盖修复](../dixiyang-vue/docs/404页被背景图覆盖修复.md) — `.ld-404` 补 `position:relative` 使其画到 `#theme-bg`（fixed/z-index:0）之上，亮纸底规则扩展匹配 `html:has(.ld-404)`；2 处 CSS、零 JS

### v1.17 (2026-09-29)
- **新增**: [弹窗面板全局化与去黑](../dixiyang-vue/docs/弹窗面板全局化与去黑.md) — 弹窗面板由不透明 `#0d0d0f` 改为 `#222530`（实测白字对比度 15.27，不黑且清晰），样式写入全局 `.el-dialog` 全站复用（8 个弹窗自动生效，含无样式的「AI 设定助手」）；同步修掉"EP 样式后导入 + 同特异性"导致标题色被覆盖成近黑的坑（改用 `html` 前缀，不引入 `!important`）；组件内约 120 行重复弹窗样式删除

### v1.16 (2026-09-29)
- **新增**: [卡片毛玻璃底板与弹窗配色修复](../dixiyang-vue/docs/卡片毛玻璃底板与弹窗配色修复.md) — 用 Chrome CDP 探针 + 像素测量取证：卡片透明真因是底板仅 `rgba(255,255,255,.05)` 而 `backdrop-filter` 不提供底色（实测切换 will-change/transform/position/overflow 零影响）；弹窗真因是全局 `.el-dialog{…!important}`，**`!important` 与特异性无关**必须逐条补 `!important`。新增 `--surface-panel-strong`（实测白字对比度 18.9），全局 `.glass-card`（时间线+角色页共用）、角色卡、角色弹窗统一换用

### v1.15 (2026-09-29)
- **新增**: [角色管理页移动端适配与美化](../dixiyang-vue/docs/角色管理页移动端适配与美化.md) — 卡片改 `auto-fill + minmax(150px,1fr)` 双列自适应（320 屏自动降单列），单卡 266→约 205px 且信息不减；弹窗改底部抽屉、输入框防 iOS 缩放、触屏去 sticky hover；圆角/语义色/动效统一到设计 token，卡片加错峰入场

### v1.14 (2026-09-29)
- **新增**: [更换邮箱验证码流程](../dixiyang-vue/docs/更换邮箱验证码流程.md) — 后端 `/user/update` 加 `CHG_EMAIL` 验证码+唯一性校验（先校验后落库），前端邮箱改为更换流程（发码/输码/确认），昵称保持失焦即存
- **新增**: [移动端响应式修复](../dixiyang-vue/docs/移动端响应式修复.md) — 角色管理删 `margin-left` 残留恢复居中、卡片字号降档、弹窗 `width=min()`；主页双列小卡降档修按钮挤压；`NovelPageHeader` 补齐响应式

### v1.13 (2026-09-29)
- **修改**: [悬浮球美化与适配修复](../dixiyang-vue/docs/悬浮球美化与适配修复.md) v1.1 — 球由左下/右下改**右侧垂直居中**，避开首页知识球体与时间线图例；横条向左展开、`pointer-events:none` 全高锚点条
- **修改**: [表单内联校验与错误文案统一](../dixiyang-vue/docs/表单内联校验与错误文案统一.md) v1.1 — 昵称/邮箱脏值检测，点一下输入框不再空发 update、不再误弹「更新成功」

### v1.12 (2026-09-29)
- **新增**: [表单内联校验与错误文案统一](../dixiyang-vue/docs/表单内联校验与错误文案统一.md) — FieldError/useFormValidation/errorText 三件套、登录页拆 el-form 三处统一、后端错误原文屏蔽、确认弹窗美化

### v1.11 (2026-09-29)
- **新增**: [悬浮球美化与适配修复](../dixiyang-vue/docs/悬浮球美化与适配修复.md) — 修复 FAB 模式巨型胶囊/横条压球两处布局回归，悬浮球纯 CSS 视觉美化 + Esc 收起 + 层级 130 + reduced-motion
- **新增**: [移动端浮动导航防遮挡](../dixiyang-vue/docs/移动端浮动导航防遮挡.md) — 触屏/窄视口 FloatingNav 改 FAB 悬浮球

### v1.10 (2026-09-28)
- **修复**: [motion-web 技能接入](./motion-web技能接入.md) — Windows 下 symlink 被 checkout 成文本文件导致技能不被发现，项目级 2 处改为 Junction 联接

### v1.9 (2026-09-28)
- **新增**: [motion-web 技能库出库与同步](./技能库出库与同步.md) — 技能移出 GitHub 但本地保留，`.githooks` 保护协作者 pull 不丢技能
- **合并**: 同步远程落地页、字体资源与 motion-web 接入文档（条目 14-17 重排）

### v1.8 (2026-09-28)
- **新增**: [LLM 接入配置切换](../DixyangFast/docs/LLM接入配置切换.md) — 临时切本地 llama-kvmem 模型、`load_dotenv(override=True)` 修复 401、切回 DeepSeek 步骤

### v1.7 (2026-09-28)
- **新增**: [登录页背景视频资源修复](../dixiyang-vue/docs/登录页背景视频资源修复.md) — `/videos/卡比.mp4` 解析失败根因与 `@/assets` 引用方案

### v1.6 (2026-09-28)
- **新增**: [对外介绍落地页](./落地页介绍页.md) — `/` 免登录首页、暖纸编辑部视觉、单屏索引切换 6 面板、抽稿换页转场、几何+动效验证记录

### v1.5 (2026-09-28)
- **新增**: [motion-web 技能接入](./motion-web技能接入.md) — opencode/Trae 接入动效网页技能，4 处软链 + AGENTS.md 索引

### v1.4 (2026-09-27)
- **新增**: [分支重建与版本对齐](./分支重建与版本对齐.md) — main 对齐 GitHub、`java` 分支恢复 Java 模块
- **调整**: `.gitignore` 放开 `dixiyang-engine/`（仅 `java` 分支）

### v1.3 (2026-09-27)
- **新增**: [Git 上传规划与执行记录](./git上传规划.md) — 上传清单、误跟踪清理、提交/推送记录
- **调整**: lock 文件（package-lock/pnpm-lock）纳入版本管理，`.gitignore` 取消对应忽略

### v1.2 (2026-09-24)
- **新增**: [登录鉴权与表单回车](./登录鉴权与表单回车.md) — `/home` 需登录、401 跳转、回车跳框/提交
- **规范**: 实现完成后必须更新 `docs/` MD 并登记本索引（见根目录 `AGENTS.md`）

### v1.1 (2026-05-31)
- **新增**: 预设背景图系统（`public/images/back/`）
- **删除**: 自定义背景图上传功能（BackgroundControl.vue 及相关 composable）
- **优化**: 背景预设精简为 3 种（dynamic/static/minimal），各有独立视觉配置
- **修复**: 小说封面字段名对齐后端 @JsonProperty snake_case
- **修复**: NovelMapper.xml cover 字段映射错误
- **修复**: 卡片入场动画阶梯效果，改为同一起点
- **清理**: 全部前端 console.log，统一全局 CSS 变量

---

*文档版本: v1.70*
*最后更新: 2026-10-19*
*维护者: Dixiyang Team*