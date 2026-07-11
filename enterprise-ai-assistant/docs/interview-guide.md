# Enterprise AI Assistant 面试指南

> 本项目展示了 FastAPI + React + RAG + FAISS + LangChain 全栈能力。本文整理面试高频问题与参考要点。

## 1. 项目背景

- **项目名称**：Enterprise AI Assistant
- **定位**：企业级 AI 知识助手 + 销售分析平台
- **目标用户**：内部员工（知识检索）、管理者（销售看板与经营报告）
- **核心价值**：降低知识检索成本 + 数据驱动业务决策
- **技术栈**：FastAPI、React 18 + TypeScript、Vite、LangChain、FAISS、OpenAI、MySQL、Recharts、Docker

## 2. 技术选型原因

### 2.1 为什么用 FastAPI？
- **异步支持**（async/await）性能高，单进程可处理大量并发请求。
- **自动 OpenAPI 文档**：基于 Pydantic 自动生成 Swagger UI / ReDoc，省去手写文档。
- **Pydantic 数据校验**：声明式 schema 即可完成入参出参校验，类型注解友好。
- **类型注解友好**：与 `mypy` 配合好，IDE 智能提示完善。

### 2.2 为什么用 React + TypeScript？
- **组件化、复用性强**：UI 拆成可组合的组件，复杂页面也能清晰维护。
- **TypeScript 提供静态类型保护**：编译期就能发现类型错误，减少线上 bug。
- **Vite 启动快、HMR 体验好**：本地开发秒级热更新，提升开发效率。

### 2.3 为什么用 FAISS？
- **Meta 开源、性能强**：工业级 C++ 实现，单机检索速度极快。
- **支持亿级向量检索**：在合适索引下可处理超大规模数据。
- **本地文件即可运行，零运维**：无需额外服务，单文件即可落地。
- **多种索引算法**（Flat / IVF / HNSW）：可按数据规模灵活切换。

### 2.4 为什么用 LangChain？
- **封装文档加载、切分、Embedding 全流程**：开箱即用，避免重复造轮子。
- **抽象 LLM 调用，统一多家模型**：OpenAI、Azure、Anthropic 一套接口切换。
- **大量 PromptTemplate 复用**：模板化管理 prompt，便于实验和版本化。

### 2.5 为什么用 Recharts？
- **基于 React，组件化**：与 React 生态无缝衔接，写法符合 React 习惯。
- **声明式 API，上手快**：用 JSX 描述图表，无需手写 canvas/SVG。
- **内置 Tooltip、Legend、响应式**：交互与响应式开箱即用。

### 2.6 为什么用 MySQL？
- **成熟稳定**：互联网公司事实标准，运维生态成熟。
- **支持事务、复杂查询**：满足业务侧 join / group by / 索引等需求。
- **与 SQLAlchemy 配合 ORM**：用 Python 对象操作数据库，开发效率高。

## 3. RAG 实现原理

### 3.1 什么是 RAG？
**检索增强生成**（Retrieval-Augmented Generation）：先从知识库检索相关内容，再让 LLM 基于检索内容生成回答。相比让 LLM 直接回答，RAG 的优势是：

- 解决 LLM 知识陈旧、私有数据不可用的问题。
- 显著降低"幻觉"（Hallucination）概率。
- 回答可附带来源（sources），可解释、可追溯。

### 3.2 文档处理流程
- **加载**：`PyPDFLoader` / `TextLoader` 提取原始文本。
- **切分**：`RecursiveCharacterTextSplitter`，按字符递归按 `["\n\n", "\n", " ", ""]` 切分，`chunk_size=1000, overlap=200`。
- **向量化**：OpenAI `text-embedding-ada-002`（1536 维）。
- **存储**：`FAISS IndexFlatL2`，同时将 `Document` 的 `page_content` 与 `metadata` 持久化。

### 3.3 检索流程
- **Query → Embedding → FAISS 检索 Top-K**。
- FAISS 返回 L2 距离（越小越相似）。
- **距离转相似度**：`1 / (1 + distance)`，归一化到 `(0, 1]`。
- Top-K 文档拼成 `context`，供 Prompt 注入。

### 3.4 Prompt 组装
模板示意：

```
你是企业知识助手，根据以下上下文回答用户问题。
上下文：{context}
问题：{question}
回答：
```

**约束**：

- 未找到相关内容时直接说"不知道"，**禁止编造**。
- 回答尽量引用来源（来源文件名 / chunk id）。
- 中文回答为主，与用户提问语言保持一致。

## 4. FAISS 原理

### 4.1 什么是 FAISS？
**Facebook AI Similarity Search**，Meta 开源的向量检索库，是工业界最常用的 ANN 库之一。

### 4.2 索引类型
- **`IndexFlatL2`**：精确 L2 距离，暴力搜索；小数据首选，结果精确。
- **`IndexIVFFlat`**：倒排索引，先聚类再搜索；速度快但近似。
- **`IndexHNSW`**：基于图的近似最近邻；查询极快，构建慢、内存大。
- **`IndexPQ`**：乘积量化，压缩存储；适合超大规模、内存敏感场景。

### 4.3 本项目为什么用 IndexFlatL2？
- **数据量小**（< 10w 向量），精确检索可接受。
- **实现简单，零配置**：无需训练聚类中心或构建图。
- **未来可升级到 IndexIVFFlat** 处理更大规模，代码改动小。

### 4.4 L2 距离 vs 余弦相似度
- **L2 距离**：欧氏距离，越小越相似；对向量长度敏感。
- **余弦相似度**：方向相似度，对长度不敏感；取值 `[-1, 1]`。
- 本项目用 **L2 距离 + `1/(1+d)` 转换**，等价于"距离越小 → 相似度越大"，实现简单直观。

## 5. 面试高频问题

### Q1：请介绍一下你这个项目的整体架构？
**要点**：前端 React + Nginx 反代 + FastAPI + MySQL/FAISS + OpenAI；分四层（前端 / 网关 / 业务 / 数据）。前端通过 Nginx `/api` 反代调用 FastAPI，FastAPI 内部按 `api / services / schemas / models` 分层；MySQL 存结构化数据，FAISS 存文档向量，OpenAI 同时提供 Embedding 与 Chat 能力。

### Q2：什么是 RAG？为什么需要 RAG？
**要点**：检索增强生成（Retrieval-Augmented Generation）；解决 LLM 知识陈旧、幻觉问题；让 LLM 基于私有知识回答。RAG 先用向量检索找出与问题相关的文档片段，再让 LLM 基于这些片段生成答案，回答更准确、可追溯。

### Q3：文档怎么切分的？为什么 `chunk_size=1000 overlap=200`？
**要点**：`RecursiveCharacterTextSplitter` 递归切分；1000 字符保证语义完整；200 重叠避免边界信息丢失。递归分隔符按 `["\n\n", "\n", " ", ""]` 优先级从大到小尝试，优先保留段落和句子结构；overlap 保证跨块语境连贯。

### Q4：Embedding 模型选型？
**要点**：`text-embedding-ada-002` 1536 维；可替换开源 BGE / M3E 节省成本。本项目用 OpenAI 闭源模型以保证质量；如对成本或数据合规有要求，可改用 `BAAI/bge-large-zh`、`moka-ai/m3e-base` 等开源中文 Embedding，LangChain 切换一行代码。

### Q5：FAISS 与 Milvus / Pinecone 的区别？
**要点**：FAISS 离线本地库，Milvus / Pinecone 分布式云服务；本项目数据量小选 FAISS；未来扩展用 Milvus。FAISS 优势是零运维、单文件落地，劣势是不支持分布式与多用户隔离；Milvus 适合大规模生产，Pinecone 是 SaaS 化的向量数据库。

### Q6：JWT 鉴权流程？
**要点**：登录签发 token → 前端存 localStorage → 每次请求带 `Authorization: Bearer <token>` 头 → 后端解析 `user_id`。JWT 优势是无状态，后端不需要存 session，便于水平扩展；劣势是 token 一旦签发难以主动失效，需要靠短过期 + 刷新 token 机制。

### Q7：SQL 聚合与 Python 聚合的取舍？
**要点**：数据量大时 SQL 聚合性能更好（数据库层有优化），Python 聚合更灵活。本项目销售看板的"按月 / 按品类"聚合直接用 `GROUP BY`，让 MySQL 利用索引完成；AI 报告生成则是先 SQL 取聚合结果、再 Python 组装为 prompt 输入，发挥各自优势。

### Q8：为什么用 Recharts 而不是 ECharts / AntV？
**要点**：React 生态原生支持；声明式 API；本项目图表需求不复杂，Recharts 足够。ECharts 偏命令式，配置项多；AntV 偏向数据可视化专业场景。Recharts 与 React 心智一致，对于趋势线、占比环、柱状图等常见图表能几行代码搞定。

### Q9：Docker 多阶段构建的好处？
**要点**：减小最终镜像体积（前端构建产物进 nginx 而非 node 镜像）；构建缓存复用。多阶段构建将 `npm run build` 放在一个阶段，把 `dist/` 拷到 nginx 镜像，最终镜像只有静态文件，没有 node_modules；后端同理，可用 slim 基础镜像减少体积。

### Q10：AI 报告生成为什么不直接让 LLM 编造？
**要点**：必须基于真实统计；用 SQL 聚合 → Prompt 注入数据 → LLM 解读；否则会出现幻觉。LLM 没有真实业务数据，直接问"上月销售怎么样"会编造数字。正确做法是先用 SQL 算出指标，把"硬数据"塞进 prompt，让 LLM 负责"解读与建议"，从根源上避免幻觉。

### Q11：如果知识库特别大（百万向量）FAISS 性能不够怎么办？
**要点**：升级到 `IndexIVFFlat` 或 `IndexHNSW`；切分到多机（Milvus / Pinecone）；量化压缩（PQ）。`IVF` 用倒排索引减少搜索范围，`HNSW` 用图结构进一步提速；`PQ` 把 1536 维向量压成几十字节，内存占用降一个数量级；分布式方案则用 Milvus / Pinecone。

### Q12：前后端如何做反向代理？为什么？
**要点**：Nginx 反代 `/api` 到 `backend:8000`；避免前端 CORS；统一入口；可加 gzip 压缩。Nginx 把 `/api/*` 请求转发到后端容器，前端只暴露 5173 一个端口；这样浏览器看是同源请求，没有跨域问题；同时也方便加 gzip、限流、灰度等网关能力。

### Q13：Pydantic 2 的 `model_validator` 与 `field_validator` 区别？
**要点**：`field_validator` 验证单个字段；`model_validator` 验证整个模型（如交叉字段）。例如"结束日期必须晚于开始日期"这种跨字段约束必须用 `model_validator(mode="after")`；而"邮箱必须合法"这种单字段约束用 `field_validator` 即可。

### Q14：解释一下 L2 距离转相似度的公式 `1/(1+d)`？
**要点**：`d ≥ 0`，`1/(1+d) ∈ (0, 1]`；`d=0` 相似度=1；`d→∞` 相似度→0；单调递减。这个变换把 L2 距离映射到 `(0, 1]`，值越大越相似；`+1` 是为了避免除零，平滑性比 `1/d` 更好，前端展示更直观。

### Q15：业务报告里"增长率"怎么算？
**要点**：后半段均值 - 前半段均值 / 前半段均值；避免被单日异常拉偏。本项目销售报告按"前 15 天均值 vs 后 15 天均值"算增长率，而不是"首日 vs 末日"；用均值抗单日异常，比绝对值差更稳健，也方便业务方做归因分析。
