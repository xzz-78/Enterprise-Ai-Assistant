"""
Pydantic Schema 定义
用于 API 请求和响应的数据验证与序列化
"""
from datetime import datetime, date
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
    date: date
    revenue: float
    orders: int
    customers: int


class DashboardResponse(BaseModel):
    """Dashboard 响应 Schema"""
    stats: DashboardStats
    trend: List[SalesTrendItem]


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
