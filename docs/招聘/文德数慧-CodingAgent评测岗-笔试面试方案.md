# 文德数慧「AI 大模型训练-代码类」评测岗笔试与面试方案

> **适配岗位**：Coding Agent / WebDev 方向大模型评测与轨迹标注（实习，4-5K，成都/宜宾）
> **考察载体**：Dixiyang 全栈 RAG 项目（Vue3 + TypeScript + FastAPI 主后端 + Java Spring Boot 备用后端 + ChromaDB）
> **版本**：v1.0 ｜ **建议时长**：笔试 120 分钟 / 面试 45-60 分钟 ｜ **满分**：笔试 100 + 面试 100
> **适用场景**：校招/实习筛选、外包评测员分级、评测团队入职校准
> **代码基准**：以当前仓库 commit 为准（考试时须锁定 commit/tag）。文中 `file:line` 会随提交漂移，命题前用 `git rev-parse HEAD` 固化。

---

## 0. 岗位拆解：这份卷子到底在考什么

| 岗位职责/要求 | 可观测能力 | 对应题型 | 笔试权重 |
|---|---|---|---|
| 拆解评测 Prompt、编写任务级 Rubric | 任务分解、验收标准设计、可判定性 | D 卷 | 20 |
| 使用 Harness 跑测、搭前端工程环境 | 启动、依赖、端口、日志、可复现 | A 卷 + 实操 | 15 |
| 识别假交互、静态占位、硬编码、功能异常、逻辑错误 | 源码审查 + 运行时取证 + 证据链 | B3 + E 卷 | 25 |
| 复现问题、整理样本/轨迹、输出 badcase | 最小复现、结构化记录、归因 | E 卷 + 实操 | 15 |
| Git、终端、依赖安装、项目启动、日志排查 | 工程基本功 | A 卷 | 15 |
| JavaScript/TypeScript + 前端框架阅读调试 | 代码审查、边界分析 | B1/B2 | 20 |
| Agent/Web/RAG 项目理解、接口契约 | 全栈链路、跨服务排障 | C 卷 | 20 |
| 逻辑严谨、细心、遵循规范、结果一致 | 双评一致性、规范执行 | 全程 + 面试 | 准入项 |

**一句话**：这不是普通前端八股卷，而是让候选人**在真实全栈 RAG 项目里当一天评测员**——找缺陷、写标准、留证据、给结论。

---

## 1. 命题原则（命题人必读）

1. **真项目、真运行**：每题结论必须能落到 `file:line`、Network 请求、后端日志、截图四类证据之一，禁止只凭"看代码感觉"。
2. **三层能力递进**：
   - 发现力：能不能找到模型/代码的缺陷；
   - 标准化力：能不能把缺陷写成别人可复现的 Rubric/badcase；
   - 工程力：能不能独立启动、复现、取证、回归。
3. **答案可验证**：参考答案必须给出操作命令、预期现象、反例；评分点必须二值化或可分级。
4. **反背题**：考试时随机注入 2 个缺陷（见 §8），并改一处默认值/字段名，防止背答案。
5. **区分"演示 mock"与"真实缺陷"**：本项目存在 `VITE_DEMO=1` 的展示模式（`src/utils/demo/`），其中的 mock 是**有意设计**；若候选人把它当真实功能交付，或评测时把 demo 当生产验收，才是 P0。能区分这一点，是本岗位的高分信号。

---

## 2. 考试环境与规则

### 2.1 环境清单

| 项 | 要求 |
|---|---|
| 操作系统 | Windows / macOS 各占 50%，候选人服从分配；允许使用 WSL/Git Bash |
| Node | `^20.19.0 || >=22.12.0`（见前端 `package.json` engines） |
| Python | 3.11 + `uv`（后端 `start_backend.sh` 用 `uv run`） |
| Java | 17（仅备用后端，默认不启动） |
| 浏览器 | Chrome/Edge 最新版，必须会用 DevTools：Network、Console、Application、Performance |
| 可选 | Docker（MySQL/Redis 一键起）、`adb`（移动端真机） |
| 测试账号 | `admin123 / 123456`（本地 dev 库，userId=4，role=user） |

### 2.2 启动方式（以仓库 README 为准）

```bash
# 1) Python 主后端（8084）：认证/小说/角色/时间线/聊天/RAG/广场/后台
./start_backend.sh

# 2) Vue 前端（5173）：/api 代理到 8084
cd dixiyang-vue/Dixiyang-vue3 && npm install && npm run dev

# 3) 可选：RAG 服务（8085）+ ChromaDB（8000），不启动不影响主流程，但检索会降级
cd DixyangFast && ./start_rag.sh
```

> **注意**：`docs/系统总览.md` 写的是"Java 8084 生产、Python 8085"，但当前 `README.md`、`vite.config.ts`、`start_backend.sh`、`docker-compose.yml` 实际是 **Python 主后端 8084、RAG 服务 8085**，Java 为备用且与 Python 同端口二选一。**文档与运行时不一致本身就是本项目的一个真实评测点**（见 C2 延伸）。考试时要求候选人"以运行时和脚本为准，不以文档为准"。

### 2.3 允许与禁止

| 允许 | 禁止 |
|---|---|
| 官方文档、IDE、终端、Git、DevTools | AI 编码助手（Copilot/ChatGPT/Claude 等），闭卷部分尤其严格 |
| `curl`、`jq`、`grep`、`sed` 等排查工具 | 伪造 token、伪造截图/HAR/日志 |
| 查看 `.env.example` | 查看/读取根目录 `.env`（真实凭据） |
| 启动本地服务、造测试数据 | 修改考试基准 commit 后声称"原始代码如此" |

### 2.4 提交物

1. `answers.md`：每题结论 + 证据（命令/路径/截图名）。
2. `fix.patch`：需要改代码的题目提交 diff（`git diff > fix.patch`）。
3. `badcase.json`：E 卷结构化记录（schema 见附录 C）。
4. `evidence/`：截图、HAR、日志片段；截图必须含 URL、时间、Network 面板。
5. `selftest.md`：如何启动、如何复现、回归结果。

> 没有证据的结论按 0 分计；证据与结论不符按作弊处理。

---

## 3. 试卷结构

| 部分 | 题型 | 题数 | 分值 | 建议时长 | 形式 |
|---|---|---:|---:|---:|---|
| A 工程基础与环境 | 简答/命令 | 6 | 15 | 20 min | 闭卷 |
| B 前端代码审查 | 找 bug + 修复 | 3 | 30 | 40 min | 开卷上机 |
| C 全栈契约与后端 | 分析 + 方案 | 2 | 20 | 25 min | 开卷 |
| D RAG 评测 Rubric | 设计题 | 1 | 20 | 25 min | 开卷 |
| E 轨迹标注与 badcase | 结构化记录 | 1 | 15 | 20 min | 开卷 |
| **合计** | | **13** | **100** | **130 min**（可压缩至 120） | |

> 建议实际执行：闭卷 A 20 分钟收卷，再发开卷 B-E 100 分钟；上机实操另设 30 分钟（见 §5，作为面试前置或加试）。

---

## 4. 笔试题目（含答案、解析、评分）

### Part A · 工程基础与环境（15 分）

#### A1（2 分）端口与进程定位

**题目**：现场机器上，前端 5173、Python 主后端 8084、RAG 服务 8085、ChromaDB 8000。请分别写出 Linux/macOS 与 Windows 下检查端口占用的命令；若 8084 被占用，如何判断是 Python 还是 Java 后端？

**参考答案**：

```bash
# Linux / macOS
ss -ltnp | grep -E ':(5173|8084|8085|8000)\b'
lsof -iTCP:8084 -sTCP:LISTEN -P -n
ps -fp <PID>          # 看命令行：uvicorn/python 还是 java/mvn

# Windows PowerShell
Get-NetTCPConnection -State Listen |
  Where-Object LocalPort -in 5173,8084,8085,8000 |
  Select-Object LocalPort,OwningProcess
Get-Process -Id <PID> | Select-Object ProcessName,Path
```

判断依据：Python 主后端命令行含 `uvicorn` 或 `python src/dixiyang/main.py`；Java 含 `java`、`spring-boot:run` 或 `dixiyang-engine`。README 明确两者同端口二选一，不能同时启动。

**解析**：考察终端、进程、端口三件套。只 `netstat` 看 PID 不落到进程名，不给分。常见错误：Windows 用 `findstr 8084` 但不会反查 PID。

**评分**：命令正确 1 分；能落到进程命令行 1 分。

---

#### A2（2 分）Git 精确取文件与历史安全

**题目**：评测脚本在 A 分支。你只想把 commit `abc123` 中 `scripts/run_eval.py` 的版本取到当前工作区，不影响其他文件。写出命令；并说明 `git revert` 与 `git reset --hard` 的区别及使用场景。

**参考答案**：

```bash
git show abc123:scripts/run_eval.py > /tmp/run_eval.py   # 先查看
git restore --source=abc123 -- scripts/run_eval.py        # 工作区 + 索引
# 等价旧写法：git checkout abc123 -- scripts/run_eval.py
```

- `revert`：生成一个反向提交，保留历史，适合已推送的共享分支。
- `reset --hard`：移动当前分支指针并丢弃工作区/索引改动，改写历史，只适合本地未推送。

**解析**：考察"精确取文件"和"不改写共享历史"的工程习惯。常见错误：`git checkout abc123` 进入 detached HEAD 后到处改文件。

**评分**：命令 1 分；区别与场景 1 分。

---

#### A3（3 分）三类启动故障的根因与排查

**题目**：启动后端出现以下三类报错，各写一条最可能根因和排查命令：
1. `ModuleNotFoundError: No module named 'dixiyang'`
2. `Address already in use`
3. 前端请求 404 / CORS

**参考答案**：

| 现象 | 最可能根因 | 排查 |
|---|---|---|
| `ModuleNotFoundError` | 没在项目虚拟环境/工作目录不对，`src` 不在 `sys.path` | `which python`；`uv sync`；`uv run python src/dixiyang/main.py`；`python -c "import sys; print(sys.path)"` |
| `Address already in use` | 端口被占（8084 上 Python/Java 二选一） | `ss -ltnp \| grep 8084` / `lsof -i:8084`；`ps -fp <PID>`；杀进程或换端口 |
| 404 / CORS | Vite proxy 目标错、后端没起、请求路径少了 `/api` 前缀 | DevTools Network 看完整 URL/状态；`curl -i http://localhost:8084/api/...`；核对 `vite.config.ts` 的 `proxy.target` |

**解析**：考察"日志 → 根因 → 命令"的映射，不接受"重启试试"。CORS 在开发环境的正解是走 Vite 同源代理，而不是无脑 `allow_origins=["*"]`。

**评分**：每条 1 分（根因 0.5 + 命令 0.5）。

---

#### A4（2 分）构建闸门与 CI 误判

**题目**：前端 `build` 脚本是 `run-p type-check "build-only {@}" --`。解释 `run-p` 与 `run-s` 的区别；为什么有时 `dist/` 已生成，CI 仍必须判失败？给出验证命令。

**参考答案**：

- `run-p` 并行执行，`run-s` 串行执行。
- `vite build` 本身不做类型检查；`vue-tsc` 失败时 `build-only` 可能已经产出 `dist/`。`run-p` 会聚合非 0 退出码，CI 必须看**进程退出码**，不能看 `dist/` 是否存在。
- 验证：

```bash
npm run type-check; echo "type-check exit=$?"
npm run build;      echo "build exit=$?"
ls dist 2>/dev/null && echo "dist 存在，但不代表类型检查通过"
```

**解析**：考察对"构建成功"的定义。常见错误：把"有 dist"当"能上线"。

**评分**：并行/串行 1 分；退出码与 dist 关系 1 分。

---

#### A5（3 分）真实登录与风控

**题目**：写出用测试账号 `admin123 / 123456` 真实登录、并让前端进入登录态的最小步骤；说明为什么禁止伪造 JWT；列出登录风控的两个限制。

**参考答案**：

```bash
curl -s -X POST http://localhost:5173/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin123","password":"123456"}'
```

在页面上下文写入 6 个键（值取响应 `data`）：

```js
localStorage.setItem('token', data.token)
localStorage.setItem('username', data.user.username)
localStorage.setItem('userId', String(data.user.userId))
localStorage.setItem('nickname', data.user.nickname)
localStorage.setItem('email', data.user.email || '')
localStorage.setItem('role', data.user.role || 'user')
location.reload()
```

**禁止伪造**：前端守卫只解析 JWT 的 `exp`，不验签，假 token 能骗过路由；但任何接口返回 401，axios 拦截器会 `clearAuth()` 并跳登录，而且假数据会写进 `localStorage` 缓存，污染后续验收结论。

**风控**：① 10 分钟内同账号第 3 次密码登录起要求邮箱验证码；② 单点登录会顶号，后登录顶掉先登录。探针应一次登录、复用 token（有效期 7 天）。

**解析**：考察真实环境验证规范与安全意识。允许 `curl`，不允许 `demo.xxx.demo` 假 token。

**评分**：登录命令 1 分；6 个键 1 分；风控/伪造原因 1 分。

---

#### A6（3 分）Harness 与可复现闭环

**题目**：用一句话定义 Harness；用文字画出一次 WebDev 评测的最小闭环；列出至少 4 个必须固定的可复现要素。

**参考答案**：

- **Harness**：驱动被测模型/Agent 在受控环境中执行任务，并采集轨迹、产物与结果判定的评测框架/脚本集合。
- **最小闭环**：固定环境快照 → 注入任务 Prompt → Agent 执行（终端/工具/浏览器）→ 产出代码或页面 → 安装依赖并启动 → 浏览器实测（截图/录屏/HAR/日志）→ 按 Rubric 判定 → 记录 badcase/轨迹 → 汇总指标。
- **固定要素（至少 4 个）**：commit/tag；依赖锁（`package-lock.json`/`uv.lock`）；运行时版本（Node/Python/JDK）；端口与数据快照；浏览器版本；模型版本/温度/随机种子；时区与时钟。

**解析**：考察对"可复现"的理解。只答"跑一下看效果"不得分；能提到"固定模型温度和种子"是加分项。

**评分**：定义 1 分；闭环 1 分；要素 ≥4 个 1 分。

---

### Part B · 前端代码审查（30 分）

> **统一要求**：每题必须给出 `file:line` 或可复现步骤；只写"这里有问题"不给分。

#### B1（10 分）分页参数漂移：为什么第 11 本小说消失了

**材料**：

```ts
// dixiyang-vue/Dixiyang-vue3/src/views/RagAssistantView.vue:449-452
http.get('/novel/listall', {
  params: { page: 1, pageSize: 100 },
})
```

```python
# DixyangFast/src/dixiyang/routers/novel.py:11
async def list_all(page: int = 1, page_size: int = 10, ...):
```

```java
// dixiyang-engine/.../NovelController.java:32
@RequestParam(defaultValue = "10") int pageSize
```

**现象**：用户有 11 本小说，RAG 助手的小说下拉只显示 10 本；知识库文档分页"看起来正常"。

**题目**：
1. 定位根因，并解释为什么知识库页面暂时没暴露。
2. 给出兼容 Python/Java 两套后端的修复方案（前端/后端/契约层任选），说明取舍。
3. 写一条 5 分钟内可完成的验证步骤。

**参考答案**：

1. **根因**：FastAPI 的查询参数名是 `page_size`，前端传的 `pageSize` 被忽略，回落到默认值 10；RAG 助手只请求第一页且没有"加载更多"，所以第 11 本永久不可见。知识库页传 `pageSize=20`，恰好等于 Python 默认值 20，被默认值掩盖；一旦改页大小或后端默认值就会暴露。Java 端使用 `pageSize`，所以**不能只把前端改成 `page_size`**，否则切 Java 会回归。

2. **修复方案与取舍**：
   - **方案 A（推荐）契约统一**：后端同时接受两种命名（FastAPI 显式声明两个参数或使用别名；Java 增加 `page_size` 别名），前端只发一种；补 OpenAPI/JSON Schema 与契约测试。一次改两端，长期最稳。
   - **方案 B 前端适配层**：按后端类型注入参数名。快，但把后端差异泄漏到每个调用点，长期腐化。
   - **方案 C 网关/BFF 归一化**：适合双后端共存期，成本最高但调用方无感。

3. **验证**：
   - 造 11 本小说（或直接把 Python 默认 `page_size` 改成 5 放大现象）。
   - 打开 RAG 助手 → Network 看 `/novel/listall` 的实际 query 与响应 `records.length/total`。
   - 切到 Java 后端重复一次；断言 11 本都出现。
   - 知识库页把 `pageSize` 改成 5，验证分页按钮与总数。

**解析**：本题是"默认值掩盖 + 双实现漂移"的典型。高分答案会指出 `pageSize=20` 的巧合，并强调"不能盲改前端"。

**评分**：根因 4 分（参数名 1、默认值 1、掩盖 1、双后端 1）；修复 4 分（方案 2、取舍 2）；验证 2 分。

---

#### B2（10 分）业务 500 被 resolve：页面崩溃与静默失败

**材料**：

```ts
// dixiyang-vue/Dixiyang-vue3/src/utils/http.ts:54-56
// 3. 对象直接返回，无论 code 是 200 还是 500，都由调用者自己判断
return res
```

```ts
// dixiyang-vue/Dixiyang-vue3/src/views/RagKnowledgeView.vue:188-206
const res = await getRagStats()
stats.value = res.data                    // data 可能为 null
const data = res.data as RagDocPage
docs.value = (data.ids || []).map(...)    // data 为 null 时抛错
```

**题目**：后端返回 `{ code: 500, msg: '...', data: null }` 时，页面会发生什么？列出至少 2 个具体故障点；给出修复原则；写 3 条验证用例。

**参考答案**：

- **机制**：axios 响应拦截器只对 401 做 reject，其他业务码（包括 500）一律 resolve，调用方必须自己检查 `code`。RAG 知识库页三个请求都没有检查。
- **故障点**：
  1. `stats.value = null`，模板访问 `stats.total_documents` 触发渲染错误/空白。
  2. `data.ids` 抛 `TypeError`，被 `catch` 吞掉只 `console.error`，用户看到旧列表或空列表，没有任何错误提示。
  3. 搜索失败时 `searchResult` 不更新，页面无反馈。
  4. Java 端 `getStats` 捕获异常后仍返回 `Result.success({connected:false,error:...})`，HTTP 200、业务码 200，前端完全感知不到失败。
- **修复原则**：统一 `unwrap/assertOk`（`code !== 200` 抛业务错误或返回 Result），页面设置 `error` 状态 + 重试按钮，**保留旧数据**；区分 `connected:false`（服务不可用）与"检索结果 0 条"（正常空态）；不要用可选链把失败吞成空。
- **验证用例**：
  1. mock `{code:500,data:null}` → 页面不崩、有错误提示、旧统计不丢。
  2. mock HTTP 500（无规范 body）→ 走网络错误分支，提示重试。
  3. mock `{code:200,data:{connected:false,error:'...'}}` → 显示离线态，而不是只显示"—"。

**解析**：HTTP 状态码 ≠ 业务码；"静默失败"是评测中最难发现的缺陷之一。只加 `?.` 是掩盖，不是修复。

**评分**：机制 3 分；故障点 3 分（每点 1，最多 3）；修复 2 分；验证 2 分。

---

#### B3（10 分）假交互、静态占位、硬编码识别

**题目**：给你 20 分钟，在本仓库中找出至少 3 处"假交互/静态占位/硬编码/语义不一致"，要求给出 `file:line` + 复现步骤 + 证据类型（Network/源码/截图/日志）。特别说明：哪些是**有意的演示 mock**，不能误判为缺陷。

**参考答案（任答 3 处即可）**：

| # | 位置 | 现象 | 证据 |
|---|---|---|---|
| 1 | `src/views/HomeView.vue:306-308` | 选择小说后用 `setTimeout(..., 800)` 假装 RAG 加载，未发请求 | 源码 + Network 无请求 |
| 2 | `src/views/HomeView.vue:345-348` | `showKnowledgeGraph` 只有 `// TODO`，但知识球可点击 | 源码 + 点击无反应 |
| 3 | `src/components/chat/ChatMessage.vue:278-282` | 点击"引用来源"只写剪贴板，无 toast/跳转，用户感知无效 | 源码 + 复现 |
| 4 | `src/views/RagAssistantView.vue:101-109` | "启用 RAG 检索"开关关闭后，后端仍注册 `knowledge_search`（`chat.py:303-304`），检索没真关 | 前后端对照 |
| 5 | `src/utils/demo/adapter.ts:115-118` | 保存/删除返回"假"成功；`VITE_DEMO=1` 时全站 mock | 源码 + Network 不出网 |
| 6 | `src/views/RagKnowledgeView.vue` 文案"查看和管理" | 页面没有上传/删除入口，属于**功能缺失**，不是假交互 | 源码 + UI |

**演示 mock 的区分**：

- `src/utils/demo/index.ts` 定义 `IS_DEMO = import.meta.env.VITE_DEMO === '1'`，仅 gh-pages 展示构建为真；`adapter.ts` 的 mock 响应、`fetchStub.ts` 的假 SSE 都是**有意设计**。
- 判定规则：如果构建是 `VITE_DEMO=1` 的展示包，mock 不算缺陷；如果**真实交付/生产验收**中出现 mock、假成功、固定数据，则记 P0。
- 第六项"缺少上传入口"要归为"功能未实现"，不要与"假交互"混为一谈——这就是标注分类的严谨性。

**解析**：本题直接对应岗位职责 3。评分重点不是"找得多"，而是**证据链完整、分类准确、不误报**。

**评分**：每处 3 分（定位 1、复现 1、证据 1），最多 9 分；能正确区分演示 mock/功能缺失加 1 分。误报一处扣 1 分。

---

### Part C · 全栈契约与后端（20 分）

#### C1（10 分）SSE 生命周期、线程池与取消

**材料**：

```java
// dixiyang-engine/.../ChatController.java:124-215（节选）
SseEmitter emitter = new SseEmitter(1800000L);
ExecutorService executor = Executors.newSingleThreadExecutor();
...
flux.subscribe(
  token -> sendEvent(emitter, "content", token),
  error -> { sendEvent(emitter, "error", ...); sendEvent(emitter, "done", null); },
  () -> { sendEvent(emitter, "done", null); emitter.complete(); }
);
latch.await();
```

```java
private void sendEvent(SseEmitter emitter, String type, String delta) {
    try {
        emitter.send(...);
    } catch (Exception e) {
        // 静默忽略
    }
}
```

**题目**：列出至少 4 个生产风险；给出修复方案；说明如何验证"客户端断开后上游真的停止"。

**参考答案**：

| # | 风险 | 修复 |
|---|---|---|
| 1 | 每请求 `Executors.newSingleThreadExecutor()`，线程池不回收，100 并发 = 100 个池 | 使用共享有界线程池（`ThreadPoolTaskExecutor`），设置队列与拒绝策略 |
| 2 | `latch.await()` 无超时，上游卡住时 Servlet 线程永久阻塞 | `await(timeout)`；超时发 `error` + `done`，并取消上游 |
| 3 | 未注册 `onTimeout/onCompletion/onError`，客户端断开后仍向已完成的 emitter 发送 | 注册三个回调，统一清理；`done` 幂等，只发一次 |
| 4 | 没有取消传播，客户端 abort 后 Flux 继续跑，浪费 token/算力 | 保存 `Disposable`，在完成/异常/超时/断开时 `dispose()` |
| 5 | `sendEvent` 吞异常，数据丢失无日志 | 记录日志并触发清理，不继续盲目推送 |

**验证**：

- Chrome DevTools 发起 SSE 后点停止，或 `curl --max-time 2` 主动断开。
- 后端日志应出现断开/取消记录；`jstack` 看线程是否回收。
- 用 mock 上游延迟 60s，断言 2s 内取消，不继续产生 token。
- 100 并发压测，线程数不随请求数线性增长；正常/异常/超时三条路径都只出现一次 `done`。

**解析**：SSE = 长连接 + 异步 + 客户端随时断开，三个坑叠加。高分答案会区分"客户端断开"与"业务超时"，并强调 `done` 幂等。

**评分**：风险 4 分（每条 1）；修复 4 分；验证 2 分。

---

#### C2（10 分）RAG 静默降级与分数语义

**材料**：

```python
# routers/rag.py:148
f"{RERANKER_URL}/api/rag/rerank"

# services/knowledge_search_tool.py:35
f"{reranker_url}/api/rerank"

# python_api/main.py:104（真实端点）
@app.post("/api/rag/rerank")
```

```python
# routers/rag.py:187-189 / knowledge_search_tool.py:64-75
candidates = [(doc.page_content, 1.0 - score, doc.metadata) ...]
```

**题目**：找出至少 2 个不一致/失真点；说明对评测结论的影响；给出修复与验证方案。

**参考答案**：

1. **Reranker 路径不一致（P0 级静默降级）**：真实端点是 `/api/rag/rerank`；`knowledge_search_tool` 调 `/api/rerank`，恒 404。异常被 `except` 吞掉后回退为向量原始排序。**Agent 检索质量下降，但界面/日志一切正常**——这是评测系统最危险的"静默降级"。
2. **分数语义失真**：Chroma 返回 cosine distance，`1.0 - distance` 是相似度，可能为负；前端把 `score` 当百分比展示，会误导为"置信度"。应 clamp 到 `[0,1]`，文案改为"相似度"，或使用校准后的分数。
3. **其他可加分点**：
   - `rag.py` 在 `async def` 中同步调用 `httpx.post`，阻塞事件循环；应改 `httpx.AsyncClient`。
   - Java `RagService` 找不到目标 collection 时回退到第一个 collection，可能返回错误知识库内容（串库）。
   - rerank 失败时没有 `degraded:true / reranked:false` 标记，无法从结果判断是否降级。
4. **修复**：路径常量化 + 启动健康检查；失败返回降级字段；分数 clamp + 文案；异步客户端；collection 不存在时 fail closed。
5. **验证**：停掉 8085 → 搜索应返回 `degraded:true` 而不是静默；对比 rerank 前后 topK 顺序；单测 mock 404 断言降级字段；检查前端展示是否仍误导。

**延伸（面试可追问）**：`docs/系统总览.md` 说 Java 是生产、Python 是 8085，但 README/脚本实际是 Python 主后端 8084、RAG 服务 8085。**文档漂移**会让评测环境搭错，属于"可复现性"风险。

**解析**：考察跨服务契约、静默失败、指标语义。高分答案能说出"评测最怕的不是报错，而是看起来成功"。

**评分**：不一致点 4 分（每点 2）；影响 3 分；修复 2 分；验证 1 分。

---

### Part D · RAG 评测 Rubric 设计（20 分）

#### D1（20 分）给"知识库上传"写任务级评测标准

**背景**：产品要求在 `/rag-knowledge` 增加"上传 Markdown/TXT 文档入库"能力。现在有一份**模型生成的实现**：只加了上传按钮和 `setTimeout` 进度条，成功后前端 `push` 一条固定记录；刷新后消失；Network 无请求；后端无日志。

**题目**：

1. 把需求拆成可评测的 Prompt（角色/目标/输入/约束/验收/禁止/输出）。
2. 写任务级 Rubric：维度、权重、判定证据、一票否决、通过线。
3. 说明如何用 Harness 采集证据，避免把"演示 mock"误判为通过。

**参考答案**：

**1）Prompt 拆解**

| 要素 | 内容 |
|---|---|
| 角色 | 资深 Vue3 + 全栈工程师，熟悉 Element Plus、TypeScript、FastAPI |
| 目标 | 在现有 Dixiyang 项目实现真实的"上传 → 切分 → 向量化 → 入库 → 列表/统计刷新"闭环 |
| 输入 | 仓库 commit、现有 `/rag` 接口、测试账号 `admin123/123456`、允许上传 `.md/.txt` |
| 约束 | 不改无关模块；复用现有 `http` 封装与组件风格；类型安全；移动端可用；不引入新重型依赖 |
| 验收 | 选择文件 → 类型/大小校验 → 真实上传请求 → 后端入库 → 列表与统计 +1 → 刷新/重启后仍在 → 失败有提示 |
| 禁止 | mock/硬编码/假进度/只改前端/绕过鉴权/删除或覆盖他人数据 |
| 输出 | `git diff` + 启动命令 + 自测记录（含截图/HAR） |

**2）任务级 Rubric**

| 维度 | 权重 | 判定证据（必须可复现） | 0 分 | 1 分 | 2 分 |
|---|---:|---|---|---|---|
| 功能闭环 | 30 | HAR 有真实上传请求；后端日志有入库；Chroma count/documents 总数 +1；刷新后仍在 | 无请求/无入库 | 前端有请求但后端未落库 | 全链路闭环 |
| 真实性与反作弊 | 20 | 无 `setTimeout` 假进度、无固定数组、无 mock adapter；重启后数据仍在；多用户隔离 | 存在造假 | 部分真实 | 完全真实 |
| 错误与边界 | 15 | `.exe`/空文件/超大文件/重复文件/401/500/断网/取消 | 未处理 | 处理 3 类 | 处理 6 类且提示清晰 |
| 状态一致性 | 15 | loading/disabled/成功提示/列表与统计同步/分页正确 | 状态错乱 | 基本同步 | 全状态闭环 |
| 可用性 | 10 | 拖拽/键盘/移动端/大文件提示 | 不可用 | 桌面可用 | 桌面+移动端 |
| 代码质量 | 10 | 类型、复用、无 `console.log`、无泄漏、可维护 | 差 | 中 | 好 |

**一票否决（任一触发即 0 分，不管其他项多高）**：

- 假上传：只弹 toast/只改前端状态，没有真实请求或没有落库。
- 硬编码列表/固定统计数字。
- 用 `VITE_DEMO=1` 的 mock 冒充真实交付。
- 删除/覆盖他人数据、绕过鉴权、路径穿越。

**通过线**：总分 ≥ 70/100，且"功能闭环"≥ 24/30，且无一票否决。

**3）Harness 取证**

- **前置**：记录 Chroma `count`、`/rag/documents` 的 `total`、当前用户文档数；保存基线截图。
- **执行**：固定账号真实登录 → 上传固定文件（含中文/大文件/重复文件）→ 采集 HAR、Console、后端日志、截图/录屏。
- **后置**：再查 `count/total`；刷新页面；重启服务再查（验证持久化）；换第二个账号验证隔离。
- **反例**：断网、停后端、传 `.exe`、传 0 字节、重复上传、未登录、401 过期。
- **判定**：每条 Rubric 绑定证据文件名；双评；分歧仲裁；把"证据缺失"判为不通过，而不是"看起来可以"。

**解析**：这是本岗位最核心的题。评分看"可判定性"——标准必须能让另一个标注员复现。空泛的"界面美观、体验流畅"不得分；没有一票否决的 Rubric 直接扣分。

**评分**：Prompt 5 分（结构完整 2、禁止项 1、验收可测 2）；Rubric 10 分（维度 3、权重 2、证据 3、否决与通过线 2）；Harness 5 分（前后置 2、反例 2、双评 1）。

---

### Part E · 轨迹标注与 badcase 记录（15 分）

#### E1（15 分）把"假上传"写成可复现 badcase

**题目**：给定轨迹——模型声称"已完成知识库上传"，实际只在前端加按钮，点击后 1.5s 显示"上传成功"，列表 push 一条固定数据；刷新后消失；Network 无请求；后端无日志。请：

1. 按附录 C 的 schema 输出一条 `badcase.json`；
2. 判定严重级别并说明理由；
3. 给出归因标签、根因、修复建议；
4. 说明团队如何保证标注一致性。

**参考答案**：

```json
{
  "badcase_id": "webdev-rag-upload-0001",
  "task_id": "rag-knowledge-upload-v1",
  "model": "candidate-webdev-agent",
  "commit": "<locked-sha>",
  "env": {
    "os": "Windows 11 / macOS 14",
    "node": "22.x",
    "python": "3.11",
    "browser": "Chrome 13x",
    "mode": "real (VITE_DEMO=0)"
  },
  "severity": "P0",
  "category": ["假交互", "硬编码", "功能异常", "无持久化"],
  "title": "知识库上传为假实现：无真实请求、无落库、刷新即消失",
  "preconditions": "已用 admin123 真实登录；进入 /rag-knowledge；VITE_DEMO=0",
  "steps": [
    "打开 DevTools Network，清空请求",
    "点击上传，选择 test.md",
    "等待 1.5s，出现『上传成功』",
    "观察列表新增一条固定记录",
    "刷新页面",
    "查看后端日志与 Chroma count"
  ],
  "expected": "产生真实上传请求；后端完成切分/向量化/入库；列表与统计 +1；刷新/重启后仍存在；失败有错误提示",
  "actual": "无网络请求；前端 setTimeout 假进度；列表 push 固定数据；刷新后消失；后端无日志；Chroma count 不变",
  "evidence": {
    "screenshot": "evidence/upload-fake-success.png",
    "har": "evidence/upload.har",
    "console": "evidence/console.log",
    "backend_log": "evidence/backend-empty.log",
    "count_before_after": "evidence/chroma-count.txt"
  },
  "root_cause": "只实现 UI 层，未接后端 ingest；未做真实请求、持久化与错误处理；用前端状态伪造成功",
  "reproducibility": "100%（3/3）",
  "suggested_fix": "补后端 ingest（chunk→embed→upsert→metadata）；前端真实上传并绑定请求状态；失败回滚；刷新校验；补权限与文件校验",
  "rubric_ref": ["功能闭环", "真实性与反作弊", "错误与边界"],
  "labels": ["webdev", "vue3", "rag", "fake-interaction", "hardcoded"],
  "annotator": "A01",
  "review_status": "pending"
}
```

**严重级别**：

- **P0**：核心功能完全造假、数据损坏、安全越权、演示 mock 冒充真实交付。
- **P1**：主流程可用但关键分支错误/静默失败/无持久化。
- **P2**：体验、文案、边缘展示问题。

本案例为 **P0**：核心功能"上传入库"完全未实现，且伪造成功，直接误导验收。

**一致性保证**：

- 统一字段字典与标签体系（假交互/静态占位/硬编码/功能异常/逻辑错误/无持久化）。
- 预标注校准集 + 培训；双评同一样本；分歧仲裁并回写规范。
- 监控 Cohen's Kappa / 一致率（建议 ≥ 0.6）；每周抽检 10%。
- 证据缺失按"不通过"处理，禁止凭印象补结论。

**解析**：考察"发现 → 复现 → 结构化 → 归因 → 反馈"的完整链路。只会写"上传是假的"不给高分；必须让另一个工程师按步骤 100% 复现。

**评分**：JSON 字段完整 5 分；级别与归因 4 分；复现步骤与证据 3 分；一致性与修复 3 分。

---

## 5. 上机实操（面试前置，30 分钟，独立 20 分）

> 目的：验证候选人能否**独立**把项目跑起来并复现问题。可安排在笔试前或面试前，不计入笔试 100 分，作为同分排序/准入依据。

| 任务 | 要求 | 分值 |
|---|---|---:|
| T1 启动 | 启动 Python 8084 + Vue 5173；真实登录；进入 `/rag-knowledge`；截图含 URL | 6 |
| T2 复现 | 造 11 本小说（或改默认值放大），复现 B1 的分页缺陷；录 Network + 截图 | 7 |
| T3 记录 | 输出 `badcase.json` + 200 字报告（现象/根因/影响/建议） | 7 |

**评分要点**：

- 能独立解决依赖/端口/代理问题（可查官方文档，不可问考官答案）。
- 复现必须**可重复**：换一个浏览器/刷新后仍能复现。
- 报告必须区分"现象"与"根因"，不能把"下拉只有 10 条"直接当根因。

**常见失败**：

- 直接改代码绕过问题，未记录原始现象。
- 只截图 UI，不截 Network/响应。
- 把"文档写 8085"当运行时事实，导致代理配错。

---

## 6. 面试环节（45-60 分钟，100 分）

### 6.1 结构

| 环节 | 时长 | 分值 | 形式 |
|---|---:|---:|---|
| 技术深挖 | 25 min | 40 | 8 题，追问 2-3 层 |
| 现场排障 | 15 min | 30 | 给一个真实小 bug，讲思路并动手 |
| 行为与规范 | 10 min | 30 | 情境题，看耐心/一致性/服从安排 |

### 6.2 技术深挖（8 题）

#### Q1 如何判断一个页面是"真实现"还是"模型糊出来的"？

**参考答案**：五查——

1. **查网络**：有没有真实请求？请求参数/响应码/响应体是否合理？
2. **查持久化**：刷新、重启、换账号、换设备后数据还在吗？
3. **查状态机**：loading/disabled/成功/失败/重试是否闭环？按钮连点会怎样？
4. **查源码**：`TODO`、`mock`、`setTimeout`、硬编码数组、`console.log`、未使用的 API。
5. **查边界**：空数据、超长、慢网、401/500、并发、无权限。

再对照产品文案与后端日志：文案说"已保存"，后端有没有写库？

**解析**：考察系统化方法。只答"看代码有没有 mock"不够，必须覆盖运行时与持久化。

#### Q2 点"停止生成"后，怎样保证前后端都真的停了？

**参考答案**：前端 `AbortController.abort()` → fetch reject → 不再 enqueue；后端在 `onCompletion/onError/onTimeout` 或 async generator 的 `CancelledError` 中取消上游订阅（Flux `Disposable.dispose()` / 停止 LLM 流），清理线程与 emitter；`done` 只发一次；验证看后端 token 是否停止消耗、线程是否回收、日志是否有取消记录。

**解析**：端到端取消，不是只把 UI 的 loading 关掉。

#### Q3 什么样的 Rubric 才算"可判定"？

**参考答案**：每条 = 可观测行为 + 证据类型 + 二值/等级标准 + 前置条件；避免"美观/流畅/合理"；写清反例与一票否决；两个标注员按同一证据能得出同一结论。

**解析**：本岗位的核心交付物。能举出"刷新后数据仍在"这种可验证条款，比空谈权重更加分。

#### Q4 RAG 检索效果怎么评？

**参考答案**：

- **离线**：黄金集（query → 相关 chunk），算 Recall@k、MRR、nDCG；分层看切分、embedding、召回、rerank。
- **端到端**：引用正确率、答案是否被引用支撑（groundedness）、忠实度、拒答率、延迟。
- **在线**：点击、追问、采纳率、失败样本回流。
- **定位**：召回有但答案错 → 生成问题；召回就没有 → 切分/embedding/索引问题。

**解析**：能区分"检索指标"与"生成指标"，并知道先定位再调参。

#### Q5 两套后端参数名不一致，如何系统性避免？

**参考答案**：单一契约源（OpenAPI/JSON Schema）；契约测试（同一请求打两套后端，断言 schema + 语义）；CI 阻断；版本化与废弃期；前端适配层只保留一处；文档从代码生成，不手写。

**解析**：结合 B1，看是否有"机制"思维，而不是每次手工修。

#### Q6 评测如何保证可复现？

**参考答案**：commit/tag + lockfile + 容器镜像；固定 Node/Python/JDK/浏览器；固定端口与数据快照；固定模型版本/温度/seed；一键脚本；保存 HAR/日志/截图/录屏；环境变更写进报告。

**解析**：Harness 的基础。能提到"数据快照"和"模型温度"是加分项。

#### Q7 模型生成的代码"能跑但逻辑错"，怎么发现？

**参考答案**：Oracle/差分测试（对照参考实现/旧版本）；边界与异常注入；属性测试；变异测试；业务走查；日志与数据对账；多角色/多租户；刷新/重启持久化；并发与重复提交。

**解析**：这是评测岗的核心难点——"能打开"不等于"做对了"。

#### Q8 标注一致性怎么保证？

**参考答案**：规范 + 字段字典 + 校准集；双评 + 仲裁；Kappa/一致率监控；定期抽检；争议回流规范；版本化规范；新人先过校准集再上岗。

**解析**：岗位要求"保证标注结果一致性"，答不出 Kappa/双评基本不及格。

### 6.3 现场排障（30 分）

**题目**：知识库页面点"搜索"没反应。给你 10 分钟定位，边操作边讲思路。

**参考路径**：

1. 复现：输入关键词，点搜索，观察 UI 是否有 loading。
2. Network：请求有没有发出？URL/参数（`query/topK/source_filter`）对不对？状态码？
3. Console：有无 JS 异常（如 `data.ids` 空指针）。
4. 后端日志：有没有收到请求？是否 500/超时？
5. 判定：前端未发 / 参数错 / 业务码未处理 / 后端异常 / 检索空结果。
6. 最小修复 + 回归：成功、空结果、500 三条路径。

**评分**：复现 3；定位 5（能否用证据排除分支）；修复 3；回归 4。

### 6.4 行为与规范（30 分）

#### Q1 规范要求判 P1，你觉得是 P2，怎么办？

**参考**：先按规范执行并记录分歧；用证据（影响面/可复现性/数据风险）提出规范改进；不擅自改标签；走仲裁；把案例沉淀到规范。

#### Q2 连续标注 8 小时，如何保持质量？

**参考**：分批 + 校准样本 + 双评抽检；记录疲劳点；不追求速度牺牲一致性；发现漂移主动要求复核。

#### Q3 发现同事标注与你不一致？

**参考**：先对照规范与证据讨论；不能达成一致找仲裁；不私下修改他人结果；把分歧变成规范条款。

#### Q4 设备 Windows/Mac 各半，你只会其中一个？

**参考**：接受分配；强调可迁移能力（Git/Node/Docker/终端）；愿意学；不因设备挑活。

**评分维度**：规范意识 10；沟通与证据 10；稳定性/服从性 10。

---

## 7. 评分、通过线与录用建议

### 7.1 总分构成

| 项 | 权重 | 说明 |
|---|---:|---|
| 笔试 | 60% | A15 + B30 + C20 + D20 + E15 |
| 面试 | 40% | 技术 40 + 排障 30 + 行为 30 |
| 实操 | 同分排序 | 20 分，不计入总分；低于 12 分不予录用 |

**总分 = 笔试 × 0.6 + 面试 × 0.4**

### 7.2 通过线

| 等级 | 条件 | 建议 |
|---|---|---|
| 优秀 | 总分 ≥ 80，D ≥ 16/20，E ≥ 12/15，实操 ≥ 16/20 | 优先录用，可带新人 |
| 合格 | 总分 ≥ 65，笔试 ≥ 60，面试 ≥ 60，实操 ≥ 12/20 | 录用，进入试用期校准 |
| 待定 | 总分 55-65，或 D/E 明显偏弱 | 加试一次 Rubric + badcase |
| 不合格 | 总分 < 55，或触发一票否决 | 不录用 |

### 7.3 一票否决

- 伪造截图/HAR/日志/复现结果。
- 无法独立启动环境（实操 < 8 分）。
- 拒绝按规范标注、擅自改标签且不沟通。
- 抄袭、泄露题库、使用 AI 助手代答（闭卷部分）。
- 把演示 mock 当真实功能交付且被指出后仍狡辩。

### 7.4 双评一致性

- 抽取 10 份同一 badcase/页面样本，两位评测员独立打分。
- 计算 Cohen's Kappa（分类标签）与组内相关系数（分数）；**Kappa ≥ 0.6** 才认为评分可信。
- 低于 0.6：重新校准规范/样例，再评；仍低则调整题目或评分粒度。

---

## 8. 反作弊与题库维护

1. **锁定基准**：考试前 `git tag exam-YYYYMMDD`，所有题目引用该 tag 的行号；考后对比 `git diff`，防止候选人改代码后声称"原代码如此"。
2. **随机注入**：从缺陷池随机选 2 个注入（如：把 `page_size` 改回 `pageSize`、把 reranker 路径改错、把 `setTimeout` 假 loading 加回去、把业务码 500 改成 resolve），防止背答案。
3. **现场变体**：改默认值/字段名/端口，要求候选人重新定位，而不是复述记忆。
4. **证据校验**：截图必须含 URL、时间、Network；HAR 用工具校验请求时间与响应；后端日志与前端时间对齐。
5. **AI 使用策略**：闭卷 A 禁用；开卷 B-E 允许查官方文档，禁用 AI 编码助手；面试追问"你是怎么得到的"，答不出过程即降档。
6. **题库轮换**：每季度替换 30% 题目；保留 B1/B2/D1 作为核心稳定题，便于横向对比。

---

## 9. 附录

### 附录 A · 考试材料清单

| 材料 | 说明 |
|---|---|
| 仓库快照 | 锁定 commit/tag，含 `dixiyang-vue`、`DixyangFast`、`dixiyang-engine`、`docs` |
| 启动脚本 | `start_backend.sh`、`start_rag.sh`、前端 `npm run dev` |
| 测试账号 | `admin123 / 123456`；说明风控与顶号 |
| 测试数据 | 11 本小说、21 条知识库文档、1 个 `.md` 上传样例、1 个 `.exe` 反例 |
| 工具 | Chrome DevTools、`curl`、`jq`、`git`、可选 Docker |
| 提交模板 | `answers.md`、`badcase.json`、`fix.patch`、`evidence/` |

### 附录 B · 60 分钟精简卷（快速筛选）

| 题 | 分值 | 说明 |
|---|---:|---|
| A5 真实登录 | 5 | 不会登录直接淘汰 |
| B1 分页漂移 | 20 | 核心代码审查 |
| B3 假交互识别 | 20 | 岗位核心能力 |
| D1 Rubric（只写维度+一票否决+通过线） | 25 | 标准化能力 |
| E1 badcase（只写 JSON 核心字段） | 20 | 复现与记录 |
| 合计 | 90 | 60 分钟；≥ 55 分进入面试 |

### 附录 C · badcase JSON Schema

```json
{
  "badcase_id": "string，全局唯一",
  "task_id": "string，任务/样本 ID",
  "model": "string，被测模型/Agent 版本",
  "commit": "string，代码基准 SHA",
  "env": {
    "os": "string",
    "node": "string",
    "python": "string",
    "browser": "string",
    "mode": "real | demo"
  },
  "severity": "P0 | P1 | P2",
  "category": ["假交互", "静态占位", "硬编码", "功能异常", "逻辑错误", "无持久化", "安全"],
  "title": "string，一句话现象",
  "preconditions": "string，账号/数据/构建模式",
  "steps": ["string，最小复现步骤"],
  "expected": "string，期望行为",
  "actual": "string，实际行为",
  "evidence": {
    "screenshot": "path",
    "har": "path",
    "console": "path",
    "backend_log": "path",
    "video": "path",
    "count_before_after": "path"
  },
  "root_cause": "string，根因（不是现象复述）",
  "reproducibility": "string，如 3/3",
  "suggested_fix": "string",
  "rubric_ref": ["string"],
  "labels": ["string"],
  "annotator": "string",
  "review_status": "pending | agreed | disputed"
}
```

**字段要求**：

- `severity` 必须有明确判据（见 E1）。
- `category` 至少 1 个，最多 3 个；禁止"其他"兜底。
- `root_cause` 不得与 `actual` 重复。
- `evidence` 至少包含截图 + 一个运行时证据（HAR/日志/console）。
- `reproducibility` 必须写实际次数，如 `3/3`、`1/3`。

### 附录 D · Rubric 模板

| 维度 | 权重 | 判定证据 | 0 分 | 1 分 | 2 分 |
|---|---:|---|---|---|---|
| 功能闭环 | 30 | 真实请求 + 落库 + 刷新后仍在 | 无 | 部分 | 完整 |
| 真实性与反作弊 | 20 | 无 mock/硬编码/假进度 | 造假 | 部分 | 真实 |
| 错误与边界 | 15 | 类型/大小/空/重复/401/500/断网 | 0-2 类 | 3-4 类 | 5+ 类 |
| 状态一致性 | 15 | loading/disabled/成功/失败/分页 | 错乱 | 基本 | 闭环 |
| 可用性 | 10 | 拖拽/键盘/移动端 | 不可用 | 桌面 | 双端 |
| 代码质量 | 10 | 类型/复用/无日志/无泄漏 | 差 | 中 | 好 |

**一票否决**：假上传、硬编码、mock 冒充真实、越权/删数据。

**通过线**：≥70，且功能闭环 ≥24/30，且无一票否决。

### 附录 E · 评分表

| 考生 | A/15 | B/30 | C/20 | D/20 | E/15 | 笔试 | 面试 | 总分 | 实操/20 | 结论 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
|  |  |  |  |  |  |  |  |  |  |  |

**评委签名**：__________  **日期**：__________

### 附录 F · 关键代码位置速查

| 主题 | 位置 |
|---|---|
| 前端 SSE/取消/会话竞态 | `dixiyang-vue/Dixiyang-vue3/src/composables/useChatStream.ts` |
| 前端 401/业务码拦截 | `dixiyang-vue/Dixiyang-vue3/src/utils/http.ts` |
| RAG 知识库页 | `dixiyang-vue/Dixiyang-vue3/src/views/RagKnowledgeView.vue` |
| RAG 助手页 | `dixiyang-vue/Dixiyang-vue3/src/views/RagAssistantView.vue` |
| 演示 mock | `dixiyang-vue/Dixiyang-vue3/src/utils/demo/` |
| Python 主后端 RAG | `DixyangFast/src/dixiyang/routers/rag.py` |
| Python 检索工具 | `DixyangFast/src/dixiyang/services/knowledge_search_tool.py` |
| Python 聊天/工具循环 | `DixyangFast/src/dixiyang/routers/chat.py` |
| Java SSE | `dixiyang-engine/src/main/java/com/dixiyang/server/Controller/ChatController.java` |
| Java 链式文件存储 | `dixiyang-engine/src/main/java/com/dixiyang/server/Service/ChatContentFileService.java` |
| Java 安全配置 | `dixiyang-engine/src/main/java/com/dixiyang/server/Config/SecurityConfig.java` |
| RAG 离线流水线 | `docs/RAG离线构建流程.md` |
| 开发环境/测试账号 | `docs/开发环境与测试账号.md` |

### 附录 G · 命题检查清单

- [ ] 题目引用的 commit/tag 已锁定。
- [ ] 每道题都有可验证的参考答案与评分点。
- [ ] 至少 1 道题要求候选人真实启动/复现（不是纯纸面）。
- [ ] 至少 1 道题考察"假交互/硬编码"识别。
- [ ] 至少 1 道题考察 Rubric 编写。
- [ ] 至少 1 道题考察 badcase 结构化记录。
- [ ] 有反作弊与随机注入方案。
- [ ] 有双评与 Kappa 一致性方案。
- [ ] 明确区分演示 mock 与真实缺陷。
- [ ] 本文档已登记到 `docs/README.md`。

---

## 10. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2026-10-30 | 首版：基于 Dixiyang 全栈 RAG 项目设计 A-E 笔试卷、实操、面试与评分体系 |

---

*返回 [docs 总索引](../README.md)*
