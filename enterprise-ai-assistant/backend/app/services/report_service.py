"""
AI 分析报告服务
根据销售数据自动生成业务分析报告
"""
import json
from datetime import date, timedelta
from typing import List, Dict, Tuple

from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.models import Sale


class ReportService:
    """
    AI 分析报告服务类
    基于销售数据生成智能分析报告
    """

    def __init__(self):
        """初始化报告服务"""
        self.llm = ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE,
            temperature=0.4,
            max_tokens=3000,
        )

    def _get_sales_data(self, db: Session, days: int) -> List[Sale]:
        """
        获取指定天数的销售数据

        Args:
            db: 数据库会话
            days: 天数

        Returns:
            List[Sale]: 销售数据列表
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        sales = db.query(Sale).filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        ).order_by(Sale.date.asc()).all()

        return sales

    def _calculate_summary(self, sales: List[Sale]) -> Dict:
        """
        计算数据摘要

        Args:
            sales: 销售数据列表

        Returns:
            Dict: 数据摘要字典
        """
        if not sales:
            return {
                "total_revenue": 0.0,
                "total_orders": 0,
                "total_customers": 0,
                "avg_daily_revenue": 0.0,
                "revenue_growth_rate": 0.0
            }

        total_revenue = sum(s.revenue for s in sales)
        total_orders = sum(s.orders for s in sales)
        total_customers = sum(s.customers for s in sales)
        avg_daily_revenue = total_revenue / len(sales)

        # 计算增长率（前半段 vs 后半段）
        mid = len(sales) // 2
        if mid > 0:
            first_half_revenue = sum(s.revenue for s in sales[:mid])
            second_half_revenue = sum(s.revenue for s in sales[mid:])
            if first_half_revenue > 0:
                revenue_growth_rate = (second_half_revenue - first_half_revenue) / first_half_revenue * 100
            else:
                revenue_growth_rate = 0.0
        else:
            revenue_growth_rate = 0.0

        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "total_customers": total_customers,
            "avg_daily_revenue": round(avg_daily_revenue, 2),
            "revenue_growth_rate": round(revenue_growth_rate, 2)
        }

    def _format_data_for_ai(self, sales: List[Sale]) -> str:
        """
        将销售数据格式化为 AI 可读的文本

        Args:
            sales: 销售数据列表

        Returns:
            str: 格式化的数据文本
        """
        lines = []
        lines.append("日期\t销售额\t订单数\t客户数")

        # 为了避免数据过多，每隔几天采样一次
        step = max(1, len(sales) // 30)
        sampled = sales[::step]

        for s in sampled:
            lines.append(f"{s.date}\t{s.revenue:.2f}\t{s.orders}\t{s.customers}")

        return "\n".join(lines)

    def _generate_ai_analysis(self, sales_data_text: str, summary: Dict) -> str:
        """
        使用 AI 生成分析内容

        Args:
            sales_data_text: 销售数据文本
            summary: 数据摘要

        Returns:
            str: AI 生成的分析文本
        """
        prompt = PromptTemplate(
            input_variables=["data", "summary"],
            template="""你是一位专业的企业数据分析师。请根据以下销售数据，生成一份详细的业务分析报告。

数据摘要：
- 总销售额：{summary[total_revenue]} 元
- 总订单数：{summary[total_orders]} 单
- 总客户数：{summary[total_customers]} 人
- 日均销售额：{summary[avg_daily_revenue]} 元
- 销售增长率：{summary[revenue_growth_rate]}%

详细销售数据：
{data}

请从以下几个方面进行分析：
1. 整体销售表现评估
2. 趋势分析（上升/下降/波动）
3. 可能的原因分析
4. 关键发现

请用中文回答，条理清晰，专业严谨，字数控制在500字左右。

分析报告："""
        )

        formatted_prompt = prompt.format(data=sales_data_text, summary=summary)
        response = self.llm.invoke(formatted_prompt)

        return response.content

    def _generate_recommendations(self, sales_data_text: str, summary: Dict) -> List[str]:
        """
        使用 AI 生成改进建议

        Args:
            sales_data_text: 销售数据文本
            summary: 数据摘要

        Returns:
            List[str]: 建议列表
        """
        prompt = PromptTemplate(
            input_variables=["data", "summary"],
            template="""你是一位资深的企业管理顾问。请根据以下销售数据，提出具体可行的改进建议。

数据摘要：
- 总销售额：{summary[total_revenue]} 元
- 总订单数：{summary[total_orders]} 单
- 总客户数：{summary[total_customers]} 人
- 日均销售额：{summary[avg_daily_revenue]} 元
- 销售增长率：{summary[revenue_growth_rate]}%

详细销售数据：
{data}

请给出 5-8 条具体、可操作的改进建议，涵盖以下方面：
1. 销售策略优化
2. 客户增长策略
3. 运营效率提升
4. 风险管理

每条建议单独列出，简洁明了，具有可操作性。

请直接输出建议列表，每行一条，以数字开头，不需要其他解释。

改进建议：
1. """
        )

        formatted_prompt = prompt.format(data=sales_data_text, summary=summary)
        response = self.llm.invoke(formatted_prompt)

        # 解析建议列表
        recommendations = []
        for line in response.content.strip().split("\n"):
            line = line.strip()
            # 去掉数字前缀
            if line and (line[0].isdigit() or line.startswith("-")):
                # 移除 "1. " 或 "- " 前缀
                import re
                clean_line = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                if clean_line:
                    recommendations.append(clean_line)

        # 确保至少有几条建议
        if not recommendations:
            recommendations = [
                "优化销售渠道，拓展线上线下融合的销售模式",
                "加强客户关系管理，提升客户复购率和忠诚度",
                "建立数据驱动的运营机制，定期分析销售数据并调整策略",
                "关注市场动态和竞争对手，及时调整产品定价策略",
                "优化库存管理，降低运营成本，提升整体利润率"
            ]

        return recommendations[:8]  # 最多返回 8 条

    def generate_report(self, db: Session, days: int = 30) -> Dict:
        """
        生成完整的 AI 分析报告

        Args:
            db: 数据库会话
            days: 分析天数

        Returns:
            Dict: 报告数据字典
        """
        # 获取销售数据
        sales = self._get_sales_data(db, days)

        if not sales:
            return {
                "data_summary": {
                    "total_revenue": 0.0,
                    "total_orders": 0,
                    "total_customers": 0,
                    "avg_daily_revenue": 0.0,
                    "revenue_growth_rate": 0.0
                },
                "ai_analysis": "暂无销售数据可供分析。",
                "recommendations": []
            }

        # 计算数据摘要
        summary = self._calculate_summary(sales)

        # 格式化数据
        data_text = self._format_data_for_ai(sales)

        # 生成 AI 分析
        ai_analysis = self._generate_ai_analysis(data_text, summary)

        # 生成建议
        recommendations = self._generate_recommendations(data_text, summary)

        return {
            "data_summary": summary,
            "ai_analysis": ai_analysis,
            "recommendations": recommendations
        }


# 全局报告服务实例
report_service = ReportService()
