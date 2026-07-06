import http from '@/utils/http';
import type { Character, CharacterDTO, PageResult } from '@/api/types';

// 根据小说ID获取角色列表（分页）
export const getCharacterList = (novelId: number, page = 1, pageSize = 10) => {
  return http.get<PageResult<Character>>(`/novelCharacter/list/${novelId}`, {
    params: { page, pageSize }
  });
};

// 获取小说所有角色列表（不分页）
export const getAllCharacters = (novelId: number) => {
  return http.get<Character[]>(`/novelCharacter/all/${novelId}`);
};

// 根据ID获取角色详情
export const getCharacterById = (id: number) => {
  return http.get<Character>(`/novelCharacter/${id}`);
};

// 处理 extra 字段：如果 extra 为空字符串时设为 undefined，有内容尝试转为 JSON 字符串兼容后端 JSON 类型
const processCharacterData = (characterDTO: CharacterDTO) => {
  const { extra, ...rest } = characterDTO;
  const data: Omit<CharacterDTO, 'extra'> & { extra?: Record<string, unknown> | string } = { ...rest };
  
  if (extra && extra.trim()) {
    try {
      data.extra = JSON.parse(extra);
    } catch (e) {
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
  return http.post<Character>('/novelCharacter/create', data);
};

// 更新角色
export const updateCharacter = (id: number, characterDTO: CharacterDTO) => {
  const data = processCharacterData(characterDTO);
  return http.post<Character>(`/novelCharacter/update/${id}`, data);
};

// 删除角色
export const deleteCharacter = (id: number) => {
  return http.post(`/novelCharacter/delete/${id}`);
};
