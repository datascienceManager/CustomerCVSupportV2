"""
pages/voice_page.py  ─  Gemini Edition
Whisper transcription → Gemini reply → gTTS playback
"""
import streamlit as st
from utils.ai_engine import transcribe_audio, chat_with_gemini, text_to_speech, detect_language
from utils.database import create_session, save_message, get_session_messages, get_connection
from utils.sheets import append_single_message
from datetime import datetime

LABELS = {
    "en": {
        "title": "🎙️ Voice Support  •  Gemini",
        "subtitle": "Upload an audio file and get a voice response powered by Gemini",
        "upload_label": "Upload audio (WAV / MP3 / M4A)",
        "transcribed": "📝 You said:",
        "ai_reply": "🤖 Gemini replied:",
        "thinking": "Processing with Gemini...",
        "no_audio": "Please upload an audio file first.",
        "history": "📜 Conversation History"
    },
    "ar": {
        "title": "🎙️ دعم صوتي  •  Gemini",
        "subtitle": "ارفع ملفًا صوتيًا واحصل على رد صوتي مدعوم بـ Gemini",
        "upload_label": "رفع ملف صوتي (WAV / MP3 / M4A)",
        "transcribed": "📝 قلت:",
        "ai_reply": "🤖 ردّ Gemini:",
        "thinking": "جاري المعالجة مع Gemini...",
        "no_audio": "يرجى رفع ملف صوتي أولاً.",
        "history": "📜 سجل المحادثة"
    }
}

def get_last_message_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM messages")
    row = cur.fetchone()
    conn.close()
    return row[0] or 0

def render_voice(language: str, session_id: str):
    lbl = LABELS[language]
    st.title(lbl["title"])
    st.caption(lbl["subtitle"])
    st.markdown("---")

    create_session(session_id, language, "voice")

    if "voice_messages" not in st.session_state:
        stored = get_session_messages(session_id)
        st.session_state.voice_messages = [{"role": m["role"], "content": m["content"]} for m in stored]

    st.info("💡 Record a WAV/MP3 with your phone or mic recorder, then upload below.")
    audio_file = st.file_uploader(lbl["upload_label"], type=["wav", "mp3", "m4a", "ogg", "webm"])

    if st.button("🚀 Process Audio", disabled=audio_file is None):
        if not audio_file:
            st.warning(lbl["no_audio"])
        else:
            with st.spinner(lbl["thinking"]):
                audio_bytes = audio_file.read()
                user_text = transcribe_audio(audio_bytes, language)
                active_lang = detect_language(user_text)

                st.success(f"{lbl['transcribed']} **{user_text}**")
                save_message(session_id, "user", user_text, active_lang, "voice")
                st.session_state.voice_messages.append({"role": "user", "content": user_text})

                reply = chat_with_gemini(st.session_state.voice_messages, active_lang)
                st.info(f"{lbl['ai_reply']} **{reply}**")

                save_message(session_id, "assistant", reply, active_lang, "voice")
                st.session_state.voice_messages.append({"role": "assistant", "content": reply})

                append_single_message({
                    "id": get_last_message_id(),
                    "session_id": session_id,
                    "role": "assistant",
                    "content": reply,
                    "language": active_lang,
                    "mode": "voice",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                tts_audio = text_to_speech(reply, active_lang)
                st.audio(tts_audio, format="audio/mp3")

    st.markdown("---")
    st.subheader(lbl["history"])
    for msg in st.session_state.get("voice_messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    if st.button("📤 Sync to Google Sheets"):
        from utils.sheets import sync_messages_to_sheet
        from utils.database import get_all_messages_flat
        result = sync_messages_to_sheet(get_all_messages_flat())
        if result["success"]:
            st.success(f"✅ Synced! ({result['synced']} new rows)")
        else:
            st.error("❌ " + result["error"])
