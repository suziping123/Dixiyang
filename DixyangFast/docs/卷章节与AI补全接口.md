# 卷 / 章节 / 正文 / AI 补全接口文档（DixyangFast）

> **模块**: 小说编辑页后端 ｜ **文档版本**: v1.0 ｜ **最后更新**: 2026-09-30
> 对应前端封装：`dixiyang-vue/docs/小说卷章节API封装.md`（`chapterApi.ts`）

## 全局约定

- 统一响应：`{ code: 200, msg, data }`；鉴权：`Authorization: Bearer <JWT>`（**全部接口均需登录**，缺失时报 `422 missing header authorization`，无效报 `401 token无效或已过期`）。
- **越权防护**：所有 service 方法签名强制携带 `user_id`，先校验目标 novel 归属再操作（已用 11 项攻击用例冒烟全拦）。
- **大文本文件化**：章节正文**不入 MySQL**，写 JSON 文件，DB 只存 `__file__:` 路径引用（见根 `AGENTS.md` 存储结构）。
  - 正文：`books/{novelId}/chapters/{chapterId}/content.json`
  - 版本历史：同目录 `versions/v{n}.json`
  - 章节删除会连带清理文件。

## 1. 卷（`/api/volumes`，prefix=`/volumes`）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/volumes/novel/{novelId}` | 某小说全部卷 |
| GET | `/volumes/{volumeId}` | 卷详情 |
| POST | `/volumes/novel/{novelId}` | 创建卷（body: `title, sort_order?`） |
| POST | `/volumes/{volumeId}` | 更新卷 |
| DELETE | `/volumes/{volumeId}` | 删除卷（含归属校验） |
| POST | `/volumes/novel/{novelId}/reorder` | 排序（body: `chapter_ids` 数组） |

## 2. 章节元数据（`/api/chapters`，prefix=`/chapters`）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/chapters/novel/{novelId}` | 某小说章节列表 |
| GET | `/chapters/{chapterId}` | 章节详情（含 `version/content_path/word_count`） |
| POST | `/chapters/novel/{novelId}` | 创建章节。**body 不含 novel_id**（路径取）：`{ title, volume_id?, sort_order? }` → `ChapterCreateReq` |
| POST | `/chapters/{chapterId}` | 更新章节（`ChapterUpdate`） |
| DELETE | `/chapters/{chapterId}` | 删除章节（连带清理正文文件与版本） |
| POST | `/chapters/novel/{novelId}/reorder` | 章节排序（body: `chapter_ids: int[]`） |

## 3. 正文（文件存储，`/api/chapters/{id}/...`）

### GET `/chapters/{chapterId}/content` — 读正文
```json
{ "code": 200, "data": {
  "chapterId": 7, "title": "第一章", "version": 4,
  "contentHash": "…", "content": "正文…", "wordCount": 24, "updatedAt": "…"
}}
```

### POST `/chapters/{chapterId}/content/conflict-check` — 保存前冲突检测
Body: `{ "clientVersion": 4, "clientHash": "…" }` → `data: { hasConflict, serverVersion, serverHash }`

### POST `/chapters/{chapterId}/content` — 保存正文（仅显式"保存到云端"触发）
Body: `{ "title", "content", "clientVersion", "clientHash", "force?": false }`
- 冲突（版本变化且 hash 不同）且未 `force` → `msg=存在冲突, data.hasConflict=true`（前端弹冲突框）
- 成功 → MySQL 更新 `content_path/content_hash/content_size/version/word_count`，正文写 JSON；返回 `{ version, contentHash, contentPath, wordCount, hasConflict:false }`
- `force=true`（用户选"用本地覆盖"）→ 强制写入

### GET `/chapters/{chapterId}/versions` — 版本列表
`data: { current, history: [{version, createdAt, contentHash, wordCount, …}] }`

### GET `/chapters/{chapterId}/versions/{version}` — 读历史版本正文

## 4. AI 补全（`/api/ai`）

> **2026-09-30 起为真模型**：mock Provider 与独立 `AI_*` 配置已全部删除，补全直接复用 RAG 聊天同一套 `DEEPSEEK_API_KEY/BASE_URL/MODEL`（一处配置，聊天与补全同切）。

### GET `/ai/status`
`data: { connected: bool(DEEPSEEK_API_KEY), provider: "openai-compatible" }` → 侧栏"AI 就绪/未连接"（无 key 时如实报未连接，不再假报就绪）。

### POST `/ai/completion`
```json
{ "chapterId": 7, "chapterTitle": "第一章 测试",
  "cursorBefore": "光标前正文（前端截断 ≤2000 字）",
  "cursorAfter": "光标后正文（≤200 字）",
  "novelContext": "背景设定（≤300 字，可空，兼容旧调用）",
  "novelId": 1,
  "characterIds": [18], "storyNodeIds": [94], "timelineIds": [4],
  "maxTokens": 80 }
```
成功：`data: { text, model, requestId, latency, finishReason }`（`model` = 实际模型名）；不可用：`data: null`（`msg=补全不可用`，编辑器静默降级）。
- 端点只返回短补全文本，**绝不修改正文**；`maxTokens` 后端钳制 20~80。
- **设定上下文（2026-10-06）**：`characterIds/storyNodeIds/timelineIds`（各 ≤50，可空数组）非空时，后端复用 `chat_service.build_fixed_context` 查角色卡（含背景/性格/外貌/附加）与事件，另查 `timeline` 表拼 `[时间线]` 条目，组装后总截断 1500 字符注入 prompt；勾选由前端编辑器侧栏「设定上下文」面板控制，未勾选=旧行为。
- **防复述（2026-10-06）**：system prompt 强化"严禁复述/重写光标前内容"；返回文本与 `cursor_before` 尾部重叠 ≥6 字符时截掉重叠前缀（`_strip_repetition`），截后为空=返回 `data:null`，修"模型整段复述返回"问题。
- 超时保护：`asyncio.wait_for(provider, COMPLETION_TIMEOUT+2)`（模块常量 10s），失败返回 None 不抛错。
- 无 `DEEPSEEK_API_KEY` → 不发请求直接返回 None（日志警告），前端显示未连接。

### 模型切换
改 `.env` 的 `DEEPSEEK_*` 即可（聊天+补全一起切），详见 `docs/LLM接入配置切换.md`（云端 DeepSeek ↔ 本地 llama）。**没有第二套补全配置。**

## 5. 改动文件（本模块实现）

- `src/dixiyang/routers/volume.py`、`chapter.py`、`ai.py`
- `src/dixiyang/services/volume_service.py`、`chapter_service.py`、`chapter_content_service.py`
- `src/dixiyang/services/completion/`（`base.py` / `__init__.py`；`mock_provider.py` 已删除）
- `src/dixiyang/config.py`（`AI_*` 独立配置 5 项已删除）
- `src/dixiyang/schemas/chapter.py`、`models/chapter.py`

## 6. 已知问题

- 章节删除只校验 novel 归属，未校验"卷归属 novel"的二次一致性（创建时已保证，风险低）。
- 正文文件清理依赖删除时同步执行，无孤儿文件定期巡检。
- AI 补全未做用户级限流（单机自用场景暂不需要）。

## 7. 验证方式

```bash
# 冒烟 + 11 项越权攻击用例（需后端 8084 在跑）
.venv/Scripts/python.exe C:\Users\Lenovo\AppData\Local\Temp\opencode\smoke_novel_editor.py
```
覆盖：注册登录、卷/章 CRUD、正文文件读写（`__file__:` 路径）、版本历史、冲突检测、force 覆盖、AI Mock 补全、删除清理、横向越权拦截。

---

*文档版本: v1.0 ｜ 维护者: Dixiyang Team*
