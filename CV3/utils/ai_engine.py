"""
utils/ai_engine.py
Unified AI engine — switches between Gemini and Ollama via AI_PROVIDER env var.
Voice: OpenAI Whisper (transcription) + gTTS (text-to-speech) for both providers.
"""
import os
import tempfile
import requests
import openai
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

# ── Provider config ────────────────────────────────────────────────────────────
AI_PROVIDER  = os.getenv("AI_PROVIDER", "gemini").lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Lazy-load Gemini only if needed
_gemini_configured = False
def _ensure_gemini():
    global _gemini_configured
    if not _gemini_configured:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        _gemini_configured = True

# ── System prompts ─────────────────────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "en": (
        "You are a helpful, friendly customer support agent for a premium OTT streaming platform. "
        "You assist customers with subscription plans, billing, login issues, streaming quality, "
        "device compatibility, content availability, parental controls, cancellations, refunds, "
        "and technical troubleshooting. Be polite, concise, and empathetic. "
        "If you cannot resolve an issue, tell the customer a specialist will contact them within 24 hours. "
        "Keep replies short (2-4 sentences). Respond in English only."
    ),
    "ar": (
        "أنت وكيل دعم عملاء ودود لمنصة بث OTT مميزة. تساعد العملاء في خطط الاشتراك، الفواتير، "
        "مشاكل تسجيل الدخول، جودة البث، توافق الأجهزة، توفر المحتوى، ضوابط الرقابة الأبوية، "
        "الإلغاء والاسترداد، واستكشاف الأخطاء التقنية. "
        "كن مهذبًا وموجزًا ومتعاطفًا. أجب باللغة العربية فقط. الردود قصيرة (2-4 جمل)."
    )
}

# ── Language detection ─────────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return "ar" if arabic_chars > len(text) * 0.2 else "en"

# ── Provider info ──────────────────────────────────────────────────────────────
def get_provider_info() -> dict:
    return {
        "provider": AI_PROVIDER,
        "model": GEMINI_MODEL if AI_PROVIDER == "gemini" else OLLAMA_MODEL,
        "ollama_host": OLLAMA_HOST if AI_PROVIDER == "ollama" else None
    }

# ── Ollama health check ────────────────────────────────────────────────────────
def check_ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

# ── Main chat function (routes to correct provider) ───────────────────────────
def chat(messages: list, language: str = "en") -> str:
    """
    Route to Gemini or Ollama based on AI_PROVIDER env var.
    messages: [{"role": "user"/"assistant", "content": "..."}]
    """
    if AI_PROVIDER == "gemini":
        return _chat_gemini(messages, language)
    elif AI_PROVIDER == "ollama":
        return _chat_ollama(messages, language)
    else:
        return f"⚠️ Unknown AI_PROVIDER: '{AI_PROVIDER}'. Set to 'gemini' or 'ollama' in .env"

# ── Gemini chat ────────────────────────────────────────────────────────────────
def _chat_gemini(messages: list, language: str = "en") -> str:
    _ensure_gemini()
    import google.generativeai as genai

    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

    # Build Gemini history (all but last message)
    history = []
    for m in messages[:-1]:
        role = "model" if m["role"] == "assistant" else "user"
        history.append({"role": role, "parts": [m["content"]]})

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_prompt
    )
    chat_session = model.start_chat(history=history)
    last_msg = messages[-1]["content"] if messages else ""
    response = chat_session.send_message(last_msg)
    return response.text.strip()

# ── Ollama chat ────────────────────────────────────────────────────────────────
def _chat_ollama(messages: list, language: str = "en") -> str:
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

    ollama_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        role = "assistant" if m["role"] == "assistant" else "user"
        ollama_messages.append({"role": role, "content": m["content"]})

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": ollama_messages,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 300}
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Cannot connect to Ollama. Please run: `ollama serve` "
            "and ensure llama3 is pulled: `ollama pull llama3`"
        )
    except Exception as e:
        return f"⚠️ Ollama error: {str(e)}"

# ── Whisper transcription ──────────────────────────────────────────────────────
def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    lang_code = "ar" if language == "ar" else "en"
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", file=f, language=lang_code
            )
        return transcript.text.strip()
    finally:
        os.unlink(tmp_path)

# ── gTTS text-to-speech ────────────────────────────────────────────────────────
def text_to_speech(text: str, language: str = "en") -> bytes:
    lang_code = "ar" if language == "ar" else "en"
    tts = gTTS(text=text, lang=lang_code, slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp_path)
