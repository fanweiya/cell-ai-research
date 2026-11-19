const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');
const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
function setup(hash='') {
  const errors = [], console = new VirtualConsole();
  console.on('jsdomError', e => errors.push(e.message));
  const dom = new JSDOM(html, {url:'https://example.test/'+hash, runScripts:'dangerously', virtualConsole:console,
    beforeParse(w) { w.HTMLElement.prototype.scrollIntoView = function() {}; w.matchMedia=()=>({matches:false,addEventListener(){}}); }});
  const w = dom.window, d = w.document;
  return {w,d,errors,shown:()=>[...d.querySelectorAll('.card')].filter(c=>c.style.display!=='none'),close:()=>w.close()};
}
test('batching and deferred detail rendering preserve whole-library Copilot scope',()=>{
  const x=setup();
  assert.deepEqual(x.errors,[]);
  assert.equal(x.shown().length,30);
  assert.equal(x.d.querySelectorAll('.card .detail').length,0);
  const total=x.d.querySelectorAll('.card').length;
  x.w.useFilteredPapers(); assert.equal(x.w.requestSnapshot('compare').primary.length,total);
  x.w.loadMorePapers(); assert.equal(x.shown().length,60);
  const details=x.shown()[0].querySelector('.paper-details');
  details.open=true; x.w.hydratePaperDetails(details);
  assert.ok(details.querySelector('.abs-sec[open]'));
  details.open=false; details.open=true; x.w.hydratePaperDetails(details);
  assert.equal(details.querySelectorAll('.detail').length,1);
  x.close();
});
test('expand displayed papers opens abstract figures and repository together, then collapses them',()=>{
  const x=setup(); x.w.toggleAll();
  const shown=x.shown();
  assert.ok(shown.some(c=>c.querySelector('.fig-sec')));
  assert.ok(shown.some(c=>c.querySelector('.repo-sec')));
  assert.ok(shown.every(c=>[...c.querySelectorAll('details')].every(d=>d.open)));
  assert.equal(x.d.querySelectorAll('.card .detail').length,30);
  x.w.toggleAll();
  assert.ok(shown.every(c=>[...c.querySelectorAll('details')].every(d=>!d.open)));
  x.close();
});
test('search reaches later batches and pending debounce cannot use stale Copilot scope',()=>{
  const x=setup(); const last=x.d.querySelector('.card:last-child');
  x.d.getElementById('searchInput').value=last.dataset.paperId;
  x.w.doSearch(); x.w.useFilteredPapers();
  assert.equal(x.shown().length,1);
  assert.equal(x.w.requestSnapshot('question').primary[0].id,last.dataset.paperId);
  x.d.getElementById('searchInput').value='nonexistent-unique-query'; x.w.applyPaperFilters();
  assert.equal(x.d.getElementById('emptyResults').hidden,false);
  assert.equal(x.d.getElementById('loadMorePapers').hidden,true);
  x.w.resetPaperFilters(); assert.equal(x.shown().length,30);
  assert.equal(x.d.querySelectorAll('.fbtn').length,5);
  x.close();
});
test('code and month filters combine and deep links reveal deferred papers',()=>{
  const x=setup();
  x.w.doFilter('code',x.d.querySelectorAll('.fbtn')[1]);
  assert.ok(x.shown().length > 0);
  assert.ok(x.shown().every(c=>c.dataset.code==='1'));
  x.w.doMonthFilter('1900-01'); assert.equal(x.shown().length,0);
  x.w.doMonthFilter('all'); assert.ok(x.shown().length > 0);
  const id=x.d.querySelector('.card:last-child').dataset.paperId; x.close();
  const y=setup('#paper-'+encodeURIComponent(id));
  assert.deepEqual(y.errors,[]);
  const target=y.d.getElementById('paper-'+id);
  assert.notEqual(target.style.display,'none');
  assert.ok(target.querySelector('.paper-details[open] .abs-sec'));
  y.close();
});
