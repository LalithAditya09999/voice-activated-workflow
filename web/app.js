"use strict";

const UI = {
  tagline: { en: "Speak. We'll handle the paperwork.", ta: "பேசுங்கள். ஆவண வேலையை நாங்கள் பார்க்கிறோம்.", hi: "बोलिए। कागज़ी काम हम संभालेंगे।" },
  tap: { en: "Tap the mic and speak", ta: "மைக்கைத் தொட்டுப் பேசுங்கள்", hi: "माइक दबाकर बोलिए" },
  listening: { en: "Listening…", ta: "கேட்கிறேன்…", hi: "सुन रहा हूँ…" },
  thinking: { en: "Working on it…", ta: "பார்க்கிறேன்…", hi: "देख रहा हूँ…" },
  speaking: { en: "Speaking… tap the mic to interrupt", ta: "பேசுகிறேன்… இடைமறிக்க மைக்கைத் தொடுங்கள்", hi: "बोल रहा हूँ… रोकने के लिए माइक दबाएँ" },
  noMic: { en: "Voice input isn't available in this browser — type instead.", ta: "இந்த உலாவியில் குரல் உள்ளீடு இல்லை — தட்டச்சு செய்யுங்கள்.", hi: "इस ब्राउज़र में आवाज़ इनपुट नहीं है — टाइप करें।" },
  heardNothing: { en: "I didn't catch that — tap and try again.", ta: "சரியாகக் கேட்கவில்லை — மீண்டும் முயலுங்கள்.", hi: "सुनाई नहीं दिया — फिर से कोशिश करें।" },
  type: { en: "Type here…", ta: "இங்கே தட்டச்சு செய்யுங்கள்…", hi: "यहाँ लिखें…" },
  send: { en: "Send", ta: "அனுப்பு", hi: "भेजें" },
  form: { en: "Application", ta: "விண்ணப்பம்", hi: "आवेदन" },
  docs: { en: "Keep these documents ready", ta: "இந்த ஆவணங்களைத் தயாராக வைத்திருங்கள்", hi: "ये दस्तावेज़ तैयार रखें" },
  correct: { en: "Yes, correct", ta: "ஆமாம், சரி", hi: "हाँ, सही है" },
  change: { en: "Change something", ta: "மாற்ற வேண்டும்", hi: "कुछ बदलना है" },
  yesWord: { en: "yes", ta: "ஆமாம்", hi: "हाँ" },
  noWord: { en: "no", ta: "இல்லை", hi: "नहीं" },
  prepared: { en: "Application prepared", ta: "விண்ணப்பம் தயார்", hi: "आवेदन तैयार" },
  reference: { en: "Reference number", ta: "குறிப்பு எண்", hi: "संदर्भ नंबर" },
  takeTo: { en: "Take it to", ta: "கொண்டு செல்ல வேண்டிய இடம்", hi: "कहाँ ले जाएँ" },
  followUp: { en: "Follow-up reminder", ta: "நினைவூட்டல் தேதி", hi: "याद दिलाने की तारीख" },
  print: { en: "Open printable form", ta: "அச்சிடும் படிவம்", hi: "प्रिंट फ़ॉर्म खोलें" },
  schemes: { en: "Schemes for you", ta: "உங்களுக்கான திட்டங்கள்", hi: "आपके लिए योजनाएँ" },
  eligible: { en: "Eligible", ta: "தகுதி உண்டு", hi: "पात्र" },
  maybe: { en: "Need details", ta: "விவரம் தேவை", hi: "जानकारी चाहिए" },
  not_eligible: { en: "Not eligible", ta: "தகுதி இல்லை", hi: "पात्र नहीं" },
  apply: { en: "Apply", ta: "விண்ணப்பி", hi: "आवेदन करें" },
  applyFor: { en: "I want to apply for", ta: "நான் விண்ணப்பிக்க வேண்டும்:", hi: "मुझे आवेदन करना है:" },
  findSchemes: { en: "Which schemes can I get?", ta: "எனக்கு எந்தத் திட்டங்கள் கிடைக்கும்?", hi: "मुझे कौन सी योजनाएँ मिल सकती हैं?" },
  myApps: { en: "My applications", ta: "என் விண்ணப்பங்கள்", hi: "मेरे आवेदन" },
  sources: { en: "From", ta: "ஆதாரம்", hi: "स्रोत" },
  unverified: { en: "verify at office", ta: "அலுவலகத்தில் உறுதி செய்யவும்", hi: "कार्यालय में पुष्टि करें" },
  offline: { en: "offline mode", ta: "ஆஃப்லைன்", hi: "ऑफ़लाइन" },
};

const state = {
  lang: localGet("saathi.lang") || "ta",
  sessionId: null,
  config: null,
  speakReplies: localGet("saathi.speak") !== "0",
  listening: false,
  busy: false,
  audio: null,
};

const $ = (sel) => document.querySelector(sel);
const chat = $("#chat");
const panels = $("#panels");
const micBtn = $("#mic");
const statusEl = $("#status");

function localGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function localSet(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } }
function tr(key) { const v = UI[key]; return v ? (v[state.lang] || v.en) : key; }
function bcp47() { return state.config?.languages?.[state.lang]?.bcp47 || "ta-IN"; }
function setStatus(key, raw) { statusEl.textContent = raw ?? tr(key); }
function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const kid of kids.flat()) if (kid != null) n.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  return n;
}

async function api(path, body) {
  const res = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

// ---------------- language ----------------
function applyLang() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === state.lang)));
  document.querySelectorAll("[data-i18n]").forEach((n) => { n.textContent = tr(n.dataset.i18n); });
  document.querySelectorAll("[data-i18n-ph]").forEach((n) => { n.placeholder = tr(n.dataset.i18nPh); });
  renderChips();
}

document.querySelectorAll("[data-lang]").forEach((b) => b.addEventListener("click", async () => {
  state.lang = b.dataset.lang;
  localSet("saathi.lang", state.lang);
  applyLang();
  stopSpeaking();
  await newSession();
}));

// ---------------- chat rendering ----------------
function addMsg(text, who) {
  const m = el("div", { class: `msg ${who}` }, text);
  if (who === "bot") {
    m.append(el("button", { class: "replay", title: "Play", "aria-label": "Play", onclick: () => speak(text) }, "🔈"));
  }
  chat.append(m);
  m.scrollIntoView({ behavior: "smooth", block: "end" });
  return m;
}

async function renderChips() {
  const box = $("#chips");
  box.replaceChildren();
  const send = (txt) => () => sendText(txt);
  box.append(el("button", { class: "chip", onclick: send(tr("findSchemes")) }, "✨ " + tr("findSchemes")));
  box.append(el("button", { class: "chip", onclick: send(tr("myApps")) }, "📋 " + tr("myApps")));
  try {
    const services = await api(`/api/services?lang=${state.lang}`);
    for (const s of services.filter((s) => s.example)) box.append(el("button", { class: "chip", onclick: send(s.example) }, "🎙️ " + s.example));
  } catch { /* chips are optional */ }
}

function renderForm(form) {
  const old = $("#formCard");
  if (!form) { old?.remove(); return; }
  const pct = form.progress.total ? Math.round((100 * form.progress.done) / form.progress.total) : 0;
  const current = form.fields.find((f) => f.current);
  const details = el("details", { class: "formbar", id: "formCard" },
    el("summary", {}, el("span", {}, `📝 ${form.title}`), el("span", { class: "count" }, `${form.progress.done}/${form.progress.total} ▾`)),
  );
  // keep it open when reviewing, or if the user had opened it
  if (form.awaiting_confirmation || old?.open) details.open = true;
  const parts = [
    el("div", { class: "progress", role: "progressbar", "aria-valuenow": pct, "aria-valuemin": 0, "aria-valuemax": 100 }, el("span", { style: `width:${pct}%` })),
  ];
  // confirm buttons first so they're always on screen during the read-back
  if (form.awaiting_confirmation) {
    parts.push(el("div", { class: "confirm-row" },
      el("button", { class: "btn", onclick: () => sendText(tr("yesWord")) }, "✓ " + tr("correct")),
      el("button", { class: "btn ghost", onclick: () => sendText(tr("noWord")) }, tr("change"))));
  }
  if (current) parts.push(el("div", { class: "now" }, "➜ " + current.label));
  parts.push(el("ul", { class: "fields" }, form.fields.map((f) =>
    el("li", { class: `${f.value == null ? "empty" : ""} ${f.current ? "current" : ""}` }, el("span", {}, f.label), el("span", { class: "v" }, f.value ?? "…")))));
  if (form.documents?.length) {
    parts.push(el("div", { class: "sources", style: "margin-top:10px" }, tr("docs")), el("ul", { class: "docs" }, form.documents.map((d) => el("li", {}, d))));
  }
  details.append(...parts);
  old ? old.replaceWith(details) : panels.append(details);
}

function addCard(card) {
  chat.append(card);
  requestAnimationFrame(() => card.scrollIntoView({ block: "start" }));
}

function renderApplication(a) {
  const card = el("div", { class: "card" },
    el("h3", {}, `✅ ${tr("prepared")}: ${a.title}`),
    el("div", { class: "sources" }, tr("reference")),
    el("div", { class: "app-id" }, a.id),
    a.deadline_note ? el("p", { class: "deadline" }, "⏱ " + a.deadline_note) : null,
    el("p", {}, el("b", {}, tr("takeTo") + ": "), a.submit_to),
    a.next_step ? el("p", {}, a.next_step) : null,
    el("p", {}, el("b", {}, tr("followUp") + ": "), a.follow_up_on),
    el("a", { class: "btn", href: a.print_url, target: "_blank", rel: "noopener" }, "🖨 " + tr("print")),
  );
  addCard(card);
}

function renderEligibility(results) {
  const card = el("div", { class: "card" }, el("h3", {}, "✨ " + tr("schemes")));
  card.append(el("ul", { class: "elig" }, results.map((r) => el("li", {},
    el("div", {}, el("span", { class: `tag ${r.status}` }, tr(r.status)), el("b", {}, r.name)),
    el("div", {}, r.benefit),
    r.reasons.length ? el("div", { class: "why" }, r.reasons.join("; ")) : null,
    r.status === "eligible" && r.service ? el("button", { class: "btn ghost", style: "margin-top:8px", onclick: () => sendText(`${tr("applyFor")} ${r.name}`) }, tr("apply")) : null,
  ))));
  addCard(card);
}

function renderApplications(apps) {
  if (!apps.length) return;
  const card = el("div", { class: "card" }, el("h3", {}, "📋 " + tr("myApps")),
    el("ul", { class: "fields" }, apps.map((a) => el("li", {},
      el("span", {}, `${a.title}`),
      el("a", { class: "v", href: `/api/applications/${a.id}/print`, target: "_blank", rel: "noopener" }, `${a.id}${a.overdue ? " ⚠️" : ""}`)))));
  addCard(card);
}

function renderSources(srcs, msgEl) {
  if (!srcs?.length || !msgEl) return;
  const names = srcs.map((s) => s.title + (s.verified ? "" : ` (${tr("unverified")})`)).join(" · ");
  msgEl.after(el("div", { class: "sources" }, `${tr("sources")}: ${names}`));
}

// ---------------- conversation ----------------
async function newSession() {
  chat.replaceChildren();
  panels.replaceChildren();
  const res = await api("/api/session", { lang: state.lang });
  state.sessionId = res.session_id;
  addMsg(res.greeting, "bot");
}

async function sendText(text) {
  text = (text || "").trim();
  if (!text || state.busy) return;
  stopSpeaking();
  addMsg(text, "user");
  state.busy = true;
  micBtn.classList.add("busy");
  setStatus("thinking");
  const pending = addMsg(tr("thinking"), "bot thinking");
  try {
    const res = await api("/api/chat", { session_id: state.sessionId, text, lang: state.lang });
    pending.remove();
    renderForm(res.form);
    const m = addMsg(res.reply, "bot");
    const sources = res.events.filter((ev) => ev.type === "sources").pop();
    renderSources(sources?.data, m);
    for (const ev of res.events) {
      if (ev.type === "application") renderApplication(ev.data);
      else if (ev.type === "eligibility") renderEligibility(ev.data);
      else if (ev.type === "applications") renderApplications(ev.data);
    }
    speak(res.reply);
  } catch (err) {
    pending.remove();
    if (String(err).startsWith("Error: 404")) { await newSession(); }
    else addMsg("⚠️ " + err.message, "bot");
    setStatus("tap");
  } finally {
    state.busy = false;
    micBtn.classList.remove("busy");
  }
}

// ---------------- speech out ----------------
function stopSpeaking() {
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  if (state.audio) { state.audio.pause(); state.audio = null; }
}

function pickVoice() {
  const voices = speechSynthesis.getVoices();
  const want = bcp47().toLowerCase();
  return voices.find((v) => v.lang.toLowerCase() === want) || voices.find((v) => v.lang.toLowerCase().startsWith(state.lang));
}

async function speak(text) {
  if (!state.speakReplies || !text) { setStatus("tap"); return; }
  stopSpeaking();
  setStatus("speaking");
  if (state.config?.server_speech) {
    try {
      const res = await fetch("/api/tts", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, lang: state.lang }) });
      if (res.ok) {
        const url = URL.createObjectURL(await res.blob());
        state.audio = new Audio(url);
        state.audio.onended = () => setStatus("tap");
        await state.audio.play();
        return;
      }
    } catch { /* fall back to browser voice */ }
  }
  if (!("speechSynthesis" in window)) { setStatus("tap"); return; }
  const u = new SpeechSynthesisUtterance(text);
  u.lang = bcp47();
  const v = pickVoice();
  if (v) u.voice = v;
  u.rate = 0.95;
  u.onend = () => setStatus("tap");
  speechSynthesis.speak(u);
}

$("#speakToggle").addEventListener("click", (e) => {
  state.speakReplies = !state.speakReplies;
  e.currentTarget.setAttribute("aria-pressed", String(state.speakReplies));
  localSet("saathi.speak", state.speakReplies ? "1" : "0");
  if (!state.speakReplies) stopSpeaking();
});

// ---------------- speech in ----------------
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognizer = null;
let recorder = null;

function startBrowserRecognition() {
  recognizer = new Recognition();
  recognizer.lang = bcp47();
  recognizer.interimResults = true;
  recognizer.maxAlternatives = 1;
  let finalText = "";
  recognizer.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const r = e.results[i];
      if (r.isFinal) finalText += r[0].transcript; else interim += r[0].transcript;
    }
    setStatus(null, interim || finalText || tr("listening"));
  };
  recognizer.onerror = () => { stopListening(); setStatus("heardNothing"); };
  recognizer.onend = () => {
    const text = finalText.trim();
    stopListening();
    if (text) sendText(text); else setStatus("heardNothing");
  };
  recognizer.start();
}

async function startServerRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const chunks = [];
  recorder = new MediaRecorder(stream);
  recorder.ondataavailable = (e) => chunks.push(e.data);
  recorder.onstop = async () => {
    stream.getTracks().forEach((t) => t.stop());
    stopListening();
    const fd = new FormData();
    fd.append("audio", new Blob(chunks, { type: recorder.mimeType }), "speech.webm");
    fd.append("lang", state.lang);
    setStatus("thinking");
    try {
      const res = await fetch("/api/stt", { method: "POST", body: fd });
      const { text } = await res.json();
      if (text) sendText(text); else setStatus("heardNothing");
    } catch { setStatus("heardNothing"); }
  };
  recorder.start();
}

function stopListening() {
  state.listening = false;
  micBtn.classList.remove("listening");
}

micBtn.addEventListener("click", async () => {
  stopSpeaking();
  if (state.busy) return;
  if (state.listening) {
    // second tap ends the utterance
    if (recognizer) recognizer.stop();
    if (recorder && recorder.state === "recording") recorder.stop();
    return;
  }
  const canServer = state.config?.server_speech && navigator.mediaDevices && window.MediaRecorder;
  if (!Recognition && !canServer) {
    setStatus("noMic");
    $("#textForm").hidden = false;
    return;
  }
  state.listening = true;
  micBtn.classList.add("listening");
  setStatus("listening");
  try {
    // prefer server STT (better on code-mixed Indic speech) when configured
    if (canServer) await startServerRecording(); else startBrowserRecognition();
  } catch {
    stopListening();
    setStatus("noMic");
    $("#textForm").hidden = false;
  }
});

$("#kbToggle").addEventListener("click", () => {
  const f = $("#textForm");
  f.hidden = !f.hidden;
  if (!f.hidden) $("#textInput").focus();
});
$("#textForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const inp = $("#textInput");
  sendText(inp.value);
  inp.value = "";
});

// ---------------- boot ----------------
(async function boot() {
  $("#speakToggle").setAttribute("aria-pressed", String(state.speakReplies));
  if ("speechSynthesis" in window) speechSynthesis.getVoices();
  state.config = await api("/api/config");
  if (state.config.agent === "offline") $(".brand-sub").title = tr("offline");
  applyLang();
  await newSession();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
})();
