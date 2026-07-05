# Enterprise AI Assistant

企业级AI知识问答与数据分析平台

## 项目简介

Enterprise AI Assistant 是一个面向企业内部员工使用的AI助手系统，提供知识问答、数据分析和智能报告生成等功能。该项目采用现代化的前后端分离架构，集成了大语言模型和向量检索技术，为企业提供智能化的知识管理和数据分析解决方案。

## 功能特性

### 1. 用户认证模块
- 用户注册与登录
- JWT Token 身份认证
- 基于角色的访问控制
- 安全的密码哈希存储

### 2. 知识库模块
- 支持 PDF、TXT 格式文档上传
- 自动文档解析与文本提取
- 智能文本切分（Chunking）
- 文本向量化与 FAISS 向量存储
- 高效的语义检索能力

### 3. AI 问答模块
- 基于 RAG（检索增强生成）的智能问答
- 知识库内容语义检索
- 大语言模型生成专业回答
- 支持上下文理解

### 4. Dashboard 数据看板
- 企业销售数据总览
- 关键指标实时展示（销售额、订单数、客户数）
- 30天趋势图表可视化
- 数据图表展示（基于 Recharts）

### 5. AI 分析报告模块
- 自动生成业务数据分析报告
- 数据摘要与趋势分析
- AI 智能洞察与建议
- 可导出的分析报告

## 技术栈

### 后端
- **框架**: FastAPI - 高性能的 Python Web 框架
- **ORM**: SQLAlchemy 2.0 - 成熟的 Python ORM
- **数据库**: MySQL 8.0+ - 关系型数据库
- **认证**: JWT (JSON Web Token)
- **数据验证**: Pydantic v2

### AI 模块
- **大语言模型**: OpenAI 兼容 API
- **框架**: LangChain - LLM 应用开发框架
- **向量数据库**: FAISS - Facebook 向量相似度搜索库
- **Embedding**: OpenAI Embedding API

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS
- **数据可视化**: Recharts
- **状态管理**: React Hooks
- **路由**: React Router

## 项目结构

```
enterprise-ai-assistant/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 数据模型
│   │   ├── services/          # 业务逻辑层
│   │   ├── core/              # 核心配置
│   │   └── utils/             # 工具函数
│   ├── uploads/               # 上传文件存储
│   ├── faiss_index/           # FAISS 向量索引
│   ├── requirements.txt       # Python 依赖
│   ├── .env.example          # 环境变量示例
│   └── init_db.py            # 数据库初始化脚本
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # 通用组件
│   │   ├── pages/            # 页面组件
│   │   ├── services/         # API 服务
│   │   ├── types/            # TypeScript 类型定义
│   │   └── hooks/            # 自定义 Hooks
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # 文档目录
└── README.md                   # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- npm 或 yarn

### 后端部署

1. **克隆项目**
```bash
git clone <repository-url>
cd enterprise-ai-assistant/backend
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置信息
```

5. **初始化数据库**
```bash
python init_db.py
```

6. **启动后端服务**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动
API 文档: http://localhost:8000/docs

### 前端部署

1. **进入前端目录**
```bash
cd ../frontend
```

2. **安装依赖**
```bash
npm install
# 或
yarn install
```

3. **启动开发服务器**
```bash
npm run dev
# 或
yarn dev
```

前端应用将在 http://localhost:5173 启动

## API 接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 知识库接口
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 获取文档列表
- `DELETE /api/documents/{id}` - 删除文档

### AI 问答接口
- `POST /api/chat` - AI 问答

### Dashboard 接口
- `GET /api/dashboard` - 获取 Dashboard 数据

### 分析报告接口
- `POST /api/report` - 生成 AI 分析报告

## 配置说明

### 环境变量 (.env)

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | MySQL 数据库连接地址 | mysql+pymysql://root:password@localhost:3306/enterprise_ai |
| SECRET_KEY | JWT 加密密钥 | your-secret-key-change-in-production |
| ALGORITHM | JWT 加密算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间（分钟） | 30 |
| OPENAI_API_KEY | OpenAI API Key | sk-xxx |
| OPENAI_API_BASE | OpenAI API Base URL | https://api.openai.com/v1 |
| OPENAI_MODEL | 使用的模型名称 | gpt-3.5-turbo |
| EMBEDDING_MODEL | Embedding 模型名称 | text-embedding-ada-002 |
| FAISS_INDEX_PATH | FAISS 索引存储路径 | ./faiss_index |
| UPLOAD_DIR | 上传文件存储路径 | ./uploads |

## 开发规范

### 后端开发规范
- 遵循 PEP 8 代码风格
- 使用类型注解（Type Hints）
- API 路由统一在 `app/api/` 目录下
- 业务逻辑封装在 `app/services/` 中
- 数据库模型定义在 `app/models/` 中
- Pydantic Schema 定义在 `app/schemas/` 中

### 前端开发规范
- 使用 TypeScript 类型定义
- 组件采用函数式组件 + Hooks
- 样式使用 TailwindCSS 工具类
- API 请求统一封装在 `services/` 中
- 通用组件放在 `components/` 目录
- 页面组件放在 `pages/` 目录

## 许可证

MIT License
