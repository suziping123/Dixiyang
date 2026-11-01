# 03 · Python 与 FastAPI 后端

> **定位**：覆盖 Python 运行时、异步并发、FastAPI 请求链路、数据层、鉴权、文件/缓存与部署，重点训练"能读、能调、能审、能复现"。
> **层级**：L1-L7
> **对应岗位能力**：接口契约审查、后端缺陷定位、鉴权/越权判断、并发与事务分析。


> **来源约定**：未标来源的段落为通用技术知识；标 `[项目]` 的有仓库代码/脚本/文档依据；`[项目-冲突]` 表示材料互相矛盾；`[推断]`/`[待确认]` 表示分析或尚需验证。

---

## 1. Python 运行时与对象模型

### 1.1 解释执行与导入

```text
python main.py
 → 找到解释器（版本/虚拟环境）
 → 编译为字节码（.pyc 缓存）
 → 逐条执行
 → import 模块：查找 sys.path → 执行模块顶层代码 → 缓存到 sys.modules
```

**工程含义**：

- `import` 会执行模块顶层代码；重依赖/副作用应延迟到函数内或 `lifespan`。
- `sys.path`、工作目录、包安装位置决定能否导入；`uv run`/虚拟环境可减少"我这里能跑"。
- 循环导入常见于路由/模型互相引用；用字符串注解、局部导入、拆分模块解决。

### 1.2 名字、对象、引用

```python
a = [1, 2]
b = a
print(a is b)        # True
b = b + [3]          # 创建新列表
print(a)             # [1, 2]
b.append(4)
print(a)             # [1, 2]
```

- 变量是名字，指向对象；`is` 比较身份，`==` 比较值。
- 函数参数是"对象引用按值传递"：修改可变对象会影响调用方，重新绑定不会。
- 默认参数在函数定义时求值一次；可变默认参数是经典坑（见 01 卷）。

### 1.3 异常与资源

```python
try:
    f = open(path, encoding="utf-8")
    data = f.read()
finally:
    f.close()
```

更推荐：

```python
with open(path, encoding="utf-8") as f:
    data = f.read()
```

- `with` 保证异常时也释放资源。
- 数据库 Session/事务、锁、临时文件、HTTP 连接都应有明确生命周期。
- 不要用裸 `except:`；捕获具体异常，保留原始 traceback（`raise ... from e`）。

### 1.4 垃圾回收

- 引用计数为主，循环引用由分代 GC 处理。
- 全局缓存、闭包、事件监听、未关闭连接会让对象长期存活。
- `__del__` 不可靠；资源释放用上下文管理器/显式 close。

---

## 2. 类型、装饰器、生成器、上下文管理器

### 2.1 类型标注

```python
from typing import Protocol

class Repository(Protocol):
    def get(self, id: int) -> dict | None: ...

def load(repo: Repository, id: int) -> dict:
    item = repo.get(id)
    if item is None:
        raise LookupError(id)
    return item
```

- 标注是给工具/读者看的，不强制运行时；边界用 Pydantic 校验。
- `Optional[T]` 等价 `T | None`（3.10+）。
- `Protocol` 做结构化接口，便于替换实现/测试。
- 避免 `Any` 扩散；外部数据先 `unknown` 式校验再收窄。

### 2.2 装饰器

```python
import functools

def retry(times: int = 3):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for _ in range(times):
                try:
                    return fn(*args, **kwargs)
                except (TimeoutError, ConnectionError) as e:
                    last = e
            raise last
        return wrapper
    return deco
```

- 装饰器会改变函数身份/签名；`functools.wraps` 保留元信息。
- FastAPI 依赖、鉴权、限流常用装饰器/依赖实现；不要隐藏事务边界和异常。
- 重试装饰器只能包可重试、幂等的操作。

### 2.3 生成器与流式

```python
def iter_chunks(text: str, size: int = 1000):
    for i in range(0, len(text), size):
        yield text[i:i + size]
```

- 生成器惰性求值，适合大文件、SSE、批处理。
- 只能消费一次；需要重复遍历要物化。
- 生成器里的异常会在迭代时抛出；流式接口要处理客户端断开。

### 2.4 上下文管理器与事务

```python
from contextlib import contextmanager

@contextmanager
def session_scope(SessionLocal):
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

**事务边界原则**：

- 一个业务用例一个事务；不要在 DAO 的每个方法里自动 commit。
- 先完成所有写操作，再 commit；commit 失败要回滚并转成明确错误。
- 外部调用（发邮件、调 LLM）不要放在长事务里，避免锁持有过久。

---

## 3. 同步、异步、并发

### 3.1 GIL

- CPython 同一进程同一时刻通常只有一个线程执行 Python 字节码。
- I/O 等待会释放 GIL；CPU 密集多线程不能线性加速。
- 多进程绕过 GIL，但有序列化/内存/启动开销。

### 3.2 `async def` 不是自动异步

```python
@app.get("/items")
async def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()   # 同步阻塞！
```

- `async def` 路由运行在事件循环；内部同步 DB/文件/HTTP 会阻塞其他请求。
- 解决：
  1. 用异步驱动/客户端（`asyncpg`、`httpx.AsyncClient`、`aiofiles`）；
  2. 把同步调用丢到线程池：`await run_in_threadpool(fn, ...)` / `asyncio.to_thread`；
  3. 路由改成普通 `def`，FastAPI 会在线程池执行（但线程池有限）。
- 不要在高并发路径里 `time.sleep`、`requests.get`、读取大文件。

**项目对照**：

- Python 主后端大量 `async def` 路由使用同步 SQLAlchemy Session；低并发可用，高并发会占住事件循环。[项目-风险]
- Java SSE 每请求新建线程池且无超时，属于另一种资源模型问题。[项目]

### 3.3 并发模型选择

| 场景 | 选择 | 说明 |
|---|---|---|
| 高并发网络 I/O | asyncio + 异步库 | 连接多、每请求等待多 |
| 阻塞库/驱动 | 线程池 | 隔离阻塞，限制池大小 |
| CPU 密集 | 多进程/任务队列 | 避免 GIL |
| 后台任务 | 队列/worker | 请求内只入队，不阻塞响应 |
| 定时任务 | 调度器/ Cron | 防重复执行/分布式锁 |

### 3.4 超时、取消、背压

```python
import asyncio

async def fetch(client, url):
    async with asyncio.timeout(5):
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
```

- 所有外部调用设超时；超时预算应小于上游超时。
- 客户端断开后，SSE/流式生成器要停止，避免继续消耗 LLM/DB。
- 队列要有界；满时拒绝/降级，不要无限堆积。
- 重试要有上限、退避、抖动，并只重试可重试错误。

---

## 4. FastAPI 请求链路

### 4.1 从请求到响应

```text
Uvicorn 接收 HTTP
 → 中间件（CORS/日志/鉴权）
 → 路由匹配
 → 依赖注入（DB/当前用户/服务）
 → Pydantic 解析与校验请求体/查询参数
 → 路由函数
 → 序列化响应（response_model）
 → 异常处理器
 → 中间件后置逻辑
 → 返回
```

### 4.2 路由与参数

```python
from fastapi import APIRouter, Depends, Query, HTTPException

router = APIRouter(prefix="/novel", tags=["novel"])

@router.get("/listall")
def list_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user_id: int = Depends(get_current_user_id),
    svc: NovelService = Depends(),
):
    return Result.success(svc.list_all(user_id, page, page_size))
```

- 路径参数/查询参数/请求体分别校验；`ge/le` 限制范围。
- `alias` 处理前后端命名差异（`pageSize` vs `page_size`）。
- 同一接口不要同时接受两种口径却不写清优先级。

### 4.3 依赖注入

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(...):
    ...
```

- `Depends` 可复用鉴权、DB、配置、服务。
- `yield` 依赖在请求结束后清理；异常也会执行 `finally`。
- 依赖不要有隐藏的全局状态；测试时可 `app.dependency_overrides` 替换。
- 依赖链过深会增加理解成本；按领域拆服务。

### 4.4 中间件与异常

```python
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response

@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    logger.exception("unhandled", extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={"code": 500, "msg": "服务器内部错误"})
```

- 中间件顺序影响行为（CORS 要在异常处理前正确配置）。
- 不要把所有异常都转 200；区分 4xx/5xx。
- 生产错误响应不暴露堆栈/SQL/路径；日志保留完整堆栈。
- 统一响应结构要前后端一致：`code/msg/data` 或 `detail`，不能混用。

### 4.5 CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- `allow_origins=["*"]` + `allow_credentials=True` 浏览器不接受通配；应明确来源。
- 预检 `OPTIONS` 要能通过；自定义头（Authorization）要允许。
- CORS 是浏览器策略，不替代后端鉴权。

### 4.6 生命周期

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    close_resources()

app = FastAPI(lifespan=lifespan)
```

- 启动时建表/补列/加载模型；关闭时释放连接/线程池。
- 启动失败要快速失败并输出明确原因，不要带病运行。
- 避免在 import 时做重初始化，影响测试/多 worker。

---

## 5. Pydantic、契约与错误

### 5.1 模型校验

```python
from pydantic import BaseModel, Field, field_validator

class NovelCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = ""

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("标题不能为空")
        return v
```

- Pydantic v2 用 `model_config`、`field_validator`、`model_validator`。
- `extra="forbid"` 可拒绝未知字段，减少契约漂移；但升级要评估兼容性。
- `response_model` 控制输出，防止 ORM 内部字段泄漏。
- `from_attributes=True` 支持从 ORM 对象转换。

### 5.2 命名与分页契约

```python
class Page(BaseModel):
    records: list[NovelVO]
    total: int
    current: int
    size: int
```

**项目坑**：

- 前端部分接口用 `pageSize`，后端部分模型用 `page_size`；`RagKnowledgeView` 用 20 的 pageSize 掩盖了默认 10 的漂移。[项目]
- `GET /novel/listall` 返回分页对象，前端却按数组 unwrap，导致下拉为空。[项目]
- 修复不是"前端猜"，而是 API 层明确类型 + 后端 alias/统一规范 + 契约测试。

### 5.3 统一响应与业务码

```python
class Result:
    @staticmethod
    def success(data=None, msg="成功"):
        return {"code": 200, "msg": msg, "data": data}

    @staticmethod
    def not_found(msg="资源不存在"):
        return JSONResponse(status_code=404, content={"code": 404, "msg": msg, "data": None})
```

**关键**：

- HTTP 状态与业务码都要正确；不能业务失败还 HTTP 200 且监控无感。
- 前端 `unwrap` 必须检查 `code`；后端测试必须断言 `code` 和副作用。
- 错误码表要稳定、可枚举；不要用自然语言当唯一标识。

### 5.4 版本与兼容

- 新增字段通常兼容；删除/改类型/改语义是破坏性变更。
- 需要版本化时用 `/api/v2` 或字段弃用期；不要静默改口径。
- 双后端（Python/Java）并存时，契约必须由测试固定，不能靠"应该一样"。

---

## 6. SQLAlchemy、MySQL 与事务

### 6.1 Session 生命周期

```python
db = SessionLocal()
try:
    user = db.get(User, user_id)
    user.nickname = "new"
    db.commit()
except Exception:
    db.rollback()
    raise
finally:
    db.close()
```

- Session 不是线程安全的；每请求一个 Session。
- 延迟加载在 Session 关闭后会失败；在服务层完成数据组装。
- `expire_on_commit` 影响 commit 后属性访问；注意序列化时机。

### 6.2 事务与并发

```python
try:
    db.begin()
    ...
    db.commit()
except IntegrityError:
    db.rollback()
    raise Conflict("重复数据")
```

- 唯一约束是防重复的最终防线；先查再插有竞态。
- 乐观锁：版本号/`updated_at` 条件更新；更新行数为 0 表示冲突。
- 悲观锁：`SELECT ... FOR UPDATE`，注意死锁/锁等待。
- 长事务会持锁、阻塞、放大回滚成本；外部调用移出事务。

**项目对照**：

- 章节保存冲突检测若返回 200 + 业务失败，前端可能当成功；应使用 409/明确业务码。[项目]
- 聊天链文件多文件写入无锁，两个请求可能交错覆盖；文件系统锁/单写队列/版本号是方向。[项目]

### 6.3 N+1 与索引

```python
# N+1：每个小说查一次作者
novels = db.query(Novel).all()
for n in novels:
    print(n.author.name)
```

解决：`joinedload/selectinload`、批量查询、join。

索引：

- 高频过滤/排序/关联字段建索引；联合索引注意最左前缀。
- 索引不是越多越好：写放大、空间、优化器选择。
- `LIKE '%x%'` 通常无法用普通索引；考虑全文/倒排/向量检索。
- 深分页 `OFFSET` 慢；用 `WHERE id < last_id ORDER BY id DESC LIMIT n`。

### 6.4 建表与迁移

- SQLAlchemy `create_all` 只建缺失表，不改已有表结构。
- 项目用启动时 `inspect` 缺列则 `ALTER` 的补列逻辑；幂等但不如正式迁移可审计。[项目]
- 生产变更应有版本化迁移（Alembic/Flyway）、回滚方案、备份。
- 迁移脚本要能在旧数据上执行；加非空列要有默认值/回填步骤。

### 6.5 SQL 注入与安全

```python
# 错
db.execute(f"SELECT * FROM user WHERE name = '{name}'")

# 对
db.execute(text("SELECT * FROM user WHERE name = :name"), {"name": name})
```

- ORM 表达式/参数绑定优先；动态排序字段要白名单。
- 数据库账号最小权限；应用账号不要 DDL/跨库权限。
- 错误信息不要返回 SQL/表名/堆栈。

---

## 7. 认证、授权与安全

### 7.1 JWT 基础

```text
header.payload.signature
payload: { sub: userId, sid: sessionId, scope: "user", exp: ... }
```

- 服务端验签 + 过期校验；密钥不能硬编码/提交。
- JWT 自包含，撤销需要黑名单/会话号/短期 token + refresh。
- 不要放敏感信息（密码、身份证）到 payload；payload 可被解码。

### 7.2 单点登录与顶号

```text
登录成功 → 生成 session_id → 覆盖写 app_user.session_id → JWT 带 sid
每次请求 → 解 sid → 与 DB 当前 session_id 比对
不匹配 → 401「账号已在其他设备登录」
```

- 会话号存 DB，重启不丢，多后端共享。
- 旧 token 无 `sid` 的兼容策略要明确（本项目兼容放行至过期）。[项目]
- 后台使用独立 `admin_session_id` + `scope=admin`，登后台不顶用户端。[项目]

### 7.3 登录风控

- 10 分钟窗口内第 3 次成功密码登录触发邮箱验证码。[项目]
- 风控计数要原子更新，避免并发绕过；窗口时间统一 UTC。
- 验证码：限流、过期、一次性消费、错误次数限制；不要返回"验证码是否正确"的枚举信息。
- 测试账号频繁登录会触发风控；验证时注意 10 分钟窗口和顶号。

### 7.4 认证 vs 授权

| 检查 | 问题 | 失败码 |
|---|---|---|
| 认证 | 有没有有效 token？ | 401 |
| 角色 | 是否管理员？ | 403 |
| 归属 | 资源是否属于当前用户？ | 403/404 |
| 状态 | 资源是否已删除/冻结？ | 404/409 |

**IDOR**：

```python
# 错：只按 userId 查，未校验当前用户
@router.get("/config")
def get_config(userId: int, current: int = Depends(get_current_user_id)):
    return svc.get_config(userId)

# 对：强制使用当前用户，或校验 owner
@router.get("/config")
def get_config(current: int = Depends(get_current_user_id)):
    return svc.get_config(current)
```

**项目对照**：

- `user_config` 接受任意 `userId`，可越权读写他人配置。[项目]
- 角色/时间线/故事节点部分路由无鉴权，匿名可读写。[项目]
- Java 侧 `permitAll` + 默认 `userId=1L`，匿名请求可能以固定用户执行。[项目]

### 7.5 路径穿越与上传

```python
from pathlib import Path

ROOT = Path("/data/chains").resolve()

def safe_path(user_id: int, session_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", session_id):
        raise ValueError("invalid session")
    p = (ROOT / str(user_id) / session_id).resolve()
    if ROOT not in p.parents:
        raise ValueError("path escape")
    return p
```

- 不要直接拼接用户输入到路径；`resolve()` 后校验是否在根目录内。
- 上传：鉴权、大小限制（先看 `Content-Length`/流式计数）、类型白名单、内容校验、重命名、隔离目录、禁止执行。
- 下载：同样校验归属，不要用用户输入直接做文件名。

**项目对照**：

- `/chat/regenerate` 的 `sessionId` 未严格校验，存在 `../` 路径穿越风险。[项目]
- 上传接口先全量读入内存再校验大小，且无鉴权；应先鉴权 + 流式限制。[项目]

### 7.6 CORS、CSRF、XSS

- CORS 不是鉴权；只是浏览器跨域策略。
- Cookie 认证要防 CSRF：SameSite、CSRF token、Origin/Referer 校验。
- 后端返回 HTML 时防 XSS；前端用 DOMPurify 消毒 Markdown 渲染。[项目]
- 安全响应头：CSP、X-Content-Type-Options、X-Frame-Options、HSTS（按部署）。

---

## 8. 文件、存储与 Redis

### 8.1 大文本文件化

约定：

```text
DB 只存路径/引用，大文本存 JSON 文件
storage/chat/{userId}/{sessionId}/{recordId}.json
DB 字段：__file__:chat/{userId}/{sessionId}/{file}.json
```

- 避免 DB 行过大、备份/查询变慢；文件系统适合追加/大块读写。
- 代价：事务一致性弱、并发写复杂、备份/迁移/权限要单独设计。
- 读取时统一 `StorageService.loadJson` 解析 `__file__:`；不要每处手写路径拼接。

### 8.2 链文件与 `next`

```json
{ "messages": [...], "next": "1783271834717_61b2d203.json" }
```

- `next` 存纯文件名，遍历时基于当前文件父目录 `resolve`。[项目]
- Java 备用实现曾写完整路径，跨后端切换会找不到文件。[项目]
- 链式存储便于追加，但随机访问/编辑/统计需要遍历；需要索引/摘要优化。

### 8.3 原子写与锁

```python
import os, tempfile

def atomic_write_json(path, obj):
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
```

- 先写临时文件再 `os.replace`，避免读到半截 JSON。
- 多进程/多请求写同一文件需要文件锁/单写队列/版本号；仅靠 `os.replace` 不能防丢失更新。
- 读取要处理空文件/半截文件/编码错误，不能直接崩溃。

### 8.4 Redis

```python
# 缓存
value = redis.get(key)
if value is None:
    value = load_from_db()
    redis.set(key, value, ex=60)

# 计数/去重
redis.sadd("view:post:1", user_id)
```

- 缓存穿透：查不存在的数据，缓存空值/布隆过滤器。
- 缓存击穿：热点 key 过期，互斥锁/逻辑过期。
- 缓存雪崩：大量 key 同时过期，随机 TTL/多级缓存。
- 一致性：先更新 DB 再删缓存；延迟双删；接受最终一致要写清边界。
- Redis 不可用要降级，不能把主流程打挂；项目广场有 3s 冷却回源。[项目]

**项目对照**：

- `view_take` 先 `DEL` 再业务 commit，commit 失败会丢增量；应先提交再删/用事务性队列。[项目]
- 热门 ZSET/浏览去重提升读性能，但压测是小数据集 SQLite，不能外推为生产容量结论。[项目]

---

## 9. 配置、日志与部署

### 9.1 配置

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://127.0.0.1:6379/0"
    jwt_secret: str
    chroma_dir: str = "./storage/vectordb_4060"

    model_config = {"env_file": ".env", "extra": "ignore"}
```

- 配置从环境变量/密钥管理读取；代码里只留安全默认值。
- 启动时校验必需配置，缺失直接失败；不要用默认 JWT 密钥/默认管理员。
- 不同环境（dev/test/prod）配置分离；日志级别、CORS、调试开关不能带到生产。

### 9.2 日志

```python
logger.info("chat.stream.start", extra={"user_id": uid, "session_id": sid})
logger.exception("chat.stream.failed", extra={"user_id": uid})
```

- 结构化、带请求 ID；错误日志带堆栈。
- 脱敏：token、密码、手机号、邮箱、LLM prompt 中的隐私。
- 日志级别：DEBUG 开发、INFO 关键路径、WARNING 可恢复异常、ERROR 需处理。
- 不要用 `print` 代替日志；不要在高频循环里打大量日志。

### 9.3 Uvicorn / uv / Docker

```bash
uv sync
uv run uvicorn dixiyang.main:app --host 0.0.0.0 --port 8084
```

- 开发 `--reload`，生产多 worker/进程管理；注意多 worker 下的内存/会话/文件锁。
- Docker：基础镜像、非 root 用户、依赖锁定、健康检查、只读文件系统（可行时）。
- 健康检查：`/docs` 或专用 `/health`；不要用需要鉴权的业务接口做探活。
- 启动顺序：MySQL/Redis 就绪 → 后端 → 前端；RAG/Chroma 独立。

### 9.4 可观测性

- 指标：请求量、错误率、P95、DB 连接池、Redis 命中、LLM 延迟/token。
- 追踪：请求 ID 贯穿前后端/下游；SSE 记录开始/结束/取消。
- 告警：错误率、P95、队列积压、磁盘/内存；阈值要可行动。
- 审计：管理操作、权限变更、删除；保留操作者/时间/对象。

---

## 10. 项目缺陷与审查案例

### 10.1 认证/授权

| 问题 | 影响 | 修复 |
|---|---|---|
| 角色/时间线/故事节点无鉴权 | 匿名读写用户数据 | 加 `Depends(get_current_user_id)` + owner 校验 |
| `userConfig` 任意 `userId` | IDOR | 强制当前用户/校验归属 |
| Java `permitAll` + `userId=1L` | 匿名以固定用户执行 | 默认拒绝 + 从 token 取用户 |
| CORS 通配 + credentials | 配置无效/安全风险 | 来源白名单 |
| 后台 403 当 401 | 误登出 | 区分状态码/独立会话 |

### 10.2 并发/事务

| 问题 | 影响 | 修复 |
|---|---|---|
| 链文件无锁 | 消息交错/丢失 | 文件锁/单写队列/版本号 |
| 摘要丢第 7-12 条 | 历史上下文丢失 | 分页/游标/完整遍历 |
| 章节冲突返回 200 | 前端误判成功 | 409 + 业务码 |
| Redis 先删后 commit | 增量丢失 | 提交后删/事务消息 |
| async 路由跑同步 DB | 事件循环阻塞 | 异步驱动/线程池/同步路由 |

### 10.3 契约/错误

| 问题 | 影响 | 修复 |
|---|---|---|
| `pageSize` vs `page_size` | 分页失效/数据缺失 | alias/统一规范/契约测试 |
| 业务 500 HTTP 200 | 静默失败 | 状态码 + unwrap |
| rerank 错端点 404 静默 | 精排失效无感 | 正确端点 + 指标/告警 |
| Java 不识别 `__file__` | 读取文件字段失败 | 统一 StorageService |
| Java 返回 JSON 字符串 | 前端多一层解析 | 统一序列化 |

### 10.4 审查清单

- [ ] 每个写接口是否有鉴权 + 归属校验？
- [ ] 请求体是否有模型校验/长度限制？
- [ ] 事务边界是否清晰？异常是否回滚？
- [ ] 外部调用是否有超时/重试/幂等？
- [ ] 文件路径是否规范化并限制根目录？
- [ ] 上传是否先鉴权、限大小、限类型？
- [ ] async 路由里是否有阻塞调用？
- [ ] 错误是否返回正确 HTTP 状态 + 业务码？
- [ ] 日志是否含请求 ID 且脱敏？
- [ ] 分页/字段命名是否与前端契约一致？
- [ ] 多 worker/多实例下锁/缓存/会话是否成立？

---

## 11. 高频追问

1. **FastAPI 为什么快？** Starlette/Uvicorn 异步、Pydantic 校验、依赖注入；但业务里同步阻塞会抵消优势。
2. **`async def` 和 `def` 路由区别？** async 在事件循环执行；def 在线程池执行。阻塞代码放 async 会卡全局。
3. **Pydantic v1/v2 区别？** v2 用 Rust 核心、`model_config`、`field_validator`；性能更好，部分 API 不兼容。
4. **Session 和事务怎么管？** 每请求一个 Session，服务层控制 commit/rollback，`yield` 依赖关闭。
5. **JWT 如何撤销？** 短期 token + refresh、会话号比对、黑名单；纯 JWT 本身无法主动撤销。
6. **如何防越权？** 后端每个资源校验 owner/role；不能依赖前端隐藏按钮。
7. **如何处理大文件上传？** 流式读取、分片、大小/类型限制、临时目录、病毒扫描、鉴权。
8. **如何保证缓存一致性？** 更新 DB 后删缓存、延迟双删、版本号；明确最终一致窗口。
9. **为什么链文件用文件系统？** 大文本/追加写、避免 DB 行膨胀；代价是一致性和并发复杂。
10. **如何定位接口 500？** 请求 ID → 日志堆栈 → 复现入参 → DB/下游 → 最小单测；不要只看前端。

---

## 12. 自检

- [ ] 能解释 Python 引用/可变默认参数/生成器/上下文管理器。
- [ ] 能说明 GIL 与 async/线程/进程的选择。
- [ ] 能画出 FastAPI 请求链路与依赖注入生命周期。
- [ ] 能写出带 alias、校验、response_model 的接口。
- [ ] 能解释事务边界、N+1、索引、乐观锁。
- [ ] 能实现 JWT + session_id 顶号，并说明 401/403 差异。
- [ ] 能识别 IDOR、路径穿越、上传、CORS 风险。
- [ ] 能设计原子写/锁/Redis 降级。
- [ ] 能给出 3 个项目后端缺陷的根因与修复。
- [ ] 能用日志/指标/复现命令完成一次 500 排查。

---

*上一卷：[Web 前端与 Vue3](./02-Web前端与Vue3.md) ｜ 下一卷：[RAG 与大模型应用](./04-RAG与大模型应用.md)*
