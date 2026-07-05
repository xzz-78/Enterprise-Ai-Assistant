"""
用户认证服务
处理用户注册、登录、用户信息查询等业务逻辑
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserCreate
from app.core.security import get_password_hash, verify_password


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名查询用户

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    根据邮箱查询用户

    Args:
        db: 数据库会话
        email: 邮箱地址

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据用户ID查询用户

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    创建新用户（注册）

    Args:
        db: 数据库会话
        user_in: 用户创建信息

    Returns:
        User: 创建的用户对象

    Raises:
        HTTPException: 用户名或邮箱已存在时抛出
    """
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )

    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    验证用户凭据

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        Optional[User]: 验证成功返回用户对象，失败返回 None
    """
    user = get_user_by_username(db, username=username)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
