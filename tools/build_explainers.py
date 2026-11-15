#!/usr/bin/env python
"""为 cell-ai-research 的每篇论文生成 visual-explainer 图解页。

两段式：先把材料包压成结构化底稿 JSON，再依据底稿写页面源，最后交给
visual-explainer 的渲染器内联样式并校验。失败就地报错，不做替代方案。

用法：
  python tools/build_explainers.py --limit 1 --pid 2607.07651v1
  python tools/build_explainers.py --missing
  python tools/build_explainers.py --missing --force --limit 50
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import llm_client

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = Path(__file__).resolve().parent / "prompts"
RENDERER = ROOT / "tools" / "visual-explainer" / "plugins" / "visual-explainer" / "kit" / "render.mjs"
PAPERS = ROOT / "papers.json"
TRANSLATIONS = ROOT / "data" / "translations.json"
CODE_SUMMARIES = ROOT / "data" / "code_summaries.json"
RESULTS = ROOT / "results"
FIGURES = ROOT / "data" / "figures"
CONTEXT = ROOT / "data" / "paper_context"
EXPLAINERS = ROOT / "explainers"
SRC = ROOT / "data" / "explainers" / "src"
BRIEF = ROOT / "data" / "explainers" / "brief"
MANIFEST = ROOT / "data" / "explainers" / "manifest.json"

PACK_LIMIT = 320000
CODE_LIMIT = 90000
CODE_KEYWORDS = ("model", "net", "arch", "encoder", "decoder", "loss", "train", "diffusion", "module", "layer", "sampler")
STRUCTURES = {"linear", "encoder_decoder", "iterative", "branch_merge", "retrieval"}
FENCE = chr(96) * 3

BANNED = [
    (r"不是[^。！？\n]{0,40}而是", "出现“不是……而是……”句式"),
    (r"落地", "出现“落地”"),
    (r"对齐", "出现“对齐”"),
    (r"钉死", "出现“钉死”"),
    (r"技术栈", "出现“技术栈”"),
    (r"闭环", "出现“闭环”"),
    (r"赋能", "出现“赋能”"),
    (r"综上所述", "出现“综上所述”"),
    (r"总而言之", "出现“总而言之”"),
    (r"值得注意的是", "出现“值得注意的是”"),
]

CJK = re.compile(r"[\u4e00-\u9fff]")


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def squash(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return "；".join(squash(v) for v in value if squash(v))
    if isinstance(value, dict):
        return "；".join(f"{k}：{squash(v)}" for k, v in value.items() if squash(v))
    return str(value)


def clip(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…（后文截断）"


def result_index() -> dict[str, dict[str, Path]]:
    index: dict[str, dict[str, Path]] = {}
    for path in RESULTS.iterdir():
        if not path.name.endswith(".json"):
            continue
        pid = path.name.split("_")[0]
        suffix = path.name[len(pid):].lstrip("_").removesuffix(".json")
        index.setdefault(pid, {})[suffix] = path
    return index


def read_result(index: dict, pid: str, suffix: str) -> dict:
    path = index.get(pid, {}).get(suffix)
    if path is None:
        return {}
    try:
        data = load_json(path)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict) or data.get("error"):
        return {}
    return data


def figure_captions(pid: str) -> list[str]:
    path = FIGURES / f"{pid}_analysis.json"
    if not path.exists():
        return []
    try:
        data = load_json(path)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, dict):
        return []
    ordered = sorted(data.items(), key=lambda kv: int(kv[0]))
    captions = []
    for _, item in ordered:
        if isinstance(item, dict) and item.get("caption") and item.get("relevant", True):
            captions.append(clip(str(item["caption"]), 160))
    return captions


def code_excerpt(pid: str, index: dict) -> str:
    """从 gread 抓到的源码里挑关键文件，供模型看清模块与张量走向。"""
    record = read_result(index, pid, "gread") or read_result(index, pid.split("v")[0], "gread")
    text = squash(record.get("source_files"))
    if not text:
        return ""
    blocks = []
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        head, _, code = chunk.partition("\n")
        path = head.strip()
        code = code.strip()
        if code.startswith("```"):
            code = code[3:]
        code = code.rstrip().removesuffix("```").strip()
        if not path or not code:
            continue
        blocks.append((path, code))
    if not blocks:
        return ""
    def score(item: tuple[str, str]) -> tuple[int, int]:
        path = item[0].lower()
        hits = sum(1 for word in CODE_KEYWORDS if word in path)
        return (-hits, len(item[1]))
    blocks.sort(key=score)
    picked = []
    total = 0
    for path, code in blocks:
        piece = clip(code, 14000)
        if total + len(piece) > CODE_LIMIT:
            continue
        picked.append(f"## {path}\n```\n{piece}\n```")
        total += len(piece)
        if len(picked) >= 8:
            break
    return "\n\n".join(picked)


def build_pack(pid: str, paper: dict, trans: dict, code_sum: dict, index: dict) -> str:
    algorithm = read_result(index, pid, "algorithm_analysis")
    task = read_result(index, pid, "task_analysis")
    critic = read_result(index, pid, "critic_analysis")
    reproduction = read_result(index, pid, "reproduction")

    parts: list[str] = ["【题录】"]
    parts.append(f"英文标题：{paper.get('title', '')}")
    parts.append(f"中文标题：{trans.get('title_zh', '')}")
    parts.append(
        f"发布日期：{paper.get('published_date', '')} ｜ 任务类型：{squash(paper.get('task_type')) or '未标注'}"
        f" ｜ arXiv：{pid}"
    )
    repo = squash(code_sum.get("repository_kind")) or "未知"
    parts.append(f"代码仓库：{repo}")

    if trans.get("abstract_zh"):
        parts.append("\n【中文摘要】\n" + clip(trans["abstract_zh"], 3000))
    if trans.get("key_points_zh"):
        parts.append("\n【核心要点】\n" + clip(trans["key_points_zh"], 3000))

    if algorithm:
        parts.append("\n【算法拆解】")
        for label, key in [
            ("设计动机", "design_motivation"),
            ("数学原理", "math_principle"),
            ("损失形式", "loss_formula"),
            ("张量流", "tensor_flow"),
            ("训练流程", "training_pipeline"),
            ("对比基线", "baselines_compared"),
            ("关键结果", "key_results"),
        ]:
            value = squash(algorithm.get(key))
            if value:
                parts.append(f"{label}：{clip(value, 2000)}")

    if task:
        parts.append("\n【任务定位】")
        parts.append(f"任务族：{squash(task.get('task_family'))}")
        parts.append(f"输入：{clip(squash(task.get('input')), 400)}")
        parts.append(f"输出：{clip(squash(task.get('output')), 400)}")
        if task.get("notable"):
            parts.append(f"特别之处：{clip(squash(task.get('notable')), 500)}")

    if critic:
        parts.append("\n【评审意见】")
        for label, key in [
            ("声称贡献", "claimed_contribution"),
            ("实际贡献", "actual_contribution"),
            ("弱点", "weakness"),
            ("缺失实验", "missing_experiments"),
            ("过度声称", "overclaim"),
        ]:
            value = squash(critic.get(key))
            if value:
                parts.append(f"{label}：{clip(value, 1400)}")

    if reproduction:
        parts.append("\n【复现条件】")
        parts.append(
            f"级别：{squash(reproduction.get('level'))}（{squash(reproduction.get('level_description'))}）"
            f" ｜ 显存：{squash(reproduction.get('gpu_requirements'))}"
            f" ｜ 数据公开：{squash(reproduction.get('data_public'))}"
        )

    if code_sum.get("summary"):
        parts.append("\n【代码结构】")
        parts.append(f"仓库类型：{repo}")
        parts.append("摘要：" + clip(str(code_sum["summary"]), 900))

    code_text = code_excerpt(pid, index)
    if code_text:
        parts.append(
            "\n【核心代码】\n仓库里与本方法最相关的文件原文，写「机制」与「数据流」时以它为准："
        )
        parts.append(code_text)

    captions = figure_captions(pid)
    if captions:
        parts.append("\n【图表注】")
        parts.extend(f"图 {i + 1}：{text}" for i, text in enumerate(captions[:12]))

    body = ""
    context_path = CONTEXT / f"{pid}.txt"
    if not context_path.exists():
        context_path = CONTEXT / f"{pid.split('v')[0]}.txt"
    if context_path.exists():
        body = context_path.read_text(encoding="utf-8", errors="replace").strip()
    head = "\n".join(parts)
    budget = max(8000, PACK_LIMIT - len(head))
    formula_hits = len(re.findall(r"[=＝]\s*[A-Za-z\\]", body))
    if body:
        parts.append(
            f"\n【正文全文】（共 {len(body)} 字，公式线索 {formula_hits} 处，以下为原文；"
            "evidence 里的 quote 必须逐字取自这里或上面的分析块）\n" + clip(body, budget)
        )
    return "\n".join(parts)


def strip_fence(text: str) -> str:
    text = text.strip()
    if text.startswith(FENCE):
        text = re.sub(r"^" + FENCE + r"[a-zA-Z]*\s*\n", "", text)
        text = re.sub(r"\n" + FENCE + r"\s*$", "", text)
    return text.strip()


def cut_to_document(text: str) -> str:
    """去掉模型在 HTML 前后附加的说明语句，只保留文档本体。"""
    text = strip_fence(text)
    head = text.lower().find("<!doctype html")
    if head > 0:
        text = text[head:]
    tail = text.lower().rfind("</html>")
    if tail >= 0:
        text = text[: tail + len("</html>")]
    return text.strip()


def normalize_anchor(source: str, pid: str) -> str:
    """把页面里指向自身的索引锚点补齐版本号，避免链接跳到不存在的卡片。"""
    return re.sub(r"index\.html#paper-\d{4}\.\d{4,6}(?:v\d+)?", f"index.html#paper-{pid}", source)


def parse_json_object(text: str) -> dict:
    cleaned = strip_fence(text)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"响应里没有 JSON 对象：{cleaned[:300]}")
    data = json.loads(cleaned[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError(f"顶层不是对象：{type(data).__name__}")
    return data


def load_prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8")


def validate_brief(brief: dict, pack: str) -> list[str]:
    problems: list[str] = []
    required = [
        "title_zh", "one_line", "problem", "intuition", "structure", "stages",
        "key_facts", "design_choices", "limits", "takeaway", "terms", "evidence",
    ]
    for key in required:
        if key not in brief or brief[key] in (None, "", [], {}):
            problems.append(f"缺少字段 {key}")
    if problems:
        return problems
    one_line = squash(brief.get("one_line", ""))
    if len(one_line) > 32:
        problems.append(f"one_line 现在 {len(one_line)} 字，压到 28 字以内")
    if one_line.endswith(("。", "，", ".", ",")):
        problems.append("one_line 结尾不要加句号或逗号")
    if brief["structure"] not in STRUCTURES:
        problems.append(f"structure 必须是 {'/'.join(sorted(STRUCTURES))} 之一，现在是 {brief['structure']}")
    stages = brief["stages"]
    if not isinstance(stages, list) or not 3 <= len(stages) <= 5:
        problems.append("stages 必须是 3 到 5 项的数组")
    else:
        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                problems.append(f"stages[{i}] 必须是对象")
                continue
            for key in ("name", "action", "detail", "input", "output"):
                if not squash(stage.get(key)):
                    problems.append(f"stages[{i}] 缺少 {key}")
    evidence = brief.get("evidence")
    if not isinstance(evidence, list) or not 3 <= len(evidence) <= 8:
        problems.append("evidence 必须是 3 到 8 项的数组")
        evidence = evidence if isinstance(evidence, list) else []
    compact = re.sub(r"\s+", "", pack)
    for i, item in enumerate(evidence):
        if not isinstance(item, dict):
            problems.append(f"evidence[{i}] 必须是对象")
            continue
        quote = re.sub(r"\s+", "", str(item.get("quote", "")))
        if len(quote) < 8:
            problems.append(f"evidence[{i}].quote 太短，至少 8 个字")
        elif quote not in compact:
            problems.append(f"evidence[{i}].quote 未在材料包中找到：{quote[:40]}")
        if not squash(item.get("claim")):
            problems.append(f"evidence[{i}] 缺少 claim")
    facts = brief.get("key_facts")
    if isinstance(facts, list):
        for i, fact in enumerate(facts):
            if not isinstance(fact, dict) or not squash(fact.get("label")) or not squash(fact.get("value")):
                problems.append(f"key_facts[{i}] 需要 label 与 value")
    else:
        problems.append("key_facts 必须是数组")
    return problems


def make_brief(pid: str, pack: str) -> dict:
    messages = [
        {"role": "system", "content": load_prompt("brief.md")},
        {"role": "user", "content": pack},
    ]
    problems: list[str] = []
    for attempt in range(3):
        raw = llm_client.chat(messages, temperature=0.3, json_object=True, max_tokens=12000)
        brief = parse_json_object(raw)
        problems = validate_brief(brief, pack)
        if not problems:
            return brief
        print(f"    底稿第 {attempt + 1} 次未通过：{'; '.join(problems[:4])}", flush=True)
        messages = messages + [
            {"role": "assistant", "content": json.dumps(brief, ensure_ascii=False)},
            {"role": "user", "content": "上一版底稿有这些问题，逐条修正后重新输出完整 JSON。evidence 的 quote 必须从材料包里连续复制一段原文，不能改写、不能跨句拼接、不能把英文摘要翻译成中文再写：\n" + "\n".join(f"- {p}" for p in problems)},
        ]
    raise RuntimeError(f"{pid} 底稿未通过校验：{'; '.join(problems)}")


def cjk_count(source: str) -> int:
    text = re.sub(r"<style.*?</style>", " ", source, flags=re.S | re.I)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return len(CJK.findall(text))


def gate_page(source: str, pid: str, brief: dict) -> list[str]:
    problems: list[str] = []
    text = source.strip()
    if not text.lower().startswith("<!doctype html"):
        problems.append("文档必须以 <!doctype html> 开头")
    if not text.lower().endswith("</html>"):
        problems.append("文档必须以 </html> 结尾")
    if source.count("data-ve-kit") != 1:
        problems.append("必须恰好一个 data-ve-kit 链接")
    if 'data-register="paper"' not in source:
        problems.append('<html> 上必须写 data-register="paper"')
    if "<script" in source.lower():
        problems.append("页面源不能包含 <script>")
    stages = (brief or {}).get("stages") or []
    svgs = re.findall(r"<svg\b.*?</svg>", source, re.S)
    for i, svg in enumerate(svgs):
        head = svg[:500]
        if "aria-label" not in head and "<title" not in svg:
            problems.append(f"第 {i + 1} 个 svg 缺少 aria-label")
        if "viewBox" not in head and "viewbox" not in head:
            problems.append(f"第 {i + 1} 个 svg 缺少 viewBox")
    if svgs:
        box = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svgs[0])
        if box:
            vb_w, vb_h = float(box.group(1)), float(box.group(2))
            nodes = re.findall(
                r'<g class="ve-n[^"]*" transform="translate\(([-\d.]+) ([\d.]+)\)">(.*?)</g>',
                svgs[0],
                re.S,
            )
            if stages and len(nodes) != len(stages):
                problems.append(f"Fig. 1 的节点组 {len(nodes)} 个，阶段有 {len(stages)} 个，数量必须相等")
            for i, (nx, ny, inner) in enumerate(nodes, 1):
                rect = re.search(r'<rect[^>]*width="([\d.]+)"[^>]*height="([\d.]+)"', inner)
                w = float(rect.group(1)) if rect else 180.0
                h = float(rect.group(2)) if rect else 96.0
                x0, y0 = float(nx), float(ny)
                if x0 < 0 or y0 < 0 or x0 + w > vb_w - 8 or y0 + h > vb_h - 8:
                    need = y0 + h + 24 if y0 + h > vb_h - 8 else vb_h
                    problems.append(
                        f"Fig. 1 第 {i} 个节点超出画布：左上 ({x0:.0f},{y0:.0f})，尺寸 {w:.0f}x{h:.0f}，画布 {vb_w:.0f}x{vb_h:.0f}；"
                        f"把 viewBox 高度改成 {need:.0f}，或把这一行节点整体上移"
                    )
    figures = re.findall(r"<figure\b.*?</figure>", source, re.S)
    if len(figures) < 3:
        problems.append(f"至少三张图，现在 {len(figures)} 张")
    for i, figure in enumerate(figures):
        if "<figcaption" not in figure:
            problems.append(f"第 {i + 1} 张图缺少 figcaption")
    if stages and source.count('class="stage-badge"') != len(stages):
        problems.append(f"Fig. 1 的编号徽章数量必须等于阶段数 {len(stages)}，现在 {source.count('class=\"stage-badge\"')}")
    if stages and source.count('class="stage-num"') != len(stages):
        problems.append(f"正文阶段编号数量必须等于 {len(stages)}")
    for sid in ("problem", "mechanism", "results", "limits", "remember"):
        if f'id="{sid}"' not in source:
            problems.append(f'缺少版块 id="{sid}"')
    if 'id="design"' not in source and 'id="tradeoff"' not in source:
        problems.append('缺少版块 id="design"')
    if source.count("<h1") != 1:
        problems.append("必须有且只有一个 h1")
    if f"https://arxiv.org/abs/{pid}" not in source and f"https://arxiv.org/abs/{pid.split('v')[0]}" not in source:
        problems.append(f"缺少 arXiv 链接 https://arxiv.org/abs/{pid}")
    if f"index.html#paper-{pid}" not in source:
        problems.append(f"缺少返回索引链接 index.html#paper-{pid}")
    count = cjk_count(source)
    if count < 900:
        problems.append(f"正文汉字只有 {count}，至少 900")
    elif count > 3000:
        problems.append(f"正文汉字 {count}，最多 3000")
    for pattern, message in BANNED:
        if re.search(pattern, source):
            problems.append(message)
    return problems


def render(src_path: Path, out_path: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["node", str(RENDERER), str(src_path), "-o", str(out_path), "--no-check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    combined = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, combined


def make_page(pid: str, brief: dict, meta: str, pack: str = "") -> tuple[str, int]:
    user = (
        "## 底稿\n\n" + json.dumps(brief, ensure_ascii=False, indent=1) +
        "\n\n## 题录\n" + meta
    )
    if pack:
        user += "\n\n## 材料包（正文里的数字与机制以这里为准，底稿只给骨架）\n" + pack
    messages = [
        {"role": "system", "content": load_prompt("page.md")},
        {"role": "user", "content": user},
    ]
    source = normalize_anchor(cut_to_document(llm_client.chat(messages, temperature=0.45, max_tokens=32000)), pid)
    repairs = 0
    while True:
        problems = gate_page(source, pid, brief)
        if problems:
            print(f"    页面结构问题 {len(problems)} 项：{problems[0]}", flush=True)
        else:
            SRC.mkdir(parents=True, exist_ok=True)
            src_path = SRC / f"{pid}.src.html"
            src_path.write_text(source, encoding="utf-8")
            ok, output = render(src_path, EXPLAINERS / f"{pid}.html")
            if ok:
                for line in output.splitlines():
                    if line.strip().startswith("⚠"):
                        print("  " + line.strip(), flush=True)
                return source, repairs
            problems = [
                line.strip().lstrip("✗").strip()
                for line in output.splitlines()
                if line.strip().startswith("✗")
            ] or [output.strip()[-800:]]
            print(f"    渲染失败：{problems[0]}", flush=True)
        repairs += 1
        if repairs > 2:
            raise RuntimeError(f"{pid} 三次修复仍未通过：{'; '.join(problems[:5])}")
        messages = messages + [
            {"role": "assistant", "content": source},
            {
                "role": "user",
                "content": load_prompt("repair.md") + "\n\n## 校验问题\n" + "\n".join(f"- {p}" for p in problems),
            },
        ]
        source = normalize_anchor(cut_to_document(llm_client.chat(messages, temperature=0.35, max_tokens=32000)), pid)


def paper_meta(paper: dict, trans: dict) -> str:
    return "\n".join([
        f"中文标题：{trans.get('title_zh', '')}",
        f"英文标题：{paper.get('title', '')}",
        f"日期：{paper.get('published_date', '')}",
        f"任务类型：{squash(paper.get('task_type')) or '未标注'}",
        f"arXiv：{paper.get('arxiv_id', '')}",
        f"代码：{'有' if paper.get('has_code') else '无'}",
    ])


LOCK_PATH = ROOT / "data" / "explainers" / ".run.lock"


def acquire_process_lock() -> "object | None":
    """同一时刻只允许一个生成进程，定时任务与手动补跑不会撞车。"""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK_PATH.open("a+")
    try:
        if sys.platform == "win32":
            import msvcrt
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    return handle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--missing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--concurrency", type=int, default=1)
    args = parser.parse_args()

    process_lock = acquire_process_lock()
    if process_lock is None:
        print("另一个解读页生成进程正在运行，本次跳过", flush=True)
        return 0

    papers = load_json(PAPERS)["database"]
    translations = load_json(TRANSLATIONS)
    code_summaries = load_json(CODE_SUMMARIES)
    index = result_index()

    EXPLAINERS.mkdir(parents=True, exist_ok=True)
    BRIEF.mkdir(parents=True, exist_ok=True)

    if MANIFEST.exists():
        manifest = load_json(MANIFEST)
    else:
        manifest = {"entries": {}, "failures": {}}
    manifest.setdefault("entries", {})
    manifest.setdefault("failures", {})

    by_id = {p["arxiv_id"]: p for p in papers}
    if args.pid:
        chosen = [by_id[pid] for pid in args.pid if pid in by_id]
        missing = [pid for pid in args.pid if pid not in by_id]
        if missing:
            raise SystemExit(f"papers.json 里没有：{', '.join(missing)}")
    else:
        chosen = [p for p in papers if args.all or p.get("relevance") == "passed"]
        chosen.sort(key=lambda p: p.get("published_date", ""), reverse=True)

    tasks = []
    for paper in chosen:
        pid = paper["arxiv_id"]
        exists = (EXPLAINERS / f"{pid}.html").exists()
        if args.missing and exists and not args.force:
            continue
        if exists and not args.force and not args.pid:
            continue
        tasks.append(paper)
    if args.limit:
        tasks = tasks[:args.limit]

    print(f"待生成 {len(tasks)} 篇，模型 {llm_client.model_name()}", flush=True)
    failures = 0

    if args.dry_run:
        paper = tasks[0]
        pid = paper["arxiv_id"]
        pack = build_pack(pid, paper, translations.get(pid, {}), code_summaries.get(pid, {}), index)
        print(f"{pid} 材料包 {len(pack)} 字")
        print(pack[:1500])
        process_lock.close()
        return 0

    started_all = time.time()
    lock = threading.Lock()
    counter = itertools.count(1)

    def run_one(paper: dict) -> bool:
        nonlocal failures
        pid = paper["arxiv_id"]
        number = next(counter)
        trans = translations.get(pid, {})
        code_sum = code_summaries.get(pid, {})
        stamp = time.strftime("%H:%M:%S")
        print(f"[{number}/{len(tasks)} {stamp}] {pid} {trans.get('title_zh', '')[:40]}", flush=True)
        began = time.time()
        try:
            brief_path = BRIEF / f"{pid}.json"
            pack = build_pack(pid, paper, trans, code_sum, index)
            if brief_path.exists() and not args.force:
                stored = load_json(brief_path)
                brief = stored["brief"]
                print(f"    {pid} 复用已有底稿", flush=True)
            else:
                brief = make_brief(pid, pack)
                brief_path.write_text(
                    json.dumps(
                        {"pid": pid, "generated_at": now(), "model": llm_client.model_name(), "brief": brief},
                        ensure_ascii=False,
                        indent=1,
                    ),
                    encoding="utf-8",
                )
            source, repairs = make_page(pid, brief, paper_meta(paper, trans), pack)
            out_path = EXPLAINERS / f"{pid}.html"
            words = cjk_count(source)
            with lock:
                manifest["entries"][pid] = {
                    "title_zh": trans.get("title_zh", ""),
                    "one_line": brief.get("one_line", ""),
                    "structure": brief.get("structure", ""),
                    "generated_at": now(),
                    "model": llm_client.model_name(),
                    "cjk": words,
                    "repairs": repairs,
                    "bytes": out_path.stat().st_size,
                }
                manifest["failures"].pop(pid, None)
                manifest["updated_at"] = now()
                MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"    {pid} 完成 {time.time() - began:.0f}s  {words} 字  修复 {repairs} 次", flush=True)
            return True
        except Exception as error:
            with lock:
                failures += 1
                manifest["failures"][pid] = {"at": now(), "error": str(error)[:800]}
                manifest["updated_at"] = now()
                MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"    {pid} 失败：{type(error).__name__}: {error}", file=sys.stderr, flush=True)
            return False

    workers = max(1, args.concurrency)
    if workers == 1:
        for paper in tasks:
            run_one(paper)
    else:
        print(f"并发 {workers} 路", flush=True)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(run_one, tasks))
    print(
        f"总计 {len(tasks)} 篇，失败 {failures} 篇，用时 {(time.time() - started_all) / 60:.1f} 分钟",
        flush=True,
    )
    process_lock.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
