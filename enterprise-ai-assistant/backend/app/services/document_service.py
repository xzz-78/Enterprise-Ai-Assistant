"""
文档服务
处理文档上传、解析、列表查询等业务逻辑
"""
import os
import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.models import Document, User
from app.schemas import DocumentCreate, DocumentResponse
from app.core.config import settings
from app.services.vector_service import vector_store_service


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名（小写）

    Args:
        filename: 文件名

    Returns:
        str: 文件扩展名（不含点号）
    """
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def allowed_file(filename: str) -> bool:
    """
    检查文件类型是否允许上传

    Args:
        filename: 文件名

    Returns:
        bool: 是否允许上传
    """
    allowed_extensions = {
        "pdf", "txt", "md", "markdown",
        "docx", "doc", "pptx", "ppt", "xlsx", "xls", "csv",
        "html", "htm", "epub", "rtf", "odt",
    }
    return get_file_extension(filename) in allowed_extensions


def save_upload_file(upload_file: UploadFile) -> Tuple[str, int, str]:
    """
    保存上传的文件到磁盘

    Args:
        upload_file: 上传的文件对象

    Returns:
        Tuple[str, int, str]: (文件保存路径, 文件大小, 文件类型)

    Raises:
        HTTPException: 文件类型不支持或保存失败时抛出
    """
    filename = upload_file.filename or "unnamed"

    # 检查文件类型
    if not allowed_file(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型，仅支持 PDF 和 TXT 格式"
        )

    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 生成唯一文件名（避免文件名冲突）
    file_ext = get_file_extension(filename)
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # 保存文件
    file_size = 0
    try:
        with open(file_path, "wb") as f:
            while True:
                chunk = upload_file.file.read(8192)
                if not chunk:
                    break
                file_size += len(chunk)

                # 检查文件大小限制
                if file_size > settings.MAX_UPLOAD_SIZE:
                    f.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"文件大小超过限制，最大允许 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
                    )

                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        # 清理可能的部分文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )

    return file_path, file_size, file_ext


def create_document_record(
    db: Session,
    filename: str,
    file_path: str,
    file_size: int,
    file_type: str,
    user_id: int
) -> Document:
    """
    创建文档数据库记录

    Args:
        db: 数据库会话
        filename: 原始文件名
        file_path: 文件存储路径
        file_size: 文件大小
        file_type: 文件类型
        user_id: 上传用户ID

    Returns:
        Document: 创建的文档对象
    """
    doc_in = DocumentCreate(
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        user_id=user_id
    )

    db_doc = Document(**doc_in.model_dump())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    return db_doc


def upload_document(db: Session, file: UploadFile, current_user: User) -> Document:
    """
    上传文档并处理

    Args:
        db: 数据库会话
        file: 上传的文件
        current_user: 当前用户

    Returns:
        Document: 文档对象
    """
    filename = file.filename or "unnamed"

    # 保存文件
    file_path, file_size, file_type = save_upload_file(file)

    try:
        # 创建数据库记录
        document = create_document_record(
            db=db,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            user_id=current_user.id
        )

        # 向量化并存入 FAISS
        vector_store_service.add_document(
            file_path=file_path,
            file_type=file_type,
            metadata={"document_id": document.id, "filename": filename}
        )

        return document

    except Exception as e:
        # 如果向量化失败，清理已保存的文件和数据库记录
        if os.path.exists(file_path):
            os.remove(file_path)
        # 数据库记录可能还未创建或需要回滚
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档处理失败: {str(e)}"
        )


def get_documents_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Document], int]:
    """
    获取用户的文档列表

    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过数量（分页）
        limit: 返回数量限制

    Returns:
        Tuple[List[Document], int]: (文档列表, 总数)
    """
    query = db.query(Document).filter(Document.user_id == user_id)

    total = query.count()
    documents = query.order_by(Document.upload_time.desc()).offset(skip).limit(limit).all()

    return documents, total


def get_document_by_id(db: Session, doc_id: int, user_id: Optional[int] = None) -> Optional[Document]:
    """
    根据ID获取文档

    Args:
        db: 数据库会话
        doc_id: 文档ID
        user_id: 用户ID（用于权限验证，None 表示不验证）

    Returns:
        Optional[Document]: 文档对象
    """
    query = db.query(Document).filter(Document.id == doc_id)

    if user_id is not None:
        query = query.filter(Document.user_id == user_id)

    return query.first()


def delete_document(db: Session, doc_id: int, user_id: int) -> bool:
    """
    删除文档

    Args:
        db: 数据库会话
        doc_id: 文档ID
        user_id: 用户ID

    Returns:
        bool: 是否删除成功

    Raises:
        HTTPException: 文档不存在时抛出
    """
    document = get_document_by_id(db, doc_id, user_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    file_path = document.file_path

    # 删除数据库记录
    db.delete(document)
    db.commit()

    # 从向量存储中删除
    try:
        vector_store_service.delete_by_metadata({"document_id": document.id})
    except Exception:
        pass

    # 删除磁盘文件
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    return True
