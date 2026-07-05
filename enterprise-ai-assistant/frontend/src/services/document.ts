import apiClient from './apiClient'
import type { Document, DocumentListResponse } from '../types'

// 获取文档列表
export const getDocuments = async (
  skip = 0,
  limit = 100
): Promise<DocumentListResponse> => {
  return apiClient.get('/documents', {
    params: { skip, limit },
  })
}

// 上传文档
export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// 删除文档
export const deleteDocument = async (docId: number): Promise<void> => {
  return apiClient.delete(`/documents/${docId}`)
}

// 获取文档详情
export const getDocumentById = async (docId: number): Promise<Document> => {
  return apiClient.get(`/documents/${docId}`)
}
