"""
utils/ai_engine.py  ─  Gemini Edition
Chat  : Google Gemini 2.0 Flash
Voice : OpenAI Whisper (transcription) + gTTS (text-to-speech)
"""
import os
import tempfile
import google.generativeai as genai
import openai
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

# ── Configure clients ──────────────────────────────────────────────────────────
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")   # Used only for Whisper

GEMINI_MODEL = "gemini-2.0-flash"

# ── System prompts ─────────────────────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "en": (
        "You are a helpful, friendly customer support agent for a premium OTT (Over-The-Top) "
        "streaming platform. You assist customers with subscription plans, billing, login issues, "
        "streaming quality, device compatibility, content availability, parental controls, "
        "cancellations, refunds, and technical troubleshooting. "
        "Be polite, concise, and empathetic. If you cannot resolve an issue, tell the customer "
        "a specialist will contact them within 24 hours. Respond in English only."
    ),
    "ar": (
        "أنت وكيل دعم عملاء ودود ومتعاون لمنصة بث OTT مميزة. تساعد العملاء في خطط الاشتراك، "
        "الفواتير، مشاكل تسجيل الدخول، جودة البث، توافق الأجهزة، توفر المحتوى، ضوابط الرقابة الأبوية، "
        "الإلغاء والاسترداد، واستكشاف الأخطاء التقنية. "
        "كن مهذبًا وموجزًا ومتعاطفًا. إذا لم تتمكن من حل المشكلة، أبلغ العميل أن متخصصًا "
        "سيتواصل معه خلال 24 ساعة. أجب باللغة العربية فقط."
    )
}

# ── Chat with Gemini ───────────────────────────────────────────────────────────
def chat_with_gemini(messages: list, language: str = "en") -> str:
    """
    Send conversation history to Gemini and return assistant reply.
    messages: [{"role": "user"/"assistant", "content": "..."}]
    """
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

    # Gemini uses 'model' instead of 'assistant' for role
    gemini_history = []
    for m in messages[:-1]:   # all but the last (current user message)
        role = "model" if m["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [m["content"]]})

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_prompt
    )
    chat = model.start_chat(history=gemini_history)

    # Send the latest user message
    last_user_msg = messages[-1]["content"] if messages else ""
    response = chat.send_message(last_user_msg)
    return response.text.strip()

# ── Whisper: audio → text ──────────────────────────────────────────────────────
def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """Transcribe audio bytes using OpenAI Whisper."""
    lang_code = "ar" if language == "ar" else "en"
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=lang_code
            )
        return transcript.text.strip()
    finally:
        os.unlink(tmp_path)

# ── gTTS: text → audio bytes ───────────────────────────────────────────────────
def text_to_speech(text: str, language: str = "en") -> bytes:
    """Convert text to speech using gTTS. Returns MP3 bytes."""
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

# ── Language detection ─────────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return "ar" if arabic_chars > len(text) * 0.2 else "en"
