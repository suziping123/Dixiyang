import http, { assertApiResponse } from '@/utils/http';
import type {
  ApiResponse,
  Chapter,
  ChapterContent,
  ChapterDTO,
  ConflictResult,
  SaveContentResult,
  Volume,
  VolumeDTO
} from '@/api/types';

// 获取小说的卷列表
export const listVolumes = async (novelId: number | string): Promise<ApiResponse<Volume[]>> => {
  const res = await http.get(`/volumes/novel/${novelId}`);
  return assertApiResponse<Volume[]>(res);
};

// 创建卷
export const createVolume = async (novelId: number | string, dto: VolumeDTO): Promise<ApiResponse<Volume>> => {
  const res = await http.post(`/volumes/novel/${novelId}`, dto);
  return assertApiResponse<Volume>(res);
};

// 更新卷
export const updateVolume = async (volumeId: number, dto: Partial<VolumeDTO>): Promise<ApiResponse<Volume>> => {
  const res = await http.post(`/volumes/${volumeId}`, dto);
  return assertApiResponse<Volume>(res);
};

// 删除卷
export const deleteVolume = async (volumeId: number): Promise<ApiResponse<void>> => {
  const res = await http.delete(`/volumes/${volumeId}`);
  return assertApiResponse<void>(res);
};

// 获取小说的章节列表
export const listChapters = async (novelId: number | string): Promise<ApiResponse<Chapter[]>> => {
  const res = await http.get(`/chapters/novel/${novelId}`);
  return assertApiResponse<Chapter[]>(res);
};

// 创建章节
export const createChapter = async (novelId: number | string, dto: Omit<ChapterDTO, 'novel_id'>): Promise<ApiResponse<Chapter>> => {
  const res = await http.post(`/chapters/novel/${novelId}`, dto);
  return assertApiResponse<Chapter>(res);
};

// 更新章节
export const updateChapter = async (chapterId: number, dto: Partial<Omit<ChapterDTO, 'novel_id'>>): Promise<ApiResponse<Chapter>> => {
  const res = await http.post(`/chapters/${chapterId}`, dto);
  return assertApiResponse<Chapter>(res);
};

// 删除章节
export const deleteChapter = async (chapterId: number): Promise<ApiResponse<void>> => {
  const res = await http.delete(`/chapters/${chapterId}`);
  return assertApiResponse<void>(res);
};

// 获取章节云端正文
export const getChapterContent = async (chapterId: number): Promise<ApiResponse<ChapterContent>> => {
  const res = await http.get(`/chapters/${chapterId}/content`);
  return assertApiResponse<ChapterContent>(res);
};

// 保存章节正文（带版本/哈希冲突检测）
export const saveChapterContent = async (
  chapterId: number,
  payload: { title: string; content: string; clientVersion: number; clientHash: string; force?: boolean }
): Promise<ApiResponse<SaveContentResult>> => {
  const res = await http.post(`/chapters/${chapterId}/content`, payload);
  return assertApiResponse<SaveContentResult>(res);
};

// 检测正文冲突
export const checkContentConflict = async (
  chapterId: number,
  payload: { clientVersion: number; clientHash: string }
): Promise<ApiResponse<ConflictResult>> => {
  const res = await http.post(`/chapters/${chapterId}/content/conflict-check`, payload);
  return assertApiResponse<ConflictResult>(res);
};
