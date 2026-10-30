# 笔试 C · 后端与 RAG 契约（18 题）

> **对应能力**：E2 代码审查、E4 契约设计
> **建议用时**：90 分钟 ｜ **满分**：100
> **规则**：必须区分"Python 主后端 / Java 备用 / 独立 RAG 8085 / Chroma 8000"；必须写清攻击面或数据后果。

---

## C1. 角色/时间线/故事节点接口裸奔（L1）★P0

**题目**：`character.py`、`timeline.py`、`story_node.py` 的全部增删改查都没有 `Depends(get_current_user_id)`。请说明攻击步骤、影响，并给出最小修复。

**材料**：

```python
# character.py
@router.get("/all/{novel_id}")
async def list_all(novel_id: int, svc: CharacterService = Depends()):
    return svc.list_all(novel_id)

@router.post("/delete/{char_id}")
async def delete(char_id: int, svc: CharacterService = Depends()):
    return svc.delete(char_id)
```

**参考答案**：

- **攻击**：未登录直接 `GET /api/novelCharacter/all/1` 读任意小说角色；`POST /api/novelCharacter/delete/123` 删任意角色；时间线/故事节点同理。ID 是自增，枚举成本极低。
- **影响**：越权读取（作品设定泄露）、越权删除/篡改（数据损坏）；属于 P0。
- **根因**：路由层没有认证依赖，Service 只按 `novel_id/char_id` 查，没有 `user_id` 归属校验。
- **最小修复**：
  1. 路由加 `user_id: int = Depends(get_current_user_id)`。
  2. Service 方法加 `user_id`，先查小说归属（`Novels.id == novel_id and Novels.user_id == user_id`），再操作子资源。
  3. 对 `char_id/timeline_id/node_id` 先查父 `novel_id` 再校验归属；不要只信前端传的 novelId。
- **不要**只在网关加鉴权：Java/Python 双后端、直连 8085 都可能绕过。
- **验证**：

```bash
# 未登录
curl -i http://localhost:8084/api/novelCharacter/all/1          # 期望 401/403
# 用户 A 的 token 操作用户 B 的角色
curl -i -X POST -H "Authorization: Bearer $A_TOKEN" \
  http://localhost:8084/api/novelCharacter/delete/$B_CHAR_ID      # 期望 403/业务错误
```

**解析**：这是"认证缺失"而不是"越权判断写错"。评测时要能区分 401（没登录）和 403（登录了但没权限）。

**评分**：攻击步骤 2；影响 1；修复 2；验证 1。

**追问**：只在 `main.py` 加全局中间件够吗？→ 可以统一认证，但资源归属仍要在 Service 校验；中间件不知道 `char_id` 属于谁。

---

## C2. 用户配置 IDOR + CORS 通配（L2）★P0

**题目**：`/api/userConfig/background?userId=4` 不需要 token，且 `main.py` 配了 `allow_origins=["*"]` + `allow_credentials=True`。请说明风险与修复。

**材料**：

```python
# user_config.py
@router.get("/background")
async def get_background(userId: int = Query(..., alias="userId"), svc=Depends()):
    return svc.get_background(userId)
```

```python
# main.py
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, ...)
```

**参考答案**：

- **IDOR**：改 `userId` 即可读/写任意用户的背景、自定义背景列表、字体颜色；不需要登录。
- **CORS**：`*` + credentials 在浏览器规范下本身不安全/不生效；若反射 Origin，则任意站点可带用户凭证跨站读写。
- **影响**：隐私泄露、配置被篡改；结合上传接口可替换背景图。
- **修复**：
  1. 路由加 `Depends(get_current_user_id)`，`userId` 从 token 取，**禁止**从 query/body 取目标用户。
  2. 管理员查看他人配置走单独 admin 路由 + `require_admin`。
  3. CORS 改为显式域名白名单；`allow_credentials=True` 时不能用 `*`。
- **验证**：无 token 请求 → 401；用户 A token 带 `userId=B` → 只返回 A 或 403；`Origin: https://evil.com` 预检 → 不回 `Access-Control-Allow-Origin`。

**解析**：IDOR 的核心是"用客户端提供的对象 ID 直接查"，而不是"有没有登录"。

**评分**：IDOR 2；CORS 1.5；修复 1.5；验证 1。

**追问**：只把 `userId` 改成从 JWT 取，Service 还要改吗？→ 要；Service 不能信任调用方传入的 userId，最好只接受认证上下文。

---

## C3. 上传接口无鉴权 + 全量读内存 + 信任 MIME（L2）★P0

**题目**：`/api/upload/novel-cover`、`/background`、`/idea-image`、`/note-image` 都没有认证；`_do_upload` 先 `file.file.read()` 再判断大小。请列出至少 4 个问题及修复。

**材料**：

```python
content = file.file.read()
if len(content) > MAX_SIZE:
    return Result.error("文件大小不能超过10MB")
...
ext = _type_to_ext(file.content_type)
```

**参考答案**：

1. **无鉴权**：任何人可上传，占用磁盘/CDN；可上传大量图片做存储滥用。
2. **全量读内存**：先读整个文件再判大小，攻击者传 2GB 直接 OOM；应在读之前检查 `Content-Length`，并分块读、累计计数，超限即断。
3. **信任 `Content-Type`**：客户端可伪造 `image/png` 上传任意内容；应校验 magic bytes（`imghdr`/Pillow）并重新编码。
4. **删除无归属校验**：`delete_cover(url, novelId)` 不校验 novel 是否属于当前用户；可清掉他人封面引用。
5. **静态目录公开**：`/api/uploads` 直接挂载，上传的 HTML/SVG 可能被浏览器执行（若允许）；只允许图片并设 `Content-Disposition`/`X-Content-Type-Options`。
6. **MD5 去重可探测**：已知文件可判断是否上传过；低风险，但要注意隐私。
7. **路径**：`_do_delete_file` 只取 basename，暂时没有穿越；但 `delete_file_by_url` 的目录推断逻辑只覆盖 covers/backgrounds，其他目录会误删/不删。

**修复**：

```python
@router.post("/novel-cover")
async def upload_cover(file: UploadFile, user_id=Depends(get_current_user_id)):
    ...
# 流式读取
size = 0
while chunk := await file.read(64 * 1024):
    size += len(chunk)
    if size > MAX_SIZE: return Result.error("...")
    hasher.update(chunk); buf.write(chunk)
# magic bytes
from PIL import Image
Image.open(BytesIO(buf)).verify()
```

**验证**：无 token → 401；传 20MB → 413/业务错误且内存不飙；传 `.html` 改名 `.png` → 拒绝；用户 A 删用户 B 的封面 → 403。

**解析**：上传是评测岗高频攻击面；要同时看认证、资源、内容、存储四条线。

**评分**：4 个问题各 1；修复 1；验证 1。

**追问**：MD5 去重有什么安全风险？→ 可做"文件存在性"侧信道；敏感文件不建议用可预测哈希做去重键。

---

## C4. 重新生成接口路径穿越（L3）★P0

**题目**：`/chat/stream` 对 `session_id` 做了正则校验，但 `/chat/regenerate` 没有；`_chain_dir` 直接 `os.path.join(..., session_id)`。请构造攻击并修复。

**材料**：

```python
_SESSION_ID_RE = re.compile(r"^[a-f0-9\-]{8,64}$")

def _chain_dir(user_id: int, session_id: str) -> str:
    return os.path.join(CHAT_STORAGE_PATH, "chat", str(user_id), session_id)

# regenerate
chain_dir = _chain_dir(user_id, req.session_id)
os.makedirs(chain_dir, exist_ok=True)
```

**参考答案**：

- **攻击**：`sessionId = "../../../../tmp/pwn"`。`os.path.join` 不会阻止 `..`，`makedirs` 可创建任意目录；后续 `save_chain_file`/`truncate_chain` 会在该目录读写 JSON，造成任意路径写入/删除（受进程权限限制）。
- **影响**：P0，路径穿越 + 文件写入/删除；若指向其他用户目录，可读写他人聊天。
- **根因**：只在 stream 分支校验；`_chain_dir` 本身没有约束；`regenerate` 也调用了 `_maybe_summarize`，会继续用恶意目录。
- **修复**：

```python
def _chain_dir(user_id: int, session_id: str) -> str:
    if not _is_valid_session_id(session_id):
        raise ValueError("invalid session_id")
    base = Path(CHAT_STORAGE_PATH, "chat", str(user_id)).resolve()
    target = (base / session_id).resolve()
    if not target.is_relative_to(base):
        raise ValueError("path traversal")
    return str(target)
```

  并在 `/chat/regenerate` 入口、`chat_history` 所有 `session_id` 路由统一校验。返回 400/422，不要静默替换。
- **验证**：

```bash
curl -i -X POST http://localhost:8084/api/chat/regenerate \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"sessionId":"../../../../tmp/pwn","regenerateIndex":0}'
```

断言 400/422，`/tmp/pwn` 不存在；正常 UUID 仍可重新生成。

**解析**：路径穿越要同时看 `join`、`resolve`、`is_relative_to`；只做正则黑名单不够稳。

**评分**：攻击 2；影响 1；修复 2；验证 1。

**追问**：为什么 `os.path.join(base, "/abs")` 会逃逸？→ 第二个参数是绝对路径时，`join` 直接返回它。`Path(base) / "/abs"` 同理。

---

## C5. 并发写链文件：丢消息/断链（L3）★P1

**题目**：两个请求同时向同一会话追加消息，`save_chain_file` 没有锁。请描述可能的结果，并给出 Python/Java 两端的修复。

**材料**：

```python
def save_chain_file(chain_dir: str, messages: list[dict]) -> str:
    fname = _make_filename()
    ...
    with open(os.path.join(chain_dir, fname), "w", encoding="utf-8") as f:
        json.dump(data, f, ...)
    # 再把 tail.next 指向 fname
```

**参考答案**：

- **竞态 A：断链**。两个请求都读到同一个 tail，各自写新文件 F1/F2，然后各自把 tail.next 指向自己的文件；后写覆盖先写，F1 或 F2 成为孤儿，消息丢失。
- **竞态 B：同秒同名**。`_make_filename` 用时间戳+随机；随机空间足够时不易碰撞，但测试 mock 随机/时钟回拨时可能覆盖。
- **竞态 C：读半截**。写文件不是原子操作，读请求可能读到未写完的 JSON，`_parse_chain_file` 解析失败，返回空链。
- **竞态 D：DB 与文件不一致**。文件写完、`_upsert_session` 前进程崩溃，DB 仍指向旧 head，新消息不可见。
- **修复（Python）**：
  1. 进程内按 `(user_id, session_id)` 加 `threading.Lock`；多进程/多实例用文件锁 `fcntl.flock` 或 Redis 分布式锁。
  2. 写临时文件 + `os.replace` 原子替换；`tail.next` 的更新也走临时文件。
  3. 先写新文件，再原子更新 tail.next；最后更新 DB；失败可重试/对账。
  4. 读链时对 JSON 解析失败做重试（短暂），并记录损坏文件。
- **修复（Java）**：`ChatContentFileService` 已有 `synchronized(getLock(userId, sessionId))`，但只覆盖 `append`；`truncateChain`、`replaceMessageInChain`、`deleteChain` 也要同一把锁，且写文件用 `Files.move(tmp, target, ATOMIC_MOVE)`。
- **验证**：用 `xargs -P 20` 并发发 20 条消息；断言链文件消息数=20、无孤儿文件、每个 `next` 可达；kill -9 在写文件中，重启后链可读。

**解析**：文件型存储的并发是评测岗高频深挖点。要能说出"锁范围"和"原子写"两件事。

**评分**：两种竞态各 1.5；修复 2；验证 1。

**追问**：`synchronized` 能跨实例吗？→ 不能，只保证单 JVM；多实例要分布式锁/DB 乐观锁。

---

## C6. 摘要逻辑丢历史（L3）★P0

**题目**：`_maybe_summarize` 在消息 ≥12 时总结 `messages[:6]`，写 `lastMessageIndex=len(messages)`，然后 `truncate_chain(chain_dir, 6)`。请指出数据丢失路径，并给出正确算法。

**材料**：

```python
to_summarize = messages[:6]
...
write_summary(chain_dir, new_summary, len(messages))
new_fname = truncate_chain(chain_dir, 6)
```

**参考答案**：

- **第一次触发**（假设 12 条）：总结第 1-6 条，`lastMessageIndex=12`；`truncate_chain(...,6)` 保留第 1-6 条。第 7-12 条**既没进摘要，也被删除** → 直接丢失。
- **后续触发**：链只剩 6 条，`len - last_idx = 6 - 12 < 6`，永远不再总结；直到消息涨到 18，`18-12=6`，又总结 `messages[:6]`（还是原来的 1-6），写 `last_idx=18`，再截到 6；第 7-18 条再次丢失。
- **根因**：摘要区间和截断区间不一致；`lastMessageIndex` 写成"总消息数"而不是"已摘要到的索引"。
- **正确算法**：

```python
start = last_idx
end = min(start + 6, len(messages))
to_summarize = messages[start:end]
new_last = end
write_summary(chain_dir, new_summary, new_last)
truncate_chain(chain_dir, new_last)   # 保留已摘要的前缀 + 未摘要的后缀？需要按设计
```

  更稳的设计：**摘要只追加，不立即删除原文**；或保留"摘要 + 最近 N 条"，删除 `[0:new_last]`，并确保 `new_last` 与删除边界一致。
- **验证**：造 20 条消息，触发两次摘要；断言摘要内容覆盖 1-12 条、链中保留 13-20 条（或按设计保留最近 N 条）、无消息既不在摘要也不在链；重启后 `lastMessageIndex` 与链长度一致。

**解析**：这是"总结导致数据丢失"的经典 off-by-design。评测时要能画出消息区间图。

**评分**：第一次丢失 2；后续丢失 1；根因 1；正确算法 2。

**追问**：为什么 `except Exception: pass` 让问题更难发现？→ 摘要失败静默，链仍可能被截断/不截断，状态不可观测；至少记日志 + 指标。

---

## C7. 章节冲突检测的"成功包裹失败"（L2，易误判）

**题目**：`save_content` 检测到冲突时返回 `Result.success("存在冲突", {"hasConflict": True, ...})`，HTTP 200、`code=200`。这是 bug 吗？请分析调用方风险与改进。

**材料**：

```python
if conflict["hasConflict"] and not req.force:
    return Result.success("存在冲突", {"hasConflict": True, ...})
```

**参考答案**：

- **不一定是 bug**：这是"业务分支用 200 包裹"的契约；前端 `NovelEditorView` 会检查 `res.data.hasConflict` 并弹冲突提示，当前主链路可用。
- **风险**：任何只看 `code===200` 的调用方（脚本、第三方、未来的移动端）都会把冲突当保存成功，继续覆盖或误报；`force=true` 也没有审计/权限区分。
- **改进**：
  1. 冲突返回 `Result.error` 或明确 `code=409`，`data` 带 serverVersion/serverHash；前端按 409 处理。
  2. 若必须保持 200，至少在 API 文档/类型里标 `hasConflict` 为必检字段，并提供 `saveContent` 封装，禁止裸调。
  3. `force` 需要记录操作者/时间/原因，避免静默覆盖。
- **验证**：两个客户端同时改同一章；后保存者收到冲突；断言不覆盖、提示版本差异；`force=true` 后断言覆盖且审计日志存在。

**解析**：这是"易误判"题：代码看起来返回成功，但业务语义是失败。评测报告要写"契约风险"而不是直接 P0。

**评分**：判断 2；风险 2；改进 1.5；验证 0.5。

**追问**：`hasConflict` 为 true 时，`code=200` 会让 axios 拦截器做什么？→ 原样 resolve；调用方必须自查 `data.hasConflict`。

---

## C8. Rerank 端点写错，静默回退（L2）★P0/P1

**题目**：`knowledge_search_tool._rerank_results` 调用 `http://localhost:8085/api/rerank`，但 RAG 服务真实端点是 `/api/rag/rerank`。请说明为什么线上"看起来正常"，以及如何发现和修复。

**材料**：

```python
resp = httpx.post(f"{reranker_url}/api/rerank", json={...}, timeout=10)
...
except Exception as e:
    log.warning("Reranker 不可用，使用向量检索原始排序: %s", e)
return list(range(len(documents)))
```

**参考答案**：

- **现象**：404 不是异常（`httpx.post` 默认不 `raise_for_status`），`resp.status_code != 200`，函数直接走到 `return list(range(...))`，**不抛异常、不告警**；回答仍能生成，只是没有精排。
- **影响**：检索质量下降，评测集上的 recall/nDCG 变差；日志没有 warning（因为没进 except），极难发现。
- **发现**：开 DEBUG 日志看请求 URL；`curl -i` 两个路径对比；在 RAG 服务加 access log；对 `status_code != 200` 记 warning + 指标。
- **修复**：改成 `/api/rag/rerank`；统一从配置读 `RERANKER_URL`，不要硬编码；`resp.raise_for_status()`；失败时返回原始排序但**必须**记 warning/指标；加契约测试。
- **验证**：

```bash
curl -i -X POST http://localhost:8085/api/rag/rerank \
  -H 'Content-Type: application/json' \
  -d '{"query":"测试","documents":["a","b"]}'
```

断言 200 且返回 `results`；再 mock 8085 返回 500，断言日志有 warning、检索仍可用。

**解析**：这是"静默降级"的典型。评测岗要能区分"功能可用"和"功能按设计工作"。

**评分**：根因 2；影响 1；发现 1.5；修复 1.5。

**追问**：`httpx.post` 404 会抛异常吗？→ 不会；只有网络错误/超时抛，HTTP 状态码要显式检查。

---

## C9. 三套 Chroma 路径，检索和统计看的不是同一个库（L2）★P1

**题目**：主后端 `rag.py` 默认 `./storage/vectordb_4060`，`knowledge_search_tool.py` 默认 `./chroma_db`，RAG 8085 通过 Chroma Server 8000 访问 `storage/vectordb_4060`。请说明后果与统一方案。

**参考答案**：

- **后果**：
  - `/api/rag/stats`、`/api/rag/documents` 读 `storage/vectordb_4060`；
  - 聊天里的 `knowledge_search` 读 `./chroma_db`；
  - 两个目录内容不同 → 统计显示有 1000 条，聊天检索却 0 条；或反之。
  - 8085 走 Server 8000，主后端走本地 PersistentClient，**同一 collection 名但不同实例**，写入/读取可能不一致。
- **根因**：默认值分散、没有唯一配置源；`CHROMA_PERSIST_DIR` 环境变量未在所有入口统一。
- **统一方案**：
  1. 只保留一个配置源（如 `config.py` 的 `CHROMA_PERSIST_DIR` / `CHROMA_HOST`），其他模块 import。
  2. 明确部署模式：**Server 模式**（8000）或 **嵌入式模式**（本地目录），不要混用。
  3. 启动时打印实际路径/URL + collection + count；健康检查返回这些字段。
  4. 迁移时做 count 对账。
- **验证**：同一 query 分别走 `/api/rag/search` 和聊天 `knowledge_search`，断言 topK 文档 ID 一致；`/api/rag/stats` 的 count 与 8085 `/api/rag/stats` 一致。

**解析**：RAG 系统"检索不到"经常不是模型问题，而是连错库/连错 collection。

**评分**：后果 2；根因 1.5；统一方案 1.5；验证 1。

**追问**：collection 名相同就一定是同一个库吗？→ 不是；不同 Chroma 实例/目录下同名 collection 互不相通。

---

## C10. Java `permitAll` + `userId=1L` 默认值（L1）★P0

**题目**：Java `SecurityConfig` 对 `/novel/**`、`/chat/**`、`/rag/**` 等全部 `permitAll`；`NovelController.create/update/delete` 在 `userId==null` 时默认 `1L`。请说明组合风险。

**材料**：

```java
.requestMatchers("/user/**","/userConfig/**","/novel/**","/auth/**","/chat/**",
  "/novelCharacter/**","/timeline/**","/storyNode/**","/upload/**","/uploads/**","/rag/**","/error").permitAll()
```

```java
if (userId == null) userId = 1L;
```

**参考答案**：

- **认证形同虚设**：Spring Security 不拦，JWT filter 即使不设置 `userId`，Controller 仍可被匿名调用。
- **默认用户 1**：匿名创建/更新/删除会以 userId=1 执行；攻击者可删除/篡改 1 号用户的作品，或把内容写进 1 号用户。
- **读取**：`GET /novel/{id}` 没有归属校验，匿名可枚举全部小说。
- **修复**：
  1. 只放行 `/auth/**`、`/uploads/**`（静态）等真正公开路径；业务路径全部 `authenticated()`。
  2. 删除 `userId=1L` 默认值；`userId==null` 直接 401。
  3. Service 层做归属校验；不要只依赖 token 里的 userId。
  4. 如果保留 JWT filter 的 `@RequestAttribute`，确保未认证时不会注入。
- **验证**：无 token `POST /api/novel/create` → 401；用户 A token 删用户 B 小说 → 403；匿名 `GET /api/novel/1` → 401。

**解析**：这是"安全配置 + 兜底默认值"的叠加灾难；单看每一行都像"开发方便"，组合起来是 P0。

**评分**：permitAll 2；默认值 2；修复 1；验证 1。

**追问**：`permitAll` 后 JWT filter 还会执行吗？→ 会，但认证失败不阻断；Controller 仍可能拿到 null 或匿名 principal。

---

## C11. Java 链文件 `next` 写全路径，与 Python 不兼容（L2）★P1

**题目**：Python 约定 `next` 存纯文件名，基于当前文件父目录解析；Java `append` 把 `newPath`（`storage/chat/.../file.json`）写进 `next`，`readChain` 直接 `new File(current)`。请说明跨后端后果与修复。

**材料**：

```java
String newPath = dirPath + "/" + System.currentTimeMillis() + "_" + ... + ".json";
...
tail.put("next", newPath);
```

**参考答案**：

- **Java 内部可用**：`newPath` 是相对工作目录的完整路径，`new File(current)` 能打开；但一旦换工作目录/容器路径就失效。
- **跨后端不兼容**：
  - Java 写的链给 Python 读：Python 用 `parent.resolve(next)`，`next` 是 `storage/chat/...`，拼成 `parent/storage/chat/...`，找不到文件，链在第 1 个文件后断。
  - Python 写的链给 Java 读：`next` 是纯文件名，`new File("178...json")` 相对 JVM 工作目录，通常找不到，链断。
- **影响**：切换后端/迁移数据后历史消息丢失；重新生成截断错误。
- **修复**：统一契约——`next` 只存文件名；Java `readChain` 用 `Paths.get(current).getParent().resolve(next)`；`append` 写 `Paths.get(newPath).getFileName().toString()`；迁移脚本把存量全路径归一化。
- **验证**：造一条 Java 链、一条 Python 链，互相读取；断言消息数一致；`next` 字段不含 `/`；切换工作目录后仍可读。

**解析**：这是"文件格式契约"题，不是简单的路径 bug。评测时要看跨语言/跨部署。

**评分**：Java 内部可用 1；两个方向不兼容 2；修复 1.5；验证 0.5。

**追问**：为什么存全路径在容器里更危险？→ 容器工作目录/挂载点变化，绝对/相对路径都可能失效；纯文件名 + 父目录最稳。

---

## C12. Java SSE：每请求一个线程池 + 无超时/无回调（L3）★P1

**题目**：Java `/chat/stream` 每个请求 `Executors.newSingleThreadExecutor()`，内部 `latch.await()` 无超时，`sendEvent` 吞异常，未注册 `onTimeout/onCompletion/onError`。请分析资源与生命周期问题。

**参考答案**：

- **线程池泄漏**：每请求创建一个池，正常路径 `finally executor.shutdown()`；但如果 `executor.execute` 前抛异常、或 `shutdown` 被跳过，池不会回收。高并发下线程数暴涨。
- **`latch.await()` 无超时**：AI 流不结束/网络挂起，线程永久阻塞；`SseEmitter` 的 30 分钟超时只触发容器回调，不会自动打断 `latch`。
- **无 `onTimeout`**：客户端断开/超时后，Flux 仍可能继续跑，继续 `sendEvent`（被吞），浪费 token。
- **`sendEvent` 吞异常**：客户端断开时 `emitter.send` 抛 `IOException`，被 `catch (Exception ignored)` 吞掉，业务不知道连接已断，不会取消上游。
- **无 `onCompletion/onError`**：没有统一清理/落盘/取消逻辑。
- **修复**：
  1. 用共享的 `ThreadPoolTaskExecutor`/`ExecutorService`，不要每请求新建。
  2. `latch.await(timeout, TimeUnit)`；超时 `emitter.complete()` + 取消 `Disposable`。
  3. `SseEmitter` 注册 `onTimeout`/`onCompletion`/`onError`，统一 `disposable.dispose()`。
  4. `sendEvent` 失败要抛出/记录并触发取消，不要静默。
  5. 用 WebFlux `Flux<ServerSentEvent>` 更自然，避免 Servlet 线程桥接。
- **验证**：50 并发流式请求，观察线程数/堆；客户端 5s 断开，断言上游在 1s 内取消、无后续 token；AI 端挂起，断言 30s 超时并释放线程。

**解析**：SSE 的难点是"客户端断开"和"上游取消"的联动；只 `emitter.complete()` 不够。

**评分**：线程池 1.5；latch 1.5；回调/吞异常 2；修复 1；验证 1。

**追问**：`SseEmitter` 超时后会自动调用 `onCompletion` 吗？→ 通常触发 `onTimeout`，完成/异常回调时机要看容器；不要假设一定有序，清理要幂等。

---

## C13. Java 重新生成先截断后生成（L2）★P1

**题目**：Java `/chat/regenerate` 在流开始前就 `truncateSessionChain(...)`；Python 版延迟到保存前。请说明用户点"停止"或 AI 失败时的差异。

**参考答案**：

- **Java**：先截断 → 旧回答已从链中删除；如果 AI 调用失败/用户取消，新回答没有落盘，链里只剩截断后的历史，**旧回答永久丢失**。
- **Python**：先流式生成，成功/异常/取消时在 `_save_reply` 里才截断+追加；取消时把已流出部分落盘，旧回答放 `paired` 存档，数据不丢。
- **影响**：Java 版重新生成是"高风险操作"，网络抖动即可丢回答。
- **修复**：延迟截断到保存阶段；或先备份旧链（`head.bak`），失败时回滚；用事务/临时文件保证"截断+追加"原子。
- **验证**：Java 版点重新生成后立即停止；断言旧回答仍在/可恢复；模拟 AI 500，断言链未丢消息。

**解析**：这是"操作顺序"导致的数据安全 bug；评测时要画时序图。

**评分**：差异 2；影响 1.5；修复 1.5；验证 1。

**追问**：延迟截断后，`regenerateIndex` 的语义要不要变？→ 要明确"截断到第 N 条（不含）"还是"保留前 N 条"；前后端必须一致。

---

## C14. Java 不识别 `__file__` 引用（L2）★P1

**题目**：Python 把 `head_path`、`custom_bgs`、`font_colors_json` 存成 `__file__:chat/...`；Java 直接 `new File(headPath)` / 把 `customBgs` 原样返回。请说明后果与修复。

**参考答案**：

- **链读取**：`ChatSessionServiceImpl.getSessionMessages` → `fileService.readChain(session.getHeadPath())`；`headPath="__file__:chat/1/s/xxx.json"`，`new File(...)` 不存在，返回空列表。用户看到"历史消息全没了"。
- **用户配置**：Java `UserConfigController.getBackgroundConfig` 直接返回 `customBgs` 字符串 `"__file__:user/customBgs/4.json"`；前端 `JSON.parse` 失败，背景列表为空/报错。
- **根因**：Java 没有实现 Python 的 `StorageService` 引用解析约定；两套后端共享 DB 但文件格式契约不一致。
- **修复**：
  1. Java 增加 `StorageService.loadJson(subdir, id, dbValue)`：识别 `__file__:` 前缀，读 `storage/...` 文件；兼容旧 JSON 字符串。
  2. `readChain` 前先解析 headPath；写回时保持 `__file__:` 前缀。
  3. 用户配置返回前把文件内容反序列化为 JSON 字符串/对象，与 Python 契约一致。
  4. 加跨后端契约测试（同一 DB、同一 storage，Python 写 Java 读）。
- **验证**：Python 创建会话 → 切 Java → 读历史，断言消息数一致；Python 存自定义背景 → Java 读，断言前端能 `JSON.parse`。

**解析**：这是"共享存储、双实现"的典型契约裂缝；评测时要跨后端验证，不能只看单端。

**评分**：链 2；配置 2；修复 1.5；验证 0.5。

**追问**：只把 `__file__:` 去掉就够吗？→ 不够；还要按 `storage` 根目录解析相对路径，并处理旧数据（纯 JSON 字符串）。

---

## C15. 前后端/双后端契约漂移（L2）★高频

**题目**：列出本项目中至少 5 处 Python/Java/前端契约不一致，并说明如何建立"单一契约源"。

**参考答案**：

| # | 契约点 | Python | Java | 前端 |
|---|---|---|---|---|
| 1 | 分页参数 | `page_size` | `pageSize` | 发 `pageSize` |
| 2 | 链 `next` | 纯文件名 | 全路径 | 不感知 |
| 3 | `__file__` 引用 | 支持 | 不支持 | 不感知 |
| 4 | SSE 错误字段 | `{type:"error", message}` | `{type:"error", delta}` | 读 `data.message` |
| 5 | 聊天落盘 | 流结束写链 | `/chat/stream` 不写链 | 不写 |
| 6 | 用户配置 | 文件引用 + JSON 字符串 | 原样返回 DB 字符串 | `JSON.parse` |
| 7 | 重新生成 | 延迟截断 | 先截断 | 同一套 UI |

- **后果**：前端"有时好有时坏"，取决于连的是哪个后端；评测结论不可复现。
- **单一契约源**：
  1. OpenAPI/JSON Schema 由一方生成，前后端 CI 校验；或手写 `contracts/` 并加测试。
  2. 前端 API 层按后端适配，不在组件里散落参数名。
  3. 双后端跑同一套契约测试（登录→小说→角色→聊天→RAG）。
  4. 在 README 明确"当前主后端是谁"，Java 只作为兼容目标。
- **验证**：同一组 curl 分别打 8084（Python）和 Java；断言响应字段/分页/错误结构一致；前端切后端不改代码。

**解析**：这是评测岗的核心能力：不是找单个 bug，而是找"系统性不一致"。

**评分**：5 处各 1；单一契约源 2；验证 1。

**追问**：为什么"前端加兼容 `res.data?.records || res.data`"不是好方案？→ 把契约差异扩散到每个调用点，无法根治；应在 API 层集中适配。

---

## C16. 依赖双清单版本漂移（L2）★P1

**题目**：`DixyangFast` 同时有 `pyproject.toml`（范围）和 `requirements.txt`（固定），且版本差距很大（如 `langchain-openai>=1.3` vs `==0.2.6`）。请说明风险与治理。

**参考答案**：

- **风险**：`uv run` 按 `pyproject`/`uv.lock` 解析，`pip install -r requirements.txt` 按旧 pin；两种启动方式得到不同 LangChain/Chroma 运行时，出现"我这能跑你那不能跑"、工具调用/SSE 行为差异。
- **具体**：`langchain-openai` 1.x 与 0.2.x 的 API/默认参数不同；`chromadb` 1.5 与旧版客户端协议不同；RAG 检索结果可能变化。
- **治理**：
  1. 选定唯一入口：`uv sync --frozen`（以 `uv.lock` 为准）；`requirements.txt` 由 `uv export` 生成，不手改。
  2. CI 用 lockfile 安装并跑测试；禁止 `pip install -r` 与 `uv run` 混用。
  3. 依赖升级用 PR + 回归（登录/聊天/RAG/上传）。
  4. 在 README 写清"用哪个命令安装"。
- **验证**：干净容器分别用两种方式安装，`pip freeze` 对比；跑同一套 `tests/api_test.sh`，断言结果一致。

**解析**：可复现性是评测的底线；依赖漂移会制造大量假 bug。

**评分**：风险 2；具体影响 1.5；治理 1.5；验证 1。

**追问**：`uv.lock` 需要提交吗？→ 应用项目应提交，保证可复现；库项目可不定。

---

## C17. 现有 API 测试脚本不可信（L2）★P1

**题目**：`tests/api_test.sh` 用 `admin/123456` 登录，但文档测试账号是 `admin123/123456`；断言只 grep `"code":200`；`NOVEL_ID` 用 `sed` 从整个响应抓第一个 `"id"`。请列出问题及改进。

**参考答案**：

1. **账号错**：`admin` 可能不存在/密码不同，脚本第一步就失败；应读环境变量 `TEST_USER/TEST_PASS`，默认 `admin123/123456`。
2. **断言太弱**：只匹配字符串 `"code":200`，不校验 `data` 结构/字段；业务成功但数据为空也会过。
3. **ID 解析错**：`sed 's/.*"id":\([0-9]*\).*/\1/'` 贪婪匹配，可能抓到 `userId`/`novelId` 等最后一个 `id`；应用 `jq -r '.data.id'`。
4. **无失败即停**：没有 `set -euo pipefail`；中间失败仍继续，最后统计可能掩盖。
5. **无清理/幂等**：`testapi2` 重复注册会失败；失败时残留测试小说/角色。
6. **无负向用例**：未测 401/403/越权/路径穿越/非法分页。
7. **依赖真实 AI/DB**：不可重复；应分层：契约测试 mock、集成测试单独跑。
8. **RAG 断言假阳性**：`/api/rag/search` 返回 `code=200` 但 `results=[]` 也会过；应断言非空/字段。
- **改进**：`set -euo pipefail`；`jq` 解析；唯一后缀；`trap cleanup EXIT`；正向+负向；CI 分 suite；输出 JUnit/JSON 报告。
- **验证**：故意让登录失败，脚本必须非 0 退出；让创建返回 `code=500`，断言失败；重复跑两次结果一致。

**解析**：测试脚本本身也是评测对象；"测试通过"不等于"功能正确"。

**评分**：4 个问题各 1；改进 1；验证 1。

**追问**：为什么只 grep `"code":200` 会漏掉"返回空列表"？→ 空列表也是成功；要断言业务字段/数量/不变量。

---

## C18. Redis 浏览增量回写丢数据（L3）★P1

**题目**：`idea_cache.flush_views` 先 `view_take(pid)` 从 Redis 原子取走增量，再写 DB，最后统一 `db.commit()`。如果 DB 提交失败/进程崩溃，会怎样？如何修复？

**材料**：

```python
delta = self.view_take(pid)      # Redis 中已删除
p = db.get(IdeaPost, pid)
p.view_count += delta
...
db.commit()
```

**参考答案**：

- **丢增量**：`view_take` 已把 Redis 计数清零；若 `db.commit()` 失败/进程在 commit 前崩溃，这部分浏览数永久丢失。
- **部分成功**：一次 flush 多个 pid，某个 `db.get` 抛异常会跳到 finally，前面已 `take` 的增量也没提交（取决于事务），全部丢。
- **重复/少算**：如果先 commit 再删 Redis，崩溃会重复计数；当前是"先删后 commit"，偏丢失。
- **修复（按一致性取舍）**：
  1. **至少一次**：先 DB commit，再删 Redis；用幂等键/版本避免重复（如 `view_flush:{pid}:{batch}` 记录已处理批次）。
  2. **可恢复**：`view_take` 改为 `view_peek` + 处理成功后 `decrby` 相同值；失败保留。
  3. **事务/批量**：每个 pid 独立事务，失败只影响该 pid；记录失败队列重试。
  4. **对账**：定期从访问日志/DB 校准，监控 `Redis pending` 与 `DB view_count` 差异。
- **验证**：mock DB commit 抛异常，断言 Redis 增量仍在/可重试；连续 flush 两次，断言不重复计数；kill -9 在 commit 前，重启后增量不丢。

**解析**：缓存与 DB 的"双写"没有完美方案，必须明确"至少一次/至多一次"和幂等策略。

**评分**：丢数据 2；部分成功 1；修复 2；验证 1。

**追问**：为什么"先 commit 再删 Redis"能避免丢失但可能重复？→ 崩溃窗口在 commit 后、删 Redis 前；重试会再加一次；需要幂等/批次号。

---

## C 卷自评表

| 题 | 得分 | 错因 | 是否 P0 | 补做 |
|---|---:|---|---|---|
| C1 |  |  |  |  |
| C2 |  |  |  |  |
| C3 |  |  |  |  |
| C4 |  |  |  |  |
| C5 |  |  |  |  |
| C6 |  |  |  |  |
| C7 |  |  |  |  |
| C8 |  |  |  |  |
| C9 |  |  |  |  |
| C10 |  |  |  |  |
| C11 |  |  |  |  |
| C12 |  |  |  |  |
| C13 |  |  |  |  |
| C14 |  |  |  |  |
| C15 |  |  |  |  |
| C16 |  |  |  |  |
| C17 |  |  |  |  |
| C18 |  |  |  |  |

**合格线**：75/100。C1/C4/C6/C10 是 P0，必须能独立写出攻击/数据丢失路径与修复。

---

*上一卷：[笔试 B · 前端代码审查](./02-笔试B-前端代码审查.md) ｜ 下一卷：[笔试 D · 评测设计与 Rubric](./04-笔试D-评测设计与Rubric.md)*
