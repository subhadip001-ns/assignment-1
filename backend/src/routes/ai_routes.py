from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from src.services.ai_service import AIService, ai_service
from src.services.chat_service import ChatService
from src.routes.auth_routes import verify_token
from src.db.postgres import get_db
from sqlalchemy.orm import Session
# Prefer decorator-based API; fall back to no-op if unavailable
try:  # Soft dependency to avoid runtime crash on incompatible envs
    from langfuse import observe  # type: ignore
    _observe = observe
    os.environ.setdefault("LANGFUSE_HOST", os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", ""))
except Exception:  # pragma: no cover - if import/init fails, disable observability
    def _observe(*args, **kwargs):  # type: ignore
        def _wrap(fn):
            return fn
        return _wrap
    print("[Langfuse] Observe disabled: decorator not available. No observability will be recorded.")


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    response: str


class ChatHistoryResponse(BaseModel):
    messages: List[dict]


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={401: {"description": "Unauthorized"}}
)


@router.post("/chat", response_model=ChatResponse)
@_observe(name="ai.chat", as_type="generation")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Non-streaming chat endpoint for AI agent interaction.

    Args:
        request: Chat request containing message and optional chat history
        current_user: Current authenticated user
        db: Database session

    Returns:
        ChatResponse containing the AI response
    """
    try:
        user_id = current_user["id"]
        
        # Save user message
        ChatService.save_message(db, user_id, "user", request.message)
        
        # Get chat history from database if not provided
        if not request.chat_history:
            db_messages = ChatService.get_chat_history(db, user_id)
            request.chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in db_messages
            ]
        
        response = ai_service.chat(request.message, request.chat_history)
        
        # Save assistant response
        ChatService.save_message(db, user_id, "assistant", response)
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/chat/stream")
@_observe(name="ai.chat.stream", as_type="generation")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Streaming chat endpoint for AI agent interaction.

    Args:
        request: Chat request containing message and optional chat history
        current_user: Current authenticated user
        db: Database session

    Returns:
        StreamingResponse with AI response chunks
    """
    user_id = current_user["id"]
    
    # Save user message
    ChatService.save_message(db, user_id, "user", request.message)
    
    # Get chat history from database if not provided
    if not request.chat_history:
        db_messages = ChatService.get_chat_history(db, user_id)
        request.chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in db_messages
        ]
    
    streaming_service = AIService(is_streaming=True)
    try:
        def generate():
            buffer = ""
            try:
                try:
                    for chunk in streaming_service.chat_stream(request.message, request.chat_history):
                        # Check if this is a tool call marker
                        if chunk.startswith("[TOOL_CALLS]") and chunk.endswith("[/TOOL_CALLS]"):
                            # Send tool calls as a special event
                            tool_calls_data = chunk.replace("[TOOL_CALLS]", "").replace("[/TOOL_CALLS]", "")
                            yield f"data: [TOOL_CALLS]{tool_calls_data}[/TOOL_CALLS]\n\n"
                        else:
                            buffer += chunk
                            yield f"data: {chunk}\n\n"
                except Exception as stream_err:  # Prevent server-side 500s during SSE
                    err_msg = f"Error: {str(stream_err)}"
                    buffer += err_msg
                    yield f"data: {err_msg}\n\n"
            finally:
                # Save assistant response after streaming completes
                if buffer:
                    try:
                        ChatService.save_message(db, user_id, "assistant", buffer)
                    except Exception as save_err:
                        print(f"Failed to save chat message: {save_err}")
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    except Exception as e:
        print(f"[AI Stream] Initialization error: {e}")
        def generate_error():
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(
            generate_error(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> ChatHistoryResponse:
    """
    Get chat history for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        ChatHistoryResponse containing list of messages
    """
    try:
        user_id = current_user["id"]
        messages = ChatService.get_chat_history(db, user_id)
        
        return ChatHistoryResponse(
            messages=[
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")


@router.delete("/chat/history")
async def clear_chat_history(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Clear chat history for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    try:
        user_id = current_user["id"]
        ChatService.clear_chat_history(db, user_id)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")
