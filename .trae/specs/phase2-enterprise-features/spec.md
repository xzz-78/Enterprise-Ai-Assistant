# 第二阶段功能规格说明（Phase 2 Spec）

## Why

当前项目已达到 MVP 状态，但销售分析能力较弱（仅按日期聚合）、AI 报告结构松散、RAG 缺少可解释的来源信息、缺少一键启动的工程化部署与简历友好的说明文档。本阶段在不重构已有代码的前提下，新增企业级能力，让项目对标校招 AI 应用开发岗位的展示标准。

## What Changes

- **P1-Dashboard 模块**：拆分 Dashboard 端点为 `/summary` / `/trend` / `/category`；扩展 `Sale` 表支持 `region` 与 `product_category`；前端使用 Recharts 展示销售/订单/用户增长趋势与产品分类占比饼图。
- **P2-AI Business Analyst 模块**：新增 `POST /report/generate`，流程固定为"SQL 统计 → 数据汇总 → Prompt → LLM"，返回 `summary` / `insights` / `suggestions` 三段式结构化报告。
- **P3-RAG 升级模块**：增强 `similarity_search_with_score`，返回 `filename` / `document_id` / `score` / `content`；完善 `POST /chat/with-sources` 响应结构。
- **P4-工程化模块**：新增根级 `Dockerfile`（backend）、`frontend/Dockerfile`、`docker-compose.yml`，一条命令拉起 `frontend` / `backend` / `mysql`。
- **P5-文档模块**：新增 `docs/architecture.md`（系统架构、RAG 流程、数据流）与 `docs/interview-guide.md`（项目背景、技术选型、RAG/FAISS 原理、面试题）。

> **不修改**：现有 `Sale.date` 字段保持兼容；现有 `GET /api/dashboard`、`POST /api/report`、`POST /api/chat` 接口保持可用；不替换 Recharts/FAISS/LangChain 任何组件。

## Impact

- **Affected specs**：
  - 数据模型层（`Sale` 表新增列）
  - 业务服务层（`dashboard_service` / `report_service` / `chat_service` / `vector_service` 新增方法）
  - API 层（`dashboard.py` / `report.py` / `chat.py` 新增路由）
  - Schema 层（`schemas.py` 新增 Pydantic 模型）
  - 前端服务与页面（`dashboard.ts` / `report.ts` / `DashboardPage.tsx` / `ReportPage.tsx`）
- **Affected code**：
  - `backend/app/models/models.py`
  - `backend/app/services/*.py`
  - `backend/app/api/*.py`
  - `backend/app/schemas/schemas.py`
  - `backend/app/core/config.py`（新增 `MYSQL_*` 等 Docker 变量）
  - `backend/init_db.py`（增加 region / product_category 模拟）
  - `frontend/src/services/*.ts`
  - `frontend/src/pages/DashboardPage.tsx`
  - `frontend/src/pages/ReportPage.tsx`
  - `frontend/src/types/index.ts`
  - `docs/architecture.md`、`docs/interview-guide.md`
  - 新增 `Dockerfile`、`docker-compose.yml`、`frontend/Dockerfile`、`.dockerignore`

## ADDED Requirements

### Requirement: 1.1 销售数据模型扩展
数据库 `Sale` 表 SHALL 在不破坏现有列的前提下新增 `region`（String(50)）与 `product_category`（String(50)）两个可空字段。

#### Scenario: 新建表与历史数据共存
- **WHEN** 通过 `init_db.py` 初始化或 `Base.metadata.create_all` 重建
- **THEN** `sales` 表包含 `id` / `date` / `revenue` / `orders` / `customers` / `region` / `product_category` 全部列；旧记录的 `region` / `product_category` 为 `NULL`，API 返回 `null` 不报错

### Requirement: 1.2 Dashboard 端点拆分
后端 SHALL 新增三个端点（`/api/dashboard/summary` `/api/dashboard/trend` `/api/dashboard/category`），全部需要登录且在现有 `GET /api/dashboard` 之外互不影响。

#### Scenario: 获取汇总
- **WHEN** 已登录用户访问 `GET /api/dashboard/summary`
- **THEN** 返回 `{ "total_revenue": number, "total_orders": int, "total_customers": int }`

#### Scenario: 获取趋势
- **WHEN** 已登录用户访问 `GET /api/dashboard/trend?days=30`
- **THEN** 返回 `[{ "date":"YYYY-MM-DD", "revenue":number, "orders":int, "customers":int, "region":string|null }]` 长度为 N 的数组

#### Scenario: 获取产品分类统计
- **WHEN** 已登录用户访问 `GET /api/dashboard/category`
- **THEN** 返回 `[{ "category":string, "revenue":number, "orders":int, "customers":int }]`，按 `revenue` 降序

### Requirement: 1.3 前端 Dashboard 图表
`DashboardPage` SHALL 展示至少四张图（销售额趋势、订单趋势、用户增长趋势、产品分类占比饼图），并支持"最近 7/30/90 天"切换与"生成模拟数据"按钮。

#### Scenario: 加载并展示
- **WHEN** 用户进入 Dashboard 页面
- **THEN** 卡片显示三组总数 + 增长率；下方依次展示四张图表，使用 Recharts，数据来源为新增的三个端点

### Requirement: 2.1 AI 业务分析师端点
后端 SHALL 新增 `POST /api/report/generate`，入参 `{ "days": int }`（7-365），返回 `{ "summary": string, "insights": [string], "suggestions": [string] }`。

#### Scenario: 流程闭环
- **WHEN** 已登录用户调用 `POST /api/report/generate { "days": 30 }`
- **THEN** 服务先执行 SQL 聚合（总额/总单/客户/日均/增长率/Top 类别/Top 区域），将统计结果注入 Prompt，再调用 LLM，输出 `summary` + `insights`(≥3) + `suggestions`(≥3)

#### Scenario: 空数据容错
- **WHEN** 销售表为空
- **THEN** 返回 `summary="暂无销售数据"`，`insights` 与 `suggestions` 为空数组，且 HTTP 状态为 200

### Requirement: 3.1 RAG 来源可追溯
`VectorStoreService.similarity_search_with_score` SHALL 返回每条结果包含 `filename`（来自 metadata.source 或 document_id 反查）、`document_id`、`score`（float，[0,1] 区间内归一化）、`content`（page_content）。

#### Scenario: 检索返回带分数来源
- **WHEN** 用户在 `POST /api/chat/with-sources` 发起提问
- **THEN** 响应为 `{ "answer": string, "sources": [{ "filename": string, "document_id": int, "score": number, "content": string }] }`，`sources` 数量等于检索 `k`

#### Scenario: 空知识库
- **WHEN** 知识库未初始化
- **THEN** 返回 `"知识库为空"` 提示，`sources` 为空数组

### Requirement: 4.1 Docker 一键部署
根目录 SHALL 提供 `Dockerfile`（backend）、`frontend/Dockerfile`、`docker-compose.yml`，执行 `docker compose up` 即可启动 frontend（5173）/ backend（8000）/ mysql（3306）。

#### Scenario: 健康启动
- **WHEN** 用户在根目录执行 `docker compose up -d`
- **THEN** 三个服务均健康启动；`http://localhost:8000/docs` 可访问；`http://localhost:5173` 可访问

### Requirement: 5.1 文档交付
`docs/architecture.md` SHALL 包含"系统架构图（mermaid）""RAG 流程图（mermaid）""数据流图（mermaid）"三段；`docs/interview-guide.md` SHALL 包含项目背景、技术选型原因、RAG 实现原理、FAISS 原理、面试高频问题 5 个章节。

#### Scenario: 文档可读
- **WHEN** 面试官打开两个 markdown 文档
- **THEN** 文档结构清晰、含 mermaid 图可被 GitHub 渲染、面试题不少于 10 道

## MODIFIED Requirements

### Requirement: 现有 Sales 数据兼容
- `Sale.date` 字段保留，列名不强制改为 `order_date`（保持兼容）；`order_date` 作为对外展示字段在 Schema 层映射（`order_date: date` 字段名出现在 `SalesTrendItem` 响应中，但通过 `model_validator`/`field_alias` 与 `date` 映射，保证响应里同时存在 `date` 与 `order_date`）。

### Requirement: 现有 Dashboard 接口保留
- 现有 `GET /api/dashboard`、`POST /api/dashboard/generate-mock-data` 保留为兼容接口，本阶段不删除。

### Requirement: 现有 Report 接口保留
- 现有 `POST /api/report` 保留为兼容接口；本阶段新增 `POST /api/report/generate` 作为更结构化的版本。

### Requirement: 现有 Chat 接口保留
- 现有 `POST /api/chat` 保留；`POST /api/chat/with-sources` 字段结构增强为 `{ answer, sources: [{filename, document_id, score, content}] }`。

## REMOVED Requirements

无。
