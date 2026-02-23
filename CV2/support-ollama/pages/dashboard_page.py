"""
pages/dashboard_page.py
Admin dashboard showing conversation analytics.
"""
import streamlit as st
import sqlite3
import os
from utils.database import get_all_sessions, get_all_messages_flat, DB_PATH

def render_dashboard():
    st.title("📊 Conversation Dashboard")
    st.markdown("---")

    sessions = get_all_sessions()
    messages = get_all_messages_flat()

    if not sessions:
        st.info("No conversations yet. Start a support chat to see data here.")
        return

    # ── KPI cards ──────────────────────────────────────────────────────────────
    total_sessions = len(sessions)
    total_messages = len(messages)
    en_msgs = sum(1 for m in messages if m.get("language") == "en")
    ar_msgs = sum(1 for m in messages if m.get("language") == "ar")
    voice_msgs = sum(1 for m in messages if m.get("mode") == "voice")
    chat_msgs = sum(1 for m in messages if m.get("mode") == "chat")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sessions", total_sessions)
    col2.metric("Total Messages", total_messages)
    col3.metric("🇬🇧 English", en_msgs)
    col4.metric("🇸🇦 Arabic", ar_msgs)

    col5, col6 = st.columns(2)
    col5.metric("💬 Chat Messages", chat_msgs)
    col6.metric("🎙️ Voice Messages", voice_msgs)

    st.markdown("---")

    # ── Sessions table ─────────────────────────────────────────────────────────
    st.subheader("📋 Recent Sessions")
    import pandas as pd
    df_sessions = pd.DataFrame(sessions)
    if not df_sessions.empty:
        df_sessions.columns = ["Session ID", "Language", "Mode", "Created At", "Messages"]
        st.dataframe(df_sessions, use_container_width=True)

    st.markdown("---")

    # ── Message log ────────────────────────────────────────────────────────────
    st.subheader("📨 Recent Messages (last 50)")
    df_msgs = pd.DataFrame(messages[:50])
    if not df_msgs.empty:
        st.dataframe(df_msgs[["session_id", "role", "content", "language", "mode", "timestamp"]],
                     use_container_width=True)

    st.markdown("---")

    # ── Google Sheets sync ─────────────────────────────────────────────────────
    st.subheader("☁️ Google Sheets Sync")
    if st.button("🔄 Sync All Conversations to Google Sheets"):
        from utils.sheets import sync_messages_to_sheet
        with st.spinner("Syncing..."):
            result = sync_messages_to_sheet(messages)
        if result["success"]:
            st.success(f"✅ Synced {result['synced']} new messages to Google Sheets!")
        else:
            st.error(f"❌ Failed: {result['error']}")
            st.info("Make sure your `credentials.json` and `GOOGLE_SHEET_ID` are configured. See README.md.")

    # ── DB download ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("⬇️ Export Data")
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            st.download_button(
                label="Download SQLite Database",
                data=f,
                file_name="conversations.db",
                mime="application/octet-stream"
            )
    if messages:
        import pandas as pd
        csv = pd.DataFrame(messages).to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="conversations.csv",
            mime="text/csv"
        )
