/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-21 15:30:13
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-24 13:25:10
 * @FilePath: \Dixiyang\dixiyang-vue\Dixiyang-vue3\src\api\novelApi.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import http, { assertApiResponse } from '@/utils/http';
import type { ApiResponse } from '@/api/types';

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
export const getNovelList = async (page = 1, pageSize = 10) => {
  const res = await http.get('/novel/listall', {
    params: { page, pageSize }
  });
  return assertApiResponse<PageResult<NovelVO>>(res);
};

// 创建小说
export const createNovel = async (novelDTO: NovelDTO) => {
  const res = await http.post('/novel/create', novelDTO);
  return assertApiResponse<NovelVO>(res);
};

// 上传小说封面
export const uploadNovelCover = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await http.post('/upload/novel-cover', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return assertApiResponse<{ coverUrl: string }>(res);
};

// 删除小说
export const deleteNovel = (novelId: string | number) => {
  return http.post(`/novel/delete/${novelId}`);
};
