"""
文档管理 API 路由
处理文档上传、列表查询、删除等接口
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User
from app.schemas import DocumentResponse, DocumentListResponse
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["知识库"])


@router.post("/upload", response_model=DocumentResponse, summary="上传文档")
async def upload_document(
    file: UploadFile = File(..., description="要上传的文档文件（PDF/TXT）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传文档到知识库

    - 支持 PDF 和 TXT 格式
    - 文档会自动解析、切分并向量化存入 FAISS
    - 需要登录认证
    """
    document = document_service.upload_document(db, file, current_user)
    return document


@router.get("", response_model=DocumentListResponse, summary="获取文档列表")
def get_documents(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=500, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户上传的文档列表

    - 按上传时间倒序排列
    - 支持分页
    """
    documents, total = document_service.get_documents_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return {
        "total": total,
        "documents": documents
    }


@router.delete("/{doc_id}", summary="删除文档")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除指定文档

    - 只能删除自己上传的文档
    - 会同时删除文件和数据库记录
    """
    document_service.delete_document(db, doc_id, current_user.id)
    return {"message": "文档删除成功"}


@router.get("/{doc_id}", response_model=DocumentResponse, summary="获取文档详情")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定文档的详细信息
    """
    document = document_service.get_document_by_id(db, doc_id, current_user.id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    return document
