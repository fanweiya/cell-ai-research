// Run: NODE_PATH=<directory containing jsdom> node --test tests/copilot.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..');
const ui = fs.readFileSync(path.join(root,'web/copilot.html'),'utf8');
const script = fs.readFileSync(path.join(root,'web/copilot.js'),'utf8');
function setup(extra = {}, extraPapers = []) {
  const fixture = ['alpha','beta','gamma'].map(id => `<div class="card" data-paper-id="${id}"><button class="ai-read-btn" onclick="readPaper(this)">AI 解读</button><label class="paper-select"><input type="checkbox" onchange="togglePaperSelection(this)"></label></div>`).join('');
  const dom = new JSDOM(fixture+ui,{url:'https://example.test/',runScripts:'outside-only'});
  const w = dom.window;
  w.HTMLDialogElement.prototype.showModal = function(){this.open=true;};
  w.HTMLDialogElement.prototype.close = function(){this.open=false;};
  const papers = ['alpha','beta','gamma'].map(id => ({id,title_en:id,title_zh:'论文'+id,abstract:'Evidence '+id,task_types:['segmentation'],arxiv_url:'https://arxiv.org/abs/'+id, ...(extra[id] || {})})).concat(extraPapers);
  w.eval(`const PAPERS_DB = ${JSON.stringify(papers)}; const LLM_BASE='https://example.test/v1'; const LLM_MODEL='test';`+'\n'+script);
  return {w, d:w.document, close:()=>w.close()};
}
test('reported escaped table with blank lines renders real table and safe links',()=>{
  const x=setup();
  const text='\\| 场景 | 优先路线 | 理由 |\n\n\\|---|---|---|\n\n\\| 标注少 | **方法 A** | [论文](https://arxiv.org/abs/a) |\n\n\\| 跨中心 | 方法 B | 少量标注 |';
  const host=x.d.createElement('div'); host.innerHTML=x.w.parseMarkdown(text);
  assert.equal(host.querySelectorAll('tbody tr').length,2); assert.equal(host.querySelectorAll('th').length,3);
  assert.equal(host.querySelector('strong').textContent,'方法 A'); assert.equal(host.querySelector('a').rel,'noopener noreferrer');
  host.innerHTML=x.w.parseMarkdown('方法 | 条件\n--- | ---\nA | 少标注');
  assert.equal(host.querySelectorAll('tbody td').length,2);
  host.innerHTML=x.w.parseMarkdown('[bad](javascript:alert%281%29) <img src=x onerror=alert(1)>\n```html\n<script>alert(1)</script>\n```');
  assert.equal(host.querySelectorAll('a,script,img').length,0); assert.ok(host.querySelector('code').textContent.includes('<script>'));
  x.close();
});
test('selected scope stays independent from page filters and outgoing snapshot is immutable',async()=>{
  const x=setup(); x.w.readPaper(x.d.querySelector('.ai-read-btn'));
  assert.deepEqual(Array.from(x.w.requestSnapshot('test').papers,p=>p.id),['alpha']);
  x.d.querySelector('.card').style.display='none';
  assert.deepEqual(Array.from(x.w.requestSnapshot('test').papers,p=>p.id),['alpha']);
  let body, release;
  x.w.fetch=async (url,opts)=>{body=JSON.parse(opts.body);return new Promise(resolve=>release=()=>resolve({ok:true,headers:{get:()=>'application/json'},json:async()=>({choices:[{message:{content:'|方法|条件|\n|---|---|\n|A|少标注|'},finish_reason:'stop'}]})}));};
  x.d.getElementById('chatInput').value='compare'; const request=x.w.sendUserMessage();
  x.w.setCopilotScope('all'); await x.w.sendUserMessage();
  assert.ok(body.messages[1].content.includes('Evidence alpha')); assert.ok(!body.messages[1].content.includes('Evidence beta'));
  assert.match(x.d.querySelector('.message-scope').textContent,/指定 1 篇/);
  release(); await request; assert.ok(x.d.querySelector('.msg.ai table'));
  assert.equal(x.w.requestSnapshot('test').papers.length,3); x.close();
});
test('picker cancel does not mutate scope; empty selection cannot send; relation expansion is explicit',()=>{
  const x=setup(); x.w.readPaper(x.d.querySelector('.ai-read-btn'));
  x.w.openPaperPicker(); const checks=x.d.querySelectorAll('.picker-row input'); checks[1].checked=true; checks[1].onchange(); x.w.closePaperPicker();
  assert.equal(x.w.requestSnapshot('test').papers.length,1);
  x.d.getElementById('includeRelated').checked=true;
  const snap=x.w.requestSnapshot('segmentation'); assert.equal(snap.primary.length,1); assert.equal(snap.related.length,2);
  x.d.querySelector('.scope-paper button').click(); assert.equal(x.d.getElementById('chatSendBtn').disabled,true); assert.equal(x.w.requestSnapshot('test').papers.length,0);
  x.close();
});
test('stop resets request state and exposes recovery without automatically resending',async()=>{
  const x=setup(); let calls=0;
  x.w.fetch=(url,opts)=>new Promise((resolve,reject)=>{calls++; opts.signal.addEventListener('abort',()=>reject(new Error('aborted')));});
  x.d.getElementById('chatInput').value='original'; const pending=x.w.sendUserMessage();
  x.d.getElementById('chatInput').value='next draft'; await x.w.sendUserMessage(); assert.equal(calls,1);
  x.w.cancelCopilot(); await pending;
  assert.equal(x.d.getElementById('chatInput').value,'next draft'); assert.equal(x.d.getElementById('chatStopBtn').hidden,true);
  assert.match(x.d.getElementById('chatMessages').textContent,/已停止/); assert.equal(calls,1); x.close();
});

test('entities remain safe, nested lists retain hierarchy, and code pipes stay in table cells',()=>{
  const x=setup(), host=x.d.createElement('div');
  host.innerHTML=x.w.parseMarkdown('**计算**&#x548C;分析 &lt;img src=x onerror=alert(1)&gt; [bad](jav&#x61;script:alert%281%29)\n- 方法\n  - 子项\n    - 细节\n- 结论\n\n| 维度 | 表达式 |\n|---|---|\n| 示例 | `a|b` |');
  assert.ok(host.textContent.includes('计算和分析'));
  assert.equal(host.querySelectorAll('img,a,script').length,0);
  assert.equal(host.querySelectorAll('ul > li > ul > li > ul').length,1);
  assert.equal(host.querySelectorAll('tbody td').length,2);
  assert.equal(host.querySelector('td code').textContent,'a|b'); x.close();
});
test('citation labels follow known paper URLs and unknown chunks are flagged',()=>{
  const x=setup();
  const p={id:'2509.12596',arxiv_url:'https://arxiv.org/html/2509.12596'};
  const q={id:'2411.1788',arxiv_url:'https://arxiv.org/html/2411.1788'};
  const b={id:'biorxiv:10.1101/2024.05.01.591234',arxiv_url:'https://doi.org/10.1101/2024.05.01.591234'};
  const snapshot={papers:[p,q,b],evidence:[
    {paper:p,chunks:[{id:'C009',text:'evidence'}]},
    {paper:q,chunks:[{id:'C012',text:'four digit evidence'}]},
    {paper:b,chunks:[{id:'C003',text:'preprint evidence'}]},
  ]};
  const result=x.w.validateEvidenceCitations(
    '[2509.25096 · C009](https://arxiv.org/html/2509.12596)'
    + ' [2509.12596 · C099](https://arxiv.org/html/2509.12596)'
    + ' [2411.1788 · C012](https://arxiv.org/html/2411.1788)'
    + ' [biorxiv:10.1101/2024.05.01.591234 · C003](https://doi.org/10.1101/2024.05.01.591234)'
    + ' [10.1101/2024.05.01.591234](https://doi.org/10.1101/2024.05.01.591234)'
    + ' [4 位论文 2411.1788](https://arxiv.org/html/2411.1788)'
    + ' [2411.1788 · C012](https://arxiv.org/html/9999.99999)'
    + ' [教程](https://example.com/guide)',snapshot);
  // 文字与链接指向不同论文：保留原文并标注，不能静默换成链接论文。
  assert.ok(result.includes('2509.25096 · C009（引用文字与链接不一致）'));
  assert.ok(!result.includes('[2509.12596 · C009]'));
  assert.ok(result.includes('引用文字与链接指向不同论文'));
  assert.ok(result.includes('C099（引用未匹配）'));
  assert.ok(!result.includes('[2509.12596 · C099]'));
  // 四位 arXiv 编号与 bioRxiv DOI 都是引用标识，不是普通文字链接。
  assert.ok(result.includes('[C012](https://arxiv.org/html/2411.1788 "2411.1788")'));
  assert.ok(result.includes('[C003](https://doi.org/10.1101/2024.05.01.591234 "biorxiv:10.1101/2024.05.01.591234")'));
  assert.ok(result.includes('[摘要](https://doi.org/10.1101/2024.05.01.591234 "biorxiv:10.1101/2024.05.01.591234")'));
  assert.ok(result.includes('[摘要](https://arxiv.org/html/2411.1788 "2411.1788")'));
  assert.ok(result.includes('2411.1788 · C012（引用未匹配）'));
  // 不含论文标识的普通链接仍按内容保留。
  assert.ok(result.includes('[教程](https://example.com/guide)')); x.close();
});
test('single-paper request reads real cached mesh evidence and reuses it on follow-up',async()=>{
  const evidence={version:1,paper_id:'2509.12596',source:'local_paper_text_cache',characters:1000,
    chunks:[{id:'C001',text:'Retrospective study of 147 patients treated with hexahedral meshing. Results reported no self-intersections in the final meshes, but manual refinement was still required for boundary layers.'}]};
  const x=setup({alpha:{evidence_url:'data/evidence/test.json'}}); let loads=0, prompts=[];
  x.w.fetch=async(url,options)=>{
    if(url.includes('/data/evidence/')) { loads++; return {ok:true,json:async()=>({...evidence,paper_id:'alpha'})}; }
    prompts.push(JSON.parse(options.body).messages[1].content);
    return {ok:true,json:async()=>({choices:[{message:{content:'有网格质量评估，但不能等同于零失败率。'}}]})};
  };
  x.w.readPaper(x.d.querySelector('.ai-read-btn'));
  x.d.getElementById('chatInput').value='六面体网格失败率有哪些证据？'; await x.w.sendUserMessage();
  assert.ok(prompts[0].includes('147 patients'));
  assert.ok(prompts[0].includes('no self-intersections'));
  assert.ok(prompts[0].includes('manual refinement'));
  assert.ok(x.d.querySelector('.message-scope').textContent.includes('原文 1 篇'));
  assert.ok(x.d.querySelector('.msg.user').textContent.includes('全部缓存文本'));
  x.d.getElementById('chatInput').value='用表格说明人工修正的限制'; await x.w.sendUserMessage();
  assert.equal(loads,1); assert.equal(prompts.length,2); x.close();
});
test('failed evidence fetch falls back explicitly and cancellation prevents model call',async()=>{
  const x=setup({alpha:{evidence_url:'data/evidence/missing.json'}}); let calls=0;
  x.w.fetch=async(url,options)=>{
    if(url.includes('/data/evidence/')) return {ok:false,status:404};
    calls++; return {ok:true,json:async()=>({choices:[{message:{content:'仅能依据摘要。'}}]})};
  };
  x.w.readPaper(x.d.querySelector('.ai-read-btn')); x.d.getElementById('chatInput').value='方法'; await x.w.sendUserMessage();
  assert.equal(calls,1); assert.ok(x.d.querySelector('.msg.user').textContent.includes('原文读取失败'));
  x.w.fetch=(url,options)=>new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new Error('aborted'))));
  x.d.getElementById('chatInput').value='继续'; const pending=x.w.sendUserMessage(); x.w.cancelCopilot(); await pending;
  assert.equal(calls,1); assert.equal(x.d.getElementById('chatStopBtn').hidden,true); x.close();
});
test('multi-paper evidence stays within budget and retrieves relevant late passages',async()=>{
  const extra=Object.fromEntries(['alpha','beta','gamma'].map(id=>[id,{evidence_url:`data/evidence/${id}.json`}]));
  const x=setup(extra);
  x.w.fetch=async url=>({ok:true,json:async()=>({paper_id:url.split('/').pop().replace('.json',''),
    chunks:Array.from({length:50},(_,i)=>({id:`C${String(i+1).padStart(3,'0')}`,text:(i===40?'mesh failure manual refinement ':'background ').padEnd(1900,'x')}))})});
  const snapshot=x.w.requestSnapshot('网格失败');
  await x.w.prepareEvidence(snapshot,'网格失败',new x.w.AbortController().signal);
  assert.equal(snapshot.evidence.length,3);
  assert.ok(snapshot.evidence.every(e=>!e.complete && e.chunks.some(c=>c.id==='C041')));
  assert.ok(snapshot.evidence.reduce((n,e)=>n+e.chunks.reduce((m,c)=>m+c.text.length,0),0)<=72000);
  x.close();
});

test('transient evidence failure retries and switches to model-generation status',async()=>{
  const x=setup({alpha:{evidence_url:'data/evidence/alpha.json'}});
  let loads=0, release;
  x.w.fetch=async(url)=>{
    if(url.includes('/data/evidence/')) {
      if(++loads===1) throw new x.w.TypeError('Failed to fetch');
      return {ok:true,json:async()=>({paper_id:'alpha',chunks:[{id:'C001',text:'actual evidence'}]})};
    }
    assert.ok(x.d.getElementById('chatStatus').textContent.includes('正在生成回答'));
    assert.ok(!x.d.querySelector('.msg.ai').textContent.includes('正在读取'));
    return {ok:true,json:async()=>({choices:[{message:{content:'answer'}}]})};
  };
  x.w.readPaper(x.d.querySelector('.ai-read-btn'));
  x.d.getElementById('chatInput').value='方法'; await x.w.sendUserMessage();
  assert.equal(loads,2);assert.ok(x.d.querySelector('.msg.user').textContent.includes('原文 1 篇'));
  x.close();
});

test('permanent evidence errors retain HTTP reason without retry',async()=>{
  const x=setup({alpha:{evidence_url:'data/evidence/missing.json'}});let calls=0;
  x.w.fetch=async()=>{calls++;return {ok:false,status:404}};
  const snapshot=x.w.requestSnapshot('test');
  await x.w.prepareEvidence(snapshot,'test',new x.w.AbortController().signal);
  assert.equal(calls,1);assert.ok(snapshot.evidenceFailureDetails.alpha.includes('HTTP 404'));
  x.close();
});


test('over-budget all-library prompt falls back to short cards plus selected abstracts',()=>{
  const many = Array.from({length: 600}, (_, i) => ({
    id: 'p' + i,
    title_en: 'Paper ' + i,
    title_zh: '论文' + i,
    abstract: 'A'.repeat(400),
    task_types: ['segmentation'],
    published_date: '2026-01-01',
    arxiv_url: 'https://arxiv.org/abs/p' + i,
    github_url: i % 2 ? 'https://github.com/x/y' : '',
  }));
  const fixture = many.map(p => '<div class="card" data-paper-id="' + p.id + '"><button class="ai-read-btn" onclick="readPaper(this)">AI 解读</button><label class="paper-select"><input type="checkbox" onchange="togglePaperSelection(this)"></label></div>').join('');
  const dom = new JSDOM(fixture + ui, {url: 'https://example.test/', runScripts: 'outside-only'});
  const w = dom.window;
  w.eval('const PAPERS_DB = ' + JSON.stringify(many) + "; const LLM_BASE='https://example.test/v1'; const LLM_MODEL='test';" + '\n' + script);
  w.setCopilotScope('all');
  const snapshot = w.requestSnapshot('对比不同论文的分割方法');
  const prompt = w.buildResearchPrompt(snapshot, '对比不同论文的分割方法');
  assert.ok(prompt.length < 220000, 'prompt must stay bounded, got ' + prompt.length);
  assert.ok(prompt.includes('短卡片'), 'over-budget path uses brief cards');
  assert.ok(prompt.includes('按问题选读的完整摘要'), 'selected abstracts section present');
  assert.ok(prompt.includes('Paper 599'), 'every paper still appears at least as a brief');
  w.close();
});

test('copilot llm settings override defaults, send bearer key, and reset',async()=>{
  const x=setup();
  const plainConfig=()=>{const c=x.w.getLlmConfig();return {base:c.base,model:c.model,key:c.key};};
  assert.deepEqual(plainConfig(),{base:'https://example.test/v1',model:'test',key:''});
  x.d.getElementById('llmBaseInput').value='https://my.llm.example/v1/';
  x.d.getElementById('llmModelInput').value='my-model';
  x.d.getElementById('llmKeyInput').value='my-secret';
  x.w.saveLlmSettings();
  const saved=JSON.parse(x.w.localStorage.getItem('cell-ai-copilot-llm'));
  assert.deepEqual(saved,{base:'https://my.llm.example/v1',model:'my-model',key:'my-secret'});
  assert.deepEqual(plainConfig(),saved);
  assert.equal(x.w.llmHeaders(x.w.getLlmConfig()).Authorization,'Bearer my-secret');
  x.d.getElementById('chatInput').value='compare';
  let url, headers;
  x.w.fetch=async(u,opts)=>{url=u;headers=opts.headers;return {ok:true,headers:{get:()=>'application/json'},json:async()=>({choices:[{message:{content:'ok'},finish_reason:'stop'}]})};};
  await x.w.sendUserMessage();
  assert.equal(url,'https://my.llm.example/v1/chat/completions');
  assert.equal(headers.Authorization,'Bearer my-secret');
  x.w.resetLlmSettings();
  assert.equal(x.w.localStorage.getItem('cell-ai-copilot-llm'),null);
  assert.deepEqual(plainConfig(),{base:'https://example.test/v1',model:'test',key:''});
  x.close();
});

test('table cells turn chunk ids and paper ids into links',()=>{
  const x=setup({}, [{id:'2411.1788v2',title_en:'target',title_zh:'目标',abstract:'a',task_types:[],arxiv_url:'https://arxiv.org/html/2411.1788'}]);
  const host=x.d.createElement('div');
  host.innerHTML=x.w.parseMarkdown('| 论文 | 证据 | 结论 |\n|---|---|---|\n| 2411.1788v2 | C003、C004 | 有效 |\n| 其他 | 摘要 | 无 |');
  const links=host.querySelectorAll('td a');
  assert.equal(links.length,3);
  assert.equal(links[0].getAttribute('href'),'https://arxiv.org/html/2411.1788');
  assert.equal(links[0].title,'2411.1788v2');
  assert.equal(links[1].textContent,'C003');
  assert.equal(links[2].textContent,'C004');
  x.close();
});
