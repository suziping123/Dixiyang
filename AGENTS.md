# OpenCode Global Rules

你是一个顶级的程序员。在每次对话中，你必须严格遵循以下“准则”：

## 核心准则

1. **绝对中文**：必须使用**简体中文**进行交流（除非是代码、专有名词等特殊情况）。
2. **言简意赅**：解释或评论代码时，必须附带**清晰且极为精简**的中文文档。
3. **先查后问**：遇到代码问题，优先在本项目的 `**/docs/` 目录或相关代码文件中寻找答案，找不到再向我提问。
4. **规划先行**：开始写代码前，必须先简要说明你的计划，并清晰扼要地分析其利弊。
5. **环境**：默认使用本目录下的环境
6. **大文本存文件系统**：所有用户生成的"大文本"内容（对话、分析、长描述等）必须存为服务器本地 JSON 文件，数据库只存文件路径/引用。路径约定 `storage/{module}/{userId}/{sessionId}/{recordId}.json`。此规则适用于：
   - AI 聊天历史（content / thinking）
   - 后续任何长文本字段
   - 或者文件，视频，日志等大文件或者可能会变成的大文件
7. **Java版本**：java17,sdkman

## 聊天编辑 & 重新生成设计

### 编辑 AI 回答（edits.json 方案）
- **后端核心**：`ChatContentFileService.java` - `addEditRecord()/readEdits()/buildEditsPrompt()/mergeEdits()`
- **编辑存储**：`storage/chat/{userId}/{sessionId}/edits.json`，与链文件同级
- **AI 学习**：每次 `/chat/stream` 请求携带 `sessionId` 时，自动从 `edits.json` 构建修正记录注入 system prompt
- **编辑端点**：`PUT /chatHistory/message/{sessionId}` → `ChatSessionServiceImpl.editMessage()`
- **链内修改**：`ChatContentFileService.replaceMessageInChain()` - 直接修改链文件中指定索引的消息内容；同时记录到 edits.json 供 AI 学习
- **前端触发**：`ChatMessage.vue` 编辑按钮 → `EditMessageModal.vue` (ElDialog 弹窗) → 原文对照 + textarea 编辑 → 保存

### 重新生成 AI 回答
- **SSE 端点**：`POST /chat/regenerate` → `ChatController.regenerate()`（真流式）
- **流程**：前端指定 `messageIndex` → 后端截断链文件 → 用截断后历史 + edits 构建 prompt → Flux 逐 token 推 SSE → 完成时追加新回答到链
- **链截断**：`ChatContentFileService.truncateChain(headPath, keepCount)` - 保留前 N 条，删除后续文件
- **前端触发**：`ChatMessage.vue` 重新生成按钮 → `useChatStream.regenerateMessage()`

### 流式输出（真流式）
- **端点**：`POST /chat/stream` → `ChatController.chatStream()` (SseEmitter 实现)
- **核心**：`chatClient.prompt(fullPrompt).stream().content()` 返回 `Flux<String>`，通过 `CountDownLatch` 桥接到 Servlet 线程，逐 token 推 SSE
- **JSON 文件修改**：`chatClient.prompt(fullPrompt).stream().content()` 改为 `chatClient.prompt(fullPrompt).call().content()`
- **thinking 标签**：后端 Flux 中实时检测 `<thinking>`/`</thinking>` 标签边界，拆分 SSE type=`thinking` / `content`
- **前/后端取消**：前端 AbortController.abort()，后端自动检测
- **思考过程渲染**：前端 `useChatStream.ts` 区分 type 渲染

### 修改 AI 行为的提示词位置
修改以下文件中的 prompt 字符串以控制 AI 行为：
1. `ChatController.java:171` - `buildFullPrompt()` 方法（主对话 prompt 构建，真流式 `stream().content()`）
2. `ChatController.java` - `/chat/regenerate` 端点中的 prompt 构建逻辑
3. `ChatSessionServiceImpl.java:171` - 标题生成 prompt（`generateAndUpdateTitle()`）
4. `ChatContentFileService.java:326` - `buildEditsPrompt()` 方法（编辑修正记录的 prompt 模板，注入到每次对话）

### 存储结构

统一存储根目录：`/home/lijiajia/项目/Dixiyang/uploads/`

```
uploads/
├── backgrounds/                    # 背景图（实际图片文件）
│   ├── {md5hash}.jpg              # 上传的背景图
│   └── {md5hash}.md5              # MD5 去重映射
├── covers/                         # 封面图（实际图片文件）
│   ├── {md5hash}.jpg
│   └── {md5hash}.md5
└── storage/                        # JSON 数据存储（DB 只存路径引用）
    ├── chat/{userId}/{sessionId}/
    │   ├── {timestamp}_{rand}.json  # 链文件（next 指针连接，纯文件名）
    │   ├── edits.json              # 编辑修正记录
    │   └── summary.json            # 历史摘要
    ├── character/{id}.json          # 角色设定
    └── user/
        ├── customBgs/{userId}.json  # 自定义背景元数据
        └── fontColors/{userId}.json # 字体颜色配置
```

### 文件引用格式（统一约定）

所有 DB 中的文件引用字段使用 `__file__:` 前缀 + 相对路径：

| 字段 | 格式示例 | 说明 |
|------|---------|------|
| `extra` | `__file__:character/{id}.json` | 角色设定 |
| `head_path` | `__file__:chat/{userId}/{sessionId}/{file}.json` | 聊天链头文件 |
| `custom_bgs` | `__file__:user/customBgs/{userId}.json` | 用户自定义背景 |
| `font_colors_json` | `__file__:user/fontColors/{userId}.json` | 字体颜色配置 |
| `cover_url` | `/api/uploads/covers/{filename}.png` | **例外**：HTTP URL，前端直接使用 |

**读取规则**：
- Java：`StorageService.loadJson(subdir, id, dbValue)` → 自动判断 `__file__:` 前缀
- Python：`storage_service.load_json(subdir, id, db_value)` → 同上

### 链文件 next 指针格式（统一约定）

链文件的 `next` 字段存储**纯文件名**（不含路径前缀）：
```json
{ "messages": [...], "next": "1783271834717_61b2d203.json" }
```
- 遍历时基于当前文件的父目录拼接：`Paths.get(currentFile).getParent().resolve(next)`
- 不使用 `./` 前缀，不使用绝对路径
