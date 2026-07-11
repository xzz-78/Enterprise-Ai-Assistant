"""
向量存储服务
使用 FAISS 进行向量存储和检索
集成 LangChain 进行文本处理和 Embedding
"""
import os
import shutil
import tempfile
import hashlib
import pickle
from typing import List, Optional, Tuple, Dict

import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS as LangchainFAISS
from langchain_core.documents import Document as LangchainDocument

from app.core.config import settings

try:
    from langchain_community.document_loaders import UnstructuredFileLoader
    HAS_UNSTRUCTURED = True
except ImportError:
    HAS_UNSTRUCTURED = False


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
            self.vector_store = LangchainFAISS.load_local(
                self.index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            os.makedirs(self.index_path, exist_ok=True)
            self.vector_store = None

    def _save_index(self):
        """保存 FAISS 索引到磁盘"""
        if self.vector_store is not None:
            self.vector_store.save_local(self.index_path)

    def _atomic_save_index(self, new_vector_store: LangchainFAISS):
        """
        原子性保存索引：先写入临时目录，成功后替换正式目录

        Args:
            new_vector_store: 新的向量存储实例
        """
        tmp_dir = tempfile.mkdtemp(dir=os.path.dirname(self.index_path.rstrip("/")))
        try:
            new_vector_store.save_local(tmp_dir)

            bak_dir = self.index_path + ".bak"
            if os.path.exists(self.index_path):
                if os.path.exists(bak_dir):
                    shutil.rmtree(bak_dir)
                shutil.move(self.index_path, bak_dir)

            shutil.move(tmp_dir, self.index_path)

            if os.path.exists(bak_dir):
                shutil.rmtree(bak_dir)
        except Exception:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
            if os.path.exists(bak_dir) and not os.path.exists(self.index_path):
                shutil.move(bak_dir, self.index_path)
            raise

    def _compute_file_hash(self, file_path: str) -> str:
        """
        计算文件 SHA256 哈希，用于去重

        Args:
            file_path: 文件路径

        Returns:
            str: 文件哈希值
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    def load_document(self, file_path: str, file_type: str) -> List[LangchainDocument]:
        """
        加载文档内容

        优先使用 Unstructured 统一解析器（支持 pdf/docx/pptx/xlsx/html/md/epub 等），
        不可用时回退到 PyPDFLoader / TextLoader。

        Args:
            file_path: 文件路径
            file_type: 文件类型扩展名（不含点号）

        Returns:
            List[LangchainDocument]: 文档对象列表
        """
        if HAS_UNSTRUCTURED:
            try:
                loader = UnstructuredFileLoader(
                    file_path,
                    mode="elements",
                    strategy="fast",
                )
                docs = loader.load()
                if docs:
                    return docs
            except Exception:
                pass

        ext = file_type.lower()
        if ext == "pdf":
            loader = PyPDFLoader(file_path)
        elif ext in ("txt", "md", "markdown"):
            loader = TextLoader(file_path, encoding="utf-8")
        elif ext in ("html", "htm"):
            try:
                from langchain_community.document_loaders import BSHTMLLoader
                loader = BSHTMLLoader(file_path)
            except ImportError:
                loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

        return loader.load()

    def split_documents(
        self,
        documents: List[LangchainDocument],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_semantic: bool = False,
    ) -> List[LangchainDocument]:
        """
        切分文档为小块

        中文友好的分隔符优先级：段落 > 换行 > 句号/感叹号/问号/分号 > 逗号 > 空格 > 字符。
        当文档包含表格或代码块时，可启用 semantic 模式（SemanticChunker）按语义切块。

        Args:
            documents: 文档列表
            chunk_size: 每块的大小（字符数）
            chunk_overlap: 块之间的重叠大小
            use_semantic: 是否使用语义切分（适合表格、代码等结构化内容）

        Returns:
            List[LangchainDocument]: 切分后的文档块列表
        """
        if use_semantic:
            try:
                from langchain_experimental.text_splitter import SemanticChunker
                semantic_splitter = SemanticChunker(
                    self.embeddings,
                    breakpoint_threshold_type="percentile",
                    breakpoint_threshold_amount=75,
                )
                return semantic_splitter.split_documents(documents)
            except ImportError:
                pass

        chinese_separators = [
            "\n\n",
            "\n",
            "。", "！", "？", "；",
            "，",
            " ",
            "",
        ]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=chinese_separators,
        )

        return text_splitter.split_documents(documents)

    def _detect_structured_content(self, documents: List[LangchainDocument]) -> bool:
        """
        检测文档是否包含表格或代码等结构化内容

        Args:
            documents: 文档列表

        Returns:
            bool: 是否包含结构化内容
        """
        code_markers = ["```", "def ", "class ", "import ", "function", "<html", "<table"]
        for doc in documents:
            content = doc.page_content.lower()
            if doc.metadata.get("category") in ("Table", "CodeSnippet"):
                return True
            for marker in code_markers:
                if marker.lower() in content:
                    return True
            lines = content.split("\n")
            table_like = sum(1 for line in lines if "|" in line and line.count("|") >= 2)
            if table_like >= 3:
                return True
        return False

    def _get_all_docs(self) -> List[LangchainDocument]:
        """
        从当前 vector_store 获取所有文档

        Returns:
            List[LangchainDocument]: 所有文档
        """
        if self.vector_store is None:
            return []

        docs = []
        if hasattr(self.vector_store, "docstore") and self.vector_store.docstore is not None:
            docstore = self.vector_store.docstore
            if hasattr(docstore, "_dict"):
                for doc in docstore._dict.values():
                    docs.append(doc)
            elif hasattr(docstore, "docs"):
                for doc_id in docstore.docs:
                    docs.append(docstore.docs[doc_id])

        if not docs and hasattr(self.vector_store, "index_to_docstore_id"):
            id_map = self.vector_store.index_to_docstore_id
            docstore = self.vector_store.docstore
            if docstore is not None:
                for idx in id_map:
                    try:
                        doc = docstore.search(id_map[idx])
                        if doc:
                            docs.append(doc)
                    except Exception:
                        pass

        return docs

    def add_document(
        self,
        file_path: str,
        file_type: str,
        metadata: Optional[dict] = None,
    ):
        """
        将文档添加到向量存储中

        特性：
        - 重复检测：通过 metadata['document_id'] 识别同一文档，已存在则先删除再添加（更新语义）
        - 文件级去重：通过文件哈希检测完全相同的文件
        - 事务一致性：原子性保存索引，add 与 save 中间崩溃不会损坏索引

        Args:
            file_path: 文件路径
            file_type: 文件类型
            metadata: 附加元数据
        """
        metadata = metadata or {}

        documents = self.load_document(file_path, file_type)

        use_semantic = self._detect_structured_content(documents)
        chunks = self.split_documents(documents, use_semantic=use_semantic)

        file_hash = self._compute_file_hash(file_path)
        for chunk in chunks:
            chunk.metadata.update(metadata)
            chunk.metadata["file_hash"] = file_hash
            chunk.metadata["file_type"] = file_type

        document_id = metadata.get("document_id")

        existing_docs = self._get_all_docs()

        filtered_docs = []
        if document_id is not None:
            for doc in existing_docs:
                if str(doc.metadata.get("document_id")) != str(document_id):
                    filtered_docs.append(doc)
        else:
            filtered_docs = list(existing_docs)

        if document_id is None:
            for doc in filtered_docs:
                if doc.metadata.get("file_hash") == file_hash:
                    return

        all_chunks = filtered_docs + chunks

        if all_chunks:
            new_vector_store = LangchainFAISS.from_documents(
                all_chunks,
                self.embeddings,
            )
            self._atomic_save_index(new_vector_store)
            self.vector_store = new_vector_store
        else:
            self.vector_store = None
            if os.path.exists(self.index_path):
                shutil.rmtree(self.index_path)
                os.makedirs(self.index_path, exist_ok=True)

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
        根据元数据删除文档

        实现策略：FAISS 本身不支持按元数据删除，因此采用全量重建索引的方式。
        从 docstore 中读取所有文档，过滤掉匹配 metadata_filter 的文档，
        然后用剩余文档重建索引并原子性保存。

        Args:
            metadata_filter: 元数据过滤条件（键值对全部匹配才删除）
        """
        if self.vector_store is None:
            return

        all_docs = self._get_all_docs()
        if not all_docs:
            return

        def _matches(doc: LangchainDocument) -> bool:
            meta = doc.metadata or {}
            for key, value in metadata_filter.items():
                if str(meta.get(key)) != str(value):
                    return False
            return True

        remaining_docs = [doc for doc in all_docs if not _matches(doc)]

        if len(remaining_docs) == len(all_docs):
            return

        if remaining_docs:
            new_vector_store = LangchainFAISS.from_documents(
                remaining_docs,
                self.embeddings,
            )
            self._atomic_save_index(new_vector_store)
            self.vector_store = new_vector_store
        else:
            self.vector_store = None
            if os.path.exists(self.index_path):
                shutil.rmtree(self.index_path)
                os.makedirs(self.index_path, exist_ok=True)

    def search_with_sources(self, query: str, k: int = 4) -> List[Dict]:
        """
        带元数据与归一化分数的相似度检索

        返回: [{
            "filename": str,        # 来自 metadata['filename']
            "document_id": int,     # 来自 metadata['document_id']
            "score": float,         # 归一化到 [0, 1]，保留 4 位小数
            "content": str          # 文档 page_content
        }]

        归一化策略：FAISS L2 距离转相似度 = 1 / (1 + distance)
        """
        if self.vector_store is None:
            return []
        raw = self.vector_store.similarity_search_with_score(query, k=k)
        results = []
        for doc, distance in raw:
            meta = doc.metadata or {}
            score = 1.0 / (1.0 + float(distance))
            score = round(score, 4)
            results.append({
                "filename": meta.get("filename", "unknown"),
                "document_id": int(meta.get("document_id", 0)),
                "score": score,
                "content": doc.page_content,
            })
        return results


vector_store_service = VectorStoreService()
