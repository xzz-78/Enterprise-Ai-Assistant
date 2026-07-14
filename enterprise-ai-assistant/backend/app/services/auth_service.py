"""
用户认证服务
处理用户注册、登录、用户信息查询等业务逻辑

安全特性：
1. 用户名/邮箱查询时小写化，保证大小写不敏感
2. 登录失败次数限制，防止暴力破解
3. 用户注册使用数据库唯一约束保证原子性
4. 数据库操作异常处理
5. 用户状态检查（禁用用户无法登录）
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserCreate
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

# 登录失败限制配置
MAX_LOGIN_FAILS = 5  # 最大连续失败次数
LOCK_DURATION_MINUTES = 15  # 锁定时长（分钟）


def get_user_by_username(db: Session, username: str, case_insensitive: bool = True) -> Optional[User]:
    """
    根据用户名查询用户

    Args:
        db: 数据库会话
        username: 用户名
        case_insensitive: 是否大小写不敏感（默认 True）

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    if case_insensitive:
        return db.query(User).filter(
            func.lower(User.username) == username.lower()
        ).first()
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str, case_insensitive: bool = True) -> Optional[User]:
    """
    根据邮箱查询用户

    Args:
        db: 数据库会话
        email: 邮箱地址
        case_insensitive: 是否大小写不敏感（默认 True）

    Returns:
        Optional[User]: 用户对象，不存在则返回 None
    """
    if case_insensitive:
        return db.query(User).filter(
            func.lower(User.email) == email.lower()
        ).first()
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

    使用数据库唯一约束保证原子性，避免并发注册导致的重复用户问题。
    用户名和邮箱存储时保持原始大小写（用于展示），但数据库约束保证唯一性。

    Args:
        db: 数据库会话
        user_in: 用户创建信息

    Returns:
        User: 创建的用户对象

    Raises:
        HTTPException: 用户名或邮箱已存在时抛出
        HTTPException: 数据库操作失败时抛出
    """
    # 创建用户（保持原始大小写用于展示）
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password)
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
        logger.info(f"用户注册成功: {user.username}")
        return user
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e).lower()
        if "username" in error_msg or user_in.username.lower() in error_msg:
            logger.warning(f"注册失败，用户名已存在: {user_in.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被注册"
            )
        elif "email" in error_msg or user_in.email.lower() in error_msg:
            logger.warning(f"注册失败，邮箱已存在: {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        else:
            logger.error(f"注册失败，数据库约束错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或邮箱已被注册"
            )
    except Exception as e:
        db.rollback()
        logger.error(f"注册失败，数据库异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


def _check_user_locked(user: User) -> bool:
    """
    检查用户账户是否被锁定

    Args:
        user: 用户对象

    Returns:
        bool: True 表示账户被锁定
    """
    if user.locked_until and user.locked_until > datetime.utcnow():
        return True
    return False


def _record_login_failure(db: Session, user: User) -> None:
    """
    记录登录失败，超过限制则锁定账户

    Args:
        db: 数据库会话
        user: 用户对象
    """
    user.login_fail_count = (user.login_fail_count or 0) + 1
    user.last_login_attempt = datetime.utcnow()

    if user.login_fail_count >= MAX_LOGIN_FAILS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_DURATION_MINUTES)
        logger.warning(f"用户 {user.username} 登录失败次数达到 {user.login_fail_count}，锁定 {LOCK_DURATION_MINUTES} 分钟")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"记录登录失败状态时数据库异常: {e}")


def _clear_login_failures(db: Session, user: User) -> None:
    """
    清除登录失败计数

    Args:
        db: 数据库会话
        user: 用户对象
    """
    user.login_fail_count = 0
    user.locked_until = None
    user.last_login_attempt = datetime.utcnow()

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"清除登录失败状态时数据库异常: {e}")


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    验证用户凭据

    包含以下安全检查：
    1. 大小写不敏感的用户名查询
    2. 账户锁定状态检查
    3. 用户状态检查（是否被禁用）
    4. 登录失败次数限制
    5. 成功登录后清除失败计数

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        Optional[User]: 验证成功返回用户对象，失败返回 None

    Raises:
        HTTPException: 账户被锁定或禁用时抛出
    """
    # 大小写不敏感查询
    user = get_user_by_username(db, username=username)

    if not user:
        # 用户不存在也记录尝试（防止用户名枚举，但这里简化处理）
        return None

    # 检查账户是否被锁定
    if _check_user_locked(user):
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60 + 1
        logger.warning(f"用户 {username} 账户已锁定，剩余 {remaining} 分钟")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"账户已锁定，请 {remaining} 分钟后重试"
        )

    # 检查用户状态
    if not user.is_active:
        logger.warning(f"用户 {username} 已被禁用")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员"
        )

    # 验证密码
    if not verify_password(password, user.password_hash):
        _record_login_failure(db, user)
        return None

    # 登录成功，清除失败计数
    _clear_login_failures(db, user)

    return user
