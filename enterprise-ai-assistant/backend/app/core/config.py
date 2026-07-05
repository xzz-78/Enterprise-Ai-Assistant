"""
应用配置模块
使用 pydantic-settings 管理环境变量配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类，从环境变量读取配置"""

    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/enterprise_ai"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production-please-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI API 配置
    OPENAI_API_KEY: str = "sk-your-openai-api-key"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"

    # FAISS 配置
    FAISS_INDEX_PATH: str = "./faiss_index"

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
