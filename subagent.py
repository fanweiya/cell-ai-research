#!/usr/bin/env python3
"""
subagent.py — Cell AI Research 子Agent 调度器
通过 Agents-A1 API 调用专用子Agent，输入输出均为JSON文件。

用法:
    python3 subagent.py --task code_analysis --paper_id 2607.04353 --input code/HASSL --output results/2607.04353_code.json
    python3 subagent.py --task algorithm_analysis --paper_id 2607.04353 --input papers/2607.04353.pdf --output results/2607.04353_algo.json
    python3 subagent.py --task reproduction --paper_id 2607.04353 --input results/2607.04353_code.json --output results/2607.04353_repro.json

参数:
    --task      : code_analysis / algorithm_analysis / reproduction
    --paper_id  : arXiv ID
    --input     : 输入文件或目录路径（代码目录、PDF路径、或前序结果JSON）
    --output    : 输出JSON文件路径
    --priority  : 优先级（可选，默认5）
"""

import sys
import json
import subprocess
import os
import argparse
from datetime import datetime

A1_API = os.environ.get('A1_API_URL', "http://10.0.0.245:8037/v1/chat/completions")
A1_KEY = os.environ.get('A1_API_KEY', 'qwe123qwe')
A1_MODEL = "Agents-A1"
WORKDIR = "/mnt/c/workspace/cell-ai-research"


def load_input(path: str) -> str:
    """加载输入内容：如果是文件则读内容，否则作为文本返回"""
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
    else:
        return path[:3000]


def call_a1(prompt: str, max_tokens: int = 8192) -> dict:
    """调用 Agents-A1 API"""
    payload = {
        "model": A1_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    cmd = [
        "curl", "-s", A1_API,
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {A1_KEY}",
        "-d", json.dumps(payload)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            return {"error": f"curl failed: {result.stderr}"}
        data = json.loads(result.stdout)
        content = data["choices"][0]["message"]["content"]
        # 尝试解析为JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_result": content}
    except subprocess.TimeoutExpired:
        return {"error": "timeout after 180s"}
    except Exception as e:
        return {"error": str(e)}


def build_prompt(task: str, paper_id: str, input_content: str) -> str:
    """构造子Agent提示词，要求输出严格JSON"""
    
    if task == "code_analysis":
        return f"""你是一个代码分析子Agent。分析论文 {paper_id} 的代码仓库。

输入内容：
{input_content}

请输出严格的JSON（不要markdown包裹，不要额外文字）：
{{
  "task": "code_analysis",
  "paper_id": "{paper_id}",
  "status": "done",
  "project_structure": "目录树描述",
  "architecture": "input→encoder→feature→decoder→output 流程图",
  "modules": [
    {{
      "name": "模块名",
      "input_shape": "tensor shape",
      "output_shape": "tensor shape",
      "function": "功能描述",
      "file": "文件名",
      "lines": "行号范围"
    }}
  ],
  "framework": "pytorch/tensorflow/jax",
  "key_files": ["model.py", "train.py"],
  "issues": [],
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