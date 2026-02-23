"""
routers/chat.py
POST /api/chat  — text chat endpoint
GET  /api/history/{session_id}  — fetch conversation history
POST /api/feedback  — submit star rating
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from utils.ai_engine import chat, detect_language, get_provider_info, AI_PROVIDER
from utils.database import (
    create_session, save_message, get_session_messages,
    get_last_message_id, save_feedback
)
from utils.sheets import append_single_message

router = APIRouter(prefix="/api", tags=["chat"])

# ── Request / Response models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = "auto"   # "en", "ar", or "auto"

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    language: str
    provider: str
    model: str

class FeedbackRequest(BaseModel):
    session_id: str
    rating: int          # 1-5
    comment: Optional[str] = ""

# ── Endpoints ──────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # Resolve language
    if req.language == "auto":
        lang = detect_language(req.message)
    else:
        lang = req.language if req.language in ("en", "ar") else "en"

    # Ensure session exists
    create_session(req.session_id, lang, "chat")

    # Load history and append new user message
    history = get_session_messages(req.session_id)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": req.message})

    # Save user message
    save_message(req.session_id, "user", req.message, lang, "chat", AI_PROVIDER)

    # Get AI reply
    reply = chat(messages, lang)

    # Save assistant message
    save_message(req.session_id, "assistant", reply, lang, "chat", AI_PROVIDER)

    # Sync to Google Sheets (best effort, non-blocking)
    try:
        msg_id = get_last_message_id()
        append_single_message({
            "id": msg_id,
            "session_id": req.session_id,
            "role": "assistant",
            "content": reply,
            "language": lang,
            "mode": "chat",
            "provider": AI_PROVIDER,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception:
        pass  # Don't fail the request if Sheets sync fails

    info = get_provider_info()
    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        language=lang,
        provider=info["provider"],
        model=info["model"]
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    messages = get_session_messages(session_id)
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": messages
    }


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    if not 1 <= req.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    save_feedback(req.session_id, req.rating, req.comment or "")
    return {"success": True, "message": "Feedback saved. Thank you!"}
