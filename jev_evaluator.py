import concurrent.futures
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Ensure hermes_switchyard and agent imports work
SWITCHYARD_PATH = "/home/fanweiya/.hermes/plugins/hermes-switchyard"
if SWITCHYARD_PATH not in sys.path:
    sys.path.insert(0, SWITCHYARD_PATH)

from agent.secret_scope import get_secret

TYPESAFE_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

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
    "5: Standard benchmarks evaluated with reasonable controls",
    "6: Solid experimental design with appropriate ablation studies",
    "7: Rigorous validation across multiple datasets with thorough controls",
    "8: Strict spatial/cross-domain hold-out with comprehensive ablations",
    "9: Extensive blind testing across instruments, noise regimes, and conditions",
    "10: Exemplary technical soundness with mathematical proofs and zero-leakage rigor"
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
    "9: Transformative practical impact broadly adoptable across microscopy/omics",
    "10: Redefines scientific imaging capability across biological sciences"
]

SCORE_CRITERIA_REPRO = [
    "1: Proprietary code and private data, completely non-reproducible",
    "2: Stated availability but no accessible repository or instructions",
    "3: Minimal skeleton repository lacking preprocessing and model weights",
    "4: Partial codebase with complex undocumented dependencies",
    "5: Code provided with basic environment instructions",
    "6: Runnable implementation with documented reproduction steps",
    "7: Well-structured repository with pretrained weights and demo data",
    "8: Clean modular codebase with automated setup and verification tests",
    "9: Production-ready open-source package with full documentation and tutorials",
    "10: Gold-standard open reproducibility with one-click end-to-end pipelines"
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


def build_evaluation_payload(paper: dict) -> dict:
    title = paper.get("title", "")
    abstract = paper.get("abstract_summary") or paper.get("abstract") or ""
    task_types = paper.get("task_type", [])
    if isinstance(task_types, list):
        tasks_str = ", ".join(task_types)
    else:
        tasks_str = str(task_types)
    
    gh = paper.get("status", {}).get("github", {})
    if not isinstance(gh, dict):
        gh = {}
    has_code = bool(paper.get("has_code") or gh.get("has_code") or gh.get("url"))
    code_desc = f"Open Source Code Available at {gh.get('url')}" if has_code else "No public code repository verified"

    state_text = (
        f"Title: {title}\n"
        f"Tasks: {tasks_str}\n"
        f"Code Status: {code_desc}\n"
        f"Abstract Excerpt: {abstract[:1200]}"
    )

    return {
        "model": "jev-latest",
        "state": state_text,
        "questions": {
            "methodological_novelty": {
                "type": "score",
                "instructions": "Rate methodological creativity and novelty from 1 (routine baseline) to 10 (paradigm shift).",
                "criteria": SCORE_CRITERIA_NOVELTY
            },
            "technical_soundness": {
                "type": "score",
                "instructions": "Rate technical soundness and experimental evidence from 1 (unsupported) to 10 (exemplary rigor).",
                "criteria": SCORE_CRITERIA_SOUNDNESS
            },
            "biological_utility": {
                "type": "score",
                "instructions": "Rate practical biological utility and real-world imaging impact from 1 (toy) to 10 (transformative).",
                "criteria": SCORE_CRITERIA_UTILITY
            },
            "reproducibility_readiness": {
                "type": "score",
                "instructions": "Rate reproducibility and engineering implementation readiness from 1 (closed) to 10 (gold standard).",
                "criteria": SCORE_CRITERIA_REPRO
            },
            "primary_paradigm": {
                "type": "choice",
                "instructions": "Classify the primary core innovation mechanism of this paper.",
                "criteria": PARADIGM_CRITERIA
            }
        }
    }


def evaluate_single_paper(paper: dict, api_key: str, retries: int = 3) -> dict | None:
    payload = build_evaluation_payload(paper)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        TYPESAFE_ENDPOINT,
        data=body,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        }
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                answers = data.get("answers", {})
                
                # Extract scores
                nov_raw = answers.get("methodological_novelty", {}).get("score", 4.0)
                sou_raw = answers.get("technical_soundness", {}).get("score", 4.0)
                uti_raw = answers.get("biological_utility", {}).get("score", 4.0)
                rep_raw = answers.get("reproducibility_readiness", {}).get("score", 4.0)

                nov_score = round(nov_raw + 1.0, 1)
                sou_score = round(sou_raw + 1.0, 1)
                uti_score = round(uti_raw + 1.0, 1)
                rep_score = round(rep_raw + 1.0, 1)

                nov_conf = answers.get("methodological_novelty", {}).get("confidence", 0.0)
                sou_conf = answers.get("technical_soundness", {}).get("confidence", 0.0)
                uti_conf = answers.get("biological_utility", {}).get("confidence", 0.0)
                rep_conf = answers.get("reproducibility_readiness", {}).get("confidence", 0.0)

                paradigm_choice = answers.get("primary_paradigm", {}).get("choice", "incremental_baseline")
                paradigm_conf = answers.get("primary_paradigm", {}).get("confidence", 0.0)

                # Composite score
                composite = round(0.35 * nov_score + 0.25 * sou_score + 0.25 * uti_score + 0.15 * rep_score, 2)

                return {
                    "evaluated_at": datetime.now(timezone.utc).isoformat(),
                    "model": data.get("model", "jev-1.14.0"),
                    "scores": {
                        "methodological_novelty": nov_score,
                        "technical_soundness": sou_score,
                        "biological_utility": uti_score,
                        "reproducibility_readiness": rep_score
                    },
                    "confidences": {
                        "methodological_novelty": nov_conf,
                        "technical_soundness": sou_conf,
                        "biological_utility": uti_conf,
                        "reproducibility_readiness": rep_conf
                    },
                    "primary_paradigm": paradigm_choice,
                    "paradigm_label_zh": PARADIGM_LABELS_ZH.get(paradigm_choice, "常规方法迁移"),
                    "paradigm_confidence": paradigm_conf,
                    "composite_priority": composite
                }
        except Exception as exc:
            if attempt == retries - 1:
                print(f"[Error] Failed to evaluate {paper.get('arxiv_id')}: {exc}", file=sys.stderr)
                return None
            time.sleep(1.0 * (attempt + 1))
    return None


def run_batch_evaluation(db_path: str = "/mnt/c/workspace/cell-ai-research/papers.json", max_workers: int = 6, force: bool = False, limit: int | None = None) -> int:
    api_key = get_secret("TYPESAFE_API_KEY")
    if not api_key:
        print("[Error] TYPESAFE_API_KEY is not available.", file=sys.stderr)
        return 0

    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    papers = db.get("database", [])
    
    # Filter candidates
    candidates = []
    for p in papers:
        if p.get("relevance") != "passed":
            continue
        if not force and p.get("jev_evaluation") and p.get("jev_evaluation", {}).get("composite_priority"):
            continue
        candidates.append(p)

    if limit:
        candidates = candidates[:limit]

    total_candidates = len(candidates)
    print(f"Total papers to evaluate with Jev: {total_candidates}")
    if total_candidates == 0:
        return 0

    evaluated_count = 0
    save_batch_size = 10

    def process_item(item):
        ev = evaluate_single_paper(item, api_key)
        return item, ev

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_item, p): p for p in candidates}
        for future in concurrent.futures.as_completed(futures):
            item, ev = future.result()
            if ev:
                item["jev_evaluation"] = ev
                # Also synchronize top-level priority and research score
                item["research_score"] = round(ev["composite_priority"], 1)
                bonus_code = 2.0 if item.get("has_code") else 0.0
                item["priority"] = round(ev["composite_priority"] + bonus_code, 1)
                evaluated_count += 1
                if evaluated_count % 5 == 0 or evaluated_count == total_candidates:
                    print(f"[{evaluated_count}/{total_candidates}] Evaluated {item.get('arxiv_id')} -> {ev['composite_priority']}/10 ({ev['paradigm_label_zh']})")
                
                # Periodic checkpoint save
                if evaluated_count % save_batch_size == 0:
                    with open(db_path, "w", encoding="utf-8") as out_f:
                        json.dump(db, out_f, ensure_ascii=False, indent=2)

    # Final writeback
    with open(db_path, "w", encoding="utf-8") as out_f:
        json.dump(db, out_f, ensure_ascii=False, indent=2)

    print(f"Successfully evaluated and updated {evaluated_count} papers.")
    return evaluated_count


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Jev System One Paper Evaluator for cell-ai-research")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers to evaluate")
    parser.add_argument("--force", action="store_true", help="Force re-evaluation of already evaluated papers")
    parser.add_argument("--workers", type=int, default=6, help="Concurrent workers")
    args = parser.parse_args()

    run_batch_evaluation(max_workers=args.workers, force=args.force, limit=args.limit)
