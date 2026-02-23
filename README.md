# 🦙 OTT Support Assistant — Ollama Edition (100% Local)

Bilingual (English/Arabic) OTT customer support powered by **Ollama llama3** running entirely on your machine. **No cloud AI costs!**

---

## 🛠️ Tech Stack
| Component | Technology |
|-----------|-----------|
| AI Chat | Ollama llama3 (local) |
| Voice Transcription | OpenAI Whisper |
| Text-to-Speech | gTTS |
| UI | Streamlit |
| Database | SQLite |
| Cloud Sync | Google Sheets API |

---

## ⚙️ Install Ollama First

### macOS / Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Download from [https://ollama.com/download](https://ollama.com/download)

### Pull llama3 model
```bash
ollama pull llama3
```
> This downloads ~4.7GB. Only needed once.

### Start Ollama server
```bash
ollama serve
```
> Keep this running in a terminal while using the app.

---

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/YOUR_USERNAME/ott-support-ollama.git
cd ott-support-ollama
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env — add OPENAI_API_KEY (for Whisper), GOOGLE_SHEET_ID

# 3. Start Ollama (separate terminal)
ollama serve

# 4. Run app
streamlit run app.py
```

---

## 🔄 Switching Models

You can use any Ollama model by changing `.env`:
```
OLLAMA_MODEL=llama3        # recommended
OLLAMA_MODEL=mistral       # smaller, faster
OLLAMA_MODEL=gemma2        # Google's model
OLLAMA_MODEL=phi3          # Microsoft's model
```

Then pull the model: `ollama pull mistral`

---

## 🔑 API Keys Needed

| Key | Purpose |
|-----|---------|
| `OPENAI_API_KEY` | Whisper voice transcription only |
| `GOOGLE_SHEET_ID` | Google Sheets sync (optional) |

> The chat itself uses **zero external API calls** — llama3 runs 100% locally!

---

## 📊 Google Sheets Setup
See the original OpenAI project README for full Google Sheets setup steps.
The process is identical for all three projects.

---

## 💻 System Requirements for llama3

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Disk | 5 GB | 10 GB |
| CPU | Modern 4-core | 8+ cores |
| GPU | Optional | NVIDIA/AMD GPU for faster responses |

---

## 🐙 Push to GitHub

```bash
git init && git add . && git commit -m "OTT Support - Ollama Edition"
git remote add origin https://github.com/YOUR_USERNAME/ott-support-ollama.git
git push -u origin main
```

> ⚠️ Never commit `.env` or `credentials.json`
