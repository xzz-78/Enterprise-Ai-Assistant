import apiClient from './apiClient'
import type {
  DashboardResponse,
  DashboardSummary,
  SalesTrendItemV2,
  CategoryStatsResponse,
} from '../types'

// 获取 Dashboard 数据（兼容旧接口）
export const getDashboardData = async (days = 30): Promise<DashboardResponse> => {
  return apiClient.get('/dashboard', {
    params: { days },
  })
}

// 生成模拟数据
export const generateMockData = async (days = 90): Promise<any> => {
  return apiClient.post('/dashboard/generate-mock-data', null, {
    params: { days },
  })
}

// P1 扩展：调用 /api/dashboard/summary 获取汇总
export const getSummary = async (): Promise<DashboardSummary> => {
  return apiClient.get('/dashboard/summary')
}

// P1 扩展：调用 /api/dashboard/trend 获取最近 N 天的趋势
export const getTrend = async (days = 30): Promise<SalesTrendItemV2[]> => {
  return apiClient.get('/dashboard/trend', {
    params: { days },
  })
}

// P1 扩展：调用 /api/dashboard/category 获取产品分类统计
export const getCategoryStats = async (): Promise<CategoryStatsResponse> => {
  return apiClient.get('/dashboard/category')
}
