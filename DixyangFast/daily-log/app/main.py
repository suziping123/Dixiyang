import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from app.chat.Controller.ChatController import router
from app.config import settings

app = FastAPI(title="AI Chat API", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
app.mount("/templates", StaticFiles(directory=str(settings.TEMPLATES_DIR)), name="templates")

app.include_router(router)


@app.get("/")
def index():
    return FileResponse(str(settings.TEMPLATES_DIR / "index.html"))


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )