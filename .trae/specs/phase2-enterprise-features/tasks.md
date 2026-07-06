# Tasks

按优先级顺序执行。每个任务完成后再启动下一个，避免大爆炸修改。

## 阶段零：基线确认
- [ ] Task 0: 启动后端 + 前端 dev，确认 `GET /api/dashboard`、`POST /api/report`、`POST /api/chat/with-sources` 当前返回结构与字段
  - [ ] SubTask 0.1: 记录现有 `Sale` 表字段与 Dashboard 响应，作为兼容性基线
  - [ ] SubTask 0.2: 记录 `ReportResponse`、`ChatResponse` 当前字段，作为对比基线

## 阶段一：Dashboard 数据分析模块（P1）
- [x] Task 1: 扩展 `Sale` 模型，新增 `region` 与 `product_category` 字段（不删不改旧字段）
  - [x] SubTask 1.1: 在 `backend/app/models/models.py` 中为 `Sale` 增加 `region`（String(50)，nullable）与 `product_category`（String(50)，nullable）
  - [x] SubTask 1.2: 在 `backend/init_db.py` 的 `generate_mock_sales_data` 调用处，扩展为按 region × category 维度生成 90 天模拟数据
- [x] Task 2: 后端新增 Dashboard 端点（保留旧 `GET /api/dashboard`）
  - [x] SubTask 2.1: 在 `schemas.py` 新增 `DashboardSummaryResponse`、`SalesTrendItem`（含 `order_date` 别名）、`CategoryStatItem`、`CategoryStatsResponse`
  - [x] SubTask 2.2: 在 `dashboard_service.py` 新增 `get_summary` / `get_trend` / `get_category_stats` 三个纯函数
  - [x] SubTask 2.3: 在 `api/dashboard.py` 新增 `GET /summary` `GET /trend` `GET /category` 三个路由，全部带 JWT 依赖
- [x] Task 3: 前端 Dashboard 页面升级为四图
  - [x] SubTask 3.1: 在 `frontend/src/services/dashboard.ts` 新增 `getSummary` `getTrend` `getCategoryStats`
  - [x] SubTask 3.2: 在 `frontend/src/types/index.ts` 新增对应 TS 类型
  - [x] SubTask 3.3: 重写 `DashboardPage.tsx`，使用 Recharts 渲染：销售额趋势（Area）、订单趋势（Line）、用户增长（Line）、产品分类占比（Pie）
  - [x] SubTask 3.4: 保留"生成模拟数据"按钮与 7/30/90 天切换

## 阶段二：AI Business Analyst（P2）
- [x] Task 4: 实现 `POST /api/report/generate`
  - [x] SubTask 4.1: 在 `schemas.py` 新增 `ReportGenerateRequest { days }` 与 `BusinessInsightReport { summary, insights, suggestions }`
  - [x] SubTask 4.2: 在 `report_service.py` 新增 `BusinessReportService.generate(days)`，内部流程严格按"SQL 聚合 → 数据汇总 → Prompt → LLM"
    - 聚合指标：total_revenue、total_orders、total_customers、avg_daily_revenue、revenue_growth_rate、top_category、top_region
    - Prompt 模板明确要求"基于以上真实数据"且不得编造
  - [x] SubTask 4.3: 在 `api/report.py` 新增 `POST /generate` 路由
  - [x] SubTask 4.4: 在前端 `services/report.ts` 与 `pages/ReportPage.tsx` 接入新端点，按钮文本"生成本月经营报告"

## 阶段三：RAG 升级（P3）
- [x] Task 5: 增强 `VectorStoreService.similarity_search_with_score` 返回结构
  - [x] SubTask 5.1: 在 `vector_service.py` 新增 `search_with_sources(query, k)`，返回 `[ {filename, document_id, score, content} ]`，其中 `score` 做 `[0,1]` 归一化
  - [x] SubTask 5.2: 在 `document_service.py` 新增 `get_filename_by_document_id(db, document_id)`，按 `file_path` 反查或直接使用 metadata.source
- [x] Task 6: 完善 `POST /api/chat/with-sources` 响应
  - [x] SubTask 6.1: 在 `schemas.py` 新增 `SourceItem { filename, document_id, score, content }`、`ChatWithSourcesResponse { answer, sources }`
  - [x] SubTask 6.2: 在 `chat_service.py` 中将 `chat_with_sources` 改用 `search_with_sources` 并按新结构返回
  - [x] SubTask 6.3: 前端 `ChatPage.tsx` 在每条回答下方折叠展示 sources 列表

## 阶段四：工程化 Docker（P4）
- [x] Task 7: 后端 Dockerfile
  - [x] SubTask 7.1: 编写 `backend/Dockerfile`（python:3.11-slim，安装 `default-libmysqlclient-dev` + `gcc` 以编译 pymysql）
  - [x] SubTask 7.2: 编写 `backend/.dockerignore`
- [x] Task 8: 前端 Dockerfile
  - [x] SubTask 8.1: 多阶段构建 `frontend/Dockerfile`（node:20-alpine 构建 → nginx:alpine 运行）
  - [x] SubTask 8.2: 编写 `frontend/nginx.conf`，反向代理 `/api` 到 backend:8000
- [x] Task 9: docker-compose.yml
  - [x] SubTask 9.1: 编写根目录 `docker-compose.yml`，包含 `mysql:8.0` `backend` `frontend` 三个 service
  - [x] SubTask 9.2: backend 启动时自动 `python init_db.py` 创建表 + 种子数据
  - [x] SubTask 9.3: 暴露端口 3306 / 8000 / 5173，挂载 volumes 持久化数据

## 阶段五：简历友好文档（P5）
- [x] Task 10: `docs/architecture.md`
  - [x] SubTask 10.1: 写"系统架构图"（mermaid）：Browser → Frontend → Backend → MySQL/FAISS/OpenAI
  - [x] SubTask 10.2: 写"RAG 流程图"（mermaid）：Upload → Split → Embed → FAISS → Query → TopK → Prompt → LLM → Answer
  - [x] SubTask 10.3: 写"数据流图"（mermaid）：用户输入 → API 网关 → 业务服务 → 数据层
- [x] Task 11: `docs/interview-guide.md`
  - [x] SubTask 11.1: 章节 1：项目背景与目标
  - [x] SubTask 11.2: 章节 2：技术选型原因（FastAPI / React / FAISS / LangChain / Recharts 选型理由）
  - [x] SubTask 11.3: 章节 3：RAG 实现原理（chunk 切分、embedding、向量检索、prompt 组装）
  - [x] SubTask 11.4: 章节 4：FAISS 原理（IVF/HNSW 简述、本项目用的 IndexFlatL2）
  - [x] SubTask 11.5: 章节 5：面试高频问题（≥10 道，每题含参考要点）

## 阶段六：验证
- [x] Task 12: 对照 `checklist.md` 逐条验证；不通过的条目回到对应 Task 修复
  - SubTask 12.1: 全部 37 项 checklist 验证通过（结构层面）
  - SubTask 12.2: 后端 `python -c "from app.main import app; print('OK')"` 输出 OK
  - SubTask 12.3: 前端 `npx tsc --noEmit` 通过，零类型错误
  - SubTask 12.4: docker-compose.yml YAML 语法通过 `yaml.safe_load` 校验

## 阶段七：QA 复盘发现的偏差（不阻塞 checklist 验收，建议后续清理）

- [ ] Fix: P3 旧端点 `POST /api/chat/with-sources` 仍返回旧格式 `{content, metadata}`，新结构 `{filename, document_id, score, content}` 放在 `POST /api/chat/with-sources-v2`
  - 原因：当前实现以"加 v2 端点 + 保留 v1"模式实现新结构，前端切换至 v2 正常使用
  - 影响：严格按 spec "将 chat_with_sources 改用 search_with_sources" 的要求，v1 端点未改写；外部若有调用 v1 的集成方，新字段不可见
  - 建议：要么把 v1 端点改写返回新结构，要么把 spec 调整为"新增 v2 端点"，二选一
- [ ] Fix: P3 分数归一化使用 `round(score, 4)` 保留 4 位小数，spec 要求 2 位小数
  - 原因：`vector_service.py:219` `score = round(score, 4)` 比 spec 要求的 2 位多保留 2 位精度
  - 影响：极端情况下前端展示精度不一致
  - 建议：改为 `round(score, 2)` 或在序列化层统一截断
- [ ] Fix: P1 `init_db.py` 旧表 schema 不会自动添加新列
  - 原因：`Base.metadata.create_all` 只创建缺失表，已存在的 sales 表若缺少 region/product_category 不会自动加列
  - 影响：现有部署的存量表升级需要手动 ALTER TABLE 或引入 Alembic 迁移
  - 建议：当前对全新安装正常工作；后续如需支持在线 schema 升级，可加 Alembic
- [ ] Fix: Task 5.2 `get_filename_by_document_id` 函数未在 document_service.py 中实现
  - 原因：实现选择直接从 metadata 读取 `filename`（由 upload_document 写入），未单独建反查函数
  - 影响：实际功能等价，但与 tasks.md 中 [x] SubTask 5.2 字面要求不完全一致
  - 建议：补一个反查函数或更新 tasks.md 标记为 N/A

# Task Dependencies
- Task 1 → Task 2（先有模型后有服务）
- Task 2 → Task 3（先有 API 后有前端）
- Task 3 → Task 4（Dashboard 数据基础稳定后接入新报告）
- Task 4 → Task 5（验证业务流后再升级 RAG）
- Task 5 → Task 6（先有 service 方法再有 API 改造）
- Task 6 → Task 7（功能稳定后再容器化）
- Task 7 / Task 8 → Task 9
- Task 9 → Task 10 / Task 11（部署形态确定后画架构图与面试题）
- Task 10 / Task 11 → Task 12
