"""
pages/chat_page.py  ─  Gemini Edition
"""
import streamlit as st
from utils.ai_engine import chat_with_gemini, detect_language
from utils.database import create_session, save_message, get_session_messages, get_connection
from utils.sheets import append_single_message
from datetime import datetime

LABELS = {
    "en": {
        "title": "💬 Chat Support  •  Gemini",
        "subtitle": "Hi! How can we help you today?",
        "placeholder": "Type your message here...",
        "thinking": "Gemini is thinking...",
        "feedback_title": "Rate this conversation",
        "feedback_thanks": "Thank you for your feedback!",
        "sync": "Sync to Google Sheets",
    },
    "ar": {
        "title": "💬 دعم المحادثة  •  Gemini",
        "subtitle": "مرحبًا! كيف يمكننا مساعدتك اليوم؟",
        "placeholder": "اكتب رسالتك هنا...",
        "thinking": "Gemini يفكر...",
        "feedback_title": "قيّم هذه المحادثة",
        "feedback_thanks": "شكرًا على ملاحظاتك!",
        "sync": "مزامنة مع Google Sheets",
    }
}

def get_last_message_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM messages")
    row = cur.fetchone()
    conn.close()
    return row[0] or 0

def render_chat(language: str, session_id: str):
    lbl = LABELS[language]
    if language == "ar":
        st.markdown("<style>.stChatMessage{direction:rtl;text-align:right;}</style>", unsafe_allow_html=True)

    st.title(lbl["title"])
    st.caption(lbl["subtitle"])
    st.markdown("---")

    create_session(session_id, language, "chat")

    if "messages" not in st.session_state:
        stored = get_session_messages(session_id)
        st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in stored]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(lbl["placeholder"]):
        active_lang = detect_language(prompt) or language

        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(session_id, "user", prompt, active_lang, "chat")

        with st.chat_message("assistant"):
            with st.spinner(lbl["thinking"]):
                reply = chat_with_gemini(st.session_state.messages, active_lang)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        save_message(session_id, "assistant", reply, active_lang, "chat")

        append_single_message({
            "id": get_last_message_id(),
            "session_id": session_id,
            "role": "assistant",
            "content": reply,
            "language": active_lang,
            "mode": "chat",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.expander(lbl["feedback_title"]):
            rating = st.slider("⭐", 1, 5, 3, key="chat_rating")
            comment = st.text_input("Comment (optional)", key="chat_comment")
            if st.button("Submit Feedback"):
                from utils.database import save_feedback
                save_feedback(session_id, rating, comment)
                st.success(lbl["feedback_thanks"])
    with col2:
        if st.button(lbl["sync"]):
            from utils.sheets import sync_messages_to_sheet
            from utils.database import get_all_messages_flat
            result = sync_messages_to_sheet(get_all_messages_flat())
            if result["success"]:
                st.success(f"✅ Synced! ({result['synced']} rows)")
            else:
                st.error("❌ " + result["error"])
