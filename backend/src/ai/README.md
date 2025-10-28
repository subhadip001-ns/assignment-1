# AI Module (LangChain + Groq + RAG)

This module powers the AI assistant used by the Enrollment Portal. It combines a Groq-hosted LLM with LangChain tools and a lightweight RAG service backed by Voyage AI embeddings.

## Components

- `prompts.py`: System prompt that governs tool usage and response style
- `tools.py`: LangChain tools for arithmetic, course lookup, enrollment, and semantic search
- `../services/ai_service.py`: Orchestrates LLM calls, tool binding, and streaming
- `../services/rag_service.py`: Embeddings, vector store, and search helpers for course context
- `../routes/ai_routes.py`: FastAPI endpoints for AI chat (regular + streaming)

## Environment Variables

- `GROQ_API_KEY`: Required for Groq LLM access
- `VOYAGE_AI_API_KEY`: Required for Voyage AI embeddings used by the RAG service
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`: Required for Langfuse observability

Set them in the root `.env`:

```
GROQ_API_KEY=your_groq_api_key
VOYAGE_AI_API_KEY=your_voyage_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

## How It Works

1. The `AIService` uses `ChatGroq` with tools bound from `tools.py`.
2. On each user request, the system prompt (`prompts.py`) instructs the model to use tools for:
   - `add_numbers`
   - `fetch_all_courses`
   - `enroll_into_course`
   - `search_course_information` (RAG)
3. If tools are called, results are injected back and a final answer is generated.
4. For semantic search, `rag_service.py` embeds and searches course documents via a cached embeddings pipeline and an in-memory vector store.

## API Endpoints

All endpoints require authentication (JWT) via the existing auth middleware.

- `POST /ai/chat`
  - Body: `{ "message": string, "chat_history"?: Array<{ role: 'user'|'assistant', content: string }> }`
  - Returns: `{ "response": string }`

- `POST /ai/chat/stream`
  - Body: same as above
  - Server-Sent Events stream of text chunks with `data: ...` lines and a final `data: [DONE]`.

## RAG Notes

- Documents are created from course data and split into chunks before indexing.
- You can trigger ingestion as part of tests (see root README for RAG ingestion note). New or updated courses should be ingested to reflect in `search_course_information` results.

## Local Development

- Ensure backend runs (`python main.py`) and DB is up via Docker Compose.
- Provide `GROQ_API_KEY`, `VOYAGE_AI_API_KEY`, and Langfuse env vars.
- Test with curl:

```
# Non-streaming
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "message": "What courses about programming do you have?",
    "chat_history": []
  }'
```

## Changing the Model

The model is configured in `services/ai_service.py`:

```
ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.2,
    streaming=is_streaming,
)
```

Adjust `model_name` or parameters as needed.
