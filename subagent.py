#!/usr/bin/env python3
"""
subagent.py — Cell AI Research 子Agent 调度器
通过 Agents-A1 API 调用专用子Agent，输入输出均为JSON文件。

用法:
    python3 subagent.py --task code_analysis --paper_id 2607.04353 --input https://github.com/owner/repo --output results/2607.04353_code.json
    python3 subagent.py --task algorithm_analysis --paper_id 2607.04353 --input papers/2607.04353.pdf --output results/2607.04353_algo.json
    python3 subagent.py --task reproduction --paper_id 2607.04353 --input results/2607.04353_code.json --output results/2607.04353_repro.json

参数:
    --task      : code_analysis / algorithm_analysis / reproduction
    --paper_id  : arXiv ID
    --input     : arXiv ID、GitHub URL（由 gread 远程读取）或前序结果JSON
    --output    : 输出JSON文件路径
    --priority  : 优先级（可选，默认5）
"""

import sys
import json
import subprocess
import os
import re
import argparse
from datetime import datetime

A1_API = os.environ.get('A1_API_URL', "http://10.0.0.240:8080/v1/chat/completions")
A1_KEY = os.environ.get('A1_API_KEY', 'cell-ai')
A1_MODEL = os.environ.get('A1_MODEL', "stable")
FALLBACK_A1_API = os.environ.get('FALLBACK_A1_API_URL', A1_API)
FALLBACK_A1_MODEL = os.environ.get('FALLBACK_A1_MODEL', "fast")
WORKDIR = "/mnt/c/workspace/cell-ai-research"


def load_input(path: str) -> str:
    """加载输入内容；GitHub 仓库只能通过 gread 远程读取，禁止本地 clone。"""
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
    full_path = os.path.join(WORKDIR, path) if not path.startswith("/") else path
    if os.path.isfile(full_path):
        with open(full_path, 'r', errors='replace') as f:
            content = f.read()
        return content[:5000]
    elif os.path.isdir(full_path):
        # 列出目录结构
        lines = []
        for root, dirs, files in os.walk(full_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '.codegraph', '__pycache__', 'node_modules', '.github', 'dist', 'build']]
            level = root.replace(full_path, '').count(os.sep)
            indent = '  ' * level
            lines.append(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for file in files[:20]:
                lines.append(f"{subindent}{file}")
            if level > 3:
                dirs.clear()
        return "\n".join(lines[:50])
    elif re.match(r'^\d{4}\.\d{5}', path):
        # 是 arXiv ID，从 HTML 页面获取内容，智能提取正文
        arxiv_id = path.strip()
        try:
            result = subprocess.run(
                ["curl", "-sL", f"https://arxiv.org/html/{arxiv_id}"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout:
                html = result.stdout

                # 检查是否为 "No HTML" 错误页面
                if "No HTML for" in html or "HTML is not available" in html:
                    # 降级到 abs 页面
                    result2 = subprocess.run(
                        ["curl", "-sL", f"https://arxiv.org/abs/{arxiv_id}"],
                        capture_output=True, text=True, timeout=30
                    )
                    if result2.returncode == 0 and result2.stdout:
                        return _extract_abs_text(result2.stdout)
                    return path[:3000]

                # 提取论文正文（<article> 或 <body> 内的文本）
                text = _extract_article_text(html)
                if len(text) > 1000:
                    return text
                return html[:50000]
        except:
            pass
        return path[:3000]

    else:
        return path[:3000]


def _extract_article_text(html: str) -> str:
    """从 arXiv HTML 页面提取论文正文文本"""
    import re
    # 策略1：找 <article> 标签（arXiv HTML 论文的主体）
    match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if match:
        body = match.group(1)
    else:
        # 策略2：找 <body> 标签
        match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        body = match.group(1) if match else html

    # 去除脚本和样式
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)

    # 提取所有段落、标题、列表项的文本
    text_parts = re.findall(r'<(?:p|h\d|li|td|th|caption|div[^>]*class="[^"]*section[^"]*"[^>]*|div[^>]*class="[^"]*abstract[^"]*"[^>]*|div[^>]*class="[^"]*keywords[^"]*"[^>]*|h\d+)[^>]*>(.*?)</(?:p|h\d|li|td|th|caption|div|/?)', body, re.DOTALL)

    # 解析每个部分，提取纯文本
    lines = []
    for part in text_parts:
        # 去除所有标签
        clean = re.sub(r'<[^>]+>', '', part)
        # 去除多余空白
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean and len(clean) > 10:
            lines.append(clean)

    result = '\n\n'.join(lines)
    return result[:200000]  # 限制在 200K 字符（A1 上下文 262K tokens）


def _extract_abs_text(html: str) -> str:
    """从 arXiv abs 页面提取文本"""
    import re
    # 提取标题
    title_match = re.search(r'<h1 class="title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ''

    # 提取作者
    authors_match = re.search(r'<div class="authors[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    authors = re.sub(r'<[^>]+>', '', authors_match.group(1)).strip() if authors_match else ''

    # 提取摘要
    abstract_match = re.search(r'<blockquote class="abstract[^"]*"[^>]*>(.*?)</blockquote>', html, re.DOTALL)
    abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip() if abstract_match else ''

    # 提取分类/关键词
    subjects_match = re.search(r'<div class="metatable[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    subjects = re.sub(r'<[^>]+>', '', subjects_match.group(1)).strip() if subjects_match else ''

    parts = [p for p in [title, authors, abstract, subjects] if p]
    return '\n\n'.join(parts) if parts else html[:20000]

def call_a1(prompt: str, max_tokens: int = 8192) -> dict:
    """Call the 8080 stable route and fall back to its fast route."""
    endpoints = [
        (A1_API, A1_MODEL),
        (FALLBACK_A1_API, FALLBACK_A1_MODEL),
    ]
    
    last_error = None
    for api_url, model in endpoints:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        cmd = [
            "curl", "-s", api_url,
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {A1_KEY}",
            "-d", json.dumps(payload)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                last_error = f"curl failed on {api_url}: {result.stderr}"
                continue
            data = json.loads(result.stdout)
            if "choices" not in data or not data["choices"]:
                last_error = f"Invalid API response structure from {api_url}: {result.stdout[:200]}"
                continue
            content = data["choices"][0]["message"]["content"]
            # 尝试解析为JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_result": content}
        except subprocess.TimeoutExpired:
            last_error = f"timeout after 180s on {api_url}"
            continue
        except Exception as e:
            last_error = str(e)
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
    result = call_a1(prompt)

    # 添加元数据
    result["task"] = args.task
    result["paper_id"] = args.paper_id
    result["task_id"] = f"{args.paper_id}-{args.task}-v1"
    result["run_at"] = datetime.now().isoformat()
    result["priority"] = args.priority
    result["agent"] = A1_MODEL

    # 写入输出文件
    output_path = args.output if args.output.startswith("/") else os.path.join(WORKDIR, args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 也输出到stdout（主Agent可以读取）
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
