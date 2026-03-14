# Academic Research Assistant (ARA)

LangGraph-based AI Agent for Academic Literature Search and Analysis

[中文](./docs/README.md) | English

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple)
![License](https://img.shields.io/badge/License-MIT-orange)

## Features

- **Multi-database Search** - Web of Science, Scopus, PubMed, Google Scholar
- **Boolean Query Support** - AND, OR, NOT operators and phrase search
- **AI Relevance Ranking** - Semantic embeddings, journal quality, study design
- **PDF Parsing** - Extract research type, variables, sample size, statistics
- **RAG Chat** - Conversational interface with citations
- **Trend Briefings** - Automated research trend reports
- **Project Management** - Organize literature collections
- **Export Formats** - BibTeX, RIS, CSV

## Quick Start

```bash
# Clone
git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant

# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python3 main.py
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
python3 -m pytest tests/ -v
```

## Docker

```bash
docker-compose up -d
```

## License

MIT License
