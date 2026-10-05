// SVG → WebP 300x418 с прозрачными углами: node raster.js <srcDir> <outDir>
const puppeteer = require('puppeteer'); const fs = require('fs'); const path = require('path');
(async () => {
  const [src, out, W = '300', H = '418', pre = ''] = process.argv.slice(2); fs.mkdirSync(out, {recursive: true});
  const b = await puppeteer.launch({headless: 'shell', args: ['--no-sandbox', '--allow-file-access-from-files']});
  const p = await b.newPage(); await p.setViewport({width: +W, height: +H});
  for (const f of fs.readdirSync(src).filter(x => x.endsWith('.svg') && x.startsWith(pre))) {
    const hf = path.resolve(src, '_r.html'); fs.writeFileSync(hf, `<html><body style="margin:0;background:transparent"><img id="i" src="${f}" style="width:${W}px;height:${H}px;display:block"></body></html>`);
    await p.goto('file://' + hf);
    await p.waitForFunction(() => document.getElementById('i').complete);
    await p.screenshot({path: path.join(out, f.replace('.svg', '.webp')), type: 'webp', quality: 86, omitBackground: true});
  }
  await b.close();
})();
