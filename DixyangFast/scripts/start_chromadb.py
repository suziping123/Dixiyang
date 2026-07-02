import argparse
import sys
import uvicorn
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chromadb.server.fastapi import ServerAPI
from chromadb.config import Settings

def main():
    parser = argparse.ArgumentParser(description="启动 ChromaDB Server")
    parser.add_argument("--path", required=True, help="向量数据库路径")
    parser.add_argument("--host", default="localhost", help="绑定地址")
    parser.add_argument("--port", type=int, default=8000, help="端口")
    args = parser.parse_args()

    settings = Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=str(args.path),
        anonymized_telemetry=False
    )

    api = ServerAPI(settings=settings)
    app = api.app

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )

if __name__ == "__main__":
    main()