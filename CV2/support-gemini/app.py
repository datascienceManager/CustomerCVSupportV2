"""
app.py  ─  OTT Support Assistant (Gemini Edition)
"""
import streamlit as st
import uuid
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="OTT Support — Gemini",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.database import init_db
init_db()

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/tv-show.png", width=80)
    st.title("🔵 OTT Support")
    st.caption("Powered by Google Gemini")
    st.markdown("---")

    lang_options = {"🇬🇧 English": "en", "🇸🇦 Arabic": "ar"}
    selected_lang_label = st.selectbox("Language / اللغة", list(lang_options.keys()))
    language = lang_options[selected_lang_label]

    mode = st.radio("Support Mode", ["💬 Chat Support", "🎙️ Voice Support"])
    mode_key = "chat" if "Chat" in mode else "voice"

    st.markdown("---")
    page = st.radio("Go to", ["🏠 Support Chat", "📊 Dashboard", "ℹ️ About"])

    st.markdown("---")
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    st.caption(f"Session: `{st.session_state.session_id}`")
    st.caption("🤖 Model: Gemini 2.0 Flash")

    if st.button("🔄 New Session"):
        for key in ["session_id", "messages", "voice_messages"]:
            st.session_state.pop(key, None)
        st.rerun()

if "🏠 Support Chat" in page:
    if mode_key == "chat":
        from pages.chat_page import render_chat
        render_chat(language, st.session_state.session_id)
    else:
        from pages.voice_page import render_voice
        render_voice(language, st.session_state.session_id)
elif "📊 Dashboard" in page:
    from pages.dashboard_page import render_dashboard
    render_dashboard()
elif "ℹ️ About" in page:
    from pages.about_page import render_about
    render_about()
