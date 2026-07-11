"""
Pydantic Schema 导出
"""
from app.schemas.schemas import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
    DocumentBase,
    DocumentCreate,
    DocumentResponse,
    DocumentListResponse,
    ChatRequest,
    ChatResponse,
    DashboardStats,
    SalesTrendItem,
    DashboardResponse,
    # P1 扩展：新增的 Dashboard 拆分端点响应模型
    DashboardSummaryResponse,
    SalesTrendItemV2,
    CategoryStatItem,
    CategoryStatsResponse,
    ReportRequest,
    ReportDataSummary,
    ReportResponse,
    # P2 扩展：AI 业务分析师（三段式报告）Schema
    ReportGenerateRequest,
    BusinessInsightReport,
    # P3 扩展：RAG 带来源问答 Schema
    SourceItem,
    ChatWithSourcesResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "DocumentBase",
    "DocumentCreate",
    "DocumentResponse",
    "DocumentListResponse",
    "ChatRequest",
    "ChatResponse",
    "DashboardStats",
    "SalesTrendItem",
    "DashboardResponse",
    # P1 扩展：导出新增的 Schema
    "DashboardSummaryResponse",
    "SalesTrendItemV2",
    "CategoryStatItem",
    "CategoryStatsResponse",
    "ReportRequest",
    "ReportDataSummary",
    "ReportResponse",
    # P2 扩展：导出 AI 业务分析师（三段式报告）Schema
    "ReportGenerateRequest",
    "BusinessInsightReport",
    # P3 扩展：导出 RAG 带来源问答 Schema
    "SourceItem",
    "ChatWithSourcesResponse",
]
