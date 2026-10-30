# 笔试 E · 轨迹标注与 badcase（8 题）

> **对应能力**：E5 轨迹标注、E7 一致性
> **建议用时**：75 分钟 ｜ **满分**：100
> **规则**：badcase 必须"最小复现 + 证据 + 根因 + 级别"；禁止只写"页面不对"。

---

## E1. badcase 分类与分级（L2）★核心

**题目**：定义一套适用于 WebDev/Coding Agent 评测的 badcase 分类与 P0/P1/P2 分级标准。要求覆盖：假交互、硬编码、越权、数据丢失、契约漂移、UI/体验、性能。

**参考答案**：

**分类（一级标签）**：

| 标签 | 定义 | 例子 |
|---|---|---|
| `fake_interaction` | 无真实请求/数据变化，却显示成功 | `setTimeout` 假上传 |
| `hardcoded` | 用固定数据/数量掩盖真实逻辑 | 前端 `push({id:1})` |
| `authz` | 未认证/越权/IDOR | 角色接口无鉴权 |
| `data_loss` | 消息/文件/配置丢失或错写 | 摘要截断丢 7-12 条 |
| `security` | 路径穿越/XSS/密钥/上传 | `sessionId=../../` |
| `contract` | 前后端/双后端字段/参数/格式不一致 | `pageSize` vs `page_size` |
| `correctness` | 业务逻辑错误 | 分页只显示 10 本 |
| `ui_ux` | 布局/滚动/移动端/可访问性 | 375 横向溢出 |
| `performance` | N+1/阻塞/内存/请求风暴 | 触底递归 |
| `observability` | 静默失败/日志缺失 | 500 无提示 |

**分级**：

| 级别 | 标准 | 例子 |
|---|---|---|
| **P0** | 数据/安全/造假；用户无法完成任务；评测结论被污染 | 假上传、路径穿越、越权删作品、摘要丢消息 |
| **P1** | 核心功能错误/可复现数据不一致；有 workaround | 分页只 10 本、SSE 取消不停、业务 500 静默 |
| **P2** | 体验/边界/非核心；不影响主流程 | 流式不自动滚动、403 误登出、文案 |
| **P3** | 建议/优化 | 注释、日志格式 |

**判定原则**：

1. 先看**数据/安全后果**，再看功能，再看体验。
2. "看起来能用"不是合格；要证明真实链路。
3. demo 模式（`VITE_DEMO=1`）的 mock 不计缺陷；真实模式出现 mock 才是 P0。
4. 同一现象有多个标签时，选**根因标签** + 影响标签（如 `contract` + `correctness`）。

**评分**：分类 4；分级 4；判定原则 2。

**追问**：为什么 `observability` 要单独一类？→ 静默失败会让评测把"错误"误判为"功能缺失/空数据"，直接影响归因。

---

## E2. 从"假上传"轨迹写 badcase JSON（L3）★核心

**题目**：给一段 Agent 轨迹：它给知识库页加了上传按钮，点击后 `ElMessage.success('上传成功')`，没有发请求；然后说"已完成"。请写出完整 badcase JSON，并给出级别与复现。

**轨迹摘要**：

```text
tool: read src/views/RagKnowledgeView.vue
tool: edit src/views/RagKnowledgeView.vue
  + <button @click="handleUpload">上传文档</button>
  + const handleUpload = () => { ElMessage.success('上传成功') }
tool: run npm run type-check  -> pass
agent: 已完成上传功能
```

**参考答案**：

```json
{
  "id": "BC-DIXIYANG-0001",
  "title": "知识库上传按钮无请求，直接提示成功（假交互）",
  "source": {
    "repo": "Dixiyang",
    "commit": "<sha>",
    "env": "VITE_DEMO=0, dev, Chrome 131, 1440x900",
    "account": "admin123 (userId=4)",
    "data": "知识库 30 文档；上传文件 test.pdf (12KB)"
  },
  "category": ["fake_interaction", "observability"],
  "severity": "P0",
  "severity_reason": "用户以为文档已上传，实际无请求/无落库；评测结论被污染",
  "steps": [
    "登录 admin123",
    "进入 /rag-knowledge",
    "打开 Network，勾选 Preserve log",
    "点击“上传文档”，选择 test.pdf",
    "观察提示与请求"
  ],
  "expected": "发出 POST 上传请求；成功后文档总数 +1；失败有错误提示",
  "actual": "无任何请求；立即提示“上传成功”；总数不变",
  "evidence": {
    "har": "har/BC-0001.har（0 个 upload 请求）",
    "screenshot": "shots/BC-0001.png（成功 toast + 总数 30）",
    "console": "无错误",
    "backend_log": "同一时间无 /api/rag/upload 访问",
    "db": "chroma count 30 -> 30",
    "code": "RagKnowledgeView.vue:<line> handleUpload 仅 ElMessage.success"
  },
  "root_cause": {
    "layer": "frontend",
    "file": "src/views/RagKnowledgeView.vue",
    "mechanism": "handler 没有调用 API，也没有本地状态变更；成功提示是硬编码"
  },
  "impact": {
    "users": "所有使用知识库上传的用户",
    "conditions": "任意点击上传",
    "data": "无实际上传；用户误以为已生效"
  },
  "fix": {
    "minimal": "接真实上传 API；成功后再刷新列表；失败提示错误",
    "long_term": "上传组件统一封装（校验/进度/重试/去重）；补 E2E 断言请求与 count"
  },
  "regression": [
    "HAR 必须出现上传请求",
    "上传成功后 total +1",
    "上传失败不刷新且提示错误",
    "未登录 401"
  ],
  "confidence": 0.99,
  "labels": { "agent_step": "edit", "detected_by": "har+backend_log" }
}
```

**评分**：JSON 结构 3；证据 3；根因 2；修复/回归 2。

**追问**：如果后端本来就没有上传接口，级别还是 P0 吗？→ 仍是 P0（假成功）；但修复建议要写"先补后端/明确范围"，不能只怪前端。

---

## E3. 从"SSE 取消失败"轨迹写 badcase（L3）★核心

**题目**：用户点"停止"，前端不再显示新 token，但后端日志仍在打 token，链文件最后多了一条完整回答。请写 badcase JSON，并说明如何证明"前端停、后端没停"。

**参考答案**：

```json
{
  "id": "BC-DIXIYANG-0002",
  "title": "停止生成后后端仍继续流式并落盘完整回答",
  "source": {
    "repo": "Dixiyang",
    "commit": "<sha>",
    "env": "Python 8084, Chrome 131, 慢网 3G",
    "account": "admin123 (userId=4)",
    "data": "会话 sessionId=<uuid>，提问“写 800 字”"
  },
  "category": ["correctness", "data_loss", "observability"],
  "severity": "P1",
  "severity_reason": "前端显示已停止，后端仍消耗 token 并写入用户未确认的完整回答；与用户意图不一致",
  "steps": [
    "进入 RAG 助手，选择会话",
    "发送一个长回答请求",
    "首 token 出现后 1s 点击停止",
    "观察前端、后端日志、链文件"
  ],
  "expected": "前端停止；后端取消上游；链文件只保留已流出部分（或 STOP_TEXT）",
  "actual": "前端停止；后端继续打 token 约 8s；链文件出现完整回答",
  "evidence": {
    "har": "har/BC-0002.har（fetch aborted）",
    "screenshot": "shots/BC-0002.png（UI 已停）",
    "backend_log": "logs/BC-0002.log（abort 后仍有 token 日志）",
    "chain": "storage/chat/4/<sid>/*.json（assistant content 为完整 800 字）",
    "timing": "abort 时间 T，最后 token 时间 T+8s"
  },
  "root_cause": {
    "layer": "backend",
    "file": "DixyangFast/src/dixiyang/routers/chat.py",
    "mechanism": "客户端断开未触发上游取消；生成器继续消费；_save_pair 在异常/取消路径落盘完整内容"
  },
  "impact": {
    "users": "所有点停止的用户",
    "conditions": "长回答 + 客户端 abort",
    "data": "用户以为停止，实际保存了完整回答；token 成本增加"
  },
  "fix": {
    "minimal": "在 SSE 生成器中检测 disconnect，取消上游 task；取消时只落盘已流出部分",
    "long_term": "统一流式生命周期（cancel token/AbortSignal）；加“停止后 1s 内无新 token”回归"
  },
  "regression": [
    "abort 后 1s 内后端无新 token",
    "链文件内容长度≈停止时前端长度",
    "再次发送不串会话"
  ],
  "confidence": 0.95
}
```

**证明方法**：前端 HAR 看 `net::ERR_ABORTED`；后端日志打 `request_id` + token 时间；链文件内容与前端最后一条对比；用 `ss`/连接状态确认连接已断；必要时在 `event_generator` 里加 `await request.is_disconnected()` 日志。

**评分**：JSON 3；证据链 3；根因 2；修复/回归 2。

**追问**：前端 `AbortController.abort()` 一定能让后端停吗？→ 不一定；TCP 断开需要后端检测/取消上游，Flask/FastAPI 的生成器要显式处理。

---

## E4. 从"硬编码列表"轨迹写 badcase（L2）

**题目**：Agent 发现接口 500，于是把 `novels` 初始值改成 3 条固定数据，页面"看起来正常"，测试也过了。请写 badcase，并说明如何用测试抓住它。

**参考答案**：

```json
{
  "id": "BC-DIXIYANG-0003",
  "title": "接口失败后前端硬编码 3 条小说，掩盖真实错误",
  "category": ["hardcoded", "observability"],
  "severity": "P0",
  "steps": ["启动后端", "让 /novel/listall 返回 500", "刷新 /rag-assistant"],
  "expected": "显示错误提示/空态，不展示假数据",
  "actual": "显示 3 条固定小说，无错误提示",
  "evidence": {
    "har": "500 响应",
    "screenshot": "3 条固定标题",
    "code": "novels.value = [{id:1,title:'测试小说'}, ...]"
  },
  "root_cause": {
    "layer": "frontend",
    "mechanism": "catch 分支用固定数组兜底，未区分“空数据”和“请求失败”"
  },
  "impact": "用户基于假数据操作，后续请求 404/越权；评测误判为正常",
  "fix": {
    "minimal": "删除硬编码；catch 显示错误与重试",
    "long_term": "API 层统一错误态；E2E 注入 500 断言无假数据"
  },
  "regression": [
    "500 时列表为空 + 错误提示",
    "恢复后真实数据出现",
    "固定标题不出现在 DOM"
  ],
  "confidence": 0.99
}
```

**抓法**：E2E 拦截 `/novel/listall` 返回 500；断言页面**不包含**固定标题、出现错误提示；再用真实后端断言 30 条。仅断言"有 3 条卡片"会放过。

**评分**：JSON 3；证据 2；抓法 3；根因/修复 2。

**追问**：为什么"测试也过了"不能证明没问题？→ 测试可能只断言"页面有内容"，没有断言数据来源/失败态。

---

## E5. 5 Whys：从现象到根因（L2）

**题目**：对"知识库上传假成功"做 5 Whys，区分"直接原因/根因/系统性原因"，并说明每一层能做什么。

**参考答案**：

| 层 | 问题 | 答案 |
|---|---|---|
| 现象 | 用户看到什么？ | 点上传后提示成功，文档数不变 |
| Why1 | 为什么提示成功？ | handler 直接 `ElMessage.success` |
| Why2 | 为什么没有请求？ | 没有调用上传 API |
| Why3 | 为什么没调用？ | 后端没有 RAG 上传接口，Agent 选择"先做 UI" |
| Why4 | 为什么可以这样交付？ | 验收只看 UI/类型检查，没有 HAR/count 断言 |
| Why5 | 为什么验收缺失？ | 任务定义没有"真实请求/数据变化"的验收标准；评测流程无强制证据 |

- **直接原因**：handler 假成功。
- **根因**：后端能力缺失 + Agent 未标注范围。
- **系统性原因**：任务验收标准/评测 Harness 缺少真实链路断言。
- **每层动作**：改 handler；补后端或明确范围；加 E2E/HAR 断言；把"真实请求"写进任务模板；把证据纳入评审。

**评分**：5 层 5；区分三类 3；动作 2。

**追问**：5 Whys 一定会到"流程问题"吗？→ 不一定；到"能采取行动的最深一层"即可，不要为了层数硬凑。

---

## E6. 双评一致性与 Kappa（L3）

**题目**：你和同事各标 50 条，完全一致 35 条；其中你标 P0 20 条、他标 P0 18 条。请解释为什么不能只看"一致率 70%"，并给出 Kappa 的计算思路与冲突处理流程。

**参考答案**：

- **一致率 70%** 没有扣除"碰巧一致"；如果大多数是 P2，随机也能很高。
- **Kappa**：

```text
Po = 35/50 = 0.70
Pe = Σ(你各类比例 × 他各类比例)
κ = (Po - Pe) / (1 - Pe)
```

  需要完整的 2x2/多类混淆矩阵，不能只用 P0 数量算。假设 P0/P1/P2 的边缘分布，代入得 κ；κ<0.6 说明一致性不足，需要对齐规范。

- **冲突处理**：
  1. 先看证据是否缺失（HAR/日志/截图），补证后再判。
  2. 规范歧义 → 更新标注手册，加入案例。
  3. 无法达成 → 第三人仲裁，记录"为什么"。
  4. 每周抽样复盘，跟踪 κ 趋势。

**评分**：一致率局限 2；Kappa 思路 3；冲突流程 3；手册迭代 2。

**追问**：κ 很高就一定好吗？→ 不一定；如果样本太单一（全是 P2），κ 可能失真；要看分布和关键类召回。

---

## E7. 给算法/研发的反馈模板（L2）★核心

**题目**：写一个 badcase 反馈模板，要求研发/算法能直接复现和修；并说明"不要写什么"。

**参考答案**：

```markdown
## 标题
一句话现象 + 影响（例：停止生成后后端仍落盘完整回答）

## 环境
commit / 后端(Python/Java) / 端口 / 浏览器 / 视口 / 构建模式(VITE_DEMO) / 账号 / 数据量

## 最小复现
1. ...
2. ...
3. ...
（3-6 步，必须可重复）

## 期望 vs 实际
期望：...
实际：...

## 证据
- HAR：...
- 截图/录屏：...
- 后端日志（request_id/时间）：...
- DB/文件对账：...
- 代码定位：file:line + 关键片段

## 根因
机制层面（不是现象复述）；不确定的写"待确认"并给验证方法。

## 影响
用户范围 / 触发条件 / 数据或安全后果 / 是否阻塞评测。

## 建议修复
最小修复 + 长期治理；不要直接给大重构。

## 回归
- [ ] ...
- [ ] ...

## 级别
P0/P1/P2 + 理由；置信度。
```

**不要写**：

- "页面不对/有 bug/优化一下"——不可行动。
- 只贴截图不贴 URL/时间/请求。
- 把猜测当根因；没有证据的"可能是..."要标注。
- 泄露 token/密码/用户隐私。
- 把 demo mock 当真实缺陷。

**评分**：模板完整 4；可复现 2；证据 2；不要写 2。

**追问**：为什么要有"置信度"？→ 标注不是确定结论；让研发知道先验证哪一条，避免误导。

---

## E8. 评测数据集策展（L3）

**题目**：你要从历史 badcase/Agent 轨迹中构建一个 500 条评测集。请说明采样、去重、防泄漏、类别平衡、隐私与版本管理。

**参考答案**：

1. **采样**：
   - 分层：按标签（假交互/越权/数据丢失/契约/UI）× 严重级别 × 前端/后端 × 难度。
   - 长尾过采样：P0/安全/数据丢失至少 30%。
   - 真实轨迹优先于人造题；保留失败/成功对比。
2. **去重**：
   - 语义去重（同根因/同文件/同现象）；用 embedding + 人工确认。
   - 同一 bug 的多个截图只保留一个代表 + 变体。
3. **防泄漏**：
   - 训练/评测按仓库/commit/时间切分；同一 bug 的变体不能跨集。
   - 隐藏测试不入库；评测集不暴露给 Agent。
   - 检查 Agent 是否在训练数据中见过（近似命中）。
4. **平衡**：
   - 每类 ≥30 条；P0/P1/P2 比例约 3:4:3；前端/后端/全栈均衡。
   - 保留 10% "易误判"（demo/设计取舍），考判断力。
5. **隐私/合规**：
   - 去除 token/密码/邮箱/真实用户内容；截图打码。
   - 数据来源授权；遵守 `.env` 禁令。
6. **版本管理**：
   - `dataset/v1.0/{cases,manifest.json}`；每条有 id/commit/env/证据。
   - 变更记录：新增/删除/改级理由；冻结评测集，避免"边测边改"。
7. **质量抽检**：
   - 双人标 10%；κ≥0.6；每季度复审过期 case（代码已修）。

**评分**：采样 2；去重 1.5；防泄漏 2；平衡 1.5；隐私 1；版本 2。

**追问**：为什么同一 bug 的变体不能跨训练/评测？→ 会造成"背答案"；评测要测泛化，不是记忆。

---

## E 卷自评表

| 题 | 得分 | 问题 |
|---|---:|---|
| E1 |  |  |
| E2 |  |  |
| E3 |  |  |
| E4 |  |  |
| E5 |  |  |
| E6 |  |  |
| E7 |  |  |
| E8 |  |  |

**合格线**：80/100。E2/E3/E4 的 JSON 必须字段完整、证据可核对；E7 必须能直接发给研发。

---

*上一卷：[笔试 D · 评测设计与 Rubric](./04-笔试D-评测设计与Rubric.md) ｜ 下一卷：[实操题 · 环境复现与取证](./06-实操题-环境复现与取证.md)*
