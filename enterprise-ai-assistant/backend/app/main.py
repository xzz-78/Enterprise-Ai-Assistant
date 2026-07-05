"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.dashboard import router as dashboard_router
from app.api.report import router as report_router

# 创建 FastAPI 应用
app = FastAPI(
    title="Enterprise AI Assistant API",
    description="企业级AI知识问答与数据分析平台 - API文档",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS 中间件
# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 根路径
@app.get("/", tags=["根路径"], summary="API 根路径")
def root():
    """API 根路径，返回欢迎信息"""
    return {
        "message": "Welcome to Enterprise AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 健康检查
@app.get("/health", tags=["健康检查"], summary="健康检查")
def health_check():
    """健康检查接口，用于监控服务状态"""
    return {"status": "healthy"}


# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(report_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
