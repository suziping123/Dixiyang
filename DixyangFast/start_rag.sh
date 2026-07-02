#!/bin/bash
# RAG 服务一键启动脚本
# 启动 ChromaDB Server (port 8000) + Python Embedding Service (port 8085)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_BIN="$SCRIPT_DIR/.venv/bin"
VECTORDB_PATH="$SCRIPT_DIR/storage/vectordb_4060"
LOG_DIR="$SCRIPT_DIR/logs"

mkdir -p "$LOG_DIR"

# 检查向量库是否存在
if [ ! -d "$VECTORDB_PATH" ]; then
    echo "❌ 向量库不存在: $VECTORDB_PATH"
    echo "请先在 Windows 上构建向量库，然后传到此目录"
    exit 1
fi

# 停止之前的进程
pkill -f "chroma run" 2>/dev/null || true
pkill -f "python_api/main.py" 2>/dev/null || true
sleep 1

echo "=========================================="
echo " 启动 RAG 服务"
echo "=========================================="

# 1. 启动 ChromaDB Server
echo "📦 启动 ChromaDB Server (port 8000) ..."
"$VENV_BIN/chroma" run \
    --path "$VECTORDB_PATH" \
    --host localhost \
    --port 8000 \
    > "$LOG_DIR/chromadb.log" 2>&1 &
CHROMA_PID=$!
echo "   ChromaDB PID: $CHROMA_PID"

# 等待 ChromaDB 启动
echo "   等待 ChromaDB 就绪..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8000/api/v2/heartbeat > /dev/null 2>&1; then
        echo "   ✅ ChromaDB 就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ ChromaDB 启动超时"
        kill $CHROMA_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# 2. 启动 Python Embedding Service
echo "🧠 启动 Python Embedding Service (port 8085) ..."
cd "$SCRIPT_DIR"
"$VENV_BIN/python" python_api/main.py \
    > "$LOG_DIR/embedding_service.log" 2>&1 &
EMBED_PID=$!
echo "   Embedding Service PID: $EMBED_PID"

# 等待服务启动
echo "   等待 Embedding Service 就绪..."
for i in $(seq 1 60); do
    if curl -s http://localhost:8085/api/rag/health > /dev/null 2>&1; then
        echo "   ✅ Embedding Service 就绪"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "   ❌ Embedding Service 启动超时"
        kill $CHROMA_PID $EMBED_PID 2>/dev/null
        exit 1
    fi
    sleep 2
done

echo ""
echo "=========================================="
echo " ✅ RAG 服务全部启动"
echo "=========================================="
echo " ChromaDB:       http://localhost:8000"
echo " Embedding API:  http://localhost:8085"
echo " 健康检查:       curl http://localhost:8085/api/rag/health"
echo "=========================================="
echo ""
echo "日志文件:"
echo "  ChromaDB:        $LOG_DIR/chromadb.log"
echo "  Embedding:       $LOG_DIR/embedding_service.log"
echo ""
echo "停止服务: pkill -f 'chroma run' && pkill -f 'python_api/main.py'"

# 保持脚本运行（等待子进程）
wait