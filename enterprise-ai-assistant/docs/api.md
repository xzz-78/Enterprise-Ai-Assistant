# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **数据格式**: JSON

---

## 认证接口

### 1. 用户注册

**POST** `/auth/register`

注册新用户账号。

**请求体**:
```json
{
  "username": "string (3-50字符)",
  "email": "string (邮箱格式)",
  "password": "string (6-100字符)"
}
```

**成功响应** (200):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**错误响应**:
- 400: 用户名或邮箱已存在

---

### 2. 用户登录

**POST** `/auth/login`

用户登录获取 JWT Token。使用 `application/x-www-form-urlencoded` 格式。

**请求体 (Form Data)**:
```
username: string
password: string
```

**成功响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**错误响应**:
- 401: 用户名或密码错误

---

### 3. 获取当前用户信息

**GET** `/auth/me`

获取当前登录用户的信息。需要认证。

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应** (200):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**错误响应**:
- 401: 未认证或 Token 无效

---

## 知识库接口

### 1. 上传文档

**POST** `/documents/upload`

上传文档到知识库，支持 PDF 和 TXT 格式。需要认证。

**请求头**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求体 (Form Data)**:
```
file: <文件>
```

**成功响应** (200):
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_time": "2024-01-01T00:00:00",
  "user_id": 1
}
```

**错误响应**:
- 400: 不支持的文件类型
- 413: 文件大小超过限制

---

### 2. 获取文档列表

**GET** `/documents`

获取当前用户的文档列表。需要认证。

**请求参数**:
- `skip` (可选): 跳过数量，默认 0
- `limit` (可选): 返回数量，默认 100

**成功响应** (200):
```json
{
  "total": 10,
  "documents": [
    {
      "id": 1,
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "upload_time": "2024-01-01T00:00:00",
      "user_id": 1
    }
  ]
}
```

---

### 3. 获取文档详情

**GET** `/documents/{doc_id}`

获取指定文档的详细信息。需要认证。

**路径参数**:
- `doc_id`: 文档 ID

**成功响应** (200):
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_time": "2024-01-01T00:00:00",
  "user_id": 1
}
```

**错误响应**:
- 404: 文档不存在

---

### 4. 删除文档

**DELETE** `/documents/{doc_id}`

删除指定文档。需要认证。

**路径参数**:
- `doc_id`: 文档 ID

**成功响应** (200):
```json
{
  "message": "文档删除成功"
}
```

**错误响应**:
- 404: 文档不存在

---

## AI 问答接口

### 1. AI 问答

**POST** `/chat`

基于知识库的智能问答。需要认证。

**请求体**:
```json
{
  "question": "公司请假制度是什么"
}
```

**成功响应** (200):
```json
{
  "answer": "根据公司规定，员工每年享有..."
}
```

---

### 2. AI 问答（带引用来源）

**POST** `/chat/with-sources`

AI 问答，同时返回参考的文档来源。需要认证。

**请求体**:
```json
{
  "question": "公司请假制度是什么"
}
```

**成功响应** (200):
```json
{
  "answer": "根据公司规定，员工每年享有...",
  "sources": [
    {
      "content": "员工手册 - 请假制度...",
      "metadata": {
        "document_id": 1,
        "filename": "员工手册.pdf"
      }
    }
  ]
}
```

---

## 数据看板接口

### 1. 获取 Dashboard 数据

**GET** `/dashboard`

获取销售数据统计和趋势。需要认证。

**请求参数**:
- `days` (可选): 趋势数据天数，默认 30，范围 7-365

**成功响应** (200):
```json
{
  "stats": {
    "total_revenue": 1000000.0,
    "total_orders": 5000,
    "total_customers": 3000
  },
  "trend": [
    {
      "date": "2024-01-01",
      "revenue": 50000.0,
      "orders": 100,
      "customers": 80
    }
  ]
}
```

---

### 2. 生成模拟数据

**POST** `/dashboard/generate-mock-data`

生成模拟销售数据（用于演示）。需要认证。

**请求参数**:
- `days` (可选): 生成数据天数，默认 90，范围 30-365

**成功响应** (200):
```json
{
  "message": "成功生成 90 条模拟销售数据",
  "count": 90
}
```

---

## AI 分析报告接口

### 1. 生成分析报告

**POST** `/report`

根据销售数据生成 AI 分析报告。需要认证。

**请求体**:
```json
{
  "days": 30
}
```

**成功响应** (200):
```json
{
  "data_summary": {
    "total_revenue": 1000000.0,
    "total_orders": 5000,
    "total_customers": 3000,
    "avg_daily_revenue": 33333.33,
    "revenue_growth_rate": 15.5
  },
  "ai_analysis": "根据最近30天的销售数据分析...",
  "recommendations": [
    "优化销售渠道...",
    "加强客户关系管理..."
  ]
}
```

---

## 错误响应格式

所有错误响应统一格式：
```json
{
  "detail": "错误描述信息"
}
```

## HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 无效 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 413 | 请求体过大 |
| 500 | 服务器内部错误 |
