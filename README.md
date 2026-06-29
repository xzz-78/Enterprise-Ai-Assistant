# AI Business Assistant

企业级 AI 智能业务助手系统

## 项目简介

AI Business Assistant 是一个结合 RAG、数据分析和 AI Agent 的企业级智能助手。

支持：

- 企业知识库问答
- 文档检索
- 数据分析
- Agent 路由
- 管理后台
- 用户权限管理

---

## Features

### RAG 知识库

- PDF 上传
- Word 上传
- 文档切片
- 向量检索
- 引用来源

### 数据分析

- CSV 上传
- Excel 上传
- Pandas 分析
- 自动生成图表

### AI Agent

自动判断：

- 知识库查询
- 数据分析请求
- 通用问答

### 管理后台

- 用户管理
- 数据集管理
- 知识库管理
- 聊天记录管理

---

## Tech Stack

### Frontend

- Next.js
- React
- TailwindCSS
- shadcn/ui

### Backend

- FastAPI
- PostgreSQL

### AI

- Ollama
- ChromaDB
- Pandas

---

## Architecture

```text
User
 ↓
Frontend (Next.js)
 ↓
FastAPI
 ├── RAG Service
 ├── Agent Router
 ├── Data Analysis
 ↓
PostgreSQL
 ↓
ChromaDB
```

---

## Development Roadmap

- [x] Create Repository
- [ ] Project Structure
- [ ] RAG Module
- [ ] Data Analysis Module
- [ ] Agent Router
- [ ] Admin Dashboard
- [ ] RBAC Permission System
- [ ] Cloud Deployment

---

## License

MIT
