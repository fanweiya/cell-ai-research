"""
Jev System One (v2) Paper Evaluator for cell-ai-research

Implements rigorous 4-dimensional paper evaluation with verifiable provenance,
evidence sufficiency validation, explicit code status verification, and robust failure propagation.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

TYPESAFE_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
RULE_VERSION = "2026.10.v2"
PINNED_MODEL = "jev-1.14.0"

# 项目根目录从脚本位置推导，可用 CELL_AI_PROJECT 覆盖；
# 不再把 /mnt/c 绝对路径写进代码，换机器或换目录时自动跟随。
PROJECT_DIR = Path(os.environ.get("CELL_AI_PROJECT", Path(__file__).resolve().parent))
load_dotenv(PROJECT_DIR / ".env")

# 通道定义：按延迟与稳定性优先级排序 (TypeSafe Jev -> Codiv OpenJev -> SubQ -> Cloudflare Clef)
EVAL_CHANNELS = [
    {
        "name": "typesafe",
        "endpoint": "https://api.typesafe.ai/v1/systemone",
        "default_model": "jev-preview",
        "key_env": "TYPESAFE_API_KEY",
        "extra_headers": {"TypeSafe-Danger-Zone-Images": "true"},
    },
    {
        "name": "codiv",
        "endpoint": "https://api.codiv.ai/v1/systemone",
        "default_model": "openjev-latest",
        "key_env": "CODIV_API_KEY",
        "extra_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"},
    },
    {
        "name": "subq",
        "endpoint": "https://api.subq.ai/v1/systemone",
        "default_model": "subq-snap-1.1",
        "key_env": "SUBQ_API_KEY",
        "extra_headers": {},
    },
    {
        "name": "cloudflare",
        "endpoint": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/cloudflare/clef-flash",
        "default_model": "clef-flash",
        "key_env": "CF_API_TOKEN",
        "extra_headers": {},
    },
]

# Dimensional Criteria - refined to eliminate arbitrary mathematical proofs / production requirements
SCORE_CRITERIA_NOVELTY = [
    "1: Routine baseline application with standard tooling",
    "2: Very minor baseline adjustment without methodological change",
    "3: Incremental engineering tweak on existing frameworks",
    "4: Minor architectural extension with modest novelty",
    "5: Solid practical solution solving a specific task",
    "6: Effective domain-adapted methodology with notable improvements",
    "7: Distinct creative methodological breakthrough overcoming key bottleneck",
    "8: Highly innovative algorithmic formulation with clear paradigm advance",
    "9: Exceptional breakthrough opening new imaging/analysis capabilities",
    "10: Groundbreaking paradigm shift establishing new foundational standard"
]

SCORE_CRITERIA_SOUNDNESS = [
    "1: Lacks baseline comparisons or contains fatal methodological flaws",
    "2: Very weak experimental validation with questionable claims",
    "3: Minimal baselines, missing ablation studies or error discussions",
    "4: Basic experimental verification with noticeable gaps",
    "5: Standard benchmarks evaluated with reasonable controls and comparisons",
    "6: Solid experimental design with appropriate ablation studies and baselines",
    "7: Rigorous validation across multiple datasets with thorough control experiments",
    "8: Strict spatial or cross-domain hold-out evaluation with comprehensive ablations",
    "9: Extensive blind testing across instruments, noise regimes, and clinical/wet-lab conditions",
    "10: Exemplary technical soundness with zero data leakage, exhaustive baselines, and statistical rigor"
]

SCORE_CRITERIA_UTILITY = [
    "1: Negligible practical relevance to real biological research",
    "2: Artificial toy setup disconnected from real laboratory needs",
    "3: Narrow niche applicability with high barrier to adoption",
    "4: Modest utility under restricted experimental conditions",
    "5: Useful tool for routine laboratory analysis pipelines",
    "6: Tangibly improves resolution, throughput, or accuracy in real workflows",
    "7: High biological impact solving genuine wet-lab/microscopy pain points",
    "8: Substantially reduces experimental costs or enables new biology assays",
    "9: Transformative practical impact broadly adoptable across microscopy/spatial omics",
    "10: Redefines scientific imaging capability across biological sciences"
]

SCORE_CRITERIA_REPRO = [
    "1: Proprietary code and private data, completely non-reproducible",
    "2: Stated availability but no accessible repository or instructions found",
    "3: Minimal skeleton repository lacking preprocessing or model weights",
    "4: Partial codebase with complex undocumented dependencies",
    "5: Complete code provided with basic environment instructions",
    "6: Runnable implementation with documented reproduction steps and data preparation",
    "7: Well-structured repository with pretrained weights, sample data, and reproduction scripts",
    "8: Clean modular codebase with verified source implementation and automated smoke tests",
    "9: Fully documented open-source scientific package with tutorials and verified pipelines",
    "10: Gold-standard open reproducibility with one-click end-to-end containerized pipelines"
]

PARADIGM_CRITERIA = {
    "physical_amortization": "Embedding physical imaging optics and inverse problem redundancy into fast neural inference",
    "multimodal_foundation": "Cross-modal biological vision-language pretraining and open-set cellular representation",
    "cross_scale_spatial_omics": "Bridging histology morphology and single-cell/spatial molecular transcriptomics",
    "synthetic_to_real": "Procedural simulation and domain-randomized synthetic data driving zero-shot real transfer",
    "mechanistic_interpretability": "Cellular communication and microenvironmental graph distillation for clinical explainability",
    "efficient_architecture": "State-space modeling (Mamba) and gradient-adaptive distillation for extreme efficiency",
    "agentic_evaluation": "Evaluating and benchmarking AI agents on complex end-to-end bioimage workflows",
    "incremental_baseline": "Standard model adaptation, parameter tuning, or incremental benchmark evaluation"
}

PARADIGM_LABELS_ZH = {
    "physical_amortization": "物理先验融合",
    "multimodal_foundation": "显微多模态基础模型",
    "cross_scale_spatial_omics": "跨尺度空间组学",
    "synthetic_to_real": "仿真向真实迁移",
    "mechanistic_interpretability": "机制级可解释性",
    "efficient_architecture": "轻量架构与蒸馏",
    "agentic_evaluation": "智能体系统评测",
    "incremental_baseline": "常规方法迁移"
}


def verify_code_status(paper: dict) -> tuple[str, str, dict]:
    """
    Distinguish between:
    - '实现已确认': verified repository ownership and actual source files present
    - '作者声明': paper statement mentions code, but source implementation not yet verified
    - '候选未确认': url exists in metadata but not provenanced/verified
    - '未提供代码': no repository claimed or found
    """
    gh = paper.get("status", {}).get("github", {})
    if not isinstance(gh, dict):
        gh = {}
    gh_url = gh.get("url") or ""
    provenance = gh.get("provenance")
    code_analysis = paper.get("code_analysis") or {}
    has_impl = code_analysis.get("has_implementation") or code_analysis.get("source_coverage", {}).get("has_implementation")

    details = {
        "url": gh_url,
        "provenance": provenance,
        "code_files": code_analysis.get("source_coverage", {}).get("code_file_count_in_tree"),
        "tests_present": code_analysis.get("source_coverage", {}).get("tests_present")
    }

    if gh_url and has_impl:
        return "实现已确认", f"源码已核验：{gh_url} (代码文件数: {details['code_files'] or '已检出'})", details
    elif gh_url and provenance == "paper_code_statement":
        return "作者声明", f"作者声明开源：{gh_url} (源码实现尚未核验)", details
    elif gh_url:
        return "候选未确认", f"发现候选仓库链接：{gh_url} (归属与实现尚未核验)", details
    else:
        return "未提供代码", "论文未提供或未检索到开源代码仓库", details


def extract_evidence(paper: dict, context_dir: Path = PROJECT_DIR / "data" / "paper_context") -> dict:
    aid = paper.get("arxiv_id", "")
    base_id = aid.split("v")[0]
    txt_path = context_dir / f"{base_id}.txt"
    full_text = ""
    if txt_path.exists():
        try:
            full_text = txt_path.read_text(encoding="utf-8")
        except Exception:
            pass

    abstract = paper.get("abstract_summary") or paper.get("abstract") or ""
    code_status, code_desc, code_details = verify_code_status(paper)

    evidence_snippets = {}
    sources = []

    # 1. Abstract
    if abstract:
        evidence_snippets["abstract"] = abstract[:1500].strip()
        sources.append("abstract")

    # 2. Full text sections if available
    has_full_text = bool(full_text and len(full_text) > 500)
    if has_full_text:
        sources.append(f"full_text:{txt_path.name}")
        sec_patterns = {
            "method": [r"\b(?:proposed\s+method|methodology|methods|our\s+approach|architecture)\b"],
            "experiment": [r"\b(?:experiments?|experimental\s+setup|evaluation\s+protocol|datasets?\s+and\s+evaluation)\b"],
            "results": [r"\b(?:results?|ablation\s+studies?|quantitative\s+results)\b"],
            "conclusion": [r"\b(?:conclusion|discussion|biological\s+implications?)\b"],
            "reproducibility": [r"\b(?:code\s+(?:and\s+data\s+)?availability|data\s+availability|reproducibility\s+statement|software\s+availability|implementation\s+details?)\b"]
        }
        for sec, pats in sec_patterns.items():
            for pat in pats:
                m = re.search(pat, full_text, re.IGNORECASE)
                if m:
                    evidence_snippets[sec] = full_text[m.start():m.start() + 600].strip()
                    break

    # 3. Code evidence
    evidence_snippets["code"] = code_desc
    if code_details.get("url"):
        sources.append(f"github:{code_details['url']}")

    # Check evidence sufficiency per dimension strictly based on extracted evidence
    sufficiency = {
        "methodological_novelty": bool(evidence_snippets.get("abstract") or evidence_snippets.get("method")),
        "technical_soundness": bool(evidence_snippets.get("experiment") or evidence_snippets.get("results")),
        "biological_utility": bool(evidence_snippets.get("abstract") or evidence_snippets.get("conclusion")),
        "reproducibility_readiness": bool(code_status == "实现已确认" or evidence_snippets.get("reproducibility"))
    }

    evidence_text = (
        f"Title: {paper.get('title', '')}\n"
        f"Tasks: {', '.join(paper.get('task_type', []) if isinstance(paper.get('task_type'), list) else [str(paper.get('task_type'))])}\n"
        f"Code Status: {code_status} ({code_desc})\n\n"
        f"[Abstract Evidence]\n{evidence_snippets.get('abstract', 'None')}\n\n"
        f"[Method Evidence]\n{evidence_snippets.get('method', 'Full text method section not extracted')}\n\n"
        f"[Experimental Evidence]\n{evidence_snippets.get('experiment', 'Full text experimental setup not extracted')}\n\n"
        f"[Results & Ablation Evidence]\n{evidence_snippets.get('results', 'Full text results/ablations not extracted')}\n\n"
        f"[Conclusion & Biological Implications]\n{evidence_snippets.get('conclusion', 'Full text conclusion not extracted')}\n\n"
        f"[Reproducibility & Implementation Materials]\n{evidence_snippets.get('reproducibility', 'Full text reproducibility materials not extracted')}"
    )

    evidence_hash = hashlib.sha256(evidence_text.encode("utf-8")).hexdigest()

    return {
        "code_status": code_status,
        "code_desc": code_desc,
        "evidence_snippets": evidence_snippets,
        "evidence_sources": sources,
        "evidence_sufficiency": sufficiency,
        "all_sufficient": all(sufficiency.values()),
        "evidence_text": evidence_text,
        "evidence_hash": evidence_hash
    }


def build_evaluation_payload(paper: dict, evidence_info: dict, model: str = PINNED_MODEL) -> tuple[dict, list[str]]:
    questions = {}
    asked_dimensions = []
    sufficiency = evidence_info["evidence_sufficiency"]

    if sufficiency["methodological_novelty"]:
        questions["methodological_novelty"] = {
            "type": "score",
            "instructions": "Rate methodological creativity and novelty relative to closest baselines from 1 to 10.",
            "criteria": SCORE_CRITERIA_NOVELTY
        }
        asked_dimensions.append("methodological_novelty")

    if sufficiency["technical_soundness"]:
        questions["technical_soundness"] = {
            "type": "score",
            "instructions": "Rate technical soundness (controls, data splits, ablations, statistical support) from 1 to 10.",
            "criteria": SCORE_CRITERIA_SOUNDNESS
        }
        asked_dimensions.append("technical_soundness")

    if sufficiency["biological_utility"]:
        questions["biological_utility"] = {
            "type": "score",
            "instructions": "Rate biological utility and real-world domain impact from 1 to 10.",
            "criteria": SCORE_CRITERIA_UTILITY
        }
        asked_dimensions.append("biological_utility")

    if sufficiency["reproducibility_readiness"]:
        questions["reproducibility_readiness"] = {
            "type": "score",
            "instructions": "Rate reproducibility and code/data implementation readiness from 1 to 10.",
            "criteria": SCORE_CRITERIA_REPRO
        }
        asked_dimensions.append("reproducibility_readiness")

    # Paradigm choice is always queried
    questions["primary_paradigm"] = {
        "type": "choice",
        "instructions": "Classify the primary core innovation mechanism of this paper.",
        "criteria": PARADIGM_CRITERIA
    }

    payload = {
        "model": model,
        "state": evidence_info["evidence_text"],
        "questions": questions
    }
    return payload, asked_dimensions


def format_evaluation_result(answers: dict, asked_dims: list[str], evidence_info: dict, model_name: str = PINNED_MODEL) -> dict:
    scores = {}
    confidences = {}
    raw_answers = {}

    # Strict validation per asked dimension
    for dim in asked_dims:
        ans = answers.get(dim)
        if not ans or not isinstance(ans, dict):
            raise ValueError(f"Missing required response field for {dim}")
        raw_score = ans.get("score")
        conf = ans.get("confidence")
        if raw_score is None or not isinstance(raw_score, (int, float)):
            raise ValueError(f"Invalid or missing score for {dim}: {raw_score}")
        if not (0.0 <= raw_score <= 9.0):
            raise ValueError(f"Score for {dim} out of bounds [0, 9]: {raw_score}")
        if conf is None or not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
            raise ValueError(f"Confidence for {dim} out of bounds [0, 1]: {conf}")

        scores[dim] = round(raw_score + 1.0, 2)
        confidences[dim] = round(conf, 3)
        raw_answers[dim] = ans

    # Unasked dimensions explicitly mapped to None
    all_dims = ["methodological_novelty", "technical_soundness", "biological_utility", "reproducibility_readiness"]
    for dim in all_dims:
        if dim not in scores:
            scores[dim] = None
            confidences[dim] = None

    # Paradigm validation
    paradigm_ans = answers.get("primary_paradigm")
    if not isinstance(paradigm_ans, dict):
        raise ValueError(f"primary_paradigm 返回结构异常: {type(paradigm_ans).__name__}")
    paradigm_choice = paradigm_ans.get("choice")
    if not paradigm_choice or paradigm_choice not in PARADIGM_CRITERIA:
        raise ValueError(f"primary_paradigm choice 缺失或不在合法范围内: {paradigm_choice!r}")
    paradigm_conf = paradigm_ans.get("confidence")
    if paradigm_conf is None or not isinstance(paradigm_conf, (int, float)) or not (0.0 <= paradigm_conf <= 1.0):
        raise ValueError(f"primary_paradigm confidence 缺失或不在 [0, 1] 范围内: {paradigm_conf}")

    raw_answers["primary_paradigm"] = paradigm_ans

    # Compute formal composite score: requires all 4 dimensions
    if all(scores[d] is not None for d in all_dims):
        composite = round(
            0.35 * scores["methodological_novelty"] +
            0.25 * scores["technical_soundness"] +
            0.25 * scores["biological_utility"] +
            0.15 * scores["reproducibility_readiness"],
            2
        )
    else:
        composite = None

    # Abstract preliminary score (based on novelty + utility when available)
    abstract_preliminary_score = None
    if scores["methodological_novelty"] is not None and scores["biological_utility"] is not None:
        abstract_preliminary_score = round(0.55 * scores["methodological_novelty"] + 0.45 * scores["biological_utility"], 2)

    return {
        "rule_version": RULE_VERSION,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "model": model_name,
        "evidence_hash": evidence_info.get("evidence_hash", ""),
        "evidence_sources": evidence_info.get("evidence_sources", []),
        "code_status": evidence_info.get("code_status", "none"),
        "code_desc": evidence_info.get("code_desc", ""),
        "evidence_sufficiency": evidence_info.get("evidence_sufficiency", "abstract_only"),
        "scores": scores,
        "confidences": confidences,
        "primary_paradigm": paradigm_choice,
        "paradigm_label_zh": PARADIGM_LABELS_ZH.get(paradigm_choice, "常规方法迁移"),
        "paradigm_confidence": round(paradigm_conf, 3),
        "composite_priority": composite,
        "abstract_preliminary_score": abstract_preliminary_score,
        "raw_answers": raw_answers
    }


def resolve_channel_config(channel: dict) -> tuple[str | None, str, str, dict]:
    name = channel.get("name", "")
    key = channel.get("default_key")
    if name == "subq":
        key = key or os.environ.get("SUBQ_API_KEY")
        model = channel.get("default_model") or os.environ.get("SUBQ_MODEL", "subq-snap-1.1")
        endpoint = channel.get("endpoint", "https://api.subq.ai/v1/systemone")
    elif name == "typesafe":
        key = key or os.environ.get("JEV_API_KEY") or os.environ.get("TYPESAFE_API_KEY")
        model = channel.get("default_model") or os.environ.get("TYPESAFE_MODEL", "jev-preview")
        endpoint = channel.get("endpoint", "https://api.typesafe.ai/v1/systemone")
    elif name == "codiv":
        key = key or os.environ.get("CODIV_API_KEY")
        model = channel.get("default_model") or os.environ.get("CODIV_MODEL", "openjev-latest")
        endpoint = channel.get("endpoint", "https://api.codiv.ai/v1/systemone")
    elif name == "cloudflare":
        key = key or os.environ.get("CF_API_TOKEN")
        model = channel.get("default_model") or os.environ.get("CF_CLEF_MODEL", "clef-flash")
        account_id = os.environ.get("CF_ACCOUNT_ID") or channel.get("account_id", "b9b1998c78f49ed2e0db3ab8e868ff85")
        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/cloudflare/{model}"
    else:
        key_env = channel.get("key_env")
        key = key or (os.environ.get(key_env) if key_env else None)
        model = channel.get("default_model", PINNED_MODEL)
        endpoint = channel.get("endpoint", TYPESAFE_ENDPOINT)

    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    headers.update(channel.get("extra_headers", {}))
    return key, model, endpoint, headers


def evaluate_single_paper(
    paper: dict,
    api_key: str | None = None,
    retries: int = 2,
    evidence_info: dict | None = None,
    channels: list[dict] | None = None
) -> dict:
    if evidence_info is None:
        evidence_info = extract_evidence(paper)

    active_channels = channels if channels is not None else EVAL_CHANNELS
    channel_errors = []

    for channel in active_channels:
        ch_name = channel.get("name", "unknown")
        key, model, endpoint, headers = resolve_channel_config(channel)
        if api_key and ch_name == "typesafe":
            key = api_key
            headers["Authorization"] = f"Bearer {key}"

        if not key:
            channel_errors.append(f"[{ch_name}] missing credentials")
            continue

        payload, asked_dims = build_evaluation_payload(paper, evidence_info, model=model)
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        for attempt in range(retries):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=body,
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
            except Exception as exc:
                channel_errors.append(f"[{ch_name} attempt {attempt+1}] {exc}")
                if attempt == retries - 1:
                    print(f"[Warning] Channel {ch_name} failed for {paper.get('arxiv_id')}: {exc}", file=sys.stderr)
                time.sleep(1.0 * (attempt + 1))
                continue

            if ch_name == "cloudflare" and isinstance(resp_data, dict) and "result" in resp_data:
                eval_data = resp_data.get("result", {})
            else:
                eval_data = resp_data

            answers = eval_data.get("answers", {})
            model_name = eval_data.get("model", model)
            return format_evaluation_result(answers, asked_dims, evidence_info, model_name=model_name)

    raise RuntimeError(f"All evaluation channels failed for {paper.get('arxiv_id')}: {'; '.join(channel_errors)}")


def run_batch_evaluation(
    db_path: str = str(PROJECT_DIR / "papers.json"),
    max_workers: int = 6,
    force: bool = False,
    limit: int | None = None,
    channels: list[dict] | None = None
) -> int:
    active_channels = channels if channels is not None else EVAL_CHANNELS
    ready_channels = [str(ch.get("name", "unknown")) for ch in active_channels if resolve_channel_config(ch)[0]]
    if not ready_channels:
        print("[Error] No evaluation channels have available credentials.", file=sys.stderr)
        raise RuntimeError("No evaluation channels have available credentials")

    print(f"Available evaluation channels: {', '.join(ready_channels)}")

    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    papers = db.get("database", [])

    # Filter candidates: check force, rule_version, and evidence_hash
    candidates = []
    for p in papers:
        if p.get("relevance") != "passed":
            continue
        ev = p.get("jev_evaluation")
        curr_ev_info = extract_evidence(p)
        # If not force and already evaluated with current rule_version, identical evidence_hash and identical sufficiency, skip
        if (
            not force
            and ev
            and ev.get("rule_version") == RULE_VERSION
            and ev.get("evidence_hash") == curr_ev_info["evidence_hash"]
            and ev.get("evidence_sufficiency") == curr_ev_info["evidence_sufficiency"]
        ):
            continue
        candidates.append((p, curr_ev_info))

    if limit:
        candidates = candidates[:limit]

    total_candidates = len(candidates)
    print(f"Total papers to evaluate with Jev (Rule Version: {RULE_VERSION}): {total_candidates}")
    if total_candidates == 0:
        return 0

    evaluated_count = 0
    failed_count = 0
    save_batch_size = 10

    def process_item(item_tuple):
        item, ev_info = item_tuple
        try:
            ev = evaluate_single_paper(item, evidence_info=ev_info, channels=active_channels)
            return item, ev, None
        except Exception as exc:
            return item, None, exc

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_item, cand): cand[0] for cand in candidates}
        for future in concurrent.futures.as_completed(futures):
            item, ev, exc = future.result()
            if ev:
                # Archive old evaluation if any relevant field changed
                old_ev = item.get("jev_evaluation")
                if old_ev and (
                    old_ev.get("rule_version") != RULE_VERSION
                    or old_ev.get("evidence_hash") != ev.get("evidence_hash")
                    or old_ev.get("evidence_sufficiency") != ev.get("evidence_sufficiency")
                ):
                    item["legacy_jev_evaluation"] = old_ev
                
                item["jev_evaluation"] = ev

                # Formal composite score
                comp = ev["composite_priority"]
                if comp is not None:
                    item["research_score"] = round(comp, 1)
                    # Priority is strictly integer without arbitrary code +2
                    item["priority"] = int(round(comp))
                else:
                    item["research_score"] = None
                    item["priority"] = 0

                evaluated_count += 1
                if evaluated_count % 5 == 0 or evaluated_count == total_candidates:
                    print(f"[{evaluated_count}/{total_candidates}] Evaluated {item.get('arxiv_id')} -> {comp or 'N/A'}/10 ({ev['code_status']} | {ev['paradigm_label_zh']})")
                
                # Periodic checkpoint save
                if evaluated_count % save_batch_size == 0:
                    _atomic_json(db_path, db)
            else:
                failed_count += 1
                print(f"[Failure] Item {item.get('arxiv_id')} failed: {exc}", file=sys.stderr)

    # Final writeback
    _atomic_json(db_path, db)

    print(f"Successfully evaluated and updated {evaluated_count} papers (failed: {failed_count}).")
    if failed_count > 0:
        raise RuntimeError(f"Jev evaluation failed for {failed_count}/{total_candidates} papers")
    return evaluated_count


def _atomic_json(path: str | Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Jev System One Paper Evaluator for cell-ai-research")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers to evaluate")
    parser.add_argument("--force", action="store_true", help="Force re-evaluation of already evaluated papers")
    parser.add_argument("--workers", type=int, default=6, help="Concurrent workers")
    args = parser.parse_args()

    count = run_batch_evaluation(max_workers=args.workers, force=args.force, limit=args.limit)
