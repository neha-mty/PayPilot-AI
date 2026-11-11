"""Pydantic schemas for AI Assistant."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    agent_type: str = "universal"  # "universal", "food", "shopping", "electronics", etc.


class ChatResponse(BaseModel):
    reply: str
    agent_type: str
    detected_intent: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = []
    action_taken: Optional[str] = None
    payment_request: Optional[Dict[str, Any]] = None
