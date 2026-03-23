import http from '@/utils/http';

// 角色类型定义
export interface CharacterDTO {
  novelId: number;
  name: string;
  gender?: string;
  age?: number;
  appearance?: string;
  background?: string;
  personality?: string;
  extra?: string;
}

export interface CharacterVO extends CharacterDTO {
  id: number;
  createTime?: string;
}

// 分页返回结果类型
export interface PageResult<T> {
  records: T[];
  total: number;
  size: number;
  current: number;
  pages: number;
}

// 根据小说ID获取角色列表（分页）
export const getCharacterList = (novelId: number, page = 1, pageSize = 10) => {
  return http.get<PageResult<CharacterVO>>(`/novelCharacter/list/${novelId}`, {
    params: { page, pageSize }
  });
};

// 获取小说所有角色列表（不分页）
export const getAllCharacters = (novelId: number) => {
  return http.get<CharacterVO[]>(`/novelCharacter/all/${novelId}`);
};

// 根据ID获取角色详情
export const getCharacterById = (id: number) => {
  return http.get<CharacterVO>(`/novelCharacter/${id}`);
};

// 处理 extra 字段：如果 extra 为空字符串时设为 undefined，有内容尝试转为 JSON 字符串兼容后端 JSON 类型
const processCharacterData = (characterDTO: CharacterDTO) => {
  const { extra, ...rest } = characterDTO;
  const data: Omit<CharacterDTO, 'extra'> & { extra?: Record<string, unknown> | string } = { ...rest };
  
  if (extra && extra.trim()) {
    try {
      // 尝试解析为 JSON
      data.extra = JSON.parse(extra);
    } catch (e) {
      // 如果不是有效的JSON，作为字符串包装成简单的键值对
      data.extra = { content: extra };
    }
  } else {
    data.extra = undefined;
  }
  
  return data;
};

// 创建角色
export const createCharacter = (characterDTO: CharacterDTO) => {
  const data = processCharacterData(characterDTO);
  return http.post<CharacterVO>('/novelCharacter/create', data);
};

// 更新角色
export const updateCharacter = (id: number, characterDTO: CharacterDTO) => {
  const data = processCharacterData(characterDTO);
  return http.post<CharacterVO>(`/novelCharacter/update/${id}`, data);
};

// 删除角色
export const deleteCharacter = (id: number) => {
  return http.post(`/novelCharacter/delete/${id}`);
};
