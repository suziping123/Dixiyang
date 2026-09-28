# RAG 服务一键启动脚本 (Windows PowerShell)
# 启动 ChromaDB Server (port 8000) + Python Embedding Service (port 8085)

$ErrorActionPreference = "Stop"

# 禁用系统代理（WinHTTP 127.0.0.1:7890），否则 Invoke-WebRequest 访问 localhost 会走代理超时
$env:NO_PROXY = "*"
[System.Net.WebRequest]::DefaultWebProxy = $null

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_BIN = Join-Path $SCRIPT_DIR ".venv\Scripts"
$VECTORDB_PATH = Join-Path $SCRIPT_DIR "storage\vectordb_4060"
$LOG_DIR = Join-Path $SCRIPT_DIR "logs"

New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

if (-not (Test-Path $VECTORDB_PATH)) {
    Write-Host "[X] 向量库不存在: $VECTORDB_PATH"
    Write-Host "请先构建向量库: uv run -m rag_shared.processor --hardware rtx_4060 --full"
    exit 1
}

# 停止之前的相关进程
Write-Host "清理旧进程..."
Get-Process -Name "chroma" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "=========================================="
Write-Host "  启动 RAG 服务"
Write-Host "  PowerShell $($PSVersionTable.PSVersion) | $($MyInvocation.MyCommand.Path)"
Write-Host "=========================================="

# 1. ChromaDB Server
Write-Host "[1/2] 启动 ChromaDB Server (port 8000) ..."
$chromaBin = Join-Path $VENV_BIN "chroma.exe"
$chromaProcess = Start-Process -FilePath $chromaBin `
    -ArgumentList "run", "--path", $VECTORDB_PATH, "--host", "::1", "--port", "8000" `
    -RedirectStandardOutput (Join-Path $LOG_DIR "chromadb.log") `
    -RedirectStandardError (Join-Path $LOG_DIR "chromadb_err.log") `
    -NoNewWindow -PassThru
Write-Host "   ChromaDB PID: $($chromaProcess.Id)"

Write-Host "   等待 ChromaDB 就绪..."
$ready = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri "http://[::1]:8000/api/v2/heartbeat" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "   [OK] ChromaDB 就绪"
        $ready = $true
        break
    } catch {}
    Start-Sleep -Seconds 1
}
if (-not $ready) {
    Write-Host "   [X] ChromaDB 启动超时"
    Stop-Process -Id $chromaProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

# 2. Python Embedding Service（入口必须是 python_api/main.py，监听 8085 并提供 /api/rag/health）
Write-Host "[2/2] 启动 Python Embedding Service (port 8085) ..."
$pythonBin = Join-Path $VENV_BIN "python.exe"
$mainPy = Join-Path $SCRIPT_DIR "python_api\main.py"

$env:RAG_EMBEDDING_MODEL = Join-Path $SCRIPT_DIR "models\bge-m3"

$embedProcess = Start-Process -FilePath $pythonBin `
    -ArgumentList $mainPy `
    -WorkingDirectory $SCRIPT_DIR `
    -RedirectStandardOutput (Join-Path $LOG_DIR "embedding_service.log") `
    -RedirectStandardError (Join-Path $LOG_DIR "embedding_service_err.log") `
    -NoNewWindow -PassThru
Write-Host "   Embedding PID: $($embedProcess.Id)"

Write-Host "   等待 Embedding Service 就绪（模型加载中，稍候）..."
$logReady = $false
$ready = $false
for ($i = 1; $i -le 180; $i++) {
    if (-not $logReady) {
        # uvicorn 日志输出到 stderr
        $logContent = Get-Content (Join-Path $LOG_DIR "embedding_service_err.log") -ErrorAction SilentlyContinue -Raw
        if ($logContent -and $logContent -match "Uvicorn running") {
            $logReady = $true
            Write-Host "   服务已启动，等待 health check..."
        }
    }
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:8085/api/rag/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "   [OK] Embedding Service 就绪"
        $ready = $true
        break
    } catch {
        if ($i -le 3 -or $i % 30 -eq 0) {
            Write-Host "   [debug][$i] health 失败: $($_.Exception.Message)"
        }
    }
    if ($i % 10 -eq 0) {
        Write-Host "   ...已等待 ${i}s"
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    Write-Host "   [X] Embedding Service 启动超时（360s）"
    Write-Host "   最后 10 行日志:"
    Get-Content (Join-Path $LOG_DIR "embedding_service_err.log") -Tail 10 -ErrorAction SilentlyContinue
    Write-Host "   最后 10 行 stdout:"
    Get-Content (Join-Path $LOG_DIR "embedding_service.log") -Tail 10 -ErrorAction SilentlyContinue
    Stop-Process -Id $chromaProcess.Id, $embedProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  [OK] RAG 服务全部启动"
Write-Host "=========================================="
Write-Host "  ChromaDB:       http://[::1]:8000"
Write-Host "  Embedding API:  http://127.0.0.1:8085"
Write-Host "  健康检查:       http://127.0.0.1:8085/api/rag/health"
Write-Host "=========================================="
Write-Host ""
Write-Host "日志:"
Write-Host "  ChromaDB:  $LOG_DIR\chromadb.log"
Write-Host "  Embedding: $LOG_DIR\embedding_service.log"
Write-Host ""
Write-Host "按 Ctrl+C 停止服务..."

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "正在停止服务..."
    Stop-Process -Id $chromaProcess.Id, $embedProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "已停止"
}
