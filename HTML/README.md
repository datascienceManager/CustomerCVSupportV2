For a custom website integration.

---

## 🏗️ How the Current App Works

```
User (Browser)
     │
     ▼
┌─────────────────────────────────┐
│        Streamlit App            │  ← Your UI (runs on localhost:8501)
│  ┌──────────┐  ┌─────────────┐  │
│  │ Chat Page│  │ Voice Page  │  │
└──┴──────────┴──┴─────────────┴──┘
         │               │
         ▼               ▼
┌─────────────────────────────────┐
│         utils/ai_engine.py      │  ← Talks to AI (OpenAI/Gemini/Ollama)
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│       utils/database.py         │  ← Saves to SQLite
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│        utils/sheets.py          │  ← Syncs to Google Sheets
└─────────────────────────────────┘
```

**The problem with embedding Streamlit into a custom website:** Streamlit is a standalone web app — it wasn't designed to be dropped into an existing website like a widget. It's great for quick internal tools, but for a real customer-facing website you need a proper **API backend**.

---

## ✅ The Right Architecture for a Custom Website

```
Your Website (React / HTML / WordPress / etc.)
     │
     │  HTTP requests (fetch/axios)
     ▼
┌─────────────────────────────────┐
│     FastAPI Backend (Python)    │  ← NEW: replaces Streamlit
│                                 │
│  POST /api/chat                 │
│  POST /api/voice                │
│  GET  /api/history/{session}    │
└─────────────────────────────────┘
         │               │
         ▼               ▼
    ai_engine.py    database.py
    (same code!)    (same code!)
```

You keep ALL the existing Python logic (`ai_engine.py`, `database.py`, `sheets.py`) — you just replace Streamlit with a **FastAPI** server that your website calls via HTTP.

---

## 📁 What the New Structure Looks Like

```
ott-support-api/
├── main.py              ← FastAPI server (replaces app.py)
├── routers/
│   ├── chat.py          ← /api/chat endpoint
│   └── voice.py         ← /api/voice endpoint
├── utils/
│   ├── ai_engine.py     ← SAME as before, unchanged
│   ├── database.py      ← SAME as before, unchanged
│   └── sheets.py        ← SAME as before, unchanged
├── requirements.txt
└── .env
```

---

## 🔌 How Your Website Calls It

**Chat (JavaScript fetch example):**
```javascript
// On your website — any framework
const response = await fetch("https://your-api.com/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    session_id: "user-abc123",
    message: "I can't login to my account",
    language: "en",
    provider: "openai"   // or "gemini" or "ollama"
  })
});
const data = await response.json();
console.log(data.reply);  // "I can help with that! Let me..."
```

**Voice (upload audio file):**
```javascript
const formData = new FormData();
formData.append("audio", audioBlob);
formData.append("session_id", "user-abc123");
formData.append("language", "ar");

const response = await fetch("https://your-api.com/api/voice", {
  method: "POST",
  body: formData
});
const data = await response.json();
// data.transcript = what user said
// data.reply = AI text response
// data.audio_base64 = MP3 audio to play back
```

---

## 🌐 Website Integration Options

| Your Website Type | How to Integrate |
|---|---|
| **React / Next.js** | Call the API with `fetch` or `axios`, render chat UI in a component |
| **Plain HTML/JS** | Use `fetch` directly, embed a chat widget `<div>` |
| **WordPress** | Add a custom plugin or use a JS snippet in footer |
| **Vue / Angular** | Same as React — just HTTP calls to the API |
| **Mobile App** | Same API works for iOS/Android/Flutter |

---

## ☁️ Deployment for Production

```
Your Website  →  FastAPI on  →  Cloud DB
(Vercel/etc)     Railway /       (PostgreSQL
                 Render /         instead of
                 AWS/GCP          SQLite)
```

For real production you'd also want to:
- Replace **SQLite → PostgreSQL** (handles multiple users at once)
- Add **authentication** (JWT tokens so only your users can call the API)
- Add **rate limiting** (so users can't spam the AI)
- Use **HTTPS** (SSL certificate)

---

Would you like me to build the **FastAPI version** of this project that's ready to plug into any custom website? I can include a sample HTML chat widget too so you can see it working end-to-end. Just let me know which AI provider (OpenAI / Gemini / Ollama) to build it for first!
