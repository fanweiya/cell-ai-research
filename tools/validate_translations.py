#!/usr/bin/env python3
"""入库前校验 data/translations.json（见 #402/#403）。

用法：
  python3 tools/validate_translations.py                 # 全量校验当前文件
  python3 tools/validate_translations.py --since HEAD    # 另列出相对某基线新增/改动的条目，
                                                         # 供提交信息如实写范围（提交信息须列出全部新增编号）

校验项：每条 title_zh/abstract_zh/key_points_zh 不得是供应商错误文本
（额度耗尽/订阅推销/服务异常等），title_zh/abstract_zh 须含足量中文。
任一不合格即退出码 1，并列出全部不合格编号；提交 data/translations.json 前必须跑过本脚本。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "data" / "translations.json"

try:
    sys.path.insert(0, str(ROOT))
    from generate_index import _is_usable_translation, _looks_like_provider_error
except Exception:  # 未装依赖时用本地同款判定兜底，不静默跳过校验
    import re

    _PROVIDER_ERROR_MARKERS = [
        "额度已用完", "额度耗尽", "免费额度", "开通订阅", "订阅畅享",
        "开通豆包", "豆包订阅", "豆包", "doubao",
        "余额不足", "请充值", "会员", "quota", "rate limit",
        "too many requests", "service unavailable", "insufficient",
        "subscription", "upgrade your plan",
    ]
    _SUSPICIOUS_URL_MARKERS = [
        "doubao", "member/subscription", "/subscribe", "/pricing", "/pay",
        "com_quota_cost", "custom_tracing", "subs_purchase", "trigger_scene",
        "quota_limit", "quota_cost",
    ]
    _URL_RE = re.compile(r"https?://\S+")

    def _looks_like_provider_error(text):
        if not text:
            return False
        lowered = text.lower()
        if any(m.lower() in lowered for m in _PROVIDER_ERROR_MARKERS):
            return True
        for url in _URL_RE.findall(text):
            if any(m in url.lower() for m in _SUSPICIOUS_URL_MARKERS):
                return True
        return False

    def _is_usable_translation(text, min_chinese=10):
        return (
            len(re.findall(r"[\u4e00-\u9fff]", text or "")) >= min_chinese
            and not _looks_like_provider_error(text)
        )


def _load_at_ref(ref: str) -> dict:
    out = subprocess.run(
        ["git", "show", f"{ref}:data/translations.json"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return {}
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def validate(data: dict) -> list[str]:
    """返回不合格条目描述列表（空表示全部通过）。"""
    problems = []
    for pid in sorted(data):
        entry = data.get(pid)
        if not isinstance(entry, dict):
            problems.append(f"{pid}：条目不是对象")
            continue
        title = entry.get("title_zh", "")
        abstract = entry.get("abstract_zh", "")
        key_points = entry.get("key_points_zh", "")
        if title and not _is_usable_translation(title, min_chinese=2):
            problems.append(f"{pid}：title_zh 不可用（无有效中文或疑似供应商错误文本）")
        if abstract and not _is_usable_translation(abstract):
            problems.append(f"{pid}：abstract_zh 不可用（无有效中文或疑似供应商错误文本）")
        if key_points and _looks_like_provider_error(key_points):
            problems.append(f"{pid}：key_points_zh 疑似供应商错误文本")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 data/translations.json 入库数据")
    parser.add_argument("--since", default=None,
                        help="git 基线（如 HEAD）：另列出相对基线新增/改动的条目编号")
    args = parser.parse_args()

    try:
        data = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"读缓存失败 {TRANSLATIONS}：{error}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("缓存顶层不是对象", file=sys.stderr)
        return 1

    problems = validate(data)
    if problems:
        print(f"校验不通过：{len(problems)} 项")
        for problem in problems:
            print(f"  ✗ {problem}")
        print("请先清空/重译上述条目再提交（不要把供应商错误文本入库）。")
        return 1
    print(f"校验通过：{len(data)} 条全部可用")

    if args.since:
        baseline = _load_at_ref(args.since)
        changed = sorted(
            pid for pid, entry in data.items()
            if baseline.get(pid) != entry
        )
        added = [pid for pid in changed if pid not in baseline]
        print(f"相对 {args.since} 改动 {len(changed)} 条，其中新增 {len(added)} 条：")
        for pid in changed:
            print(f"  {'+ ' if pid in added else '~ '}{pid}")
        if added:
            print("建议提交信息：data: 补 " + "、".join(added) + " 中译"
                  + (f"（另改动 {len(changed) - len(added)} 条）" if len(changed) > len(added) else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
