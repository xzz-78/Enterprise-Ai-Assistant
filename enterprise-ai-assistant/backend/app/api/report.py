"""
AI 分析报告 API 路由
处理业务分析报告生成相关接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User
from app.schemas import ReportRequest, ReportResponse
from app.services.report_service import report_service

router = APIRouter(prefix="/report", tags=["AI分析报告"])


@router.post("", response_model=ReportResponse, summary="生成 AI 分析报告")
def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    根据销售数据自动生成 AI 业务分析报告

    - 数据摘要（总销售额、订单数、客户数、增长率等）
    - AI 智能分析（趋势分析、原因分析、关键发现）
    - 改进建议（销售策略、客户增长、运营优化等）
    - 可指定分析天数（7-365天，默认30天）
    """
    try:
        report = report_service.generate_report(db, days=request.days)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"报告生成失败: {str(e)}"
        )
