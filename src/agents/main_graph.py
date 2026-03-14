"""Main LangGraph orchestration for query routing."""
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel


class QueryState(TypedDict):
    """State for the main query graph."""

    # Input
    query: str
    user_id: Optional[str]
    project_id: Optional[str]

    # Classification
    query_type: Optional[Literal["search", "parse", "chat", "briefing"]]
    confidence: float
    entities: list[str]

    # Search state
    parsed_query: Optional[dict]
    search_results: Optional[list[dict]]
    ranked_results: Optional[list[dict]]

    # Parse state
    paper_id: Optional[str]
    pdf_url: Optional[str]
    parsed_data: Optional[dict]

    # Chat state
    conversation_id: Optional[str]
    chat_history: list[dict]
    context_papers: list[dict]
    answer: Optional[str]

    # Output
    response: Optional[dict]
    error: Optional[str]


def create_main_graph():
    """Create the main LangGraph for query routing."""
    graph = StateGraph(QueryState)

    # Add nodes
    graph.add_node("classify_query", classify_query_node)
    graph.add_node("search_subgraph", search_subgraph_node)
    graph.add_node("parse_subgraph", parse_subgraph_node)
    graph.add_node("rag_subgraph", rag_subgraph_node)
    graph.add_node("briefing_subgraph", briefing_subgraph_node)

    # Set entry point
    graph.set_entry_point("classify_query")

    # Add conditional edges
    graph.add_conditional_edges(
        "classify_query",
        route_query,
        {
            "search": "search_subgraph",
            "parse": "parse_subgraph",
            "chat": "rag_subgraph",
            "briefing": "briefing_subgraph",
        },
    )

    # Add edges to end
    graph.add_edge("search_subgraph", END)
    graph.add_edge("parse_subgraph", END)
    graph.add_edge("rag_subgraph", END)
    graph.add_edge("briefing_subgraph", END)

    return graph.compile()


async def classify_query_node(state: QueryState) -> QueryState:
    """Classify the user query to determine the appropriate subgraph."""
    from ..services.llm import LLMService

    llm = LLMService()
    query = state["query"]

    prompt = f"""Classify the following academic research query and return a JSON object with:
- query_type: one of "search" (looking for papers), "parse" (analyzing a specific paper),
  "chat" (asking questions about papers), or "briefing" (wanting a summary/trends)
- confidence: a score from 0 to 1
- entities: key research terms or paper titles mentioned

Query: {query}

Return JSON only."""

    result = await llm.generate(prompt, response_format={"type": "json_object"})

    # Parse the result
    import json

    try:
        parsed = json.loads(result)
        state["query_type"] = parsed.get("query_type", "search")
        state["confidence"] = parsed.get("confidence", 0.5)
        state["entities"] = parsed.get("entities", [])
    except (json.JSONDecodeError, Exception):
        state["query_type"] = "search"
        state["confidence"] = 0.5
        state["entities"] = []

    return state


def route_query(state: QueryState) -> str:
    """Route to the appropriate subgraph based on classification."""
    return state.get("query_type", "search")


async def search_subgraph_node(state: QueryState) -> QueryState:
    """Execute the search subgraph."""
    from .search_agent import SearchAgent

    agent = SearchAgent()
    results = await agent.search(
        query=state["query"],
        user_id=state.get("user_id"),
        project_id=state.get("project_id"),
    )

    state["search_results"] = results
    state["response"] = {"type": "search_results", "data": results}
    return state


async def parse_subgraph_node(state: QueryState) -> QueryState:
    """Execute the parse subgraph."""
    from .parser_agent import ParserAgent

    agent = ParserAgent()
    parsed = await agent.parse(
        paper_id=state.get("paper_id"),
        pdf_url=state.get("pdf_url"),
    )

    state["parsed_data"] = parsed
    state["response"] = {"type": "parsed_data", "data": parsed}
    return state


async def rag_subgraph_node(state: QueryState) -> QueryState:
    """Execute the RAG subgraph."""
    from .rag_agent import RAGAgent

    agent = RAGAgent()
    result = await agent.chat(
        project_id=state.get("project_id", ""),
        message=state["query"],
        history=state.get("chat_history", []),
    )

    state["answer"] = result.get("answer")
    state["response"] = {"type": "chat", "data": result}
    return state


async def briefing_subgraph_node(state: QueryState) -> QueryState:
    """Execute the briefing subgraph."""
    # TODO: Implement briefing agent
    state["response"] = {"type": "briefing", "data": {"message": "Briefing feature coming soon"}}
    return state


# Create singleton graph instance
_main_graph = None


def get_main_graph():
    """Get the main graph singleton."""
    global _main_graph
    if _main_graph is None:
        _main_graph = create_main_graph()
    return _main_graph
