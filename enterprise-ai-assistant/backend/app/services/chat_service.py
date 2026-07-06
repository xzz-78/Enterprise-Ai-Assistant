"""
AI 聊天服务
实现基于 RAG（检索增强生成）的问答功能
"""
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document as LangchainDocument

from app.core.config import settings
from app.services.vector_service import vector_store_service


class ChatService:
    """
    AI 聊天服务类
    实现基于知识库的智能问答
    """

    def __init__(self):
        """初始化聊天服务"""
        self.llm = ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE,
            temperature=0.3,
            max_tokens=2000,
        )

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

        # 链的类型参数
        self.chain_type_kwargs = {"prompt": self.PROMPT}

    def _retrieve_documents(self, query: str, k: int = 4) -> List[LangchainDocument]:
        """
        从知识库检索相关文档

        Args:
            query: 查询问题
            k: 返回的文档数量

        Returns:
            List[LangchainDocument]: 相关文档列表
        """
        return vector_store_service.similarity_search(query, k=k)

    def _build_context(self, documents: List[LangchainDocument]) -> str:
        """
        将检索到的文档构建成上下文字符串

        Args:
            documents: 文档列表

        Returns:
            str: 拼接后的上下文
        """
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[文档 {i}]:\n{doc.page_content}")

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
        # 构建完整的 prompt
        prompt = self.PROMPT.format(context=context, question=question)

        # 调用 LLM
        response = self.llm.invoke(prompt)

        return response.content

    def chat(self, question: str, use_knowledge_base: bool = True) -> str:
        """
        AI 问答接口

        Args:
            question: 用户问题
            use_knowledge_base: 是否使用知识库（True 为 RAG 模式，False 为纯 LLM）

        Returns:
            str: AI 回答
        """
        if use_knowledge_base and vector_store_service.vector_store is not None:
            # 检索相关文档
            documents = self._retrieve_documents(question)

            if documents:
                # 构建上下文
                context = self._build_context(documents)

                # 生成回答（RAG 模式）
                answer = self._generate_answer(question, context)
                return answer

        # 如果没有启用知识库或没有检索到文档，使用纯 LLM 回答
        # 使用更通用的提示词
        general_prompt = f"""你是一个专业的企业知识助手。
用户问：{question}
请用中文简洁、专业地回答用户的问题。如果不确定，请如实说明。

回答："""

        response = self.llm.invoke(general_prompt)
        return response.content

    def chat_with_sources(self, question: str, k: int = 4) -> dict:
        """
        带来源引用的问答

        Args:
            question: 用户问题
            k: 检索的文档数量

        Returns:
            dict: 包含 answer 和 sources 的字典
        """
        documents = self._retrieve_documents(question, k=k)
        sources = []

        if documents:
            context = self._build_context(documents)
            answer = self._generate_answer(question, context)

            # 提取来源信息
            for doc in documents:
                source_info = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source_info)
        else:
            answer = self.chat(question, use_knowledge_base=False)

        return {
            "answer": answer,
            "sources": sources
        }

    def chat_with_sources_v2(self, question: str, k: int = 4) -> dict:
        """
        升级版带来源问答
        返回 {"answer": str, "sources": [{filename, document_id, score, content}]}
        知识库为空时 sources=[], answer="知识库为空，请先上传文档。"
        """
        sources = vector_store_service.search_with_sources(question, k=k)
        if not sources:
            return {
                "answer": "知识库为空，请先上传文档后再提问。",
                "sources": []
            }
        context_parts = [
            f"[文档 {i+1} - {s['filename']}]:\n{s['content']}"
            for i, s in enumerate(sources)
        ]
        context = "\n\n".join(context_parts)
        prompt = self.PROMPT.format(context=context, question=question)
        response = self.llm.invoke(prompt)
        return {
            "answer": response.content,
            "sources": sources
        }


# 全局聊天服务实例
chat_service = ChatService()
