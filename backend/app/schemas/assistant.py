"""Pydantic schemas for AI Assistant."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    agent_type: str = "food"  # "food" or "shopping"


class ChatResponse(BaseModel):
    reply: str
    agent_type: str
    recommendations: List[Dict[str, Any]] = []
    action_taken: Optional[str] = None
    payment_request: Optional[Dict[str, Any]] = None
