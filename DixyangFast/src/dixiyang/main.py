import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dixiyang.models.user import AppUser
from dixiyang.models.novel import Novels
from dixiyang.models.character import NovelCharacter
from dixiyang.models.timeline import Timeline
from dixiyang.models.story_node import StoryNode
from dixiyang.models.file import File
from dixiyang.models.user_config import UserConfig
from dixiyang.models.novel_relation import NovelRelation
from dixiyang.models.chat_session import ChatSession
from dixiyang.models.volume import Volume
from dixiyang.models.chapter import Chapter
from dixiyang.models import idea as idea_model  # noqa: F401  注册 idea_* 7 张表到 Base.metadata
from dixiyang.models.sticky import StickyNote  # noqa: F401  注册 sticky_note 表
from dixiyang.routers import auth, novel, character, story_node, timeline, file, user, chat, user_config, chat_history, rag, volume, chapter, ai, idea, admin, sticky
from dixiyang.utils.database import Base, engine
from dixiyang.config import UPLOAD_DIR
from dixiyang.services.idea_cache import cache as idea_cache
from dixiyang.services import sticky_cleanup


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    # 既有表补列：app_user.role（create_all 不会给旧表加列）
    from sqlalchemy import inspect as sa_inspect, text
    cols = {c["name"] for c in sa_inspect(engine).get_columns("app_user")}
    if "role" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE app_user ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
    # 既有表补列：app_user.admin_session_id（管理后台独立会话号，与用户端 session_id 隔离）
    if "admin_session_id" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE app_user ADD COLUMN admin_session_id VARCHAR(64)"))
    # 既有表补列：sticky_note.done（同上，create_all 不会给旧表加列，缺失则增删改查全 500）
    s_cols = {c["name"] for c in sa_inspect(engine).get_columns("sticky_note")}
    if "done" not in s_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE sticky_note ADD COLUMN done INT NOT NULL DEFAULT 0"))
    idea_cache.start_background()
    sticky_cleanup.start_background()  # 每日清理 sticky/ 孤儿文件 + 空用户目录
    yield
    sticky_cleanup.stop_background()
    idea_cache.stop_background()


app = FastAPI(title="Dixiyang API - Python 版", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_path = Path(UPLOAD_DIR).resolve()
if uploads_path.exists():
    app.mount("/api/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

app.include_router(auth.router, prefix="/api")
app.include_router(novel.router, prefix="/api")
app.include_router(character.router, prefix="/api")
app.include_router(story_node.router, prefix="/api")
app.include_router(timeline.router, prefix="/api")
app.include_router(file.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(user_config.router, prefix="/api")
app.include_router(chat_history.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(volume.router, prefix="/api")
app.include_router(chapter.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(idea.router, prefix="/api")
app.include_router(sticky.router, prefix="/api")
app.include_router(admin.auth_router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Dixiyang API - Python 版"}


if __name__ == "__main__":
    import os as _os
    _os.makedirs(UPLOAD_DIR, exist_ok=True)
    import uvicorn

    # reload 默认关闭（Windows 下 WatchFiles 启动极慢）；需要热重载时设 RELOAD=1
    uvicorn.run("dixiyang.main:app", host="0.0.0.0", port=8084, reload=os.getenv("RELOAD", "0") == "1")
