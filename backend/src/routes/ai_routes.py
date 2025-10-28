from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from src.services.ai_service import AIService, ai_service
from src.routes.auth_routes import verify_token


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    response: str


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={401: {"description": "Unauthorized"}}
)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(verify_token)
) -> ChatResponse:
    """
    Non-streaming chat endpoint for AI agent interaction.

    Args:
        request: Chat request containing message and optional chat history
        current_user: Current authenticated user

    Returns:
        ChatResponse containing the AI response
    """
    try:
        response = ai_service.chat(request.message, request.chat_history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Streaming chat endpoint for AI agent interaction.

    Args:
        request: Chat request containing message and optional chat history
        current_user: Current authenticated user

    Returns:
        StreamingResponse with AI response chunks
    """
    streaming_service = AIService(is_streaming=True)
    try:
        def generate():
            for chunk in streaming_service.chat_stream(request.message, request.chat_history):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI streaming service error: {str(e)}")
