# 🔵 OTT Support Assistant — Gemini Edition

Bilingual (English/Arabic) OTT customer support powered by **Google Gemini 2.0 Flash**.

---

## 🛠️ Tech Stack
| Component | Technology |
|-----------|-----------|
| AI Chat | Google Gemini 2.0 Flash |
| Voice Transcription | OpenAI Whisper |
| Text-to-Speech | gTTS |
| UI | Streamlit |
| Database | SQLite |
| Cloud Sync | Google Sheets API |

---

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/YOUR_USERNAME/ott-support-gemini.git
cd ott-support-gemini
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env — add GEMINI_API_KEY, OPENAI_API_KEY, GOOGLE_SHEET_ID

# 3. Run
streamlit run app.py
```

---

## 🔑 API Keys

### Gemini API Key
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Create a new key
3. Add to `.env` as `GEMINI_API_KEY`

### OpenAI API Key (Whisper only)
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Add to `.env` as `OPENAI_API_KEY`

> 💡 **Tip:** Gemini has a generous free tier — great for testing without cost!

---

## 📊 Google Sheets Setup
See the original OpenAI project README for full Google Sheets setup steps.
The process is identical for all three projects.

---

## 🐙 Push to GitHub

```bash
git init && git add . && git commit -m "OTT Support - Gemini Edition"
git remote add origin https://github.com/YOUR_USERNAME/ott-support-gemini.git
git push -u origin main
```

> ⚠️ Never commit `.env` or `credentials.json`
