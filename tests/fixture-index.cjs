const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

// 测试夹具：用 generate_index.generate_html 现场渲染索引页，不依赖本地生成物。
const ROOT = path.resolve(__dirname, '..');
const PAPER_COUNT = 60;

function buildFixture() {
  const script = `
import base64, io, json, sys
sys.path.insert(0, ${JSON.stringify(ROOT)})
import generate_index as g
from PIL import Image

created = []
def write_cache(pid, payload):
    path = g.FIGURES_DIR / f'{pid}.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    created.append(path)

buf = io.BytesIO(); Image.new('RGB', (8, 8), (200, 30, 30)).save(buf, format='JPEG')
tiny = base64.b64encode(buf.getvalue()).decode()
g.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
for i in range(30):
    write_cache(f'2611.{i:05d}', [{'src': 'data/figures/originals/fixture.png', 'caption': '夹具图', 'data': tiny}])

papers = []
for i in range(${PAPER_COUNT}):
    pid = f'2611.{i:05d}v1'
    papers.append({
        'arxiv_id': pid,
        'title': f'Fixture paper {i}',
        'abstract': f'夹具摘要 {i}。' + '用于验证列表分批、筛选与详情渲染。' * 3,
        'published_date': '2026-11-01' if i % 2 else '2026-10-01',
        'authors': 'A. Author',
        'task_type': ['segmentation'],
        'research_score': 6,
        'engineering_score': 5,
        'priority': 5.5,
        'bonus': [],
        'status': {'html': 'done', 'github': {
            'url': 'https://github.com/fixture/repo',
            'provenance': 'paper_code_statement',
            'has_code': True,
            'framework': 'PyTorch',
        }},
        'code_analysis': {},
        'code_analysis_result': {},
        'jev_evaluation': {},
    })
print(g.generate_html(papers, {}, '2026-11-19 00:00'))
for path in created:
    path.unlink(missing_ok=True)
`;
  return execFileSync('/usr/bin/python3', ['-c', script], {
    cwd: ROOT,
    encoding: 'utf-8',
    env: {...process.env, PYTHONPATH: ''},
    maxBuffer: 64 * 1024 * 1024,
  });
}

let cached = null;
function fixtureHtml() {
  if (cached === null) cached = buildFixture();
  return cached;
}

module.exports = {fixtureHtml, PAPER_COUNT};
