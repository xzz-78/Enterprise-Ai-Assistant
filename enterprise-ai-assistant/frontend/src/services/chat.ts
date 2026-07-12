import apiClient from './apiClient'
import type { ChatRequest, ChatResponse, ChatWithSourcesResponse } from '../types'

// AI 问答
export const chat = async (question: string): Promise<ChatResponse> => {
  const data: ChatRequest = { question }
  return apiClient.post('/chat', data)
}

// AI 问答（带引用来源）
export const chatWithSources = async (question: string): Promise<ChatWithSourcesResponse> => {
  const data: ChatRequest = { question }
  return apiClient.post('/chat/with-sources', data)
}
