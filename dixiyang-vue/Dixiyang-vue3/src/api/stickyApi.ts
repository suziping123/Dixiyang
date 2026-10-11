import http from '@/utils/http';

// ==================== 类型 ====================

export type StickyColor = 'yellow' | 'pink' | 'blue' | 'green' | 'purple';

export interface StickyNoteItem {
  id: number;
  color: StickyColor;
  /** 归一化坐标 0~1（相对视口），窗口缩放不漂移 */
  x: number;
  y: number;
  /** 钉住的路由 path；null=浮动（全站可见可拖） */
  pinnedRoute: string | null;
  /** 已投喂 AI 补全素材池 */
  inPool: boolean;
  rotation: number;
  zIndex: number;
  content: string;
  images: string[];
  createTime: string | null;
  updateTime: string | null;
  /** 完成态：划掉/勾选 */
  done: boolean;
}

// ==================== 便签 CRUD ====================

export const listNotes = () => http.get<StickyNoteItem[]>('/sticky/notes');

export const listPool = () => http.get<StickyNoteItem[]>('/sticky/pool');

export const createNote = (body: { content: string; color: StickyColor; x: number; y: number; images?: string[] }) =>
  http.post<StickyNoteItem>('/sticky/notes', body);

export interface NoteUpdateBody {
  content?: string;
  color?: StickyColor;
  x?: number;
  y?: number;
  images?: string[];
  /** True=钉在 routePath；False=解锁回浮动 */
  pinned?: boolean;
  routePath?: string;
  inPool?: boolean;
  zIndex?: number;
  done?: boolean;
}

export const updateNote = (id: number, body: NoteUpdateBody) => http.put<StickyNoteItem>(`/sticky/notes/${id}`, body);

export const deleteNote = (id: number) => http.delete(`/sticky/notes/${id}`);

// ==================== 配图上传 ====================

export const uploadNoteImage = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await http.post('/upload/note-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res as { code?: number; msg?: string; data?: string };
};
