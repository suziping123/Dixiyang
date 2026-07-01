import http, { assertApiResponse } from '@/utils/http'
import type { ApiResponse } from '@/api/types'

export interface RagStats {
  total_collections: number
  total_documents?: number
  embedding_model: string
  embedding_dimension: number
  collection_details: {
    name: string
    id: string
    count: number
  }[]
  connected: boolean
  error?: string
}

export interface RagDocument {
  id: string
  content: string
  metadata: Record<string, unknown> | null
  score?: number
}

export interface RagDocPage {
  ids: string[]
  documents: string[]
  metadatas: Record<string, unknown>[] | null
  page: number
  page_size: number
  error?: string
}

export interface RagSearchResult {
  query: string
  results: RagDocument[]
  error?: string
}

export const getRagStats = async () => {
  const res = await http.get('/rag/stats')
  return assertApiResponse<RagStats>(res)
}

export const getRagCount = async () => {
  const res = await http.get('/rag/count')
  return assertApiResponse<number>(res)
}

export const getRagDocuments = async (page = 1, pageSize = 20) => {
  const res = await http.get('/rag/documents', { params: { page, pageSize } })
  return assertApiResponse<RagDocPage>(res)
}

export const searchRag = async (query: string, topK = 5) => {
  const res = await http.post('/rag/search', null, { params: { query, topK } })
  return assertApiResponse<RagSearchResult>(res)
}
