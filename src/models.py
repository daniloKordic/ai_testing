"""Data models for the application."""

from pydantic import BaseModel
from typing import Optional


class SearchQuery(BaseModel):
    """Request model for search queries."""

    query: str
    top_k: int = 5


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    messages: list[ChatMessage]
    search_query: Optional[str] = None

    class Config:
        """Config for the model."""
        json_schema_extra = {
            "example": {
                "messages": [{"role": "user", "content": "What are green apples?"}],
                "search_query": "optional: leave empty to use last message as query"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    source_documents: list[dict] = []
