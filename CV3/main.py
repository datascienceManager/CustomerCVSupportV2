"""
main.py
FastAPI entry point for OTT Support API.
Serves the REST API + the static HTML chat widget demo.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from utils.database import init_db
from routers.chat import router as chat_router
from routers.voice import router as voice_router
from routers.admin import router as admin_router
from routers.tts import router as tts_router
from utils.ai_engine import AI_PROVIDER, get_provider_info

# ── Init DB ────────────────────────────────────────────────────────────────────
init_db()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="OTT Support API",
    description="Bilingual AI customer support for OTT platforms (Gemini / Ollama)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ── CORS — allow your website domain ──────────────────────────────────────────
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in raw_origins.split(",")] if raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(admin_router)
app.include_router(tts_router)

# ── Serve static files (HTML widget demo) ─────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/demo", include_in_schema=False)
async def serve_demo():
    """Serve the HTML chat widget demo page."""
    demo_path = os.path.join(static_dir, "demo.html")
    if os.path.exists(demo_path):
        return FileResponse(demo_path)
    return {"error": "Demo file not found"}

# ── Root ───────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    info = get_provider_info()
    return {
        "service": "OTT Support API",
        "version": "1.0.0",
        "provider": info["provider"],
        "model": info["model"],
        "docs": "/docs",
        "demo": "/demo",
        "endpoints": {
            "chat":     "POST /api/chat",
            "voice":    "POST /api/voice",
            "history":  "GET  /api/history/{session_id}",
            "feedback": "POST /api/feedback",
            "health":   "GET  /api/health",
            "sessions": "GET  /api/admin/sessions",
            "messages": "GET  /api/admin/messages",
            "sync":     "POST /api/admin/sync"
        }
    }

# ── Run directly ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 OTT Support API starting...")
    print(f"   Provider : {AI_PROVIDER.upper()}")
    print(f"   Model    : {get_provider_info()['model']}")
    print(f"   API Docs : http://localhost:{port}/docs")
    print(f"   Demo     : http://localhost:{port}/demo\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
