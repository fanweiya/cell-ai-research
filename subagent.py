from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader

A1_API = os.environ.get('A1_API_URL', "http://10.0.0.240:8080/v1/chat/completions")
A1_KEY = os.environ.get('A1_API_KEY', 'cell-ai')
A1_MODEL = os.environ.get('A1_MODEL', "stable")
FALLBACK_A1_API = os.environ.get('FALLBACK_A1_API_URL', A1_API)
FALLBACK_A1_MODEL = os.environ.get('FALLBACK_A1_MODEL', "fast")
WORKDIR = Path(os.environ.get("CELL_AI_WORKDIR", str(Path(__file__).resolve().parent)))


def load_input(path: str) -> str:
    """Load input content; GitHub repositories are inspected via gread only."""
    if re.match(r'^https?://github\.com/', path):
        try:
            from gread_remote import as_analysis_context, collect_repository
            return as_analysis_context(collect_repository(path))[:200000]
        except Exception as exc:
            return json.dumps({
                "source": "gread",
                "repository_url": path,
                "error": str(exc),
                "instruction": "Do not fall back to a local clone.",
            }, ensure_ascii=False)
    target_path = Path(path)
    full_path = target_path if target_path.is_absolute() else WORKDIR / target_path
    if full_path.is_file():
        if full_path.suffix.lower() == ".pdf":
            reader = PdfReader(str(full_path))
            pages = [page.extract_text() or "" for page in reader.pages]
            content = "\n\n".join(p for p in pages if p).strip()
            if not content:
                raise ValueError(f"Extracted empty text from PDF: {full_path}")
            return content[:200000]
        return full_path.read_text(encoding="utf-8", errors="replace")[:200000]
    elif full_path.is_dir():
        lines = []
        for root, dirs, files in os.walk(full_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '.codegraph', '__pycache__', 'node_modules', '.github', 'dist', 'build']]
            level = Path(root).relative_to(full_path).parts
            indent = '  ' * len(level)
            lines.append(f"{indent}{Path(root).name}/")
            subindent = '  ' * (len(level) + 1)
            for file in files[:20]:
                lines.append(f"{subindent}{file}")
            if len(level) > 3:
                dirs.clear()
        return "\n".join(lines[:50])
    elif re.match(r'^\d{4}\.\d{5}', path):
        arxiv_id = path.strip()
        html = ""
        fetch_err = None
        try:
            req = urllib.request.Request(
                f"https://arxiv.org/html/{arxiv_id}",
                headers={"User-Agent": "cell-ai-research/2.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            fetch_err = exc

        if not html or "No HTML for" in html or "HTML is not available" in html:
            try:
                abs_req = urllib.request.Request(
                    f"https://arxiv.org/abs/{arxiv_id}",
                    headers={"User-Agent": "cell-ai-research/2.0"},
                )
                with urllib.request.urlopen(abs_req, timeout=30) as resp:
                    abs_html = resp.read().decode("utf-8", errors="replace")
                abs_text = _extract_abs_text(abs_html)
                if abs_text:
                    return abs_text
            except Exception as abs_exc:
                raise RuntimeError(f"Failed to fetch arXiv paper {arxiv_id}: HTML error ({fetch_err}), ABS error ({abs_exc})")
            raise RuntimeError(f"Failed to fetch arXiv paper {arxiv_id}: empty abstract from abs page")

        text = _extract_article_text(html)
        if len(text) > 1000:
            return text
        if html:
            return html[:50000]
        raise RuntimeError(f"Failed to extract paper text for arXiv ID {arxiv_id}")

    else:
        return path[:3000]


def _extract_article_text(html: str) -> str:
    """Extract paper body text from arXiv HTML."""
    match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if match:
        body = match.group(1)
    else:
        match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        body = match.group(1) if match else html

    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)

    text_parts = re.findall(
        r'<(?:p|h[1-6]|li|td|th|caption|div[^>]*class="[^"]*(?:section|abstract|keywords)[^"]*")[^>]*>(.*?)</(?:p|h[1-6]|li|td|th|caption|div)>',
        body,
        re.DOTALL,
    )

    lines = []
    for part in text_parts:
        clean = re.sub(r'<[^>]+>', '', part)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean and len(clean) > 10:
            lines.append(clean)

    result = '\n\n'.join(lines)
    return result[:200000]


def _extract_abs_text(html: str) -> str:
    """Extract paper abstract text from arXiv abs page."""
    title_match = re.search(r'<h1 class="title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ''

    authors_match = re.search(r'<div class="authors[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    authors = re.sub(r'<[^>]+>', '', authors_match.group(1)).strip() if authors_match else ''

    abstract_match = re.search(r'<blockquote class="abstract[^"]*"[^>]*>(.*?)</blockquote>', html, re.DOTALL)
    abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip() if abstract_match else ''

    subjects_match = re.search(r'<div class="metatable[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    subjects = re.sub(r'<[^>]+>', '', subjects_match.group(1)).strip() if subjects_match else ''

    parts = [p for p in [title, authors, abstract, subjects] if p]
    return '\n\n'.join(parts) if parts else html[:20000]


def call_a1(prompt: str, max_tokens: int = 8192, timeout: int = 180, retries: int = 0) -> dict:
    """Call the 8080 stable route and fall back to its fast route."""
    endpoints = [
        (A1_API, A1_MODEL),
        (FALLBACK_A1_API, FALLBACK_A1_MODEL),
    ]

    last_error = None
    for _ in range(retries + 1):
        for api_url, model in endpoints:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                api_url,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {A1_KEY}",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    res_body = response.read().decode("utf-8", errors="replace")
                data = json.loads(res_body)
                if "choices" not in data or not data["choices"]:
                    last_error = f"Invalid API response structure from {api_url}: {res_body[:200]}"
                    continue
                content = data["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"raw_result": content}
            except urllib.error.URLError as exc:
                last_error = f"Request failed on {api_url}: {exc}"
                continue
            except TimeoutError:
                last_error = f"timeout after {timeout}s on {api_url}"
                continue
            except Exception as exc:
                last_error = f"{api_url}: {exc}"
                continue

    return {"error": last_error or "All endpoints failed"}


def build_prompt(task: str, paper_id: str, input_content: str) -> str:
    """构造子Agent提示词，要求输出严格JSON"""
    
    if task == "code_analysis":
        return f"""你是一个资深静态代码审阅子Agent。分析论文 {paper_id} 的远程代码仓库。输入只来自 gread API，禁止声称读取、执行或测试了本地仓库。

输入内容：
{input_content}

审阅规则：
1. 先根据 coverage 判断仓库是完整实现、部分实现还是 README 占位仓库；不得把“存在 GitHub 链接”等同于“代码已发布”。
2. 必须以 source_files 中的具体源码为主要证据，README 只能用于核对作者声明和运行说明。
3. 交叉核对入口、导入路径、配置 target、类名、依赖清单和 README 命令，主动发现不一致。
4. 只写静态证据支持的结论。无法运行验证的内容标记为“疑似”或“无法确认”。
5. issues 中每项都给出文件/符号证据、影响和置信度；不得编造行号、tensor shape、性能或硬件数据。

请输出严格的JSON（不要markdown包裹，不要额外文字）：
{{
  "task": "code_analysis",
  "paper_id": "{paper_id}",
  "status": "done",
  "source": "gread",
  "repository_url": "GitHub URL",
  "repository_kind": "implementation/partial/placeholder/third_party/unknown",
  "analysis_scope": "gread 多轮静态分析；未执行代码",
  "summary": "仓库用途和实现完整度",
  "project_structure": "核心目录与职责，不复制完整目录树",
  "architecture": "基于源码的架构说明",
  "call_chain": "入口→数据→核心算法→输出",
  "modules": [
    {{
      "name": "模块名",
      "input": "能从源码确认的输入；未知则写未知",
      "output": "能从源码确认的输出；未知则写未知",
      "function": "功能描述",
      "evidence": "文件路径:类名或函数名"
    }}
  ],
  "framework": "pytorch/tensorflow/jax/other/unknown",
  "dependencies": ["直接依赖与外部工具"],
  "key_files": ["入口和核心算法文件"],
  "reproduction_readiness": "ready/needs_fixes/blocked/placeholder/unknown",
  "reproduction_steps": ["从仓库证据得到的最短复现链路"],
  "reproduction_blockers": ["数据、依赖、配置、代码问题"],
  "issues": [
    {{
      "severity": "blocker/high/medium/low",
      "finding": "问题描述",
      "evidence": ["文件路径:类名/函数/配置键"],
      "impact": "潜在影响",
      "confidence": 0.95
    }}
  ],
  "tests_present": false,
  "static_limitations": ["未执行代码，不能确认运行时兼容性或论文指标"],
  "confidence": 0.85
}}"""

    elif task == "algorithm_analysis":
        return f"""你是一个算法拆解子Agent。拆解论文 {paper_id} 的核心算法。

输入内容：
{input_content}

请输出严格的JSON（不要markdown包裹，不要额外文字）：
{{
  "task": "algorithm_analysis",
  "paper_id": "{paper_id}",
  "status": "done",
  "design_motivation": "为什么这样设计，vs替代方案",
  "loss_formula": "核心loss公式（LaTeX）",
  "math_principle": "数学原理说明",
  "tensor_flow": [
    {{"layer": "input", "shape": "[B,3,H,W]"}},
    {{"layer": "encoder", "shape": "[B,256]"}},
    {{"layer": "output", "shape": "[B,C]"}}
  ],
  "training_pipeline": [
    "step1: 数据加载",
    "step2: forward"
  ],
  "baselines_compared": ["Cellpose", "SAM"],
  "key_results": {{
    "metric1": "value1",
    "metric2": "value2"
  }},
  "confidence": 0.85
}}"""

    elif task == "reproduction":
        return f"""你是一个复现评估子Agent。评估论文 {paper_id} 的可复现性。

输入内容：
{input_content}

请输出严格的JSON（不要markdown包裹，不要额外文字）：
{{
  "task": "reproduction",
  "paper_id": "{paper_id}",
  "status": "done",
  "level": "A",
  "level_description": "A=一键运行, B=需要数据, C=需要修改, D=不可复现",
  "gpu_requirements": {{
    "min_vram_gb": 24,
    "gpu_count": 1,
    "gpu_type": "A100/RTX4090"
  }},
  "training_time_hours": null,
  "data_public": true,
  "data_source": "公开数据集名称或'未公开'",
  "dependencies": ["pytorch", "cuda11.8"],
  "pretrained_weights_available": true,
  "reproduction_steps": ["1. 下载数据", "2. 运行train.py"],
  "confidence": 0.85
}}"""

    elif task == "relevance_analysis":
        return f"""你是一个Cell AI论文相关性分类子Agent。判断论文 {paper_id} 是否属于Cell AI领域。

输入内容：
{input_content}

判断标准：
- 输入是否为显微镜/组织/细胞图像？
- 输出是否为细胞分割/检测/追踪/分类/计数/表示学习？
- 方法是否与Cell AI相关（SAM/ViT/transformer/U-Net/对比学习/自监督等）？

宁可误报不要漏报。不自信时判为通过。

请输出严格的JSON（不要markdown包裹，不要额外文字）：
{{
  "task": "relevance_analysis",
  "paper_id": "{paper_id}",
  "is_cell_ai": true,
  "domain": ["segmentation", "detection", "embedding", "tracking", "counting"],
  "confidence": 0.92,
  "reason": "简短说明为什么是/不是Cell AI",
  "status": "passed"
}}

如果 confidence < 0.8，status="failed"。"""

    elif task == "task_analysis":
        return f"""你是一个任务分类子Agent。分析论文 {paper_id} 属于哪个任务族。

输入内容：
{input_content}

请输出严格的JSON（不要markdown包裹，不要额外文字）：
{{
  "task": "task_analysis",
  "paper_id": "{paper_id}",
  "status": "done",
  "task_family": "cell_detection / cell_segmentation / cell_embedding / cell_tracking / spatial_biology / virtual_imaging / benchmark / multimodal / counting",
  "input": "模型输入类型",
  "output": "模型输出类型",
  "notable": "特殊说明",
  "task_type": ["detection", "segmentation", "embedding", "tracking", "counting", "spatial", "virtual_staining", "benchmark", "multimodal", "foundation_model"],
  "confidence": 0.85
}}"""

    elif task == "critic_analysis":
        return f"""你是一个论文批判子Agent（对抗式审查）。对论文 {paper_id} 进行严格的技术审查。

输入内容：
{input_content}

请输出严格的JSON（不要markdown包裹，不要额外文字）：
{{
  "task": "critic_analysis",
  "paper_id": "{paper_id}",
  "status": "done",
  "claimed_contribution": "论文声称的贡献",
  "actual_contribution": "实际做到的",
  "weakness": [
    "弱点1：方法缺陷",
    "弱点2：实验不足",
    "弱点3：对比不充分"
  ],
  "missing_experiments": [
    "缺少的消融实验",
    "缺少的基线对比"
  ],
  "overclaim": "是否有过度声称",
  "confidence": 0.8
}}"""

    else:
        return f"Task: {task}\nPaper: {paper_id}\nInput: {input_content}\n\n输出JSON格式分析结果。"


def main():
    parser = argparse.ArgumentParser(description="Cell AI 子Agent调度器")
    parser.add_argument("--task", required=True, choices=["relevance_analysis", "task_analysis", "code_analysis", "algorithm_analysis", "reproduction", "critic_analysis"])
    parser.add_argument("--paper_id", required=True)
    parser.add_argument("--input", required=True, help="输入文件或目录路径")
    parser.add_argument("--output", required=True, help="输出JSON文件路径")
    parser.add_argument("--priority", type=int, default=5)
    parser.add_argument("--retry", type=int, default=0, help="重试次数")
    parser.add_argument("--timeout", type=int, default=180, help="API超时秒数")
    args = parser.parse_args()

    input_content = load_input(args.input)
    prompt = build_prompt(args.task, args.paper_id, input_content)
    result = call_a1(prompt, timeout=args.timeout, retries=args.retry)

    if not isinstance(result, dict) or "error" in result:
        err_msg = result.get("error") if isinstance(result, dict) else "Unknown subagent failure"
        print(f"Subagent execution failed for {args.paper_id} [{args.task}]: {err_msg}", file=sys.stderr)
        return 1

    result["task"] = args.task
    result["paper_id"] = args.paper_id
    result["task_id"] = f"{args.paper_id}-{args.task}-v1"
    result["run_at"] = datetime.now().isoformat()
    result["priority"] = args.priority
    result["agent"] = A1_MODEL

    out_file = Path(args.output)
    output_path = out_file if out_file.is_absolute() else WORKDIR / out_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    temp_path.replace(output_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
