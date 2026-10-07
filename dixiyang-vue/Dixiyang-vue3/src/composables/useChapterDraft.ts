import { ref, getCurrentScope, onScopeDispose } from 'vue'
import type { Ref } from 'vue'
import { getDraft, putDraft } from '@/utils/draftDB'
import type { ChapterDraft } from '@/utils/draftDB'

export type SaveLocalState = 'idle' | 'saving' | 'saved' | 'error'

export interface DraftLoadResult {
  content: string
  fromLocal: boolean
  isDirty: boolean
}

/** 调用方提交的最小草稿输入，server 侧字段由 composable 合并 */
export interface DraftSaveInput {
  chapterId: number
  novelId: number
  title: string
  content: string
}

interface SyncContext {
  chapterId: number
  serverVersion: number
  serverHash: string
}

const SAVE_DEBOUNCE_MS = 800

/** 中文按字符计数，忽略所有空白 */
export function wordCount(content: string): number {
  return content.replace(/\s+/g, '').length
}

export function useChapterDraft() {
  const saveState: Ref<SaveLocalState> = ref('idle')

  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  let pendingDraft: DraftSaveInput | null = null
  // 当前章节的云端同步上下文，写入时用于组装 server 字段
  let syncCtx: SyncContext | null = null

  // 组装完整草稿：优先取当前章节上下文的 server 字段，否则沿用本地已有值
  async function buildDraft(input: DraftSaveInput): Promise<ChapterDraft> {
    let serverVersion = 0
    let serverHash = ''
    if (syncCtx && syncCtx.chapterId === input.chapterId) {
      serverVersion = syncCtx.serverVersion
      serverHash = syncCtx.serverHash
    } else {
      const prev = await getDraft(input.chapterId)
      if (prev) {
        serverVersion = prev.serverVersion
        serverHash = prev.serverHash
      }
    }
    return {
      ...input,
      updatedAt: Date.now(),
      serverVersion,
      serverHash,
      wordCount: wordCount(input.content),
      isDirty: true,
    }
  }

  async function commitPending(): Promise<void> {
    const input = pendingDraft
    if (!input) return
    pendingDraft = null
    try {
      await putDraft(await buildDraft(input))
      saveState.value = 'saved'
    } catch (e) {
      // 失败保留 pending，便于 flushSave 重试
      pendingDraft = input
      saveState.value = 'error'
      if (import.meta.env.DEV) console.warn('[useChapterDraft] 本地保存失败', e)
    }
  }

  // 优先返回本地草稿；本地无则返回云端内容并初始化本地记录
  async function loadDraft(
    novelId: number,
    chapterId: number,
    serverContent: string,
    serverVersion: number,
    serverHash: string,
  ): Promise<DraftLoadResult> {
    // 先落盘上一章节的待保存数据，避免被新章节上下文覆盖
    await flushSave()
    const local = await getDraft(chapterId)
    syncCtx = { chapterId, serverVersion, serverHash }
    saveState.value = 'idle'
    if (local) {
      return { content: local.content, fromLocal: true, isDirty: local.isDirty }
    }
    const fresh: ChapterDraft = {
      chapterId,
      novelId,
      title: '',
      content: serverContent,
      updatedAt: Date.now(),
      serverVersion,
      serverHash,
      wordCount: wordCount(serverContent),
      isDirty: false,
    }
    try {
      await putDraft(fresh)
    } catch (e) {
      if (import.meta.env.DEV) console.warn('[useChapterDraft] 初始化本地草稿失败', e)
    }
    return { content: serverContent, fromLocal: false, isDirty: false }
  }

  // 防抖 800ms 写入 IndexedDB
  function scheduleSave(draft: DraftSaveInput): void {
    pendingDraft = draft
    saveState.value = 'saving'
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      debounceTimer = null
      void commitPending()
    }, SAVE_DEBOUNCE_MS)
  }

  // 立即落盘（页面关闭 / 切换章节前调用）
  async function flushSave(): Promise<void> {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
    await commitPending()
  }

  // 云端保存成功后更新 server 字段并清除脏标记
  async function markSynced(chapterId: number, version: number, hash: string): Promise<void> {
    if (syncCtx && syncCtx.chapterId === chapterId) {
      syncCtx = { chapterId, serverVersion: version, serverHash: hash }
    }
    try {
      const existing = await getDraft(chapterId)
      if (!existing) return
      await putDraft({ ...existing, serverVersion: version, serverHash: hash, isDirty: false })
    } catch (e) {
      if (import.meta.env.DEV) console.warn('[useChapterDraft] markSynced 失败', e)
    }
  }

  // 清理定时器并尽力落盘未保存数据
  function dispose(): void {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
    if (pendingDraft) void commitPending()
  }

  if (getCurrentScope()) onScopeDispose(dispose)

  return { saveState, loadDraft, scheduleSave, flushSave, markSynced, wordCount, dispose }
}
