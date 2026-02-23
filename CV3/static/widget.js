/**
 * OTT Support Chat + Voice Widget  v2.0
 * Embed on any website with ONE line:
 *
 *   <script src="https://your-api.com/static/widget.js"
 *           data-api="https://your-api.com"
 *           data-lang="en">
 *   </script>
 *
 * Features:
 *  - 💬 Text chat  (Gemini or Ollama backend)
 *  - 🎤 Real-time voice via Web Speech API (no file upload, no extra API key)
 *  - 🌊 Live mic waveform driven by AudioContext analyser
 *  - 🔊 AI voice reply auto-played via gTTS from backend
 *  - 🌐 English & Arabic with RTL support
 *  - 📝 Transcript shown in chat after each voice turn
 *  - 💾 Conversation saved to SQLite + Google Sheets
 */
(function () {
  "use strict";

  /* ── Read config from <script> tag ─────────────────────────────────────── */
  const scriptTag = document.currentScript || (() => {
    const s = document.getElementsByTagName("script");
    return s[s.length - 1];
  })();

  const API  = (scriptTag.getAttribute("data-api") || "http://localhost:8000").replace(/\/$/, "");
  const DLANG = scriptTag.getAttribute("data-lang") || "en";

  /* ── Session ────────────────────────────────────────────────────────────── */
  let sid = sessionStorage.getItem("_ott_sid");
  if (!sid) { sid = "s_" + Math.random().toString(36).slice(2, 9); sessionStorage.setItem("_ott_sid", sid); }

  let lang      = DLANG;
  let mode      = "chat";
  let isOpen    = false;
  let exchanges = 0;

  /* ── Labels ─────────────────────────────────────────────────────────────── */
  const L = {
    en: {
      ph:"Type your message…", welcome:"👋 Hi! How can I help you today?",
      rLbl:"How was your experience?", rThanks:"Thanks for the feedback! 🙏",
      micIdle:"Click the mic to speak", micOn:"Listening… click to stop",
      micProc:"Sending to AI…", micErr:"⚠️ Mic denied. Allow microphone access.",
      micNone:"⚠️ Voice not supported. Use Chrome or Edge.",
      playLbl:"Playing response…", hint:"Chrome · Edge · Safari | Allow mic"
    },
    ar: {
      ph:"اكتب رسالتك هنا…", welcome:"👋 مرحبًا! كيف يمكنني مساعدتك اليوم؟",
      rLbl:"كيف كانت تجربتك؟", rThanks:"شكرًا على ملاحظاتك! 🙏",
      micIdle:"انقر على الميكروفون", micOn:"جاري الاستماع… انقر للإيقاف",
      micProc:"جاري الإرسال…", micErr:"⚠️ تم رفض الميكروفون.",
      micNone:"⚠️ الصوت غير مدعوم. استخدم Chrome أو Edge.",
      playLbl:"جاري تشغيل الرد…", hint:"Chrome · Edge · Safari | اسمح بالميكروفون"
    }
  };

  const CHIPS = {
    en: ["Can't login","Billing issue","Streaming quality","Cancel subscription"],
    ar: ["لا أستطيع تسجيل الدخول","مشكلة في الفاتورة","جودة البث","إلغاء الاشتراك"]
  };

  /* ── Inject CSS ──────────────────────────────────────────────────────────── */
  const css = document.createElement("style");
  css.textContent = `
  #_ob{position:fixed;bottom:24px;right:24px;width:60px;height:60px;border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#2563eb);border:none;cursor:pointer;
    box-shadow:0 8px 28px rgba(124,58,237,.5);display:flex;align-items:center;
    justify-content:center;z-index:99998;transition:transform .2s,box-shadow .2s;}
  #_ob:hover{transform:scale(1.08);box-shadow:0 14px 44px rgba(124,58,237,.65);}
  #_ob svg{width:26px;height:26px;fill:#fff;pointer-events:none;}
  #_on{position:fixed;bottom:74px;right:22px;width:13px;height:13px;background:#f43f5e;
    border-radius:50%;border:2px solid #fff;z-index:99999;animation:_op 2s infinite;}
  @keyframes _op{0%,100%{transform:scale(1)}50%{transform:scale(1.25);opacity:.7}}
  #_ow{position:fixed;bottom:98px;right:24px;width:380px;max-width:calc(100vw - 32px);
    height:600px;max-height:calc(100vh - 120px);background:#11111a;border:1px solid #22223a;
    border-radius:20px;box-shadow:0 28px 90px rgba(0,0,0,.7);display:none;
    flex-direction:column;overflow:hidden;z-index:99997;font-family:'Segoe UI',system-ui,sans-serif;}
  #_ow.open{display:flex;animation:_ou .22s ease;}
  @keyframes _ou{from{opacity:0;transform:translateY(16px) scale(.97)}to{opacity:1;transform:none}}
  ._oh{background:linear-gradient(135deg,#16162a,#1a1a30);padding:14px 16px;
    display:flex;align-items:center;gap:10px;border-bottom:1px solid #22223a;flex-shrink:0;}
  ._oav{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#2563eb);
    display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
  ._oht{flex:1;}._oht h3{font-size:.88rem;font-weight:600;color:#e2e8f0;margin:0;}
  ._os{display:flex;align-items:center;gap:4px;font-size:.68rem;color:#64748b;}
  ._od{width:6px;height:6px;border-radius:50%;background:#22c55e;animation:_op 2.5s infinite;}
  ._oha{display:flex;gap:5px;align-items:center;}
  ._olb{background:#1a1a2e;border:1px solid #2d2d48;color:#94a3b8;border-radius:7px;
    padding:3px 8px;font-size:.7rem;cursor:pointer;transition:all .15s;font-family:inherit;}
  ._olb.on,._olb:hover{background:#7c3aed;border-color:#7c3aed;color:#fff;}
  ._ocb{background:transparent;border:none;color:#4a5568;cursor:pointer;font-size:18px;
    padding:2px 4px;border-radius:5px;line-height:1;transition:color .15s,background .15s;}
  ._ocb:hover{color:#e2e8f0;background:#22223a;}
  ._tabs{display:flex;background:#0f0f18;border-bottom:1px solid #22223a;flex-shrink:0;}
  ._tab{flex:1;padding:9px;border:none;background:transparent;color:#4a5568;font-size:.78rem;
    font-family:inherit;cursor:pointer;display:flex;align-items:center;justify-content:center;
    gap:5px;border-bottom:2px solid transparent;transition:all .15s;}
  ._tab.on{color:#a78bfa;border-bottom-color:#7c3aed;background:#16162a;}
  ._tab:hover:not(.on){color:#94a3b8;background:#14141f;}
  ._msgs{flex:1;overflow-y:auto;padding:12px 12px 6px;display:flex;flex-direction:column;
    gap:10px;scroll-behavior:smooth;}
  ._msgs::-webkit-scrollbar{width:3px;}
  ._msgs::-webkit-scrollbar-thumb{background:#2d2d48;border-radius:3px;}
  ._m{display:flex;flex-direction:column;max-width:84%;gap:3px;}
  ._m.u{align-self:flex-end;align-items:flex-end;}
  ._m.b{align-self:flex-start;align-items:flex-start;}
  ._m.rtl{direction:rtl;}
  ._bub{padding:9px 13px;border-radius:14px;font-size:.84rem;line-height:1.5;word-break:break-word;}
  ._m.u ._bub{background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#f3f0ff;border-bottom-right-radius:3px;}
  ._m.b ._bub{background:#1c1c2e;color:#c8d0e0;border:1px solid #2a2a42;border-bottom-left-radius:3px;}
  ._mm{display:flex;align-items:center;gap:3px;}
  ._vb{font-size:.6rem;color:#a78bfa;}._mt{font-size:.62rem;color:#3d4a5c;padding:0 2px;}
  ._typ ._bub{background:#1c1c2e;border:1px solid #2a2a42;padding:11px 14px;}
  ._dots{display:flex;gap:4px;align-items:center;}
  ._dots span{width:6px;height:6px;background:#7c3aed;border-radius:50%;animation:_db 1.2s infinite;}
  ._dots span:nth-child(2){animation-delay:.2s;}._dots span:nth-child(3){animation-delay:.4s;}
  @keyframes _db{0%,80%,100%{transform:translateY(0);opacity:.35}40%{transform:translateY(-5px);opacity:1}}
  ._chips{display:flex;flex-wrap:wrap;gap:5px;padding:0 12px 7px;}
  ._chip{background:#1a1a2e;border:1px solid #2d2d48;border-radius:999px;color:#a78bfa;
    font-size:.72rem;padding:4px 11px;cursor:pointer;transition:all .15s;white-space:nowrap;font-family:inherit;}
  ._chip:hover{background:#7c3aed;border-color:#7c3aed;color:#fff;}
  ._tbar{padding:9px 12px;border-top:1px solid #22223a;display:flex;gap:6px;align-items:flex-end;
    background:#11111a;flex-shrink:0;}
  ._ta{flex:1;background:#1a1a2e;border:1px solid #2d2d48;border-radius:11px;color:#e2e8f0;
    font-size:.84rem;padding:8px 12px;resize:none;min-height:38px;max-height:88px;outline:none;
    font-family:inherit;line-height:1.4;transition:border-color .15s;}
  ._ta::placeholder{color:#3d4a5c;}._ta:focus{border-color:#7c3aed;}
  ._sb{width:38px;height:38px;background:linear-gradient(135deg,#7c3aed,#2563eb);border:none;
    border-radius:10px;cursor:pointer;display:flex;align-items:center;justify-content:center;
    flex-shrink:0;transition:transform .15s,opacity .15s;}
  ._sb:hover:not(:disabled){transform:scale(1.06);}._sb:disabled{opacity:.4;cursor:not-allowed;}
  ._sb svg{width:16px;height:16px;fill:#fff;}
  ._vp{display:none;flex-direction:column;align-items:center;justify-content:center;
    padding:18px;gap:16px;flex:1;background:#0f0f18;}
  ._vp.show{display:flex;}
  ._vst{font-size:.8rem;color:#64748b;text-transform:uppercase;letter-spacing:.04em;
    font-weight:500;min-height:18px;text-align:center;}
  ._wf{display:flex;align-items:center;justify-content:center;gap:3px;height:50px;width:210px;}
  ._wb{width:4px;border-radius:3px;background:linear-gradient(to top,#5b21b6,#a78bfa);
    height:4px;transition:height .07s ease;opacity:.2;}
  ._wf.act ._wb{opacity:1;}
  @keyframes _wi{0%,100%{height:4px}50%{height:18px}}
  ._mr{position:relative;width:100px;height:100px;display:flex;align-items:center;justify-content:center;}
  ._rp{position:absolute;inset:0;border-radius:50%;border:2px solid #7c3aed;opacity:0;transition:opacity .3s;}
  ._mr.rec ._rp{opacity:.7;animation:_rpa 1.1s ease-out infinite;}
  @keyframes _rpa{0%{transform:scale(1);opacity:.7}100%{transform:scale(1.7);opacity:0}}
  ._mb{width:78px;height:78px;border-radius:50%;border:none;cursor:pointer;position:relative;z-index:1;
    background:linear-gradient(135deg,#2d2d48,#1a1a2e);display:flex;align-items:center;
    justify-content:center;transition:all .22s;box-shadow:0 4px 20px rgba(0,0,0,.5);}
  ._mb:hover:not(:disabled){transform:scale(1.05);}
  ._mb.rec{background:linear-gradient(135deg,#7c3aed,#5b21b6);box-shadow:0 8px 32px rgba(124,58,237,.6);}
  ._mb svg{width:34px;height:34px;fill:#64748b;transition:fill .2s;}._mb.rec svg{fill:#fff;}
  ._mb:disabled{opacity:.45;cursor:not-allowed;}
  ._ltx{min-height:36px;max-height:66px;overflow-y:auto;font-size:.8rem;color:#94a3b8;
    text-align:center;line-height:1.5;padding:6px 10px;background:#1a1a2e;border:1px solid #2d2d48;
    border-radius:10px;width:100%;display:none;word-break:break-word;}
  ._ltx.show{display:block;}
  ._np{display:none;align-items:center;gap:7px;font-size:.76rem;color:#a78bfa;}
  ._np.show{display:flex;}
  ._pb{display:flex;gap:3px;align-items:center;}
  ._pb span{width:3px;border-radius:2px;background:#7c3aed;animation:_pba .8s ease-in-out infinite;}
  ._pb span:nth-child(1){height:8px}._pb span:nth-child(2){height:14px;animation-delay:.15s}
  ._pb span:nth-child(3){height:10px;animation-delay:.3s}._pb span:nth-child(4){height:16px;animation-delay:.1s}
  ._pb span:nth-child(5){height:8px;animation-delay:.25s}
  @keyframes _pba{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.25)}}
  ._vh{font-size:.68rem;color:#252538;text-align:center;}
  ._rat{display:none;padding:9px 14px;border-top:1px solid #22223a;background:#14142a;
    flex-direction:column;gap:6px;flex-shrink:0;}
  ._rat.show{display:flex;}
  ._rat p{font-size:.74rem;color:#64748b;margin:0;}
  ._stars{display:flex;gap:5px;}
  ._star{font-size:1.25rem;cursor:pointer;filter:grayscale(1) opacity(.3);transition:filter .15s,transform .1s;}
  ._star:hover,._star.on{filter:none;opacity:1;transform:scale(1.18);}
  `;
  document.head.appendChild(css);

  /* ── Build DOM ───────────────────────────────────────────────────────────── */
  const notif = el("div", { id:"_on" });

  const btn = el("button", { id:"_ob", "aria-label":"Open support" });
  btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>`;

  const win = el("div", { id:"_ow" });
  win.innerHTML = `
    <div class="_oh">
      <div class="_oav">🎬</div>
      <div class="_oht"><h3>OTT Support</h3>
        <div class="_os"><div class="_od"></div><span id="_ost">Online</span></div>
      </div>
      <div class="_oha">
        <button class="_olb on" id="_en">EN</button>
        <button class="_olb"    id="_ar">AR</button>
        <button class="_ocb"    id="_cx">✕</button>
      </div>
    </div>
    <div class="_tabs">
      <button class="_tab on" id="_tc">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>Chat
      </button>
      <button class="_tab" id="_tv">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>Voice
      </button>
    </div>
    <div id="_cp" style="display:flex;flex-direction:column;flex:1;overflow:hidden;">
      <div class="_msgs" id="_msgs"></div>
      <div class="_chips" id="_chips"></div>
      <div class="_tbar">
        <textarea id="_ta" class="_ta" rows="1" placeholder="${L[lang].ph}"></textarea>
        <button class="_sb" id="_send" aria-label="Send">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>
    </div>
    <div class="_vp" id="_vp">
      <div class="_vst" id="_vst">${L[lang].micIdle}</div>
      <div class="_wf" id="_wf">
        ${Array(15).fill('<div class="_wb"></div>').join("")}
      </div>
      <div class="_mr" id="_mr">
        <div class="_rp"></div>
        <button class="_mb" id="_mb">
          <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
        </button>
      </div>
      <div class="_ltx" id="_ltx"></div>
      <div class="_np"  id="_np">
        <div class="_pb"><span></span><span></span><span></span><span></span><span></span></div>
        <span id="_pl">${L[lang].playLbl}</span>
      </div>
      <div class="_vh" id="_vh">${L[lang].hint}</div>
    </div>
    <div class="_rat" id="_rat">
      <p id="_rl">${L[lang].rLbl}</p>
      <div class="_stars">
        ${[1,2,3,4,5].map(n=>`<span class="_star" data-v="${n}">⭐</span>`).join("")}
      </div>
    </div>`;

  const audioEl = el("audio", { style:"display:none" });

  document.body.append(notif, btn, win, audioEl);

  /* ── DOM refs ────────────────────────────────────────────────────────────── */
  const $ = id => document.getElementById(id);
  const msgs   = $("_msgs"), chips = $("_chips"), ta = $("_ta"), sendBtn = $("_send");
  const chatP  = $("_cp"), voiceP = $("_vp");
  const micBtn = $("_mb"), micRing = $("_mr");
  const waveDiv= $("_wf"), bars = waveDiv.querySelectorAll("._wb");
  const liveTx = $("_ltx"), vStat = $("_vst"), nowPlay = $("_np"), ratBox = $("_rat");

  /* ── Voice state ─────────────────────────────────────────────────────────── */
  let recog = null, isRec = false, rafId = null;
  let audioCtx = null, analyser = null, micStream = null, finalText = "";

  /* ── Wire events ─────────────────────────────────────────────────────────── */
  btn.onclick       = toggle;
  $("_cx").onclick  = toggle;
  $("_en").onclick  = () => setLang("en");
  $("_ar").onclick  = () => setLang("ar");
  $("_tc").onclick  = () => setMode("chat");
  $("_tv").onclick  = () => setMode("voice");
  sendBtn.onclick   = sendText;
  micBtn.onclick    = toggleMic;
  ta.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendText(); } });
  ta.addEventListener("input",   e => { e.target.style.height = "auto"; e.target.style.height = Math.min(e.target.scrollHeight, 88) + "px"; });
  win.querySelectorAll("._star").forEach(s =>
    s.addEventListener("click", () => rate(+s.dataset.v))
  );

  /* ════════════════════════════════════════════════════════
     CORE FUNCTIONS
     ════════════════════════════════════════════════════════ */

  function toggle() {
    isOpen = !isOpen;
    win.classList.toggle("open", isOpen);
    notif.style.display = "none";
    if (isOpen && msgs.children.length === 0) init();
    if (isOpen && mode === "chat") ta.focus();
  }

  function setLang(l) {
    lang = l;
    const ar = l === "ar";
    win.style.direction = ar ? "rtl" : "ltr";
    ta.placeholder = L[l].ph; ta.style.direction = ar ? "rtl" : "ltr";
    $("_en").classList.toggle("on", !ar);
    $("_ar").classList.toggle("on",  ar);
    $("_rl").textContent  = L[l].rLbl;
    $("_vh").textContent  = L[l].hint;
    $("_pl").textContent  = L[l].playLbl;
    vStat.textContent     = L[l].micIdle;
    if (recog) recog.lang = ar ? "ar-SA" : "en-US";
    showChips();
  }

  function setMode(m) {
    mode = m;
    $("_tc").classList.toggle("on", m === "chat");
    $("_tv").classList.toggle("on", m === "voice");
    chatP.style.display = m === "chat" ? "flex" : "none";
    voiceP.classList.toggle("show", m === "voice");
    if (m === "voice") setupRecog();
    else { stopRec(false); ta.focus(); }
  }

  async function init() {
    try { const d = await (await fetch(`${API}/api/health`)).json(); $("_ost").textContent = `Online · ${d.model||"AI"}`; }
    catch { $("_ost").textContent = "Connecting…"; }
    bubble("bot", L[lang].welcome);
    showChips();
  }

  function showChips() {
    chips.innerHTML = (CHIPS[lang]||CHIPS.en).map(t => `<button class="_chip">${esc(t)}</button>`).join("");
    chips.querySelectorAll("._chip").forEach(b =>
      b.addEventListener("click", () => { ta.value = b.textContent.trim(); sendText(); })
    );
  }

  /* ── Text chat ───────────────────────────────────────────────────────────── */
  async function sendText() {
    const txt = ta.value.trim(); if (!txt) return;
    ta.value = ""; ta.style.height = "auto"; sendBtn.disabled = true;
    chips.innerHTML = "";
    bubble("user", txt);
    const tid = typing();
    const reply = await callChat(txt);
    rmTyping(tid); bubble("bot", reply);
    bump(); sendBtn.disabled = false; ta.focus();
  }

  /* ── Voice: Web Speech API ───────────────────────────────────────────────── */
  function setupRecog() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { vStat.textContent = L[lang].micNone; micBtn.disabled = true; return; }
    if (recog) return;

    recog = new SR();
    recog.continuous = true; recog.interimResults = true; recog.maxAlternatives = 1;
    recog.lang = lang === "ar" ? "ar-SA" : "en-US";

    recog.onstart  = () => {
      isRec = true;
      micBtn.classList.add("rec"); micRing.classList.add("rec");
      vStat.textContent = L[lang].micOn;
      liveTx.classList.add("show"); liveTx.textContent = "";
      startWave();
    };

    recog.onresult = e => {
      let interim = ""; finalText = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        e.results[i].isFinal ? finalText += t : interim += t;
      }
      liveTx.textContent = finalText || interim;
    };

    recog.onerror = ev => {
      if (["not-allowed","service-not-allowed"].includes(ev.error))
        vStat.textContent = L[lang].micErr;
      stopRec(false);
    };

    recog.onend = () => { if (isRec) stopRec(true); };
  }

  function toggleMic() { isRec ? stopRec(true) : startRec(); }

  function startRec() {
    finalText = ""; liveTx.textContent = "";
    try { recog.start(); }
    catch { recog.stop(); setTimeout(() => recog.start(), 200); }
  }

  function stopRec(process) {
    const had = finalText.trim();
    isRec = false;
    micBtn.classList.remove("rec"); micRing.classList.remove("rec");
    liveTx.classList.remove("show"); stopWave();
    try { recog && recog.stop(); } catch {}
    if (process && had) handleVoice(had);
    else vStat.textContent = L[lang].micIdle;
  }

  async function handleVoice(text) {
    vStat.textContent = L[lang].micProc; micBtn.disabled = true;
    bubble("user", text, true);
    const tid = typing();
    const reply = await callChat(text);
    rmTyping(tid); bubble("bot", reply, true);
    await playTTS(reply);
    micBtn.disabled = false; vStat.textContent = L[lang].micIdle;
    bump();
  }

  async function playTTS(text) {
    try {
      const r = await fetch(`${API}/api/tts`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ text, language: lang })
      });
      if (!r.ok) throw 0;
      const url = URL.createObjectURL(await r.blob());
      audioEl.src = url;
      nowPlay.classList.add("show");
      await new Promise(res => {
        audioEl.onended = () => { nowPlay.classList.remove("show"); URL.revokeObjectURL(url); res(); };
        audioEl.onerror = () => { nowPlay.classList.remove("show"); res(); };
        audioEl.play().catch(res);
      });
    } catch { nowPlay.classList.remove("show"); }
  }

  /* ── Waveform driven by real mic audio levels ────────────────────────────── */
  async function startWave() {
    waveDiv.classList.add("act");
    try {
      micStream = await navigator.mediaDevices.getUserMedia({ audio:true, video:false });
      audioCtx  = new (window.AudioContext || window.webkitAudioContext)();
      analyser  = audioCtx.createAnalyser(); analyser.fftSize = 64;
      audioCtx.createMediaStreamSource(micStream).connect(analyser);
      const buf = new Uint8Array(analyser.frequencyBinCount);
      const draw = () => {
        if (!isRec) return;
        analyser.getByteFrequencyData(buf);
        bars.forEach((b,i) => {
          const v = buf[Math.floor(i * buf.length / bars.length)] / 255;
          b.style.height = Math.max(4, Math.round(v * 46)) + "px";
        });
        rafId = requestAnimationFrame(draw);
      };
      draw();
    } catch {
      bars.forEach((b,i) => { b.style.animation = `_wi ${.35+i*.07}s ease-in-out ${i*.04}s infinite alternate`; });
    }
  }

  function stopWave() {
    waveDiv.classList.remove("act");
    if (rafId)     { cancelAnimationFrame(rafId); rafId = null; }
    if (micStream) { micStream.getTracks().forEach(t => t.stop()); micStream = null; }
    if (audioCtx)  { audioCtx.close().catch(()=>{}); audioCtx = null; analyser = null; }
    bars.forEach(b => { b.style.height = "4px"; b.style.animation = ""; });
  }

  /* ── API ─────────────────────────────────────────────────────────────────── */
  async function callChat(text) {
    try {
      const r = await fetch(`${API}/api/chat`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ session_id:sid, message:text, language:lang })
      });
      if (!r.ok) throw 0;
      return (await r.json()).reply;
    } catch {
      return lang === "ar" ? "⚠️ خطأ في الاتصال. يرجى المحاولة." : "⚠️ Connection error. Please try again.";
    }
  }

  async function rate(stars) {
    win.querySelectorAll("._star").forEach((s,i) => s.classList.toggle("on", i < stars));
    try { await fetch(`${API}/api/feedback`, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ session_id:sid, rating:stars }) }); } catch {}
    setTimeout(() => {
      $("_rl").textContent = L[lang].rThanks;
      win.querySelector("._stars").style.display = "none";
      setTimeout(() => ratBox.classList.remove("show"), 2500);
    }, 400);
  }

  /* ── DOM helpers ─────────────────────────────────────────────────────────── */
  function bubble(role, text, isVoice=false) {
    const now = new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});
    const d   = document.createElement("div");
    d.className = `_m ${role}${lang==="ar"?" rtl":""}`;
    d.innerHTML = `<div class="_bub">${esc(text)}</div>
      <div class="_mm">${isVoice?`<span class="_vb">🎙️</span>`:""}<span class="_mt">${now}</span></div>`;
    msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight;
  }

  function typing() {
    const id = "_t"+Date.now(), d = document.createElement("div");
    d.className = "_m b _typ"; d.id = id;
    d.innerHTML = `<div class="_bub"><div class="_dots"><span></span><span></span><span></span></div></div>`;
    msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight; return id;
  }

  function rmTyping(id) { const e = document.getElementById(id); if(e) e.remove(); }

  function bump() { if (++exchanges >= 3) ratBox.classList.add("show"); }

  function esc(t) { return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g,"<br/>"); }

  function el(tag, attrs={}) {
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k,v]) => k === "style" ? e.setAttribute("style",v) : e.setAttribute(k,v));
    return e;
  }

})();
