"""
Voice router — TTS endpoint using Groq.
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

TTS_MODEL = os.getenv("GROQ_TTS_MODEL", "playai-tts")
TTS_VOICE_EN = os.getenv("GROQ_TTS_VOICE_EN", "alloy")
TTS_VOICE_HI = os.getenv("GROQ_TTS_VOICE_HI", "alloy")


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    """Convert text to speech using Groq TTS. Returns audio config info."""
    voice = TTS_VOICE_EN if req.language == "en" else TTS_VOICE_HI
    # TODO: Implement actual Groq TTS streaming
    return {
        "status": "ok",
        "model": TTS_MODEL,
        "voice": voice,
        "language": req.language,
        "text_length": len(req.text),
        "message": "TTS endpoint ready — configure GROQ_API_KEY to enable audio streaming",
    }
