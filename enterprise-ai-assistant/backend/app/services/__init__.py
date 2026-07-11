"""
服务层导出
"""
from app.services.auth_service import (
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    create_user,
    authenticate_user,
)
from app.services.document_service import (
    upload_document,
    get_documents_by_user,
    get_document_by_id,
    delete_document,
)
from app.services.dashboard_service import (
    get_total_stats,
    get_sales_trend,
    get_dashboard_data,
    generate_mock_sales_data,
    # P1 扩展：新增的三个纯函数
    get_summary,
    get_trend,
    get_category_stats,
)

__all__ = [
    "get_user_by_username",
    "get_user_by_email",
    "get_user_by_id",
    "create_user",
    "authenticate_user",
    "upload_document",
    "get_documents_by_user",
    "get_document_by_id",
    "delete_document",
    "get_total_stats",
    "get_sales_trend",
    "get_dashboard_data",
    "generate_mock_sales_data",
    # P1 扩展：导出新增的三个 dashboard 纯函数
    "get_summary",
    "get_trend",
    "get_category_stats",
]
