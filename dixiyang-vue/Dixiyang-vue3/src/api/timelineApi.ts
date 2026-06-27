import http from '@/utils/http'
import type { ApiResponse, Timeline, TimelineNode } from '@/api/types'

export const getAllTimelines = (novelId: number) => {
  return http.get(`/timeline/all/${novelId}`) as Promise<ApiResponse<Timeline[]>>
}

export const getAllStoryNodes = (novelId: number) => {
  return http.get(`/storyNode/all/${novelId}`) as Promise<ApiResponse<TimelineNode[]>>
}

export const getStoryNodesByTimeline = (timelineId: number) => {
  return http.get(`/storyNode/timeline/${timelineId}`) as Promise<ApiResponse<TimelineNode[]>>
}

export const createTimeline = (dto: { novelId: number; name: string; description?: string }) => {
  return http.post('/timeline/create', dto) as Promise<ApiResponse<Timeline>>
}

export const updateTimeline = (id: number, dto: { name?: string; description?: string }) => {
  return http.post(`/timeline/update/${id}`, dto) as Promise<ApiResponse<Timeline>>
}

export const deleteTimeline = (id: number) => {
  return http.post(`/timeline/delete/${id}`) as Promise<ApiResponse<null>>
}

export const createStoryNode = (dto: {
  novelId: number; timelineId: number; title: string; content?: string;
  eventDate?: string; eventType?: string; importance?: number;
  characterNames?: string; tags?: string
}) => {
  return http.post('/storyNode/create', dto) as Promise<ApiResponse<TimelineNode>>
}

export const updateStoryNode = (id: number, dto: {
  title?: string; content?: string; eventDate?: string; eventType?: string;
  importance?: number; characterNames?: string; tags?: string
}) => {
  return http.post(`/storyNode/update/${id}`, dto) as Promise<ApiResponse<TimelineNode>>
}

export const deleteStoryNode = (id: number) => {
  return http.post(`/storyNode/delete/${id}`) as Promise<ApiResponse<null>>
}
