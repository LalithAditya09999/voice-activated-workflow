"use strict";

/* ---------------- words on screen, in three languages ---------------- */
const UI = {
  helloTitle: { en: "Vanakkam!", ta: "வணக்கம்!", hi: "नमस्ते!" },
  helloSub: { en: "What do you need today?", ta: "இன்று என்ன உதவி வேண்டும்?", hi: "आज क्या मदद चाहिए?" },
  tap: { en: "Tap to speak", ta: "தொட்டுப் பேசுங்கள்", hi: "दबाकर बोलिए" },
  listening: { en: "Listening…", ta: "கேட்கிறேன்…", hi: "सुन रहा हूँ…" },
  thinking: { en: "Working on it", ta: "பார்க்கிறேன்", hi: "देख रहा हूँ" },
  speaking: { en: "Speaking…", ta: "பேசுகிறேன்…", hi: "बोल रहा हूँ…" },
  noMic: { en: "Voice input isn't available in this browser. Please type instead.", ta: "இந்த உலாவியில் குரல் உள்ளீடு இல்லை. தட்டச்சு செய்யுங்கள்.", hi: "इस ब्राउज़र में आवाज़ इनपुट नहीं है। कृपया टाइप करें।" },
  heardNothing: { en: "Sorry, I didn't catch that. Please say it again.", ta: "மன்னிக்கவும், சரியாகக் கேட்கவில்லை. மீண்டும் சொல்லுங்கள்.", hi: "माफ़ कीजिए, ठीक से सुनाई नहीं दिया। फिर से बोलिए।" },
  typeHere: { en: "Type here…", ta: "இங்கே தட்டச்சு செய்யுங்கள்…", hi: "यहाँ लिखें…" },
  send: { en: "Send", ta: "அனுப்பு", hi: "भेजें" },
  history: { en: "Conversation", ta: "உரையாடல்", hi: "बातचीत" },
  historyShort: { en: "History", ta: "வரலாறு", hi: "इतिहास" },
  typeShort: { en: "Type", ta: "எழுது", hi: "लिखें" },
  speak: { en: "Speak", ta: "பேசு", hi: "बोलें" },
  replay: { en: "Play again", ta: "மீண்டும் கேள்", hi: "फिर सुनें" },
  newChat: { en: "Start again", ta: "புதிதாகத் தொடங்கு", hi: "फिर से शुरू करें" },
  youSaid: { en: "You said", ta: "நீங்கள் சொன்னது", hi: "आपने कहा" },
  details: { en: "Details", ta: "விவரம்", hi: "विवरण" },
  next: { en: "Next", ta: "அடுத்து", hi: "अगला" },
  docs: { en: "Keep these documents ready", ta: "இந்த ஆவணங்களைத் தயாராக வைத்திருங்கள்", hi: "ये दस्तावेज़ तैयार रखें" },
  correct: { en: "Yes, correct", ta: "ஆமாம், சரி", hi: "हाँ, सही है" },
  change: { en: "Change something", ta: "மாற்ற வேண்டும்", hi: "कुछ बदलना है" },
  yesWord: { en: "yes", ta: "ஆமாம்", hi: "हाँ" },
  noWord: { en: "no", ta: "இல்லை", hi: "नहीं" },
  prepared: { en: "Application ready", ta: "விண்ணப்பம் தயார்", hi: "आवेदन तैयार" },
  reference: { en: "Reference number", ta: "குறிப்பு எண்", hi: "संदर्भ नंबर" },
  takeTo: { en: "Take it to", ta: "கொண்டு செல்ல வேண்டிய இடம்", hi: "कहाँ ले जाएँ" },
  followUp: { en: "Follow-up on", ta: "நினைவூட்டல் தேதி", hi: "याद दिलाने की तारीख" },
  print: { en: "Open printable form", ta: "அச்சிடும் படிவம்", hi: "प्रिंट फ़ॉर्म खोलें" },
  schemes: { en: "Schemes for you", ta: "உங்களுக்கான திட்டங்கள்", hi: "आपके लिए योजनाएँ" },
  eligible: { en: "Eligible", ta: "தகுதி உண்டு", hi: "पात्र" },
  maybe: { en: "Need details", ta: "விவரம் தேவை", hi: "जानकारी चाहिए" },
  not_eligible: { en: "Not eligible", ta: "தகுதி இல்லை", hi: "पात्र नहीं" },
  apply: { en: "Apply", ta: "விண்ணப்பி", hi: "आवेदन करें" },
  applyFor: { en: "I want to apply for", ta: "நான் விண்ணப்பிக்க வேண்டும்:", hi: "मुझे आवेदन करना है:" },
  findSchemes: { en: "Which schemes can I get?", ta: "எனக்கு எந்தத் திட்டங்கள் கிடைக்கும்?", hi: "मुझे कौन सी योजनाएँ मिल सकती हैं?" },
  findSchemesSub: { en: "Find out in 9 questions", ta: "9 கேள்விகளில் தெரிந்துகொள்ளுங்கள்", hi: "9 सवालों में जानिए" },
  myApps: { en: "My applications", ta: "என் விண்ணப்பங்கள்", hi: "मेरे आवेदन" },
  sources: { en: "From", ta: "ஆதாரம்", hi: "स्रोत" },
  unverified: { en: "confirm at the office", ta: "அலுவலகத்தில் உறுதி செய்யவும்", hi: "कार्यालय में पुष्टि करें" },
  voiceOn: { en: "🔊 Voice on", ta: "🔊 குரல் ஆன்", hi: "🔊 आवाज़ चालू" },
  voiceOff: { en: "🔇 Voice off", ta: "🔇 குரல் ஆஃப்", hi: "🔇 आवाज़ बंद" },
  basicMode: { en: "Basic mode", ta: "அடிப்படை முறை", hi: "बेसिक मोड" },
  doneShort: { en: "Done! Your application is ready.", ta: "முடிந்தது! உங்கள் விண்ணப்பம் தயார்.", hi: "हो गया! आपका आवेदन तैयार है।" },
  checkDetails: { en: "Are these details correct?", ta: "இந்த விவரங்கள் சரியா?", hi: "क्या ये जानकारी सही है?" },
  schemesFound: { en: "Here are the schemes for you.", ta: "உங்களுக்கான திட்டங்கள் இதோ.", hi: "ये रहीं आपके लिए योजनाएँ।" },
  bring: { en: "Bring these", ta: "கொண்டு வர வேண்டியவை", hi: "ये साथ लाएँ" },
  more: { en: "Read more", ta: "மேலும் படிக்க", hi: "और पढ़ें" },
  less: { en: "Show less", ta: "குறைவாகக் காட்டு", hi: "कम दिखाएँ" },
  keyNotSet: { en: "AI key not set: the main services work fully; free-form questions are understood better with the key.", ta: "AI சாவி அமைக்கப்படவில்லை: முக்கிய சேவைகள் முழுமையாக வேலை செய்யும்; சாவியுடன் இயல்பான பேச்சை இன்னும் நன்றாகப் புரிந்துகொள்ளும்.", hi: "AI कुंजी सेट नहीं है: मुख्य सेवाएँ पूरी तरह काम करती हैं; कुंजी के साथ खुली बातचीत बेहतर समझी जाती है।" },
  speechKeyNotSet: { en: "Speech key not set: using this phone's own voice recognition.", ta: "பேச்சு சாவி அமைக்கப்படவில்லை: இந்த போனின் குரல் அறிதல் பயன்படுத்தப்படுகிறது.", hi: "स्पीच कुंजी सेट नहीं है: फ़ोन की अपनी आवाज़ पहचान इस्तेमाल हो रही है।" },
};

/* the home tiles: a short label to read, and a sentence that starts the request */
const TILES = [
  { ico: "🌾", label: { ta: "பயிர் சேதம்", en: "Crop damage", hi: "फसल नुकसान" }, say: { ta: "நேற்று மழையில் என் நெல் சேதமானது", en: "Rain destroyed my paddy yesterday", hi: "कल बारिश से मेरी फसल खराब हो गई" } },
  { ico: "💧", label: { ta: "சொட்டு நீர்", en: "Drip irrigation", hi: "ड्रिप सिंचाई" }, say: { ta: "சொட்டு நீர் பாசனம் வேண்டும்", en: "I want drip irrigation", hi: "मुझे ड्रिप सिंचाई चाहिए" } },
  { ico: "☀️", label: { ta: "சோலார் பம்ப்", en: "Solar pump", hi: "सोलर पंप" }, say: { ta: "சோலார் பம்ப் வேண்டும்", en: "I want a solar pump", hi: "मुझे सोलर पंप चाहिए" } },
  { ico: "🪙", label: { ta: "பிஎம்-கிசான்", en: "PM-KISAN", hi: "पीएम-किसान" }, say: { ta: "பிஎம் கிசான்", en: "PM Kisan", hi: "पीएम किसान" } },
  { ico: "🌿", label: { ta: "இயற்கை / ரசாயனம்", en: "Organic or chemical", hi: "जैविक या रासायनिक" }, say: { ta: "ரசாயன உரமா இயற்கை உரமா, எது நல்லது?", en: "Chemical or organic fertiliser, which is better?", hi: "रासायनिक या जैविक खाद, कौन सा बेहतर है?" } },
  { ico: "🪔", label: { ta: "நம்மாழ்வார் முறை", en: "Nammalvar’s way", hi: "नम्मालवार विधि" }, say: { ta: "நம்மாழ்வார் இயற்கை வேளாண்மை", en: "Nammalvar natural farming", hi: "नम्मालवार प्राकृतिक खेती" } },
  { ico: "🙏", label: { ta: "ஓய்வூதியம்", en: "Pension", hi: "पेंशन" }, say: { ta: "முதியோர் ஓய்வூதியம்", en: "Old age pension", hi: "वृद्धावस्था पेंशन" } },
  { ico: "📣", label: { ta: "புகார்", en: "Complaint", hi: "शिकायत" }, say: { ta: "புகார் கொடுக்க வேண்டும்", en: "I want to file a complaint", hi: "मुझे शिकायत करनी है" } },
];
const pick = (o) => o[state.lang] || o.en;

const state = {
  lang: localGet("velan.lang") || "ta",
  sessionId: null,
  config: null,
  services: [],
  speakReplies: localGet("velan.speak") !== "0",
  listening: false,
  busy: false,
  audio: null,
  lastReply: "",
  form: null,
  history: [],
};

const $ = (sel) => document.querySelector(sel);
const app = $(".app");
const micBtn = $("#mic");
const live = $("#live");

function localGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function localSet(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } }
function tr(key) { const v = UI[key]; return v ? (v[state.lang] || v.en) : key; }
function bcp47() { return state.config?.languages?.[state.lang]?.bcp47 || "ta-IN"; }
function setLive(key, raw) { live.textContent = raw ?? tr(key); }
function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) n.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  return n;
}

async function api(path, body) {
  const res = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

/* ---------------- language ---------------- */
function applyLang() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === state.lang)));
  document.querySelectorAll("[data-i18n]").forEach((n) => { n.textContent = tr(n.dataset.i18n); });
  document.querySelectorAll("[data-i18n-ph]").forEach((n) => { n.placeholder = tr(n.dataset.i18nPh); });
  document.querySelectorAll("[data-i18n-aria]").forEach((n) => { n.setAttribute("aria-label", tr(n.dataset.i18nAria)); });
  renderSpeakToggle();
  renderModeChip();
}

document.querySelectorAll("[data-lang]").forEach((b) => b.addEventListener("click", async () => {
  if (b.dataset.lang === state.lang) return;
  state.lang = b.dataset.lang;
  localSet("velan.lang", state.lang);
  applyLang();
  stopSpeaking();
  await loadServices();
  await newSession();
}));

/* ---------------- home ---------------- */
async function loadServices() {
  try { state.services = await api(`/api/services?lang=${state.lang}`); } catch { state.services = []; }
  renderTiles();
}

function renderTiles() {
  const box = $("#tiles");
  box.replaceChildren(
    el("button", { class: "tile wide", onclick: () => sendText(tr("findSchemes")) },
      el("span", { class: "ico", "aria-hidden": "true" }, "✨"),
      el("span", { class: "t-text" }, el("span", { class: "t-name" }, tr("findSchemes")), el("span", { class: "t-say" }, tr("findSchemesSub")))),
    ...TILES.map((t) => el("button", { class: "tile", onclick: () => sendText(pick(t.say)) },
      el("span", { class: "ico", "aria-hidden": "true" }, t.ico),
      el("span", { class: "t-name" }, pick(t.label)))));
}

function showHome(on) {
  $("#home").hidden = !on;
  $("#talk").hidden = on;
}

/* ---------------- the stage ---------------- */
function sentences(text) {
  return text.match(/[^.!?।]+[.!?।]+["”’)]*\s*|[^.!?।]+$/g)?.map((x) => x.trim()).filter(Boolean) || [text];
}

function showReply(text, { thinking = false, full = null } = {}) {
  const reply = $(".reply");
  reply.classList.toggle("thinking", thinking);
  const box = $("#replyText");
  box.replaceChildren();
  const parts = sentences(text);
  if (parts.length <= 2 || thinking) {
    box.textContent = text;
  } else {
    // keep the screen light: two sentences, the rest behind "Read more"
    const shortText = parts.slice(0, 2).join(" ");
    const more = el("button", { class: "more" }, tr("more"));
    let open = false;
    more.onclick = () => { open = !open; box.firstChild.textContent = open ? text : shortText; more.textContent = open ? tr("less") : tr("more"); };
    box.append(document.createTextNode(shortText), more);
  }
  // restart the arrival animation
  reply.style.animation = "none"; void reply.offsetWidth; reply.style.animation = "";
}

function showSaid(text) {
  const said = $("#said");
  said.hidden = !text;
  said.textContent = text || "";
  said.dataset.label = tr("youSaid");
}

function renderSources(srcs) {
  const box = $("#sources");
  if (!srcs?.length) { box.hidden = true; return; }
  box.hidden = false;
  box.textContent = `${tr("sources")}: ` + srcs.map((s) => s.title + (s.verified ? "" : ` (${tr("unverified")})`)).join(" · ");
}

function renderConfirm(form) {
  const box = $("#confirm");
  box.replaceChildren();
  box.hidden = !form?.awaiting_confirmation;
  if (box.hidden) return;
  box.append(
    el("button", { class: "btn", onclick: () => sendText(tr("yesWord")) }, "✓ " + tr("correct")),
    el("button", { class: "btn ghost", onclick: () => sendText(tr("noWord")) }, tr("change")));
}

function renderTask(form) {
  state.form = form;
  const bar = $("#task");
  if (!form) { bar.hidden = true; bar.replaceChildren(); return; }
  bar.hidden = false;
  const current = form.fields.find((f) => f.current);
  const total = form.progress.total || 1;
  const steps = el("div", { class: "steps", role: "progressbar", "aria-valuemin": 0, "aria-valuemax": total, "aria-valuenow": form.progress.done });
  for (let i = 0; i < Math.min(total, 16); i++) {
    const at = Math.floor((i * total) / Math.min(total, 16));
    steps.append(el("i", { class: at < form.progress.done ? "done" : (at === form.progress.done && !form.awaiting_confirmation ? "now" : "") }));
  }
  const parts = [
    el("div", { class: "task-title" }, form.title),
    el("button", { class: "task-open", onclick: openFormSheet }, `${form.progress.done}/${form.progress.total} · ${tr("details")}`),
    steps,
  ];
  if (current) parts.push(el("div", { class: "task-now" }, `${tr("next")}: ${current.label}`));
  bar.replaceChildren(...parts);
  if (!$("#formSheet").hidden) renderFormSheet();
}

function renderFormSheet() {
  const form = state.form;
  if (!form) return;
  $("#formTitle").textContent = form.title;
  $("#fieldList").replaceChildren(...form.fields.map((f) =>
    el("li", { class: `${f.value == null ? "empty" : ""} ${f.current ? "current" : ""}` }, el("span", {}, f.label), el("span", { class: "v" }, f.value ?? "…"))));
  $("#docList").replaceChildren(...(form.documents || []).map((d) => el("li", {}, d)));
}
function openFormSheet() { renderFormSheet(); $("#formSheet").hidden = false; }

function applicationCard(a) {
  const extra = el("details", { class: "extra" },
    el("summary", {}, tr("more")),
    a.deadline_note ? el("p", { class: "deadline" }, "⏱ " + a.deadline_note) : null,
    el("p", {}, el("b", {}, tr("takeTo") + ": "), a.submit_to),
    a.next_step ? el("p", {}, a.next_step) : null);
  return el("div", { class: "card done-card" },
    el("p", { class: "ref-label" }, "✅ " + tr("prepared") + " · " + tr("reference")),
    el("p", { class: "ref" }, a.id),
    el("p", { class: "follow" }, `${tr("followUp")}: ${a.follow_up_on}`),
    el("a", { class: "btn wide", href: a.print_url, target: "_blank", rel: "noopener" }, "🖨 " + tr("print")),
    extra);
}

function documentsCard(items) {
  return el("div", { class: "card light" }, el("h3", {}, "📄 " + tr("bring")),
    el("ul", { class: "checks" }, items.map((d) => el("li", {}, d))));
}

function reviewCard(form) {
  return el("div", { class: "card light" },
    el("ul", { class: "review" }, form.fields.filter((f) => f.value != null).map((f) =>
      el("li", {}, el("span", {}, f.label), el("b", {}, f.value)))));
}

function eligibilityCard(results) {
  return el("div", { class: "card" }, el("h3", {}, "✨ " + tr("schemes")),
    el("ul", { class: "elig" }, results.map((r) => el("li", {},
      el("div", {}, el("span", { class: `tag ${r.status}` }, tr(r.status)), el("b", {}, r.name)),
      r.status !== "not_eligible" ? el("div", { class: "why" }, r.benefit) : el("div", { class: "why" }, r.reasons[0] || ""),
      r.status === "eligible" && r.service ? el("button", { class: "btn ghost", style: "margin-top:8px;min-height:44px", onclick: () => sendText(`${tr("applyFor")} ${r.name}`) }, tr("apply")) : null))));
}

function applicationsCard(apps) {
  if (!apps.length) return null;
  return el("div", { class: "card" }, el("h3", {}, "📋 " + tr("myApps")),
    el("ul", { class: "mini-list" }, apps.map((a) => el("li", {},
      el("span", {}, a.title),
      el("a", { href: `/api/applications/${a.id}/print`, target: "_blank", rel: "noopener" }, `${a.id}${a.overdue ? " ⚠️" : ""}`)))));
}

/* ---------------- history ---------------- */
function remember(who, text) { state.history.push({ who, text }); }
function renderHistory() {
  $("#historyList").replaceChildren(...state.history.map((m) => el("div", { class: `h-msg ${m.who}` }, m.text)));
}

/* ---------------- conversation ---------------- */
async function newSession() {
  const res = await api("/api/session", { lang: state.lang });
  state.sessionId = res.session_id;
  state.history = [{ who: "bot", text: res.greeting }];
  state.lastReply = res.greeting;
  renderTask(null);
  renderConfirm(null);
  $("#cards").replaceChildren();
  $("#after").replaceChildren();
  showSaid("");
  showReply(res.greeting);
  renderSources(null);
  showHome(true);
  setLive("tap");
}

async function sendText(text) {
  text = (text || "").trim();
  if (!text || state.busy) return;
  stopSpeaking();
  showHome(false);
  showSaid(text);
  remember("user", text);
  $("#cards").replaceChildren();
  $("#after").replaceChildren();
  renderConfirm(null);
  renderSources(null);
  showReply(tr("thinking"), { thinking: true });
  state.busy = true;
  app.classList.add("busy");
  setLive("thinking");
  try {
    const res = await api("/api/chat", { session_id: state.sessionId, text, lang: state.lang });
    renderTask(res.form);
    const evs = (type) => res.events.filter((ev) => ev.type === type);
    let display = res.reply;
    for (const d of evs("documents")) display = display.replace(d.data.sentence, "").replace(/\s{2,}/g, " ").trim();
    if (evs("application").length) display = tr("doneShort");
    else if (res.form?.awaiting_confirmation) display = tr("checkDetails");
    else if (evs("eligibility").length) display = tr("schemesFound");
    showReply(display);
    state.lastReply = res.reply;   // the full reply is what gets spoken
    remember("bot", res.reply);
    renderSources(res.events.filter((ev) => ev.type === "sources").pop()?.data);
    const cards = $("#cards");
    for (const ev of res.events) {
      let card = null;
      if (ev.type === "application") { card = applicationCard(ev.data); remember("bot", `✅ ${ev.data.id} · ${ev.data.title}`); }
      else if (ev.type === "eligibility") card = eligibilityCard(ev.data);
      else if (ev.type === "applications") card = applicationsCard(ev.data);
      else if (ev.type === "documents") { $("#after").append(documentsCard(ev.data.items)); continue; }
      if (card) cards.append(card);
    }
    if (res.form?.awaiting_confirmation) $("#after").append(reviewCard(res.form));
    renderConfirm(res.form);
    window.scrollTo({ top: 0, behavior: "smooth" });
    speak(res.reply);
  } catch (err) {
    if (String(err).startsWith("Error: 404")) { await newSession(); }
    else { showReply("⚠️ " + err.message); setLive("tap"); }
  } finally {
    state.busy = false;
    app.classList.remove("busy");
  }
}

/* ---------------- speech out ---------------- */
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
  if (!state.speakReplies || !text) { setLive("tap"); return; }
  stopSpeaking();
  setLive("speaking");
  if (state.config?.server_speech) {
    try {
      const res = await fetch("/api/tts", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, lang: state.lang }) });
      if (res.ok) {
        state.audio = new Audio(URL.createObjectURL(await res.blob()));
        state.audio.onended = () => setLive("tap");
        await state.audio.play();
        return;
      }
    } catch { /* fall back to the browser's voice */ }
  }
  if (!("speechSynthesis" in window)) { setLive("tap"); return; }
  const u = new SpeechSynthesisUtterance(text);
  u.lang = bcp47();
  const v = pickVoice();
  if (v) u.voice = v;
  u.rate = 0.95;
  u.onend = () => setLive("tap");
  speechSynthesis.speak(u);
}

function renderSpeakToggle() {
  const b = $("#speakToggle");
  b.setAttribute("aria-pressed", String(state.speakReplies));
  b.textContent = state.speakReplies ? tr("voiceOn") : tr("voiceOff");
}
$("#speakToggle").addEventListener("click", () => {
  state.speakReplies = !state.speakReplies;
  localSet("velan.speak", state.speakReplies ? "1" : "0");
  renderSpeakToggle();
  if (!state.speakReplies) stopSpeaking();
});
$("#replay").addEventListener("click", () => { const prev = state.speakReplies; state.speakReplies = true; speak(state.lastReply); state.speakReplies = prev; });

/* ---------------- speech in ---------------- */
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognizer = null;
let recorder = null;

function startBrowserRecognition() {
  recognizer = new Recognition();
  recognizer.lang = bcp47();
  recognizer.interimResults = true;
  recognizer.maxAlternatives = 1;
  let finalText = "";
  let lowConfidence = false;
  recognizer.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const r = e.results[i];
      if (r.isFinal) {
        finalText += r[0].transcript;
        // Chrome reports 0 when it has no estimate; only a real, very low score counts
        if (r[0].confidence > 0 && r[0].confidence < 0.35) lowConfidence = true;
      } else interim += r[0].transcript;
    }
    setLive(null, interim || finalText || tr("listening"));
  };
  recognizer.onerror = () => { stopListening(); didNotCatch(); };
  recognizer.onend = () => {
    const text = finalText.trim();
    stopListening();
    if (!text || lowConfidence) didNotCatch(); else sendText(text);
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
    setLive("thinking");
    try {
      const res = await fetch("/api/stt", { method: "POST", body: fd });
      const { text } = await res.json();
      if (text) sendText(text); else didNotCatch();
    } catch { didNotCatch(); }
  };
  recorder.start();
}

function didNotCatch() {
  showHome(false);
  showReply(tr("heardNothing"));
  state.lastReply = tr("heardNothing");
  speak(tr("heardNothing"));
}

function stopListening() {
  state.listening = false;
  app.classList.remove("listening");
}

micBtn.addEventListener("click", async () => {
  stopSpeaking();
  if (state.busy) return;
  if (state.listening) {
    // the second tap ends the utterance
    if (recognizer) recognizer.stop();
    if (recorder && recorder.state === "recording") recorder.stop();
    return;
  }
  const canServer = state.config?.server_speech && navigator.mediaDevices && window.MediaRecorder;
  if (!Recognition && !canServer) {
    setLive("noMic");
    $("#textForm").hidden = false;
    return;
  }
  state.listening = true;
  app.classList.add("listening");
  setLive("listening");
  try {
    // server speech-to-text handles code-mixed Indian speech better, when configured
    if (canServer) await startServerRecording(); else startBrowserRecognition();
  } catch {
    stopListening();
    setLive("noMic");
    $("#textForm").hidden = false;
  }
});

/* ---------------- typing, sheets, notices ---------------- */
$("#kbBtn").addEventListener("click", () => {
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
$("#historyBtn").addEventListener("click", () => { renderHistory(); $("#history").hidden = false; });
$("#myAppsBtn").addEventListener("click", () => { $("#history").hidden = true; sendText(tr("myApps")); });
$("#newChat").addEventListener("click", async () => { $("#history").hidden = true; stopSpeaking(); await newSession(); });
document.querySelectorAll("[data-close]").forEach((b) => b.addEventListener("click", () => { $("#" + b.dataset.close).hidden = true; }));
document.querySelectorAll(".sheet").forEach((s) => s.addEventListener("click", (e) => { if (e.target === s) s.hidden = true; }));
document.addEventListener("keydown", (e) => { if (e.key === "Escape") document.querySelectorAll(".sheet").forEach((s) => { s.hidden = true; }); });

function renderModeChip() {
  const chip = $("#modeChip");
  if (!state.config) return;
  const lines = [];
  if (state.config.agent === "offline") lines.push(tr("keyNotSet"));
  if (!state.config.server_speech) lines.push(tr("speechKeyNotSet"));
  chip.hidden = !lines.length;
  chip.textContent = chip.classList.contains("open") ? lines.join(" ") : "ⓘ " + tr("basicMode");
  chip.onclick = () => { chip.classList.toggle("open"); renderModeChip(); };
}

/* ---------------- start ---------------- */
(async function boot() {
  if ("speechSynthesis" in window) speechSynthesis.getVoices();
  state.config = await api("/api/config");
  applyLang();
  await loadServices();
  await newSession();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
})();
