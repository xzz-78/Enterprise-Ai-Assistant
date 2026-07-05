"""
通用工具函数
"""
import os
import re
from datetime import datetime, date
from typing import Optional, Any


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读格式

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        str: 格式化的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_datetime(dt: Optional[datetime]) -> str:
    """
    格式化日期时间为字符串

    Args:
        dt: 日期时间对象

    Returns:
        str: 格式化的日期时间字符串
    """
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(d: Optional[date]) -> str:
    """
    格式化日期为字符串

    Args:
        d: 日期对象

    Returns:
        str: 格式化的日期字符串
    """
    if not d:
        return ""
    return d.strftime("%Y-%m-%d")


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式是否有效

    Args:
        email: 邮箱地址

    Returns:
        bool: 是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def ensure_dir(dir_path: str) -> None:
    """
    确保目录存在，不存在则创建

    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def safe_filename(filename: str) -> str:
    """
    生成安全的文件名，移除危险字符

    Args:
        filename: 原始文件名

    Returns:
        str: 安全的文件名
    """
    # 移除路径分隔符和其他危险字符
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    # 去除首尾空格和点
    filename = filename.strip().strip('.')
    return filename or 'unnamed'
