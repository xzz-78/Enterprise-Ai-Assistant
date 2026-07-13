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


@router.post("", response_model=ReportResponse, summary="生成 AI 分析报告（已废弃）", deprecated=True)
def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    [已废弃] 请使用 POST /api/report/generate 代替

    旧版报告生成接口，返回 {data_summary, ai_analysis, recommendations} 结构。
    新版接口 POST /generate 返回 {summary, insights, suggestions} 三段式结构化报告，
    采用"SQL 聚合 → Prompt → LLM"工程化流水线，输出更稳定。
    """
    try:
        report = report_service.generate_report(db, days=request.days)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"报告生成失败: {str(e)}"
        )


# ============= P2 扩展：AI 业务分析师端点 =============
# 新增 POST /generate，固定走"SQL 聚合 → 数据汇总 → Prompt → LLM"流水线
# 与上面的 POST / 端点完全独立：原端点保留为兼容接口，本端点返回三段式结构化报告
# P2 新增的 Request/Response 模型在函数内延迟 import，避免与 P0 旧 schema 在模块加载阶段互相干扰


@router.post(
    "/generate",
    response_model=None,  # 实际响应模型通过函数返回注解声明
    summary="生成 AI 业务分析报告（三段式）",
)
def generate_business_report(
    request: "ReportGenerateRequest",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    AI 业务分析师端点（P2 阶段新增）

    流程：SQL 聚合 → 数据汇总 → Prompt → LLM
    返回三段式结构：summary / insights / suggestions

    - summary：200-400 字的中文执行摘要
    - insights：至少 3 条关键洞察
    - suggestions：至少 3 条行动建议
    - 销售表为空时直接返回 summary="暂无销售数据可供分析。"
    - 内部异常已做兜底，不会抛 500
    """
    # 函数内 import：避免 P0 旧版与 P2 新版 schemas 在模块加载阶段互相干扰
    from app.schemas import BusinessInsightReport, ReportGenerateRequest  # noqa: WPS433
    from app.services.report_service import business_report_service  # noqa: WPS433

    # 显式将 P2 新请求体标准化
    if not isinstance(request, ReportGenerateRequest):
        request = ReportGenerateRequest(days=request.days)

    result = business_report_service.generate(db, days=request.days)
    # 用 Pydantic 模型序列化，保证响应字段顺序与文档一致
    return BusinessInsightReport(**result)
