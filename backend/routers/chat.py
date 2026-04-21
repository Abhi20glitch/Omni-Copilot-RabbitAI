"""
Chat router — SSE streaming endpoint that calls the LangGraph orchestrator.
"""

import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    history: list[dict] = []


async def _stream_orchestrator(request: ChatRequest):
    """Run the orchestrator and stream results as SSE events."""
    from agents.orchestrator import OrchestratorAgent

    orchestrator = OrchestratorAgent()

    messages = list(request.history)
    messages.append({"role": "user", "content": request.message})

    # Send a "thinking" step
    yield f"data: {json.dumps({'type': 'step', 'agent': 'orchestrator', 'action': 'Analyzing your request...'})}\n\n"
    await asyncio.sleep(0.3)

    # Run the graph
    try:
        result = orchestrator.run(user_id=request.user_id, messages=messages)
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
        return

    # Stream each agent step
    for step in result.get("agent_steps", []):
        yield f"data: {json.dumps({'type': 'step', 'agent': step['agent'], 'action': step['action']})}\n\n"
        await asyncio.sleep(0.15)

    # Stream the final assistant message token-by-token
    assistant_msgs = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_msgs:
        content = assistant_msgs[-1]["content"]
        # Simulate token-by-token streaming
        words = content.split(" ")
        buffer = ""
        for i, word in enumerate(words):
            buffer += word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
            await asyncio.sleep(0.03)

    yield f"data: {json.dumps({'type': 'done', 'plan': result.get('plan')})}\n\n"
    yield "data: [DONE]\n\n"


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """SSE streaming endpoint — calls LangGraph orchestrator."""
    return StreamingResponse(
        _stream_orchestrator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
