"""
routers/admin.py
GET  /api/admin/sessions   — list all sessions
GET  /api/admin/messages   — list recent messages
POST /api/admin/sync       — trigger Google Sheets sync
GET  /api/health           — server + provider health check
"""
from fastapi import APIRouter
from utils.database import get_all_sessions, get_all_messages_flat
from utils.ai_engine import get_provider_info, check_ollama_running, AI_PROVIDER
from utils.sheets import sync_messages_to_sheet

router = APIRouter(tags=["admin"])

@router.get("/api/health")
async def health_check():
    info = get_provider_info()
    status = {"status": "ok", "provider": info["provider"], "model": info["model"]}

    if AI_PROVIDER == "ollama":
        status["ollama_running"] = check_ollama_running()
    else:
        status["gemini_configured"] = bool(__import__("os").getenv("GEMINI_API_KEY"))

    return status

@router.get("/api/admin/sessions")
async def list_sessions():
    sessions = get_all_sessions()
    return {"total": len(sessions), "sessions": sessions}

@router.get("/api/admin/messages")
async def list_messages(limit: int = 100):
    messages = get_all_messages_flat()[:limit]
    return {"total": len(messages), "messages": messages}

@router.post("/api/admin/sync")
async def sync_to_sheets():
    messages = get_all_messages_flat()
    result = sync_messages_to_sheet(messages)
    return result
