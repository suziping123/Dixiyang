import os
import sys
from pathlib import Path
from typing import Optional


DATASETS_DIR = Path(__file__).resolve().parent / "chroma_data" / "datasets"
if not DATASETS_DIR.exists():
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

BASE_DIR = Path(__file__).resolve().parent.parent

model_path = BASE_DIR.parent / "models" / "bge-m3"
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

class Settings:
    DS_API_KEY: Optional[str] = os.getenv("DS_API_KEY")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-v4-flash")
    BASE_URL: str = os.getenv("BASE_URL", "https://api.deepseek.com")
    ALLOWED_ORIGINS: list = ["http://localhost:63342", "http://127.0.0.1:8000", "*"]
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    STATIC_DIR: Path = BASE_DIR/ "app" / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "app" / "templates"
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "3268845120@qq.com")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.qq.com")

settings = Settings()