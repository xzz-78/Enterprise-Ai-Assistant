"""
AI 问答 API 路由
处理知识库问答相关接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User
from app.schemas import ChatRequest, ChatResponse, ChatWithSourcesResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["AI问答"])


@router.post("", response_model=ChatResponse, summary="AI 问答")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    基于知识库的 AI 智能问答

    - 系统会自动从知识库中检索相关内容
    - 使用 RAG（检索增强生成）技术生成回答
    - 如果知识库中没有相关内容，会使用通用知识回答
    """
    try:
        answer = chat_service.chat(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 回答生成失败: {str(e)}"
        )


@router.post("/with-sources", response_model=ChatWithSourcesResponse, summary="AI 问答（带来源）")
def chat_with_sources(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    AI 问答，返回答案和参考来源

    - 返回生成的答案
    - 同时返回检索到的相关文档片段作为参考来源
    - sources 结构：[{filename, document_id, score, content}]
    """
    try:
        result = chat_service.chat_with_sources(request.question)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 回答生成失败: {str(e)}"
        )
