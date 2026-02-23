"""
pages/about_page.py
About / info page.
"""
import streamlit as st

def render_about():
    st.title("ℹ️ About This App")
    st.markdown("""
    ## 🎬 OTT Customer Support Assistant

    This AI-powered customer support system is built for OTT (streaming) platforms.

    ### ✨ Features
    - **💬 Chat Support** — Text-based AI support in English & Arabic
    - **🎙️ Voice Support** — Upload audio → Transcription (Whisper) → AI Reply → Voice playback (gTTS)
    - **🌐 Bilingual** — Automatic language detection (English / Arabic)
    - **🗄️ SQLite Storage** — All conversations saved locally
    - **📊 Google Sheets Sync** — Real-time + manual sync to Google Sheets
    - **📊 Dashboard** — Analytics and export tools

    ---

    ### 🛠️ Tech Stack
    | Component | Technology |
    |-----------|-----------|
    | AI Chat | OpenAI GPT-4o |
    | Voice Transcription | OpenAI Whisper |
    | Text-to-Speech | Google TTS (gTTS) |
    | UI | Streamlit |
    | Database | SQLite |
    | Cloud Storage | Google Sheets API |
    | Language | Python 3.11+ |

    ---

    ### 🔧 Setup
    1. Clone the repo and install requirements
    2. Copy `.env.example` to `.env` and fill in your API keys
    3. Add your `credentials.json` for Google Sheets (see README)
    4. Run `streamlit run app.py`

    ---

    ### 📞 Supported Topics
    - Subscription & billing
    - Account login / password reset
    - Streaming quality issues
    - Device compatibility
    - Content & parental controls
    - Cancellation & refunds
    """)
