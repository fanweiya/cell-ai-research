"""给图解页补一段「原文关键图」，图取自论文原页，配注沿用站点的图注分析。

单独跑时遍历 explainers/ 下所有页面；生成流水线在每篇渲染成功后调 insert_for(pid)。
"""

from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLAINERS = ROOT / "explainers"
FIGURES = ROOT / "data" / "figures"
RENDER = ROOT / "tools" / "visual-explainer" / "plugins" / "visual-explainer" / "kit" / "render.mjs"

STYLE = (
    ".fig-pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:var(--s-4);margin-top:var(--s-3)}"
    ".fig-pair figure{margin:0}"
    ".fig-pair img{width:100%;height:auto;border:1px solid var(--border);border-radius:var(--r-2);background:#fff}"
    ".fig-pair figcaption{font-size:var(--t-small);color:var(--muted);line-height:1.5;margin-top:var(--s-1)}"
)

SANITIZE = {"对齐": "对应", "闭环": "循环", "落地": "实现", "钉死": "固定", "技术栈": "技术组合"}

NAV = '<a href="#figures">原图</a>'

SECTION = """<section id="figures">
<h2>原文关键图</h2>
<p>下面两张图取自论文原页，配注由站点自动摘写，可对照上面的机制与数字一起看。</p>
<div class="fig-pair">
{figures}
</div>
</section>
"""

FIGURE = """<figure>
<img src="../data/figures/previews/{name}" alt="{alt}" loading="lazy">
<figcaption>{caption}</figcaption>
</figure>"""


def clean(text: str) -> str:
    for word, replacement in SANITIZE.items():
        text = text.replace(word, replacement)
    return text


def source_path(pid: str) -> Path | None:
    for path in (
        ROOT / "data" / "explainers" / "agent" / pid / "out" / f"{pid}.src.html",
        ROOT / "data" / "explainers" / "src" / f"{pid}.src.html",
    ):
        if path.exists():
            return path
    return None


def pick(pid: str) -> list[tuple[str, str, str]]:
    base = pid.split("v")[0]
    analysis_path = FIGURES / f"{pid}_analysis.json"
    if not analysis_path.exists():
        analysis_path = FIGURES / f"{base}_analysis.json"
    if not analysis_path.exists():
        return []
    try:
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    rows = []
    for key, info in analysis.items():
        if not isinstance(info, dict) or not info.get("relevant"):
            continue
        caption = (info.get("caption") or "").strip()
        if len(caption) < 12:
            continue
        preview = FIGURES / "previews" / f"{pid}_{int(key) + 1}.jpg"
        if not preview.exists():
            preview = FIGURES / "previews" / f"{base}_{int(key) + 1}.jpg"
        if not preview.exists():
            continue
        rows.append((info.get("score", 0), caption, preview.name))
    rows.sort(key=lambda row: (-row[0], row[1]))
    return rows[:2]


def insert_for(pid: str) -> bool:
    src = source_path(pid)
    if src is None:
        return False
    source = src.read_text(encoding="utf-8")
    if 'id="figures"' in source:
        if NAV in source or '<a href="#limits"' not in source:
            return False
        updated = source.replace('<a href="#limits"', NAV + '<a href="#limits"', 1)
        return render(pid, src, source, updated)
    rows = pick(pid)
    if not rows:
        return False
    marker = source.find('id="limits"')
    if marker == -1:
        return False
    anchor = source.rfind("<section", 0, marker)
    if anchor == -1:
        return False
    blocks = "\n".join(
        FIGURE.format(
            name=name,
            caption=html.escape(clean(caption), quote=True),
            alt=html.escape(clean(caption)[:40], quote=True),
        )
        for _, caption, name in rows
    )
    updated = source[:anchor] + SECTION.format(figures=blocks) + "\n" + source[anchor:]
    if "</style>" in updated:
        updated = updated.replace("</style>", STYLE + "\n</style>", 1)
    if '<a href="#limits"' in updated:
        updated = updated.replace('<a href="#limits"', NAV + '<a href="#limits"', 1)
    return render(pid, src, source, updated)


def render(pid: str, src: Path, original: str, updated: str) -> bool:
    out = EXPLAINERS / f"{pid}.html"
    backup = out.read_bytes() if out.exists() else b""
    src.write_text(updated, encoding="utf-8")
    result = subprocess.run(
        ["node", str(RENDER), str(src), "-o", str(out), "--no-check"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        src.write_text(original, encoding="utf-8")
        if backup:
            out.write_bytes(backup)
        return False
    return True


def main() -> int:
    changed = 0
    thin: list[str] = []
    for page in sorted(EXPLAINERS.glob("*.html")):
        if insert_for(page.stem):
            changed += 1
        elif not pick(page.stem):
            thin.append(page.stem)
    print(f"补图 {changed} 篇，无可用原图 {len(thin)} 篇")
    if thin[:12]:
        print("跳过样例：" + "、".join(thin[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
