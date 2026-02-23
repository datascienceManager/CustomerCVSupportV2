"""
routers/tts.py
POST /api/tts  — convert text to MP3 and return as streamable audio response.
Used by the voice widget to play AI replies back without any file upload.
"""
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from utils.ai_engine import text_to_speech

router = APIRouter(prefix="/api", tags=["tts"])

class TTSRequest(BaseModel):
    text: str
    language: str = "en"   # "en" or "ar"

@router.post("/tts")
async def tts_endpoint(req: TTSRequest):
    """
    Converts text to speech using gTTS and returns raw MP3 bytes.
    The browser plays this directly via the Audio API — no file saved anywhere.
    """
    lang = req.language if req.language in ("en", "ar") else "en"
    # Truncate very long replies to keep audio short
    text = req.text[:600] if len(req.text) > 600 else req.text
    audio_bytes = text_to_speech(text, lang)
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "Content-Disposition": "inline; filename=reply.mp3"
        }
    )
