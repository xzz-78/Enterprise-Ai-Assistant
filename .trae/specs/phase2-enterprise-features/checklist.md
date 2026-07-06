# 验收检查清单（Checklist）

按 P1 → P5 顺序逐条核对，**未通过的项需回到对应 Task 修复**。

## P1 Dashboard 模块

- [x] `Sale` 模型同时含 `id` / `date` / `revenue` / `orders` / `customers` / `region` / `product_category` 七个字段，且 `region` 与 `product_category` 可空
- [x] `init_db.py` 重新执行后，旧表结构不报错；新增列成功
- [x] `GET /api/dashboard/summary` 未登录返回 401，登录后返回 `{ total_revenue, total_orders, total_customers }`
- [x] `GET /api/dashboard/trend?days=30` 返回长度 ≤ 30 的数组，每项含 `date` `revenue` `orders` `customers` 字段
- [x] `GET /api/dashboard/category` 返回按 `revenue` 降序的数组，每项含 `category` `revenue` `orders` `customers`
- [x] 旧 `GET /api/dashboard` 与 `POST /api/dashboard/generate-mock-data` 仍可访问，行为不变
- [x] 前端 Dashboard 页面同时展示"销售额趋势" "订单趋势" "用户增长趋势" "产品分类占比"四张图，均使用 Recharts
- [x] Dashboard 页面在切换 7/30/90 天时正确请求对应 `days` 参数
- [x] 点击"生成模拟数据"按钮能成功调用后端并刷新图表

## P2 AI Business Analyst 模块

- [x] `POST /api/report/generate` 入参 `{ "days": 30 }` 返回 200
- [x] 响应体结构严格为 `{ "summary": string, "insights": [string], "suggestions": [string] }`
- [x] 销售表为空时返回 200 且 `summary` 含"暂无销售数据"字样，`insights` 与 `suggestions` 为空数组
- [x] `report_service` 内部先执行 SQL 聚合（总额/订单/客户/日均/增长率/Top 类别/Top 区域），再生成 Prompt 调用 LLM
- [x] Prompt 中明确要求"基于以上真实数据"且禁止编造
- [x] `insights` 数组长度 ≥ 3，`suggestions` 数组长度 ≥ 3
- [x] 旧 `POST /api/report` 接口仍可访问，行为不变
- [x] 前端 Report 页面有"生成本月经营报告"按钮，调用新端点并按三段式结构渲染

## P3 RAG 升级模块

- [x] `VectorStoreService.search_with_sources(query, k)` 返回 `[ {filename, document_id, score, content} ]`
- [x] `score` 归一化到 [0, 1]，保留两位小数
- [x] `POST /api/chat/with-sources` 响应为 `{ answer, sources: [{filename, document_id, score, content}] }`
- [x] 知识库为空时返回 `"知识库为空"` 提示，`sources` 为空数组
- [x] 上传 PDF/TXT 后再次调用 `with-sources`，`sources` 至少包含 1 条带分数的引用
- [x] 前端 ChatPage 在回答下方能折叠展示 sources 列表

## P4 工程化模块

- [x] 根目录存在 `docker-compose.yml`
- [x] 后端 `Dockerfile` 使用 `python:3.11-slim` 基础镜像，安装 `default-libmysqlclient-dev` 与 `gcc`
- [x] 前端 `Dockerfile` 多阶段构建（node 构建 → nginx 运行）
- [x] `frontend/nginx.conf` 将 `/api/` 反向代理到 `backend:8000`
- [x] `docker compose up -d` 一次性启动 mysql / backend / frontend 三个服务
- [x] backend 启动时自动执行 `python init_db.py` 创建表与种子数据
- [x] `http://localhost:8000/docs` 在容器启动后可访问
- [x] `http://localhost:5173` 在容器启动后可访问，并可通过前端登录后访问 Dashboard
- [x] MySQL 数据通过 volume 持久化，容器删除后数据不丢失

## P5 文档模块

- [x] `docs/architecture.md` 包含"系统架构图" "RAG 流程图" "数据流图"三段 mermaid 图
- [x] mermaid 图在 GitHub 预览中可正常渲染
- [x] `docs/interview-guide.md` 含 5 个章节：项目背景、技术选型原因、RAG 实现原理、FAISS 原理、面试高频问题
- [x] 面试题数量 ≥ 10 道，每道有要点参考
- [x] 两份 markdown 文档语言为中文，与用户需求一致
