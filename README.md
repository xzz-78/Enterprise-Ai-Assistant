# Enterprise AI Assistant

企业级 AI 知识问答与数据分析平台 — 基于 RAG 架构的知识库系统，支持多格式文档解析、中文智能切分、语义检索与 AI 分析报告。

## 项目简介

Enterprise AI Assistant 是一个面向企业内部员工的 AI 助手系统，提供知识问答、文档管理、数据看板和智能报告生成等核心能力。项目采用前后端分离架构，集成大语言模型与 FAISS 向量检索，通过 RAG（检索增强生成）技术将企业内部知识转化为可对话的智能服务，帮助员工快速获取信息、洞察业务数据。

知识库模块支持 PDF、DOCX、PPTX、XLSX、TXT、Markdown、HTML、CSV、EPUB 等十余种文档格式，内置中文友好的文本切分策略和结构化内容语义切分，具备文件哈希去重、原子性索引保存和按元数据删除向量等企业级特性。

## 功能特性

### 知识库管理
- **多格式支持**：支持 PDF、DOCX、PPTX、XLSX、TXT、MD、HTML、CSV、EPUB、RTF、ODT 等十余种文档格式，基于 Unstructured 统一解析器
- **中文智能切分**：针对中文优化的分隔符优先级（段落 → 换行 → 句号/感叹号/问号/分号 → 逗号 → 空格 → 字符），提升检索精度
- **语义切分**：自动检测文档中的表格、代码块等结构化内容，启用 SemanticChunker 按语义边界切块，避免破坏结构
- **文件去重与更新**：通过 SHA256 文件哈希检测重复文件，同一文档支持更新上传（先删后加），避免冗余占用
- **原子性索引保存**：先写临时目录再原子替换，防止中途崩溃导致 FAISS 索引损坏
- **向量索引删除**：删除文档时同步清理向量索引，通过全量重建实现按元数据过滤删除

### RAG 智能问答
- **检索增强生成**：基于 FAISS 向量相似度检索 Top-K 相关片段，注入 Prompt 后由 LLM 生成精准回答
- **来源引用**：回答附带来源文档、相关片段和相似度分数（4 位小数精度），方便溯源
- **上下文理解**：支持多轮对话，基于历史上下文生成连贯回答

### 数据看板
- **关键指标**：销售额、订单数、客户数等核心业务指标总览
- **趋势可视化**：30 天销售趋势图表，基于 Recharts 实现交互式折线图、柱状图
- **模拟数据生成**：一键生成演示数据，快速体验看板功能

### AI 分析报告
- **自动分析**：基于销售数据自动生成业务分析报告
- **智能洞察**：AI 生成趋势判断、问题诊断和 actionable 建议
- **结构化输出**：数据摘要 + AI 分析 + 建议清单，一键获取

### 用户认证
- **JWT 认证**：基于 JSON Web Token 的无状态身份认证
- **密码安全**：bcrypt 哈希存储，保障用户密码安全
- **角色隔离**：用户只能访问和管理自己上传的文档

## 技术栈

### 后端
- **Web 框架**：FastAPI 0.110 — 高性能异步 Python Web 框架，自动生成 OpenAPI 文档
- **ORM**：SQLAlchemy 2.0 — 成熟的 Python ORM，支持异步查询
- **数据库**：MySQL 8.0+ — 关系型数据库，存储用户、文档、业务数据
- **认证**：JWT (python-jose) + bcrypt — 安全的身份认证与密码哈希
- **数据验证**：Pydantic v2 — 严格的类型校验与序列化
- **数据库迁移**：Alembic — 数据库版本管理工具

### AI / 向量检索
- **大语言模型**：OpenAI 兼容 API (GPT-3.5/4、Azure OpenAI、vLLM 等)
- **LLM 框架**：LangChain 0.2 — 统一的 LLM 应用开发框架
- **向量数据库**：FAISS 1.12 — Facebook 开源向量相似度搜索库
- **Embedding**：OpenAI text-embedding-ada-002 (1536 维)
- **文档解析**：Unstructured — 统一文档解析器，支持多种格式
- **Office 解析**：python-docx / python-pptx / openpyxl — Word / PPT / Excel 解析
- **语义切分**：langchain-experimental SemanticChunker — 基于 Embedding 的语义边界切分
- **HTML 解析**：BeautifulSoup4 + lxml — HTML 内容提取

### 前端
- **框架**：React 18 + TypeScript — 类型安全的组件化开发
- **构建工具**：Vite 5 — 极速开发与构建体验
- **样式**：TailwindCSS 3 — 原子化 CSS，快速构建现代化 UI
- **图表**：Recharts — 基于 React 的声明式图表库
- **路由**：React Router v6 — 客户端路由管理
- **HTTP**：Axios — HTTP 请求库
- **图标**：lucide-react — 轻量美观的图标库

### 部署
- **容器化**：Docker + Docker Compose — 一键部署完整环境
- **反向代理**：Nginx — 前端静态资源托管 + API 反向代理
- **数据持久化**：Docker Volume — MySQL 数据、上传文件、FAISS 索引持久化

## 项目结构

```
enterprise-ai-assistant/
├── backend/                          # FastAPI 后端服务
│   ├── app/
│   │   ├── api/                      # API 路由层
│   │   │   ├── auth.py              # 认证接口
│   │   │   ├── documents.py         # 文档管理接口
│   │   │   ├── chat.py              # AI 问答接口
│   │   │   ├── dashboard.py         # 数据看板接口
│   │   │   └── report.py            # 分析报告接口
│   │   ├── core/                     # 核心配置
│   │   │   ├── config.py            # 环境变量配置
│   │   │   ├── database.py          # 数据库连接
│   │   │   └── security.py          # 安全工具（JWT/密码）
│   │   ├── models/                   # SQLAlchemy ORM 模型
│   │   ├── schemas/                  # Pydantic 数据模型
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── vector_service.py    # 向量存储服务
│   │   │   ├── document_service.py  # 文档服务
│   │   │   ├── chat_service.py      # 问答服务
│   │   │   ├── dashboard_service.py # 看板服务
│   │   │   └── report_service.py    # 报告服务
│   │   ├── utils/                    # 工具函数
│   │   └── main.py                   # FastAPI 应用入口
│   ├── uploads/                      # 上传文件存储目录
│   ├── faiss_index/                  # FAISS 向量索引目录
│   ├── init_db.py                    # 数据库初始化脚本
│   ├── requirements.txt              # Python 依赖
│   ├── .env.example                  # 环境变量示例
│   ├── Dockerfile                    # 后端 Docker 镜像
│   └── .dockerignore
├── frontend/                         # React 前端应用
│   ├── src/
│   │   ├── pages/                    # 页面组件
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── ChatPage.tsx
│   │   │   ├── DocumentsPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   └── ReportPage.tsx
│   │   ├── components/               # 通用组件
│   │   │   └── Layout.tsx
│   │   ├── services/                 # API 服务封装
│   │   ├── hooks/                    # 自定义 Hooks
│   │   ├── types/                    # TypeScript 类型定义
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── nginx.conf                    # Nginx 配置
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── Dockerfile                    # 前端 Docker 镜像
│   └── .dockerignore
├── docs/                             # 项目文档
│   ├── architecture.md               # 架构设计文档
│   ├── api.md                        # API 接口文档
│   └── interview-guide.md
├── docker-compose.yml                # Docker Compose 编排
├── .env.example                      # 根目录环境变量示例
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- npm 或 yarn
- Docker & Docker Compose（推荐）

### 方式一：Docker Compose 一键启动（推荐）

确保已安装 Docker 与 Docker Compose，然后执行：

```bash
# 1. 克隆项目
git clone <repository-url>
cd enterprise-ai-assistant

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY 等配置

# 3. 一键启动
docker compose up -d

# 4. 访问应用
# 前端: http://localhost:5173
# 后端 API 文档: http://localhost:8000/docs
# MySQL: localhost:3306 (user=eai, password=eaipass)
```

默认测试账号：`admin` / `admin123`

### 方式二：本地开发启动

#### 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入数据库连接、OpenAI Key 等

# 5. 初始化数据库（建表 + 种子数据）
python init_db.py

# 6. 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动，API 文档：http://localhost:8000/docs

#### 前端部署

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install
# 或 yarn install

# 3. 启动开发服务器
npm run dev
# 或 yarn dev
```

前端应用将在 http://localhost:5173 启动

## 配置说明

### 环境变量 (.env)

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| **数据库配置** | | |
| DATABASE_URL | MySQL 数据库连接地址 | mysql+pymysql://root:password@localhost:3306/enterprise_ai |
| **JWT 配置** | | |
| SECRET_KEY | JWT 加密密钥（生产环境务必修改） | your-secret-key-change-in-production |
| ALGORITHM | JWT 加密算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间（分钟） | 30 |
| **OpenAI 配置** | | |
| OPENAI_API_KEY | OpenAI API Key | sk-your-openai-api-key |
| OPENAI_API_BASE | OpenAI API Base URL（兼容其他服务） | https://api.openai.com/v1 |
| OPENAI_MODEL | 使用的对话模型名称 | gpt-3.5-turbo |
| EMBEDDING_MODEL | Embedding 模型名称 | text-embedding-ada-002 |
| **FAISS 配置** | | |
| FAISS_INDEX_PATH | FAISS 索引存储路径 | ./faiss_index |
| **文档解析与切分** | | |
| CHUNK_SIZE | 文本切块大小（字符数） | 1000 |
| CHUNK_OVERLAP | 块间重叠大小（字符数） | 200 |
| USE_SEMANTIC_SPLITTING | 是否启用语义切分（表格/代码） | true |
| SEMANTIC_BREAKPOINT_THRESHOLD | 语义切分阈值（百分位数） | 75 |
| **文件上传配置** | | |
| UPLOAD_DIR | 上传文件存储路径 | ./uploads |
| MAX_UPLOAD_SIZE | 单文件最大大小（字节） | 10485760 (10MB) |
| **服务配置** | | |
| HOST | 服务监听地址 | 0.0.0.0 |
| PORT | 服务监听端口 | 8000 |

## API 接口概览

完整接口文档请访问启动后的 `/docs`（Swagger UI）或 `/redoc`，或查看 [docs/api.md](docs/api.md)。

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录（获取 JWT） |
| GET | `/api/auth/me` | 获取当前用户信息 |

### 知识库接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/documents/upload` | 上传文档（多格式支持） |
| GET | `/api/documents` | 获取文档列表 |
| GET | `/api/documents/{id}` | 获取文档详情 |
| DELETE | `/api/documents/{id}` | 删除文档（含向量索引） |

### AI 问答接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | AI 问答 |
| POST | `/api/chat/with-sources` | AI 问答（带来源引用） |

### 数据看板接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard` | 获取看板统计数据与趋势 |
| POST | `/api/dashboard/generate-mock-data` | 生成模拟销售数据 |

### 分析报告接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/report` | 生成 AI 业务分析报告 |

## 架构设计

系统采用经典的前后端分离 + 多层架构，主要分为：

- **前端层**：React 18 + TypeScript + Vite，Nginx 托管静态资源并反向代理 API
- **后端业务层**：FastAPI + SQLAlchemy，按 api/services/schemas/models 四层分层
- **数据层**：MySQL 存储结构化数据，FAISS 本地文件存储文档向量
- **AI 服务层**：OpenAI 兼容 API 提供 Embedding 与 Chat 能力

核心 RAG 流程：文档上传 → Unstructured 解析 → 中文智能切分（结构化内容用语义切分）→ Embedding 向量化 → FAISS 存储 → 用户提问 → 相似度检索 → Prompt 拼装 → LLM 生成回答 → 返回结果与来源。

更多架构细节请参考 [docs/architecture.md](docs/architecture.md)。

## 开发规范

### 后端开发规范
- 遵循 PEP 8 代码风格
- 使用类型注解（Type Hints）
- API 路由统一放在 `app/api/` 目录下，一个模块一个文件
- 业务逻辑封装在 `app/services/` 中，不直接写在路由层
- 数据库模型定义在 `app/models/`，Pydantic Schema 定义在 `app/schemas/`
- 配置项通过 `app/core/config.py` 统一管理，从环境变量读取

### 前端开发规范
- 使用 TypeScript 类型定义，避免 any
- 组件采用函数式组件 + Hooks
- 样式使用 TailwindCSS 工具类
- API 请求统一封装在 `services/` 中
- 通用组件放在 `components/` 目录，页面组件放在 `pages/` 目录

## 许可证

MIT License
