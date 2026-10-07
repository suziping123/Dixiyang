// 本地章节草稿 IndexedDB 封装（原生 API）；IDB 不可用时降级为内存 Map

const DB_NAME = 'dixiyang-drafts'
const DB_VERSION = 1
const STORE_NAME = 'chapters'
const INDEX_NOVEL_ID = 'novelId'

export interface ChapterDraft {
  chapterId: number
  novelId: number
  title: string
  content: string
  updatedAt: number // 本地最后修改时间戳
  serverVersion: number // 最后同步到云端的版本号
  serverHash: string // 最后同步的内容 hash
  wordCount: number
  isDirty: boolean // 有未上传到云端的修改
}

let dbPromise: Promise<IDBDatabase> | null = null
let memoryMode = false
const memoryStore = new Map<number, ChapterDraft>()

function warnDev(e: unknown): void {
  if (import.meta.env.DEV) console.warn('[draftDB]', e)
}

function isSupported(): boolean {
  try {
    return typeof indexedDB !== 'undefined' && indexedDB !== null
  } catch {
    return false
  }
}

/** 打开数据库（单例缓存）；失败时转内存降级并 reject */
export function openDraftDB(): Promise<IDBDatabase> {
  if (dbPromise) return dbPromise
  if (memoryMode || !isSupported()) {
    memoryMode = true
    return Promise.reject(new Error('IndexedDB 不可用'))
  }
  dbPromise = new Promise<IDBDatabase>((resolve, reject) => {
    let request: IDBOpenDBRequest
    try {
      request = indexedDB.open(DB_NAME, DB_VERSION)
    } catch (e) {
      reject(e)
      return
    }
    let settled = false
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'chapterId' })
        store.createIndex(INDEX_NOVEL_ID, 'novelId', { unique: false })
      }
    }
    request.onsuccess = () => {
      if (settled) {
        request.result.close()
        return
      }
      settled = true
      const db = request.result
      // 其他标签页触发版本升级时释放连接，避免后续 open 永久 blocked
      db.onversionchange = () => {
        db.close()
        dbPromise = null
      }
      resolve(db)
    }
    request.onerror = () => {
      if (settled) return
      settled = true
      reject(request.error ?? new Error('IndexedDB 打开失败'))
    }
    request.onblocked = () => {
      if (settled) return
      settled = true
      reject(new Error('IndexedDB 打开被阻塞'))
    }
  })
  // 打开失败转内存模式，并允许下次重新尝试前先走降级
  dbPromise.catch(() => {
    dbPromise = null
    memoryMode = true
  })
  return dbPromise
}

function txDone(tx: IDBTransaction): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error ?? new Error('IndexedDB 事务失败'))
    tx.onabort = () => reject(tx.error ?? new Error('IndexedDB 事务中止'))
  })
}

// upsert：按 chapterId 主键写入
export async function putDraft(draft: ChapterDraft): Promise<void> {
  if (memoryMode) {
    memoryStore.set(draft.chapterId, { ...draft })
    return
  }
  let db: IDBDatabase
  try {
    db = await openDraftDB()
  } catch {
    memoryStore.set(draft.chapterId, { ...draft })
    return
  }
  const tx = db.transaction(STORE_NAME, 'readwrite')
  tx.objectStore(STORE_NAME).put(draft)
  await txDone(tx)
}

/** 读取单条草稿；任何失败均返回 null，不抛错 */
export async function getDraft(chapterId: number): Promise<ChapterDraft | null> {
  if (memoryMode) return memoryStore.get(chapterId) ?? null
  let db: IDBDatabase
  try {
    db = await openDraftDB()
  } catch {
    return memoryStore.get(chapterId) ?? null
  }
  try {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const req = tx.objectStore(STORE_NAME).get(chapterId)
    const result = await new Promise<ChapterDraft | undefined>((resolve, reject) => {
      req.onsuccess = () => resolve(req.result as ChapterDraft | undefined)
      req.onerror = () => reject(req.error)
    })
    return result ?? null
  } catch (e) {
    warnDev(e)
    return null
  }
}

export async function deleteDraft(chapterId: number): Promise<void> {
  if (memoryMode) {
    memoryStore.delete(chapterId)
    return
  }
  let db: IDBDatabase
  try {
    db = await openDraftDB()
  } catch {
    memoryStore.delete(chapterId)
    return
  }
  const tx = db.transaction(STORE_NAME, 'readwrite')
  tx.objectStore(STORE_NAME).delete(chapterId)
  await txDone(tx)
}

/** 按 novelId 索引取该小说全部草稿 */
export async function listDraftsByNovel(novelId: number): Promise<ChapterDraft[]> {
  if (memoryMode) {
    return [...memoryStore.values()].filter((d) => d.novelId === novelId)
  }
  let db: IDBDatabase
  try {
    db = await openDraftDB()
  } catch {
    return [...memoryStore.values()].filter((d) => d.novelId === novelId)
  }
  try {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const index = tx.objectStore(STORE_NAME).index(INDEX_NOVEL_ID)
    const req = index.getAll(novelId)
    const result = await new Promise<ChapterDraft[]>((resolve, reject) => {
      req.onsuccess = () => resolve(req.result as ChapterDraft[])
      req.onerror = () => reject(req.error)
    })
    return result ?? []
  } catch (e) {
    warnDev(e)
    return []
  }
}

/** 云端保存成功后清除脏标记 */
export async function clearDirtyByChapter(chapterId: number): Promise<void> {
  if (memoryMode) {
    const existing = memoryStore.get(chapterId)
    if (existing) memoryStore.set(chapterId, { ...existing, isDirty: false })
    return
  }
  let db: IDBDatabase
  try {
    db = await openDraftDB()
  } catch {
    const existing = memoryStore.get(chapterId)
    if (existing) memoryStore.set(chapterId, { ...existing, isDirty: false })
    return
  }
  const tx = db.transaction(STORE_NAME, 'readwrite')
  const store = tx.objectStore(STORE_NAME)
  const req = store.get(chapterId)
  const existing = await new Promise<ChapterDraft | undefined>((resolve, reject) => {
    req.onsuccess = () => resolve(req.result as ChapterDraft | undefined)
    req.onerror = () => reject(req.error)
  })
  if (existing) store.put({ ...existing, isDirty: false })
  await txDone(tx)
}
