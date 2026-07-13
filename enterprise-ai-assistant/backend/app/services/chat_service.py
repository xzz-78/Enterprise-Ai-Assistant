"""
AI 聊天服务
实现基于 RAG（检索增强生成）的问答功能
"""
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document as LangchainDocument

from app.core.config import settings
from app.services.vector_service import vector_store_service


class ChatService:
    """
    AI 聊天服务类
    实现基于知识库的智能问答

    延迟初始化设计：
    - __init__ 只初始化 Prompt，不创建 LLM 实例
    - LLM 实例在首次调用时通过 _get_llm() 懒加载创建
    - 如果 OPENAI_API_KEY 缺失或 API Base 不可达，不会导致应用启动崩溃
    - 错误延迟到实际调用时抛出，便于捕获和处理
    """

    def __init__(self):
        """初始化聊天服务（延迟初始化模式）"""
        self._llm = None

        # 自定义 Prompt 模板
        self.prompt_template = """你是一个专业的企业知识助手，请根据以下提供的上下文信息回答用户的问题。
如果上下文信息中没有相关答案，请如实告知用户你不知道，不要编造答案。
回答要简洁明了，条理清晰，使用中文回答。

上下文信息：
{context}

用户问题：{question}

回答："""

        self.PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

    def _get_llm(self) -> ChatOpenAI:
        """
        延迟获取 LLM 实例

        首次调用时创建 LLM 实例，后续调用复用。
        如果 OPENAI_API_KEY 缺失，会在调用时抛出错误，而非应用启动时。

        Returns:
            ChatOpenAI: LLM 实例

        Raises:
            ValueError: 如果 OPENAI_API_KEY 为空
        """
        if self._llm is None:
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-your-openai-api-key":
                raise ValueError("OPENAI_API_KEY 未配置，请在 .env 文件中设置有效的 API Key")

            self._llm = ChatOpenAI(
                model_name=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.3,
                max_tokens=2000,
            )
        return self._llm

    def _retrieve_documents(self, query: str, k: int = 4) -> List[dict]:
        """
        从知识库检索相关文档（带分数）

        Args:
            query: 查询问题
            k: 返回的文档数量（会根据上下文长度动态调整）

        Returns:
            List[dict]: 相关文档列表，每条包含：
                - content: 文档内容
                - score: 归一化相似度分数 [0, 1]
                - filename: 文件名
                - document_id: 文档 ID
        """
        return vector_store_service.search_with_sources(query, k=k)

    def _build_context(self, documents: List[dict], max_context_chars: int = 8000) -> str:
        """
        将检索到的文档构建成上下文字符串

        优化策略：
        1. 相关性阈值过滤：只保留 score >= 0.3 的文档，避免低相关度内容污染回答
        2. 去重：基于内容哈希去重，避免重复文档浪费 token
        3. 长度控制：总上下文不超过 max_context_chars（约 2000-3000 tokens）
        4. 按分数排序：高相关度文档优先放入，保证回答质量

        Args:
            documents: 文档列表（带 score 的字典结构）
            max_context_chars: 上下文最大字符数限制

        Returns:
            str: 拼接后的上下文（可能为空字符串）
        """
        if not documents:
            return ""

        RELEVANCE_THRESHOLD = 0.3

        filtered = [
            doc for doc in documents
            if doc.get("score", 0) >= RELEVANCE_THRESHOLD
        ]

        filtered.sort(key=lambda x: x.get("score", 0), reverse=True)

        seen_hashes = set()
        context_parts = []
        total_chars = 0

        for i, doc in enumerate(filtered, 1):
            content = doc.get("content", "")
            filename = doc.get("filename", "unknown")
            content_hash = hash(content.strip()[:500])

            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            part = f"[文档 {i} - {filename}]:\n{content}"
            part_chars = len(part)

            if total_chars + part_chars > max_context_chars:
                remaining = max_context_chars - total_chars
                if remaining > 100:
                    truncated = part[:remaining - 3] + "..."
                    context_parts.append(truncated)
                break

            context_parts.append(part)
            total_chars += part_chars

        return "\n\n".join(context_parts)

    def _generate_answer(self, question: str, context: str) -> str:
        """
        使用 LLM 生成回答

        Args:
            question: 用户问题
            context: 上下文信息

        Returns:
            str: 生成的回答
        """
        prompt = self.PROMPT.format(context=context, question=question)
        response = self._get_llm().invoke(prompt)
        return response.content

    def chat(self, question: str, use_knowledge_base: bool = True) -> dict:
        """
        AI 问答接口

        Args:
            question: 用户问题
            use_knowledge_base: 是否使用知识库（True 为 RAG 模式，False 为纯 LLM）

        Returns:
            dict: 包含 answer 和 source 字段的字典
                - answer: AI 回答内容
                - source: 回答来源标识 ("rag" | "llm" | "empty_knowledge")
        """
        if use_knowledge_base:
            if vector_store_service.vector_store is None:
                return {
                    "answer": "知识库为空，请先上传文档后再提问，当前回答基于通用知识。",
                    "source": "empty_knowledge"
                }

            documents = self._retrieve_documents(question)

            if documents:
                context = self._build_context(documents)

                if context:
                    answer = self._generate_answer(question, context)
                    return {
                        "answer": answer,
                        "source": "rag"
                    }

                return {
                    "answer": "检索到的文档相关性较低，当前回答基于通用知识。",
                    "source": "llm"
                }

            return {
                "answer": "未检索到相关文档，请尝试更换关键词提问，当前回答基于通用知识。",
                "source": "llm"
            }

        general_prompt = f"""你是一个专业的企业知识助手。
用户问：{question}
请用中文简洁、专业地回答用户的问题。如果不确定，请如实说明。

回答："""

        response = self._get_llm().invoke(general_prompt)
        return {
            "answer": response.content,
            "source": "llm"
        }

    def chat_with_sources(self, question: str, k: int = 8) -> dict:
        """
        带来源引用的 RAG 问答

        返回 {"answer": str, "sources": [{filename, document_id, score, content}]}
        知识库为空时 sources=[], answer="知识库为空，请先上传文档。"

        优化策略：
        - 动态 k 值：默认检索 8 条，通过 _build_context 的相关性过滤和长度控制筛选有效内容
        - 只返回实际参与回答的来源（过滤后的文档）

        Args:
            question: 用户问题
            k: 初始检索的文档数量（会通过过滤/去重/长度控制进一步筛选）

        Returns:
            dict: 包含 answer 和 sources 的字典
        """
        sources = vector_store_service.search_with_sources(question, k=k)
        if not sources:
            return {
                "answer": "知识库为空，请先上传文档后再提问。",
                "sources": []
            }

        context = self._build_context(sources)

        if not context:
            return {
                "answer": "检索到的文档相关性较低，请尝试更换关键词提问。",
                "sources": []
            }

        prompt = self.PROMPT.format(context=context, question=question)
        response = self._get_llm().invoke(prompt)

        RELEVANCE_THRESHOLD = 0.3
        filtered_sources = [
            s for s in sources
            if s.get("score", 0) >= RELEVANCE_THRESHOLD
        ]
        filtered_sources.sort(key=lambda x: x.get("score", 0), reverse=True)

        return {
            "answer": response.content,
            "sources": filtered_sources
        }


# 全局聊天服务实例
chat_service = ChatService()
