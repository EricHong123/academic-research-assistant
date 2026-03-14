"""Chat API routes for RAG conversations."""
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...models.chat import ChatRequest, ChatResponse
from ...agents.rag_agent import RAGAgent


router = APIRouter()

# In-memory conversation storage
_conversations: dict[str, list[dict]] = {}


def get_current_user_id() -> str:
    """Get current user ID (replace with auth)."""
    return "demo-user"


@router.post("", response_model=dict)
async def chat(request: ChatRequest):
    """Send a chat message and get a response."""
    user_id = get_current_user_id()

    # Get or create conversation
    conversation_id = request.conversation_id or str(uuid.uuid4())

    if conversation_id not in _conversations:
        _conversations[conversation_id] = []

    # Add user message
    _conversations[conversation_id].append({
        "role": "user",
        "content": request.message,
    })

    try:
        # Get RAG response
        agent = RAGAgent()

        result = await agent.chat(
            project_id=request.project_id,
            message=request.message,
            history=_conversations[conversation_id],
        )

        # Add assistant message
        _conversations[conversation_id].append({
            "role": "assistant",
            "content": result.get("answer", ""),
            "citations": result.get("citations", []),
        })

        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "message": {
                    "role": "assistant",
                    "content": result.get("answer", ""),
                    "citations": result.get("citations", []),
                },
                "references": result.get("referenced_papers", []),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=dict)
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "success": True,
        "data": {
            "conversation_id": conversation_id,
            "messages": _conversations[conversation_id],
        },
    }


@router.delete("/{conversation_id}", response_model=dict)
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    del _conversations[conversation_id]

    return {
        "success": True,
        "message": "Conversation deleted",
    }
