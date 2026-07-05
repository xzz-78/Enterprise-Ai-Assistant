"""
Dashboard API 路由
处理数据看板相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User
from app.schemas import DashboardResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


@router.get("", response_model=DashboardResponse, summary="获取 Dashboard 数据")
def get_dashboard(
    days: int = Query(30, ge=7, le=365, description="趋势数据天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取 Dashboard 数据

    - 总销售额、总订单数、总客户数
    - 最近 N 天的销售趋势数据
    - 需要登录认证
    """
    data = dashboard_service.get_dashboard_data(db, days=days)
    return data


@router.post("/generate-mock-data", summary="生成模拟销售数据")
def generate_mock_data(
    days: int = Query(90, ge=30, le=365, description="生成数据的天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成模拟销售数据（用于演示）

    - 会清空现有销售数据
    - 生成带有趋势和波动的模拟数据
    - 包含周末效应
    """
    count = dashboard_service.generate_mock_sales_data(db, days=days)
    return {
        "message": f"成功生成 {count} 条模拟销售数据",
        "count": count
    }
