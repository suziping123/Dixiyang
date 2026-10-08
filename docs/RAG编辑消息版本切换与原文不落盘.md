# RAG 编辑消息：版本切换（上限6次）与改前原文不落盘

- 日期：2026-10-08
- 范围：`/rag-assistant` 页面编辑消息（AI 回答 + 用户提问），前后端联改
- 关联：`DixyangFast/src/dixiyang/`（Python FastAPI 后端）+ `dixiyang-vue/Dixiyang-vue3/`

## 需求

1. 对话只保留**改之后**的内容：链文件不存改前原文、编辑弹窗去掉「原始回答」对照、AI 修正学习只注入要点（不注入原文）
2. 已编辑消息支持**左右切换**浏览历史版本（`‹ n/N ›`），可**恢复**某版本为当前内容、可**删除**某版本
3. 每条消息最多 **6 个版本**（= 最多改 6 次）；删除 1 个版本配额减一，可继续编辑
4. 用户提问编辑**持久化**（原为纯本地改+截断重发，刷新丢失、链不截断）
5. 编辑提问后**历史回答不丢失**（第四轮）：切换提问第 i 版时，下方回答同步显示第 i 次编辑时生成的回答；删除/恢复提问版本时回答**成对**操作
6. **单一版本切换器**（第五、六轮）：版本条只挂在**用户消息**上（第六轮用户反馈：不应在 AI 消息上、应在自己发的消息上；第五轮曾在回答侧），AI 消息不出条、内容随 `browseIndex` 联动切换+描边；**计数与实际格数一致**（第六轮："看似2个却能切3个"= 显示历史数 N 实际 N+1 格 → 总数含当前 = N+1，显示 `当前 1/3 → 2/3 → 3/3`）；杜绝同一回答双写；流式完成后加载指示器立即消失

## 数据模型

```json
{ "role": "user", "content": "Q最新", "versions": ["Q改前1", "Q改前2"] }
{ "role": "assistant", "content": "A最新", "edited": true,
  "versions": ["独立编辑历史"], "paired": ["A0", "A1"] }
```

- **`versions` 存每次编辑前的内容**（原文/中间态），`content` 恒为最新；切换历史看到的是"改之前的样子"，长度 ≤ 6 = 已编辑次数
- **编辑**：`versions.append(改前content)` + `content = 新内容`；编辑前 `len(versions) >= 6` → 拒绝
- **恢复**：`content = versions[i]`，versions 不变、不占配额
- **删除**：`splice(i)` 配额减一；历史与当前**解耦**——删除/删空均不影响 `content`（对话内容永不为空）
- **对话流只显示 `content`（最新）**：不展示改前痕迹；改前内容仅存在于 versions 供左右切换浏览
- **`paired`（仅回答，第四轮新增）**：与提问 `versions` 一一对齐的"第 k 次编辑提问时正在生效的回答"，只由编辑提问 append、删除提问版本时同步 splice；**手动重新生成原样保留**（语义=丢弃当前，不追加）。联动规则：浏览提问第 i 版 → 回答显示 `paired[i] ?? content`（越界兜底 content）

## 方案

### 后端（DixyangFast/src/dixiyang/）

| 文件 | 改动 |
|------|------|
| `services/chain_file_manager.py` | `EDIT_VERSION_LIMIT=6`、`EditQuotaExceeded`；`replace_message` 不写 `originalContent`、维护 versions、超限抛异常；新增 `restore_version()`/`delete_version()`（历史与当前解耦，**第四轮加 `field` 参数**支持操作 `versions`/`paired`，非法值 IndexError）；公共 `_rewrite_chain()` 原子重写 |
| `services/chat_history_service.py` | `edit_message` 超限返回「修改次数已达上限（6次）…」；`truncate_after` 参数（用户提问编辑后 `truncate_chain(idx+1)`）；edits.json record **去掉 originalContent/editedContent**（keyPoint 仍异步提取，原文仅内存瞬时）；新增 restore/delete 方法（**透传 `field`**）；`get_session_messages` 读取时 `pop` 旧数据残留的 `originalContent` 不下发 |
| `routers/chat_history.py` + `schemas/chat_history.py` | PUT body 加 `truncateAfter`；新增 `POST /chatHistory/restore-version/{sessionId}`、`DELETE /chatHistory/version/{sessionId}`（body `{messageIndex, versionIndex, field?}`，**第四轮加 `field`**） |
| `routers/chat.py` + `schemas/chat.py` | **第四轮**：RegenerateRequest 加 `prevAnswerVersions: list[str] \| None`，regenerate 成功/兜底两处把旧回答存档写入新回答 `paired`；**第五轮**：`full_content` 拆为 `content_parts`/`thinking_parts` 分开累计（4 处保存点），thinking 独立字段落链不混入 `content`（与前端加载渲染对齐）——后端为聊天**唯一写入点** |
| `services/chat_service.py` | `load_edit_context` **只用 keyPoint**，删除「原文→修正版」回退分支（旧记录原文字段一律忽略） |

### 前端（Dixiyang-vue3/src/）

| 文件 | 改动 |
|------|------|
| `composables/useChatStream.ts` | `ChatMessage.versions?: string[]`；`editMessage` 改返回 `string \| null`（错误信息/成功），支持 `(index, content, role, truncateAfter)`；新增 `restoreVersion`/`deleteVersion`（历史与当前解耦，**第四轮加 `field` 参数**）；删除死代码 `replaceUserMessage`；**第四轮**：`ChatMessage.paired?: string[]`、`regenerateMessage` 加 `prevPaired` 参数（body `prevAnswerVersions`，不传则原样保留被截断回答的 paired）、load/save 映射 paired；**第五轮**：**删除 `saveToBackend`/batchSave 双写**（发送与重新生成两处调用点，落盘以后端为唯一写入点）、`sendStreamMessage` push 完成消息后**立即复位 `isStreaming`**（标题生成/会话刷新移出解锁关键路径，修 typing 指示器残留）、`editMessage`/`restoreVersion`/`deleteVersion` **检查业务返回码**（拦截器对 code≠200 也 resolve，失败不再静默改本地） |
| `components/chat/ChatMessage.vue` | 去掉「已编辑」「vN」徽章；`versions≥1` 时气泡底部常显版本条 `‹ 当前·N个版本 ›`，浏览态出「恢复此版本」「删除（confirmDelete 确认，禁回车）」；`displayContent` computed 驱动气泡正文切换；`is-browsing` 描边；**第四轮**：`browseIndex` 改**受控**（props + `update:browseIndex`），新增 `browseSource`（`paired` 优先 / `versions` 兜底）决定版本条内容源；**第五轮**：版本条渲染加单侧条件 → **单一切换器**；**第六轮**：条件改 `role==='user'`（版本条挂用户消息，AI 消息不出条、仍随 `browseMap` 联动），`positionLabel` 总数 = 历史 N+1（含当前），`当前 1/k → k/…` 与实际可切换格数一致 |
| `components/chat/EditMessageModal.vue` | 删「原始回答」对照面板 → 单 textarea 全宽（720px） |
| `views/RagAssistantView.vue` | 编辑入口（AI 回答 + 用户提问）先查配额满 6 → `ElMessage.warning` 拦截；`handleEditSave` 适配新返回值；`handleUserEditSave` 先 `editMessage(idx, content, 'user', true)` 持久化+后端截断，成功后改走 `regenerateMessage(idx+1, buildRegenContext())`（只生成回答，不重复写提问）；接线 `@restoreVersion/@deleteVersion`（单参数 `$event`=versionIndex）；**第四轮**：`handleUserEditSave` 抓旧回答组 `prevPaired` 传入 regenerate；`browseMap`+`setBrowse` 维护提问↔回答**成对浏览联动**；恢复/删除按角色**成对编排**（提问 ↔ 回答 `field='paired'`）；切会话/编辑/重新生成时 `clearBrowse()` |

## 改动文件

- 后端：`chain_file_manager.py`、`chat_history_service.py`、`chat_service.py`、`routers/chat_history.py`、`schemas/chat_history.py`、`routers/chat.py`、`schemas/chat.py`
- 前端：`useChatStream.ts`、`ChatMessage.vue`、`EditMessageModal.vue`、`RagAssistantView.vue`
- 文档：本文档 + `docs/README.md`

## 已知问题

- **中途空白回归（已修复）**：ChatMessage template 先行改用 `displayContent` 但 script 未补完时，气泡渲染 `undefined` → 全部消息空白（用户截图反馈）；补全 computed/方法后恢复
- **编辑提问产生重复对话（已修复，第二轮）**：`handleUserEditSave` 在 PUT+截断后又调 `sendStreamMessage()`，其内部 `sendMessage` 把同一条提问再 push 本地、`/chat/stream` 再 append 一遍 → 链里同一提问出现两次（截图"多个对话"）→ 改走 `regenerateMessage(idx+1)` 通道（截断到提问、只 append 回答，复用现有重新生成机制，零后端改动）
- **「版本不存在」误报（已修复，第二轮）**：emit 是双参数 `(index, versionIndex)`，Vue 内联模板 `$event` 只取第一个参数 → 第 2/3 条消息把"消息序号"当 versionIndex 传入越界 → 改为 emit 单参数 `versionIndex`（index 由父组件 v-for 提供）；守卫同步改长度判断（防空字符串误判）
- **切换永远显示最新（已修复，第三轮）**：初版 versions 只存"改后内容"，改 1 次时 `versions[0] == content` → 切到哪都是最新（「浏览 1/1」）→ 改为**每次编辑前快照改前内容**（`versions=[原文, 改1前, …]`，content 恒最新）；删除同步解耦（不再回退 content）。旧测试会话的 versions 是"改后快照"格式，混用时前几格可能与当前相同，建议删测试会话
- **切提问版本回答永远是最新（已修复，第四轮）**：编辑提问时三重截断（前端 `truncateAfter`、`/chat/regenerate` 的 `truncate_chain`、本地 `slice`）把旧回答**物理删除**，链里只剩最新一条 → 切任何提问版本下方回答都不变 → 新增回答 `paired` 成对存档（regenerate 请求体携带旧回答）、浏览态 `browseMap` 提问↔回答联动。**历史回答只对修复后的编辑生效，旧会话已删的回答无法找回（删会话重聊）**
- **paired 与独立版本条互斥（已知限制）**：回答同时有 `paired` 与独立编辑 `versions` 时，版本条只显示 `paired`（联动优先），独立编辑历史暂不可浏览（`browseSourceOf` 兜底仅在 paired 为空时启用）
- **存量脏数据不自动清洗**：以上两 bug 已产生的重复消息/脏链无法可靠识别（"编辑前+编辑后"内容不同、无标记），修复只保证以后不再产生；当前受影响会话建议删除重聊
- **同一回答双写（已修复，第五轮）**：`/chat/stream`、`/chat/regenerate` 流完成时后端写链，前端 `saveToBackend→batchSave` 又追加一份 → 链里每轮回答两份（本地链文件实证：后端 naive 时间 + 前端 UTC 时间同秒两条），后续编辑/版本操作按索引只改其中一份 → 出现"一条有版本条、一条没有"的截图现象 → **删除前端两处 `saveToBackend` 调用及函数，后端为聊天唯一写入点**（`batchSave` 端点保留兼容，主流程不再调用）
- **加载态残留（已修复，第五轮）**：`sendStreamMessage` 完成后 `isStreaming=false` 要等 `finally`，中间串行 await 标题生成/会话刷新 → 已完成回答下方 typing 三点指示器残留数秒（"明明还在却显示在加载"）→ push 完成消息后立即复位 `isStreaming`
- **双版本条冗余（已修复，第五、六轮）**：提问侧+回答侧各渲染一个版本条 → 第五轮先收敛为单侧（回答侧），第六轮按用户反馈改挂**用户消息**（"切换不应该在 AI 消息上面，应该在我发的消息上面"）：版本条 `role==='user'` 渲染，AI 消息不出条、内容随 `browseMap` 联动切换与描边
- **版本计数与实际不符（已修复，第六轮）**：显示"N个版本"（=历史数 N）但实际可切换 N+1 格（当前+N历史）→ "看似只有两个却有3个" → `positionLabel` 总数改为 **N+1（含当前）**：`当前 1/3`、`2/3`、`3/3`，数字与格数自洽
- **AI 回答独立编辑历史暂无浏览入口（第六轮限制）**：版本条移至用户消息后，仅编辑过 AI 回答（铅笔）而从未编辑过提问的会话无切换入口（提问 versions 为空不出条）；恢复/删除逻辑仍支持 `field='versions'`，待后续决定入口形态
- **编辑/恢复/删除静默失败（已修复，第五轮）**：`http.ts` 拦截器对业务错误（code≠200）也 resolve，调用方不检查 code → 后端替换/截断失败时本地照改造成分叉 → 三个方法显式检查 `res.code`，失败返回错误信息并中止后续操作
- **旧数据 content 混入 thinking（不回溯）**：修复前后端把 thinking 拼进 content 落链，老消息的思考文本仍显示在正文；新数据起 thinking 独立字段存储
- **旧数据残留**：历史链文件里的 `originalContent` 字段不主动清洗，读取时过滤不下发，下次编辑时随重写自然消失
- **AI 学习退化**：edits.json 不再存原文后，无 keyPoint 的旧记录不再注入 prompt（符合"只存要点"决策）
- **用户提问编辑链截断**：`truncate_after` 失败仅记 warning（前端本地仍截断），极端情况刷新后旧问答复现——低概率，后续可加重试
- type-check 9 处、lint 8 处为既有基线（RagAssistantView readonly 2 处属既有），本次无新增

## 验证方式

```bash
# 后端逻辑单测（临时目录直测，已全绿）
# 编辑6次成功第7次 EditQuotaExceeded、每次快照改前内容、
# 切换可见原文、恢复不占配额、删除/删空不影响 content、越界 IndexError
# 第四轮：paired 成对落盘/对齐、field=paired 恢复删除、非法 field 拒绝
# 第五轮（test_chain_v134.py）：write/read 追加、truncate 按消息数跨文件截断、
#   replace 快照、restore/delete × versions|paired、越界/非法 field —— 15/15 全绿
cd DixyangFast && python -m py_compile src/dixiyang/services/*.py src/dixiyang/routers/*.py src/dixiyang/schemas/*.py

# 前端
cd dixiyang-vue/Dixiyang-vue3
npm run type-check   # 9 处既有，无新增
npm run lint         # 8 处既有，无新增
npx vite build       # ✓ built
```

手工清单（需前后端服务运行）：
1. 消息内容正常显示（空白回归验收）
2. 编辑 AI 回答 → 气泡出现版本条 `当前 · 1个版本`；再改 → `2个版本`
3. 点 ‹ › 浏览历史，气泡内容切换 + `is-browsing` 描边；点「恢复此版本」→ 对话内容替换
4. 「删除」→ 确认弹窗（回车不触发）→ 版本减一、提示「修改次数减一」
5. 改满 6 次 → 第 7 次点编辑被 `warning` 拦截；删 1 个版本后可再改
6. 编辑用户提问 → 刷新后新内容仍在、其后旧问答已截断（原刷新复现 bug 修复）
7. 编辑弹窗只有单个输入框（无「原始回答」）
8. 抓 `/chat/stream` system prompt：无「原文「…」→修正版」字样
9. **（第四轮）编辑提问 1 次 → 浏览提问 1/1 时下方回答同步显示改前那次的回答**；改 2 次在 3 个问答对间循环，刷新后联动仍在
10. **（第四轮）删除/恢复提问版本 → 回答成对变化**；提问与回答两条版本条索引始终一致
11. **（第四轮）手动点重新生成 → `paired` 不变**（再编辑提问后联动仍对齐）
12. **（第五轮）发送一条消息 → 会话目录链文件内该轮问答只有一份**（无同秒双份）；编辑提问/重新生成后同样无重复回答
13. **（第五、六轮）版本条只在用户消息上**；AI 消息无条但内容随切换联动、`is-browsing` 描边同步；计数显示 `当前 1/3 → 2/3 → 3/3`（总数=历史+当前，与实际格数一致）
14. **（第五轮）流式生成结束瞬间 typing 三点指示器立即消失**（不再残留到标题生成/会话刷新完成）
15. **（第五轮）带 thinking 的新回答刷新后**：思考文本在「思考过程」折叠区、不在正文（老数据正文含思考属已知不回溯）
