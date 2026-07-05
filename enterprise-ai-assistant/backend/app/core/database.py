"""
数据库连接配置
使用 SQLAlchemy 2.0 进行数据库操作
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 自动检测连接是否有效
    pool_recycle=3600,   # 连接回收时间（秒）
    echo=False           # 是否打印SQL语句，生产环境建议关闭
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，所有模型都继承自这个基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    使用生成器模式确保会话正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
