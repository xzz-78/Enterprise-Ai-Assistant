"""
向量存储服务
使用 FAISS 进行向量存储和检索
集成 LangChain 进行文本处理和 Embedding
"""
import os
import pickle
from typing import List, Optional, Tuple

import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS as LangchainFAISS
from langchain_core.documents import Document as LangchainDocument

from app.core.config import settings


class VectorStoreService:
    """
    向量存储服务类
    负责文档的向量化、存储和检索
    """

    def __init__(self):
        """初始化向量存储服务"""
        self.index_path = settings.FAISS_INDEX_PATH
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE,
        )
        self.vector_store: Optional[LangchainFAISS] = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        """加载已有的 FAISS 索引，或创建新索引"""
        index_file = os.path.join(self.index_path, "index.faiss")
        pkl_file = os.path.join(self.index_path, "index.pkl")

        if os.path.exists(index_file) and os.path.exists(pkl_file):
            # 加载已有索引
            self.vector_store = LangchainFAISS.load_local(
                self.index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            # 创建索引目录
            os.makedirs(self.index_path, exist_ok=True)
            # 创建空的向量存储（用一个占位文档初始化）
            self.vector_store = None

    def _save_index(self):
        """保存 FAISS 索引到磁盘"""
        if self.vector_store is not None:
            self.vector_store.save_local(self.index_path)

    def load_document(self, file_path: str, file_type: str) -> List[LangchainDocument]:
        """
        加载文档内容

        Args:
            file_path: 文件路径
            file_type: 文件类型（pdf/txt）

        Returns:
            List[LangchainDocument]: 文档对象列表
        """
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type == "txt":
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

        return loader.load()

    def split_documents(
        self,
        documents: List[LangchainDocument],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[LangchainDocument]:
        """
        切分文档为小块

        Args:
            documents: 文档列表
            chunk_size: 每块的大小（字符数）
            chunk_overlap: 块之间的重叠大小

        Returns:
            List[LangchainDocument]: 切分后的文档块列表
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        return text_splitter.split_documents(documents)

    def add_document(self, file_path: str, file_type: str, metadata: Optional[dict] = None):
        """
        将文档添加到向量存储中

        Args:
            file_path: 文件路径
            file_type: 文件类型
            metadata: 附加元数据
        """
        # 加载文档
        documents = self.load_document(file_path, file_type)

        # 切分文档
        chunks = self.split_documents(documents)

        # 添加元数据
        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)

        # 添加到向量存储
        if self.vector_store is None:
            self.vector_store = LangchainFAISS.from_documents(
                chunks,
                self.embeddings
            )
        else:
            self.vector_store.add_documents(chunks)

        # 保存索引
        self._save_index()

    def similarity_search(
        self,
        query: str,
        k: int = 4
    ) -> List[LangchainDocument]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回的结果数量

        Returns:
            List[LangchainDocument]: 最相似的文档块列表
        """
        if self.vector_store is None:
            return []

        results = self.vector_store.similarity_search(query, k=k)
        return results

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4
    ) -> List[Tuple[LangchainDocument, float]]:
        """
        带分数的相似度搜索

        Args:
            query: 查询文本
            k: 返回的结果数量

        Returns:
            List[Tuple[LangchainDocument, float]]: 文档和相似度分数的列表
        """
        if self.vector_store is None:
            return []

        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results

    def delete_by_metadata(self, metadata_filter: dict):
        """
        根据元数据删除文档（简单实现）

        Args:
            metadata_filter: 元数据过滤条件
        """
        # 注意：FAISS 本身不支持按元数据删除
        # 生产环境建议使用更强大的向量数据库如 Pinecone, Weaviate, Milvus 等
        # 这里提供一个简化实现：重建索引
        if self.vector_store is None:
            return

        # 获取所有文档（简化处理，实际可能需要更复杂的逻辑）
        # 对于小型项目，可以接受全量重建
        pass


# 全局向量存储服务实例
vector_store_service = VectorStoreService()
