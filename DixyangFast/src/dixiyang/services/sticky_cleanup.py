"""便签存储定期清理（每日一轮 + 启动即跑）

清理两类残留（只动 storage/sticky/ 子树，幂等安全）：
1. 孤儿 json：文件在、DB 无对应 sticky_note 行（异常中断/手工拷贝残留）
2. 空用户目录：delete_json 只删文件不删目录，删光便签后 sticky/{userId}/ 永久残留

DB 查询失败时**只做空目录、不判孤儿**（孤儿判定依赖 DB 全量行，DB 不可用时不能盲删文件）。
"""
import logging
import os
import threading
import time

from ..config import STORAGE_DIR

log = logging.getLogger(__name__)

INTERVAL = 24 * 3600  # 每 24h 一轮
ROOT = os.path.join(STORAGE_DIR, "sticky")


def sweep() -> dict:
    """执行一轮清理，返回 {"orphan_files": n, "empty_dirs": n}"""
    if not os.path.isdir(ROOT):
        return {"orphan_files": 0, "empty_dirs": 0}

    ids: set[int] | None = None  # None = DB 不可用（不判孤儿）
    try:
        from ..models.sticky import StickyNote
        from ..utils.database import SessionLocal

        db = SessionLocal()
        try:
            ids = {r[0] for r in db.query(StickyNote.id).all()}
        finally:
            db.close()
    except Exception as e:  # noqa: BLE001 后台任务绝不拖垮主服务
        log.warning("便签清理：DB 查询失败，本轮跳过孤儿文件判定（%s）", e)

    orphan_files = 0
    empty_dirs = 0
    for uid in os.listdir(ROOT):
        d = os.path.join(ROOT, uid)
        if not os.path.isdir(d):
            continue
        # 1) 删孤儿 json（文件 id 不在 DB 行集合）
        if ids is not None:
            for f in os.listdir(d):
                if not f.endswith(".json"):
                    continue
                try:
                    fid = int(f[:-5])
                except ValueError:
                    continue  # 非约定命名：不动
                if fid not in ids:
                    try:
                        os.remove(os.path.join(d, f))
                        orphan_files += 1
                        log.info("便签清理：删除孤儿文件 sticky/%s/%s", uid, f)
                    except OSError as e:
                        log.warning("便签清理：删除失败 %s/%s: %s", uid, f, e)
        # 2) 删空目录（递归无任何文件才算空）
        if not _has_file(d):
            try:
                os.rmdir(d)
                empty_dirs += 1
                log.info("便签清理：删除空目录 sticky/%s", uid)
            except OSError:
                pass  # 并发下目录已被占用/重建：跳过
    if orphan_files or empty_dirs:
        log.info("便签清理完成：孤儿文件 %s，空目录 %s", orphan_files, empty_dirs)
    return {"orphan_files": orphan_files, "empty_dirs": empty_dirs}


def _has_file(path: str) -> bool:
    """目录树中是否还有任何文件"""
    for _root, _dirs, files in os.walk(path):
        if files:
            return True
    return False


# ---------- 后台线程（与 idea_cache 同款：daemon + stop event） ----------

_stop = threading.Event()
_bg: threading.Thread | None = None


def start_background() -> None:
    global _bg
    if _bg and _bg.is_alive():
        return
    _stop.clear()
    _bg = threading.Thread(target=_loop, name="sticky-cleanup", daemon=True)
    _bg.start()
    log.info("便签存储清理任务已启动（每 %ss 一轮）", INTERVAL)


def stop_background() -> None:
    _stop.set()


def _loop() -> None:
    while not _stop.is_set():
        try:
            sweep()
        except Exception as e:  # noqa: BLE001
            log.warning("便签清理异常：%s", e)
        _stop.wait(INTERVAL)
