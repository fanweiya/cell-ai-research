#!/usr/bin/env python3
"""
generate_index.py — Cell AI Research 论文索引生成器 v2

从 papers.json 读取论文数据，并行调用 LLM 翻译+摘要，提取 PDF 关键图片，
生成可浏览的亮色主题 HTML 索引页。

用法:
  python3 generate_index.py                    # 完整运行（翻译+摘要+图片）
  python3 generate_index.py --no-translate     # 跳过翻译（用缓存）
  python3 generate_index.py --no-images        # 跳过 PDF 图片提取
  python3 generate_index.py --force-translate  # 强制重新翻译全部

输出: index.html（项目根目录）
缓存: data/translations.json, data/figures/
"""

import json
import os
import sys
import time
import subprocess
import argparse
import html as html_mod
import base64
import io
import re
import difflib
from evidence_export import export_evidence
from text_render import render_prose
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# === Config ===
WORKSPACE = Path(__file__).parent
PAPERS_FILE = WORKSPACE / "papers.json"
TRANSLATIONS_CACHE = WORKSPACE / "data" / "translations.json"
ARXIV_LINK_CACHE = WORKSPACE / "data" / "arxiv_link_status.json"
PAPER_CONTEXT_DIR = WORKSPACE / "data" / "paper_context"
FIGURES_DIR = WORKSPACE / "data" / "figures"
ORIGINAL_FIGURES_DIR = FIGURES_DIR / "originals"
OUTPUT_FILE = WORKSPACE / "index.html"
LLM_BASE = os.environ.get(
    "CELL_AI_LLM_BASE",
    "http://10.0.0.240:8080/v1",
).rstrip("/")
LLM_MODEL = os.environ.get("CELL_AI_LLM_MODEL", "stable")
LLM_FALLBACK_MODEL = os.environ.get("CELL_AI_LLM_FALLBACK_MODEL", "fast")
LLM_API_KEY = os.environ.get("CELL_AI_LLM_API_KEY", "cell-ai")
# The generated Cloudflare page cannot call a private RFC1918 address over
# HTTP. Keep the browser endpoint separately configurable from backend jobs.
BROWSER_LLM_BASE = os.environ.get(
    "CELL_AI_BROWSER_LLM_BASE",
    "https://ai.fanweiya.qzz.io/v1",
).rstrip("/")
BROWSER_LLM_MODEL = os.environ.get("CELL_AI_BROWSER_LLM_MODEL", "fast")
IMAGE_LLM_BASE = os.environ.get(
    "CELL_AI_IMAGE_LLM_BASE",
    "http://10.0.0.240:8080/v1",
).rstrip("/")
IMAGE_LLM_MODEL = os.environ.get(
    "CELL_AI_IMAGE_LLM_MODEL",
    "vision",
)
MAX_WORKERS = 8          # 并行 LLM 调用数
CODE_SUMMARY_WORKERS = max(1, int(os.environ.get("CELL_AI_CODE_SUMMARY_WORKERS", "2")))
CODE_SUMMARY_ATTEMPTS = 3
CODE_SUMMARY_MAX_TOKENS = 6400
MAX_FIGURES_PER_PAPER = 3
MAX_FIGURE_WIDTH = 600   # px, 仅用于多模态分析缩略图；网页展示原图
ARXIV_LINK_CACHE_TTL = 7 * 24 * 60 * 60
CODE_SUMMARY_CACHE = WORKSPACE / "data" / "code_summaries.json"
CODE_REPORT_VERSION = 3
TRANSLATION_VERSION = 2
KEY_POINTS_VERSION = 2
OLLAMA_BASE = "http://10.0.0.240:11434"
OLLAMA_TRANSLATE_MODEL = "kaelri/hy-mt2:1.8b"
USE_OLLAMA_TRANSLATE = True  # 用 Ollama 翻译模型代替 Agent-A1 做翻译


# ============================================================
# LLM Helpers
# ============================================================
def _llm_call(prompt, temperature=0.3, max_tokens=8192, json_mode=False, model_order=None):
    """Call the 8080 stable route, then fast, with prompt-leak detection."""
    import requests
    # prompt 前缀特征，用于检测 LLM 回显
    _LEAK_MARKERS = ["将以下英文学术文本翻译为中文", "你是一位细胞生物学 AI 研究员", "只输出翻译结果，不要解释"]
    models = list(dict.fromkeys(model_order or [LLM_MODEL, LLM_FALLBACK_MODEL]))
    for model in models:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        try:
            resp = requests.post(
                f"{LLM_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                json=payload,
                timeout=90,
            )
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"].strip()
            # 检测 prompt 泄漏：如果返回内容包含 prompt 指令文本，视为失败
            if any(marker in result for marker in _LEAK_MARKERS):
                print(f"  [WARN] Prompt leak detected on {model}, trying fallback...")
                continue
            return result
        except Exception:
            continue
    return None


def _translate_prompt(text):
    return f"""将以下英文学术文本翻译为中文。要求：
1. 保持学术术语准确性
2. 专有名词保留英文并括号标注，如"细胞分割（Cell Segmentation）"
3. 只输出翻译结果，不要解释

{text}"""


def _ollama_translate(text):
    """调用 Ollama 翻译模型（专用翻译模型，更快更省资源）"""
    import requests
    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": OLLAMA_TRANSLATE_MODEL,
                "prompt": f"将以下英文学术文本翻译为中文，只输出翻译结果：\n\n{text}",
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 4096},
            },
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json().get("response", "").strip()
        return result if result else None
    except Exception as e:
        return None


def _has_meaningful_chinese(text):
    """避免把英文原文或翻译失败提示写入中文缓存。"""
    return len(re.findall(r"[\u4e00-\u9fff]", text or "")) >= 10


def _translate_text(text):
    """优先使用专用翻译模型，失败或返回非中文时回退到 Agents-A1。"""
    if USE_OLLAMA_TRANSLATE:
        translated = _ollama_translate(text)
        if _has_meaningful_chinese(translated):
            return translated
    translated = _llm_call(_translate_prompt(text), temperature=0.1, max_tokens=8192)
    return translated if _has_meaningful_chinese(translated) else None


def _translation_domain_hint(task_types):
    tasks = {str(task).lower() for task in (task_types or [])}
    hints = [
        "通用约定：model/dataset/benchmark 名称保持英文；inference 按语境译为“推理”，representation 按语境译为“表征”。",
        "模型蒸馏语境：teacher model/student model 译为“教师模型/学生模型”，不得译为教师或学生。",
    ]
    if tasks & {"segmentation", "detection", "tracking", "counting", "organoid_analysis"}:
        hints.append(
            "生物图像分析：instance segmentation=实例分割，semantic segmentation=语义分割，"
            "cell tracking=细胞追踪，lineage=细胞谱系，label-free=无标记。"
        )
    if tasks & {"spatial", "spatial_biology", "spatial_transcriptomics", "multimodal"}:
        hints.append(
            "空间组学：spatial transcriptomics=空间转录组学，spot=空间位点，"
            "gene expression=基因表达，cross-modal=跨模态。"
        )
    if tasks & {"pathology", "classification", "diagnosis", "virtual_staining"}:
        hints.append(
            "计算病理：whole-slide image/WSI=全切片图像，patch=图块，"
            "virtual staining=虚拟染色，stain 按语境译为染色。"
        )
    if tasks & {"foundation_model", "foundation_models", "representation", "embedding"}:
        hints.append(
            "基础模型：foundation model=基础模型，embedding 按语境译为嵌入或表征，"
            "fine-tuning=微调，pretraining=预训练。"
        )
    return "\n".join(hints)


def _academic_translation_prompt(text, title, task_types, text_type, retry_note=""):
    title_note = (
        "标题中的模型或系统名称保持英文，但其余语义必须译成中文；"
        "若标题只有一个英文名称，也要补充简洁、忠实的中文释义。"
        if text_type == "标题" else
        "参考标题只用于理解语境，绝不能把标题当作摘要译文。"
    )
    return f"""你是细胞生物学、显微成像、计算病理与生物医学人工智能领域的资深学术译者。

请先在内部理解论文所属子领域、术语含义和句间逻辑，再将原文忠实重写为自然、严谨的简体中文。这里的“重写”只允许调整中文语序和拆分长句，不得总结、删减、扩写或改变原意。

翻译对象：论文{text_type}
<context_title>{title}</context_title>
任务类型：{", ".join(task_types or []) or "未标注"}

领域约定：
{_translation_domain_hint(task_types)}

硬性要求：
1. 事实、因果关系、比较关系、否定、数据、单位和实验结论必须与原文完全一致。
2. 模型名、数据集名、基因名、蛋白名、指标缩写和代码名保持英文，不音译、不自行改名。
3. 专业术语使用领域通行译法；仅对容易歧义的重要术语在首次出现时保留英文括注，避免满篇括号。
4. 中文应像研究人员原生撰写的论文，拆分英语长句，避免欧化语序和逐词直译。
5. 不添加译者注、解释、标题、前言或 Markdown；只输出最终译文。
6. {title_note}

{retry_note}

<source_text>
{text}
</source_text>

只翻译 <source_text> 内的内容；<context_title> 仅提供语境。只输出最终译文。"""


def _numeric_tokens(text):
    """把英文数量单位与中文万/亿归一化，比较数值语义而非表面格式。"""
    from decimal import Decimal, InvalidOperation

    text = (text or "").replace(r"\%", "%").replace("％", "%")
    # 章节/步骤编号允许自然译为“第一阶段”“图二”，不属于实验数值。
    text = re.sub(
        r"\b(?:stage|step|phase|figure|fig\.?|table|section|equation|eq\.?)\s*\d+\b",
        "",
        text,
        flags=re.IGNORECASE,
    )
    # LaTeX 下标/上标中的数字（如 G_{2}, x^{3}）是公式符号，不是实验数值。
    text = re.sub(r"(?:_|\^)\{?\d+\}?", "", text)
    multipliers = {
        "thousand": Decimal("1000"),
        "million": Decimal("1000000"),
        "billion": Decimal("1000000000"),
        "k": Decimal("1000"),
        "m": Decimal("1000000"),
        "b": Decimal("1000000000"),
        "t": Decimal("1000000000000"),
        "万": Decimal("10000"),
        "亿": Decimal("100000000"),
    }
    pattern = re.compile(
        r"(?<![A-Za-z0-9.])"
        r"(\d+(?:\.\d+)?)"
        r"\s*([%kmbt]|thousand|million|billion|万|亿)?"
        r"(?![A-Za-z0-9])",
        re.IGNORECASE,
    )
    values = set()
    for match in pattern.finditer(text):
        raw_number, raw_unit = match.groups()
        try:
            number = Decimal(raw_number)
        except InvalidOperation:
            continue
        unit = (raw_unit or "").lower()
        if unit in multipliers:
            number *= multipliers[unit]
        normalized = format(number.normalize(), "f")
        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".")
        prefix = "percent:" if unit == "%" else "number:"
        values.add(prefix + normalized)
    return values


def _translation_quality(source, translated, text_type="摘要"):
    min_chinese = 2 if text_type == "标题" else 10
    if len(re.findall(r"[\u4e00-\u9fff]", translated or "")) < min_chinese:
        return False, "没有生成有效中文"
    source_numbers = _numeric_tokens(source)
    translated_numbers = _numeric_tokens(translated)
    missing = sorted(source_numbers - translated_numbers)
    if missing:
        return False, f"遗漏或改动数字：{', '.join(missing[:8])}"
    if len(translated.strip()) < max(4, len(source.strip()) * 0.18):
        return False, "译文疑似被过度删减"
    return True, ""


def _translate_academic(text, title, task_types, text_type):
    """按宝玉 normal 模式的精简思路，用 A1 做领域分析后的忠实重写。"""
    prompt = _academic_translation_prompt(text, title, task_types, text_type)
    translated = _llm_call(
        prompt,
        temperature=0.1,
        max_tokens=512 if text_type == "标题" else 8192,
    )
    valid, reason = _translation_quality(text, translated, text_type)
    if valid:
        return translated
    retry_prompt = _academic_translation_prompt(
        text,
        title,
        task_types,
        text_type,
        retry_note=f"上一次结果未通过质量检查：{reason}。请逐项核对原文后重新输出。",
    )
    translated = _llm_call(
        retry_prompt,
        temperature=0.05,
        max_tokens=512 if text_type == "标题" else 8192,
    )
    valid, _ = _translation_quality(text, translated, text_type)
    return translated if valid else None


def _summarize_prompt(title, abstract):
    return f"""你是一位细胞生物学 AI 研究员。请根据以下论文标题和摘要，用中文提炼 3-5 个核心要点（Key Takeaways）。

要求：
- 每个要点一句话，不超过 40 字
- 突出方法创新、技术亮点、实验结论
- 用编号列表格式，如：
1. xxx
2. xxx
3. xxx

论文标题：{title}

摘要：{abstract}"""


def _paper_context(pid, abstract):
    """提取论文方法/实验/结果/结论；HTML 不可用时从 PDF 读取。"""
    import requests
    from bs4 import BeautifulSoup

    clean_id = re.sub(r"v\d+$", "", pid)
    cache_file = PAPER_CONTEXT_DIR / f"{clean_id}.txt"
    if cache_file.exists():
        cached = cache_file.read_text(encoding="utf-8", errors="ignore").strip()
        if len(cached) > len(abstract) + 200:
            return cached

    context = ""
    html_url = f"https://arxiv.org/html/{clean_id}"
    try:
        response = requests.get(
            html_url,
            timeout=25,
            headers={"User-Agent": "cell-ai-research-context/1.0"},
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for node in soup(["script", "style", "nav", "footer"]):
                node.decompose()
            selected = []
            keywords = (
                "method", "approach", "model", "architecture", "experiment",
                "evaluation", "result", "discussion", "conclusion",
                "limitation", "ablation", "dataset",
            )
            for section in soup.select("section"):
                heading = section.find(["h1", "h2", "h3", "h4"])
                heading_text = heading.get_text(" ", strip=True).lower() if heading else ""
                if any(keyword in heading_text for keyword in keywords):
                    text = section.get_text(" ", strip=True)
                    if len(text) > 100:
                        selected.append(text)
            if selected:
                context = "\n\n".join(selected)
            else:
                context = soup.get_text(" ", strip=True)
    except requests.RequestException:
        pass

    if len(context) < len(abstract) + 200:
        try:
            import fitz
            response = requests.get(
                f"https://arxiv.org/pdf/{clean_id}",
                timeout=45,
                headers={"User-Agent": "cell-ai-research-context/1.0"},
            )
            if response.status_code == 200 and response.content.startswith(b"%PDF"):
                document = fitz.open(stream=response.content, filetype="pdf")
                context = "\n\n".join(page.get_text("text") for page in document)
                document.close()
        except Exception:
            pass

    context = re.sub(r"\s+", " ", context).strip()
    if len(context) > 60000:
        context = context[:60000]
    if len(context) < len(abstract):
        context = abstract

    PAPER_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(context, encoding="utf-8")
    return context


def _key_points_prompt(title, abstract, paper_context, retry_note=""):
    return f"""你是严谨的细胞生物学与生物医学图像分析研究员。请根据提供的论文材料生成真正有决策价值的中文核心要点。

必须严格输出 4 条编号要点，分别使用以下标签：
1. 问题与价值：
2. 方法创新：
3. 实验结论：
4. 局限与应用：

要求：
- 每条 1-2 句、40-100 个中文字符，总长度不超过 600 个中文字符。
- 不要复述研究背景或按摘要顺序改写；每条必须提供不同信息。
- “方法创新”要说明相对常规方案新增了什么机制或设计。
- “实验结论”优先写数据集、基线、指标和具体数值；材料未提供时明确写“材料未给出具体数值”，禁止编造。
- “局限与应用”要区分论文明确结论和基于材料的谨慎推断。
- 只输出 4 条要点，不要标题、前言、Markdown 表格或额外说明。

论文标题：{title}

论文摘要：
{abstract}

论文方法、实验、结果和结论材料：
{paper_context}

{retry_note}"""


def _key_points_quality(text, abstract_zh):
    """检查条数、长度和摘要复制程度。"""
    if not text:
        return False, "输出为空"
    numbered = len(re.findall(r"(?m)^\s*[1-4][.、]\s*", text))
    compact = re.sub(r"\s+", "", text)
    abstract_compact = re.sub(r"\s+", "", abstract_zh or "")
    similarity = (
        difflib.SequenceMatcher(None, compact, abstract_compact).ratio()
        if abstract_compact else 0
    )
    if numbered != 4:
        return False, f"必须恰好 4 条，当前 {numbered} 条"
    if len(compact) < 120 or len(compact) > 900:
        return False, f"总长度不合格，当前 {len(compact)} 字符"
    if similarity >= 0.72:
        return False, f"与摘要过于相似，相似度 {similarity:.2f}"
    return True, ""


def _generate_key_points(pid, title, abstract, abstract_zh):
    """核心要点始终由 Agents-A1 直接生成，不经过翻译模型。"""
    context = _paper_context(pid, abstract)
    prompt = _key_points_prompt(title, abstract, context)
    result = _llm_call(prompt, temperature=0.15, max_tokens=1800)
    valid, reason = _key_points_quality(result, abstract_zh)
    if valid:
        return result
    retry_prompt = _key_points_prompt(
        title,
        abstract,
        context,
        retry_note=f"上一次输出未通过质量检查：{reason}。请重新提炼，尤其避免复制摘要。",
    )
    retried = _llm_call(retry_prompt, temperature=0.1, max_tokens=1800)
    valid, _ = _key_points_quality(retried, abstract_zh)
    return retried if valid else ""


def _process_paper_llm(pid, title, abstract, task_types, existing, force):
    """并行处理单篇论文的翻译+摘要（全部用 Ollama）"""
    result = {"pid": pid}
    has_abstract = bool(abstract and len(abstract.strip()) > 10)

    # 标题和摘要由 A1 按 Cell AI 子领域做忠实学术重写。
    if (
        force
        or existing.get("translation_version") != TRANSLATION_VERSION
        or not _has_meaningful_chinese(existing.get("title_zh", ""))
    ):
        t = _translate_academic(title, title, task_types, "标题")
        result["title_zh"] = t or ""
    else:
        result["title_zh"] = existing["title_zh"]

    # 翻译摘要（用 Ollama 专用翻译模型）
    if not has_abstract:
        result["abstract_zh"] = ""
    elif (
        force
        or existing.get("translation_version") != TRANSLATION_VERSION
        or not _has_meaningful_chinese(existing.get("abstract_zh", ""))
        or existing.get("abstract_zh", "").strip() == abstract.strip()
    ):
        t = _translate_academic(abstract, title, task_types, "摘要")
        result["abstract_zh"] = t or ""
    else:
        result["abstract_zh"] = existing["abstract_zh"]

    # 核心要点：直接使用 Agents-A1 + 论文正文，不经过翻译模型
    if not has_abstract:
        result["key_points_zh"] = ""
    elif (
        force
        or not existing.get("key_points_zh")
        or existing.get("key_points_version") != KEY_POINTS_VERSION
    ):
        result["key_points_zh"] = _generate_key_points(
            pid,
            title,
            abstract,
            result.get("abstract_zh", existing.get("abstract_zh", "")),
        )
    else:
        result["key_points_zh"] = existing["key_points_zh"]

    result["key_points_version"] = KEY_POINTS_VERSION
    result["translation_version"] = TRANSLATION_VERSION
    result["translated_at"] = datetime.now().isoformat()
    return result


def translate_and_summarize(papers, translations, force=False):
    """并行翻译+摘要生成"""
    tasks = []
    for i, p in enumerate(papers):
        pid = p.get("arxiv_id", f"unknown_{i}")
        title = p.get("title", "")
        abstract = p.get("abstract", "") or p.get("abstract_summary", "") or ""
        task_types = p.get("task_type", [])
        if not isinstance(task_types, list):
            task_types = [task_types]
        existing = translations.get(pid, {})

        has_title_zh = bool(
            existing.get("title_zh")
            and existing.get("title_zh") != title
            and existing.get("translation_version") == TRANSLATION_VERSION
        )
        has_abstract_zh = (
            (bool(existing.get("abstract_zh")) if abstract else True)
            and (existing.get("abstract_zh") != abstract if abstract else True)
            and existing.get("translation_version") == TRANSLATION_VERSION
        )
        has_kp_zh = (
            existing.get("key_points_zh") is not None
            and (bool(existing.get("key_points_zh")) if abstract else True)
            and existing.get("key_points_version") == KEY_POINTS_VERSION
        )

        if not force and has_title_zh and has_abstract_zh and has_kp_zh:
            continue
        tasks.append((pid, title, abstract, task_types, existing, force))

    if not tasks:
        print("  All translations + summaries cached, skipping.")
        return translations

    print(f"  Processing {len(tasks)} papers with {MAX_WORKERS} workers...")
    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(
                _process_paper_llm,
                pid,
                title,
                abstract,
                task_types,
                existing,
                force,
            ): pid
            for pid, title, abstract, task_types, existing, force in tasks
        }
        for future in as_completed(futures):
            pid = futures[future]
            try:
                r = future.result()
                translations[r["pid"]] = {
                    "title_zh": r["title_zh"],
                    "abstract_zh": r["abstract_zh"],
                    "key_points_zh": r["key_points_zh"],
                    "key_points_version": r["key_points_version"],
                    "translation_version": r["translation_version"],
                    "translated_at": r["translated_at"],
                }
                done += 1
                print(f"  [{done}/{len(tasks)}] ✓ {pid}")
            except Exception as e:
                print(f"  [WARN] Failed {pid}: {e}")

            # 增量保存
            if done % 5 == 0:
                _save_translations(translations)

    _save_translations(translations)
    print(f"  Done: {done} papers processed.")
    return translations


# ============================================================
# Cache I/O
# ============================================================
def _load_translations():
    if TRANSLATIONS_CACHE.exists():
        with open(TRANSLATIONS_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_translations(translations):
    TRANSLATIONS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRANSLATIONS_CACHE, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)


def _load_code_summaries():
    if CODE_SUMMARY_CACHE.exists():
        try:
            with open(CODE_SUMMARY_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def _save_code_summaries(summaries):
    CODE_SUMMARY_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(CODE_SUMMARY_CACHE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)


def _load_gread_result(code_analysis):
    """Load the bounded gread evidence file referenced by a paper record."""
    result_file = str((code_analysis or {}).get("result_file") or "").strip()
    if not result_file:
        return {}
    path = (WORKSPACE / result_file).resolve()
    try:
        path.relative_to(WORKSPACE.resolve())
    except ValueError:
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) and data.get("source") == "gread" else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _bounded_source_excerpt(source, max_chars=60_000, per_file=7_500):
    """Keep evidence from several files instead of truncating one giant dump."""
    blocks = re.split(r"(?=^##\s+[^\n]+\n```)", source or "", flags=re.M)
    selected = []
    used = 0
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if len(block) <= per_file:
            excerpt = block
        else:
            head_size = int(per_file * 0.7)
            omitted = len(block) - per_file
            excerpt = (
                block[:head_size]
                + f"\n\n[gread analysis excerpt omitted {omitted} characters; "
                  "this is not a truncation of the repository file]\n\n"
                + block[-(per_file - head_size):]
            )
        remaining = max_chars - used
        if remaining <= 0:
            break
        selected.append(excerpt[:remaining])
        used += min(len(excerpt), remaining)
    return "\n\n".join(selected)


def _code_summary_prompt(repo_url, code_analysis, gread_data=None):
    """Build an evidence-first prompt for a structured static code report."""
    code_analysis = code_analysis if isinstance(code_analysis, dict) else {}
    gread_data = gread_data if isinstance(gread_data, dict) else {}
    coverage = gread_data.get("coverage") or code_analysis.get("source_coverage") or {}
    overview = gread_data.get("overview") or ""
    tree = gread_data.get("tree") or ""
    key_files = gread_data.get("key_files") or []
    sources = _bounded_source_excerpt(gread_data.get("source_files", ""))
    searches = "\n\n".join(str(item)[:3500] for item in gread_data.get("search_results", [])[:5])
    evidence = {
        "repository": repo_url,
        "analysis_depth": gread_data.get("analysis_depth") or code_analysis.get("analysis_depth"),
        "coverage": coverage,
        "overview": str(overview)[:10_000],
        "tree": str(tree)[:20_000],
        "key_files": key_files[:40],
        "source_files": sources,
        "grep_results": searches,
    }
    evidence_json = json.dumps(evidence, ensure_ascii=False, indent=2)
    return f"""你是细胞影像、计算病理和机器学习工程方向的资深静态代码审阅者。以下证据全部由 gread HTTP API 远程取得，仓库没有被 clone，代码也没有被执行。

<gread_evidence>
{evidence_json}
</gread_evidence>

请基于源码而不是 README 宣传语生成中文代码审阅报告。要求：
1. 先根据 coverage 和文件扩展名判断 implementation、partial、placeholder、third_party 或 unknown；GitHub 链接存在不代表已公开实现。
2. 给出真实入口、调用链、核心模块、关键算法和输入输出。证据不足就写“无法确认”，不得套用 input→encoder→decoder 模板。
3. 交叉检查 README 命令、包名、导入、配置 target、类名、依赖清单和实际文件；issues 只收录有具体文件/符号证据的问题。
4. “confirmed”仅用于源码直接证明的问题；未执行才能确认的行为必须写“疑似”并降低 confidence。
5. 不得声称代码已运行、测试通过或论文结果可复现。不要编造行号、性能、显存和硬件。
6. 报告应让研究者能判断是否值得使用，篇幅比仓库简介详细，但避免复述完整目录树。
7. source_files 是按分析预算提供的源码摘录。摘录省略或未展示某个 key_file 不是仓库缺陷，绝不能写成“仓库源码被截断”或“文件未提供”。
8. repository_kind 描述发布完整度，不描述代码质量；代码存在可修复 bug 时仍可判为 implementation。

只输出严格 JSON，不要 Markdown：
{{
  "summary": "2-4句用途及实现完整度",
  "repository_kind": "implementation|partial|placeholder|third_party|unknown",
  "architecture": "基于源码的架构和数据流",
  "call_chain": "入口 → 数据加载 → 核心算法 → 输出",
  "core_modules": [{{"name":"模块","role":"职责","evidence":"path:Class/function"}}],
  "dependencies": ["直接依赖、外部工具和数据要求"],
  "reproduction_readiness": "ready|needs_fixes|blocked|placeholder|unknown",
  "reproduction_notes": "最短复现路径、环境和阻碍",
  "issues": [{{"severity":"blocker|high|medium|low","finding":"问题或疑点","evidence":["path:symbol/config"],"impact":"影响","confidence":0.0}}],
  "static_limitations": ["静态分析不能确认的事项"],
  "confidence": 0.0
}}"""


def _parse_code_report(raw_result, coverage=None):
    if not raw_result:
        return None
    text = raw_result.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        report = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(report, dict) or not _has_meaningful_chinese(report.get("summary", "")):
        return None

    allowed_kinds = {"implementation", "partial", "placeholder", "third_party", "unknown"}
    allowed_readiness = {"ready", "needs_fixes", "blocked", "placeholder", "unknown"}
    if report.get("repository_kind") not in allowed_kinds:
        report["repository_kind"] = "unknown"
    if report.get("reproduction_readiness") not in allowed_readiness:
        report["reproduction_readiness"] = "unknown"

    valid_issues = []
    for issue in report.get("issues", []):
        if not isinstance(issue, dict) or not issue.get("finding") or not issue.get("evidence"):
            continue
        if issue.get("severity") not in {"blocker", "high", "medium", "low"}:
            issue["severity"] = "medium"
        try:
            issue["confidence"] = max(0.0, min(1.0, float(issue.get("confidence", 0.5))))
        except (TypeError, ValueError):
            issue["confidence"] = 0.5
        if issue["confidence"] >= 0.65:
            valid_issues.append(issue)
    report["issues"] = valid_issues[:10]
    report["core_modules"] = [item for item in report.get("core_modules", []) if isinstance(item, dict)][:12]
    report["dependencies"] = [str(item) for item in report.get("dependencies", [])][:20]
    limitations = [str(item) for item in report.get("static_limitations", [])]
    if not any("未执行" in item or "静态" in item for item in limitations):
        limitations.append("仅进行了 gread 静态分析，未执行代码，不能确认运行时兼容性或论文指标。")
    report["static_limitations"] = limitations[:8]
    try:
        report["confidence"] = max(0.0, min(1.0, float(report.get("confidence", 0.5))))
    except (TypeError, ValueError):
        report["confidence"] = 0.5

    coverage = coverage if isinstance(coverage, dict) else {}
    if coverage.get("has_implementation") is False:
        report["repository_kind"] = "placeholder"
        report["reproduction_readiness"] = "placeholder"
    report["version"] = CODE_REPORT_VERSION
    return report


def summarize_code_repositories(papers, summaries, force=False):
    """Turn gread source evidence into structured Chinese static reports."""
    tasks = []
    for i, p in enumerate(papers):
        pid = p.get("arxiv_id", f"unknown_{i}")
        ca = p.get("code_analysis") or {}
        if not isinstance(ca, dict):
            ca = {}
        gh = p.get("status", {}).get("github", {}) or {}
        has_code = bool(gh.get("has_code", p.get("has_code", False)))
        url = gh.get("url", "") or ca.get("repository_url", "")
        if not url:
            continue
        gread_data = _load_gread_result(ca)
        if not gread_data:
            continue
        existing = summaries.get(pid, {})
        if not force and existing.get("summary") and existing.get("version", 0) >= CODE_REPORT_VERSION:
            continue
        tasks.append((pid, url, ca, gread_data))

    if not tasks:
        print("  Code summaries cached, skipping.")
        return summaries

    worker_count = min(CODE_SUMMARY_WORKERS, len(tasks))
    print(f"  Summarizing {len(tasks)} repositories with {worker_count} workers...")
    done = 0
    pending = tasks
    for attempt in range(1, CODE_SUMMARY_ATTEMPTS + 1):
        failed = []
        if attempt > 1:
            print(f"  Retrying {len(pending)} incomplete summaries (attempt {attempt}/{CODE_SUMMARY_ATTEMPTS})...")
        with ThreadPoolExecutor(max_workers=min(CODE_SUMMARY_WORKERS, len(pending))) as pool:
            futures = {
                pool.submit(_summarize_one, pid, url, ca, gread_data): task
                for task in pending
                for pid, url, ca, gread_data in [task]
            }
            for fut in as_completed(futures):
                task = futures[fut]
                pid = task[0]
                try:
                    report = fut.result()
                except Exception as e:
                    print(f"  [WARN] Failed {pid}: {type(e).__name__}: {e}")
                    failed.append(task)
                    continue
                if not report:
                    print(f"  [WARN] No valid structured report for {pid}")
                    failed.append(task)
                    continue
                report["generated_at"] = datetime.now().isoformat()
                summaries[pid] = report
                done += 1
                print(f"  [{done}/{len(tasks)}] ✓ {pid}")
                if done % 5 == 0:
                    _save_code_summaries(summaries)
        pending = failed
        if not pending:
            break
        if attempt < CODE_SUMMARY_ATTEMPTS:
            time.sleep(attempt * 2)

    _save_code_summaries(summaries)
    print(f"  Done: {done} repository summaries; incomplete: {len(pending)}.")
    return summaries


def _summarize_one(pid, url, code_analysis, gread_data=None):
    del pid  # reserved for future paper-aware checks
    prompt = _code_summary_prompt(url, code_analysis, gread_data=gread_data)
    # The fast route handles large structured-source prompts more reliably than
    # the stable route; keep stable as a fallback for transient failures.
    result = _llm_call(
        prompt,
        temperature=0.1,
        max_tokens=CODE_SUMMARY_MAX_TOKENS,
        json_mode=True,
        model_order=[LLM_FALLBACK_MODEL, LLM_MODEL],
    )
    coverage = (gread_data or {}).get("coverage") or (code_analysis or {}).get("source_coverage")
    report = _parse_code_report(result, coverage=coverage)
    if not report:
        return None
    known_files = set((gread_data or {}).get("key_files") or (code_analysis or {}).get("key_files") or [])
    if known_files:
        report["issues"] = [
            issue for issue in report.get("issues", [])
            if any(
                any(str(evidence).startswith(path + ":") or str(evidence) == path for path in known_files)
                for evidence in issue.get("evidence", [])
            )
        ]
    return report


def refresh_arxiv_link_status(papers, offline=False):
    """定期实测 arXiv HTML；明确 404 时让页面回退到 PDF。"""
    cache = {}
    if ARXIV_LINK_CACHE.exists():
        try:
            cache = json.loads(ARXIV_LINK_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cache = {}

    if offline:
        return cache

    import requests

    now = time.time()
    pending = []
    for p in papers:
        pid = p.get("arxiv_id", "")
        if not pid or pid.startswith("biorxiv:"):
            continue
        clean_id = re.sub(r"v\d+$", "", pid)
        cached = cache.get(clean_id, {})
        if now - cached.get("checked_at", 0) >= ARXIV_LINK_CACHE_TTL:
            pending.append(clean_id)

    def probe(clean_id):
        url = f"https://arxiv.org/html/{clean_id}"
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=15,
                headers={"User-Agent": "cell-ai-research-link-check/1.0"},
            )
            if response.status_code == 200:
                return clean_id, True, response.status_code
            if response.status_code == 404:
                return clean_id, False, response.status_code
            return clean_id, None, response.status_code
        except requests.RequestException:
            return clean_id, None, None

    if pending:
        print(f"🔗 Checking {len(pending)} arXiv HTML links...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = [pool.submit(probe, clean_id) for clean_id in pending]
            for future in as_completed(futures):
                clean_id, available, status_code = future.result()
                # Only cache conclusive results; transient failures retain old data.
                if available is not None:
                    cache[clean_id] = {
                        "html_available": available,
                        "status_code": status_code,
                        "checked_at": now,
                    }

        ARXIV_LINK_CACHE.parent.mkdir(parents=True, exist_ok=True)
        ARXIV_LINK_CACHE.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return {
        clean_id: item.get("html_available")
        for clean_id, item in cache.items()
    }


# ============================================================
# HTML Figure Extraction (replaces old PDF extraction)
# ============================================================
def _safe_figure_extension(rel_path, image_format):
    """返回适合静态站点的图片扩展名。"""
    suffix = Path(rel_path.split("?", 1)[0]).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    format_suffix = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "GIF": ".gif",
        "WEBP": ".webp",
    }
    return format_suffix.get((image_format or "").upper(), ".img")


def _extract_figures_for_paper(pid, papers_map, force=False):
    """从 arXiv HTML 页面提取论文原图，并保留分析用缩略图。"""
    clean_id = pid.replace("v1", "").replace("v2", "").replace("v3", "")
    if pid.startswith("biorxiv:"):
        clean_id = pid.replace("biorxiv:", "").split("/")[-1]

    # 检查缓存
    cache_file = FIGURES_DIR / f"{clean_id}.json"
    if cache_file.exists() and not force:
        try:
            with open(cache_file, "r") as f:
                cached = json.load(f)
            if all(
                fig.get("src") and (WORKSPACE / fig["src"]).is_file()
                for fig in cached
            ):
                return cached
        except:
            pass

    # 从 arXiv HTML 页面获取图片
    html_url = f"https://arxiv.org/html/{pid}"
    try:
        result = subprocess.run(
            ["curl", "-sL", html_url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []
        html = result.stdout

        # 检查是否为 arXiv "No HTML" 错误页面
        # 这些论文源文件不是纯 LaTeX/HTML 或转换失败，无法获取全文
        if "No HTML for" in html or "HTML is not available" in html:
            print(f"  [WARN] No HTML available for {pid}")
            return []
    except:
        return []

    import re
    from PIL import Image

    # 从 HTML 中提取论文图片
    # arXiv HTML 页面中的图片 src 格式多样：
    #   "2607.08297v1/x1.png"  或  "x1.png"  或  "2607.04353v1/Figures/Hier3.png"
    # src 已经是相对路径，直接拼到 https://arxiv.org/html/{arxiv_id}/ 后面即可
    # 图片文件名模式：x{N}.png, fig{N}.png, 或子目录中的自定义名
    fig_urls = []
    for match in re.finditer(r'src=[\"\']([^\"\']*?\.(?:png|jpg|jpeg|gif|svg))[^\"\']*[\"\']', html):
        rel_path = match.group(1)
        # 跳过静态资源/logo/资助方图标
        if any(k in rel_path for k in ('static/', 'logo', 'funder', 'smileybones')):
            continue
        # 构建下载 URL
        if rel_path.startswith('http'):
            full_url = rel_path
        elif rel_path.startswith('/'):
            full_url = f"https://arxiv.org{rel_path}"
        else:
            # src 已经是 {arxiv_id}/path 格式，拼到 /html/ 后面
            full_url = f"https://arxiv.org/html/{rel_path}"
        fig_urls.append((len(fig_urls), full_url, rel_path))

    # 按出现顺序（已在 HTML 中顺序），但只保留前 N 张最大的
    if not fig_urls:
        return []

    fig_urls.sort(key=lambda x: x[0])
    if not fig_urls:
        return []

    figures = []
    for idx, (seq_num, url, rel_path) in enumerate(fig_urls[:MAX_FIGURES_PER_PAPER]):
        try:
            result = subprocess.run(
                ["curl", "-sL", url],
                capture_output=True, timeout=30
            )
            if result.returncode != 0 or len(result.stdout) < 2000:
                continue

            img_bytes = result.stdout
            img = Image.open(io.BytesIO(img_bytes))
            image_format = img.format
            img.load()
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            width, height = img.size
            if width < 150 or height < 100:
                continue

            extension = _safe_figure_extension(rel_path, image_format)
            original_name = f"{clean_id}_{idx + 1}{extension}"
            original_path = ORIGINAL_FIGURES_DIR / original_name
            ORIGINAL_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
            original_path.write_bytes(img_bytes)

            preview = img.copy()
            if preview.width > MAX_FIGURE_WIDTH:
                ratio = MAX_FIGURE_WIDTH / preview.width
                new_size = (MAX_FIGURE_WIDTH, int(preview.height * ratio))
                preview = preview.resize(new_size, Image.LANCZOS)

            buf = io.BytesIO()
            preview.save(buf, format="JPEG", quality=75, optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            figures.append({
                "data": b64,
                "src": original_path.relative_to(WORKSPACE).as_posix(),
                "source_url": url,
                "page": idx + 1,
                "width": width,
                "height": height,
            })
        except:
            continue

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(figures, f)

    return figures


def extract_all_figures(papers, force=False):
    """提取所有论文的 HTML 页面图片，并用多模态 LLM 过滤"""
    papers_map = {p.get("arxiv_id", ""): p for p in papers}
    total = len(papers)
    extracted = 0
    analyzed = 0

    for i, p in enumerate(papers):
        pid = p.get("arxiv_id", f"unknown_{i}")
        clean_id = pid.replace("v1", "").replace("v2", "").replace("v3", "")
        if pid.startswith("biorxiv:"):
            clean_id = pid.replace("biorxiv:", "").split("/")[-1]

        cache_file = FIGURES_DIR / f"{clean_id}.json"
        analysis_file = FIGURES_DIR / f"{clean_id}_analysis.json"

        # 强制刷新时必须穿透旧的 base64 缓存，重新下载原始文件。
        if force or not cache_file.exists():
            print(f"  [{i+1}/{total}] Extracting figures: {clean_id}...")
            figs = _extract_figures_for_paper(pid, papers_map, force=force)
            if figs:
                extracted += 1
        else:
            figs = []

        # Analyze if not cached
        if not analysis_file.exists() and cache_file.exists():
            if not figs:
                try:
                    with open(cache_file) as f:
                        figs = json.load(f)
                except:
                    continue
            if figs:
                title = p.get("title", "")
                print(f"  [{i+1}/{total}] Analyzing figures: {clean_id} ({len(figs)} images)...")
                _filter_figures_by_relevance(figs, title, pid)
                # Save filtered figures back
                filtered = _load_figures_filtered(pid)
                with open(cache_file, "w") as f:
                    json.dump(filtered, f)
                analyzed += 1

    print(f"  Extracted: {extracted}, Analyzed: {analyzed} papers")


def _analyze_image(b64_data, paper_title):
    """用 Qwen3.6 多模态模型分析图片，返回 (is_relevant, caption)。"""
    import requests
    prompt_text = (
        "你是一位细胞生物学AI研究员。请分析这张来自论文的图片。\n"
        f"论文标题：{paper_title}\n\n"
        "判断这张图是否是论文的核心图示（架构图、实验结果、方法流程图、对比图、数据可视化等），"
        "还是无关紧要的图片（logo、装饰图、小图标、纯文本截图等）。\n\n"
        "请返回 JSON 格式（不要包含其他内容）：\n"
        '{"relevant": true/false, "score": 0-10, "caption": "简短中文描述"}'
    )
    try:
        resp = requests.post(
            f"{IMAGE_LLM_BASE}/chat/completions",
            json={
                "model": IMAGE_LLM_MODEL,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"}}
                    ]
                }],
                "max_tokens": 4096,
                "temperature": 0.1,
            },
            timeout=120,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        # Parse JSON from response
        import re
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result.get("relevant", False), result.get("score", 0), result.get("caption", "")
        # Fallback: if LLM says relevant in text
        return "relevant" in text.lower() or "true" in text.lower(), 5, text[:50]
    except Exception as e:
        # If analysis fails, keep the image (safe default)
        return True, 5, ""


def _filter_figures_by_relevance(figures, paper_title, pid):
    """用多模态 LLM 过滤不相关图片，只保留核心图示"""
    if not figures:
        return figures

    clean_id = pid.replace("v1", "").replace("v2", "").replace("v3", "")
    if pid.startswith("biorxiv:"):
        clean_id = pid.replace("biorxiv:", "").split("/")[-1]

    # Check analysis cache
    analysis_file = FIGURES_DIR / f"{clean_id}_analysis.json"
    if analysis_file.exists():
        try:
            with open(analysis_file, "r") as f:
                analysis = json.load(f)
            # Apply cached analysis
            filtered = []
            for i, fig in enumerate(figures):
                key = str(i)
                if key in analysis and analysis[key].get("relevant", True):
                    fig["caption"] = analysis[key].get("caption", "")
                    fig["score"] = analysis[key].get("score", 5)
                    filtered.append(fig)
            return filtered if filtered else figures[:1]  # 至少保留1张
        except:
            pass

    # Analyze each image
    analysis = {}
    filtered = []
    for i, fig in enumerate(figures):
        is_rel, score, caption = _analyze_image(fig["data"], paper_title)
        analysis[str(i)] = {"relevant": is_rel, "score": score, "caption": caption}
        if is_rel:
            fig["caption"] = caption
            fig["score"] = score
            filtered.append(fig)

    # Cache analysis
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # Always keep at least 1 image
    if not filtered and figures:
        fig = figures[0]
        fig["caption"] = ""
        fig["score"] = 5
        filtered = [fig]

    return filtered


def _load_figures_filtered(pid):
    """加载缓存图片并应用分析过滤"""
    clean_id = pid.replace("v1", "").replace("v2", "").replace("v3", "")
    if pid.startswith("biorxiv:"):
        clean_id = pid.replace("biorxiv:", "").split("/")[-1]
    cache_file = FIGURES_DIR / f"{clean_id}.json"
    analysis_file = FIGURES_DIR / f"{clean_id}_analysis.json"

    figures = []
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                figures = json.load(f)
        except:
            return []

    if analysis_file.exists():
        try:
            with open(analysis_file) as f:
                analysis = json.load(f)
            filtered = []
            for i, fig in enumerate(figures):
                key = str(i)
                if key in analysis and analysis[key].get("relevant", True):
                    fig["caption"] = analysis[key].get("caption", "")
                    fig["score"] = analysis[key].get("score", 5)
                    filtered.append(fig)
            return filtered if filtered else []
        except:
            pass
    return figures


def _load_figures(pid):
    """加载已缓存的图片"""
    clean_id = pid.replace("v1", "").replace("v2", "").replace("v3", "")
    if pid.startswith("biorxiv:"):
        clean_id = pid.replace("biorxiv:", "").split("/")[-1]
    cache_file = FIGURES_DIR / f"{clean_id}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except:
            pass
    return []


# ============================================================
# HTML Generation
# ============================================================
def _esc(text):
    return html_mod.escape(str(text)) if text else ""


def _render_code_report(entry):
    """Render a structured report cache entry using escaped, compact HTML."""
    if (
        not isinstance(entry, dict)
        or not entry.get("summary")
        or entry.get("version", 0) < CODE_REPORT_VERSION
    ):
        return ""
    confidence = entry.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0.65:
        return ""
    parts = []
    summary = render_prose(entry.get("summary", ""), code=True)
    parts.append('<p class="repo-scope-note">仅依据源码静态分析；未运行代码，未验证论文指标。</p>')
    parts.append(f'<div class="ri"><span class="rl">📝 静态审阅:</span> {summary}</div>')

    kind_labels = {
        "implementation": "实现型仓库",
        "partial": "部分实现",
        "placeholder": "占位仓库/未公开实现",
        "third_party": "第三方仓库",
        "unknown": "无法确认",
    }
    readiness_labels = {
        "ready": "静态证据较完整（仍未运行验证）",
        "needs_fixes": "需要修复后尝试",
        "blocked": "存在复现阻碍",
        "placeholder": "代码未公开",
        "unknown": "无法确认",
    }
    kind = kind_labels.get(entry.get("repository_kind"), "无法确认")
    readiness = readiness_labels.get(entry.get("reproduction_readiness"), "无法确认")
    confidence_text = f" · 模型自评置信度 {float(confidence):.0%}" if isinstance(confidence, (int, float)) else ""
    parts.append(f'<div class="ri"><span class="rl">📦 仓库判定:</span> {_esc(kind)} · {_esc(readiness)}{confidence_text}</div>')

    if entry.get("architecture"):
        parts.append(f'<div class="ri"><span class="rl">🏗 架构:</span> {render_prose(entry["architecture"], code=True)}</div>')
    if entry.get("call_chain"):
        parts.append(f'<div class="ri"><span class="rl">🔗 调用链:</span> <code class="cc">{_esc(entry["call_chain"])}</code></div>')

    modules = []
    for module in entry.get("core_modules", [])[:8]:
        if not isinstance(module, dict):
            continue
        label = f"{module.get('name', '模块')}：{module.get('role', '')}"
        evidence = module.get("evidence")
        if evidence:
            label += f"（{evidence}）"
        modules.append('<li>' + render_prose(label, code=True) + '</li>')
    if modules:
        parts.append(f'<div class="ri"><span class="rl">🧩 核心模块:</span><ul class="repo-list">{"".join(modules)}</ul></div>')

    if entry.get("reproduction_notes"):
        parts.append(f'<div class="ri"><span class="rl">🔄 运行准备（静态建议）:</span> {render_prose(entry["reproduction_notes"], code=True)}</div>')
    dependencies = [_esc(item) for item in entry.get("dependencies", [])[:10] if item]
    if dependencies:
        parts.append(f'<div class="ri"><span class="rl">🧰 依赖与数据:</span> {"；".join(dependencies)}</div>')

    issue_rows = []
    severity_labels = {"blocker": "阻断", "high": "高", "medium": "中", "low": "低"}
    for issue in entry.get("issues", [])[:6]:
        if not isinstance(issue, dict):
            continue
        severity = severity_labels.get(issue.get("severity"), "中")
        evidence = "、".join(str(item) for item in issue.get("evidence", [])[:3])
        row = f"[{severity}] {issue.get('finding', '')}"
        if evidence:
            row += f"（证据：{evidence}）"
        issue_rows.append('<li>' + render_prose(row, code=True) + '</li>')
    if issue_rows:
        parts.append(f'<div class="ri"><span class="rl">⚠️ 源码发现:</span><ul class="repo-list">{"".join(issue_rows)}</ul></div>')

    limitations = ['<li>' + render_prose(item, code=True) + '</li>' for item in entry.get("static_limitations", [])[:4] if item]
    if limitations:
        parts.append(f'<div class="ri"><span class="rl">ℹ️ 分析边界:</span><ul class="repo-list">{"".join(limitations)}</ul></div>')
    return "".join(parts)


VERIFIED_REPOSITORY_PROVENANCE = {
    "paper_code_statement",
    "paper_identity_match",
    "manual_verified",
}


def _is_verified_repository(github):
    return bool(
        isinstance(github, dict)
        and github.get("url")
        and github.get("provenance") in VERIFIED_REPOSITORY_PROVENANCE
    )


def _is_code_ready(paper):
    github = paper.get("status", {}).get("github", {})
    return _is_verified_repository(github) and bool(github.get("has_code"))


def _score_text(value):
    return "—" if value in (None, "") else str(value)


def _render_gread_fallback(code_analysis):
    """Render bounded facts when no trustworthy natural-language report exists."""
    coverage = (code_analysis or {}).get("source_coverage") or {}
    if not isinstance(coverage, dict):
        coverage = {}
    if coverage.get("has_implementation") is False:
        return (
            '<div class="ri"><span class="rl">📦 远程静态证据:</span> '
            "当前 HEAD 未检测到实现源码；仓库可能是占位页或仅含文档。</div>"
        )
    code_files = coverage.get("code_file_count_in_tree")
    selected = coverage.get("selected_code_file_count")
    languages = coverage.get("languages_by_extension") or {}
    language_text = "、".join(sorted(str(item) for item in languages))
    facts = []
    if isinstance(code_files, int):
        facts.append(f"目录中识别到 {code_files} 个代码文件")
    if isinstance(selected, int):
        facts.append(f"本轮选读 {selected} 个")
    if language_text:
        facts.append(f"语言：{language_text}")
    if not facts:
        return (
            '<div class="ri"><span class="rl">📦 远程静态证据:</span> '
            "证据覆盖不足，已隐藏未经源码支撑的架构与调用链推断。</div>"
        )
    return (
        '<div class="ri"><span class="rl">📦 远程静态证据:</span> '
        + _esc("；".join(facts))
        + "。代码未执行，尚不能据此确认可复现性。</div>"
    )


def _get_grade(priority):
    try:
        priority = float(priority or 0)
    except (TypeError, ValueError):
        priority = 0
    if priority >= 15: return "A"
    elif priority >= 10: return "B"
    elif priority >= 7: return "C"
    return "D"


def _normalize_status(value):
    if isinstance(value, dict):
        value = value.get("status", "")
    value = str(value or "").lower().strip()
    if value in {"done", "completed", "passed"}: return "done"
    if value in {"doing", "in_progress", "running", "processing"}: return "running"
    if value in {"error", "failed"}: return "failed"
    if value == "blocked": return "blocked"
    if value in {"skipped", "not_applicable"}: return "skipped"
    return "pending"


def _status_icons(status, has_code=False, summary_ready=False):
    def render(label, state):
        css, text = {
            "done": ("sd", "完成"), "running": ("sp", "处理中"),
            "failed": ("se", "失败"), "blocked": ("se", "受阻"),
            "skipped": ("sn", "已跳过"), "pending": ("sn", "未完成"),
        }[state]
        return f'<span class="{css}">{label}：{text}</span>'

    icons = [render("摘要整理", "done" if summary_ready else "pending"),
             render("全文获取", _normalize_status(status.get("html")))]
    if has_code:
        icons.append(render("代码静态分析", _normalize_status(status.get("code_analysis"))))
    return " ".join(icons)


def generate_html(papers, translations, generated_at, arxiv_html_status=None, code_summaries=None, evidence_manifest=None):
    evidence_manifest = evidence_manifest or {}
    assets = WORKSPACE / "web"
    copilot_css = (assets / "copilot.css").read_text(encoding="utf-8")
    copilot_html = (assets / "copilot.html").read_text(encoding="utf-8")
    copilot_js = (assets / "copilot.js").read_text(encoding="utf-8")
    paper_list_js = (assets / "paper-list.js").read_text(encoding="utf-8")
    paper_list_css = (assets / "paper-list.css").read_text(encoding="utf-8")
    theme_js = (assets / "theme.js").read_text(encoding="utf-8")
    theme_css = (assets / "theme.css").read_text(encoding="utf-8")
    arxiv_html_status = arxiv_html_status or {}
    code_summaries = code_summaries or {}
    papers_sorted = sorted(papers, key=lambda p: p.get("published_date", ""), reverse=True)

    total = len(papers)
    has_code = 0
    has_html = 0
    has_figs = 0

    for p in papers:
        if _is_code_ready(p):
            has_code += 1
        if _normalize_status(p.get("status", {}).get("html")) == "done":
            has_html += 1

    # 按年月统计（用于侧栏年月筛选下拉）
    month_counts = {}
    for p in papers:
        ym = (p.get("published_date") or "")[:7]
        if len(ym) == 7:
            month_counts[ym] = month_counts.get(ym, 0) + 1
    month_options = '<option value="all">全部年月</option>' + "".join(
        f'<option value="{ym}">{ym[:4]}年{ym[5:]}月 ({cnt})</option>'
        for ym, cnt in sorted(month_counts.items(), reverse=True)
    )


    # Build cards
    cards = []
    js_papers = []
    for p in papers_sorted:
        pid = p.get("arxiv_id", "unknown")

        title = _esc(p.get("title", "Untitled"))
        trans = translations.get(pid, {})
        title_zh = _esc(trans.get("title_zh", title))
        abstract = p.get("abstract") or p.get("abstract_summary") or ""
        abstract_zh = render_prose(trans.get("abstract_zh", abstract))
        abstract_en = render_prose(abstract)
        key_points = trans.get("key_points_zh", "")
        key_points_html = _esc(key_points).replace("\n", "<br>") if key_points else ""

        date = p.get("published_date", "")
        authors = p.get("authors", "")
        if isinstance(authors, list):
            authors = ", ".join(authors[:5]) + ("..." if len(authors) > 5 else "")
        authors = _esc(authors[:200]) if authors else ""

        r_score = p.get("research_score")
        e_score = p.get("engineering_score")
        priority = p.get("priority")
        bonus = p.get("bonus", [])
        task_types = p.get("task_type", [])

        gh = p.get("status", {}).get("github", {})
        if not isinstance(gh, dict):
            gh = {}
        repository_verified = _is_verified_repository(gh)
        has_code_flag = _is_code_ready(p)
        github_url = gh.get("url", "") if repository_verified else ""
        stars = gh.get("stars", 0)
        framework = gh.get("framework", "")

        # code_analysis info
        ca = p.get("code_analysis") or p.get("code_analysis_result", {})
        if not isinstance(ca, dict):
            ca = {}
        is_gread_analysis = ca.get("source") == "gread" or gh.get("analysis_source") == "gread"
        ca_arch = _esc(ca.get("architecture", ""))
        ca_chain = _esc(ca.get("call_chain", ""))
        ca_classes = ca.get("core_classes", [])
        ca_quality = ca.get("code_quality", {})
        if not isinstance(ca_quality, dict):
            ca_quality = {}
        ca_repro = _esc(ca.get("reproduction_readiness", ""))

        status_html = _status_icons(p.get("status", {}), has_code_flag, bool(trans.get("abstract_zh") or key_points))
        teaser_text = " ".join((key_points or trans.get("abstract_zh") or abstract).split())
        teaser_text = re.sub(r"^1[.、]\s*问题与价值[：:]\s*", "", teaser_text)
        teaser = _esc((teaser_text.split("。", 1)[0] + "。" if "。" in teaser_text else teaser_text)[:180])

        # Link
        clean_id = pid.replace("v1", "").replace("v2", "").replace("v3", "").replace("biorxiv:", "")
        if pid.startswith("biorxiv:"):
            link = f"https://doi.org/{clean_id}"
            link_kind = "论文页面"
        elif (
            arxiv_html_status.get(clean_id) is False
            or (
                clean_id not in arxiv_html_status
                and _normalize_status(p.get("status", {}).get("html")) == "failed"
            )
        ):
            link = f"https://arxiv.org/pdf/{clean_id}"
            link_kind = "PDF"
        else:
            link = f"https://arxiv.org/html/{clean_id}"
            link_kind = "HTML"

        # Tags
        tags = ""
        for t in (task_types if isinstance(task_types, list) else [task_types]):
            if t:
                tags += f'<span class="tag">{_esc(t)}</span>'
        for b in (bonus if isinstance(bonus, list) else []):
            tags += f'<span class="tag tb">+{_esc(b)}</span>'

        code_html = ""
        if has_code_flag and github_url:
            code_html = f'<a href="{_esc(github_url)}" target="_blank" class="cb" onclick="event.stopPropagation()">💻 GitHub</a>'
        elif has_code_flag:
            code_html = '<span class="cb">💻 Code</span>'
        # HTML link (replaces old PDF link)
        html_link = ""

        # Figures (filtered by multimodal LLM) — collapsible
        figures = _load_figures_filtered(pid)
        figs_html = ""
        if figures:
            has_figs += 1
            imgs = ""
            for fig in figures:
                caption = fig.get("caption", "")
                caption_html = f'<div class="fig-cap">{_esc(caption)}</div>' if caption else ""
                image_src = fig.get("src")
                if image_src:
                    image_src = _esc(image_src)
                else:
                    image_src = f'data:image/jpeg;base64,{fig["data"]}'
                imgs += f'<div class="fig-item"><img src="{image_src}" class="fig-img" loading="lazy" decoding="async" onclick="openModal(this)" />{caption_html}</div>'
            figs_html = f'''<details class="sec fig-sec">
  <summary class="sec-h">📊 论文关键图示 ({len(figures)} 张)</summary>
  <div class="fig-grid">{imgs}</div>
</details>'''

        # Key points section — always visible
        kp_html = ""
        if key_points_html:
            kp_html = f'<div class="kp"><div class="kp-label">💡 核心要点</div><div class="kp-content">{key_points_html}</div></div>'

        # Repo / Code Analysis section — collapsible
        repo_html = ""
        code_summary = ""
        code_report_html = ""
        cs_entry = {}
        if github_url and (ca_arch or ca_chain or ca_classes or github_url):
            parts = []
            if github_url:
                parts.append(f'<div class="ri"><span class="rl">🔗 GitHub:</span> <a href="{_esc(github_url)}" target="_blank" class="rlink" onclick="event.stopPropagation()">{_esc(github_url)}</a></div>')
            if is_gread_analysis:
                parts.append('<div class="ri"><span class="rl">🌐 分析来源:</span> gread 远程仓库分析</div>')
            # 结构化中文静态报告优先；旧缓存仍兼容 summary 字段。
            cs_entry = code_summaries.get(pid, {})
            if isinstance(cs_entry, dict):
                code_summary = cs_entry.get("summary", "")
                code_report_html = _render_code_report(cs_entry)
            if code_report_html:
                parts.append(code_report_html)
            elif is_gread_analysis:
                parts.append(_render_gread_fallback(ca))
            elif framework:
                parts.append(f'<div class="ri"><span class="rl">🛠 框架:</span> {_esc(framework)}</div>')
            if ca_arch and not code_summary and not is_gread_analysis:
                parts.append(f'<div class="ri"><span class="rl">🏗 架构:</span> {ca_arch}</div>')
            if ca_chain and not is_gread_analysis:
                parts.append(f'<div class="ri"><span class="rl">🔗 调用链:</span> <code class="cc">{ca_chain}</code></div>')
            if ca_classes and isinstance(ca_classes, list) and not is_gread_analysis:
                cls_tags = "".join(f'<span class="ctag">{_esc(c)}</span>' for c in ca_classes[:8])
                parts.append(f'<div class="ri"><span class="rl">🎯 核心类:</span> {cls_tags}</div>')
            cq_parts = []
            if ca_quality.get("tests"):
                cq_parts.append("✅ Tests")
            if ca_quality.get("framework"):
                cq_parts.append(f"🛠 {_esc(ca_quality['framework'])}")
            if ca_quality.get("modularity"):
                cq_parts.append(f"📦 {_esc(ca_quality['modularity'])}")
            if cq_parts and not is_gread_analysis:
                parts.append(f'<div class="ri"><span class="rl">📋 质量:</span> {" · ".join(cq_parts)}</div>')
            if ca_repro and not is_gread_analysis:
                parts.append(f'<div class="ri"><span class="rl">🔄 可复现:</span> {ca_repro}</div>')
            repo_html = f'''<details class="sec repo-sec">
  <summary class="sec-h">💻 代码 & 仓库信息</summary>
  <div class="repo-body">{"".join(parts)}</div>
</details>'''

        # Abstract section — collapsible, default open
        abs_section = f'''<details class="sec abs-sec">
  <summary class="sec-h">📝 摘要</summary>
  <div class="abs-body">
    <div class="azh">{abstract_zh}</div>
    <div class="aen">{abstract_en}</div>
  </div>
</details>'''

        card = f"""
<div class="card" tabindex="-1" id="paper-{_esc(pid)}" data-paper-id="{_esc(pid)}" data-code="{'1' if has_code_flag else '0'}" data-date="{_esc(date)}">
  <div class="ch">
    <div class="ct">
      <div class="tzh">{title_zh}</div>
      <div class="ten">{title}</div>

    </div>
    <div class="cd">
      <span class="date">{date}</span>
    </div>
  </div>
  <div class="cm">
    {f'<span class="au">{authors}</span>' if authors else ''}
    {tags}
  </div>
      <div class="paper-ai-actions">
        <button class="ai-read-btn" type="button" onclick="readPaper(this)" aria-label="AI 解读：{_esc(p.get('title', pid))}">✦ AI 解读</button>
        <label class="paper-select"><input type="checkbox" onchange="togglePaperSelection(this)" aria-label="选择论文：{_esc(p.get('title', pid))}">加入对比</label>
        {code_html}
        <a href="{link}" target="_blank" class="al" title="打开论文原文（{link_kind}）">📎 {_esc(pid)}</a>
      </div>
  <p class="paper-teaser">{teaser}</p>
  <details class="paper-details" ontoggle="hydratePaperDetails(this)">
    <summary>展开论文详情</summary>
    <template><div class="detail">
    <div class="cs">{status_html}</div>
    {kp_html}
    {repo_html}
    {figs_html}
    {abs_section}
    </div></template>
  </details>
</div>"""
        cards.append(card)

        # Collect data for chatbot
        js_papers.append({
            "id": pid,
            "evidence_url": evidence_manifest.get(pid),
            "authors": authors,
            "title_en": p.get("title", ""),
            "title_zh": trans.get("title_zh", p.get("title", "")),
            "key_points": key_points.strip() if key_points else "",
            "abstract": abstract,
            "abstract_zh": trans.get("abstract_zh", ""),
            "task_types": task_types if isinstance(task_types, list) else [task_types],
            "published_date": date,
            "research_score": r_score,
            "engineering_score": e_score,
            "priority": priority,
            "has_code": has_code_flag,
            "github_url": github_url,
            "framework": framework,
            "architecture": (
                cs_entry.get("architecture", "")
                if isinstance(cs_entry, dict) and code_report_html
                else ca.get("architecture", "") if not is_gread_analysis else ""
            ),
            "reproduction_readiness": (
                cs_entry.get("reproduction_readiness", "")
                if isinstance(cs_entry, dict) and code_report_html
                else ca.get("reproduction_readiness", "") if not is_gread_analysis else ""
            ),
            "arxiv_url": link
        })

    cards_html = "\n".join(cards)
    import json
    js_papers_json = json.dumps(js_papers, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cell AI Research · 论文索引</title>
<script>{theme_js}</script>
<link rel="stylesheet" href="vendor/katex/katex.min.css">
<script defer src="vendor/katex/katex.min.js"></script>
<script defer src="vendor/katex/auto-render.min.js"></script>
<script defer src="web/paper-math.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700&display=swap');

:root {{
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-alt: #f1f5f9;
  --border: #e2e8f0;
  --border-h: #cbd5e1;
  --text: #0f172a;
  --text2: #475569;
  --text3: #94a3b8;
  --accent: #4f46e5;
  --accent-l: #e0e7ff;
  --accent-d: #3730a3;
  --green: #10b981;
  --green-l: #d1fae5;
  --green-d: #065f46;
  --orange: #f97316;
  --orange-l: #ffedd5;
  --orange-d: #9a3412;
  --red: #ef4444;
  --red-l: #fee2e2;
  --red-d: #991b1b;
  --purple: #8b5cf6;
  --purple-l: #ede9fe;
  --purple-d: #5b21b6;
  
  --ga: #10b981;
  --gb: #3b82f6;
  --gc: #f59e0b;
  --gd: #64748b;
  
  --radius: 12px;
  --radius-sm: 8px;
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
  --shadow-h: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
  --font: 'Inter', system-ui, -apple-system, sans-serif;
  --font-title: 'Outfit', 'Georgia', serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  overflow-x: hidden;
}}

/* ===== Layout ===== */
.app-container {{
  display: flex;
  min-height: 100vh;
  position: relative;
}}

/* ===== Sidebar ===== */
.sidebar {{
  width: 320px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  flex-shrink: 0;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), 
              padding 0.3s cubic-bezier(0.4, 0, 0.2, 1), 
              opacity 0.2s ease, 
              min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

.sidebar-header {{
  background: linear-gradient(135deg, var(--accent-d) 0%, var(--accent) 100%);
  padding: 20px;
  border-radius: var(--radius);
  color: #fff;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
}}

.sidebar-header h1 {{
  font-family: var(--font-title);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
}}

.sidebar-header p {{
  font-size: 11px;
  opacity: 0.8;
  margin-top: 4px;
}}

.search-box {{
  width: 100%;
}}

.search-input {{
  width: 100%;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg);
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
}}

.search-input:focus {{
  border-color: var(--accent);
  background: #fff;
  box-shadow: 0 0 0 3px var(--accent-l);
}}

.filter-group h3,
.stats-panel h3 {{
  font-size: 11px;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
}}

.filter-buttons {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}

.month-filter {{
  margin-top: 10px;
}}

.month-select {{
  width: 100%;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text2);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease;
}}

.month-select:hover,
.month-select:focus {{
  border-color: var(--accent);
  color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-l);
}}

.fbtn {{
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text2);
  font-size: 13px;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.fbtn:hover {{
  border-color: var(--accent);
  color: var(--accent);
  background: var(--bg);
}}

.fbtn.active {{
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}}

.stats-panel {{
  display: flex;
  flex-direction: column;
  gap: 16px;
}}

.stat-item {{
  display: flex;
  flex-direction: column;
  gap: 6px;
}}

.stat-label {{
  font-size: 12px;
  color: var(--text2);
  display: flex;
  justify-content: space-between;
}}

.stat-val {{
  font-weight: 700;
  color: var(--text);
}}

.progress-bar {{
  height: 6px;
  width: 100%;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}}

.progress-fill {{
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.3s ease;
}}

.sidebar-footer {{
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}}

.expand-btn {{
  padding: 10px;
  border-radius: var(--radius-sm);
  background: var(--orange-l);
  color: var(--orange-d);
  border: 1px solid rgba(249, 115, 22, 0.2);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  text-align: center;
}}

.expand-btn:hover {{
  background: var(--orange);
  color: #fff;
}}

.update-time {{
  font-size: 11px;
  color: var(--text3);
  text-align: center;
}}

/* Sidebar Toggle Button */
.sidebar-toggle {{
  position: fixed;
  left: 320px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 48px;
  background: var(--accent);
  color: #fff;
  border: 1px solid var(--accent-d);
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 12px;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  outline: none;
}}

.sidebar-toggle:hover {{
  background: var(--accent-d);
}}

.app-container.collapsed .sidebar {{
  width: 0;
  min-width: 0;
  padding: 0;
  opacity: 0;
  border-right: none;
  overflow: hidden;
}}

.app-container.collapsed .sidebar-toggle {{
  left: 0;
}}

/* ===== Main Content ===== */
.main-content {{
  flex: 1;
  padding: 24px;
  height: 100vh;
  overflow-y: auto;
  background: var(--bg);
}}

.cards-flow {{
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 900px;
  margin: 0 auto;
}}

/* ===== Paper Card ===== */
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow);
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
}}

.card:hover {{
  transform: translateY(-2px);
  box-shadow: var(--shadow-h);
  border-color: var(--border-h);
}}

.card.ga {{ border-left: 5px solid var(--ga); }}
.card.gb {{ border-left: 5px solid var(--gb); }}
.card.gc {{ border-left: 5px solid var(--gc); }}
.card.gd {{ border-left: 5px solid var(--gd); }}

.ch {{
  display: flex;
  gap: 16px;
  align-items: flex-start;
}}

.badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  font-weight: 800;
  font-size: 14px;
  color: #fff;
  flex-shrink: 0;
}}

.badge.ga {{ background: var(--ga); }}
.badge.gb {{ background: var(--gb); }}
.badge.gc {{ background: var(--gc); }}
.badge.gd {{ background: var(--gd); }}

.ct {{
  flex: 1;
  min-width: 0;
}}

.tzh {{
  font-family: var(--font-title);
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.35;
}}

.ten {{
  font-size: 13px;
  color: var(--text2);
  margin-top: 4px;
  font-style: italic;
}}

.cd {{
  text-align: right;
  flex-shrink: 0;
}}

.date {{
  font-size: 12px;
  color: var(--text3);
  font-weight: 500;
}}

.pri {{
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-l);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  display: inline-block;
  margin-top: 6px;
}}

/* Meta Row */
.cm {{
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 12px;
}}

.au {{
  color: var(--text2);
  font-weight: 500;
}}

.sc {{
  color: var(--accent);
  font-weight: 700;
  background: var(--accent-l);
  padding: 1px 6px;
  border-radius: 4px;
}}

.tag {{
  padding: 2px 8px;
  border-radius: 20px;
  background: var(--surface-alt);
  color: var(--text2);
  font-size: 11px;
  border: 1px solid var(--border);
  font-weight: 500;
}}

.tb {{
  background: var(--green-l);
  color: var(--green-d);
  border-color: rgba(16, 185, 129, 0.2);
}}

.cb {{
  padding: 2px 8px;
  border-radius: 20px;
  background: var(--accent-l);
  color: var(--accent-d);
  font-size: 11px;
  text-decoration: none;
  font-weight: 600;
  border: 1px solid rgba(79, 70, 229, 0.15);
}}

.cb.lb {{
  background: var(--orange-l);
  color: var(--orange-d);
  border: 1px solid rgba(249, 115, 22, 0.15);
}}

.al {{
  color: var(--text3);
  text-decoration: none;
  font-size: 11px;
  transition: color 0.15s;
}}

.al:hover {{
  color: var(--accent);
  text-decoration: underline;
}}

.pdf-link {{
  color: var(--red);
  font-weight: 700;
  margin-left: 4px;
}}

.pdf-link:hover {{
  color: var(--red-d);
}}

/* Status Indicators */
.cs {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}}

.cs span {{
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--surface-alt);
  font-weight: 600;
  border: 1px dashed var(--border);
}}

.cs span.sd {{
  background: var(--green-l);
  color: var(--green-d);
  border-color: rgba(16, 185, 129, 0.3);
  border-style: solid;
}}

.cs span.sn {{
  background: #f3f4f6;
  color: #9ca3af;
  border-color: #e5e7eb;
  border-style: solid;
  opacity: 0.72;
}}

.cs span.sp {{
  background: var(--orange-l);
  color: var(--orange-d);
  border-color: rgba(249, 115, 22, 0.3);
  border-style: solid;
  position: relative;
  padding-left: 15px;
}}

.cs span.sp::before {{
  content: "";
  position: absolute;
  left: 6px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  animation: statusPulse 1.4s ease-in-out infinite;
}}

.cs span.se {{
  background: var(--red-l);
  color: var(--red-d);
  border-color: rgba(239, 68, 68, 0.3);
  border-style: solid;
}}

@keyframes statusPulse {{
  0%, 100% {{ opacity: 0.35; transform: scale(0.8); }}
  50% {{ opacity: 1; transform: scale(1.15); }}
}}

.cs span.sn {{
  opacity: 0.4;
}}

/* Detail Sections */
.detail {{
  display: flex;
  flex-direction: column;
  gap: 12px;
}}

.kp {{
  background: #f0fdf4;
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-sm);
  padding: 16px;
}}

.kp-label {{
  font-size: 12px;
  font-weight: 800;
  color: var(--green-d);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}}

.kp-content {{
  font-size: 13.5px;
  line-height: 1.7;
  color: var(--text);
}}

.sec {{
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--surface);
}}

.sec[open] {{
  border-color: var(--border-h);
}}

.sec-h {{
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text2);
  padding: 12px 16px;
  cursor: pointer;
  background: var(--surface-alt);
  user-select: none;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 8px;
}}

.sec-h:hover {{
  background: var(--border);
}}

.sec-h::-webkit-details-marker {{ display: none; }}
.sec-h::before {{
  content: '▸';
  font-size: 10px;
  color: var(--text3);
  transition: transform 0.2s;
  display: inline-block;
}}

.sec[open] > .sec-h::before {{
  transform: rotate(90deg);
}}

.sec[open] > .sec-h {{
  border-bottom: 1px solid var(--border);
}}

.repo-body, .abs-body, .fig-grid {{
  padding: 16px;
  background: #fff;
}}

.ri {{
  font-size: 12.5px;
  margin-bottom: 8px;
}}

.ri:last-child {{
  margin-bottom: 0;
}}

.rl {{
  font-weight: 600;
  color: var(--text);
}}

.rlink {{
  color: var(--accent);
  text-decoration: none;
}}

.msg-bubble .md-h {{
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  margin: 10px 0 4px;
}}

.msg-bubble .md-h:first-child {{
  margin-top: 0;
}}

.msg-bubble .md-p {{
  margin: 0 0 6px;
}}

.msg-bubble .md-p:last-child {{
  margin-bottom: 0;
}}

.msg-bubble .md-list {{
  margin: 4px 0 8px;
  padding-left: 20px;
}}

.msg-bubble .md-list li {{
  margin: 2px 0;
}}

.msg-bubble .md-hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 10px 0;
}}

.rlink:hover {{
  text-decoration: underline;
}}

.cc {{
  font-family: var(--font-mono);
  background: var(--surface-alt);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11.5px;
  color: var(--purple-d);
}}

.ctag {{
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--purple-l);
  color: var(--purple-d);
  font-size: 11px;
  font-weight: 600;
  margin-right: 4px;
}}

/* Figures Grid */
.fig-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}}

.fig-item {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}

.fig-img {{
  width: 100%;
  height: 150px;
  object-fit: contain;
  background: var(--bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  cursor: zoom-in;
  transition: transform 0.2s ease;
}}

.fig-img:hover {{
  transform: scale(1.02);
  border-color: var(--border-h);
}}

.fig-cap {{
  font-size: 11px;
  color: var(--text2);
  line-height: 1.4;
}}

.azh {{
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
  margin-bottom: 12px;
}}

.aen {{
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--text3);
  padding-top: 12px;
  border-top: 1px solid var(--border);
}}

/* ===== Modal Gallery ===== */
.modal {{
  display: none;
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.85);
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  user-select: none;
}}

.modal.show {{
  display: flex;
}}

.modal-content {{
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 90vw;
  max-height: 92vh;
}}

.modal-content img {{
  max-width: 85vw;
  max-height: 75vh;
  object-fit: contain;
  border-radius: var(--radius);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  cursor: default;
}}

.modal-caption {{
  margin-top: 12px;
  color: #f1f5f9;
  font-size: 13px;
  line-height: 1.5;
  text-align: center;
  max-width: 820px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
}}

.modal-counter {{
  margin-top: 6px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
}}

.modal-btn {{
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(30, 41, 59, 0.75);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 1010;
}}

.modal-btn:hover {{
  background: rgba(30, 41, 59, 0.95);
  transform: translateY(-50%) scale(1.1);
  border-color: rgba(255, 255, 255, 0.4);
}}

.modal-prev {{
  left: 24px;
}}

.modal-next {{
  right: 24px;
}}

.modal-close {{
  position: fixed;
  top: 20px;
  right: 24px;
  background: rgba(30, 41, 59, 0.75);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 1010;
}}

.modal-close:hover {{
  background: rgba(30, 41, 59, 0.95);
  transform: scale(1.08);
}}

/* ===== Back to top ===== */
.btt {{
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
  display: none;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.2s ease;
  z-index: 99;
}}

.btt:hover {{
  transform: translateY(-2px);
  background: var(--accent-d);
}}

.btt.show {{
  display: flex;
}}

/* ===== Paper quick navigation rail ===== */
.paper-rail {{
  position: fixed;
  top: 72px;
  right: 8px;
  bottom: 84px;
  width: 30px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  z-index: 97;
}}

.paper-rail-mark {{
  width: 12px;
  min-height: 2px;
  flex: 0 1 5px;
  padding: 0;
  border: 0;
  border-radius: 2px;
  background: var(--text3);
  opacity: 0.42;
  cursor: pointer;
  transition: width 0.16s ease, opacity 0.16s ease, background 0.16s ease;
  position: relative;
}}

.paper-rail-mark:hover,
.paper-rail-mark:focus-visible {{
  width: 26px;
  opacity: 1;
  background: var(--accent);
  outline: none;
}}

.paper-rail-mark.active {{
  width: 22px;
  opacity: 1;
  background: var(--accent);
}}

.paper-rail-tooltip {{
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
  width: max-content;
  max-width: 360px;
  padding: 7px 10px;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--surface);
  color: var(--text);
  box-shadow: var(--shadow-h);
  font-size: 12px;
  line-height: 1.35;
  text-align: left;
  white-space: normal;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.14s ease;
}}

.paper-rail-mark:hover .paper-rail-tooltip,
.paper-rail-mark:focus-visible .paper-rail-tooltip {{
  opacity: 1;
  visibility: visible;
}}

/* ===== Chat Drawer ===== */
.chat-trigger {{
  position: fixed;
  bottom: 24px;
  right: 88px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 30px;
  padding: 12px 24px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
  z-index: 998;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}}

.chat-trigger:hover {{
  transform: translateY(-2px);
  background: var(--accent-d);
}}

.chat-drawer {{
  position: fixed;
  right: -420px;
  top: 0;
  width: 400px;
  height: 100vh;
  background: var(--surface);
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
  z-index: 1002;
  display: flex;
  flex-direction: column;
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-left: 1px solid var(--border);
}}

.chat-drawer.open {{
  right: 0;
}}

.chat-header {{
  padding: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--surface-alt);
}}

.chat-title h3 {{
  font-size: 15px;
  font-weight: 700;
}}

.chat-subtitle {{
  font-size: 11px;
  color: var(--text3);
}}

.chat-close {{
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text2);
}}

.chat-close:hover {{
  color: var(--text);
}}

.chat-messages {{
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--bg);
}}

.msg {{
  display: flex;
  flex-direction: column;
  max-width: 85%;
}}

.msg.ai {{
  align-self: flex-start;
}}

.msg.user {{
  align-self: flex-end;
}}

.msg-bubble {{
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
}}

.msg.ai .msg-bubble {{
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-top-left-radius: 2px;
}}

.msg.user .msg-bubble {{
  background: var(--accent);
  color: #fff;
  border-top-right-radius: 2px;
}}

.suggestion-chips {{
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 10px;
}}

.chip {{
  padding: 6px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  font-size: 11.5px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--accent-d);
  font-weight: 500;
}}

.chip:hover {{
  background: var(--accent-l);
  border-color: var(--accent);
}}

.chat-input-area {{
  padding: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  align-items: center;
  background: var(--surface);
}}

.chat-input {{
  flex: 1;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px;
  font-size: 13px;
  outline: none;
  resize: none;
  background: var(--bg);
  transition: all 0.2s;
}}

.chat-input:focus {{
  border-color: var(--accent);
  background: #fff;
}}

.chat-send {{
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 10px 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}}

.chat-send:hover {{
  background: var(--accent-d);
}}

.typing-indicator {{
  display: flex;
  gap: 4px;
  padding: 4px 8px;
}}

.typing-dot {{
  width: 6px;
  height: 6px;
  background: var(--text3);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}}

.typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
.typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}

@keyframes typing {{
  0%, 80%, 100% {{ transform: scale(0); }}
  40% {{ transform: scale(1); }}
}}

/* ===== Responsive ===== */
@media (max-width: 1024px) {{
  .paper-rail {{
    display: none;
  }}
  .app-container {{
    flex-direction: column;
  }}
  .sidebar {{
    width: 100%;
    height: auto;
    position: relative;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }}
  .main-content {{
    height: auto;
  }}
  .sidebar-toggle {{
    display: none;
  }}
  .chat-drawer {{
    width: 100%;
    right: -100%;
  }}
}}
{copilot_css}
{paper_list_css}
{theme_css}
</style>
</head>
<body>

<div class="app-container">
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1>🔬 Cell AI Console</h1>
      <p>自动追踪细胞生物学 × AI 前沿</p>
    </div>
    
    <div class="search-box">
      <input class="search-input" id="searchInput" type="text" placeholder="🔍 搜索标题 / 摘要 / 标签 / 作者..." oninput="doSearch(this.value)">
    </div>
    
    <button id="mobileFilterButton" type="button" onclick="openMobileFilters()" aria-haspopup="dialog">筛选论文</button>
    <div id="desktopFilterSlot"><div class="filter-group" id="paperFilters">
      <h3>筛选</h3>
      <div class="filter-buttons">
        <button class="fbtn active" onclick="doFilter('all', this)">全部 ({total})</button>
        <button class="fbtn" onclick="doFilter('code', this)">💻 有代码 ({has_code})</button>
      </div>
      <div class="month-filter">
        <select class="month-select" id="monthSelect" onchange="doMonthFilter(this.value)">
          {month_options}
        </select>
      </div>
    </div>
    
    </div>
    <details class="stats-panel"><summary>数据概况 · {total} 篇</summary>
      <div class="stat-item">
        <div class="stat-label">发现论文 <span class="stat-val">{total}</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
      </div>
      <div class="stat-item">
        <div class="stat-label">HTML 全文 <span class="stat-val">{has_html} / {total}</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width: {has_html/total*100 if total else 0:.0f}%;"></div></div>
      </div>
      <div class="stat-item">
        <div class="stat-label">已核验代码链接 <span class="stat-val">{has_code} / {total}</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width: {has_code/total*100 if total else 0:.0f}%;"></div></div>
      </div>
    </details>

    <div class="sidebar-footer">
      <div class="update-time">更新于: {generated_at}</div>
    </div>
  </aside>
  
  <button class="sidebar-toggle" id="sidebarToggle" onclick="toggleSidebar()" title="收起/展开侧边栏">◀</button>
  
  <main class="main-content">
    <div class="list-toolbar"><span id="resultCount" role="status" aria-live="polite"></span><div class="list-actions"><button id="expandBtn" type="button" onclick="toggleAll()">展开已显示论文</button><button type="button" onclick="resetPaperFilters()">重置筛选</button><button id="themeToggle" type="button" aria-label="切换到暗色模式">🌙 暗色</button></div></div>
    <div id="emptyResults" hidden>没有找到匹配的论文。试试其他关键词，或重置筛选。</div>
    <div id="list" class="cards-flow">
      {cards_html}
    </div>
    <div class="list-more"><div id="loadMorePapers" role="status">继续向下滚动，自动载入更多论文</div></div>
  </main>
</div>

<dialog id="mobileFilters" aria-labelledby="filterDialogTitle"><div class="filter-dialog-header"><h2 id="filterDialogTitle">筛选论文</h2><button type="button" onclick="closeMobileFilters()" aria-label="关闭筛选">✕</button></div><div id="mobileFilterSlot"></div><button class="filter-apply" type="button" onclick="closeMobileFilters()">查看筛选结果</button></dialog>

{copilot_html}

<nav class="paper-rail" id="paperRail" aria-label="论文快速导航"></nav>

<div class="modal" id="modal">
  <button class="modal-btn modal-prev" id="modal-prev" type="button" aria-label="上一张">◀</button>
  <div class="modal-content" onclick="event.stopPropagation()">
    <img id="modal-img" src="" alt="论文关键图示" />
    <div class="modal-caption" id="modal-caption"></div>
    <div class="modal-counter" id="modal-counter"></div>
  </div>
  <button class="modal-btn modal-next" id="modal-next" type="button" aria-label="下一张">▶</button>
  <button class="modal-close" id="modal-close" type="button" aria-label="关闭">✕</button>
</div>

<button class="btt" id="btt" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" title="回到顶部">↑</button>

<script>
const PAPERS_DB = {js_papers_json};
const LLM_BASE = {json.dumps(BROWSER_LLM_BASE).replace(chr(60), chr(92) + "u003c")};
const LLM_MODEL = {json.dumps(BROWSER_LLM_MODEL).replace(chr(60), chr(92) + "u003c")};
let activeFilter = 'all';
let activeMonth = 'all';

{paper_list_js}

/* Image modal gallery */
const modalGallery = {{
  items: [],
  index: 0
}};

function renderModalImage(targetIndex) {{
  if (!modalGallery.items.length) return;
  if (targetIndex < 0) targetIndex = modalGallery.items.length - 1;
  if (targetIndex >= modalGallery.items.length) targetIndex = 0;
  modalGallery.index = targetIndex;

  const current = modalGallery.items[targetIndex];
  const modalImg = document.getElementById('modal-img');
  const modalCap = document.getElementById('modal-caption');
  const modalCounter = document.getElementById('modal-counter');
  const prevBtn = document.getElementById('modal-prev');
  const nextBtn = document.getElementById('modal-next');

  if (modalImg) modalImg.src = current.src;
  if (modalCap) modalCap.textContent = current.caption;
  if (modalCounter) {{
    modalCounter.textContent = `${{targetIndex + 1}} / ${{modalGallery.items.length}}`;
    modalCounter.style.display = modalGallery.items.length > 1 ? 'block' : 'none';
  }}

  const multi = modalGallery.items.length > 1;
  if (prevBtn) prevBtn.style.display = multi ? 'flex' : 'none';
  if (nextBtn) nextBtn.style.display = multi ? 'flex' : 'none';
}}

function openModal(target) {{
  let imgElem = null;
  let src = '';
  if (typeof target === 'string') {{
    src = target;
    const allImgs = Array.from(document.querySelectorAll('.fig-img'));
    imgElem = allImgs.find(i => i.src === src || i.getAttribute('src') === src);
  }} else if (target && target.tagName === 'IMG') {{
    imgElem = target;
    src = target.src || target.getAttribute('src');
  }}

  if (imgElem) {{
    const grid = imgElem.closest('.fig-grid');
    if (grid) {{
      const items = Array.from(grid.querySelectorAll('.fig-item'));
      modalGallery.items = items.map(item => ({{
        src: item.querySelector('.fig-img')?.getAttribute('src') || '',
        caption: item.querySelector('.fig-cap')?.textContent.trim() || ''
      }}));
      const foundIdx = items.findIndex(item => item.querySelector('.fig-img') === imgElem);
      modalGallery.index = foundIdx >= 0 ? foundIdx : 0;
    }} else {{
      modalGallery.items = [{{ src: src, caption: '' }}];
      modalGallery.index = 0;
    }}
  }} else {{
    modalGallery.items = [{{ src: src, caption: '' }}];
    modalGallery.index = 0;
  }}

  renderModalImage(modalGallery.index);
  document.getElementById('modal').classList.add('show');
}}

// 弹窗按键与遮罩关闭事件
document.getElementById('modal-prev')?.addEventListener('click', event => {{
  event.stopPropagation();
  renderModalImage(modalGallery.index - 1);
}});

document.getElementById('modal-next')?.addEventListener('click', event => {{
  event.stopPropagation();
  renderModalImage(modalGallery.index + 1);
}});

document.getElementById('modal-close')?.addEventListener('click', event => {{
  event.stopPropagation();
  document.getElementById('modal').classList.remove('show');
}});

document.getElementById('modal')?.addEventListener('click', event => {{
  if (event.target.id === 'modal') {{
    document.getElementById('modal').classList.remove('show');
  }}
}});

/* Back to top */
window.addEventListener('scroll', () => {{
  document.getElementById('btt').classList.toggle('show', window.scrollY > 400);
}});

/* Keyboard shortcuts: Escape closes modal, Arrow keys navigate */
document.addEventListener('keydown', event => {{
  const modal = document.getElementById('modal');
  if (!modal || !modal.classList.contains('show')) return;

  if (event.key === 'ArrowLeft') {{
    event.preventDefault();
    renderModalImage(modalGallery.index - 1);
  }} else if (event.key === 'ArrowRight') {{
    event.preventDefault();
    renderModalImage(modalGallery.index + 1);
  }} else if (event.key === 'Escape') {{
    modal.classList.remove('show');
  }}
}});

{copilot_js}

initPaperList();
</script>
</body>
</html>"""


# ============================================================
# Codebase Analysis (CodeGraph + RepoWiki)
# ============================================================
def cg_sync():
    """同步 CodeGraph 索引"""
    print("  [CodeGraph] Syncing index...")
    try:
        r = subprocess.run(
            ["codegraph", "sync", str(WORKSPACE)],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode != 0:
            print(f"  [CodeGraph] Sync failed: {r.stderr[:200]}")
            return False
        return True
    except Exception as e:
        print(f"  [CodeGraph] Sync command error: {e}")
        return False


def cg_query(repo_name: str) -> dict:
    """用 CodeGraph 查询仓库的符号、结构"""
    repo_dir = WORKSPACE / "code" / repo_name
    if not repo_dir.exists():
        return {"error": f"repo dir not found: {repo_dir}"}

    result = {"files": [], "key_symbols": [], "top_files": []}

    # 1. 查询关键符号（类名、函数名）
    for query in ["class", "def ", "def train", "def predict", "def __init__"]:
        try:
            r = subprocess.run(
                ["codegraph", "query", query, "--limit", "5"],
                capture_output=True, text=True, timeout=30,
                cwd=str(repo_dir)
            )
            if r.returncode == 0 and r.stdout.strip():
                lines = [l for l in r.stdout.strip().split("\n") if l.strip()][:8]
                result["key_symbols"].extend(lines)
        except Exception:
            pass

    # 2. 获取文件结构
    try:
        r = subprocess.run(
            ["codegraph", "files", "--limit", "20"],
            capture_output=True, text=True, timeout=30,
            cwd=str(repo_dir)
        )
        if r.returncode == 0:
            result["files"] = [l.strip() for l in r.stdout.strip().split("\n") if l.strip()][:20]
    except Exception:
        pass

    # 3. 查看索引状态
    try:
        r = subprocess.run(
            ["codegraph", "status"],
            capture_output=True, text=True, timeout=15,
            cwd=str(repo_dir)
        )
        if r.returncode == 0:
            result["status"] = r.stdout.strip()[:500]
    except Exception:
        pass

    result["cg_available"] = bool(result["key_symbols"] or result["files"])
    return result


def rw_scan(repo_name: str, repo_path: Path) -> dict:
    """用 RepoWiki 扫描并生成 wiki 文档"""
    import requests
    result = {"scan_ok": False, "wiki_dir": "", "summary": ""}

    reports_dir = WORKSPACE / "reports"
    target_dir = reports_dir / f"{repo_name}_wiki"
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 生成 Markdown wiki
        r = subprocess.run(
            ["repowiki", "scan", str(repo_path), "-f", "markdown", "-o", str(target_dir), "-l", "zh"],
            capture_output=True, text=True, timeout=300
        )

        result["scan_ok"] = r.returncode == 0
        result["stdout"] = r.stdout.strip()[:1000]
        result["stderr"] = r.stderr.strip()[:500] if not result["scan_ok"] else ""

        # 检查生成了什么文件
        if target_dir.exists():
            files = list(target_dir.rglob("*.md"))
            result["generated_files"] = [str(f.relative_to(target_dir)) for f in files[:10]]
        else:
            result["generated_files"] = []

        result["wiki_dir"] = str(target_dir)

        # 后处理：用 Agents-A1 把 index.md 概览翻译成中文
        index_path = target_dir / "index.md"
        if index_path.exists():
            eng = index_path.read_text(encoding="utf-8")
            if len(eng) > 50 and not any('\u4e00' <= c <= '\u9fff' for c in eng[:200]):
                try:
                    resp = requests.post(
                        f"{LLM_BASE}/chat/completions",
                        json={"model": LLM_MODEL, "messages": [{"role": "user", "content": f"将以下项目概览翻译成中文，保持Markdown格式不变：\n\n{eng}"}], "temperature": 0.1, "max_tokens": 4096},
                        timeout=60
                    )
                    if resp.status_code == 200:
                        zh = resp.json()["choices"][0]["message"]["content"].strip()
                        if zh and len(zh) > len(eng) * 0.3:
                            index_path.write_text(zh, encoding="utf-8")
                            result["translated"] = True
                except Exception as e:
                    result["translation_error"] = str(e)
    except subprocess.TimeoutExpired:
        result["error"] = "timeout after 300s"
    except Exception as e:
        result["error"] = str(e)

    return result


def _process_inline_markdown(text):
    import re
    # Escape HTML
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # Inline code
    text = re.sub(r"`(.*?)`", r'<code class="inline-code">\1</code>', text)
    # Links
    def repl_link(match):
        t = match.group(1)
        p = match.group(2)
        if p.endswith(".md"):
            p = p[:-3] + ".html"
        return f'<a href="{p}">{t}</a>'
    text = re.sub(r"\[(.*?)\]\((.*?)\)", repl_link, text)
    return text


def render_markdown(md_content, is_sidebar=False):
    lines = md_content.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False
    code_lang = ""
    code_content = []

    for line in lines:
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith("```"):
            if in_code_block:
                code_text = "\n".join(code_content)
                code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html_lines.append(f'<pre class="code-block"><code class="language-{code_lang}">{code_text}</code></pre>')
                in_code_block = False
                code_content = []
            else:
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue

        if in_code_block:
            code_content.append(line)
            continue

        # Lists
        is_list_item = stripped.startswith("- ") or stripped.startswith("* ") or (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == "." and stripped[2] == " ")
        if is_list_item:
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item_text = stripped[2:].strip()
            item_text = _process_inline_markdown(item_text)
            html_lines.append(f"<li>{item_text}</li>")
            continue
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False

        # Empty lines
        if not stripped:
            html_lines.append("<br>")
            continue

        # Headings
        if stripped.startswith("#"):
            level = 0
            while level < len(stripped) and stripped[level] == "#":
                level += 1
            if level <= 6 and level < len(stripped) and stripped[level] == " ":
                heading_text = stripped[level:].strip()
                heading_text = _process_inline_markdown(heading_text)
                html_lines.append(f"<h{level}>{heading_text}</h{level}>")
                continue

        # Paragraph
        line_text = _process_inline_markdown(stripped)
        html_lines.append(f"<p>{line_text}</p>")

    if in_list:
        html_lines.append("</ul>")
        
    return "\n".join(html_lines)


def wrap_wiki_page(title, repo_name, body_html, sidebar_html, back_link):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700&display=swap');

:root {{
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-alt: #f1f5f9;
  --border: #e2e8f0;
  --border-h: #cbd5e1;
  --text: #0f172a;
  --text2: #475569;
  --text3: #94a3b8;
  --accent: #4f46e5;
  --accent-l: #e0e7ff;
  --accent-d: #3730a3;
  
  --radius: 12px;
  --radius-sm: 8px;
  --font: 'Inter', system-ui, -apple-system, sans-serif;
  --font-title: 'Outfit', 'Georgia', serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}}

.navbar {{
  height: 56px;
  background: linear-gradient(135deg, var(--accent-d) 0%, var(--accent) 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 100;
  flex-shrink: 0;
}}

.navbar-brand {{
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 16px;
}}

.back-btn {{
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;
}}

.back-btn:hover {{
  background: rgba(255,255,255,0.25);
}}

.container {{
  display: flex;
  flex: 1;
  overflow: hidden;
}}

.sidebar {{
  width: 260px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 24px;
  overflow-y: auto;
  flex-shrink: 0;
}}

.sidebar ul {{
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}}

.sidebar li {{
  font-size: 14px;
}}

.sidebar a {{
  color: var(--text2);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s;
  display: block;
}}

.sidebar a:hover {{
  color: var(--accent);
}}

.sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4 {{
  font-size: 11px;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 700;
  margin-top: 16px;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}}

.sidebar h1:first-child, .sidebar h2:first-child, .sidebar h3:first-child {{
  margin-top: 0;
}}

.content-area {{
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  background: #fff;
}}

.markdown-body {{
  max-width: 800px;
  margin: 0 auto;
}}

.markdown-body h1 {{
  font-family: var(--font-title);
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}}

.markdown-body h2 {{
  font-size: 20px;
  margin-top: 24px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 6px;
}}

.markdown-body h3 {{
  font-size: 16px;
  margin-top: 20px;
  margin-bottom: 12px;
}}

.markdown-body p {{
  margin-bottom: 16px;
}}

.markdown-body ul, .markdown-body ol {{
  margin-bottom: 16px;
  padding-left: 20px;
}}

.markdown-body li {{
  margin-bottom: 6px;
}}

.markdown-body a {{
  color: var(--accent);
  text-decoration: none;
}}

.markdown-body a:hover {{
  text-decoration: underline;
}}

.code-block {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 16px;
  overflow-x: auto;
  margin-bottom: 16px;
}}

.code-block code {{
  font-family: var(--font-mono);
  font-size: 13px;
  color: #0f172a;
}}

.inline-code {{
  font-family: var(--font-mono);
  background: var(--surface-alt);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--accent-d);
}}
</style>
</head>
<body>

<header class="navbar">
  <div class="navbar-brand">🔬 Cell AI Console / {repo_name} Wiki</div>
  <a href="{back_link}" class="back-btn">返回主控制台</a>
</header>

<div class="container">
  <aside class="sidebar">
    {sidebar_html}
  </aside>
  
  <main class="content-area">
    <article class="markdown-body">
      {body_html}
    </article>
  </main>
</div>

</body>
</html>
"""


def prune_sidebar(sidebar_md: str) -> str:
    """过滤掉 _sidebar.md 中无关的本地工具链节点，如 .codegraph, .github 等"""
    lines = sidebar_md.split("\n")
    cleaned = []
    for line in lines:
        if any(x in line.lower() for x in [".codegraph", ".github", "rw_test"]):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def compile_wiki_to_html(wiki_dir: Path, repo_name: str):
    """将 wiki 目录下的所有 markdown 文件转化为本地静态 HTML，实现完全的无CORS离线导航"""
    import re
    import requests
    
    # 1. 查找并生成 Sidebar
    sidebar_file = wiki_dir / "_sidebar.md"
    sidebar_html = ""
    if sidebar_file.exists():
        try:
            sidebar_md = sidebar_file.read_text(encoding="utf-8")
            sidebar_md = prune_sidebar(sidebar_md)
            sidebar_html = render_markdown(sidebar_md, is_sidebar=True)
        except Exception as e:
            print(f"   [WARN] Failed to parse _sidebar.md: {e}")
            
    # 2. 递归遍历编译所有的 md 文件
    for f in list(wiki_dir.rglob("*.md")):
        # 排除 _sidebar.md 和系统冗余模块
        if f.name == "_sidebar.md" or any(x in f.name.lower() for x in [".codegraph", ".github"]):
            try:
                # 删除冗余文件以保持目录整洁
                f.with_suffix(".html").unlink(missing_ok=True)
                f.unlink(missing_ok=True)
            except Exception:
                pass
            continue
            
        try:
            md_content = f.read_text(encoding="utf-8")
            
            # 检测是否为纯英文，如果是则调用本地 LLM 自动翻译成中文
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in md_content[:600])
            if len(md_content.strip()) > 30 and not has_chinese:
                print(f"   [AI Translate] Translating {f.name} into Chinese...")
                try:
                    resp = requests.post(
                        f"{LLM_BASE}/chat/completions",
                        json={
                            "model": LLM_MODEL,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"将以下代码库文档翻译成中文，保持Markdown格式与文件/图片链接（例如 [Link](path.md)）的路径完全不变，仅翻译链接文本与正文：\n\n{md_content}"
                                }
                            ],
                            "temperature": 0.1,
                            "max_tokens": 4096
                        },
                        timeout=120
                    )
                    if resp.status_code == 200:
                        translated_text = resp.json()["choices"][0]["message"]["content"].strip()
                        if translated_text and len(translated_text) > 10:
                            md_content = translated_text
                            f.write_text(md_content, encoding="utf-8")
                            print(f"     ✓ Translated and cached.")
                except Exception as e:
                    print(f"     [WARN] Translation failed for {f.name}: {e}")

            body_html = render_markdown(md_content, is_sidebar=False)
            
            # 计算返回主页的相对路径
            rel_path = f.relative_to(wiki_dir)
            depth = len(rel_path.parts) - 1
            back_link = "../" * depth + "../../index.html"
            
            # 对 sidebar 中的超链接做路径修正
            adjusted_sidebar_html = sidebar_html
            if depth > 0:
                prefix = "../" * depth
                def fix_side_links(match):
                    link = match.group(1)
                    if not link.startswith("http") and not link.startswith("/"):
                        return f'href="{prefix}{link}"'
                    return match.group(0)
                adjusted_sidebar_html = re.sub(r'href="([^"]+)"', fix_side_links, sidebar_html)

            # 包装成 HTML
            page_title = f"{repo_name} Wiki — {f.stem}"
            html_content = wrap_wiki_page(page_title, repo_name, body_html, adjusted_sidebar_html, back_link)
            
            # 输出到同名 .html 文件
            out_file = f.with_suffix(".html")
            out_file.write_text(html_content, encoding="utf-8")
        except Exception as e:
            print(f"   [WARN] Failed to compile {f.name} to html: {e}")


def generate_combined_report(repo_name: str, gh_repo: str, cg_data: dict,
                            rw_data: dict, old_report: str) -> str:
    """合并 CodeGraph + RepoWiki + 原有分析报告"""
    lines = []
    lines.append(f"# {repo_name} — 综合分析报告")
    lines.append(f"")
    lines.append(f"- **GitHub**: {gh_repo}")
    lines.append(f"- **分析时间**: {datetime.now().isoformat()}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # CodeGraph 部分
    lines.append(f"## CodeGraph 知识图谱分析")
    lines.append(f"")
    if cg_data.get("error"):
        lines.append(f"> CodeGraph: {cg_data['error']}")
    else:
        if cg_data.get("key_symbols"):
            lines.append(f"### 关键符号")
            for s in cg_data["key_symbols"][:10]:
                lines.append(f"- `{s}`")
        if cg_data.get("files"):
            lines.append(f"### 文件结构")
            for f in cg_data["files"][:15]:
                lines.append(f"- {f}")
        if cg_data.get("status"):
            lines.append(f"### 索引状态")
            lines.append(f"```")
            lines.append(cg_data["status"])
            lines.append(f"```")
    lines.append(f"")

    # RepoWiki 部分
    lines.append(f"## RepoWiki 文档生成")
    lines.append(f"")
    if rw_data.get("error"):
        lines.append(f"> RepoWiki: {rw_data['error']}")
    elif rw_data.get("scan_ok"):
        lines.append(f"- ✅ 扫描成功")
        lines.append(f"- 📁 Wiki 目录: `{rw_data.get('wiki_dir', '')}`")
        if rw_data.get("generated_files"):
            lines.append(f"- 📄 生成文件:")
            for f in rw_data["generated_files"]:
                lines.append(f"  - {f}")
        if rw_data.get("stdout"):
            lines.append(f"- 输出: {rw_data['stdout']}")
    else:
        lines.append(f"- ❌ 扫描失败: {rw_data.get('stderr', 'unknown')}")
    lines.append(f"")

    lines.append(f"## 原有子代理分析报告")
    lines.append(f"")
    if old_report:
        lines.append(f"```")
        lines.append(old_report[:3000])
        lines.append(f"```")
        lines.append(f"")
        lines.append(f"> 完整报告: [subagent_report.md](subagent_report.md)")
    else:
        lines.append(f"暂无原有分析报告")

    return "\n".join(lines)


def analyze_cloned_repos(papers, force=False):
    """Deprecated: local repository analysis is permanently disabled."""
    print("⏭  Local repository analysis is disabled; use gread_remote.py instead.")
    return
    cloned_targets = []
    
    # 查找所有已经克隆代码的项目
    for p in papers:
        gh = p.get("status", {}).get("github", {})
        if not isinstance(gh, dict):
            continue
        repo_path = gh.get("repo_path")
        if repo_path:
            repo_dir = WORKSPACE / "code" / repo_path
            if repo_dir.exists():
                url = gh.get("url", "")
                cloned_targets.append((repo_path, url))
                
    if not cloned_targets:
        return
        
    print(f"🔍 Found {len(cloned_targets)} cloned repositories to check.")
    
    # 同步 CodeGraph
    cg_sync()
    
    reports_dir = WORKSPACE / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    for repo_name, gh_url in sorted(cloned_targets):
        wiki_dir = reports_dir / f"{repo_name}_wiki"
        wiki_dir.mkdir(parents=True, exist_ok=True)
        
        combined_report_path = wiki_dir / "combined_report.md"
        wiki_index_path = wiki_dir / "index.md"
        
        # 增量分析，避免重复分析已有的报告
        if not force and combined_report_path.exists() and wiki_index_path.exists():
            continue
            
        print(f"▶ Analyzing codebase: {repo_name}...")
        
        # 1. CodeGraph 分析
        cg_data = cg_query(repo_name)
        
        # 2. RepoWiki 文档化
        repo_path = WORKSPACE / "code" / repo_name
        rw_data = rw_scan(repo_name, repo_path)
        
        # 3. 读取并重组已有的子代理报告 (大小写不敏感)
        old_report = ""
        old_report_path = None
        for f in reports_dir.iterdir():
            if f.is_file() and f.suffix == ".md" and f.stem.lower() == repo_name.lower() and not f.name.endswith("_combined.md"):
                old_report_path = f
                break
                
        if old_report_path and old_report_path.exists():
            try:
                old_report = old_report_path.read_text(encoding="utf-8")
                # 将子代理报告移入 wiki 目录下，清理根目录的杂乱文件
                subagent_report_dest = wiki_dir / "subagent_report.md"
                subagent_report_dest.write_text(old_report, encoding="utf-8")
                old_report_path.unlink() # 删除根目录的冗余文件
                print(f"   ✓ Moved raw report to {subagent_report_dest.relative_to(WORKSPACE)}")
            except Exception as e:
                print(f"   [WARN] Failed to organize subagent report: {e}")
                
        # 4. 生成合并报告
        combined_content = generate_combined_report(repo_name, gh_url, cg_data, rw_data, old_report)
        try:
            combined_report_path.write_text(combined_content, encoding="utf-8")
            print(f"   ✓ Unified report generated: {combined_report_path.relative_to(WORKSPACE)}")
        except Exception as e:
            print(f"   [WARN] Failed to write unified report: {e}")
            
        # 5. 编译所有 wiki 页面为本地静态 HTML (实现无 CORS 离线阅读)
        compile_wiki_to_html(wiki_dir, repo_name)


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Cell AI Research 论文索引生成器 v2")
    parser.add_argument("--offline", action="store_true", help="仅用已有缓存生成页面，不调用模型、下载图片或检查链接")
    parser.add_argument("--no-translate", action="store_true", help="跳过 LLM 翻译+摘要")
    parser.add_argument("--no-images", action="store_true", help="跳过 HTML 图片提取")
    parser.add_argument("--refresh-images", action="store_true", help="重新下载 arXiv 原图并刷新图片缓存")
    parser.add_argument("--force-translate", action="store_true", help="强制重新翻译全部")
    parser.add_argument("--no-ollama-translate", action="store_true", help="禁用 Ollama 翻译，改用 Agents-A1 翻译")
    parser.add_argument("--no-code-analysis", action="store_true", help="跳过 gread 代码报告的 LLM 提炼（保留现有缓存）")
    parser.add_argument("--force-code-analysis", action="store_true", help="兼容参数；不会启用本地代码分析")
    args = parser.parse_args()

    if args.offline:
        args.no_translate = True
        args.no_images = True
        args.no_code_analysis = True

    # 全局切换翻译后端
    global USE_OLLAMA_TRANSLATE
    if args.no_ollama_translate:
        USE_OLLAMA_TRANSLATE = False

    # Load
    print("📚 Loading papers.json...")
    with open(PAPERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    papers = data["database"]
    print(f"   Found {len(papers)} papers")

    print("🌐 Code repositories are analyzed remotely through gread; local cloning is disabled.")

    # Translate + Summarize (parallel)
    translations = _load_translations()
    if not args.no_translate:
        print("🌐 Translating + summarizing (parallel)...")
        translations = translate_and_summarize(papers, translations, force=args.force_translate)
    else:
        print("⏭  Skipping translation (--no-translate)")

    # Extract figures
    if not args.no_images:
        print("🖼  Extracting figures from arXiv HTML...")
        extract_all_figures(papers, force=args.refresh_images)
    else:
        print("⏭  Skipping image extraction (--no-images)")

    # Generate HTML
    print("🏗  Generating HTML...")
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # LLM 把 gread 代码分析 dump 提炼成中文总结（增量，缓存于 data/code_summaries.json）
    code_summaries = _load_code_summaries()
    if not args.no_translate and not args.no_code_analysis:
        print("🔎 Summarizing code repositories...")
        code_summaries = summarize_code_repositories(papers, code_summaries, force=args.force_code_analysis)
    else:
        print("⏭  Skipping code summary (--no-translate/--no-code-analysis)")

    arxiv_html_status = refresh_arxiv_link_status(papers, offline=args.offline)
    html_content = generate_html(
        papers,
        translations,
        generated_at,
        arxiv_html_status=arxiv_html_status,
        code_summaries=code_summaries,
        evidence_manifest=export_evidence(papers, PAPER_CONTEXT_DIR, WORKSPACE / "data" / "evidence"),
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    size_kb = len(html_content) / 1024
    print(f"✅ Output: {OUTPUT_FILE} ({size_kb:.0f} KB)")
    print("Done!")


if __name__ == "__main__":
    main()
