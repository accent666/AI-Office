const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.route(/^https?:\/\//, r => r.abort()); // реальный сервер не трогаем
  await ctx.addInitScript(() => { window.__calls = []; window.Capacitor = { isNativePlatform: () => true, addListener: () => ({}),
    nativePromise: (p, m, a) => { window.__calls.push(p + '.' + m + ' ' + JSON.stringify(a || {})); return Promise.resolve({}); } }; });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const url = 'file://' + path.resolve(process.argv[2]) + '/index.html';
  await p.goto(url); await p.waitForTimeout(500);
  console.log('старт:', await p.evaluate(() => __calls.filter(c => c.startsWith('Orientation'))));
  await p.evaluate(() => go('me')); await p.click('#setor [data-o=landscape]'); await p.waitForTimeout(200);
  console.log('после выбора:', await p.evaluate(() => [__calls.filter(c => c.startsWith('Orientation')).pop(), localStorage.getItem('mb_orient'), document.querySelector('#setor .on').textContent, document.getElementById('setorn').textContent]));
  await p.click('#setsnd'); console.log('звук:', await p.evaluate(() => [SOUND, document.getElementById('setsnd').getAttribute('aria-checked'), localStorage.getItem('riviera_sound')]));
  await p.reload(); await p.waitForTimeout(500);
  console.log('после перезапуска:', await p.evaluate(() => [__calls.filter(c => c.startsWith('Orientation')), document.documentElement.dataset.orient, document.documentElement.dataset.theme, SOUND]));
  await p.evaluate(() => go('me')); await p.click('#setor [data-o=auto]'); await p.waitForTimeout(200);
  console.log('авто:', await p.evaluate(() => [__calls.filter(c => c.startsWith('Orientation')).pop(), localStorage.getItem('mb_orient')]));
  console.log('тема-кнопка видна:', await p.evaluate(() => getComputedStyle(document.getElementById('theme')).display));
  console.log('ошибки:', errs); await b.close(); })();
