import { defineStore } from 'pinia'
import { ref } from 'vue'
import http, { assertApiResponse } from '@/utils/http'
import { getNovelById } from '@/api/novelApi'
import type { Novel } from '@/api/types'

export const useNovelStore = defineStore('novel', () => {
  const currentNovel = ref<Novel | null>(null)
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
    const id = Number(novelId)
    if (!id || isNaN(id)) return
    try {
      const res = await http.post(`/novel/update/${id}`, { coverUrl })
      assertApiResponse(res)
      if (currentNovel.value && String(currentNovel.value.id) === String(id)) {
        currentNovel.value = { ...currentNovel.value, cover_url: coverUrl }
      }
    } catch (e) {
      console.error('更新封面失败:', e)
    }
  }

  return { currentNovel, loading, loadNovel, clearNovel, updateCover }
})
