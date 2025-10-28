from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from src.services.ai_service import AIService, ai_service
from src.routes.auth_routes import verify_token
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


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={401: {"description": "Unauthorized"}}
)


@router.post("/chat", response_model=ChatResponse)
@_observe(name="ai.chat", as_type="generation")
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
@_observe(name="ai.chat.stream", as_type="generation")
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
            buffer = ""
            try:
                try:
                    for chunk in streaming_service.chat_stream(request.message, request.chat_history):
                        buffer += chunk
                        yield f"data: {chunk}\n\n"
                except Exception as stream_err:  # Prevent server-side 500s during SSE
                    err_msg = f"Error: {str(stream_err)}"
                    buffer += err_msg
                    yield f"data: {err_msg}\n\n"
            finally:
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
