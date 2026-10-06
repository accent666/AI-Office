// Скриншоты всех экранов MULBERRY в 4 размерах + автопроверки.
// usage: node shots.js <public_dir> <out_dir> [--orient=auto|portrait|landscape]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.resolve(process.argv[2]), OUT = path.resolve(process.argv[3]);
const ORIENT = (process.argv.find(a => a.startsWith('--orient=')) || '').split('=')[1] || '';
fs.mkdirSync(OUT, { recursive: true });
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.mp3': 'audio/mpeg', '.json': 'application/json' };

// заглушки API (только для тестов): гость не ходит в API, но на всякий случай отвечаем пустым
function stub(act) {
  if (act === 'version') return {};
  return { error: 'offline-test' };
}
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  if (u.startsWith('/api/')) { res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(stub(u.slice(5)))); return; }
  const f = path.join(ROOT, u === '/' ? 'index.html' : u);
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});

const SIZES = [[390, 844], [360, 740], [844, 390], [740, 360]];
const sleep = ms => new Promise(r => setTimeout(r, ms));

// проверки раскладки на текущем экране
async function audit(page) {
  return page.evaluate(() => {
    const W = innerWidth, H = innerHeight, out = [];
    const de = document.documentElement;
    if (de.scrollWidth > W + 1) out.push(`h-scroll документа: ${de.scrollWidth}>${W}`);
    document.querySelectorAll('.scr:not(.hide), .rz:not(.hide), .bsheet:not(.hide)').forEach(s => { if (s.scrollWidth > s.clientWidth + 2) out.push(`h-scroll в #${s.id || s.className}: ${s.scrollWidth}>${s.clientWidth}`); });
    const name = el => (el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + [...el.classList].join('.')) + ' "' + (el.textContent || el.placeholder || '').trim().replace(/\s+/g, ' ').slice(0, 18) + '"';
    const hscroller = el => { for (let p = el.parentElement; p; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if ((o === 'auto' || o === 'scroll') && p.scrollWidth > p.clientWidth + 2) return p; } return null; };
    // элемент реально виден (не закрыт шторкой/оверлеем): проверяем несколько точек
    const onTop = (el, r) => { const pts = [[.5, .5], [.2, .5], [.8, .5]]; for (const [fx, fy] of pts) { const x = r.left + r.width * fx, y = r.top + r.height * fy; if (x < 0 || y < 0 || x >= W || y >= H) continue; const t = document.elementFromPoint(x, y); if (t && (t === el || el.contains(t) || t.contains(el))) return true; } return false; };
    const vis = el => { const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return null; const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity < .05 || cs.pointerEvents === 'none') return null; return r; };
    const btns = [...document.querySelectorAll('button, input, .btn')].filter(b => !b.closest('.hide') && !b.disabled);
    const live = [];
    let small = [];
    for (const b of btns) {
      const r = vis(b); if (!r) continue;
      const hs = hscroller(b);
      if (!hs && (r.right > W + 1 || r.left < -1)) out.push(`за краем по X: ${name(b)} [${Math.round(r.left)}..${Math.round(r.right)}]`);
      if (r.bottom <= 0 || r.top >= H || r.right <= 0 || r.left >= W) continue;
      if (!onTop(b, r)) continue;
      live.push([b, r]);
      if ((r.width < 43.5 || r.height < 43.5) && b.tagName !== 'INPUT') small.push(`${name(b)} ${Math.round(r.width)}x${Math.round(r.height)}`);
    }
    if (small.length) out.push('кнопки <44px: ' + [...new Set(small)].slice(0, 8).join('; ') + (small.length > 8 ? ` …(+${small.length - 8})` : ''));
    // видимая часть: обрезаем по прокручиваемым предкам; «закреплённые» (fixed/sticky) — отдельно
    const clip = (el, r) => { let L = r.left, T = r.top, R = r.right, B = r.bottom; for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) { const cs = getComputedStyle(p); if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') { const q = p.getBoundingClientRect(); L = Math.max(L, q.left); T = Math.max(T, q.top); R = Math.min(R, q.right); B = Math.min(B, q.bottom); } } return {left: L, top: T, right: R, bottom: B}; };
    const pinned = el => { for (let p = el; p && p !== document.body; p = p.parentElement) { const cs = getComputedStyle(p); if (p !== el && (cs.overflowY === 'auto' || cs.overflowY === 'scroll') && p.scrollHeight > p.clientHeight + 2) return false; if (cs.position === 'fixed' || cs.position === 'sticky') return true; } return false; };
    const scrolled = el => { for (let p = el.parentElement; p; p = p.parentElement) { const o = getComputedStyle(p).overflowY; if ((o === 'auto' || o === 'scroll') && p.scrollHeight > p.clientHeight + 2) return true; } return false; };
    for (const x of live) x[1] = clip(x[0], x[1]);
    let ov = [];
    for (let i = 0; i < live.length; i++) for (let j = i + 1; j < live.length; j++) {
      const [a, ra] = live[i], [b, rb] = live[j]; if (a.contains(b) || b.contains(a)) continue;
      const pa = pinned(a), pb = pinned(b);
      if (pa !== pb && scrolled(pa ? b : a)) continue; // контент прокручивается под закреплённой панелью — это нормально
      const x = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), y = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (x > 3 && y > 3) ov.push(`${name(a)} × ${name(b)}`);
    }
    if (ov.length) out.push('наложение кнопок: ' + ov.slice(0, 5).join('; ') + (ov.length > 5 ? ` …(+${ov.length - 5})` : ''));
    // элементы стола: ники игроков не закрыты картами/фишками
    const nk = [...document.querySelectorAll('.scr:not(.hide) .plate b, .scr:not(.hide) .bseat b, .scr:not(.hide) .dko b')].filter(e => vis(e));
    let hid = [];
    for (const e of nk) { const r = e.getBoundingClientRect(); const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (t && !(t === e || e.contains(t) || t.contains(e)) && t.closest('.cd, .pchip, .chip, .chips')) hid.push(name(e)); }
    if (hid.length) out.push('ник закрыт картой/фишкой: ' + hid.slice(0, 4).join('; '));
    // контраст текста: цвет надписи против первого сплошного фона под ней (фон-картинки/градиенты пропускаем)
    const rgb = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return {r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1}; };
    const lum = c => { const f = x => { x /= 255; return x <= .03928 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); }; return .2126 * f(c.r) + .7152 * f(c.g) + .0722 * f(c.b); };
    const blend = (top, bot) => ({r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1});
    const bgOf = el => { let acc = null; for (let p = el; p; p = p.parentElement) { const cs = getComputedStyle(p); if (cs.backgroundImage !== 'none') return null; const c = rgb(cs.backgroundColor); if (c && c.a > 0) { acc = acc ? blend(acc, c) : c; if (acc.a >= .99) return acc; } } return acc ? blend(acc, {r: 0, g: 0, b: 0, a: 1}) : {r: 0, g: 0, b: 0, a: 1}; };
    let low = [];
    const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const seen = new Set();
    while (tw.nextNode()) { const t = tw.currentNode; if (!t.nodeValue.trim()) continue; const el = t.parentElement; if (!el || seen.has(el) || el.closest('.hide, svg, .cd, #bsq')) continue; seen.add(el);
      const r = el.getBoundingClientRect(); if (r.width < 1 || r.bottom <= 0 || r.top >= H || r.right <= 0 || r.left >= W) continue;
      const cs = getComputedStyle(el); if (cs.visibility === 'hidden') continue; let op = 1; for (let p = el; p; p = p.parentElement) op *= +getComputedStyle(p).opacity; if (op < .6) continue; // приглушённое = неактивное
      if (el.closest('button:disabled, .lock')) continue;
      const fg = rgb(cs.color), bg = bgOf(el); if (!fg || !bg) continue;
      const f2 = fg.a < 1 ? blend(fg, bg) : fg; const L1 = lum(f2), L2 = lum(bg); const k = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
      const big = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.66 && +cs.fontWeight >= 700);
      if (k < (big ? 3 : 4.5)) low.push(`"${t.nodeValue.trim().slice(0, 16)}" ${k.toFixed(2)}`); }
    if (low.length) out.push('контраст < 4.5: ' + [...new Set(low)].slice(0, 6).join('; ') + (low.length > 6 ? ` …(+${low.length - 6})` : ''));
    return out;
  });
}

async function main() {
  await new Promise(r => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch();
  const report = {};
  for (const [w, h] of SIZES) {
    const tag = `${w}x${h}`;
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    const errs = [];
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    page.on('pageerror', e => errs.push('pageerror: ' + e.message));
    if (ORIENT) await page.addInitScript(o => { try { localStorage.setItem('mb_orient', o); } catch (e) {} }, ORIENT);
    await page.goto(base, { waitUntil: 'load' });
    await sleep(800);
    const shot = async (name) => {
      await sleep(350);
      const f = path.join(OUT, `${tag}_${name}.png`);
      await page.screenshot({ path: f });
      const a = await audit(page);
      report[`${tag}_${name}`] = a;
    };
    const ev = (fn, ...a) => page.evaluate(fn, ...a).catch(e => errs.push('eval: ' + e.message));
    const goV = v => ev(v => go(v), v);
    const closeSheets = () => ev(() => { try { tsOpen(false); } catch (e) {} document.querySelectorAll('.rz, .rzbg').forEach(e => e.classList.add('hide')); });
    const unsqueeze = () => ev(() => { const b = document.getElementById('bsqall'); for (const b of document.querySelectorAll('#bsqall')) b.click(); });
    const clickSel = async sel => { await ev(sel => { const e = document.querySelector(sel); if (e) e.click(); }, sel); };

    await shot('01_home');
    await ev(() => { const s = document.querySelector('.scr:not(.hide)'); s && s.scrollTo(0, 99999); window.scrollTo(0, 99999); });
    await shot('01b_home_bottom');
    await ev(() => { const s = document.querySelector('.scr:not(.hide)'); s && s.scrollTo(0, 0); window.scrollTo(0, 0); });
    await clickSel('#balbtn'); await shot('02_balance_sheet'); await clickSel('#bsx');
    await goV('games'); await shot('03_games');
    await goV('setup'); await shot('04_poker_lobby');
    await clickSel('#v-setup .tiles [data-ty=bots]'); await shot('05_poker_create_sheet');
    await clickSel('#tsgo'); await sleep(3500); await shot('06_poker_table');
    // ждём своего хода, если ещё нет
    for (let i = 0; i < 20; i++) { const on = await page.evaluate(() => !document.getElementById('pacts').classList.contains('hide')).catch(() => false); if (on) break; await sleep(500); }
    await shot('07_poker_my_turn');
    await ev(() => { const b = document.getElementById('pr'); if (b && !b.closest('.hide')) b.click(); });
    await shot('08_poker_raise_sheet'); await ev(() => { const b = document.getElementById('rzx'); b && b.click(); });
    await goV('bjset'); await shot('09_bj_lobby');
    await clickSel('#v-bjset .tiles [data-ty=bots]'); await clickSel('#tsgo'); await sleep(1200); await shot('10_bj_table_bet');
    await clickSel('#chipsel button'); await clickSel('#deal'); await sleep(2500); await unsqueeze();
    for (let i = 0; i < 16; i++) { const on = await page.evaluate(() => !document.getElementById('bjacts').classList.contains('hide')).catch(() => false); if (on) break; await sleep(500); }
    await shot('11_bj_table_play');
    await goV('bcset'); await shot('12_bc_lobby');
    await clickSel('#v-bcset .tiles [data-ty=bots]'); await clickSel('#tsgo'); await sleep(1200); await shot('13_bc_table');
    await clickSel('#bczp'); await clickSel('#bcdeal'); await sleep(2500); await shot('14_bc_squeeze'); for (let i = 0; i < 4; i++) { await unsqueeze(); await sleep(1200); } await shot('14_bc_table_dealt');
    await unsqueeze(); await sleep(900); await unsqueeze(); await sleep(900);
    await goV('dkset'); await shot('15_dk_lobby');
    await clickSel('#v-dkset .tiles [data-ty=bots]'); await clickSel('#tsgo'); await sleep(4000); await shot('16_dk_table');
    for (const g of ['cs', 'tc', 'pg']) {
      await goV('games'); await ev(g => cgOpen(g), g); await shot(`17_cg_${g}_sheet`); await clickSel('#tsgo'); await sleep(1200); await shot(`18_cg_${g}_table`);
      await ev(() => { const b = document.querySelector('#cgchips button'); b && b.click(); const d = [...document.querySelectorAll('#cgacts button')].pop(); d && d.click(); }); await sleep(2500); for (let i = 0; i < 3; i++) { await unsqueeze(); await sleep(1000); } await shot(`19_cg_${g}_dealt`);
    }
    await goV('games'); await ev(() => stOpen()); await clickSel('#tsgo'); await sleep(5000); await shot('20_stud_table');
    // онлайн-блэкджек и комната «с другом»: состояние стола как от сервера (только для теста)
    const ptState = ph => ({id: 1, lvl: 0, pub: true, name: 'Mulberry 7', code: '1234', min: 10, max: 500, me: 0, n: 1, left: 9, phase: ph, turn: ph === 'play' ? 0 : -1,
      d: ph === 'bet' ? [] : ['AS', 'X'], dt: ph === 'bet' ? null : 11,
      seats: [{name: 'Вы', bet: ph === 'bet' ? 50 : 50, ready: false, h: ph === 'bet' ? [] : ['TH', '7C'], t: 17},
              {name: 'Анна', bet: 20, ready: true, h: ph === 'bet' ? [] : ['9D', '9S'], t: 18},
              {name: 'Игорь_длинный_ник', bet: 100, h: ph === 'bet' ? [] : ['2C', 'KH'], t: 12},
              {name: 'Max', bet: 10, h: ph === 'bet' ? [] : ['5D', '6D', '4S'], t: 15},
              {name: 'Lee', bet: 30, h: ph === 'bet' ? [] : ['QC', '3H'], t: 13}]});
    for (const ph of ['bet', 'play', 'ins']) {
      await ev(v => { PT.id = 1; PT.t = BJT[0]; PT.v = v; PT.shown = {}; PT.chip = PT.t.ch[0]; if (VIEW !== 'pt') go('pt'); ptDraw(); }, ptState(ph));
      await sleep(1500); await shot(`25_bj_online_${ph}`);
    }
    await ev(() => { clearInterval(PT.poll); });
    await ev(() => { RM.code = '4821'; RM.v = {code: '4821', bet: 100, phase: 'wait', me: 0, n: 0, p: [{name: 'Вы', score: 0, h: [], ready: true}]}; go('room'); roomDraw(); });
    await shot('26_room_wait');
    await ev(() => { RM.v = {code: '4821', bet: 100, phase: 'play', me: 0, turn: 0, left: 12, n: 1, p: [{name: 'Вы', score: 2, h: ['9H', '7D'], t: 16, ready: true}, {name: 'Анна', score: 1, h: ['KS', 'X'], t: null}]}; roomDraw(); });
    await sleep(1500); await shot('27_room_play');
    await ev(() => { RM.code = null; RM.v = null; });
    await goV('home'); await ev(() => duOpen(true)); await sleep(2500); await shot('28_duo'); await ev(() => duOpen(false));
    await goV('shop'); await shot('21_shop');
    await ev(() => { const b = document.querySelector('#shopseg [data-k=pack]'); b && b.click(); }); await shot('21b_shop_packs');
    await clickSel('#shop > *'); await shot('22_shop_item_sheet'); await closeSheets();
    await goV('inv'); await shot('23_inventory');
    await goV('me'); await shot('24_profile');
    await ev(() => { const e = document.getElementById('sets'); e && e.scrollIntoView({block: 'center'}); }); await shot('24c_profile_settings');
    await ev(() => { const s = document.querySelector('.scr:not(.hide)'); s && s.scrollTo(0, 99999); }); await shot('24b_profile_bottom');
    report[`${tag}__console`] = [...new Set(errs)];
    await ctx.close();
  }
  await browser.close(); server.close();
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 1));
  for (const [k, v] of Object.entries(report)) if (v.length) console.log(k + ':\n  - ' + v.join('\n  - '));
}
main().catch(e => { console.error(e); process.exit(1); });
