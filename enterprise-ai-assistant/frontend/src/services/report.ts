import apiClient from './apiClient'
import type { ReportResponse, ReportRequest, BusinessInsightReport, ReportGenerateRequest } from '../types'

// 生成 AI 分析报告（P0 兼容版本：返回 data_summary + ai_analysis + recommendations）
export const generateReport = async (days = 30): Promise<ReportResponse> => {
  const data: ReportRequest = { days }
  return apiClient.post('/report', data)
}

// P2 扩展：AI 业务分析师（三段式报告）
// 调用 POST /api/report/generate，固定走"SQL 聚合 → 数据汇总 → Prompt → LLM"
// 返回 {summary, insights[], suggestions[]}
export const generateBusinessReport = async (days = 30): Promise<BusinessInsightReport> => {
  const data: ReportGenerateRequest = { days }
  return apiClient.post('/report/generate', data)
}
