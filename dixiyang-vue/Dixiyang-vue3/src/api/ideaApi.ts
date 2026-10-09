import http from '@/utils/http';

// ==================== 类型 ====================

export type IdeaCategory = 'idea' | 'character' | 'setting' | 'timeline' | 'tech';
export type IdeaSort = 'new' | 'hot' | 'like';

export interface IdeaPostItem {
  id: number;
  category: IdeaCategory;
  title: string;
  summary: string;
  authorId: number;
  authorName: string;
  tags: string[];
  attach: { id: number; type: string } | null;
  status: string;
  viewCount: number;
  likeCount: number;
  commentCount: number;
  collectCount: number;
  likedByMe: boolean;
  createTime: string;
  content?: string;
  images: string[];
  coverUrl?: string | null;
}

export interface IdeaDraftItem {
  id: number;
  category: IdeaCategory;
  title: string;
  summary: string;
  sourceRef?: string | null;
  updateTime: string;
}

export interface IdeaDraftDetail extends IdeaDraftItem {
  content: string;
  tags: string[];
  images?: string[];
}

export interface IdeaPage<T> {
  total: number;
  list: T[];
}

export interface IdeaComment {
  id: number;
  authorId: number;
  authorName: string;
  content: string;
  createTime: string;
}

export interface IdeaTagCount {
  tag: string;
  count: number;
}

export interface CharacterCard {
  characterId: number;
  novelId: number;
  name: string;
  gender?: string | null;
  age?: number | null;
  appearance?: string | null;
  background?: string | null;
  personality?: string | null;
}

// ==================== 草稿 ====================

export const listDrafts = (params: { category?: string; q?: string; page?: number; pageSize?: number }) =>
  http.get('/idea/drafts', { params });

export const createDraft = (body: {
  category: IdeaCategory;
  title: string;
  content: string;
  tags?: string[];
  images?: string[];
  sourceRef?: string;
}) => http.post('/idea/drafts', body);

export const getDraft = (id: number) => http.get<IdeaDraftDetail>(`/idea/drafts/${id}`);

export const updateDraft = (
  id: number,
  body: { category: IdeaCategory; title: string; content: string; tags?: string[]; images?: string[]; sourceRef?: string },
) => http.put(`/idea/drafts/${id}`, body);

export const deleteDraft = (id: number) => http.delete(`/idea/drafts/${id}`);

export const publishDraft = (id: number, previewed: boolean) =>
  http.post(`/idea/drafts/${id}/publish`, { previewed });

// ==================== 帖子 ====================

export const listPosts = (params: {
  category?: string;
  sort?: IdeaSort;
  q?: string;
  tags?: string;
  page?: number;
  pageSize?: number;
}) => http.get('/idea/posts', { params });

export const getPost = (id: number) => http.get<IdeaPostItem>(`/idea/posts/${id}`);

export const getAttachment = (id: number) =>
  http.get<{ type: string; data: unknown }>(`/idea/posts/${id}/attachment`);

export const importAttachment = (id: number, novelId: number) =>
  http.post<{ characters: { characterId: number; name: string }[] }>(`/idea/posts/${id}/import`, { novelId });

export const removePost = (id: number) => http.post(`/idea/posts/${id}/remove`);
export const restorePost = (id: number) => http.post(`/idea/posts/${id}/restore`);

export const listMinePosts = (params: { page?: number; pageSize?: number }) =>
  http.get('/idea/mine/posts', { params });

// ==================== 互动 ====================

export const toggleLike = (id: number) =>
  http.post<{ liked: boolean; likeCount: number }>(`/idea/posts/${id}/like`);

export const toggleCollect = (id: number) =>
  http.post<{ collected: boolean; collectCount: number }>(`/idea/posts/${id}/collect`);

export const listMineCollects = (params: { page?: number; pageSize?: number }) =>
  http.get('/idea/mine/collects', { params });

export const listMineLikes = (params: { page?: number; pageSize?: number }) =>
  http.get('/idea/mine/likes', { params });

// ==================== 评论 ====================

export const listComments = (postId: number, params: { page?: number; pageSize?: number }) =>
  http.get(`/idea/posts/${postId}/comments`, { params });

export const addComment = (postId: number, content: string) =>
  http.post<IdeaComment>(`/idea/posts/${postId}/comments`, { content });

export const deleteComment = (commentId: number) => http.delete(`/idea/comments/${commentId}`);

// ==================== 标签 ====================

export const listTags = (top = 30) => http.get<IdeaTagCount[]>('/idea/tags', { params: { top } });

// ==================== 关联数据（选择来源用） ====================

export const getNovelOptions = () => http.get<{ records: { id: number; title: string }[] }>('/novel/listall', { params: { page: 1, pageSize: 50 } });

export const getCharacters = (novelId: number) => http.get(`/novelCharacter/all/${novelId}`);

export const getChatSessions = (novelId?: number | null) =>
  http.get('/chatHistory/sessions', { params: novelId ? { novelId } : {} });

// ==================== 配图上传 ====================

export const uploadIdeaImage = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await http.post('/upload/idea-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res as { code?: number; msg?: string; data?: string };
};
