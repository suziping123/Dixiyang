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

### 8.4 [移动端浮动导航防遮挡](../dixiyang-vue/docs/移动端浮动导航防遮挡.md) ✨ 新增
**位置**: `dixiyang-vue/docs/移动端浮动导航防遮挡.md`

**内容**:
- 触屏 FloatingNav 由左下角常驻横条改为 FAB 悬浮球 + 点击展开（含全屏遮罩拦截误触）
- FAB 触发条件扩展为「触屏 或 视口 ≤1024px」：桌面缩窗下 100px hover 热区挡按钮的问题一并解决
- RAG 页 ≤768px「历史/上下文」按钮居中，远离左缘
- 点遮罩 / 再点球 / 选导航项 / 路由切换均收起；>1024px 桌面 hover 模式不变
- 层级结构、已知问题、验证方式

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

*文档版本: v1.25*
*最后更新: 2026-10-06*
*维护者: Dixiyang Team*