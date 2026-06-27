import { defineStore } from 'pinia'
import { ref } from 'vue'
import http, { assertApiResponse } from '@/utils/http'
import { getNovelById, type NovelVO } from '@/api/novelApi'

export const useNovelStore = defineStore('novel', () => {
  const currentNovel = ref<NovelVO | null>(null)
  const loading = ref(false)

  async function loadNovel(novelId: number | string) {
    if (currentNovel.value && String(currentNovel.value.id) === String(novelId)) return
    loading.value = true
    try {
      const res = await getNovelById(novelId)
      const data = (res as any).data
      currentNovel.value = data || null
    } catch {
      currentNovel.value = null
    } finally {
      loading.value = false
    }
  }

  function clearNovel() {
    currentNovel.value = null
  }

  async function updateCover(novelId: number | string, coverUrl: string) {
    try {
      const res = await http.post(`/novel/update/${novelId}`, { coverUrl })
      assertApiResponse(res)
      if (currentNovel.value && String(currentNovel.value.id) === String(novelId)) {
        currentNovel.value = { ...currentNovel.value, cover_url: coverUrl }
      }
    } catch (e) {
      console.error('更新封面失败:', e)
    }
  }

  return { currentNovel, loading, loadNovel, clearNovel, updateCover }
})
