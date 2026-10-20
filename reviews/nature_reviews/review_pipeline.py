#!/usr/bin/env python3
"""
Nature-style review pipeline for cell-ai-research papers.
Calls local A1 model at :8080 for reviewer generation.
No subagents. Pure Python + curl.
"""
import subprocess, json, re, os, sys, time

WORKDIR = "/mnt/c/workspace/cell-ai-research"
A1_API = "http://10.0.0.240:8080/v1/chat/completions"
A1_KEY = "cell-ai"
A1_MODEL = "stable"

def call_a1(messages, max_tokens=4000, timeout=120):
    payload = {
        "model": A1_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl","-s","--max-time",str(timeout), A1_API,
                 "-H","Content-Type: application/json",
                 "-H",f"Authorization: Bearer {A1_KEY}",
                 "-d", json.dumps(payload)],
                capture_output=True, text=True, timeout=timeout+15
            )
            if r.returncode == 0:
                d = json.loads(r.stdout)
                content = d['choices'][0]['message']['content']
                # Strip markdown code fence if present
                m = re.search(r'```json?\s*\n?(.*?)\n?```', content, re.DOTALL)
                if m: content = m.group(1)
                return json.loads(content)
        except Exception as e:
            print(f"  attempt {attempt+1} failed: {e}", file=sys.stderr)
            time.sleep(2)
    return {"error": "all attempts failed"}


def build_reviewer_prompt(paper_id, paper_text, role, domain, emphasis):
    return f"""你是 Nature Methods 期刊的资深审稿人，专长领域：{domain}。对以下论文进行 {emphasis} 视角的方法论审视。

== 论文全文（已截断至核心内容） ==
{paper_text}
== 论文全文结束 ==

你扮演 Reviewer {role}，侧重 {emphasis}。请独立给出严格、有据可查的审稿意见。

规则：
1. 每个 concern 必须有：ID（{role}-M1..N）、severity（major/minor）、blocking（true/false）、axis（methodology/statistics/generalizability/citation/interpretability）、claim_pointer（论文具体声称了什么）、concern（具体问题）、why_it_matters（为什么是问题）、resolution_test（需要什么实验/分析解决）
2. 不要虚构行号或数据
3. 必须基于论文实际内容，不要泛泛而谈
4. 不要与其他审稿人共享视角

请只输出严格 JSON，不要 markdown 包裹，不要多余文字：
{{
  "paper_id": "{paper_id}",
  "reviewer_role": "{role}",
  "emphasis": "{emphasis}",
  "overall_assessment": "总体评价，100-200字，聚焦你负责的侧重点",
  "strengths": ["优势1", "优势2", "优势3"],
  "concerns": [
    {{
      "id": "{role}-M1",
      "severity": "major",
      "blocking": true,
      "axis": "methodology",
      "claim_pointer": "论文声称了什么（引用具体表述）",
      "concern": "具体问题",
      "why_it_matters": "为什么构成问题",
      "resolution_test": "需要什么来验证/解决"
    }}
  ],
  "assessment_boundaries": ["无法评估的方面", "缺失材料影响"],
  "recommendation_posture": "Major Revision|Minor Revision|Accept|Reject",
  "confidence": 0.8
}}"""


def build_synthesis_prompt(paper_id, r1, r2, r3):
    return f"""你是期刊主编，综合以下三位独立审稿人的审稿意见，生成事后综合报告。不要改写审稿人的独立意见。

Reviewer 1: {json.dumps(r1, ensure_ascii=False)[:3000]}

Reviewer 2: {json.dumps(r2, ensure_ascii=False)[:3000]}

Reviewer 3: {json.dumps(r3, ensure_ascii=False)[:3000]}

请输出严格 JSON，不要 markdown：
{{
  "paper_id": "{paper_id}",
  "synthesis": true,
  "consensus_strengths": ["三位共同认可的优势"],
  "consensus_blocking_concerns": [{{
    "concern": "综合意见",
    "independently_raised_by": ["R1","R2","R3"]
  }}],
  "other_major_concerns": [{{
    "concern": "只有部分审稿人提出的问题",
    "raised_by": ["R1","R2"]
  }}],
  "minor_revision_checklist": ["具体可修改项"],
  "most_important_issues": ["投稿前必须解决的核心问题"],
  "overall_recommendation": "Major Revision|Minor Revision|Accept|Reject"
}}"""


def build_single_review_prompt(paper_id, paper_text, domain):
    return f"""你是 Nature 期刊的资深审稿人，对以下细胞 AI 论文（领域：{domain}）进行深度单审。覆盖四个评估轴：方法论、统计报告、泛化性、引用真实性。

== 论文全文（已截断至核心内容） ==
{paper_text}
== 论文全文结束 ==

请输出严格 JSON，不要 markdown：
{{
  "paper_id": "{paper_id}",
  "task": "single_review",
  "overall_assessment": "总体评价，100-200字",
  "strengths": ["优势1", "优势2"],
  "concerns": [
    {{
      "id": "S-M1",
      "severity": "major",
      "blocking": true,
      "axis": "methodology|statistics|generalizability|citation",
      "claim_pointer": "论文声称了什么",
      "concern": "具体问题",
      "why_it_matters": "为什么是问题",
      "resolution_test": "需要什么来验证"
    }}
  ],
  "assessment_boundaries": ["无法评估的方面"],
  "recommendation_posture": "Major Revision|Minor Revision|Accept|Reject",
  "confidence": 0.8
}}"""


def review_top_paper(paper_id, paper_text, domain):
    """Three independent reviewers + synthesis for top-tier papers."""
    print(f"  Reviewer R1...", end="", flush=True)
    r1 = call_a1([
        {"role": "user", "content": build_reviewer_prompt(paper_id, paper_text, "R1", domain, "方法论设计与算法创新（关注架构合理性、动机是否充分、消融是否完备）")}
    ], max_tokens=4000)
    time.sleep(1)
    print(f" R2...", end="", flush=True)
    r2 = call_a1([
        {"role": "user", "content": build_reviewer_prompt(paper_id, paper_text, "R2", domain, "统计严谨性与实验设计（关注样本量、误差报告、显著性检验、多随机种子、泛化交叉验证）")}
    ], max_tokens=4000)
    time.sleep(1)
    print(f" R3...", end="", flush=True)
    r3 = call_a1([
        {"role": "user", "content": build_reviewer_prompt(paper_id, paper_text, "R3", domain, "生物学泛化性与引用真实性（关注跨数据集泛化、数据集多样性、参考文献是否支持核心论断）")}
    ], max_tokens=4000)
    print(f" Synthesis...", end="", flush=True)
    synthesis = call_a1([
        {"role": "user", "content": build_synthesis_prompt(paper_id, r1, r2, r3)}
    ], max_tokens=2000)
    print(" done")
    return {"reviewers": [r1, r2, r3], "synthesis": synthesis}


def review_single(paper_id, paper_text, domain):
    """Single deep review for standard-tier papers."""
    print(f"  Reviewing...", end="", flush=True)
    result = call_a1([
        {"role": "user", "content": build_single_review_prompt(paper_id, paper_text, domain)}
    ], max_tokens=3500)
    print(" done")
    return result


def get_domain(paper):
    task_type = paper.get('task_type', [])
    if isinstance(task_type, list):
        return ','.join(task_type[:3])
    return 'cell_ai'


def load_paper(paper_id):
    """Find paper metadata and context."""
    data = json.load(open(os.path.join(WORKDIR, 'papers.json')))
    db = data.get('database', data)
    for p in db:
        clean = re.sub(r'v\d+$', '', str(p.get('arxiv_id','')))
        if clean == paper_id:
            return p
    return {}


def load_context(paper_id):
    ctx_path = os.path.join(WORKDIR, 'data/paper_context', f'{paper_id}.txt')
    if os.path.exists(ctx_path):
        with open(ctx_path) as f:
            txt = f.read()
        return txt[:30000]  # cap at 30K chars
    return ""


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: review_pipeline.py <paper_id> <mode>")
        print("  mode: 'top' for triple blind review, 'single' for deep single review")
        sys.exit(1)
    
    paper_id = sys.argv[1]
    mode = sys.argv[2]
    paper = load_paper(paper_id)
    paper_text = load_context(paper_id)
    domain = get_domain(paper)
    
    print(f"=== Reviewing {paper_id} (mode={mode}, domain={domain}) ===")
    print(f"  Context: {len(paper_text)} chars")
    
    if mode == 'top':
        result = review_top_paper(paper_id, paper_text, domain)
    else:
        result = review_single(paper_id, paper_text, domain)
    
    # Save
    out_dir = os.path.join(WORKDIR, 'reviews/nature_reviews')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{paper_id}_review.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {out_path}")
    print("  DONE")
