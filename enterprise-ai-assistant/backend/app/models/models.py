"""
数据库模型定义
包含所有数据库表的 ORM 模型
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """用户表模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系：用户上传的文档
    documents = relationship("Document", back_populates="uploader", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Document(Base):
    """文档表模型"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, comment="文档ID")
    filename = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(Integer, comment="文件大小（字节）")
    file_type = Column(String(20), comment="文件类型（pdf/txt）")
    upload_time = Column(DateTime, default=datetime.utcnow, comment="上传时间")
    user_id = Column(Integer, ForeignKey("users.id"), comment="上传用户ID")

    # 关系：上传者
    uploader = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"


class Sale(Base):
    """销售数据表模型"""

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    date = Column(Date, nullable=False, index=True, comment="销售日期")
    revenue = Column(Float, nullable=False, default=0.0, comment="销售额")
    orders = Column(Integer, nullable=False, default=0, comment="订单数")
    customers = Column(Integer, nullable=False, default=0, comment="客户数")

    def __repr__(self):
        return f"<Sale(id={self.id}, date={self.date}, revenue={self.revenue})>"
