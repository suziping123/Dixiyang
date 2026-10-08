# RAG 消息版本交互与接口规范

> 版本：v1.39（2026-10-08）
> 地位：**本文件是版本切换/删除功能的唯一契约**。实现必须与本文一致；不一致即为 bug。
> 历史演进见 [RAG编辑消息版本切换与原文不落盘](./RAG编辑消息版本切换与原文不落盘.md)（8.23）。

---

## 1. 术语与数据模型

### 1.1 链文件消息字段

| 消息 | 字段 | 语义 |
|------|------|------|
| `user` | `content` | **最新**提问内容 |
| `user` | `versions: string[]` | 每次「编辑提问」前的快照，**旧→新**：`versions[0]`=最初原文 |
| `assistant` | `content` | **最新**回答内容 |
| `assistant` | `paired: string[]` | 与提问 `versions` **对齐**的历史回答：`paired[i]` = 第 i 次编辑提问时（该快照生效期间）的 AI 回答 |
| `assistant` | `versions: string[]` | AI 回答被**铅笔编辑**时的改前快照（独立历史，与提问无关） |

### 1.2 不变量

- **I1 成对等长**：提问每编辑一次，`user.versions` 与 `assistant.paired` 同步 +1（`len(paired) == len(versions)`）。无旧回答时 `paired` 不写（前端兜底）。
- **I2 删除成对**：删除提问历史格 `i` 必须同时删除 `paired[i]`；删除后两数组仍等长。
- **I3 铅笔独立**：`assistant.versions` 仅由铅笔编辑增删，**不与** `user.versions`/`paired` 联动。
- **I4 不重算**：除「删除」外，任何切换/浏览**不改变**数组长度与编号。

---

## 2. 交互规范（格子模型）

### 2.1 格子与编号

- 某消息版本条总格数 **`M = versions.length + 1`**（历史 N 格 + 最新 1 格）。
- 编号显示 **`k/M`**，`k ∈ [1, M]`：
  - `k < M` → 显示 `versions[k-1]`（`k=1` 最旧 … `k=M-1` 次新）
  - `k = M` → 显示 `content`（最新）
- **分母恒定**：只有删除使 `M` 减 1；切换/浏览永不重算编号。
- 浏览状态默认（未切换）= 最新格 `k=M`（`browseIndex = null`）。

### 2.2 版本条渲染条件

| 消息 | 渲染条件 | 数据源 |
|------|---------|--------|
| `user` | `role==='user' && versions.length > 0 && !isEditing` | 自己的 `versions` |
| `assistant` | `role==='assistant' && versions.length > 0 && !isEditing`（**仅铅笔历史非空**；只有 `paired` 无铅笔历史 → **不渲染**） | 自己的 `versions`（铅笔历史） |

- 成对历史（`paired`）**只通过提问侧条**驱动，AI 消息上不重复出条。

### 2.3 切换（无「恢复」概念）

- **切换就是查看该版本**，界面上**没有「恢复此版本」按钮**（旧 restore 流程废弃）。
- 方向：`‹` 向旧（`k-1`，停于 `k=1`）；`›` 向新（`k+1`，停于 `k=M`）。**线性移动，端点按钮禁用**，不循环。
- **成对联动（提问条）**：在 `user` 条切到 `k`：
  - 提问气泡显示 `user.versions[k-1]`（`k=M` 显示 `content`）；
  - 紧随的 AI 回答显示 `assistant.paired[k-1]`（`k=M` 或 `paired` 缺失/越界 → 显示 AI `content`）。
- **AI 铅笔条独立**：在 `assistant` 条切到 `k` 只改该 AI 气泡显示 `assistant.versions[k-1]`（`k=M` 显示 `content`），**提问不动**。
- **互斥**：点提问条 → 清本对 AI 铅笔浏览态（AI 显示回到成对源）；点 AI 铅笔条 → AI 显示以铅笔历史为准（成对浏览态保留在提问侧、不回写 AI）。
- **流式生成期间切换**（v1.37/v1.38）：
  - 生成（发送/编辑保存/重新生成）进行中可自由切换历史格，**看到的是该格旧内容，不显示三点/逐字加载**；
  - 浏览任一历史格（`k<M`）期间**隐藏底部流式加载区**，生成在后台继续；切回最新格 `M/M` 恢复显示流式区；
  - 切到历史格**自动滚动**到该消息（平滑居中）；切回最新格滚动到底部；
  - **一个提问一个气泡**（v1.38）：重新生成加载期，该条旧回答**临时隐藏**（`streamingHiddenIndex`），提问下方只有流式气泡；浏览历史格时旧回答强制显示（保证成对切换可见）；
  - **停止 = 停在流式状态**（v1.39）：点停止/失败时，已流出的**部分内容成为该回答**（原位替换，本地与链一致）；一字未出 → 两端统一显示/落盘占位句 **「未生成回答内容」**（`STOP_TEXT`）；旧回答不丢，存进新回答的 `paired` 存档（版本条/成对切换仍可回看）；
  - 数据层面旧回答不预截断（v1.37），成功/失败/取消三出口均原位替换（v1.39）。
- 刷新/切会话/编辑/重新生成 → 一切浏览态回 `k=M`（最新）。

### 2.4 删除

- 删除按钮在**所有版本条**显示（历史格与最新格`M/M`均有，v1.37 起最新格可删）。
- 点击弹确认（`confirmDelete`，禁回车触发），确认后：
  1. **提问条历史格 i（`k<M`）**：删 `user.versions[i]` **和** `assistant.paired[i]`（两次 DELETE，成对编排）；
  2. **AI 铅笔条历史格 i**：仅删 `assistant.versions[i]`（`field=versions`，AI 自己），**不联动提问**；
  3. **最新格（`k=M`）删除 = 删当前版、回退上一版**（v1.37 新增）：
     - 提问条 → `target=pair` 单次原子调用：`user.content = versions.pop()` **且** `assistant.content = paired.pop()`（其后回答成对回退）；
     - AI 铅笔条 → `target=self`：仅 `assistant.content = versions.pop()`（AI 自己回退，提问/`paired` 不动）；
     - **消息不删除**，只回退内容与版本栈；可一路删到 `1/1`（`versions` 空后再删 → `code!=200`）；
  4. 删除后该消息及联动消息浏览态回最新格（`k=M-1`，即新的 `M/M`）——「回到最近一次的回答」。
- 删除同时释放 1 个编辑配额（`EDIT_VERSION_LIMIT` 判断在 `replace_message` 内；`delete-current` pop 后同效）。

### 2.5 不再存在的行为

- ✗ 「恢复此版本」按钮及其一切前后端调用（`restore-version` 端点保留但**前端永不调用**，标废弃）。
- ✗ 恢复导致 `content == versions[i]` 的重复格。
- ✗ 任何「当前 x/N」特殊编号（统一 `k/M`，最新即 `M/M`）。
- ✗ 版本条双侧重复渲染成对历史。

---

## 3. API 契约

Base：`/api/chatHistory`（JWT 必带）。字段语义以本文档为准。

### 3.1 编辑消息（提问/回答）

```
PUT /api/chatHistory/message/{sessionId}
body: { "messageIndex": int, "role": "user"|"assistant",
        "content": str, "truncateAfter": bool }
resp: { "code": 0, "msg": "success" }   // 失败 code!=200
```

- `role=user`：改前快照 append → `user.versions`；`truncateAfter=true` 时删除该索引及之后消息（新回答由前端随后写入）。
- `role=assistant`：改前快照 append → 该 AI 的 `versions`（铅笔历史），不动 `paired`。
- **当前前端一律传 `truncateAfter=false`**（v1.37）：编辑保存只改提问，**旧回答保留在链上**；重新生成的截断/保存由后端在成功/异常/取消三出口统一执行（见 §3.4）。失败/取消后本地与链一致（部分内容或占位），不再出现"全部消失"。

### 3.2 删除版本格

```
DELETE /api/chatHistory/version/{sessionId}
body: { "messageIndex": int, "versionIndex": int,
        "field": "versions"|"paired" }
resp: { "code": 0, "msg": "..." }
```

- 提问格删除 = 前端顺序调用两次：`{userIdx, i, versions}` + `{aiIdx, i, paired}`（非原子，失败可重试，见 §4）。
- `versionIndex` 越界 → `code!=200`（`msg` 含"越界"，实际 `code=500`）。

### 3.3 删除当前版本（最新格回退，v1.37）

```
POST /api/chatHistory/delete-current/{sessionId}
body: { "messageIndex": int, "target": "pair"|"self" }
resp: { "code": 200, "data": { "content": str, "pairedContent": str|null } }
```

- `target=pair`（提问条最新格）：**单次原子 rewrite** —— `user.content = versions.pop()` 且其后 `assistant.content = paired.pop()`（`paired` 为空/AI 缺失时降级只回退提问，`pairedContent=null`）。
- `target=self`（AI 铅笔条最新格）：仅 `assistant.content = versions.pop()`，提问/`paired` 不动。
- **消息不删除**，仅回退内容与版本栈；pop 后配额释放（快照数 -1）。
- 错误：`messageIndex<0` → "参数不完整"；越界 / `versions` 空 / `target` 非法 → `code!=200`，**失败不改写文件**。

### 3.4 重新生成的截断时序（v1.37）

```
POST /api/chat/stream （带 regenerateIndex 时 = 重新生成）
```

- **开流不截断链**：`_build_stream_messages` 在内存中排除 `history[:regenerateIndex]` 构建 prompt；
- **三出口统一落盘** `_save_reply()`（全同步，可在取消上下文安全执行）：**成功**跑完流后截断+追加；**异常**捕获 `Exception` 后截断+追加部分内容；**取消**（客户端断开 → `GeneratorExit`/`asyncio.CancelledError`）截断+追加已流出部分——三种情况 `content` 为空时均落占位句 `STOP_TEXT="未生成回答内容"`；`prevAnswerVersions` 始终写入新回答 `paired`（旧回答存档）；
- 前端配合：`regenerateMessage` 成功/失败/取消**一律原位替换** `messages[messageIndex]` 为「部分内容或占位」（槽位被切换会话等破坏时写兜底），本地与链所见一致；普通发送 `sendStreamMessage` 取消同理 push「部分内容或占位」。

### 3.5 废弃端点

```
POST /api/chatHistory/restore-version/{sessionId}   // DEPRECATED：前端不调用，保留兼容旧数据
```

### 3.6 只读与造数

```
GET  /api/chatHistory/session/{sessionId}   // 消息列表（验收读取）
POST /api/chatHistory/batchSave             // 原样落链（聊天主流程不再调用；测试造数入口）
     body: { sessionId, messages: [{role, content, versions?, paired?, ...}] }
```

### 3.7 编辑配额

- 每会话每用户 `EDIT_VERSION_LIMIT = 6`；超限 `PUT message` 返回 `code!=200` + `msg="修改次数已达上限（6次），删除历史版本后可继续修改"`。
- 每次 `DELETE version` 或 `POST delete-current` 释放 1 配额（由快照总数 `versions+paired+AI.versions` 计数）。

---

## 4. 边界与旧数据

| 场景 | 行为 |
|------|------|
| `paired` 短于 `versions`（旧数据/无旧回答） | AI 联动显示兜底 `content`；不报错 |
| 旧会话 `content == versions[i]`（历史恢复遗留） | 显示重复格（数据不解清洗）；验收用新建会话 |
| 成对删除两次请求第二次失败 | `versions`/`paired` 暂不等长（I1 破）→ 重试删 `paired[i]`；浏览越界按 §2.3 兜底 |
| AI 有 `paired` 无铅笔 `versions` | AI 无条；成对切换由提问条驱动（I3） |
| 浏览历史格时发送新消息 | 链数据始终是最新版（浏览不落盘）；发送/重新生成用链上 `content`（最新格）；流式区在浏览态隐藏（§2.3） |
| 编辑保存后停止重新生成（过渡态） | 本地与链 =「新提问 + 停止时的部分回答/占位」，旧回答在新回答 `paired` 中（`prevAnswerVersions` 落盘）→ I1 等长保持；`delete-current pair` 正常成对回退 |
| 生成期间切换会话 | `regenerateMessage` 成功时按对象引用校验槽位，会话已切换则丢弃新回答不写入（防串会话） |

---

## 5. 测试用例矩阵

### 5.1 API 自动化（不依赖 LLM）

| # | 步骤 | 断言 |
|---|------|------|
| A1 | 登录 → `batchSave` 造 `[user(versions=[Q1]), assistant(paired=[A1], versions=[B1])]` → GET | 字段原样返回；`len(paired)==len(versions)`（I1） |
| A2 | `PUT message` 编辑提问（`truncateAfter=false`） | `user.versions` +1；`content` 更新；AI 字段不动 |
| A3 | `PUT message` 第 7 次 | `code!=200`，msg 含"最大编辑次数"（§3.5） |
| A4 | 成对删 `{userIdx,0,versions}`+`{aiIdx,0,paired}` → GET | 两数组同步 -1 仍等长（I2）；`content` 不变 |
| A5 | 删 AI 铅笔 `{aiIdx,0,versions}` → GET | 仅 AI `versions` -1；`paired`/提问不动（I3） |
| A6 | `versionIndex` 越界 → GET | `code!=200`（msg 含"越界"） |
| A7 | `POST restore-version`（兼容性） | 仍 200（前端不调，仅兼容） |

**实测结果（2026-10-08）**：`test_version_api.py` 对 8084 运行中服务、账号 11111 实测 **30/30 PASS**（登录、A1-A7 全矩阵、两会话测后即删）。脚本存于 `C:\Users\Lenovo\AppData\Local\Temp\opencode\test_version_api.py`。

#### v1.37 增补（`test_v137_api.py`）

| # | 步骤 | 断言 |
|---|------|------|
| B0 | 无 token 调 `delete-current` | HTTP 401/403/422 拒绝 |
| B1 | `PUT message` `truncateAfter=false` → GET | 链长不变、旧回答保留、`versions` push、`content` 更新 |
| B2 | `POST delete-current` `target=pair` ×2 → GET | 每次 `data.content/pairedContent` 为上一版；两数组同步 pop 仍等长（I1）；铅笔不受影响；消息数不变；第 3 次 `versions` 空 → `code!=200` 且状态不变；越界/`target=bad`/`messageIndex=-1` 拒绝 |
| B3 | `POST delete-current` `target=self` | 仅 AI `content/versions` 回退；`paired` 与提问完全不动；`pairedContent=null` |
| B4 | 编辑至第 7 次被拒 → `delete-current` → 再编辑 | 拒绝 msg 含"上限"；回退后配额释放，编辑恢复 200 |

**实测结果（2026-10-08）**：`test_v137_api.py` **29/29 PASS**（回归 `test_version_api.py` 同轮 **30/30 PASS**）。脚本存于 `C:\Users\Lenovo\AppData\Local\Temp\opencode\test_v137_api.py`。

#### v1.39 增补（`test_v139_api.py`，真 LLM + 提前断开连接模拟"点停止"）

| # | 步骤 | 断言 |
|---|------|------|
| C1 | 造 `[user, assistant]` → `POST chat/regenerate`（`prevAnswerVersions` 带旧回答）流式挂 2s 后 `close()` → GET | 消息数仍 2（截断+追加原子）；新回答 `content` 非空（部分内容或占位 `未生成回答内容`）；`paired == [旧回答]`；提问不动 |
| C2 | 新会话 `POST chat/stream` 流式挂 2s 后 `close()` → GET | 恰好 `[user, assistant]` 各 1（不重复、提问不丢）；回答 `content` 非空 |

**实测结果（2026-10-08）**：`test_v139_api.py` **8/8 PASS**（2 秒断开时 LLM 尚未出字 → 占位句落盘，与前端 `STOP_TEXT` 完全一致；回归 30/30 + 29/29 同轮通过）。脚本存于 `C:\Users\Lenovo\AppData\Local\Temp\opencode\test_v139_api.py`。

### 5.2 UI 验收（测试账号手测）

| # | 步骤 | 预期 |
|---|------|------|
| U1 | 编辑提问 2 次后查看你消息上的条 | 显示 `k/3`；分母=2历史+1最新 |
| U2 | `‹` 从 `3/3` | 到 `2/3`：你的提问和 AI 回答**同时**换成第 2 格内容；再 `‹` 到 `1/3`；`‹` 禁用 |
| U3 | `›` 回 `3/3` | 内容回最新；`›` 禁用；**全程无"恢复"按钮、无"当前 x/N"字样** |
| U4 | 历史格点删除（确认） | 该格提问+回答都消失，跳到最新格，分母 -1（如 `2/3→2/2`） |
| U5 | AI 铅笔编辑过 1 次 | AI 消息上出独立条 `k/2`，切换只改 AI 内容，你的提问不动 |
| U6 | 提问条切到历史 + 点 AI 铅笔条切换 | AI 显示以铅笔条为准；点回铅笔条最新格 → AI 回到与提问条一致的成对内容 |
| U7 | 刷新页面 | 所有条回最新格（`M/M`），内容为最新版 |
| U8 | 未编辑过提问的会话 | 你消息上无条；AI 铅笔编辑过才有 AI 条 |
| U9 | AI 回答生成中（三点/逐字）立刻 `‹` 切历史格 | **立即看到旧对话内容，不出现加载动画**；底部流式区隐藏；自动滚动到该消息；生成完成后切回最新格看到新回答 |
| U10 | 编辑提问保存后点重新生成，生成中点"停止" | 加载期提问下方**只有一个气泡**（旧回答隐藏）；点停止后**停在当前已流出的内容**上（成为正式回答）；若一字未出则显示「未生成回答内容」占位；刷新页面内容一致 |
| U11 | 最新格 `M/M` 点删除（确认） | 提问+回答内容同时回退上一版（消息不消失、条变 `M-1/M-1`）；可继续删到 `1/1`，再删提示错误 |
| U12 | AI 铅笔条最新格点删除 | 仅 AI 内容回退，你的提问完全不动 |

---

## 6. 实现文件索引

| 文件 | 职责 |
|------|------|
| `dixiyang-vue/Dixiyang-vue3/src/components/chat/ChatMessage.vue` | 版本条渲染条件、`k/M` 标签、线性 ‹›、删除按钮（历史格+最新格，无恢复） |
| `dixiyang-vue/Dixiyang-vue3/src/views/RagAssistantView.vue` | `pairBrowse`/`aiOwnBrowse` 双状态、成对联动、成对删除编排、`isBrowsingHistory` 隐藏流式区、`scrollBrowseTarget`、`handleDeleteCurrent` |
| `dixiyang-vue/Dixiyang-vue3/src/composables/useChatStream.ts` | `editMessage`（恒 `truncateAfter=false`）/`deleteVersion`/`deleteCurrent`（code 检查）；`regenerateMessage` 原位替换（成功/失败/取消三出口，停止=部分内容或占位）+`streamingHiddenIndex`；`sendStreamMessage` 取消 push 部分/占位；**无 restore** |
| `DixyangFast/src/dixiyang/routers/chat_history.py` | 编辑/删除/`delete-current`/废弃 restore 端点 |
| `DixyangFast/src/dixiyang/routers/chat.py` | `_build_stream_messages` 内存排除 `regenerateIndex`；`STOP_TEXT` 占位句；`_save_pair`/`_save_reply` 三出口统一落盘（成功/`Exception`/`GeneratorExit`+`CancelledError` 取消），取消=停在流式状态 |
| `DixyangFast/src/dixiyang/services/chat_history_service.py` | `delete_current` 服务编排（越界/配额/原子改写） |
| `DixyangFast/src/dixiyang/services/chain_file_manager.py` | 链文件追加/截断/改写；`replace_message`/`restore_version`/`delete_version` 快照语义；`delete_current`（pair/self 回退，原子单次改写） |
