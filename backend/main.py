"""
Omni Copilot — FastAPI Backend Entry Point
Provides streaming chat, integrations management, memory, and voice endpoints.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from routers import chat, integrations, memory, voice  # noqa: E402

app = FastAPI(
    title="Omni Copilot API",
    description="Universal AI workspace backend with multi-agent orchestration",
    version="1.0.0",
)

# CORS — allow the Next.js frontend
FRONTEND_URL = os.getenv("FRONTEND_APP_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Basic health-check endpoint."""
    return {"status": "ok", "service": "omni-copilot-backend"}


# ── Routers ───────────────────────────────────────────────────────────
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
