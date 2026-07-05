import apiClient from './apiClient'
import type { ReportResponse, ReportRequest } from '../types'

// 生成 AI 分析报告
export const generateReport = async (days = 30): Promise<ReportResponse> => {
  const data: ReportRequest = { days }
  return apiClient.post('/report', data)
}
