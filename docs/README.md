# Academic Research Assistant (ARA)

[English](./README_EN.md) | 中文

基于 LangGraph 的学术文献智能搜索与分析系统，支持多数据库搜索、AI 排序、PDF 解析、RAG 对话等功能。

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple)
![License](https://img.shields.io/badge/License-MIT-orange)

## 功能特性

### 🔍 多数据库搜索
- **Web of Science** - 科睿唯安学术引文数据库
- **Scopus** - 爱思唯尔学术数据库
- **PubMed** - 生物医学文献数据库
- **Google Scholar** - 谷歌学术搜索
- **EBSCOhost** - EBSCO 学术数据库

### 🔎 高级搜索
- 布尔运算符支持 (AND, OR, NOT)
- 精确短语搜索 ("exact phrase")
- 嵌套逻辑查询
- 年份范围筛选
- 期刊分区筛选 (Q1-Q4)
- 研究类型筛选

### 🤖 AI 智能排序
```
相关性评分 = 语义相似度(40%) + 期刊质量(30%) + 研究设计(30%)
```
- 基于 text-embedding-3-large 的语义相似度计算
- Q1-Q4 期刊权重分配
- 元分析、纵向研究、实验研究等设计类型优先级

### 📄 PDF 解析
- 章节结构识别（引言、方法、结果、讨论）
- 结构化数据提取：
  - 研究类型（横断面、纵向、荟萃分析等）
  - 自变量、因变量、中介变量、调节变量
  - 样本量、研究对象
  - 测量工具（量表名称、项目数、α系数）
  - 统计值提取（r, d, F, t, p 等）
- CSV/Excel 矩阵生成

### 💬 RAG 对话
- 基于 Pinecone/Weaviate 的向量检索
- 带引用的学术回答
- 引用格式：[作者, 年份, 页码]
- 项目级别的文献对话

### 📊 趋势简报
- 定时任务自动执行（Celery Beat）
- 新论文检测与摘要生成
- 周报/月报自动生成
- 自定义追踪查询

### 📁 项目管理
- 用户认证系统 (JWT)
- 项目/工作区管理
- 文献收藏与标注
- BibTeX/RIS/CSV 导出

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend (Next.js)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │  Search Bar │  │   Projects  │  │     Chat Interface         │ │
│  │             │  │  Workspace  │  │   (RAG Conversation)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API Layer (FastAPI)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ /search  │ │ /parse   │ │  /chat   │ │ /projects│ │ /export  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LangGraph Agent Orchestration                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │    Search    │───▶│    Parser    │───▶│     RAG      │        │
│  │    Agent     │    │    Agent      │    │    Agent     │        │
│  └──────────────┘    └──────────────┘    └──────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External Services                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │   WOS     │ │  Scopus  │ │  PubMed  │ │Google    │              │
│  │           │ │          │ │          │ │ Scholar  │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### LangGraph 节点设计

```
START
  │
  ▼
┌─────────────────────────┐
│  query_classification   │  ──▶ 判断查询类型
└─────────────────────────┘
  │
  ├── [search] ──▶ search_subgraph
  ├── [parse] ──▶ parse_subgraph
  ├── [chat] ──▶ rag_subgraph
  └── [briefing] ──▶ briefing_subgraph
```

---

## 快速开始

### 前置要求

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.11+ | 主要运行环境 |
| Node.js | 18+ | 前端开发 |
| Redis | 7.0+ | 缓存/消息队列 |
| PostgreSQL | 15+ | 生产数据库 |

### 1. 克隆项目

```bash
git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 或使用 conda
conda create -n ara python=3.11
conda activate ara
```

### 3. 安装依赖

```bash
# 后端
pip install -e ".[dev]"

# 前端 (可选)
cd frontend && npm install && cd ..
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 添加 API 密钥
```

必需的配置：

```env
# LLM - 至少选择一个
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# JWT - 生产环境请修改
JWT_SECRET_KEY=your-secret-key-change-in-production
```

可选的配置：

```env
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./ara.db

# Redis
REDIS_URL=redis://localhost:6379/0

# 向量数据库
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1

# 学术数据库 API
PUBMED_API_KEY=...
WOS_API_KEY=...
SCOPUS_API_KEY=...
EBSCO_API_KEY=...
```

### 5. 启动服务

```bash
# API 服务 (端口 8000)
python3 main.py

# Celery Worker (可选)
python3 celery_worker.py
```

或使用 Docker：

```bash
docker-compose up -d
```

---

## API 文档

### 完整 API 端点列表

#### 搜索 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/search` | 搜索学术论文 |
| GET | `/api/search/databases` | 获取可用数据库列表 |

**搜索请求示例：**

```json
{
  "query": "(远程工作 OR 居家办公) AND 职业倦怠",
  "databases": ["pubmed", "wos"],
  "filters": {
    "year_from": 2020,
    "year_to": 2024,
    "journal_tiers": ["Q1", "Q2"]
  },
  "limit": 50
}
```

#### 项目 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/projects` | 列表项目 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| DELETE | `/api/projects/{id}` | 删除项目 |
| GET | `/api/projects/{id}/papers` | 获取项目论文 |
| POST | `/api/projects/{id}/papers` | 添加论文 |

#### 聊天 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/chat` | 发送聊天消息 |
| GET | `/api/chat/{conversation_id}` | 获取对话历史 |
| DELETE | `/api/chat/{conversation_id}` | 删除对话 |

#### 解析 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/parse` | 解析论文 |
| GET | `/api/parse/task/{task_id}` | 获取解析状态 |

#### 导出 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/export/bibtex` | 导出 BibTeX |
| POST | `/api/export/ris` | 导出 RIS |
| POST | `/api/export/csv` | 导出 CSV |

#### 认证 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/token` | 登录获取 Token |
| GET | `/api/auth/me` | 获取当前用户 |

#### 简报 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/briefings` | 列表简报 |
| GET | `/api/briefings/{id}` | 获取简报详情 |
| POST | `/api/briefings/trackers` | 创建追踪器 |
| POST | `/api/briefings/trackers/{id}/run` | 手动执行追踪 |

#### 监控 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 基础健康检查 |
| GET | `/health/deep` | 深度健康检查 |
| GET | `/metrics` | Prometheus 指标 |

### API 使用示例

#### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 搜索论文
response = requests.post(f"{BASE_URL}/api/search", json={
    "query": "machine learning healthcare",
    "databases": ["pubmed"],
    "limit": 10
})
papers = response.json()["data"]["papers"]

# 创建项目
response = requests.post(f"{BASE_URL}/api/projects", json={
    "name": "ML in Healthcare",
    "description": "Machine learning applications in healthcare"
})
project = response.json()["data"]

# RAG 对话
response = requests.post(f"{BASE_URL}/api/chat", json={
    "project_id": project["id"],
    "message": "What are the main findings?"
})
answer = response.json()["data"]["message"]["content"]
```

#### JavaScript 示例

```javascript
const response = await fetch('http://localhost:8000/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'machine learning',
    databases: ['pubmed'],
    limit: 20
  })
});
const data = await response.json();
console.log(data.data.papers);
```

---

## 数据模型

### PostgreSQL Schema

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 论文表
CREATE TABLE papers (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    title VARCHAR(500) NOT NULL,
    authors JSONB,
    abstract TEXT,
    journal VARCHAR(255),
    year INTEGER,
    doi VARCHAR(100),
    source VARCHAR(50),
    paper_type VARCHAR(50),
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 论文解析数据矩阵
CREATE TABLE paper_matrix (
    id UUID PRIMARY KEY,
    paper_id UUID REFERENCES papers(id),
    research_type VARCHAR(50),
    independent_vars JSONB,
    dependent_vars JSONB,
    mediating_vars JSONB,
    moderating_vars JSONB,
    sample_size INTEGER,
    subjects JSONB,
    key_findings TEXT,
    raw_json JSONB
);
```

### 向量数据库 Schema (Pinecone)

```python
{
    "id": "paper_{id}_chunk_{index}",
    "values": [embedding],  # 768维或1536维
    "metadata": {
        "paper_id": "uuid",
        "project_id": "uuid",
        "title": "string",
        "authors": "string",
        "year": "int",
        "chunk_text": "string",
        "page": "int",
        "section": "string"  # method/result/discussion
    }
}
```

---

## 配置选项

### 速率限制

默认配置（可在 `src/utils/rate_limit.py` 修改）：

```python
requests_per_minute = 60
requests_per_hour = 1000
```

### 缓存策略

| 缓存类型 | TTL | 说明 |
|---------|-----|------|
| 搜索结果 | 1 小时 | 相同查询结果缓存 |
| 用户会话 | 24 小时 | JWT Token |
| 论文解析 | 7 天 | PDF 解析结果 |

### 日志级别

| 级别 | 说明 |
|------|------|
| DEBUG | 详细调试信息 |
| INFO | 一般信息 |
| WARNING | 警告信息 |
| ERROR | 错误信息 |

---

## 测试

### 运行测试

```bash
# 所有测试
python3 -m pytest tests/ -v

# 覆盖率报告
python3 -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# 特定模块
python3 -m pytest tests/test_search_agent.py -v
python3 -m pytest tests/test_api.py -v
```

### 测试覆盖范围

| 模块 | 测试类型 | 覆盖率 |
|------|---------|--------|
| models | Unit | 100% |
| search_agent | Unit + Integration | 85%+ |
| parser_agent | Unit | 80%+ |
| API routes | Integration | 75%+ |

---

## 部署

### Docker 部署

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/ara
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: python celery_worker.py
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/ara
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=postgres

  redis:
    image: redis:7-alpine
```

### 生产环境检查清单

- [ ] 使用 PostgreSQL 替代 SQLite
- [ ] 配置 Redis 缓存
- [ ] 设置 JWT_SECRET_KEY
- [ ] 配置 HTTPS/TLS
- [ ] 设置日志级别为 WARNING
- [ ] 配置监控和告警
- [ ] 定期备份数据库

---

## 常见问题

### Q: 搜索返回空结果

A: 检查以下内容：
1. 是否配置了 API 密钥
2. PubMed 无密钥时有速率限制
3. 查询语法是否正确

### Q: PDF 解析失败

A: 可能原因：
1. PDF 是扫描版（需要 OCR）
2. PDF 加密或损坏
3. 网络问题无法下载

### Q: RAG 对话无响应

A: 检查：
1. Pinecone/Weaviate 是否正确配置
2. 项目中是否有论文
3. LLM API 密钥是否有效

### Q: 速率限制错误

A: 默认限制 60次/分钟。修改 `src/utils/rate_limit.py` 或申请提高配额。

---

## 开发指南

### 添加新的数据库适配器

1. 创建适配器文件：

```python
# src/services/adapters/my_adapter.py
from typing import Optional, Protocol

class MyAdapter:
    BASE_URL = "https://api.example.com"

    def __init__(self):
        self.api_key = os.getenv("MY_API_KEY")

    async def search(self, query: dict, filters: Optional[dict] = None, limit: int = 50) -> list[dict]:
        """搜索实现"""
        # 实现搜索逻辑
        return []

    async def get_metadata(self, paper_id: str) -> dict:
        """获取元数据"""
        return {}

    async def download_pdf(self, paper_id: str) -> bytes:
        """下载 PDF"""
        raise NotImplementedError()
```

2. 注册适配器：

```python
# src/agents/search_agent.py
self.adapters["my_db"] = MyAdapter()
```

### 添加新的 Agent

1. 创建 Agent 文件：

```python
# src/agents/my_agent.py
class MyAgent:
    async def run(self, input_data: dict) -> dict:
        # 实现逻辑
        return {"result": "..."}
```

2. 在主图中注册：

```python
# src/agents/main_graph.py
graph.add_node("my_agent", my_agent_node)
```

---

## 性能优化

### 建议配置

| 组件 | 开发环境 | 生产环境 |
|------|---------|---------|
| Workers | 1 | 4+ |
| Worker Threads | 2 | 4 |
| Connection Pool | 5 | 20 |
| Request Timeout | 30s | 60s |

### 缓存策略

- 搜索结果：1小时
- 向量嵌入：24小时
- 用户认证：会话期间
- 论文元数据：7天

---

## 安全考虑

- [x] JWT 认证
- [x] 速率限制
- [x] 输入验证
- [x] SQL 注入防护
- [x] XSS 防护
- [x] CORS 配置

### 安全建议

1. 生产环境使用 HTTPS
2. 定期轮换 API 密钥
3. 启用审计日志
4. 定期安全更新

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'feat: add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 联系方式

- GitHub Issues: https://github.com/EricHong123/academic-research-assistant/issues
- Email: erich@example.com
