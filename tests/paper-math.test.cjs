const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');
test('expanded Phi-Omni abstract renders nested textsc math safely and only once',()=>{
  const dom=new JSDOM('<!doctype html><div class="abs-body"></div>',{runScripts:'outside-only'});
  for(const file of ['vendor/katex/katex.min.js','vendor/katex/auto-render.min.js','web/paper-math.js']) {
    dom.window.eval(fs.readFileSync(path.join(__dirname,'..',file),'utf8'));
  }
  const body=dom.window.document.querySelector('.abs-body');
  body.textContent=String.raw`记为 $\mathrm{\Phi}$。提出 \textsc{$\mathrm{\Phi}$-Omni}，由 $\mathrm{\Phi}\text{ID}$ 调控，$n$=1031。<img src=x onerror=alert(1)>`;
  dom.window.renderPaperMath(body);
  assert.equal(body.querySelectorAll('.katex').length,4);
  assert.equal(body.querySelectorAll('.katex-error,img').length,0);
  assert.equal(body.querySelector('.latex-smallcaps').textContent.includes('-Omni'),true);
  const before=body.innerHTML;
  dom.window.renderPaperMath(body);
  assert.equal(body.innerHTML,before);
  dom.window.close();
});
