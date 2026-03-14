# Academic Research Assistant (ARA)

学术文献智能搜索与分析系统 | LangGraph-based AI Agent for Academic Literature Search

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![License](https://img.shields.io/badge/License-MIT-orange)

[English](#english) | [中文](#中文)

---

## 中文

### 功能特性

- 🔍 **多数据库搜索** - Web of Science、Scopus、PubMed、Google Scholar
- 🔎 **高级搜索** - 布尔运算符 (AND, OR, NOT)、精确短语
- 🤖 **AI 智能排序** - 语义嵌入、期刊质量、研究设计
- 📄 **PDF 解析** - 提取研究类型、变量、样本量、统计值
- 💬 **RAG 对话** - 带引用的学术问答
- 📊 **趋势简报** - 自动追踪研究趋势
- 📁 **项目管理** - 文献收藏与管理
- 🌐 **多语言** - 支持中文/英文界面

### 快速开始

#### 1. 克隆项目

```bash
git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant
```

#### 2. 安装依赖

```bash
# 后端
pip install -e ".[dev]"

# 前端
cd frontend
npm install
cd ..
```

#### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 添加 API 密钥
```

必需配置：
```env
# LLM - 至少选择一个
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# JWT 密钥
JWT_SECRET_KEY=your-secret-key
```

#### 4. 启动服务

```bash
# 后端 (端口 8000)
python3 main.py

# 前端 (端口 3000) - 新终端
cd frontend && npm run dev
```

#### 5. 访问

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| API 文档 | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/health |

### Docker 部署

```bash
docker-compose up -d
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14, React, Tailwind CSS |
| 后端 | FastAPI, Python 3.11+ |
| Agent | LangGraph |
| LLM | OpenAI GPT-4, Anthropic Claude |
| 数据库 | PostgreSQL, Redis, Pinecone |

### 项目结构

```
academic-research-assistant/
├── main.py                 # 后端入口
├── main.py               # 后端入口
├── main.py               # 后端入口
├── src/
│   ├── agents/          # LangGraph Agents
│   ├── api/              # FastAPI 路由
│   ├── models/           # 数据模型
│   ├── services/         # 业务服务
│   ├── tasks/            # Celery 任务
│   └── utils/            # 工具函数
├── frontend/             # Next.js 前端
│   └── src/
│       ├── app/          # 页面组件
│       └── lib/          # 工具库
└── tests/                # 测试
```

### API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/search` | 搜索论文 |
| POST | `/api/parse` | 解析 PDF |
| POST | `/api/chat` | RAG 对话 |
| GET/POST | `/api/projects` | 项目管理 |
| POST | `/api/export/bibtex` | 导出引用 |

### 测试

```bash
# 运行测试
python3 -m pytest tests/ -v
```

---

## English

### Features

- 🔍 **Multi-database Search** - Web of Science, Scopus, PubMed, Google Scholar
- 🔎 **Advanced Search** - Boolean operators (AND, OR, NOT), phrase search
- 🤖 **AI Ranking** - Semantic embeddings, journal quality, study design
- 📄 **PDF Parsing** - Extract research type, variables, sample size, statistics
- 💬 **RAG Chat** - Conversational interface with citations
- 📊 **Trend Briefings** - Automated research trend reports
- 📁 **Project Management** - Organize literature collections
- 🌐 **Multi-language** - Chinese/English UI

### Quick Start

```bash
# Clone
git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant

# Install
pip install -e ".[dev]"

# Frontend
cd frontend && npm install && cd ..

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run Backend (port 8000)
python3 main.py

# Run Frontend (port 3000) - New terminal
cd frontend && npm run dev
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

### Docker

```bash
docker-compose up -d
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, Tailwind CSS |
| Backend | FastAPI, Python 3.11+ |
| Agent | LangGraph |
| LLM | OpenAI GPT-4, Anthropic Claude |
| Database | PostgreSQL, Redis, Pinecone |

### Testing

```bash
python3 -m pytest tests/ -v
```

---

## License

MIT License
