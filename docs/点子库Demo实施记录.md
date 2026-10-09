# 点子库 Demo 实施记录

> **适用范围**: `DixyangFast/src/dixiyang/{models,schemas,services,routers}/idea*`、`dixiyang-vue/Dixiyang-vue3/src/{api/ideaApi.ts,views/IdeaLibraryView.vue,components/idea/*}`
> **契约**: [点子库与创意社区策划](./点子库与创意社区策划.md) v1.1（唯一契约）
> **文档版本**: v1.0 ｜ **最后更新**: 2026-10-08

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
7. **发布频控 10s 对同一用户全局生效**（含从失败调用计数），测试需注意时序。
8. **测试账号** 11111 连续登录会触发 10 分钟 3 次风控，脚本跑前先执行 `unlock_user.py`（临时脚本，不入库）。

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

---

*文档版本: v1.0 ｜ 维护者: Dixiyang Team*
