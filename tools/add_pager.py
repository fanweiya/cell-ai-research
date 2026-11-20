"""给每篇图解页加「上一篇 / 下一篇」，并给没有原图的页面补一句说明。"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_paper_figures import EXPLAINERS, ROOT, RENDER, source_path  # noqa: E402

DB = ROOT / "papers.json"
H1 = re.compile(r"<h1>(.*?)</h1>", re.S)
TAGS = re.compile(r"<[^>]+>")

STYLE = (
    ".ve-pager{display:flex;justify-content:space-between;gap:var(--s-4);margin-top:var(--s-5);"
    "padding-top:var(--s-3);border-top:1px solid var(--border);font-size:var(--t-small);line-height:1.5}"
    ".ve-pager a{color:var(--accent);text-decoration:none;max-width:47%}"
    ".ve-pager a:hover{text-decoration:underline}"
    ".ve-pager .next{text-align:right;margin-left:auto}"
    ".ve-note{margin:var(--s-3) 0 0;font-size:var(--t-small);color:var(--muted)}"
)

NOTE = '<p class="ve-note">本文的论文插图无法自动获取，图注里的信息已写进上文的机制与数字。</p>'


def title_of(source: str) -> str:
    match = H1.search(source)
    if not match:
        return ""
    text = html.unescape(TAGS.sub("", match.group(1))).strip()
    return text[:26] + ("…" if len(text) > 26 else "")


def order() -> list[str]:
    database = json.loads(DB.read_text(encoding="utf-8"))["database"]
    rows = [(paper.get("published_date") or "", paper.get("arxiv_id", "")) for paper in database]
    dates = {pid: day for day, pid in rows}
    pids = [page.stem for page in sorted(EXPLAINERS.glob("*.html")) if page.name != "index.html"]
    return sorted(pids, key=lambda pid: (dates.get(pid, ""), pid), reverse=True)


def main() -> int:
    pids = order()
    changed = 0
    for index, pid in enumerate(pids):
        src = source_path(pid)
        if src is None:
            continue
        source = src.read_text(encoding="utf-8")
        if "ve-pager" in source:
            continue
        prev_pid = pids[index - 1] if index > 0 else ""
        next_pid = pids[index + 1] if index + 1 < len(pids) else ""
        links = []
        if prev_pid:
            links.append(f'<a class="prev" href="{prev_pid}.html">← 上一篇：{html.escape(title_of((EXPLAINERS / (prev_pid + ".html")).read_text(encoding="utf-8")))}</a>')
        if next_pid:
            links.append(f'<a class="next" href="{next_pid}.html">下一篇：{html.escape(title_of((EXPLAINERS / (next_pid + ".html")).read_text(encoding="utf-8")))} →</a>')
        block = '<nav class="ve-pager">' + "".join(links) + "</nav>"
        if 'id="figures"' not in source:
            block += NOTE
        anchor = source.rfind("</main>")
        if anchor == -1:
            anchor = source.rfind('<footer class="src"')
        if anchor == -1:
            anchor = source.rfind("</body>")
        if anchor == -1:
            continue
        updated = source[:anchor] + block + "\n" + source[anchor:]
        if "</style>" in updated:
            updated = updated.replace("</style>", STYLE + "\n</style>", 1)
        out = EXPLAINERS / f"{pid}.html"
        backup = out.read_bytes()
        src.write_text(updated, encoding="utf-8")
        result = subprocess.run(
            ["node", str(RENDER), str(src), "-o", str(out), "--no-check"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode != 0:
            src.write_text(source, encoding="utf-8")
            out.write_bytes(backup)
            continue
        changed += 1
    print(f"加翻页 {changed} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
