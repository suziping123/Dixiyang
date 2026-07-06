import os
from pathlib import Path

# 加载项目根 .env（与 Spring 版共用）
_env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

# ── 敏感信息（必须从环境变量或 .env 提供，无硬编码默认值）──
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# ── 非敏感配置（有合理默认值）──
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
STORAGE_DIR = os.getenv("STORAGE_DIR", os.path.join(UPLOAD_DIR, "storage"))

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", os.getenv("DS_API_KEY", ""))
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

CHAT_STORAGE_PATH = os.getenv("CHAT_STORAGE_PATH", STORAGE_DIR)
CHAT_MAX_FILE_SIZE = int(os.getenv("CHAT_MAX_FILE_SIZE", "102400"))

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
