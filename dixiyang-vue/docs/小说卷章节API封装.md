# 小说卷/章节 API 封装层

## 需求

为小说编辑器（卷 Volume / 章节 Chapter / 云端正文）提供前端 API 封装，配套 `DixyangFast` 新增的 `/volumes`、`/chapters` 路由，供后续编辑器页面调用。

## 方案

完全复用 `novelApi.ts` 既有风格：`import http, { assertApiResponse } from '@/utils/http'` + `async/await` + `assertApiResponse<T>(res)`，返回 `Promise<ApiResponse<T>>`。`http` 已配置 `baseURL: '/api'`，函数内只写相对路径。

### 类型定义（`src/api/types.ts` 末尾追加）

| 类型 | 说明 |
|------|------|
| `Volume` / `VolumeDTO` | 卷实体（snake_case 对齐后端）/ 创建入参 |
| `Chapter` / `ChapterDTO` | 章节实体（含 `version`、`local_version`、`word_count` 等冲突检测字段）/ 入参 |
| `ChapterContent` | 云端正文（`GET /chapters/{id}/content` 返回） |
| `SaveContentResult` | 保存正文结果（含 `hasConflict`、`serverVersion`、`serverHash`） |
| `ConflictResult` | 冲突检测结果 |

### 接口清单（`src/api/chapterApi.ts`）

| 函数 | 方法与路径 |
|------|-----------|
| `listVolumes(novelId)` | `GET /volumes/novel/{novelId}` |
| `createVolume(novelId, dto: VolumeDTO)` | `POST /volumes/novel/{novelId}` |
| `updateVolume(volumeId, dto: Partial<VolumeDTO>)` | `POST /volumes/{volumeId}` |
| `deleteVolume(volumeId)` | `DELETE /volumes/{volumeId}` |
| `listChapters(novelId)` | `GET /chapters/novel/{novelId}` |
| `createChapter(novelId, dto)` | `POST /chapters/novel/{novelId}` |
| `updateChapter(chapterId, dto)` | `POST /chapters/{chapterId}` |
| `deleteChapter(chapterId)` | `DELETE /chapters/{chapterId}` |
| `getChapterContent(chapterId)` | `GET /chapters/{chapterId}/content` |
| `saveChapterContent(chapterId, payload)` | `POST /chapters/{chapterId}/content` |
| `checkContentConflict(chapterId, payload)` | `POST /chapters/{chapterId}/content/conflict-check` |

`createChapter` / `updateChapter` 的 dto 用 `Omit<ChapterDTO, 'novel_id'>`（novelId 走路径参数，避免与 body 重复）。

## 改动文件

- `dixiyang-vue/Dixiyang-vue3/src/api/types.ts`：末尾追加上述 7 个接口类型（未改动已有内容）
- `dixiyang-vue/Dixiyang-vue3/src/api/chapterApi.ts`：新增，导出 11 个函数

## 已知问题

- `npm run type-check` 存在**既有**错误（`localImages.ts`、`storyMappings.ts`、`RagAssistantView.vue`、`TimelineView.vue`），与本次改动无关；本次两个文件零报错
- 后端路由若与上述路径不一致，需对照 `DixyangFast/src/dixiyang/routers/volume.py`、`chapter.py` 校正
- `saveChapterContent` 首次保存时 `clientHash` 约定传 `''`（后端以空哈希识别首版）

## 验证方式

```bash
cd dixiyang-vue/Dixiyang-vue3
npm run type-check   # 确认无 chapterApi.ts / types.ts 相关错误
npm run lint
```
