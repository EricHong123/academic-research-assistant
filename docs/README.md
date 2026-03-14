# Academic Research Assistant (ARA)

基于 LangGraph 的学术文献智能搜索与分析系统

## 功能特性

- **多数据库搜索** - 同时查询 Web of Science、Scopus、PubMed、Google Scholar
- **布尔查询支持** - 支持 AND、OR、NOT 运算符和精确短语搜索
- **AI 相关性排序** - 基于语义嵌入、期刊质量、研究设计的智能排序
- **PDF 解析** - 自动提取研究类型、变量、样本量、统计值等结构化数据
- **RAG 对话** - 与文献进行对话，生成带引用的回答
- **趋势简报** - 自动追踪研究领域新论文，生成趋势报告
- **项目管理** - 组织和管理文献收藏
- **多格式导出** - 支持 BibTeX、RIS、CSV 格式导出

## 技术架构

```
┌─────────────────────────────────────────┐
│          Next.js Frontend               │
├─────────────────────────────────────────┤
│            FastAPI Backend              │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐  │
│  │ Search  │ │  Parse  │ │   RAG    │  │
│  │ Agent   │ │  Agent  │ │  Agent   │  │
│  └─────────┘ └─────────┘ └──────────┘  │
├─────────────────────────────────────────┤
│        LangGraph Orchestration           │
├─────────────────────────────────────────┤
│  Database Adapters (PubMed, WOS, etc.) │
├─────────────────────────────────────────┤
│   PostgreSQL  │  Redis  │  Pinecone   │
└─────────────────────────────────────────┘
```

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+ (前端)
- Redis (可选，用于缓存)
- PostgreSQL (可选，用于生产)

### 1. 克隆项目

```bash
cd /Users/erich
git clone <repo-url> academic-research-assistant
cd academic-research-assistant
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate   # Windows

# 或使用 conda
conda create -n ara python=3.11
conda activate ara
```

### 3. 安装依赖

```bash
# 后端依赖
pip install -e ".[dev]"

# 前端依赖 (可选)
cd frontend
npm install
cd ..
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API 密钥
```

`.env` 文件示例：

```env
# 应用配置
APP_NAME=Academic Research Assistant
DEBUG=true

# LLM 提供商 (至少选择一个)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 向量数据库 (可选)
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1

# 学术数据库 API (可选)
PUBMED_API_KEY=...
WOS_API_KEY=...
SCOPUS_API_KEY=...

# JWT 密钥 (生产环境请修改)
JWT_SECRET_KEY=your-secret-key-change-in-production

# 数据库 (可选，使用 SQLite 作为默认)
DATABASE_URL=sqlite+aiosqlite:///./ara.db
# 或 PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/ara

# Redis (可选)
REDIS_URL=redis://localhost:6379/0
```

### 5. 启动服务

#### 方式一：直接运行

```bash
# 启动后端 API (默认端口 8000)
python3 main.py

# 启动 Celery Worker (可选，用于异步任务)
python3 celery_worker.py
```

#### 方式二：Docker 运行

```bash
# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

服务地址：
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 前端: http://localhost:3000

## API 使用

### 搜索论文

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning AND healthcare",
    "databases": ["pubmed"],
    "filters": {
      "year_from": 2020,
      "year_to": 2024
    },
    "limit": 20
  }'
```

### 创建项目

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Research",
    "description": "Machine learning in healthcare"
  }'
```

### 导出 BibTeX

```bash
curl -X POST http://localhost:8000/api/export/bibtex \
  -H "Content-Type: application/json" \
  -d '{
    "papers": [
      {
        "title": "Sample Paper",
        "authors": ["Author A", "Author B"],
        "year": 2023,
        "journal": "Nature",
        "doi": "10.1234/test"
      }
    ]
  }'
```

### RAG 对话

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "your-project-id",
    "message": "What are the main findings about machine learning in healthcare?"
  }'
```

## 项目结构

```
academic-research-assistant/
├── main.py                    # 应用入口
├── celery_worker.py           # Celery Worker
├── pyproject.toml             # Python 项目配置
├── Dockerfile                 # Docker 镜像
├── docker-compose.yml         # Docker Compose 配置
│
├── src/
│   ├── agents/               # LangGraph Agents
│   │   ├── main_graph.py     # 主图（查询路由）
│   │   ├── search_agent.py   # 搜索 Agent
│   │   ├── parser_agent.py   # 解析 Agent
│   │   └── rag_agent.py      # RAG Agent
│   │
│   ├── api/                  # FastAPI 路由
│   │   ├── main.py           # API 应用
│   │   └── routes/           # API 端点
│   │       ├── search.py
│   │       ├── projects.py
│   │       ├── chat.py
│   │       ├── auth.py
│   │       ├── export.py
│   │       └── parse.py
│   │
│   ├── models/               # Pydantic 模型
│   ├── services/             # 业务服务
│   │   ├── llm.py           # LLM 服务
│   │   ├── cache.py         # Redis 缓存
│   │   ├── vector_store.py  # 向量数据库
│   │   └── adapters/        # 数据库适配器
│   │
│   ├── tasks/               # Celery 任务
│   ├── utils/               # 工具函数
│   │   ├── logging.py       # 日志
│   │   ├── errors.py        # 错误处理
│   │   ├── rate_limit.py    # 速率限制
│   │   ├── metrics.py       # 监控指标
│   │   ├── text.py          # 文本处理
│   │   ├── citation.py      # 引用格式化
│   │   └── pdf.py           # PDF 处理
│   │
│   └── db/                  # 数据库模型
│
├── frontend/                # Next.js 前端
│   ├── src/app/            # React 页面
│   └── package.json
│
├── tests/                   # 测试
└── docs/                    # 文档
```

## 测试

```bash
# 运行所有测试
python3 -m pytest tests/ -v

# 运行特定测试
python3 -m pytest tests/test_search_agent.py -v

# 查看测试覆盖率
python3 -m pytest tests/ --cov=src --cov-report=html
```

## 监控

### 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/health

# 深度健康检查
curl http://localhost:8000/health/deep

# Prometheus 指标
curl http://localhost:8000/metrics
```

### 日志

```bash
# 查看日志
tail -f logs/ara.log

# JSON 格式日志 (生产环境)
tail -f logs/ara.log | jq
```

## 常见问题

### Q: 搜索返回空结果

A: 检查是否配置了 API 密钥。部分数据库 (PubMed) 可以无需密钥使用，但有速率限制。

### Q: PDF 解析失败

A: 确保 PDF 文件可读，部分扫描版 PDF 需要 OCR 支持。

### Q: RAG 对话无响应

A: 检查向量数据库配置，确保已正确初始化 Pinecone 或 Weaviate。

### Q: 速率限制

A: 默认限制为 60 次/分钟。如需提高，请修改 `src/utils/rate_limit.py` 中的配置。

## 开发指南

### 添加新的数据库适配器

1. 在 `src/services/adapters/` 创建新文件
2. 继承 `DatabaseAdapter` 协议
3. 实现 `search()`, `get_metadata()`, `download_pdf()` 方法
4. 在 `search_agent.py` 中注册适配器

```python
# src/services/adapters/my_adapter.py
from typing import Optional

class MyAdapter:
    async def search(self, query: dict, filters: Optional[dict] = None, limit: int = 50) -> list[dict]:
        # 实现搜索逻辑
        return []

    async def get_metadata(self, paper_id: str) -> dict:
        return {}

    async def download_pdf(self, paper_id: str) -> bytes:
        raise NotImplementedError()
```

### 添加新的 API 端点

1. 在 `src/api/routes/` 创建新文件
2. 定义 router 并添加端点
3. 在 `src/api/main.py` 中注册 router

## 生产部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 使用 Docker

```bash
# 构建镜像
docker build -t ara-api:latest .

# 运行
docker run -d -p 8000:8000 --env-file .env ara-api:latest
```

### 环境变量 (生产环境)

```env
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:password@db:5432/ara
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=<生成的随机密钥>
```

## 许可证

MIT License
