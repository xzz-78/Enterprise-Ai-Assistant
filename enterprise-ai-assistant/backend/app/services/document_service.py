"""
文档服务
处理文档上传、解析、列表查询等业务逻辑
"""
import os
import uuid
import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.models import Document, User
from app.schemas import DocumentCreate, DocumentResponse
from app.core.config import settings
from app.services.vector_service import vector_store_service

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    "pdf", "txt", "md", "markdown",
    "docx", "doc", "pptx", "ppt", "xlsx", "xls", "csv",
    "html", "htm", "epub", "rtf", "odt",
}

ALLOWED_EXTENSIONS_DISPLAY = "PDF、TXT、Markdown、Word、Excel、PPT、CSV、HTML、EPUB、RTF、ODT"

MAGIC_NUMBERS = {
    b"%PDF-": "pdf",
    b"\x50\x4B\x03\x04": "zip",
    b"\x50\x4B\x05\x06": "zip",
    b"\x50\x4B\x07\x08": "zip",
    b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1": "ole",
    b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
    b"\xFF\xD8\xFF": "jpg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"\x25\x21\x50\x53": "ps",
    b"\x1B\x45": "esc",
}

ZIP_BASED_FORMATS = {
    "docx": ["[Content_Types].xml", "word/document.xml"],
    "xlsx": ["[Content_Types].xml", "xl/workbook.xml"],
    "pptx": ["[Content_Types].xml", "ppt/presentation.xml"],
    "odt": ["mimetype"],
    "epub": ["mimetype"],
}


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名（小写）

    Args:
        filename: 文件名

    Returns:
        str: 文件扩展名（不含点号）
    """
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def detect_file_type_by_magic(file_path: str, filename_ext: str = "") -> Optional[str]:
    """
    通过文件魔数（Magic Number）检测文件真实类型

    Args:
        file_path: 文件路径
        filename_ext: 文件名扩展名，用于辅助判断 zip 格式的文件

    Returns:
        Optional[str]: 检测到的文件类型，无法检测时返回 None
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(512)

        if not header:
            return None

        detected = None
        for magic, ftype in MAGIC_NUMBERS.items():
            if header.startswith(magic):
                detected = ftype
                break

        if detected in ("zip", "ole"):
            if detected == "zip":
                return _detect_zip_format(file_path, filename_ext)
            else:
                return _detect_ole_format(filename_ext)

        if detected == "pdf":
            return "pdf"

        if not detected:
            if _is_text_file(header):
                return "txt"

        return detected

    except Exception as e:
        logger.warning(f"文件魔数检测失败: {str(e)}")
        return None


def _is_text_file(header: bytes) -> bool:
    """
    简单判断是否为文本文件
    """
    try:
        header.decode("utf-8")
        return True
    except UnicodeDecodeError:
        pass

    try:
        header.decode("gbk")
        return True
    except UnicodeDecodeError:
        pass

    try:
        header.decode("latin-1")
        text_chars = sum(1 for b in header if 32 <= b < 127 or b in (9, 10, 13))
        return text_chars / len(header) > 0.85 if header else False
    except Exception:
        return False


def _detect_zip_format(file_path: str, filename_ext: str) -> Optional[str]:
    """
    检测 ZIP 格式文件的具体类型（docx/xlsx/pptx/odt/epub 等）
    """
    import zipfile

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            namelist = zf.namelist()

            ext_lower = filename_ext.lower()
            if ext_lower in ZIP_BASED_FORMATS:
                markers = ZIP_BASED_FORMATS[ext_lower]
                if all(any(n.startswith(m) for n in namelist) for m in markers):
                    return ext_lower

            for fmt, markers in ZIP_BASED_FORMATS.items():
                if all(any(n.startswith(m) for n in namelist) for m in markers):
                    return fmt

        return "zip"
    except Exception:
        return "zip"


def _detect_ole_format(filename_ext: str) -> Optional[str]:
    """
    检测 OLE 格式文件的具体类型（doc/xls/ppt 等旧版 Office 文件）
    """
    ext_lower = filename_ext.lower()
    ole_extensions = {"doc", "xls", "ppt", "rtf"}
    if ext_lower in ole_extensions:
        return ext_lower
    return "ole"


def allowed_file(filename: str, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    检查文件类型是否允许上传
    优先使用文件魔数检测，魔数检测失败时回退到扩展名检查

    Args:
        filename: 文件名
        file_path: 文件路径（如果已保存到磁盘）

    Returns:
        Tuple[bool, str]: (是否允许上传, 检测到的文件类型或空字符串)
    """
    ext = get_file_extension(filename)

    if ext not in ALLOWED_EXTENSIONS:
        return False, ext

    if file_path and os.path.exists(file_path):
        detected_type = detect_file_type_by_magic(file_path, ext)
        if detected_type and detected_type not in ALLOWED_EXTENSIONS and detected_type not in ("zip", "ole", "txt"):
            logger.warning(f"文件扩展名 {ext} 与实际类型 {detected_type} 不匹配")
            return False, detected_type

    return True, ext


def safe_remove_file(file_path: str) -> bool:
    """
    安全删除文件，捕获所有异常并记录日志

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否删除成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return True
    except OSError as e:
        logger.warning(f"删除文件失败 {file_path}: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"删除文件时发生未知错误 {file_path}: {str(e)}")
        return False


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

    # 预检查文件扩展名
    is_allowed, detected_type = allowed_file(filename)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型 {detected_type}，支持的格式：{ALLOWED_EXTENSIONS_DISPLAY}"
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
                    safe_remove_file(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"文件大小超过限制，最大允许 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
                    )

                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件保存失败: {str(e)}")
        safe_remove_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )

    # 保存完成后，通过魔数再次验证文件类型
    is_allowed, verified_type = allowed_file(filename, file_path)
    if not is_allowed:
        safe_remove_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件实际类型 {verified_type} 与扩展名不符，不支持的文件类型。支持的格式：{ALLOWED_EXTENSIONS_DISPLAY}"
        )

    return file_path, file_size, file_ext


def create_document_record(
    db: Session,
    filename: str,
    file_path: str,
    file_size: int,
    file_type: str,
    user_id: int,
    auto_commit: bool = True
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
        auto_commit: 是否自动提交事务，默认 True

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

    if auto_commit:
        db.commit()
        db.refresh(db_doc)
    else:
        db.flush()

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
    file_path = ""
    document = None

    try:
        # 保存文件
        file_path, file_size, file_type = save_upload_file(file)

        # 创建数据库记录（先不提交，等向量化成功后再提交）
        document = create_document_record(
            db=db,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            user_id=current_user.id,
            auto_commit=False
        )

        # 向量化并存入 FAISS
        vector_store_service.add_document(
            file_path=file_path,
            file_type=file_type,
            metadata={"document_id": document.id, "filename": filename}
        )

        # 所有步骤成功，提交事务
        db.commit()
        db.refresh(document)

        return document

    except HTTPException:
        db.rollback()
        if file_path:
            safe_remove_file(file_path)
        raise
    except Exception as e:
        logger.error(f"文档处理失败: {str(e)}")
        db.rollback()
        if file_path:
            safe_remove_file(file_path)
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
    doc_id_value = document.id
    doc_filename = document.filename

    # 删除数据库记录
    db.delete(document)
    db.commit()

    delete_warnings = []

    # 从向量存储中删除
    try:
        vector_store_service.delete_by_metadata({"document_id": doc_id_value})
    except Exception as e:
        error_msg = f"从向量存储删除文档失败 (id={doc_id_value}, filename={doc_filename}): {str(e)}"
        logger.error(error_msg)
        delete_warnings.append("向量索引删除失败")

    # 删除磁盘文件
    if not safe_remove_file(file_path):
        error_msg = f"删除磁盘文件失败 (id={doc_id_value}, path={file_path})"
        logger.error(error_msg)
        delete_warnings.append("磁盘文件删除失败")

    if delete_warnings:
        logger.warning(
            f"文档删除存在部分失败 (id={doc_id_value}, filename={doc_filename}): {', '.join(delete_warnings)}，"
            f"数据库记录已删除，建议进行数据一致性检查"
        )

    return True
