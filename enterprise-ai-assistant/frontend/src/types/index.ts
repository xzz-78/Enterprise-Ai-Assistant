// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

// 文档相关类型
export interface Document {
  id: number
  filename: string
  file_type: string
  file_size: number | null
  upload_time: string
  user_id: number
}

export interface DocumentListResponse {
  total: number
  documents: Document[]
}

// 聊天相关类型
export interface ChatRequest {
  question: string
}

export interface ChatResponse {
  answer: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// Dashboard 相关类型
export interface DashboardStats {
  total_revenue: number
  total_orders: number
  total_customers: number
}

export interface SalesTrendItem {
  date: string
  revenue: number
  orders: number
  customers: number
}

export interface DashboardResponse {
  stats: DashboardStats
  trend: SalesTrendItem[]
}

// 报告相关类型
export interface ReportDataSummary {
  total_revenue: number
  total_orders: number
  total_customers: number
  avg_daily_revenue: number
  revenue_growth_rate: number
}

export interface ReportResponse {
  data_summary: ReportDataSummary
  ai_analysis: string
  recommendations: string[]
}

export interface ReportRequest {
  days: number
}
