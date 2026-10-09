# 点子库 Demo 实施记录

> **适用范围**: `DixyangFast/src/dixiyang/{models,schemas,services,routers}/idea*`、`dixiyang-vue/Dixiyang-vue3/src/{api/ideaApi.ts,views/IdeaLibraryView.vue,components/idea/*}`
> **契约**: [点子库与创意社区策划](./点子库与创意社区策划.md) v1.2（唯一契约）
> **文档版本**: v1.2 ｜ **最后更新**: 2026-10-09

## 1. 需求

按策划 v1.1 完成点子库功能的**可运行 Demo**——实际完成、能跑通全链路，但控制体量不做二期内容。

## 2. Demo 范围（与策划 v1.1 的裁剪差异）

| 项 | 策划 v1.1 | Demo 实现 | 说明 |
|----|----------|----------|------|
| 数据表 | 7 表 | ✅ 7 表全建 | `idea_post/idea_draft/idea_attachment/idea_post_tag/idea_like/idea_collect/idea_comment`，`create_all` 自动建表 |
| 五分区 | idea/character/setting/timeline/tech | ✅ 同 | `CATEGORIES` 校验，**无 chat 分区**（对话快照挂在 idea 分区的 sourceRef 上） |
| Redis | 计数/热门 ZSET/频控/降级 | ❌ 跳过 | 计数直读 DB；热门 = `3赞+2收藏+2评论+1浏览` 实时算；频控进程内存 `_limited()`（发帖 10s/导入 10s/评论 15s）；正式版按策划 §4 换 Redis |
| `app_user` ALTER | 加 `avatar_url`/`pen_name` | ❌ 跳过 | 作者名取 nickname→username，头像用首字母占位；Demo 不动存量表结构 |
| 附件类型 | 4 类导出 | ⚠️ 2 类 | `chat_snapshot`（idea 分区选会话）+ `character_card`（character 分区选角色，支持逗号分隔多选）；**setting/timeline 分区可发帖但仅纯文字**（导出未接） |
| 角色一键导入 | ✅ | ✅ | 复制行 + extra 文件、vector_id 不涉及；同名自动加后缀（`uk_novel_name` 唯一键防撞）；频控 10s |
| 前端组件 | 6 组件 | ⚠️ 4 文件 | `IdeaLibraryView`（四 Tab 集一页）+ `DraftEditorDialog` + `PostDetailDialog` + `ideaApi.ts`（按现有 `src/api/*Api.ts` 惯例命名，非策划中 composables 路径） |
| 附件预览 | 服务端生成预览 | ⚠️ 前端确认制 | 后端无独立预览端点；前端「预览」步骤展示正文+附件来源摘要，`previewed=true` 后才允许点「确认发布」（后端仍强校验 `previewed`） |
| 相似推荐/投票/知识库 | 二期 | ❌ 不做 | 策划 §8 路线图 |

## 3. 后端实现

- **模型** `models/idea.py`：7 张表，`create_time` 惯例、组合索引、`IdeaAttachment.type ∈ {chat_snapshot, character_card, setting_bundle, timeline_view}`。
- **服务** `services/idea_service.py`：
  - 草稿 CRUD（`body_path` 存 `storage/community/{userId}/draft_{id}.json`）→ 发布（删草稿、写正文、生成附件、写标签行）；
  - 广场列表：分区/关键词/标签多选过滤 + `new|hot|like` 排序 + 分页；详情浏览 +1；
  - 点赞/收藏 toggle（计数原子 `max(0, n-1)`）、评论（15s 频控）、标签聚合 TopN、我的三列表（帖子/收藏/点赞）、下架/恢复（作者仍可访问已下架）；
  - 进程内存频控 `_limited(key, seconds)`；`hot_score` 发布/互动时重算。
- **导出导入** `services/idea_export.py`：`export_chat_snapshot`（复用 `chain_file_manager.read_chain`）、`export_character_cards`（权限校验：角色所属小说归本人）、`import_character_cards`（同名自动 `(2)` 后缀）、community JSON 读写删。
- **路由** `routers/idea.py`：策划 §5 全端点；公开读接口用新增 `get_optional_user_id`（`utils/auth_deps.py`，带合法 token 返回 userId、否则 None，支撑 `likedByMe`），写接口沿用 `get_current_user_id`。
- **接线** `main.py`：import 模型注册 + `include_router(idea.router, prefix="/api")`。

## 4. 前端实现

- `api/ideaApi.ts`：全部 `/idea/*` 端点 + 类型（snake→camel 已由后端统一）。
- `views/IdeaLibraryView.vue`：四 Tab（广场/草稿箱/我发布的/我的收藏）、分区 chips、排序、热门标签过滤、卡片网格、分页、草稿编辑/删除/发布入口。
- `components/idea/DraftEditorDialog.vue`：分区切换、来源级联（character→小说+角色必选；idea→会话可选）、标签多选（allow-create）、**保存草稿→预览→确认发布**三步流（`previewed` 变更即重置，改内容需重新预览）。
- `components/idea/PostDetailDialog.vue`：详情+附件渲染（角色卡人设表/对话快照预览）、**一键导入**（弹小说选择）、点赞/收藏 toggle、评论分页/发送/删除（回车=换行、按钮提交）、作者下架/恢复。
- 路由 `/ideas`（requiresAuth）+ `FloatingNav` 加「点子库」入口（`Collection` 图标）。

## 5. 踩坑记录（先查文档的一课）

| 坑 | 来源文档 | 处置 |
|----|---------|------|
| **新增页面根容器必须 `position: relative`**，否则有背景图时整页被 `#theme-bg` 压住（看不见但可点） | `dixiyang-vue/docs/小说编辑页背景图层叠与视觉AI修复.md` ⚠️、`404页被背景图覆盖修复.md` | `.idea-page` 补 relative + 警告注释；CDP 冒烟验证 `computed position === 'relative'` |
| 弹窗面板全局色 `#222530` | `弹窗面板全局化与去黑.md` | 未覆盖面板色，冒烟实测 `rgb(34,37,48)` 生效 |
| 回车约定：单行 `enterSubmit(fn, $event)`、textarea 不触发提交 | `dixiyang-vue/AGENTS.md` | 搜索框改 `enterSubmit`；评论 textarea 移除回车发送、仅按钮提交 |
| 危险删除用 `confirmDelete`（autofocus:false 禁回车误删） | `utils/confirm.ts` | 草稿删除/下架/删评论均走 `confirmDelete` |
| 拦截器对 code≠200 也 resolve | `docs/README.md` 8.24 勘误 | 所有调用经 `unwrap()` 显式检查 code |
| `FloatingNav` 是**各 view 自行挂载**（非全局） | 代码普查 | `IdeaLibraryView` 补挂；新增第 4 项补 `nth-child(4)` 依次弹入延迟 |
| 用户 id 存储 key 是 `userId`/`userInfo`（非 `user`） | `stores/UserStore.ts` | 作者身份判定改读正确 key，否则「下架」按钮永不出现 |
| 无 `chat` 分区——对话快照挂 **idea 分区**（后端 `category→attach_type` 映射） | 后端 `idea_service.py:26-30` | 前端来源选择分支由 `chat` 改 `idea`（可选），角色区仍必选 |

## 6. 改动文件

| 文件 | 改动 |
|------|------|
| `DixyangFast/src/dixiyang/models/idea.py` | 新增：7 表 |
| `DixyangFast/src/dixiyang/schemas/idea.py` | 新增：入参 schema（alias 惯例） |
| `DixyangFast/src/dixiyang/services/idea_service.py` | 新增：草稿/发布/列表/互动/评论/导入业务 |
| `DixyangFast/src/dixiyang/services/idea_export.py` | 新增：快照导出 + 角色导入（同名后缀） |
| `DixyangFast/src/dixiyang/routers/idea.py` | 新增：全部端点 |
| `DixyangFast/src/dixiyang/utils/auth_deps.py` | 加 `get_optional_user_id` |
| `DixyangFast/src/dixiyang/main.py` | import 模型 + include_router |
| `dixiyang-vue/Dixiyang-vue3/src/api/ideaApi.ts` | 新增 |
| `dixiyang-vue/Dixiyang-vue3/src/views/IdeaLibraryView.vue` | 新增 |
| `dixiyang-vue/Dixiyang-vue3/src/components/idea/{DraftEditorDialog,PostDetailDialog}.vue` | 新增 |
| `dixiyang-vue/Dixiyang-vue3/src/router/index.ts` | 加 `/ideas` |
| `dixiyang-vue/Dixiyang-vue3/src/components/FloatingNav.vue` | 加点子库入口 + 第4项动画延迟 |

## 7. 已知问题 / 限制

1. **收藏状态不回显**：后端列表/详情未返回 `collectedByMe`（仅 `likedByMe`），弹窗打开时收藏按钮恒未选中（计数正确）；正式版加字段。
2. **Redis 未接**：频控为进程内存（重启清零、多进程失效），热门分数实时算无缓存；按策划 §4 换 Redis。
3. **`app_user` 未加 `avatar_url`/`pen_name`**：作者展示昵称/用户名，头像首字母占位。
4. **setting/timeline 分区仅纯文字**：`idea_attachment` 结构支持，导出函数未实现（策划二期项）。
5. **表单未接 `FieldError` 内联校验**：仍用 `ElMessage.warning`（与全站现存 37 处同风格）；后续按[表单内联校验与错误文案统一](../dixiyang-vue/docs/表单内联校验与错误文案统一.md)接入。
6. **character 分区来源为单选**：后端支持逗号分隔多角色，前端下拉暂单选。
7. ~~**发布频控 10s 对同一用户全局生效**（含从失败调用计数）~~ → **第二轮已修复**：改为 `_limit_check`（只读）+ `_limit_mark`（成功才打点），业务失败不消耗额度，频控文案带剩余秒数（见 §10）。
8. **测试账号** 11111 连续登录会触发 10 分钟 3 次风控，脚本跑前先执行 `unlock_user.py`（临时脚本，不入库）。
9. **配图文件不回收**：删除/下架帖子与移除草稿图片仅删 DB 行/引用，`uploads/idea-images/` 实体文件保留（MD5 去重下重复上传可复用）；正式版加引用计数或定期清扫。

## 8. 验证方式与结果

```bash
# 后端
cd DixyangFast && .\.venv\Scripts\python.exe -m py_compile src\dixiyang\{models/idea.py,schemas/idea.py,services/idea_service.py,services/idea_export.py,routers/idea.py,main.py}   # ✓
# API 全链路（Temp/opencode/test_idea_api.py，登录前先 unlock）→ 40/40 PASS
#   覆盖：登录/未登录拒绝/草稿CRUD/预览拦截/发布/分区/搜索/标签/排序/详情浏览+1/
#        点赞收藏toggle/评论+频控/我的列表/标签聚合/下架恢复/角色帖附件/
#        导入(越权/正常/同名后缀/频控)/发帖频控/无效token

# 前端（基线：type-check 9 / lint 8 / build ✓）
cd dixiyang-vue/Dixiyang-vue3
npm run type-check   # 9 = 既有基线
npm run lint         # 8 = 既有基线
npx vite build       # ✓ 9.08s

# CDP 冒烟（headless Chrome 9222 + Temp/opencode/_smoke_ideas.mjs）
# 未登录 /ideas → /login ✓；注入 token → 渲染 4 Tab + 10 卡片 + 4 导航项 ✓
# .idea-page position:relative ✓（背景层叠坑）；弹窗面板 #222530 ✓；控制台 0 错误 ✓
# → SMOKE PASS ×2（补挂 FloatingNav 后复测）
```

## 9. 后续建议

按策划 §8 路线图：① Redis 接入（计数/热门/频控）→ ② `collectedByMe` 字段 + `avatar/pen_name` ALTER → ③ setting/timeline 附件导出 → ④ Chroma `idea_posts` 相似推荐 → ⑤ 分享按钮/作者主页。

## 10. 第二轮：用户反馈修复与增强（2026-10-09，v1.1）

### 10.1 需求

用户实测反馈 5 问题：① 弹窗内下拉/输入框出现白色"蒙版" ② 发布报"会话不存在或已删除" ③ 失败后立即重试被"频繁发布"拦截且感觉无提示 ④ 来源角色两个下拉同样蒙版 ⑤ 广场要支持图片 + 改小红书瀑布流；追加 ⑥ 来源对话按小说分类（先选小说再选对话）。

### 10.2 根因与方案

| # | 根因 | 修复 |
|---|------|------|
| ①④ | `main.css:479` 选择器 `.el-option` **错误**（EP 实际类 `.el-select-dropdown__item`），且 EP 浮层 teleport 到 body 不在 dialog 内，白底浮层从未被深色化 | 重写为 `html .el-select__popper/.el-popper/.el-select-dropdown` 全局深色 `#222530` 实底 + 选项 hover 高亮（`html` 前缀提特异性压过后导入的 EP CSS） |
| ② | `idea_export.export_chat_snapshot` 拼 `CHAT_STORAGE_PATH/{user}/{session}`，真实链目录是 `.../chat/{user}/{session}`（少 `chat` 段）→ 快照永远找不到 | 目录补 `chat` 段，对齐 `chat_history_service._session_dir`；同时前端 `DraftEditorDialog` 切分区不清 `sourceRef`（残留角色 id 被当 sessionId）→ `onCategoryChange()` 统一清来源 |
| ③ | `_limited()` 检查即打点——**业务失败也扣频控额度** | 拆 `_limit_check()`（只读，返回剩余秒）+ `_limit_mark()`（发布/评论/导入**成功后**才打点）；文案带剩余秒数（"发布太频繁了，请 N 秒后再试"）；弹窗 footer 加 inline 红色错误条（与 ElMessage 双保险） |
| ⑤ | 无图、网格布局 | 新表 `idea_post_image(post_id,url,sort)`（**新表避免 ALTER**，create_all 自动建）+ `POST /upload/idea-image`（复用 `_do_upload` MD5 去重，存 `uploads/idea-images/`）；草稿 body 存 images（`_clean_images` 白名单校验防外链，≤9 张），发布转正为行；列表/详情批量带 `images/coverUrl`；前端 `el-upload` 手写缩略图网格（首张标"封面"）、广场 CSS multi-column 瀑布流（3:4 封面卡）、详情 `el-image` 预览画廊 |
| ⑥ | 后端 `GET /chatHistory/sessions?novelId=` 已支持 | 纯前端：来源对话改两级级联（小说下拉含「未绑定小说」→ `getChatSessions(novelId)` 过滤），编辑草稿按 `sessions[].novelId` 回显 |

### 10.3 改动文件

| 文件 | 改动 |
|------|------|
| `DixyangFast/src/dixiyang/services/idea_export.py` | 快照目录补 `chat` 段 |
| `DixyangFast/src/dixiyang/services/idea_service.py` | 频控 check/mark 分离（publish/comment/import 三处）；`_clean_images`/`_images_of`；草稿/发布/`_post_item`/`update_post` 接入 images |
| `DixyangFast/src/dixiyang/models/idea.py` | 新增 `IdeaPostImage`（第 8 张表） |
| `DixyangFast/src/dixiyang/schemas/idea.py` | `DraftBase.images`、`PostUpdate.images` |
| `DixyangFast/src/dixiyang/routers/file.py` | `POST /upload/idea-image` |
| `dixiyang-vue/Dixiyang-vue3/src/assets/main.css` | EP 浮层全局深色（修错误选择器） |
| `dixiyang-vue/Dixiyang-vue3/src/api/ideaApi.ts` | `images/coverUrl` 类型、`uploadIdeaImage`、`getChatSessions(novelId?)` |
| `dixiyang-vue/Dixiyang-vue3/src/components/idea/DraftEditorDialog.vue` | 切分区清 sourceRef、小说→对话级联、配图上传网格、inline 错误条 |
| `dixiyang-vue/Dixiyang-vue3/src/views/IdeaLibraryView.vue` | 广场 `.feed-waterfall` 小红书瀑布流 + `.xhs-card` 封面卡 |
| `dixiyang-vue/Dixiyang-vue3/src/components/idea/PostDetailDialog.vue` | `.d-gallery` 配图画廊（`el-image` 预览） |

### 10.4 验证方式与结果

```bash
# 后端 py_compile 5 文件 ✓
# API 第二轮回归（Temp/opencode/test_idea_api_round2.py）→ 15/15 PASS
#   配图上传/MD5复用/格式拒绝、草稿 images 清洗（去外链+去重）、失败不扣额度
#   （连续两次"草稿不存在"仍返回草稿不存在而非频控）、失败重试后立即发布成功、
#   列表/详情 images+coverUrl、频控文案带秒数、会话按小说过滤、
#   真实会话快照发布 → 附件 messages=6（chat 段修复实证）
# 既有 40 用例回归 → 40/40 PASS（频控新语义下全绿）
# 前端基线 type-check 9 / lint 8 / build ✓ 9.30s
# CDP 冒烟（_smoke_round2.mjs）→ SMOKE2 PASS ×2
#   下拉 popper bg=rgb(34,37,48) 深色 ✓、级联两级下拉 ✓、
#   选对话→切分区→切回 sourceRef 清空 ✓、错误条可见 ✓、守卫/瀑布流/0 控制台错误 ✓
# 独立截图（_shot_errbar.mjs → errbar_shot.png）：错误条红底红字 + ElMessage 双提示 ✓
```

### 10.5 遗留

1. 标题输入框在亮背景页上的观感待用户复核（`--surface-input` 5% 白半透明，本轮未收到确证反馈前不动）。
2. 配图文件不回收（见 §7.9）。
3. 拖拽排序/裁剪等进阶图片编辑未做（Demo 只支持增删、首图即封面）。

---

## 11. 第三轮：九条用户反馈（2026-10-09，v1.2）

### 11.1 需求

用户 9 条反馈：① emoji 统计图标 AI 味 ② 赞/藏无动画 ③ 必须进详情才能互动 ④ 手机端无优化 ⑤ 卡片与背景不融合 ⑥ 输入弹窗模糊蒙板 ⑦ 详情图"点进去没了" ⑧ 下架应为修改服务 ⑨ Redis+管理员策划（→ 见 [Redis与管理后台策划](./Redis与管理后台策划.md)，本轮仅出文档）。

### 11.2 根因与方案

| # | 根因（实测） | 方案 |
|---|---|---|
| ① | 全站 emoji（👁👍💬⭐❤📎） | 新建 `IdeaIcon.vue`（viewBox 24 / stroke currentColor / 1.6px 自绘线性 SVG）替换全部 |
| ② | 无反馈 | `stat-bump`/`act-bump` keyframes（图标+计数弹跳）+ `:active` 缩放 + 实心填色 |
| ③ | 卡片统计仅展示 | 卡脚 `.stat-btn`（♡/☆）`@click.stop` 乐观更新+失败回滚；后端补发 `collectedByMe` |
| ④ | 无断点样式 | IdeaLibraryView 768 media：padding `14px 88px 72px 14px` 避让 FAB、tab/chip/tag 横滑、grid 150px 双列、瀑布流 column-width 150；DraftEditor source-row 1 列；PostDetail .d-actions 换行；**横向溢出根因**=`.filter-row` 内 chip/sort 组 `flex-shrink:0`+nowrap 撑到 572px → 改 overflow-x 收在块级容器内（实测 scrollWidth 572→375） |
| ⑤ | `--surface-card` 全局 `rgba(255,255,255,0.04)` | `.idea-page` 与 `PostDetailDialog .detail-body` 作用域覆盖 `#171a24` 实底+border/shadow（grep 实证全站仅此 2 文件 6 处引用） |
| ⑥ | 全局 `input,textarea,select{backdrop-filter:blur(10px)}` + 控件 5% 半透明 | `html .el-dialog` 控件 `background:#191c27 !important; backdrop-filter:none !important`（!important 压 main.css 尾部全局 `.el-input__wrapper !important`）、面板去 blur、`.el-overlay` 加深 0.62。**⑥-b 复燃修复**：filterable select 的原生 `input.el-select__input` 聚焦展开时命中全局 blur 规则 → 白雾蒙板（点击出现、失焦 input 塌缩消失）；补 `html .el-dialog input,textarea,select{backdrop-filter:none !important}` 通配 + 页面级 `input.el-select__input,.el-input-number__input` 同治（CDP 实测 focus 态 `backdropFilter:none`，26/26 回归） |
| ⑦ | 画廊在正文后被挤出视口 | 详情模板画廊移到 tags 后、`d-content` 前（置顶） |
| ⑧ | 后端 update_post 已支持 removed；前端无编辑入口 | 新建 `PostEditDialog.vue`（标题/正文/标签/配图，分区只读+removed 提示条）；入口：详情操作栏「编辑帖子」+「我发布的」removed 卡 `.edit-entry`；**附带修 bug**：toggle_like/collect 原要求 published 导致悬空收藏无法取消 → 改为取消操作允许 removed、新增仍限 published |
| ⑨ | — | 仅策划：[Redis与管理后台策划](./Redis与管理后台策划.md) v1.0 |

### 11.3 改动文件

- **前端**：`components/idea/IdeaIcon.vue`（新）、`components/idea/PostEditDialog.vue`（新）、`IdeaLibraryView.vue`、`PostDetailDialog.vue`、`DraftEditorDialog.vue`、`assets/main.css`、`api/ideaApi.ts`（`collectedByMe` + `updatePost`）。
- **后端**：`services/idea_service.py` — `_collected_set()`、`_post_item(..., collected)` 下发 `collectedByMe`、5 调用点（list_posts/get_post/list_mine_posts/collects/likes）、toggle 双修。
- **文档**：本记录 v1.2、`Redis与管理后台策划.md`（新）、README 登记。

### 11.4 验证方式与结果

```bash
# 后端 py_compile ✓
# round3 API（test_idea_api_round3.py）→ 19/19 PASS
#   collectedByMe 全链路（赞/藏后 feed/详情/我喜欢/我收藏）、下架帖可 update、
#   更新配图、恢复上架、下架后仍可取消收藏
# round2 → 15/15 ｜ round1 → 40/40（先 unlock_user.py 解登录风控；跑前 sleep 11 避发布频控）
# 前端基线 type-check 9 / lint 8 / npx vite build ✓ 8.53s
# CDP 冒烟（_smoke_round3.mjs）→ 26/26 PASS、控制台 0 错误
#   图标/动画/卡脚赞藏/详情画廊置顶/编辑弹窗回显/移动端 375 无横向溢出/蒙板实底
# 截图复核：smoke3_detail / smoke3_mobile / smoke3_editor ✓
# ⑥-b 蒙板复燃专项（_dbg_select.mjs CDP）：focus 态 dump 全部 backdropFilter=none ✓、sel_focus.png 无白雾 ✓
#   注：冒烟选帖改为"第一个带图卡"（首卡可能无图，数据依赖非代码回归）
```

### 11.5 遗留

1. 移动端管理后台不适配（明确不做，见策划 §2.5）。
2. Redis/管理后台本轮仅策划未实施（见 [Redis与管理后台策划](./Redis与管理后台策划.md) §3 风险）。
3. 配图文件回收、拖拽排序沿袭第二轮遗留（§10.5）。

---

*文档版本: v1.2 ｜ 维护者: Dixiyang Team*（v1.0 2026-10-08 首版，v1.1 2026-10-09 第二轮修复与图片/瀑布流增强，v1.2 2026-10-09 第三轮九条反馈）
