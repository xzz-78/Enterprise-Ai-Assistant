"""
数据库初始化脚本
运行此脚本创建数据库表并插入初始数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine, SessionLocal
from app.models import User, Document, Sale
from app.core.security import get_password_hash
# P1 扩展：导入默认的 region/category 列表，确保模拟数据覆盖分析维度
from app.services.dashboard_service import (
    generate_mock_sales_data,
    DEFAULT_REGIONS,
    DEFAULT_CATEGORIES,
)
from sqlalchemy import inspect, text


def migrate_sales_table():
    """
    自动迁移：检查 sales 表是否缺少 region / product_category 列，
    缺失时通过 ALTER TABLE 补列，保证旧表升级不报错。

    Base.metadata.create_all 只创建缺失的表，不会为已存在的表添加新列，
    因此存量部署需要此函数做在线 schema 升级。
    """
    inspector = inspect(engine)
    if "sales" not in inspector.get_table_names():
        return  # 表尚未创建，create_all 会负责建表

    existing_columns = {col["name"] for col in inspector.get_columns("sales")}

    migrations = [
        ("region", "VARCHAR(50) NULL COMMENT '销售区域'"),
        ("product_category", "VARCHAR(50) NULL COMMENT '产品分类'"),
    ]

    added = []
    with engine.connect() as conn:
        for col_name, col_def in migrations:
            if col_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE sales ADD COLUMN {col_name} {col_def}"))
                conn.commit()
                added.append(col_name)

    if added:
        print(f"   ✓ 自动迁移：已为 sales 表补充列 {', '.join(added)}")


def migrate_users_table():
    """
    自动迁移：检查 users 表是否缺少安全相关字段，
    缺失时通过 ALTER TABLE 补列。

    新增字段：
    - is_active: 用户状态（1-正常，0-禁用）
    - login_fail_count: 连续登录失败次数
    - locked_until: 账户锁定结束时间
    - last_login_attempt: 上次登录尝试时间
    """
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return  # 表尚未创建，create_all 会负责建表

    existing_columns = {col["name"] for col in inspector.get_columns("users")}

    migrations = [
        ("is_active", "INT DEFAULT 1 COMMENT '用户状态：1-正常，0-禁用'"),
        ("login_fail_count", "INT DEFAULT 0 COMMENT '连续登录失败次数'"),
        ("locked_until", "DATETIME NULL COMMENT '账户锁定结束时间'"),
        ("last_login_attempt", "DATETIME NULL COMMENT '上次登录尝试时间'"),
    ]

    added = []
    with engine.connect() as conn:
        for col_name, col_def in migrations:
            if col_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"))
                conn.commit()
                added.append(col_name)

    if added:
        print(f"   ✓ 自动迁移：已为 users 表补充列 {', '.join(added)}")


def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60)

    # 创建所有表
    print("\n1. 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ 数据库表创建成功")

    # 自动迁移：为旧表补充缺失列
    migrate_sales_table()
    migrate_users_table()

    # 创建默认管理员用户
    print("\n2. 创建默认管理员用户...")
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123")
            )
            db.add(admin_user)
            db.commit()
            print("   ✓ 默认管理员创建成功")
            print("     用户名: admin")
            print("     密码: admin123")
            print("     邮箱: admin@example.com")
        else:
            print("   - 管理员用户已存在，跳过")

        # 创建测试用户
        test_user = db.query(User).filter(User.username == "testuser").first()
        if not test_user:
            test = User(
                username="testuser",
                email="test@example.com",
                password_hash=get_password_hash("test123")
            )
            db.add(test)
            db.commit()
            print("   ✓ 测试用户创建成功")
            print("     用户名: testuser")
            print("     密码: test123")
        else:
            print("   - 测试用户已存在，跳过")

    except Exception as e:
        db.rollback()
        print(f"   ✗ 用户创建失败: {e}")
    finally:
        db.close()

    # 生成模拟销售数据
    print("\n3. 生成模拟销售数据...")
    db = SessionLocal()
    try:
        # 检查是否已有数据
        count = db.query(Sale).count()
        if count == 0:
            # P1 扩展：传入默认 region/category 列表，让模拟数据自带分析维度
            data_count = generate_mock_sales_data(
                db,
                days=90,
                regions=DEFAULT_REGIONS,
                categories=DEFAULT_CATEGORIES,
            )
            print(f"   ✓ 成功生成 {data_count} 条模拟销售数据（含 region/product_category）")
        else:
            print(f"   - 已有 {count} 条销售数据，跳过生成")
    except Exception as e:
        print(f"   ✗ 模拟数据生成失败: {e}")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("数据库初始化完成！")
    print("=" * 60)
    print("\n默认账号:")
    print("  管理员: admin / admin123")
    print("  测试用户: testuser / test123")
    print("\n启动服务:")
    print("  uvicorn app.main:app --reload")
    print("\nAPI文档:")
    print("  http://localhost:8000/docs")


if __name__ == "__main__":
    init_database()
