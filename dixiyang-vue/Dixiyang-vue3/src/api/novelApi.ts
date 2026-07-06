import http, { assertApiResponse } from '@/utils/http';
import type { ApiResponse, Novel, NovelDTO, PageResult } from '@/api/types';

// 获取小说列表
export const getNovelList = async (page = 1, pageSize = 10) => {
  const res = await http.get('/novel/listall', {
    params: { page, pageSize }
  });
  return assertApiResponse<PageResult<Novel>>(res);
};

// 创建小说
export const createNovel = async (novelDTO: NovelDTO) => {
  const res = await http.post('/novel/create', novelDTO);
  return assertApiResponse<Novel>(res);
};

// 上传小说封面
export const uploadNovelCover = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await http.post('/upload/novel-cover', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return assertApiResponse<string>(res);
};

// 删除小说封面（物理文件 + 清数据库 cover_url）
export const deleteNovelCover = async (url: string, novelId: string | number) => {
  const res = await http.delete('/upload/novel-cover', { params: { url, novelId } });
  return assertApiResponse<void>(res);
};

// 上传背景图
export const uploadBgImage = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await http.post('/upload/background', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return assertApiResponse<{ bgUrl: string }>(res);
};

// 删除背景图（物理文件 + 清数据库索引）
export const deleteBgImage = async (url: string, userId: string | number) => {
  const res = await http.delete('/upload/background', { params: { url, userId } });
  return assertApiResponse<void>(res);
};

// 删除小说
export const deleteNovel = (novelId: string | number) => {
  return http.post(`/novel/delete/${novelId}`);
};

// 根据ID获取单本小说详情（子页面用来显示小说名称和封面）
export const getNovelById = async (novelId: string | number) => {
  const res = await http.get(`/novel/${novelId}`);
  return assertApiResponse<Novel>(res);
};
