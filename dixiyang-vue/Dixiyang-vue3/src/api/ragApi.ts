import http, { assertApiResponse } from '@/utils/http'
import type { ApiResponse } from '@/api/types'

export interface RagStats {
  total_collections: number
  total_documents?: number
  embedding_model: string
  embedding_dimension: number
  source_distribution?: Record<string, number>
  category_distribution?: Record<string, number>
  book_distribution?: Record<string, number>
  collection_details: {
    name: string
    id: string
    count: number
    metadata?: Record<string, unknown>
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
  total?: number
  error?: string
}

export interface RagSearchResult {
  query: string
  results: RagDocument[]
  total?: number
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

export const getRagDocuments = async (page = 1, pageSize = 20, source?: string) => {
  const params: Record<string, string | number> = { page, pageSize }
  if (source) params.source = source
  const res = await http.get('/rag/documents', { params })
  return assertApiResponse<RagDocPage>(res)
}

export const searchRag = async (
  query: string,
  topK = 5,
  sourceFilter?: string
) => {
  const params: Record<string, string | number | null> = { query, topK }
  if (sourceFilter) params.source_filter = sourceFilter
  const res = await http.post('/rag/search', null, { params })
  return assertApiResponse<RagSearchResult>(res)
}
