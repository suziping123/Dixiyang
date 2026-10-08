# LLM 接入配置切换（本地 llama-kvmem ↔ DeepSeek）

- 需求：临时把聊天 LLM 从 DeepSeek 官方 API 切到本地 `llama-kvmem` 服务，原配置保留可随时切回
- 日期：2026-09-28
- 涉及模块：`DixyangFast`（Python FastAPI，8084）聊天链路

---

## 一、当前状态（本地模型）

| 项 | 值 |
|----|----|
| 服务地址 | `http://127.0.0.1:18200/v1` |
| 模型名 | `Ternary-Bonsai-2-27B-PTQ1_0.gguf` |
| 模型文件 | `D:\llama-kvmem\model\Ternary-Bonsai-2-27B-PTQ1_0.gguf` |
| API Key | `bonsai-1c25071f3eb54524`（llama-kvmem 启动横幅中的 `Key` 字段，**每次启动可能变化**） |
| 协议 | OpenAI 兼容（`/v1/chat/completions`） |

---

## 二、改动文件

### 1. 根目录 `.env`（LLM 三件套）

```env
# 【当前生效】本地 llama-kvmem
DEEPSEEK_API_KEY=bonsai-1c25071f3eb54524
DEEPSEEK_BASE_URL=http://127.0.0.1:18200/v1
DEEPSEEK_MODEL=Ternary-Bonsai-2-27B-PTQ1_0.gguf

# 【已注释停用】DeepSeek 官方 API
# DEEPSEEK_API_KEY=sk-your-api-key-here
# DEEPSEEK_BASE_URL=https://api.deepseek.com/
# DEEPSEEK_MODEL=deepseek-v4-flash
```

> 变量名沿用 `DEEPSEEK_*`，因为读取方是 `src/dixiyang/config.py:32-34`，改名需同步改代码。

### 2. `src/dixiyang/config.py:9`（关键修复）

```python
load_dotenv(_env_path, override=True)
```

**为什么必须 `override=True`**：本机 **Machine 级系统环境变量**存在
`DEEPSEEK_API_KEY=sk-e046d...`（35 位），`load_dotenv` 默认 `override=False`
**不覆盖已存在的变量** → `.env` 里改了 key 也读不到，实际拿 DeepSeek 真 key
去请求本地服务，返回 `401 Invalid API Key`。

排查命令（只读）：

```powershell
[Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','Machine')   # 系统级
[Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User')      # 用户级
```

---

## 三、如何切回 DeepSeek

编辑根目录 `.env`：

1. 注释掉「当前生效」那 3 行（加 `#`）
2. 取消注释「已停用」那 3 行
3. 把 `DEEPSEEK_API_KEY` 换成真实 `sk-` key（从 https://platform.deepseek.com 获取）
4. **确认 `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL` 也一并放开**——只放 key 不放
   `BASE_URL` 会仍指向 18200 本地端口

无需改代码，重启服务生效。

> 若切换后仍读到旧值，先确认没有别的进程级环境变量覆盖，并重启终端。

---

## 四、前置依赖

本地模型必须先起来，否则聊天接口报连接拒绝：

```powershell
# 启动 llama-kvmem（横幅会打印 Key / 端口 18200）
# 就绪探测：
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:18200/v1/models
# 期望 200（未带 key 时为 401，说明服务已就绪）
```

---

## 五、验证方式

```powershell
# 1. 配置读取
cd DixyangFast
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'src'); from dixiyang.config import *; print(DEEPSEEK_BASE_URL, DEEPSEEK_MODEL)"

# 2. LLM 直调（不依赖 HTTP 服务）
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'src'); from dixiyang.services.chat_service import call_llm; print(call_llm([{'role':'user','content':'只回复两个字：你好'}], max_tokens=30))"

# 3. 服务启动
uv run --no-sync .\src\dixiyang\main.py
# 期望: Uvicorn running on http://0.0.0.0:8084
```

**已验证（2026-09-28）**：
- `POST /v1/chat/completions` 直连返回正常
- `call_llm()` 返回正常
- 服务 `Application startup complete` + 根路径 200

---

## 六、已知问题

0. **`StreamChunkTimeoutError: No streaming chunk received for 120.0s`（2026-09-28 已修）**：
   langchain_openai 默认 `stream_chunk_timeout=120s`，本地 27B 模型长 prompt
   （角色卡+故事节点+历史）首 token 延迟可超 120s，且 `chunks_received=1`
   （只收到流首个 role chunk）即被掐断。
   **修复**：`chat_service.py:get_chat_model()` 加 `stream_chunk_timeout=600`。
   若仍超时，说明 llama-kvmem 侧真卡死，排查模型服务而非调大此值。

1. **本地模型质量/速度**：27B PTQ 模型，单 token 约 13 tok/s，长回复明显慢于云端
2. **`_llm_cache` 缓存**：`chat_service.py:26` 按 `temperature:max_tokens` 缓存
   `ChatOpenAI` 实例，**不含 model/base_url** → 同一进程内切换 `.env` 后
   必须重启服务才生效（开发用 `reload=True` 时改 `.env` 不触发重载，
   `.env` 不在 WatchFiles 监听范围内）
3. **系统级 key 干扰**：Machine 级 `DEEPSEEK_API_KEY` 长期存在，任何绕过
   `config.py`、直接 `load_dotenv()` 的新代码都会踩同样的坑
4. **`requirements.txt` 与 `pyproject.toml` 版本不一致**、**无 `uv.lock`**：
   见启动排错历史，本次未处理
