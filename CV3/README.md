# Support API — FastAPI Backend + Floating Chat Widget

A production-ready AI customer support API for OTT platforms with a dark floating chat bubble
that embeds into **any website with a single `<script>` tag**.

Supports **Gemini 2.0 Flash** and **Ollama llama3** — switch with one line in `.env`.

---

## 🏗️ Project Structure

```
ott-support-api/
├── main.py                  ← FastAPI app entry point
├── routers/
│   ├── chat.py              ← POST /api/chat, GET /api/history, POST /api/feedback
│   ├── voice.py             ← POST /api/voice
│   └── admin.py             ← GET /api/health, /api/admin/sessions, POST /api/admin/sync
├── utils/
│   ├── ai_engine.py         ← Gemini + Ollama + Whisper + gTTS (unified)
│   ├── database.py          ← SQLite operations
│   └── sheets.py            ← Google Sheets sync
├── static/
│   ├── demo.html            ← Live demo page (visit /demo)
│   └── widget.js            ← Embeddable chat widget for any website
├── data/
│   └── conversations.db     ← Auto-created SQLite database
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/YOUR_USERNAME/ott-support-api.git
cd ott-support-api
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env (see Configuration section below)

# 3. Run
python main.py
```

Open:
- **API Docs**: http://localhost:8000/docs
- **Live Demo**: http://localhost:8000/demo
- **Health Check**: http://localhost:8000/api/health

---

## ⚙️ Configuration (.env)

```env
# Switch between providers with ONE line:
AI_PROVIDER=gemini     # or: ollama

# Gemini (if AI_PROVIDER=gemini)
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash

# Ollama (if AI_PROVIDER=ollama)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# OpenAI Whisper — voice transcription (both providers)
OPENAI_API_KEY=your_key_here

# Google Sheets
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=credentials.json

# CORS — your website domain(s), comma-separated
ALLOWED_ORIGINS=https://yourwebsite.com,https://www.yourwebsite.com
# Use * for local development only
```

---

## 🌐 Embed on Any Website

### Option 1 — Script tag (recommended)
```html
<!-- Add to your website's <body> — that's it! -->
<script
  src="https://your-api.com/static/widget.js"
  data-api="https://your-api.com"
  data-lang="en">
</script>
```

### Option 2 — Inline in HTML
Copy the contents of `static/widget.js` into a `<script>` block on your page.

### Option 3 — WordPress
1. Go to **Appearance → Theme Editor → footer.php**
2. Paste the `<script>` tag before `</body>`

### Option 4 — React / Next.js
```jsx
useEffect(() => {
  const script = document.createElement("script");
  script.src = "https://your-api.com/static/widget.js";
  script.setAttribute("data-api", "https://your-api.com");
  document.body.appendChild(script);
  return () => document.body.removeChild(script);
}, []);
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Service info + endpoint list |
| `GET`  | `/api/health` | Provider health check |
| `POST` | `/api/chat` | Send a chat message |
| `GET`  | `/api/history/{session_id}` | Get conversation history |
| `POST` | `/api/feedback` | Submit star rating |
| `POST` | `/api/voice` | Upload audio → transcript + reply + TTS |
| `GET`  | `/api/admin/sessions` | List all sessions |
| `GET`  | `/api/admin/messages` | List recent messages |
| `POST` | `/api/admin/sync` | Sync all to Google Sheets |
| `GET`  | `/demo` | Live widget demo page |
| `GET`  | `/docs` | Interactive API docs (Swagger) |

### POST /api/chat — Example
```json
// Request
{
  "session_id": "sess_abc123",
  "message": "I can't login to my account",
  "language": "en"
}

// Response
{
  "session_id": "sess_abc123",
  "reply": "I'm sorry to hear that! Let me help you...",
  "language": "en",
  "provider": "gemini",
  "model": "gemini-2.0-flash"
}
```

---

## 🔵 Gemini Setup
1. Go to https://aistudio.google.com/app/apikey
2. Create a free API key
3. Add to `.env` as `GEMINI_API_KEY=...`
4. Set `AI_PROVIDER=gemini`

## 🦙 Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh   # macOS/Linux
# Windows: download from https://ollama.com/download

# Pull llama3 (~4.7GB, one time only)
ollama pull llama3

# Keep running in a terminal
ollama serve
```
Then set `AI_PROVIDER=ollama` in `.env`.

---

## 📊 Google Sheets Setup
1. Go to https://console.cloud.google.com → Create project
2. Enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** → Download JSON → rename to `credentials.json`
4. Create a Google Sheet → copy the Sheet ID from the URL
5. Share the sheet with the service account email (Editor access)
6. Add `GOOGLE_SHEET_ID=...` to `.env`

---

## ☁️ Deploy to Production

### Railway (easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

### Render
1. Push to GitHub
2. New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in the Render dashboard

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔒 Production Checklist

- [ ] Set `ALLOWED_ORIGINS` to your real domain (not `*`)
- [ ] Use HTTPS (SSL certificate via your host or Cloudflare)
- [ ] Replace SQLite with PostgreSQL for multi-user scale
- [ ] Add API key authentication for admin endpoints
- [ ] Set rate limiting (e.g., 20 requests/minute per IP)

---

## 🐙 GitHub

```bash
git init && git add .
git commit -m "OTT Support API — FastAPI + Floating Chat Widget"
git remote add origin https://github.com/YOUR_USERNAME/ott-support-api.git
git push -u origin main
```


 ElevenLabs fully supports Arabic**, and it's actually significantly better than gTTS for Arabic

---

## ElevenLabs Arabic Support (2025)

### 🔊 Text-to-Speech (Arabic voices)
ElevenLabs supports **Arabic (Saudi Arabia, UAE)** across its Multilingual v2 and Eleven v3 models. And there's a large library of Arabic voices available — Egyptian, Gulf, Modern Standard Arabic, Moroccan Darija — both male and female, for different use cases like narration, customer service, podcasts, and storytelling.

### 🎙️ Speech-to-Text (Arabic transcription)
ElevenLabs' **Scribe** model supports Arabic transcription across multiple dialects including Modern Standard Arabic, Egyptian, Levantine, Gulf, and Maghrebi.

### 🤖 Conversational AI (Real-time voice agent)
ElevenLabs Conversational AI supports **automatic language detection and seamless in-conversation switching across 32+ languages**, with sub-100ms latency. Conversational AI 2.0 introduced automatic language detection directly into the agent, allowing it to identify the language being spoken and respond appropriately within the same interaction — enabling seamless multilingual discussions without manual configuration.

---

## 📊 ElevenLabs vs gTTS for Arabic

| Feature | gTTS (current) | ElevenLabs |
|---|---|---|
| **Arabic TTS quality** | Basic, robotic | Human-like, expressive |
| **Arabic dialects** | MSA only | Egyptian, Gulf, Levantine, MSA |
| **Real-time STT** | ❌ (uses Whisper) | ✅ Scribe (99 languages) |
| **Conversational AI** | ❌ | ✅ Full voice agent platform |
| **Auto language detect** | ❌ | ✅ Built-in |
| **Latency** | ~2-3 sec | Sub-100ms (Flash model) |
| **Voice cloning** | ❌ | ✅ |
| **Cost** | Free | Paid (free tier: 10k chars/month) |
| **API** | Simple | Full SDK (Python, JS, Swift) |

---

## 🚀 What This Means for Your OTT Project

You could replace gTTS with ElevenLabs to get a **dramatically better Arabic voice experience**:

```python
# Current (gTTS) — robotic, basic
tts = gTTS(text=reply, lang="ar")

# With ElevenLabs — human-like, natural Arabic
from elevenlabs import ElevenLabs
client = ElevenLabs(api_key="your_key")
audio = client.text_to_speech.convert(
    text=reply,
    voice_id="arabic_voice_id",   # pick from their Arabic voice library
    model_id="eleven_multilingual_v2"
)
```

Or even better — use **ElevenLabs Conversational AI** which handles the entire loop (mic → STT → LLM → TTS → speaker) as a single real-time WebSocket connection, replacing your current Web Speech API + gTTS setup entirely.

---

Would you like me to upgrade the project to use **ElevenLabs** instead of gTTS for the Arabic TTS, or go further and integrate the full **ElevenLabs Conversational AI** platform for a true real-time voice agent?
