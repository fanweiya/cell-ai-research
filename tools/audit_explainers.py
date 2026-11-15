"""扫描已生成的图解页，报告结构、字数、图注与用词问题。

只读，不改任何文件。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLAINERS = ROOT / "explainers"
MANIFEST = ROOT / "data" / "explainers" / "manifest.json"
PAPERS = ROOT / "papers.json"

SECTIONS = ("problem", "mechanism", "design", "results", "limits", "remember")
BANNED = ("落地", "对齐", "钉死", "技术栈", "闭环", "赋能", "综上所述", "总而言之", "值得注意的是", "原理解读", "不是……而是")
CJK = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"entries": {}}
    entries = manifest.get("entries", {})
    papers = json.loads(PAPERS.read_text(encoding="utf-8"))["database"]
    passed = [p for p in papers if p.get("relevance") == "passed"]
    problems: dict[str, list[str]] = {}
    stats = {"total": 0, "agent": 0, "pack": 0, "cjk_min": 10**6, "cjk_max": 0}
    for paper in passed:
        pid = paper["arxiv_id"]
        path = EXPLAINERS / f"{pid}.html"
        if not path.exists():
            continue
        stats["total"] += 1
        entry = entries.get(pid) or {}
        stats["agent" if entry.get("generator") == "agent" else "pack"] += 1
        html = path.read_text(encoding="utf-8")
        issues: list[str] = []
        for name in SECTIONS:
            if f'id="{name}"' not in html:
                issues.append(f"缺版块 {name}")
        if html.count("<figure") < 3:
            issues.append(f"figure {html.count('<figure')} 个")
        if html.count("<figcaption") < 3:
            issues.append(f"figcaption {html.count('<figcaption')} 个")
        if "data-ve-kit" not in html:
            issues.append("未内联样式")
        for word in BANNED:
            if word in html:
                issues.append(f"出现「{word}」")
        body = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
        body = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
        words = len(CJK.findall(re.sub(r"<[^>]+>", " ", body)))
        stats["cjk_min"] = min(stats["cjk_min"], words)
        stats["cjk_max"] = max(stats["cjk_max"], words)
        if words < 900:
            issues.append(f"正文 {words} 字偏少")
        if words > 3200:
            issues.append(f"正文 {words} 字偏多")
        if issues:
            problems[pid] = issues
    print(f"已生成 {stats['total']} 篇：代理版 {stats['agent']}，早期版 {stats['pack']}")
    print(f"正文汉字区间 {stats['cjk_min']}–{stats['cjk_max']}")
    print(f"有问题 {len(problems)} 篇")
    for pid, issues in list(problems.items())[:40]:
        print(f"  {pid}: {'；'.join(issues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
