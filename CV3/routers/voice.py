"""
routers/voice.py
POST /api/voice  — upload audio, get transcript + AI reply + base64 TTS audio
"""
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from datetime import datetime

from utils.ai_engine import transcribe_audio, chat, text_to_speech, detect_language, AI_PROVIDER, get_provider_info
from utils.database import (
    create_session, save_message, get_session_messages,
    get_last_message_id
)
from utils.sheets import append_single_message

router = APIRouter(prefix="/api", tags=["voice"])

ALLOWED_TYPES = {
    "audio/wav", "audio/wave", "audio/mpeg", "audio/mp3",
    "audio/mp4", "audio/m4a", "audio/ogg", "audio/webm",
    "application/octet-stream"
}

@router.post("/voice")
async def voice_endpoint(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    language: str = Form("auto")
):
    # Validate file type
    if audio.content_type and audio.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio type: {audio.content_type}. Use WAV, MP3, or M4A."
        )

    audio_bytes = await audio.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty.")
    if len(audio_bytes) > 25 * 1024 * 1024:  # 25MB limit
        raise HTTPException(status_code=400, detail="Audio file too large (max 25MB).")

    # Resolve language hint for Whisper
    lang_hint = language if language in ("en", "ar") else "en"

    # Step 1: Transcribe
    transcript = transcribe_audio(audio_bytes, lang_hint)

    # Auto-detect language from transcript
    lang = detect_language(transcript) if language == "auto" else lang_hint

    # Step 2: Load history and build messages
    create_session(session_id, lang, "voice")
    history = get_session_messages(session_id)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": transcript})

    # Save user message
    save_message(session_id, "user", transcript, lang, "voice", AI_PROVIDER)

    # Step 3: AI reply
    reply = chat(messages, lang)
    save_message(session_id, "assistant", reply, lang, "voice", AI_PROVIDER)

    # Sync to Sheets
    try:
        msg_id = get_last_message_id()
        append_single_message({
            "id": msg_id,
            "session_id": session_id,
            "role": "assistant",
            "content": reply,
            "language": lang,
            "mode": "voice",
            "provider": AI_PROVIDER,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception:
        pass

    # Step 4: TTS — return as base64 so any frontend can play it
    tts_bytes = text_to_speech(reply, lang)
    audio_b64 = base64.b64encode(tts_bytes).decode("utf-8")

    info = get_provider_info()
    return {
        "session_id": session_id,
        "transcript": transcript,
        "reply": reply,
        "language": lang,
        "provider": info["provider"],
        "model": info["model"],
        "audio_base64": audio_b64,
        "audio_mime": "audio/mp3"
    }
