import os

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123321@127.0.0.1:3306/dixiyang?charset=utf8")
SECRET_KEY = os.getenv("SECRET_KEY", "dixiyang-secret-key-1234567890abcdef12345678")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/home/lijiajia/项目/Dixiyang/uploads")
STORAGE_DIR = os.getenv("STORAGE_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage"))

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/")
