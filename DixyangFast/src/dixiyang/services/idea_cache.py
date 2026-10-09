"""点子库 Redis 缓存封装（业务层唯一 Redis 入口，全链路可降级）

Key 约定（全部 idea: 前缀，DB 0）：
- idea:rl:{scope}:{uid}   频控 TTL（SETEX，成功才打点）
- idea:hot                热门榜 ZSET（member=post_id，score=热度增量）
- idea:view:{pid}:{uid}   浏览去重 SETNX（600s）
- idea:vcnt:{pid}         未回写浏览增量 INCRBY

降级铁律：Redis 不可用 → healthy()==False，各方法返回哨兵/直接跳过，
调用方回退原 DB 路径，现有功能零阻断（回归用例 Redis down 态必须全绿）。
"""
from __future__ import annotations

import logging
import os
import threading
import time

from ..config import REDIS_URL

log = logging.getLogger(__name__)

PROTOCOL = 2  # 本机 Windows Redis（老版）不支持 RESP3/HELLO
COOLDOWN_SEC = 3.0  # 探活失败后的快速拒绝窗口（避免每请求撞连接超时）
VIEW_DEDUP_SEC = 600  # 浏览去重有效期
FLUSH_INTERVAL = 60  # 浏览增量回写 DB 周期
REBUILD_INTERVAL = 600  # 热门 ZSET 全量重建周期

# Lua：GET+DEL 原子取走浏览增量（防 回写读取与新 INCRBY 竞态丢量）
_TAKE_LUA = """
local v = redis.call('GET', KEYS[1])
if v then redis.call('DEL', KEYS[1]) end
return v
"""


class IdeaCache:
    def __init__(self) -> None:
        self._client = None
        self._down_until = 0.0
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._bg: threading.Thread | None = None

    # ---------- 连接与探活 ----------

    def _get(self):
        if time.monotonic() < self._down_until:
            return None
        try:
            if self._client is None:
                import redis  # lazy：未装 redis-py 时整个模块仍可导入（降级）

                self._client = redis.Redis.from_url(
                    REDIS_URL,
                    protocol=PROTOCOL,
                    socket_timeout=1.5,
                    socket_connect_timeout=1.5,
                    decode_responses=True,
                )
            return self._client
        except Exception as e:  # noqa: BLE001 连接层任何异常都走降级
            self._mark_down(f"connect: {e}")
            return None

    def _mark_down(self, why: str) -> None:
        with self._lock:
            if time.monotonic() >= self._down_until:
                log.warning("Redis 降级（%s），%ss 内不再尝试", why, COOLDOWN_SEC)
            self._down_until = time.monotonic() + COOLDOWN_SEC

    def healthy(self) -> bool:
        c = self._get()
        if c is None:
            return False
        try:
            return bool(c.ping())
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"ping: {e}")
            return False

    # ---------- 频控（TTL 语义与内存版一致：check 只读，成功才 mark） ----------

    def rate_check(self, scope: str, uid: int, seconds: float) -> float:
        """0 = 放行；>0 = 剩余等待秒数"""
        c = self._get()
        if c is None:
            return 0.0  # 降级：调用方回退内存 dict
        try:
            ttl = c.ttl(f"idea:rl:{scope}:{uid}")
            return float(ttl) if ttl and ttl > 0 else 0.0
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"rate_check: {e}")
            return 0.0

    def rate_mark(self, scope: str, uid: int, seconds: float) -> bool:
        c = self._get()
        if c is None:
            return False
        try:
            c.setex(f"idea:rl:{scope}:{uid}", int(seconds), "1")
            return True
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"rate_mark: {e}")
            return False

    # ---------- 热门榜 ZSET ----------

    def hot_zincr(self, post_id: int, delta: float) -> None:
        if not delta:
            return
        c = self._get()
        if c is None:
            return
        try:
            c.zincrby("idea:hot", delta, str(post_id))
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"hot_zincr: {e}")

    def hot_top(self, n: int) -> list[int] | None:
        """None = 无数据/降级，调用方回源 DB hot_score 排序"""
        c = self._get()
        if c is None:
            return None
        try:
            rows = c.zrevrange("idea:hot", 0, n - 1)
            return [int(x) for x in rows] if rows else None
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"hot_top: {e}")
            return None

    def hot_top_scores(self, n: int) -> list[tuple[int, float]] | None:
        """热门榜 TopN（id, score），供综合推荐热度项使用；None = 无数据/降级"""
        c = self._get()
        if c is None:
            return None
        try:
            rows = c.zrevrange("idea:hot", 0, n - 1, withscores=True)
            return [(int(a), float(b)) for a, b in rows] if rows else None
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"hot_top_scores: {e}")
            return None

    def hot_rebuild(self, pairs: list[tuple[int, float]]) -> None:
        """全量重建（临时 key + RENAME 原子替换，防重建窗口内榜单为空）"""
        c = self._get()
        if c is None:
            return
        tmp = f"idea:hot:tmp:{os.getpid()}"
        try:
            pipe = c.pipeline()
            pipe.delete(tmp)
            for pid, score in pairs:
                pipe.zadd(tmp, {str(pid): score})
            pipe.rename(tmp, "idea:hot")
            pipe.execute()
        except Exception as e:  # noqa: BLE001 无数据时 RENAME 报错也走降级
            self._mark_down(f"hot_rebuild: {e}")
            c.delete(tmp)

    # ---------- 浏览：去重 + 增量暂存（60s 回写 DB） ----------

    def view_seen(self, post_id: int, uid: int) -> bool:
        """True = 600s 内已看过（调用方跳过计数）"""
        c = self._get()
        if c is None:
            return False
        try:
            return not c.set(f"idea:view:{post_id}:{uid}", "1", nx=True, ex=VIEW_DEDUP_SEC)
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"view_seen: {e}")
            return False

    def view_incr(self, post_id: int) -> None:
        c = self._get()
        if c is None:
            return
        try:
            c.incrby(f"idea:vcnt:{post_id}", 1)
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"view_incr: {e}")

    def view_pending(self, post_id: int) -> int:
        """未回写的浏览增量（详情响应叠加显示用；只读不取走）"""
        c = self._get()
        if c is None:
            return 0
        try:
            return int(c.get(f"idea:vcnt:{post_id}") or 0)
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"view_pending: {e}")
            return 0

    def view_take(self, post_id: int) -> int:
        """原子取走未回写增量（回写任务用）"""
        c = self._get()
        if c is None:
            return 0
        try:
            v = c.eval(_TAKE_LUA, 1, f"idea:vcnt:{post_id}")
            return int(v or 0)
        except Exception as e:  # noqa: BLE001
            self._mark_down(f"view_take: {e}")
            return 0

    # ---------- 后台任务：60s 回写浏览数 / 10min 重建热门 ----------

    def start_background(self) -> None:
        if self._bg and self._bg.is_alive():
            return
        self._stop.clear()
        self._bg = threading.Thread(target=self._loop, name="idea-cache-flush", daemon=True)
        self._bg.start()
        log.info("IdeaCache 后台任务已启动（回写 %ss / 重建 %ss）", FLUSH_INTERVAL, REBUILD_INTERVAL)

    def stop_background(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        next_flush = time.monotonic()
        next_rebuild = time.monotonic()
        while not self._stop.is_set():
            self._stop.wait(5)
            now = time.monotonic()
            if now >= next_flush:
                next_flush = now + FLUSH_INTERVAL
                try:
                    self.flush_views()
                except Exception as e:  # noqa: BLE001 后台任务绝不拖垮主服务
                    log.warning("浏览回写失败：%s", e)
            if now >= next_rebuild:
                next_rebuild = now + REBUILD_INTERVAL
                try:
                    self.rebuild_hot()
                except Exception as e:  # noqa: BLE001
                    log.warning("热门重建失败：%s", e)

    def flush_views(self) -> int:
        """把 Redis 中未回写的浏览增量合入 DB view_count + hot_score 列"""
        c = self._get()
        if c is None:
            return 0
        from ..models.idea import IdeaPost
        from ..utils.database import SessionLocal

        flushed = 0
        db = SessionLocal()
        try:
            for key in c.scan_iter(match="idea:vcnt:*", count=200):
                try:
                    pid = int(key.rsplit(":", 1)[-1])
                except ValueError:
                    continue
                delta = self.view_take(pid)
                if delta <= 0:
                    continue
                p = db.get(IdeaPost, pid)
                if p is not None:
                    p.view_count += delta
                    p.hot_score = 3 * p.like_count + 2 * p.collect_count + 2 * p.comment_count + p.view_count
                    flushed += 1
            db.commit()
        finally:
            db.close()
        if flushed:
            log.info("浏览增量回写 %d 帖", flushed)
        return flushed

    def rebuild_hot(self) -> int:
        """从 DB hot_score 全量重建热门 ZSET（防事件增量漂移）"""
        from ..models.idea import IdeaPost
        from ..utils.database import SessionLocal

        db = SessionLocal()
        try:
            rows = db.query(IdeaPost.id, IdeaPost.hot_score).filter(
                IdeaPost.status == "published"
            ).all()
        finally:
            db.close()
        if not rows:
            return 0
        self.hot_rebuild([(pid, float(score or 0)) for pid, score in rows])
        return len(rows)


cache = IdeaCache()
