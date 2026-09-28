# start_rag.ps1 启动故障排查（2026-09-28）

## 需求
`start_rag.ps1` 双击/运行后无法正常启动 RAG 服务，embedding 模型"加载不了"，且多次启动验证耗时过长。

## 根因

### 1. 脚本启动了错误的入口（主因）
- 旧脚本启动 `src\dixiyang\main.py`，它硬编码监听 **8084**（`src/dixiyang/main.py:71`），且没有 `/api/rag/health` 端点。
- 脚本却轮询 `http://localhost:8085/api/rag/health` → 永远失败 → 360s 超时后杀进程退出。
- 正确入口是 `python_api/main.py`（8085，含 health、embed、/rag 可视化），`start_rag.sh` 用的就是它。

### 2. 系统代理劫持 localhost（次因）
- 本机 WinHTTP 代理为 `127.0.0.1:7890`，Bypass List 为空。
- PowerShell 5.1 的 `Invoke-WebRequest` 走代理访问 localhost → `The operation has timed out.`，即使服务已就绪也永远轮询失败。

### 3. 次要问题
- `$env:RAG_EMBEDDING_MODEL = "./models/bge-m3"` 相对路径 + `Start-Process` 无 `-WorkingDirectory` → 换目录运行时模型路径失效。
- 进度检测读 `embedding_service.log`（stdout），而 uvicorn 日志走 **stderr** → 永远匹配不到 `Uvicorn running`。

## 方案（改动均在 `start_rag.ps1`）

| # | 位置 | 改动 |
|---|------|------|
| 1 | 入口 | `src\dixiyang\main.py` → `python_api\main.py` |
| 2 | 代理 | 脚本开头 `$env:NO_PROXY="*"` + `[System.Net.WebRequest]::DefaultWebProxy=$null` |
| 3 | URL | health 改用 `http://127.0.0.1:8085`，并加 `-UseBasicParsing` |
| 4 | 模型路径 | 改为绝对路径 `Join-Path $SCRIPT_DIR "models\bge-m3"`，`Start-Process` 加 `-WorkingDirectory $SCRIPT_DIR` |
| 5 | 日志检测 | `Uvicorn running` 改读 `embedding_service_err.log`；超时时同时打印 stdout/stderr 尾部 |
| 6 | 诊断 | health 失败时每 30 次打印一次真实错误（`[debug][N]`） |

## 改动文件
- `DixyangFast/start_rag.ps1`（唯一改动）

## 验证方式与结果
```powershell
powershell -ExecutionPolicy Bypass -File start_rag.ps1
```
- ChromaDB `[OK] 就绪`，Embedding `[OK] 就绪`（冷启动含 2.27GB bge-m3 加载约 20~40s）
- `GET http://127.0.0.1:8085/api/rag/health` → `{"status":"ok","dimension":1024,"chromadb_connected":true}`
- `POST /api/rag/embed` → 真实向量化成功，维度 1024
- `GET http://[::1]:8000/api/v2/heartbeat` → 200

## 启动耗时说明（为什么"等那么久"）
1. **服务冷启动本身耗时**：加载 `models/bge-m3/pytorch_model.bin`（2.27GB）约 20~40s，这是必要开销。
2. **脚本是常驻型设计**：结尾 `while($true)` 挂起、`Ctrl+C` 停止，进程永不自行退出；任何"等待脚本结束"的验证都会等到超时。正确做法是轮询 health/日志，命中即返回（本机实测 0~40s）。

## 已知问题
- `start_rag.ps1:21` 仅按进程名清理 `chroma`，残留的旧 8085 python 进程需手动清理（或按端口杀：`Get-NetTCPConnection -LocalPort 8085`）。
- 本机 8084 端口存在旧 `src/dixiyang/main.py` 残留进程时会与主 API 冲突，启动前确认无占用。
- PS 5.1 重定向输出文件为 GBK 编码，脚本进度文件用 `[System.Text.Encoding]::GetEncoding(936)` 读取。
