const puppeteer = require('puppeteer'); const wait = ms => new Promise(r => setTimeout(r, ms));
(async () => { const b = await puppeteer.launch({headless: 'shell', args: ['--no-sandbox']}); const p = await b.newPage(); const errs = [];
 p.on('pageerror', e => errs.push(e.message)); await p.setViewport({width: 390, height: 700});
 await p.evaluateOnNewDocument(() => { localStorage.setItem('riviera_sound', '0');
   Element.prototype.animate = function(){ return {finished: Promise.resolve(), cancel(){}, onfinish: null, set onfinish(f){ f && f(); }}; }; });
 await p.goto('https://2-56-120-214.sslip.io/monaco/test.html', {waitUntil: 'networkidle0'});
 await p.evaluate(() => { window.sleep = () => Promise.resolve(); setInterval(() => { const x = document.getElementById('cutok'); if (x) x.click(); }, 5); S.bal = 100000; });
 await p.evaluate(() => { BJC.n = 4; BJ.t = BJT[0]; go('bj'); }); await wait(300);
 const res = await p.evaluate(async () => {
  const W = () => new Promise(r => setTimeout(r, 5)), vis = id => !$(id).classList.contains('hide'), out = {hands: 0, bad: [], acts: {}};
  const bv = h => bjv(h).t;
  for (let n = 0; n < 400; n++) {
    BJ.bet = [10, 50, 100, 250][n % 4]; renderChips(); const before = S.bal; $('deal').click(); $('deal').click();
    let guard = 0; while (BJ.busy && guard++ < 400) { await W();
      if (vis('bjins')) { const y = Math.random() < .5; out.acts.ins = (out.acts.ins || 0) + y; $(y ? 'insyes' : 'insno').click(); $(y ? 'insyes' : 'insno').click(); continue; }
      if (vis('bjacts') && !BJ.lock) { const opts = ['hit', 'stand']; if (!$('dbl').disabled) opts.push('dbl', 'dbl'); if (!$('spl').disabled) opts.push('spl', 'spl', 'spl');
        const k = opts[Math.floor(Math.random() * opts.length)]; out.acts[k] = (out.acts[k] || 0) + 1; $(k).click(); $(k).click(); } }
    if (BJ.busy) { out.bad.push('stuck ' + n); break; }
    // независимый расчёт
    const d = bv(BJ.d), dbj = d === 21 && BJ.d.length === 2; let exp = 0;
    BJ.hs.forEach(h => { const pv = bv(h.cards), pbj = pv === 21 && h.cards.length === 2 && !h.split; exp -= h.bet;
      if (pv > 21) return; if (pbj && !dbj) exp += h.bet * 2.5; else if (dbj && !pbj) ; else if (d > 21 || pv > d) exp += h.bet * 2; else if (pv === d) exp += h.bet; });
    if (BJ.ins) exp += dbj ? BJ.ins * 2 : -BJ.ins;
    const got = S.bal - before; out.hands++;
    if (got !== exp) out.bad.push(JSON.stringify({n, got, exp, hs: BJ.hs.map(h => [h.cards.join(','), h.bet, h.split || 0]), d: BJ.d.join(','), ins: BJ.ins, msg: $('bjmsg').textContent}));
  }
  return out; });
 console.log(JSON.stringify(res, null, 1).slice(0, 3000)); console.log('errs', errs); await b.close(); })();
