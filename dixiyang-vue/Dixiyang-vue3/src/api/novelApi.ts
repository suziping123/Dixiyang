import http from '@/utils/http';

// 小说DTO类型定义
export interface NovelDTO {
  title: string;
  penName: string;
  description: string;
  coverUrl?: string;
}

// 小说VO类型定义
export interface NovelVO extends NovelDTO {
  id: string | number;
  createTime?: string;
  updateTime?: string;
  charCount?: number;
  nodeCount?: number;
  relationCount?: number;
}

// 分页返回结果类型
export interface PageResult<T> {
  records: T[];
  total: number;
  size: number;
  current: number;
  pages: number;
}

// 获取小说列表
export const getNovelList = (page = 1, pageSize = 10) => {
  return http.get<PageResult<NovelVO>>('/novel/listall', {
    params: { page, pageSize }
  });
};

// 创建小说
export const createNovel = (novelDTO: NovelDTO) => {
  return http.post<NovelVO>('/novel/create', novelDTO);
};

// 上传小说封面
export const uploadNovelCover = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return http.post<{ coverUrl: string }>('/upload/novel-cover', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 删除小说
export const deleteNovel = (novelId: string | number) => {
  return http.post(`/novel/delete/${novelId}`);
};
