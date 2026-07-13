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
  source?: 'rag' | 'llm' | 'empty_knowledge'
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

// P1 扩展：拆分端点对应的前端类型
// 与后端 DashboardSummaryResponse / SalesTrendItemV2 / CategoryStatsResponse 对齐
export interface DashboardSummary {
  total_revenue: number
  total_orders: number
  total_customers: number
  last_updated: string | null
}

export interface SalesTrendItemV2 {
  order_date: string
  date: string
  revenue: number
  orders: number
  customers: number
  region: string | null
}

export interface CategoryStat {
  category: string
  revenue: number
  orders: number
  customers: number
}

export interface CategoryStatsResponse {
  total: number
  items: CategoryStat[]
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

// P2 扩展：AI 业务分析师（三段式报告）类型
// 与后端 ReportGenerateRequest / BusinessInsightReport 对齐
export interface ReportGenerateRequest {
  days: number
}

export interface BusinessInsightReport {
  summary: string
  insights: string[]
  suggestions: string[]
}

// P3 扩展：RAG 带来源问答类型
// 与后端 SourceItem / ChatWithSourcesResponse 对齐
export interface SourceItem {
  filename: string
  document_id: number
  score: number
  content: string
}

export interface ChatWithSourcesResponse {
  answer: string
  sources: SourceItem[]
}
