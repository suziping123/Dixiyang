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
from dixiyang.routers import auth, novel, character, story_node, timeline, file, user, chat, user_config, chat_history, rag
from dixiyang.utils.database import Base, engine
from dixiyang.config import UPLOAD_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield


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


@app.get("/")
async def root():
    return {"message": "Dixiyang API - Python 版"}


if __name__ == "__main__":
    import os as _os
    _os.makedirs(UPLOAD_DIR, exist_ok=True)
    import uvicorn

    uvicorn.run("dixiyang.main:app", host="0.0.0.0", port=8084, reload=True)
