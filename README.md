# Academic Research Assistant (ARA)

LangGraph-based AI Agent for academic literature search and analysis.

## Features

- **Multi-database Search**: Search across Web of Science, Scopus, PubMed, Google Scholar
- **Boolean Query Support**: Support for AND, OR, NOT operators and phrase search
- **AI-Powered Ranking**: Relevance scoring using semantic embeddings
- **PDF Parsing**: Extract structured data from academic papers
- **RAG Chat**: Conversational interface with your paper collection
- **Trend Briefings**: Automated research trend reports

## Quick Start

### 1. Install Dependencies

```bash
cd academic-research-assistant
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | Search academic papers |
| POST | `/api/chat` | RAG conversation |
| GET | `/api/projects` | List projects |
| POST | `/api/projects` | Create project |
| POST | `/api/export/bibtex` | Export to BibTeX |
| POST | `/api/export/ris` | Export to RIS |

## Architecture

```
src/
├── agents/          # LangGraph agents
│   ├── main_graph.py
│   ├── search_agent.py
│   ├── parser_agent.py
│   └── rag_agent.py
├── api/            # FastAPI routes
│   └── routes/
├── models/         # Pydantic models
├── services/       # Business logic
│   ├── llm.py
│   ├── vector_store.py
│   └── adapters/   # Database adapters
└── db/             # SQLAlchemy models
```

## Development

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
ruff check src/
mypy src/
```

## License

MIT
