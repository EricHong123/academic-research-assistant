# 快速开始指南

## 5分钟快速启动

### 1. 安装

```bash
cd /Users/erich/academic-research-assistant
pip install -e .
```

### 2. 配置

```bash
cp .env.example .env
# 编辑 .env 添加 API 密钥
```

### 3. 启动

```bash
python3 main.py
```

### 4. 访问

- API: http://localhost:8000
- 文档: http://localhost:8000/docs
- 示例: http://localhost:8000/redoc

## Docker 启动 (一行命令)

```bash
docker-compose up -d
```

## 验证安装

```bash
# 健康检查
curl http://localhost:8000/health

# 搜索测试
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## 需要的 API 密钥

| 服务 | 必需 | 获取方式 |
|------|------|----------|
| PubMed | 可选 | 免费 API key (可选) |
| OpenAI/Anthropic | 推荐 | openai.com / anthropic.com |
| Pinecone | 可选 | pinecone.io |

## 下一步

- 查看完整文档: `docs/README.md`
- 访问 API 文档: http://localhost:8000/docs
- 运行测试: `python3 -m pytest tests/`
