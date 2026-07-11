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

# P1 扩展：默认销售区域与产品分类字典
# 这里集中维护默认值，便于 init_db 与单元测试复用
DEFAULT_REGIONS: List[str] = ["华东", "华北", "华南", "西南", "西北"]
DEFAULT_CATEGORIES: List[str] = [
    "电子产品",
    "家居用品",
    "服装鞋帽",
    "美妆个护",
    "食品饮料",
]


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


def generate_mock_sales_data(
    db: Session,
    days: int = 90,
    regions: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
) -> int:
    """
    生成模拟销售数据（用于演示/测试）

    Args:
        db: 数据库会话
        days: 生成数据的天数
        regions: 销售区域可选列表；传 None 时不写入 region 字段（保持原有默认行为）
        categories: 产品分类可选列表；传 None 时不写入 product_category 字段

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

        # P1 扩展：当传入 regions/categories 时为每条记录随机抽样
        # 不传时维持 None，保留原有行为
        region_value = random.choice(regions) if regions else None
        category_value = random.choice(categories) if categories else None

        sale = Sale(
            date=current_date,
            revenue=round(revenue, 2),
            orders=orders,
            customers=customers,
            region=region_value,
            product_category=category_value,
        )
        db.add(sale)
        count += 1

    db.commit()
    return count


# ============= P1 扩展：Dashboard 拆分端点的三个纯函数 =============
# 下面三个函数不修改上述任何函数体，专供 /api/dashboard/summary/trend/category 调用


def get_summary(db: Session) -> dict:
    """
    获取 Dashboard 汇总数据
    复用已有的 get_total_stats，避免重复聚合逻辑

    Args:
        db: 数据库会话

    Returns:
        dict: { total_revenue, total_orders, total_customers }
    """
    total_revenue, total_orders, total_customers = get_total_stats(db)
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
    }


def get_trend(db: Session, days: int = 30) -> List[Sale]:
    """
    获取最近 N 天的销售趋势数据（含 region 字段）
    复用已有的 get_sales_trend，由于 Sale 模型已新增 region/product_category，
    ORM 对象天然包含这些字段，无需额外查询

    Args:
        db: 数据库会话
        days: 天数

    Returns:
        List[Sale]: 按日期升序的销售数据列表
    """
    return get_sales_trend(db, days=days)


def get_category_stats(db: Session) -> List[dict]:
    """
    按产品分类聚合销售数据
    使用 SQL group_by 直接在数据库层聚合，避免 Python 侧遍历

    Args:
        db: 数据库会话

    Returns:
        List[dict]: 每个分类一条记录，按 revenue 降序
        - 过滤掉 product_category 为 None 的记录
        - 若全部为 None，返回空列表
    """
    # 数据库层聚合：使用 SQLAlchemy 的 group_by + 聚合函数
    # 注意 func.sum 在 MySQL/SQLite 中对 NULL 返回 None，类型断言为 0
    rows = (
        db.query(
            Sale.product_category.label("category"),
            func.coalesce(func.sum(Sale.revenue), 0.0).label("revenue"),
            func.coalesce(func.sum(Sale.orders), 0).label("orders"),
            func.coalesce(func.sum(Sale.customers), 0).label("customers"),
        )
        .filter(Sale.product_category.isnot(None))
        .group_by(Sale.product_category)
        .order_by(func.sum(Sale.revenue).desc())
        .all()
    )

    result: List[dict] = []
    for row in rows:
        result.append(
            {
                "category": row.category,
                "revenue": float(row.revenue or 0.0),
                "orders": int(row.orders or 0),
                "customers": int(row.customers or 0),
            }
        )
    return result
