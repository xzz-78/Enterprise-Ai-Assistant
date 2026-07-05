import apiClient from './apiClient'
import type { DashboardResponse } from '../types'

// 获取 Dashboard 数据
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
