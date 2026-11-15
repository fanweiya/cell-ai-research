"""清掉原文图注里的禁用词，并重新渲染这些页面。"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_paper_figures import EXPLAINERS, RENDER, ROOT, SANITIZE, source_path  # noqa: E402

CAPTION = re.compile(r"<figcaption>(.*?)</figcaption>", re.S)


def main() -> int:
    changed = 0
    for page in sorted(EXPLAINERS.glob("*.html")):
        pid = page.stem
        src = source_path(pid)
        if src is None:
            continue
        source = src.read_text(encoding="utf-8")
        if 'id="figures"' not in source:
            continue

        def fix(match: re.Match[str]) -> str:
            text = match.group(1)
            for word, replacement in SANITIZE.items():
                text = text.replace(word, replacement)
            return f"<figcaption>{text}</figcaption>"

        def fix_alt(match: re.Match[str]) -> str:
            text = match.group(1)
            for word, replacement in SANITIZE.items():
                text = text.replace(word, replacement)
            return f'alt="{text}"'

        updated = CAPTION.sub(fix, source)
        updated = re.sub(r'alt="([^"]*)"', fix_alt, updated)
        if updated == source:
            continue
        src.write_text(updated, encoding="utf-8")
        result = subprocess.run(
            ["node", str(RENDER), str(src), "-o", str(page), "--no-check"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode != 0:
            src.write_text(source, encoding="utf-8")
            continue
        changed += 1
    print(f"清洗 {changed} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
