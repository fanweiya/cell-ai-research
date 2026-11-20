"""生成图解目录页 explainers/index.html：从已生成的页面里读出标题、主题与日期。"""

from __future__ import annotations

import html
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLAINERS = ROOT / "explainers"
OUT = EXPLAINERS / "index.html"

H1 = re.compile(r"<h1>(.*?)</h1>", re.S)
EYEBROW = re.compile(r'class="(?:ve-)?eyebrow">(.*?)</(?:p|div)>', re.S)
LEAD = re.compile(r'<p class="lead">(.*?)</p>', re.S)
TAGS = re.compile(r"<[^>]+>")

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>图解目录 · 细胞与 AI 论文索引</title>
<style>
:root{{--ink:#1b1d22;--muted:#5d6470;--line:#e3e6ec;--paper:#fbfbf9;--accent:#2c4cd0;--chip:#eef2ff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 "Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif}}
header{{padding:40px 24px 12px;max-width:1080px;margin:0 auto}}
.crumb{{font-size:13px;color:var(--muted);letter-spacing:.04em}}
h1{{font:600 34px/1.3 "Noto Serif SC","Songti SC",serif;margin:10px 0 6px}}
.count{{color:var(--muted);font-size:14px}}
.tools{{max-width:1080px;margin:18px auto 0;padding:0 24px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}}
input[type=search]{{flex:1 1 260px;min-width:200px;padding:10px 14px;border:1px solid var(--line);border-radius:10px;background:#fff;font-size:15px}}
.chips{{max-width:1080px;margin:12px auto 0;padding:0 24px;display:flex;flex-wrap:wrap;gap:8px}}
.chip{{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:999px;padding:5px 12px;font-size:13px;cursor:pointer}}
.chip.active{{background:var(--chip);border-color:#c7d2fe;color:var(--accent);font-weight:600}}
main{{max-width:1080px;margin:0 auto;padding:22px 24px 64px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
a.card{{display:block;padding:16px 18px;border:1px solid var(--line);border-radius:14px;background:#fff;text-decoration:none;color:inherit}}
a.card:hover{{border-color:#c7d2fe;box-shadow:0 6px 18px rgba(44,76,208,.08)}}
a.card h2{{font:600 17px/1.5 "Noto Serif SC","Songti SC",serif;margin:0 0 6px}}
a.card p{{margin:0;font-size:13px;color:var(--muted)}}
a.card .meta{{margin-top:10px;font-size:12px;color:#8a90a0}}
.empty{{grid-column:1/-1;color:var(--muted);padding:28px 0}}
@media (prefers-color-scheme: dark){{
 :root{{--ink:#e8e9ee;--muted:#a4a9b6;--line:#2c3038;--paper:#15171b;--chip:#1e2540}}
 input[type=search],.chip,a.card{{background:#1b1e24;color:var(--ink)}}
}}
</style>
</head>
<body>
<header>
  <div class="crumb"><a href="../index.html">← 返回论文索引</a></div>
  <h1>图解目录</h1>
  <p class="count">每篇论文一张单页图解：机制全图、新旧做法对比、关键数字与边界。<span id="shown">{count}</span> / {count} 篇</p>
</header>
<div class="tools"><input id="q" type="search" placeholder="搜索标题、主题或日期" aria-label="搜索图解"></div>
<div class="chips" id="chips">
  <button class="chip active" data-topic="">全部</button>
{chips}
</div>
<main id="list">
{cards}
</main>
<p class="empty" id="empty" hidden>没有匹配的图解，换个词试试。</p>
<script>
const q = document.getElementById('q');
const chips = document.getElementById('chips');
const cards = Array.from(document.querySelectorAll('a.card'));
const shown = document.getElementById('shown');
const empty = document.getElementById('empty');
let topic = '';
let keyword = '';
function apply() {{
  let n = 0;
  for (const card of cards) {{
    const okTopic = !topic || card.dataset.topic.split('|').includes(topic);
    const okWord = !keyword || card.dataset.text.includes(keyword);
    const show = okTopic && okWord;
    card.hidden = !show;
    if (show) n += 1;
  }}
  shown.textContent = n;
  empty.hidden = n !== 0;
}}
q.addEventListener('input', () => {{ keyword = q.value.trim().toLowerCase(); apply(); }});
chips.addEventListener('click', (event) => {{
  const btn = event.target.closest('.chip');
  if (!btn) return;
  topic = btn.dataset.topic;
  chips.querySelectorAll('.chip').forEach((c) => c.classList.toggle('active', c === btn));
  apply();
}});
</script>
</body>
</html>
"""

CARD = """<a class="card" href="{pid}.html" data-topic="{topics}" data-text="{text}">
<h2>{headline}</h2>
<p>{lead}</p>
<div class="meta">{topic_label} · {day} · {chars} 字</div>
</a>"""


def clean(text: str) -> str:
    text = TAGS.sub("", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def build() -> int:
    cards = []
    topic_counts: Counter[str] = Counter()
    for page in sorted(EXPLAINERS.glob("*.html")):
        if page.name == "index.html":
            continue
        source = page.read_text(encoding="utf-8")
        head = H1.search(source)
        eyebrow = EYEBROW.search(source)
        lead = LEAD.search(source)
        headline = clean(head.group(1)) if head else page.stem
        parts = [clean(part) for part in eyebrow.group(1).split("·")] if eyebrow else []
        topics = [part for part in (parts[1].split("/") if len(parts) > 1 else []) if part]
        day = parts[2] if len(parts) > 2 else ""
        for topic in topics:
            topic_counts[topic] += 1
        body = clean(lead.group(1)) if lead else ""
        lead_text = body[:80] + ("…" if len(body) > 80 else "")
        text = " ".join([headline, " ".join(topics), day, body[:160]]).lower()
        cards.append(CARD.format(
            pid=page.stem,
            topics=html.escape("|".join(topics), quote=True),
            text=html.escape(text, quote=True),
            headline=html.escape(headline),
            lead=html.escape(lead_text),
            topic_label=html.escape(" / ".join(topics)),
            day=html.escape(day),
            chars=len(re.findall(r"[\u4e00-\u9fff]", source)),
        ))
    chips = []
    for topic, count in topic_counts.most_common(14):
        chips.append(f'<button class="chip" data-topic="{html.escape(topic, quote=True)}">{html.escape(topic)} ({count})</button>')
    OUT.write_text(PAGE.format(count=len(cards), chips="\n  ".join(chips), cards="\n".join(cards)), encoding="utf-8")
    print(f"目录 {len(cards)} 篇，主题 {len(topic_counts)} 个 → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
