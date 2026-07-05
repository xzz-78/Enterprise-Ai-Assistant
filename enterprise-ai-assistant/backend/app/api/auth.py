"""
用户认证 API 路由
处理注册、登录、获取当前用户信息等接口
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
)
from app.schemas import UserCreate, UserResponse, Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户

    - **username**: 用户名（3-50字符，只能包含字母、数字和下划线）
    - **email**: 邮箱地址
    - **password**: 密码（6-100字符）
    """
    user = auth_service.create_user(db, user_in)
    return user


@router.post("/login", response_model=Token, summary="用户登录")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录获取 Token

    - **username**: 用户名
    - **password**: 密码

    返回 JWT Token，后续请求需在 Header 中携带:
    `Authorization: Bearer <token>`
    """
    # 验证用户
    user = auth_service.authenticate_user(
        db,
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建 Token
    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_me(current_user = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    需要在请求头中携带有效的 JWT Token
    """
    return current_user
