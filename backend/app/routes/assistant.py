"""AI Purchasing Assistant chat routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.ai_service import AIAssistantService

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Interact with the AI purchasing assistant to discover and compare items."""
    result = await AIAssistantService.process_user_message(
        db=db,
        user_id=user.id,
        message=payload.message,
        agent_type=payload.agent_type,
    )
    return ChatResponse(**result)
