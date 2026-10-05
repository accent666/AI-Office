const puppeteer = require('puppeteer'); const wait = ms => new Promise(r => setTimeout(r, ms));
(async () => { const b = await puppeteer.launch({headless: 'shell', args: ['--no-sandbox']}); const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
 await p.setViewport({width: 390, height: 780}); await p.goto('https://2-56-120-214.sslip.io/monaco/test.html', {waitUntil: 'networkidle0'}); await wait(500);
 for (const v of ['games','bjset','dkset','bcset','setup','shop','inv','me','home']) { await p.evaluate(v => go(v), v); await wait(300); }
 await p.evaluate(() => { go('shop'); $('shopf').children[1].click(); $('shopsort').click(); });
 const n = await p.evaluate(() => $('shop').children.length); await p.screenshot({path: '/tmp/claude-0/-root-agents-dev/444327f4-c212-4b71-84f5-cac5c3756b6e/scratchpad/o/smoke.png'});
 console.log('errors:', errs.length ? errs : 'none', 'shop items:', n); await b.close(); })();
