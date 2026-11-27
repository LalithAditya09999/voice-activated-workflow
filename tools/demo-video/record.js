const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path = require('path');
const out = process.argv[2];
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: out, size: { width: 1920, height: 1080 } } });
  const p = await ctx.newPage();
  const marks = [];
  const t0 = Date.now();
  const mark = (label) => marks.push(`${((Date.now() - t0) / 1000).toFixed(1)}s  ${label}`);
  await p.goto('file://' + path.join(__dirname, 'stage.html'));
  await p.evaluate(() => showCard('c-title'));
  const app = () => p.frames().find(f => f.url().startsWith('http://localhost:3000'));
  for (let i = 0; i < 100 && !app(); i++) await sleep(100);
  await app().waitForSelector('.chip');
  const cap = (step, en, ta, gloss) => p.evaluate(([a, b, c, d]) => setCap(a, b, c, d), [step, en, ta || '', gloss || '']);
  const settle = () => app().waitForFunction(() => !document.querySelector('.app').classList.contains('busy') && !document.querySelector('.reply').classList.contains('thinking'));
  // shows the mic listening with the words appearing, then sends them as the transcript
  const speak = async (text, ms = 1600) => {
    await app().evaluate(async ([t, dur]) => {
      const appEl = document.querySelector('.app'), live = document.querySelector('#live');
      appEl.classList.add('listening');
      const words = t.split(' ');
      for (let i = 1; i <= words.length; i++) { live.textContent = words.slice(0, i).join(' '); await new Promise(r => setTimeout(r, dur / words.length)); }
      await new Promise(r => setTimeout(r, 250));
      appEl.classList.remove('listening');
      sendText(t);
    }, [text, ms]);
    await sleep(300); await settle();
  };
  const scrollApp = (y) => app().evaluate((yy) => window.scrollTo({ top: yy, behavior: 'smooth' }), y);

  mark('title card'); await sleep(7000);
  await p.evaluate(() => showCard('c-problem')); mark('problem card'); await sleep(7000);
  await p.evaluate(() => showCard('c-intro')); mark('intro card'); await sleep(4500);
  await p.evaluate(() => { showCard(null); tag(true); });
  await cap('1 · Speak', 'Murugan just says<br><span class="soft">what happened.</span>');
  mark('walkthrough: home'); await sleep(3000);
  await speak('நேற்று மழையில் என் நெல் சேதமானது, ரெண்டு ஏக்கர்', 2400);
  mark('farmer speaks');
  await cap('2 · Deadline first', 'Velan says the deadline first,<br><span class="soft">then what to bring.</span>', 'சேதம் நடந்த 72 மணி நேரத்துக்குள் தெரிவிக்கவும்', 'Report within 72 hours of the damage.');
  await sleep(4500); await scrollApp(360); await sleep(3500); await scrollApp(0); await sleep(1200);
  await cap('3 · Never asks twice', 'It keeps the date, the cause<br><span class="soft">and the acres he already said.</span>', 'ஆமாம்', 'Yes, fill it with me.');
  await speak('ஆமாம்', 700); mark('form starts'); await sleep(3500);
  await cap('4 · One question at a time', 'Short questions,<br><span class="soft">one at a time.</span>');
  for (const a of ['நெல்', 'வங்கி', 'முருகன்']) { await speak(a, 700); await sleep(1700); }
  await speak('98765 43210', 1200);
  await cap('5 · Numbers checked', 'Numbers are read back<br><span class="soft">digit by digit.</span>', '9 8 7 6 5, 4 3 2 1 0 — சரியா?', 'I heard 98765 43210. Is that right?');
  mark('digit read-back'); await sleep(4200);
  await speak('ஆமாம்', 600); await sleep(1000);
  await cap('4 · One question at a time', 'Short questions,<br><span class="soft">one at a time.</span>');
  for (const a of ['தேனி', 'கம்பம்', '45/2', 'ஆமாம்']) { await speak(a, 700); await sleep(1500); }
  await cap('6 · Read back', 'Everything is read back.<br><span class="soft">Nothing goes ahead without a spoken yes.</span>', 'இந்த விவரங்கள் சரியா?', 'Are these details correct?');
  mark('full read-back'); await sleep(3000); await scrollApp(420); await sleep(3200); await scrollApp(0); await sleep(1000);
  await speak('ஆமாம்', 700);
  await cap('7 · Done', 'A reference number,<br><span class="soft">a printable form and a follow-up date.</span>');
  mark('application ready'); await sleep(4000);
  const href = await app().evaluate(() => document.querySelector('.done-card a.btn').href);
  await p.evaluate((u) => showPrint(u), href); mark('printable form'); await sleep(5500);
  await p.evaluate(() => showPrint(null)); await sleep(800);
  await app().evaluate(() => newSession()); await sleep(1500);
  await cap('8 · Both paths', 'Ask about farming: chemical and organic,<br><span class="soft">with side effects. The farmer chooses.</span>', 'ரசாயன உரமா இயற்கை உரமா, எது நல்லது?', 'Chemical or organic fertiliser, which is better?');
  await speak('ரசாயன உரமா இயற்கை உரமா, எது நல்லது?', 2000); mark('organic vs chemical'); await sleep(3500);
  await app().evaluate(() => document.querySelector('.more')?.click()); await sleep(4500);
  await cap('9 · Three languages', 'Tamil, Hindi or English,<br><span class="soft">mixed freely.</span>');
  await app().evaluate(() => window.scrollTo(0, 0));
  await app().evaluate(() => document.querySelector('[data-lang="en"]').click()); mark('English'); await sleep(3000);
  await app().evaluate(() => document.querySelector('[data-lang="hi"]').click()); mark('Hindi'); await sleep(2800);
  await p.evaluate(() => { tag(false); showCard('c-docker'); }); mark('docker card'); await sleep(6500);
  await p.evaluate(() => showCard('c-end')); mark('end card'); await sleep(7000);
  mark('end');
  const video = p.video();
  await ctx.close(); await b.close();
  console.log((await video.path()));
  console.log(marks.join('\n'));
})();
