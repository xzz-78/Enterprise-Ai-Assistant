"""
Dashboard API 路由
处理数据看板相关接口
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User
from app.schemas import (
    DashboardResponse,
    DashboardSummaryResponse,
    SalesTrendItemV2,
    CategoryStatsResponse,
    CategoryStatItem,
)
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


# ============= P1 扩展：Dashboard 拆分端点 =============
# 以下三个路由为 /summary /trend /category，全部需要登录认证
# 已有 / 与 /generate-mock-data 端点行为完全保留


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="获取 Dashboard 汇总数据",
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取 Dashboard 汇总数据

    - 总销售额、总订单数、总客户数
    - 复用 dashboard_service.get_summary
    - 需要登录认证
    """
    return dashboard_service.get_summary(db)


@router.get(
    "/trend",
    response_model=List[SalesTrendItemV2],
    summary="获取销售趋势数据（按天）",
)
def get_dashboard_trend(
    days: int = Query(30, ge=1, le=365, description="趋势数据天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取最近 N 天的销售趋势数据

    - 复用 dashboard_service.get_trend
    - 返回字段同时包含 date 与 order_date，兼容新旧前端
    - region 可能为 null（历史数据）
    - 需要登录认证
    """
    # 直接调用 service 层方法，返回 List[dict]（含填充的零值日期）
    rows = dashboard_service.get_trend(db, days=days)
    # 将字典转为 SalesTrendItemV2（同时填充 date/order_date 两个字段）
    items: List[SalesTrendItemV2] = []
    for row in rows:
        items.append(
            SalesTrendItemV2(
                order_date=row["date"],
                date=row["date"],
                revenue=row["revenue"],
                orders=row["orders"],
                customers=row["customers"],
                region=row["region"],
            )
        )
    return items


@router.get(
    "/category",
    response_model=CategoryStatsResponse,
    summary="获取产品分类销售统计",
)
def get_dashboard_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取产品分类销售统计

    - 按 product_category 聚合
    - 按 revenue 降序
    - 忽略 product_category 为 NULL 的记录
    - 需要登录认证
    """
    rows = dashboard_service.get_category_stats(db)
    items = [CategoryStatItem(**row) for row in rows]
    return CategoryStatsResponse(total=len(items), items=items)
