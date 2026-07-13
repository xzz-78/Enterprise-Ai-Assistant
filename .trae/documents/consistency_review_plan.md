# 项目一致性审查计划

## 一、审查结论

对 Enterprise AI Assistant 项目进行全量代码审查后，共发现 **8 类 15 项** 不一致的处理方式，按严重程度分级如下：

---

## 二、不一致问题清单

### 🔴 高优先级（影响功能一致性 / 存在重复逻辑）

#### 1. LLM 初始化模式不统一

| 服务 | 初始化模式 | 文件位置 |
|------|-----------|---------|
| `ChatService` | 延迟初始化（`_get_llm()` 懒加载） | [chat_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/chat_service.py#L44-L52) |
| `VectorStoreService` | 延迟初始化（`_get_embeddings()` 懒加载） | [vector_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/vector_service.py#L53-L77) |
| `ReportService` | 立即初始化（`__init__` 中直接创建） | [report_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/report_service.py#L25-L33) |
| `BusinessReportService` | 立即初始化（`__init__` 中直接创建） | [report_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/report_service.py#L300-L308) |

**问题**：`report_service.py` 中的两个服务在模块导入时就创建 LLM 实例，如果 `OPENAI_API_KEY` 缺失会导致应用启动崩溃，与 chat/vector 服务的延迟初始化设计不一致。

---

#### 2. end_date 计算方式不统一

| 函数 | end_date 来源 | 文件位置 |
|------|-------------|---------|
| `get_sales_trend` | `db.query(func.max(Sale.date)).scalar()`（DB 最后一天） | [dashboard_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/dashboard_service.py#L72) |
| `_get_sales_data` | `db.query(func.max(Sale.date)).scalar()`（DB 最后一天） | [report_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/report_service.py#L46) |
| `_sql_aggregate` | `date.today()`（当前日期） | [report_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/report_service.py#L342) |

**问题**：`BusinessReportService._sql_aggregate` 使用 `date.today()` 作为结束日期，而 Dashboard 和旧版 ReportService 都使用数据库中最后一条销售记录的日期。这会导致：
- 如果数据停留在几天前，报告中的"窗口天数"会包含大量零值日期
- 增长率计算不准确（因为后半段可能全是零）

---

#### 3. 报告服务重复（ReportService vs BusinessReportService）

| 类名 | 用途 | 重复逻辑 |
|------|------|---------|
| `ReportService` | P0 兼容版本，返回 `{data_summary, ai_analysis, recommendations}` | 数据聚合、增长率计算、格式化数据、LLM 调用 |
| `BusinessReportService` | P2 新版本，返回 `{summary, insights, suggestions}` | 数据聚合、增长率计算、Prompt 构建、LLM 调用 |

**问题**：两个类存在大量重复逻辑：
- 都在做销售数据聚合（一个用 Python 循环 sum，一个用 SQL 聚合）
- 都在计算增长率（前半段 vs 后半段）
- 都在构建 Prompt + 调用 LLM
- 都有"空数据返回提示"的兜底逻辑

`ReportService` 是旧版实现，`BusinessReportService` 是新版工程化实现。旧版在 API 层仍有端点（`POST /api/report`），但前端实际使用的是新版端点（`POST /api/report/generate`）。

---

### 🟡 中优先级（代码风格 / 架构一致性）

#### 4. 服务层风格不统一：函数式 vs 类式

| 服务文件 | 风格 | 全局实例 |
|---------|------|---------|
| `auth_service.py` | 函数式（纯函数） | 无 |
| `dashboard_service.py` | 函数式（纯函数） | 无 |
| `document_service.py` | 函数式（纯函数） | 无 |
| `chat_service.py` | 类式（`ChatService` 类） | `chat_service` |
| `vector_service.py` | 类式（`VectorStoreService` 类） | `vector_store_service` |
| `report_service.py` | 类式（两个类） | `report_service` + `business_report_service` |

**问题**：同一项目的 service 层混用两种风格。有状态的服务（需要 LLM/向量库实例）用类式，无状态的服务（纯数据库操作）用函数式。这本身是合理的，但缺乏明确的约定和文档说明。

---

#### 5. API 路由错误处理方式不统一

| 路由文件 | 错误处理方式 |
|---------|------------|
| `auth.py` | service 层直接抛 `HTTPException`，router 层不捕获 |
| `chat.py` | router 层 try/catch，捕获后抛 `HTTPException(500)` |
| `dashboard.py` | 部分端点 try/catch，部分不捕获 |
| `documents.py` | service 层直接抛 `HTTPException`，router 层不捕获 |
| `report.py` | router 层 try/catch（仅旧端点，新端点在 service 层兜底） |

**问题**：
- 有的在 service 层抛 `HTTPException`（HTTP 框架类混入业务层）
- 有的在 router 层 try/catch
- `BusinessReportService` 内部兜底返回 dict，不抛异常

---

#### 6. 前端服务文件导出风格不统一

| 服务文件 | 导出方式 | 函数命名 |
|---------|---------|---------|
| `auth.ts` | 命名导出 | `login`, `register`, `getCurrentUser` |
| `chat.ts` | 命名导出 | `chat`, `chatWithSources` |
| `dashboard.ts` | 命名导出 | `getDashboardData`, `getSummary`, `getTrend`... |
| `document.ts` | 命名导出 | `getDocuments`, `uploadDocument`, `deleteDocument`... |
| `report.ts` | 命名导出 | `generateReport`, `generateBusinessReport` |

**说明**：前端服务文件风格基本一致（都是命名导出），但函数命名前缀不统一：有的用动词开头（`get/delete/upload/generate`），有的直接用名词（`chat`）。

---

### 🟢 低优先级（细节 / 代码整洁度）

#### 7. import 位置不统一

- [report_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/report_service.py#L212) `_generate_recommendations` 方法内部 `import re`（顶部已经 import 了）
- [document_service.py](file:///workspace/enterprise-ai-assistant/backend/app/services/document_service.py#L136) `_detect_zip_format` 函数内部 `import zipfile`（合理，因为只有这个函数用）

---

#### 8. 日志方式不统一

| 文件 | 日志方式 |
|------|---------|
| `document_service.py` | `logging.getLogger(__name__)` 标准 logger |
| `report_service.py` | `print()` 直接输出 |
| `chat_service.py` | 无日志 |
| `vector_service.py` | `print()` 直接输出 |

---

## 三、建议修复方案（按优先级）

### 高优先级修复

1. **统一 LLM 延迟初始化**：将 `ReportService` 和 `BusinessReportService` 改为延迟初始化模式，与 `ChatService` 保持一致
2. **统一 end_date 计算**：将 `BusinessReportService._sql_aggregate` 的 end_date 改为 DB 最后一天，与 Dashboard 保持一致
3. **评估移除旧版 ReportService**：确认前端是否完全不再使用 `POST /api/report` 端点，如果是，可以考虑标记为 deprecated 或移除

### 中优先级修复

4. **统一错误处理模式**：约定 service 层抛业务异常（自定义异常类），router 层统一捕获并转换为 HTTPException
5. **统一日志方式**：所有 service 都使用 `logging.getLogger(__name__)` 替代 `print()`

### 低优先级修复

6. **清理重复 import**：移除 `_generate_recommendations` 中冗余的 `import re`

---

## 四、涉及文件清单

| 文件 | 修改项数量 |
|------|-----------|
| `backend/app/services/report_service.py` | 高优：LLM 延迟初始化 + end_date 统一 |
| `backend/app/api/report.py` | 中优：评估旧端点是否保留 |
| `backend/app/services/chat_service.py` | 低优：添加 logger |
| `backend/app/services/vector_service.py` | 低优：print 改 logger |

---

## 五、风险说明

1. **end_date 变更**：可能影响现有报告的日期范围，需要确认业务需求是"以当前日期为基准"还是"以最后一条数据为基准"
2. **移除旧端点**：`POST /api/report` 如果有外部调用方，不能直接删除，需要先 deprecated
3. **延迟初始化**：如果有代码在模块导入阶段依赖 LLM 实例存在，需要调整
