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


def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60)

    # 创建所有表
    print("\n1. 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ 数据库表创建成功")

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
