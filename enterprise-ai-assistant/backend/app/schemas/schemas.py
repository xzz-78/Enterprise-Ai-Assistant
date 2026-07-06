"""
Pydantic Schema 定义
用于 API 请求和响应的数据验证与序列化
"""
# P1 修复：把 `date` 导入改名为 `_Date`，避免与 SalesTrendItemV2 字段名 `date` 冲突
# Pydantic 2.13+ 在类体内处理 `date: date` 这样的同名字段+类型注解时
# 会触发 unevaluable-type-annotation 错误，重命名 import 是最稳妥的做法
from datetime import datetime
from datetime import date as _Date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator


# ============= 用户相关 Schema =============

class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    """用户创建 Schema（注册请求）"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """验证用户名只能包含字母数字和下划线"""
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserLogin(BaseModel):
    """用户登录 Schema"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应 Schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 配置，支持从 ORM 对象转换


class Token(BaseModel):
    """Token 响应 Schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据 Schema"""
    user_id: Optional[int] = None


# ============= 文档相关 Schema =============

class DocumentBase(BaseModel):
    """文档基础 Schema"""
    filename: str = Field(..., description="文件名")
    file_type: Optional[str] = Field(None, description="文件类型")


class DocumentCreate(DocumentBase):
    """文档创建 Schema"""
    file_path: str = Field(..., description="文件存储路径")
    file_size: Optional[int] = Field(None, description="文件大小")
    user_id: int = Field(..., description="上传用户ID")


class DocumentResponse(DocumentBase):
    """文档响应 Schema"""
    id: int
    file_size: Optional[int] = None
    upload_time: datetime
    user_id: int

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应 Schema"""
    total: int
    documents: List[DocumentResponse]


# ============= AI 问答相关 Schema =============

class ChatRequest(BaseModel):
    """AI 问答请求 Schema"""
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")


class ChatResponse(BaseModel):
    """AI 问答响应 Schema"""
    answer: str = Field(..., description="AI 回答")


# ============= Dashboard 相关 Schema =============

class DashboardStats(BaseModel):
    """Dashboard 统计数据 Schema"""
    total_revenue: float = Field(..., description="总销售额")
    total_orders: int = Field(..., description="总订单数")
    total_customers: int = Field(..., description="客户数量")


class SalesTrendItem(BaseModel):
    """销售趋势单项 Schema"""
    date: _Date
    revenue: float
    orders: int
    customers: int


class DashboardResponse(BaseModel):
    """Dashboard 响应 Schema"""
    stats: DashboardStats
    trend: List[SalesTrendItem]


# ============= P1 扩展：Dashboard 拆分端点的响应 Schema =============

class DashboardSummaryResponse(BaseModel):
    """
    Dashboard 汇总响应 Schema
    用于 GET /api/dashboard/summary
    """
    total_revenue: float = Field(..., description="总销售额")
    total_orders: int = Field(..., description="总订单数")
    total_customers: int = Field(..., description="总客户数")


class SalesTrendItemV2(BaseModel):
    """
    新版趋势项，同时暴露 date 与 order_date 两个字段（保持兼容）

    - order_date 字段对应数据库 Sale.date，命名遵循业务语义
    - date 字段作为别名字段保留，前端旧逻辑可直接读取
    """
    order_date: _Date = Field(..., description="销售日期（业务字段）")
    date: _Date = Field(..., description="销售日期（别名）")
    revenue: float = Field(..., description="销售额")
    orders: int = Field(..., description="订单数")
    customers: int = Field(..., description="客户数")
    region: Optional[str] = Field(None, description="销售区域，可为空")


class CategoryStatItem(BaseModel):
    """
    单个产品分类的统计项
    用于 GET /api/dashboard/category
    """
    category: str = Field(..., description="产品分类名称")
    revenue: float = Field(..., description="该分类累计销售额")
    orders: int = Field(..., description="该分类累计订单数")
    customers: int = Field(..., description="该分类累计客户数")


class CategoryStatsResponse(BaseModel):
    """
    产品分类统计响应 Schema
    用于 GET /api/dashboard/category
    """
    total: int = Field(..., description="分类数量")
    items: List[CategoryStatItem] = Field(..., description="分类列表")


# ============= AI 分析报告相关 Schema =============

class ReportRequest(BaseModel):
    """分析报告请求 Schema"""
    days: int = Field(default=30, ge=7, le=365, description="分析天数")


class ReportDataSummary(BaseModel):
    """报告数据摘要 Schema"""
    total_revenue: float
    total_orders: int
    total_customers: int
    avg_daily_revenue: float
    revenue_growth_rate: float


class ReportResponse(BaseModel):
    """AI 分析报告响应 Schema"""
    data_summary: ReportDataSummary
    ai_analysis: str = Field(..., description="AI 生成的分析内容")
    recommendations: List[str] = Field(..., description="改进建议列表")


# ============= P2 扩展：AI 业务分析师（三段式报告）Schema =============
# 仅追加在文件末尾，不修改上述任何已有类，保证与 P0/P1 兼容


class ReportGenerateRequest(BaseModel):
    """
    AI 业务分析报告生成请求 Schema
    对应端点：POST /api/report/generate
    """
    days: int = Field(default=30, ge=7, le=365, description="分析窗口天数")


class BusinessInsightReport(BaseModel):
    """
    三段式业务分析报告响应 Schema
    - summary：数据驱动的执行摘要（200-400 字左右的中文叙述）
    - insights：关键洞察列表，至少 3 条
    - suggestions：行动建议列表，至少 3 条
    """
    summary: str = Field(..., description="数据驱动的执行摘要")
    insights: List[str] = Field(default_factory=list, description="关键洞察列表")
    suggestions: List[str] = Field(default_factory=list, description="行动建议列表")


# ============= P3 扩展：RAG 带来源问答 Schema =============
# 仅追加在文件末尾，不修改上述任何已有类，保证与 P0/P1/P2 兼容


class SourceItem(BaseModel):
    """RAG 来源条目"""
    filename: str
    document_id: int
    score: float
    content: str


class ChatWithSourcesResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = []
