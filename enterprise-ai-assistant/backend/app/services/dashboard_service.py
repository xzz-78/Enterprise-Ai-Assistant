"""
Dashboard 服务
处理销售数据查询、统计计算等业务逻辑
"""
import random
from datetime import date, timedelta
from typing import List, Tuple, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Sale


def get_total_stats(db: Session) -> Tuple[float, int, int]:
    """
    获取总体统计数据

    Args:
        db: 数据库会话

    Returns:
        Tuple[float, int, int]: (总销售额, 总订单数, 总客户数)
    """
    result = db.query(
        func.sum(Sale.revenue).label("total_revenue"),
        func.sum(Sale.orders).label("total_orders"),
        func.sum(Sale.customers).label("total_customers")
    ).first()

    total_revenue = result.total_revenue or 0.0
    total_orders = result.total_orders or 0
    total_customers = result.total_customers or 0

    return total_revenue, total_orders, total_customers


def get_sales_trend(
    db: Session,
    days: int = 30
) -> List[Sale]:
    """
    获取最近 N 天的销售趋势数据

    Args:
        db: 数据库会话
        days: 天数

    Returns:
        List[Sale]: 按日期排序的销售数据列表
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    sales = db.query(Sale).filter(
        Sale.date >= start_date,
        Sale.date <= end_date
    ).order_by(Sale.date.asc()).all()

    return sales


def get_dashboard_data(db: Session, days: int = 30) -> dict:
    """
    获取 Dashboard 完整数据

    Args:
        db: 数据库会话
        days: 趋势数据天数

    Returns:
        dict: Dashboard 数据字典
    """
    # 获取总统计
    total_revenue, total_orders, total_customers = get_total_stats(db)

    # 获取趋势数据
    trend = get_sales_trend(db, days=days)

    return {
        "stats": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_customers": total_customers
        },
        "trend": trend
    }


def generate_mock_sales_data(db: Session, days: int = 90) -> int:
    """
    生成模拟销售数据（用于演示/测试）

    Args:
        db: 数据库会话
        days: 生成数据的天数

    Returns:
        int: 生成的记录数量
    """
    # 先清空现有数据
    db.query(Sale).delete()
    db.commit()

    today = date.today()
    count = 0

    # 设置随机种子以确保数据可重复
    random.seed(42)

    for i in range(days):
        current_date = today - timedelta(days=days - 1 - i)

        # 生成模拟数据，带有一定的趋势和波动
        base_revenue = 50000 + i * 200  # 缓慢上升趋势
        base_orders = 100 + int(i * 0.5)
        base_customers = 80 + int(i * 0.3)

        # 添加随机波动
        revenue = max(10000, base_revenue + random.gauss(0, 8000))
        orders = max(10, base_orders + int(random.gauss(0, 15)))
        customers = max(5, base_customers + int(random.gauss(0, 10)))

        # 周末效应：周末数据稍低
        if current_date.weekday() >= 5:  # 周六周日
            revenue *= 0.7
            orders = int(orders * 0.7)
            customers = int(customers * 0.7)

        sale = Sale(
            date=current_date,
            revenue=round(revenue, 2),
            orders=orders,
            customers=customers
        )
        db.add(sale)
        count += 1

    db.commit()
    return count
