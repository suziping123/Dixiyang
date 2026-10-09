# Redis 与管理后台策划

> 版本：v1.0（评审稿）｜创建：2026-10-09｜作者：opencode  
> 定位：**策划文档，本轮不写码**。用户第 9 条反馈"既然有公共场所了，Redis、管理员页面之类传统东西该开始策划了"。  
> 衔接：[点子库与创意社区策划](./点子库与创意社区策划.md) §4 已给出 Redis **设计方案**（Key/热门分/降级），本文补齐**落地实施**；管理后台为**全新策划**。

---

## 一、Redis 落地实施

### 1.1 现状与动机

| 能力 | 现状 | 问题 |
|------|------|------|
| 频控（发帖/评论/导入） | 内存 dict：`idea_service.py:45 _limit_check / :54 _limit_mark` | 重启丢失；多 worker 不共享；与热榜/计数无法共用连接 |
| 计数（赞/藏/评） | 直接读写 MySQL `idea_post` 计数列 | 高频写放大；热门排序靠 DB `hot_score` 全表排序 |
| 热门榜 | `ORDER BY hot_score DESC` | 无事件级增量，冷热混排 |
| 浏览数 | 直接 `view_count += 1` 每次详情 `commit` | 重复浏览无去重，写放大 |

### 1.2 依赖与配置

- 依赖：`redis`（Python 官方客户端，纯协议无编译）；本地/内网 `redis-server`（Windows 可用 memurai/WSL，部署机为 Linux）。
- 配置：`.env.example` 增占位键 `REDIS_URL=redis://127.0.0.1:6379/0`（**实施时先读 `.env.example` 确认结构**；真实 `.env` 按 AGENTS §9 不读不改，由部署者自行填）。
- **不引入** redis-py 之外的缓存框架（无 FastAPI-cache/aiocache——降级逻辑简单，自封装更可控）。

### 1.3 封装层 `services/idea_cache.py`（新）

业务层**只经此模块**摸 Redis，绝不直连（= 点子库策划 §4.5）：

```python
class IdeaCache:
    # 连接：lazy 单例，url 读环境变量；任何异常 → self._down=True 进入降级
    def healthy() -> bool
    # 频控：沿用现有语义（remain 秒 / 成功才 mark）
    def rate_check(key: str, seconds: float) -> float   # GET+EXPIRE，返回剩余秒
    def rate_mark(key: str, ttl: float) -> None         # SETEX
    # 计数
    def incr(field: str, post_id: int, delta: int = 1)
    def get_count(field: str, post_id: int) -> int | None   # None=回源 DB
    # 热门
    def hot_zincr(post_id: int, delta: float)
    def hot_top(n: int) -> list[int] | None
    # 浏览去重
    def view_seen(post_id: int, user_id: int) -> bool   # SETNX 600s，True=已看
    # 生命周期
    async def start_background()   # lifespan 启动 60s 回写 + 10min 重建
```

**降级铁律**：`healthy()==False` 时所有方法返回哨兵（`None`/直接跳过），调用方回退现有 DB 路径——**Redis 全挂不阻断任何现有功能**（回归 40+15+19 用例在 Redis down 态必须全绿）。

### 1.4 迁移分期

| 期 | 内容 | 改动点 | 验收 |
|----|------|--------|------|
| **P0** | 频控迁移 | `_limit_check/_limit_mark` 内部改走 `IdeaCache`，Redis down 退内存 dict（现行为） | round2 频控 5 用例 + 文案秒数不变；kill redis 后重跑仍过 |
| **P0** | 计数旁路 | `toggle_like/collect`、评论增删 → 同步 `INCR`；读路径 `get_count` 有则读、无回源并回填 | 计数与 DB 最终一致；round1/3 不变 |
| **P1** | 热门 ZSET | 事件 `ZINCRBY idea:hot`；`sort=hot` 读 `hot_top` → 空则回源 `hot_score` | 热门榜顺序合理；redis down 时排序退化但可用 |
| **P1** | 浏览去重 | 详情接口 `view_seen` 命中则跳过 `view_count` 写 | 同用户 10 分钟内重复浏览不涨数 |
| **P1** | 定时任务 | lifespan：60s pipeline 回写计数 ↔ DB + `hot_score`；10min 全量重建 ZSET 防漂移 | `admin`/脚本对账：Redis vs DB 差值窗口内 < 阈值 |
| **P2** | 会话锁/全局 | 聊天顶号、跨实例锁等（超出点子库范围，另立项） | — |

### 1.5 验收方式

1. `test_idea_api*.py` 三套（40+15+19）在 **redis up / down** 两态各跑一遍全绿。
2. 新增 `test_redis_cache.py`：频控 TTL、计数 incr/回写、ZSET 增删、降级哨兵。
3. 手测：起停 redis-server 观察日志（warning 而非 error）与页面无感切换。

---

## 二、管理后台策划

### 2.1 现状

- 无角色字段：`app_user` 无 `role/is_admin`（models 已确认）；无任何 `/admin` 端点与页面。
- 内容治理仅作者自助（下架/编辑/重新上架），**平台侧无审核入口**。

### 2.2 角色模型（最小侵入）

- `app_user` 增列 `role VARCHAR(16) NOT NULL DEFAULT 'user'`（CREATE TABLE 已建表的走 `ALTER ... DEFAULT 'user'`，**零破坏**；老数据自动 user）。
- 首个管理员：部署脚本/SQL 手工 `UPDATE app_user SET role='admin' WHERE username='...'`（不做注册开放 admin）。
- 登录响应带 `role`；**后端**：FastAPI 依赖 `require_admin`（读 JWT sub → 查 role，非 admin → 403）；**前端**：`localStorage.role` + `/admin` 路由守卫（非 admin 跳 `/home`）+ 导航仅 admin 可见入口。

### 2.3 页面与功能（P0 四块）

| # | 页面 | 功能 | 优先级 |
|---|------|------|--------|
| 1 | **仪表盘** `/admin` | 用户数/帖子数/评论数、今日新增三项、`uploads/` 存储用量（目录统计）、在线会话数（Java 侧可选） | P0 |
| 2 | **用户管理** | 列表（分页/搜索 username&nickname）、封禁/解封（封禁=登录接口拒绝 + 现存 token 401）、重置密码（生成随机并回显一次）、角色查看 | P0 |
| 3 | **内容审核** | 帖子列表（状态/作者/时间/搜索，含已下架）→ 详情（复用 `PostDetailDialog` 只读）→ **平台下架 / 恢复 / 删除**；评论列表 → 删除。与作者自助下架共用 service 方法，仅入口不同 | P0 |
| 4 | **举报处理** | 举报提交（P0.5 前端入口：详情页"举报"按钮）+ 管理端列表/处理（忽略/下架/删评论）| P1 |

**不做（本期）**：内容自动审核（敏感词可 P2 挂钩已有词库）、用户封禁申诉流、管理端操作审计表（P1 再加 `admin_audit`）。

### 2.4 API 草案（FastAPI `routers/admin.py`，全部 `Depends(require_admin)`）

```
GET    /api/admin/stats                    → {users, posts, comments, todayNewUsers, todayNewPosts, storageBytes}
GET    /api/admin/users?query=&page=&pageSize=&status=
POST   /api/admin/users/{id}/ban           → {banned:true}      # body: {reason?}
POST   /api/admin/users/{id}/unban
POST   /api/admin/users/{id}/reset-password→ {tempPassword}
GET    /api/admin/posts?status=&query=&page=
POST   /api/admin/posts/{id}/remove        # 与 idea.remove_post 同 service，仅权限包装
POST   /api/admin/posts/{id}/restore
DELETE /api/admin/posts/{id}               # 级联删评论/标签/附件记录（P1）
GET    /api/admin/comments?query=&page=
DELETE /api/admin/comments/{id}
GET    /api/admin/reports?status=          # P1
POST   /api/admin/reports/{id}/resolve     # P1 {action: ignore|remove_post|delete_comment}
```

- 错误约定沿用 `Result`（code/msg）；**403 与业务失败统一 code**（前端拦截器已 resolve，调用方 unwrap 判断）。
- 封禁实现：`app_user.status='banned'`（或 `banned_at` 时间戳）；`auth_service.login` 拒绝 + JWT 中间件对 banned 用户返回 401（复用现有 `handleUnauthorized` 踢出链路）。

### 2.5 前端结构（新增）

```
src/
├── api/adminApi.ts                 # 上表全部端点 + 类型
├── views/AdminView.vue             # /admin 路由，左侧栏 4 Tab（仪表盘/用户/内容/举报）+ 顶栏
│   ├── AdminDashboard.vue          # 统计卡片
│   ├── AdminUsers.vue              # 表格 + 封禁/解封/重置密码（危险操作 confirmDelete）
│   ├── AdminContent.vue            # 帖子/评论双 Tab，复用 PostDetailDialog 查看
│   └── AdminReports.vue            # P1
└── router：/admin 守卫（meta.requiresAdmin + localStorage.role）
```

- 风格：沿用 `--surface-card` 实底 + 表格/分页 EP 组件；**移动端 P0 不适配**（管理后台桌面优先，写入已知问题）。
- 危险操作全部 `confirmDelete`（禁回车确认，遵循前端 AGENTS）。

### 2.6 里程碑

| 里程碑 | 内容 | 依赖 |
|--------|------|------|
| M1 | `role` 列 + `require_admin` + 前端路由守卫（空 `/admin` 页占位） | DB 改动评审通过 |
| M2 | 仪表盘 + 用户管理（含封禁/重置密码） | M1 |
| M3 | 内容审核（帖子下架/恢复/删除 + 评论删除） | M1；与点子库 service 复用 |
| M4 | 举报提交入口 + 举报处理 | M3 |
| M5 | `admin_audit` 审计表 + 操作留痕 | M2-M3 稳定后 |

---

## 三、风险与已知问题

1. **Redis 部署形态未定**（本机/内网/容器）——P0 频控迁移设计为可降级，形态不影响开发。
2. `app_user` 改表需与 Java 侧共用该表（登录/JWT 在 Java？若 FastAPI auth 独立则只动 Python；**实施 M1 前先确认登录链路归属**——当前点子库登录走 `/api/auth/login` FastAPI）。
3. 管理员无自助开通——首个 admin 靠 SQL，需写入部署文档。
4. 平台下架与作者下架共用 `status='removed'`，作者"重新上架"会绕过平台处置——**P0 约定**：平台下架的帖子作者 restore 时校验 `removed_by='admin'` 拒绝（字段 P0.5 增加或 P1 用 `admin_audit` 反查，落地时定）。
5. 移动端管理后台不适配（明确不做，见 §2.5）。

## 四、验证方式（策划阶段）

- 本文评审通过后按 M1-M5 立项；每个里程碑验收 = API 自动化（新增 admin 用例）+ 手测清单。
- Redis 部分：§1.5 三态回归。

---

**变更记录**
- v1.0 2026-10-09：首版（Redis 落地实施 + 管理后台策划）。
