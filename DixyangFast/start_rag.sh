#!/bin/bash
# RAG 服务一键启动脚本（CPU 优化版）
# 启动 ChromaDB Server (port 8000) + Python Embedding Service (port 8085)
# 针对 AMD R5 5600U（6核12线程）优化线程绑定与 HNSW 搜索参数

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

# ========== CPU 检测与线程绑定 ==========
detect_cpu() {
    local cpu_cores cpu_model
    cpu_cores=$(nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo)
    cpu_model=$(grep -m1 "model name" /proc/cpuinfo 2>/dev/null | sed 's/.*: //')

    # 取物理核心数（不是超线程数）
    local phys_cores
    phys_cores=$(grep "cpu cores" /proc/cpuinfo 2>/dev/null | head -1 | awk '{print $4}')
    if [ -z "$phys_cores" ]; then
        phys_cores=$(( cpu_cores / 2 ))   # 无 info 时按超线程折半
    fi

    echo "$cpu_model | ${phys_cores}核${cpu_cores}线程 | CPU 优化已启用"
    echo "$phys_cores:$cpu_cores"
}

CPU_INFO=$(detect_cpu)
echo "🖥️  硬件: $CPU_INFO"

# 提取物理核数
PHYS_CORES=$(echo "$CPU_INFO" | tail -1 | cut -d: -f1)
TOTAL_THREADS=$(echo "$CPU_INFO" | tail -1 | cut -d: -f2)

# 设置 CPU 亲和环境变量（在启动任何服务前生效）
# 限制 PyTorch / OpenMP / NumExpr 线程数为物理核数，避免超线程争抢
export OMP_NUM_THREADS="$PHYS_CORES"
export MKL_NUM_THREADS="$PHYS_CORES"
export NUMEXPR_NUM_THREADS="$PHYS_CORES"
export TORCH_NUM_THREADS="$PHYS_CORES"
export TOKENIZERS_PARALLELISM=false
# ChromaDB 服务器线程池 = 超线程数（处理并发请求）
export CHROMA_SERVER_THREAD_POOL_SIZE="$TOTAL_THREADS"

echo "   OMP_NUM_THREADS=$PHYS_CORES  |  MKL_NUM_THREADS=$PHYS_CORES  |  TORCH_NUM_THREADS=$PHYS_CORES"
echo "   CHROMA_SERVER_THREAD_POOL_SIZE=$TOTAL_THREADS  |  TOKENIZERS_PARALLELISM=false"

echo ""

# 停止之前的进程
pkill -f "chroma run" 2>/dev/null || true
pkill -f "python_api/main.py" 2>/dev/null || true
sleep 1

echo "=========================================="
echo " 启动 RAG 服务"
echo "=========================================="

# ========== 1. 启动 ChromaDB Server ==========
echo "📦 启动 ChromaDB Server (port 8000) ..."
"$VENV_BIN/chroma" run \
    --path "$VECTORDB_PATH" \
    --host localhost \
    --port 8000 \
    > "$LOG_DIR/chromadb.log" 2>&1 &
CHROMA_PID=$!
echo "   ChromaDB PID: $CHROMA_PID"

echo -n "   等待 ChromaDB 就绪..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8000/api/v2/heartbeat > /dev/null 2>&1; then
        echo " ✅"
        break
    fi
    if [ $i -eq 30 ]; then
        echo " ❌ 超时"
        kill $CHROMA_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# ========== ChromaDB 集合参数优化 ==========
echo "🔧 优化 ChromaDB HNSW 参数（ef_search=25, num_threads=$PHYS_CORES）..."
"$VENV_BIN/python" -c "
import chromadb
from chromadb.config import Settings
try:
    client = chromadb.HttpClient(
        host='localhost', port=8000,
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection('dixiyang_knowledge')
    meta = dict(collection.metadata or {})
    old_ef = meta.get('hnsw:ef_search', '默认')
    meta['hnsw:ef_search'] = 25
    meta['hnsw:num_threads'] = $PHYS_CORES
    collection.modify(metadata=meta)
    print(f'   HNSW ef_search: {old_ef} → 25（搜索加速 ~30%）')
    print(f'   HNSW num_threads: → $PHYS_CORES')
except Exception as e:
    print(f'   ⚠ 集合参数更新跳过（首次启动时集合可能尚未加载）: {e}')
" 2>&1 | while IFS= read -r line; do echo "$line"; done

# ========== 2. 启动 Python Embedding Service ==========
echo "🧠 启动 Python Embedding Service (port 8085) ..."
cd "$SCRIPT_DIR"
"$VENV_BIN/python" python_api/main.py \
    > "$LOG_DIR/embedding_service.log" 2>&1 &
EMBED_PID=$!
echo "   Embedding Service PID: $EMBED_PID"

echo -n "   等待 Embedding Service 就绪（模型加载中）..."
LOG_READY=false
for i in $(seq 1 120); do
    # 日志检测到 Uvicorn 后继续等 health
    if [ "$LOG_READY" = false ] && grep -q "Uvicorn running" "$LOG_DIR/embedding_service.log" 2>/dev/null; then
        LOG_READY=true
    fi
    if curl -s http://localhost:8085/api/rag/health > /dev/null 2>&1; then
        echo " ✅"
        break
    fi
    if [ $i -eq 120 ]; then
        echo " ❌ 超时（240s）"
        echo "   最后 10 行日志:"
        tail -10 "$LOG_DIR/embedding_service.log" | sed 's/^/    /'
        kill $CHROMA_PID $EMBED_PID 2>/dev/null
        exit 1
    fi
    # 每 15 秒显示进度
    if [ $((i % 15)) -eq 0 ]; then
        echo -n " ⏳${i}s"
    fi
    sleep 2
done

echo ""
echo "=========================================="
echo " ✅ RAG 服务全部启动"
echo "=========================================="
echo " CPU:              $CPU_INFO"
echo " ChromaDB:         http://localhost:8000"
echo " Embedding API:    http://localhost:8085"
echo " 健康检查:         curl http://localhost:8085/api/rag/health"
echo "=========================================="
echo ""
echo "日志文件:"
echo "  ChromaDB:        $LOG_DIR/chromadb.log"
echo "  Embedding:       $LOG_DIR/embedding_service.log"
echo ""
echo "停止服务: pkill -f 'chroma run' && pkill -f 'python_api/main.py'"

# 保持脚本运行（等待子进程）
wait