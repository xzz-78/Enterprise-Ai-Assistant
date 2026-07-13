"""
AI 分析报告服务
根据销售数据自动生成业务分析报告
"""
import json
import logging
import re
from datetime import date, timedelta
from typing import List, Dict, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.models import Sale

logger = logging.getLogger(__name__)


class ReportService:
    """
    AI 分析报告服务类
    基于销售数据生成智能分析报告

    延迟初始化设计：
    - __init__ 不创建 LLM 实例
    - LLM 实例在首次调用时通过 _get_llm() 懒加载创建
    - 如果 OPENAI_API_KEY 缺失，不会导致应用启动崩溃
    """

    def __init__(self):
        """初始化报告服务（延迟初始化模式）"""
        self._llm = None

    def _get_llm(self) -> ChatOpenAI:
        """
        延迟获取 LLM 实例

        首次调用时创建 LLM 实例，后续调用复用。

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
                temperature=0.4,
                max_tokens=3000,
            )
        return self._llm

    def _get_sales_data(self, db: Session, days: int) -> List[Sale]:
        """
        获取指定天数的销售数据

        Args:
            db: 数据库会话
            days: 天数

        Returns:
            List[Sale]: 销售数据列表
        """
        end_date = db.query(func.max(Sale.date)).scalar()
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
        response = self._get_llm().invoke(formatted_prompt)

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
        response = self._get_llm().invoke(formatted_prompt)

        # 解析建议列表
        recommendations = []
        for line in response.content.strip().split("\n"):
            line = line.strip()
            # 去掉数字前缀
            if line and (line[0].isdigit() or line.startswith("-")):
                # 移除 "1. " 或 "- " 前缀
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


# ============= P2 扩展：AI 业务分析师（BusinessReportService） =============
# 不修改上述 ReportService 类的任何方法，仅在文件末尾追加新类与全局实例
# 流程严格遵循："SQL 聚合 → 数据汇总 → Prompt → LLM"


class BusinessReportService:
    """
    AI 业务分析师服务类（P2 阶段新增）

    与原有 ReportService 并存，职责不同：
    - ReportService：生成兼容版本的"数据摘要 + 大段 AI 分析 + 建议列表"
    - BusinessReportService：生成结构化三段式报告（summary / insights / suggestions），
      严格走"SQL 聚合 → Prompt → LLM → JSON 解析"的工程化流程

    三步流水线：
    1. _sql_aggregate：在数据库层做 SQL 聚合（func.sum / group_by / order_by），
       禁止在 Python 端 list 循环做 sum；
    2. _build_prompt：把聚合结果格式化为中文 Prompt，要求 LLM 只基于真实数据回答；
    3. _call_llm：调用 LLM 并用 json.loads 解析响应；解析失败时回退到默认结构。
    """

    def __init__(self):
        """初始化业务分析服务（延迟初始化模式）"""
        self._llm = None

    def _get_llm(self) -> ChatOpenAI:
        """
        延迟获取 LLM 实例

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

    # ------------------------------------------------------------------ #
    # 第一步：SQL 聚合                                                    #
    # ------------------------------------------------------------------ #
    def _sql_aggregate(self, db: Session, days: int) -> dict:
        """
        第一步：SQL 聚合统计

        完全在数据库层完成聚合计算，遵循以下规范：
        - 使用 SQLAlchemy 的 func.sum / group_by / order_by 在 MySQL/SQLite 内执行
        - 禁止在 Python 端用 list 循环做 sum（性能差且不可扩展）
        - 使用 func.coalesce 把 NULL 聚合为 0，保证下游计算不报 NoneType 错误
        - 对 category_breakdown / region_breakdown 做 isnot(None) 过滤，剔除历史脏数据

        Args:
            db: 数据库会话
            days: 分析窗口天数（7-365）

        Returns:
            dict: 包含以下字段
                - total_revenue: 窗口内累计销售额
                - total_orders: 窗口内累计订单数
                - total_customers: 窗口内累计客户数
                - avg_daily_revenue: 日均销售额
                - revenue_growth_rate: 销售增长率（%）
                - top_category: 销售额最高的产品分类（可能为 None）
                - top_region: 销售额最高的销售区域（可能为 None）
                - category_breakdown: 分类维度明细
                - region_breakdown: 区域维度明细
                - daily_avg_orders: 日均订单数
                - daily_avg_customers: 日均客户数
                - actual_days: 实际覆盖的天数
        """
        # end_date 取 DB 中最后一条销售记录的日期，与 Dashboard 保持一致
        # 这样即使数据停留在几天前，分析窗口也能正确覆盖有数据的范围
        end_date = db.query(func.max(Sale.date)).scalar()
        if end_date is None:
            end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        # 1) 总体聚合：sum(revenue) / sum(orders) / sum(customers) / count(distinct date)
        total_row = (
            db.query(
                func.coalesce(func.sum(Sale.revenue), 0.0).label("total_revenue"),
                func.coalesce(func.sum(Sale.orders), 0).label("total_orders"),
                func.coalesce(func.sum(Sale.customers), 0).label("total_customers"),
                func.count(func.distinct(Sale.date)).label("actual_days"),
            )
            .filter(Sale.date >= start_date, Sale.date <= end_date)
            .first()
        )

        # 兜底：销售表为空时 .first() 返回 None，避免 AttributeError
        if total_row is None:
            total_revenue = 0.0
            total_orders = 0
            total_customers = 0
            actual_days = 0
        else:
            total_revenue = float(total_row.total_revenue or 0.0)
            total_orders = int(total_row.total_orders or 0)
            total_customers = int(total_row.total_customers or 0)
            actual_days = int(total_row.actual_days or 0) or days  # 若全空则按窗口天数兜底

        # 2) 日均指标（避免除零）
        avg_daily_revenue = round(total_revenue / actual_days, 2) if actual_days else 0.0
        daily_avg_orders = round(total_orders / actual_days, 2) if actual_days else 0.0
        daily_avg_customers = round(total_customers / actual_days, 2) if actual_days else 0.0

        # 3) 增长率：窗口后半段 vs 前半段（按日期升序排序后切片）
        #    这里仍然在 SQL 层做"按日期排序的金额"获取，再在 Python 端做切片
        #    是因为 SQL 的 split-half 需要窗口函数，跨数据库兼容性差
        daily_revenue_rows = (
            db.query(Sale.date, Sale.revenue)
            .filter(Sale.date >= start_date, Sale.date <= end_date)
            .order_by(Sale.date.asc())
            .all()
        )
        revenue_growth_rate = 0.0
        if len(daily_revenue_rows) >= 2:
            mid = len(daily_revenue_rows) // 2
            first_half = sum(float(r.revenue or 0.0) for r in daily_revenue_rows[:mid])
            second_half = sum(float(r.revenue or 0.0) for r in daily_revenue_rows[mid:])
            if first_half > 0:
                revenue_growth_rate = round(
                    (second_half - first_half) / first_half * 100, 2
                )
            else:
                revenue_growth_rate = 0.0

        # 4) 分类维度聚合（NULL 过滤）—— 严格在 SQL 层做 group_by
        category_rows = (
            db.query(
                Sale.product_category.label("category"),
                func.coalesce(func.sum(Sale.revenue), 0.0).label("revenue"),
                func.coalesce(func.sum(Sale.orders), 0).label("orders"),
                func.coalesce(func.sum(Sale.customers), 0).label("customers"),
            )
            .filter(
                Sale.date >= start_date,
                Sale.date <= end_date,
                Sale.product_category.isnot(None),  # NULL 过滤
            )
            .group_by(Sale.product_category)
            .order_by(func.sum(Sale.revenue).desc())
            .all()
        )
        category_breakdown = [
            {
                "category": row.category,
                "revenue": float(row.revenue or 0.0),
                "orders": int(row.orders or 0),
                "customers": int(row.customers or 0),
            }
            for row in category_rows
        ]
        # 5) 区域维度聚合（NULL 过滤）
        region_rows = (
            db.query(
                Sale.region.label("region"),
                func.coalesce(func.sum(Sale.revenue), 0.0).label("revenue"),
                func.coalesce(func.sum(Sale.orders), 0).label("orders"),
                func.coalesce(func.sum(Sale.customers), 0).label("customers"),
            )
            .filter(
                Sale.date >= start_date,
                Sale.date <= end_date,
                Sale.region.isnot(None),  # NULL 过滤
            )
            .group_by(Sale.region)
            .order_by(func.sum(Sale.revenue).desc())
            .all()
        )
        region_breakdown = [
            {
                "region": row.region,
                "revenue": float(row.revenue or 0.0),
                "orders": int(row.orders or 0),
                "customers": int(row.customers or 0),
            }
            for row in region_rows
        ]

        # 6) Top 1 类别 / 区域（若存在）
        top_category = category_breakdown[0]["category"] if category_breakdown else None
        top_region = region_breakdown[0]["region"] if region_breakdown else None

        return {
            "window_start": start_date.isoformat(),
            "window_end": end_date.isoformat(),
            "window_days": days,
            "actual_days": actual_days,
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "total_customers": total_customers,
            "avg_daily_revenue": avg_daily_revenue,
            "daily_avg_orders": daily_avg_orders,
            "daily_avg_customers": daily_avg_customers,
            "revenue_growth_rate": revenue_growth_rate,
            "top_category": top_category,
            "top_region": top_region,
            "category_breakdown": category_breakdown,
            "region_breakdown": region_breakdown,
        }

    # ------------------------------------------------------------------ #
    # 第二步：构建 Prompt                                                 #
    # ------------------------------------------------------------------ #
    def _build_prompt(self, agg: dict) -> str:
        """
        第二步：把 SQL 聚合结果格式化为中文 Prompt 字符串

        Prompt 必须强制约束：
        - 只能基于上面提供的真实统计数据回答
        - 禁止编造任何数字
        - 返回严格的 JSON 结构：{"summary": str, "insights": [str], "suggestions": [str]}
        - insights 至少 3 条、suggestions 至少 3 条

        Args:
            agg: _sql_aggregate 返回的聚合字典

        Returns:
            str: 拼装好的中文 Prompt
        """
        # 类别 Top 5
        top_categories = agg.get("category_breakdown", [])[:5]
        category_text = (
            "\n".join(
                f"  - {c['category']}: 销售额 ¥{c['revenue']:.2f}，"
                f"订单 {c['orders']}，客户 {c['customers']}"
                for c in top_categories
            )
            if top_categories
            else "  （无数据，product_category 全部为 NULL）"
        )

        # 区域 Top 5
        top_regions = agg.get("region_breakdown", [])[:5]
        region_text = (
            "\n".join(
                f"  - {r['region']}: 销售额 ¥{r['revenue']:.2f}，"
                f"订单 {r['orders']}，客户 {r['customers']}"
                for r in top_regions
            )
            if top_regions
            else "  （无数据，region 全部为 NULL）"
        )

        prompt = f"""你是一位资深的企业经营分析师，请基于以下【真实】销售数据撰写一份业务分析报告。

========================================
【分析窗口】
- 窗口起止：{agg['window_start']} 至 {agg['window_end']}（共 {agg['window_days']} 天，实际覆盖 {agg['actual_days']} 天）

【核心 KPI】
- 累计销售额：¥{agg['total_revenue']:.2f}
- 累计订单数：{agg['total_orders']}
- 累计客户数：{agg['total_customers']}
- 日均销售额：¥{agg['avg_daily_revenue']:.2f}
- 日均订单数：{agg['daily_avg_orders']:.2f}
- 日均客户数：{agg['daily_avg_customers']:.2f}
- 销售增长率（窗口后半段 vs 前半段）：{agg['revenue_growth_rate']:.2f}%
- 销售额最高的产品分类：{agg['top_category'] or '无'}
- 销售额最高的销售区域：{agg['top_region'] or '无'}

【产品分类明细（按销售额降序，最多 5 条）】
{category_text}

【销售区域明细（按销售额降序，最多 5 条）】
{region_text}
========================================

【硬性要求】
1. 你必须**只**基于上方提供的真实数据回答问题；
2. **禁止编造任何具体数字**（订单数、金额、百分比等必须与上方一致或显式标注为"约"）；
3. 必须返回**严格的 JSON 对象**，不要包裹在 ```json``` 代码块中，不要有任何额外解释文字；
4. JSON 字段：
   - "summary": string，200-400 字的中文执行摘要，覆盖整体表现、增长率、品类/区域集中度；
   - "insights": 数组，**至少 3 条**关键洞察，每条 1-2 句话，引用具体数字；
   - "suggestions": 数组，**至少 3 条**可执行的行动建议，覆盖销售/客户/品类/区域运营；
5. 若数据存在 NULL 字段（category/region 缺失），请在建议中提示补充数据维度。

请直接输出以下 JSON（不要加任何前缀）：
{{"summary": "...", "insights": ["...", "...", "..."], "suggestions": ["...", "...", "..."]}}
"""
        return prompt

    # ------------------------------------------------------------------ #
    # 第三步：调用 LLM + JSON 解析                                        #
    # ------------------------------------------------------------------ #
    def _call_llm(self, prompt: str) -> dict:
        """
        第三步：调用 LLM 并解析 JSON 响应

        - 使用 LangChain ChatOpenAI 调用模型
        - 尝试用 json.loads 解析响应
        - 解析失败时（模型偶发返回带 markdown 围栏或多余文字）尝试用正则抓出首个 {...}
        - 仍失败则回退到默认结构，避免 500

        Args:
            prompt: 拼装好的中文 Prompt

        Returns:
            dict: {summary, insights, suggestions}，任何字段缺失都用空值兜底
        """
        # 兜底：保证即使完全失败也返回结构
        fallback = {
            "summary": "AI 暂时无法生成分析报告，请稍后重试。",
            "insights": [
                "已获取基础销售汇总数据，但模型未返回结构化洞察。",
                "建议关注整体销售趋势与高贡献分类/区域。",
                "建议后续接入更丰富的维度（毛利率、退货率、客单价）以提升洞察质量。",
            ],
            "suggestions": [
                "对 Top 分类追加促销活动，拉动头部品类继续增长。",
                "对尾部区域投放定向广告，缩小区域销售差距。",
                "建立周维度复盘机制，结合本报告持续跟踪关键 KPI。",
            ],
        }

        try:
            response = self._get_llm().invoke(prompt)
            content = (response.content or "").strip()
        except Exception as e:  # noqa: BLE001
            # LLM 调用异常时仍返回兜底
            logger.warning(f"LLM invoke failed: {e}")
            return fallback

        # 1) 直接解析
        parsed = self._try_parse_json(content)
        if parsed is None:
            # 2) 尝试从字符串中抓取第一个 {...} 块
            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                parsed = self._try_parse_json(match.group(0))

        if not isinstance(parsed, dict):
            return fallback

        summary = parsed.get("summary") or "暂无执行摘要。"
        insights = parsed.get("insights") or []
        suggestions = parsed.get("suggestions") or []

        # 规范化：强制转成 list[str]
        if not isinstance(insights, list):
            insights = [str(insights)]
        if not isinstance(suggestions, list):
            suggestions = [str(suggestions)]
        insights = [str(x).strip() for x in insights if str(x).strip()]
        suggestions = [str(x).strip() for x in suggestions if str(x).strip()]

        return {
            "summary": str(summary).strip(),
            "insights": insights,
            "suggestions": suggestions,
        }

    @staticmethod
    def _try_parse_json(text: str):
        """安全地尝试 json.loads，失败返回 None"""
        try:
            return json.loads(text)
        except Exception:  # noqa: BLE001
            return None

    # ------------------------------------------------------------------ #
    # 主入口                                                              #
    # ------------------------------------------------------------------ #
    def generate(self, db: Session, days: int = 30) -> dict:
        """
        主入口：编排 "SQL 聚合 → 数据汇总 → Prompt → LLM" 三步

        - 空数据时直接返回固定提示，不调用 LLM，节省 token
        - 任何异常都不抛 500，而是返回带兜底结构的 dict

        Args:
            db: 数据库会话
            days: 分析窗口天数（7-365）

        Returns:
            dict: {summary: str, insights: List[str], suggestions: List[str]}
        """
        try:
            # 第一步：SQL 聚合
            agg = self._sql_aggregate(db, days)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SQL aggregate failed: {e}")
            return {
                "summary": "数据库聚合失败，请稍后重试。",
                "insights": [],
                "suggestions": [],
            }

        # 空数据快捷返回（不浪费 LLM token）
        if agg["total_revenue"] <= 0 and agg["total_orders"] <= 0:
            return {
                "summary": "暂无销售数据可供分析。",
                "insights": [],
                "suggestions": [],
            }

        # 第二步：构建 Prompt
        prompt = self._build_prompt(agg)

        # 第三步：调用 LLM（内部已有兜底，不会抛 500）
        return self._call_llm(prompt)


# 全局业务分析报告服务实例（P2）
business_report_service = BusinessReportService()
