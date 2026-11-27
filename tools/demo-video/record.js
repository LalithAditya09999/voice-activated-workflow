const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/opt/node-tools/node_modules/playwright');
const path = require('path');
const out = process.argv[2];
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: out, size: { width: 1920, height: 1080 } } });
  const p = await ctx.newPage();
  const marks = []; const t0 = Date.now();
  const mark = (label) => marks.push(`${((Date.now() - t0) / 1000).toFixed(1)}s  ${label}`);
  await p.goto('file://' + path.join(__dirname, 'stage.html'));
  await p.evaluate(() => showCard('c-title'));
  const app = () => p.frames().find(f => f.url().startsWith('http://localhost:3000'));
  for (let i = 0; i < 100 && !app(); i++) await sleep(100);
  await app().waitForSelector('.chip');
  const cap = (step, en, ta, gloss) => p.evaluate(([a, b, c, d]) => setCap(a, b, c, d), [step, en, ta || '', gloss || '']);
  const settle = () => app().waitForFunction(() => !document.querySelector('.app').classList.contains('busy') && !document.querySelector('.reply').classList.contains('thinking'));
  // the mic listens and the words appear, then they are sent as the transcript (voice input simulated)
  const speak = async (text, ms = 1400) => {
    await app().evaluate(async ([t, dur]) => {
      const appEl = document.querySelector('.app'), live = document.querySelector('#live');
      appEl.classList.add('listening');
      const words = t.split(' ');
      for (let i = 1; i <= words.length; i++) { live.textContent = words.slice(0, i).join(' '); await new Promise(r => setTimeout(r, dur / words.length)); }
      await new Promise(r => setTimeout(r, 200));
      appEl.classList.remove('listening');
      sendText(t);
    }, [text, ms]);
    await sleep(250); await settle();
  };
  const quick = async (answers, gap = 900) => { for (const a of answers) { await speak(a, 550); await sleep(gap); } };
  const scrollApp = (y) => app().evaluate((yy) => window.scrollTo({ top: yy, behavior: 'smooth' }), y);
  const home = async () => { await app().evaluate(() => newSession()); await sleep(1200); };

  mark('title card'); await sleep(7000);
  await p.evaluate(() => showCard('c-problem')); mark('problem card'); await sleep(6500);
  await p.evaluate(() => showCard('c-intro')); mark('intro card'); await sleep(4500);
  await p.evaluate(() => { showCard(null); tag(true); });

  // 1. plan the season
  await cap('Morning · Plan the season', 'What should I plant<br><span class="soft">this season?</span>', 'சம்பா பருவத்தில் என்ன பயிரிடலாம்?', 'What can I plant in Samba season?');
  mark('season'); await sleep(2500);
  await speak('சம்பா பருவத்தில் என்ன பயிரிடலாம்?', 1800); await sleep(3000);
  await app().evaluate(() => document.querySelector('.more')?.click()); await sleep(4000);

  // 2. find every scheme
  await home();
  await cap('Find every benefit', 'Which schemes can I get?<br><span class="soft">Nine quick spoken answers.</span>', 'எனக்கு எந்தத் திட்டங்கள் கிடைக்கும்?', 'Which schemes can I get?');
  mark('schemes'); await sleep(2000);
  await speak('எனக்கு எந்தத் திட்டங்கள் கிடைக்கும்?', 1600); await sleep(1500);
  await quick(['ஆமாம்', 'ஆமாம்', '3', 'போர்வெல்', 'இல்லை', 'இல்லை', '45', 'இல்லை', 'இல்லை']);
  await speak('ஆமாம்', 500);
  await cap('Find every benefit', 'Every scheme he qualifies for,<br><span class="soft">and why.</span>');
  mark('schemes found'); await sleep(3500); await scrollApp(500); await sleep(3000); await scrollApp(0); await sleep(800);

  // 3. apply for drip irrigation
  await home();
  await cap('Get it done', 'Apply for the<br><span class="soft">drip irrigation subsidy.</span>', 'சொட்டு நீர் பாசனம் வேண்டும்', 'I want drip irrigation.');
  mark('drip'); await sleep(1500);
  await speak('சொட்டு நீர் பாசனம் வேண்டும்', 1500); await sleep(2500); await scrollApp(330); await sleep(2800); await scrollApp(0); await sleep(600);
  await cap('Get it done', 'The documents to bring,<br><span class="soft">then one question at a time.</span>');
  await speak('ஆமாம்', 500); await sleep(1500);
  await quick(['முருகன்', 'ராமசாமி']);
  await speak('98765 43210', 1000);
  await cap('Numbers checked', 'Numbers are read back<br><span class="soft">digit by digit.</span>', '9 8 7 6 5, 4 3 2 1 0 — சரியா?', 'I heard 98765 43210. Is that right?');
  mark('digits'); await sleep(3500);
  await cap('Get it done', 'One question at a time.');
  await quick(['ஆமாம்', '1234 5678 9012', 'ஆமாம்', 'தேனி', 'கம்பம்', 'சுருளிப்பட்டி', '123/4', 'ஆமாம்', '2', 'போர்வெல்', 'தென்னை', 'சிறு'], 700);
  await cap('Read back', 'Everything is read back.<br><span class="soft">Nothing goes ahead without a spoken yes.</span>', 'இந்த விவரங்கள் சரியா?', 'Are these details correct?');
  mark('read back'); await sleep(2500); await scrollApp(420); await sleep(2500); await scrollApp(0); await sleep(600);
  await speak('ஆமாம்', 500);
  await cap('Done', 'A reference number,<br><span class="soft">a printable form and a follow-up date.</span>');
  mark('done'); await sleep(3200);
  const href = await app().evaluate(() => document.querySelector('.done-card a.btn').href);
  await p.evaluate((u) => showPrint(u), href); await sleep(4500);
  await p.evaluate(() => showPrint(null)); await sleep(700);

  // 4. farming advice, both paths
  await home();
  await cap('Farming advice', 'Chemical or organic?<br><span class="soft">Both paths, with side effects. He chooses.</span>', 'ரசாயன உரமா இயற்கை உரமா, எது நல்லது?', 'Chemical or organic fertiliser, which is better?');
  mark('advice'); await sleep(1500);
  await speak('ரசாயன உரமா இயற்கை உரமா, எது நல்லது?', 1800); await sleep(2000);
  await app().evaluate(() => document.querySelector('.more')?.click()); await sleep(4000);

  // 5. family too
  await home();
  await cap('For the family too', 'A pension for his mother,<br><span class="soft">with the documents to bring.</span>', 'அம்மாவுக்கு முதியோர் ஓய்வூதியம் வேண்டும்', 'My mother needs an old-age pension.');
  mark('pension'); await sleep(1500);
  await speak('அம்மாவுக்கு முதியோர் ஓய்வூதியம் வேண்டும்', 1700); await sleep(3000); await scrollApp(330); await sleep(2500); await scrollApp(0);

  // 6. languages
  await home();
  await cap('Three languages', 'Tamil, Hindi or English,<br><span class="soft">mixed freely.</span>');
  await app().evaluate(() => document.querySelector('[data-lang="en"]').click()); mark('English'); await sleep(2800);
  await app().evaluate(() => document.querySelector('[data-lang="hi"]').click()); await sleep(2500);
  await app().evaluate(() => document.querySelector('[data-lang="ta"]').click()); await sleep(1500);

  await p.evaluate(() => { tag(false); showCard('c-docker'); }); mark('docker card'); await sleep(6000);
  await p.evaluate(() => showCard('c-end')); mark('end card'); await sleep(6500);
  mark('end');
  const video = p.video();
  await ctx.close(); await b.close();
  console.log(await video.path());
  console.log(marks.join('\n'));
})();
