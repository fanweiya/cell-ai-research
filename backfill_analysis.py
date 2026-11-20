import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

WORKDIR = Path(os.environ.get("CELL_AI_WORKDIR", str(Path(__file__).resolve().parent)))
PAPERS_FILE = WORKDIR / "papers.json"
RESULTS_DIR = WORKDIR / "results"
SUBAGENT = WORKDIR / "subagent.py"
PY = sys.executable

STAGE_ALIAS = {
    "algo": "algorithm_analysis",
    "critic": "critic_analysis",
}


def scan_existing_results():
    paper_stages = {}
    if not os.path.isdir(RESULTS_DIR):
        return {}
    for f in os.listdir(RESULTS_DIR):
        if not f.endswith(".json"):
            continue
        base = f[:-5]
        m = re.match(r"((?:\d{4}\.\d{4,5}|biorxiv:\S+?)(?:v\d+)?)_(.+)", base)
        if not m:
            continue
        pid = m.group(1)
        stage = STAGE_ALIAS.get(m.group(2), m.group(2))
        if stage not in ("task_analysis", "algorithm_analysis", "critic_analysis",
                         "code_analysis", "reproduction", "relevance_analysis"):
            continue
        file_path = os.path.join(RESULTS_DIR, f)
        try:
            with open(file_path, "r", encoding="utf-8") as rf:
                content = json.load(rf)
            if not isinstance(content, dict) or "error" in content:
                continue
            if content.get("status") not in ("done", "passed", "completed"):
                continue
        except (json.JSONDecodeError, OSError):
            continue
        paper_stages.setdefault(pid, {})[stage] = file_path
    return paper_stages


def needs_analysis(paper, stage, existing):
    status = paper.get("status") or {}
    if status.get(stage) == "done":
        return False
    pid = paper.get("arxiv_id", "")
    if pid in existing and stage in existing.get(pid, {}):
        return "backfill"
    if status.get(stage) in ("error", "skipped"):
        return False
    return "run"


def save_papers_atomic(data):
    temp_file = Path(PAPERS_FILE).with_suffix(f".tmp.{os.getpid()}")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp_file.replace(PAPERS_FILE)


def build_todo_tasks(papers_data, existing):
    stages_order = ["task_analysis", "algorithm_analysis", "critic_analysis"]
    todo = []
    for paper in papers_data.get("database", []):
        if paper.get("relevance") != "passed":
            continue
        pid = paper["arxiv_id"]
        status = paper.setdefault("status", {})
        jev = paper.get("jev_evaluation") or {}
        comp_score = jev.get("composite_priority")
        raw_score = float(comp_score) if comp_score is not None else 0.0
        p = paper.get("priority")
        prio = p if isinstance(p, int) and not isinstance(p, bool) else int(round(raw_score))
        for stage in stages_order:
            if needs_analysis(paper, stage, existing) == "run" and status.get(stage) == "pending":
                todo.append((pid, stage, prio, raw_score))

    # Sort primarily by raw composite score descending, then stage order, then paper id
    todo.sort(key=lambda x: (-x[3], stages_order.index(x[1]), x[0]))
    return todo


def main():
    silent_only = "--silent-only" in sys.argv
    dry_run = "--dry-run" in sys.argv
    papers_data = json.load(open(PAPERS_FILE, "r", encoding="utf-8"))
    existing = scan_existing_results()

    backfilled = 0
    for paper in papers_data["database"]:
        status = paper.setdefault("status", {})
        pid = paper["arxiv_id"]
        if pid in existing:
            for stage in ("task_analysis", "algorithm_analysis", "critic_analysis"):
                if stage in existing[pid] and status.get(stage) != "done":
                    status[stage] = "done"
                    backfilled += 1

    if silent_only:
        if not dry_run and backfilled:
            save_papers_atomic(papers_data)
        print(f"✅ 静默回填 {backfilled} 个已有结果的状态 (silent-only)")
        return

    todo = build_todo_tasks(papers_data, existing)

    if dry_run:
        print(f"[dry-run] 可静默回填: {backfilled}")
        print(f"[dry-run] 需要补跑: {len(todo)} 个任务")
        for pid, stage, prio, raw_score in todo[:20]:
            print(f"  {pid} {stage} (score={raw_score:.2f}, priority={prio})")
        return

    save_papers_atomic(papers_data)
    print(f"✅ 静默回填 {backfilled} 个已有结果的状态")

    print(f"需要补跑 {len(todo)} 个分析任务（串行执行）")
    ok = fail = 0
    for i, (pid, stage, prio, raw_score) in enumerate(todo, 1):
        output = os.path.join(RESULTS_DIR, f"{pid}_{stage}.json")
        cmd = [PY, str(SUBAGENT), "--task", stage, "--paper_id", pid,
               "--input", pid, "--output", output, "--priority", str(prio),
               "--retry", "1", "--timeout", "180"]
        print(f"[{i}/{len(todo)}] {pid} {stage} ...", flush=True)
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if os.path.exists(output):
                data = json.load(open(output, encoding="utf-8"))
                if data.get("status") == "done":
                    ok += 1
                    for paper in papers_data["database"]:
                        if paper["arxiv_id"] == pid:
                            paper.setdefault("status", {})[stage] = "done"
                            break
                    save_papers_atomic(papers_data)
                    print(f"    ✓ done ({time.time()-t0:.0f}s)")
                else:
                    fail += 1
                    try:
                        os.unlink(output)
                    except OSError:
                        pass
                    print(f"    ✗ 结果文件无 done 状态: {data.get('status')}")
            else:
                fail += 1
                print(f"    ✗ 无输出文件, rc={r.returncode}, err={r.stderr[:200]}")
        except Exception as e:
            fail += 1
            print(f"    ✗ 异常: {e}")
        time.sleep(0.5)

    print(f"\n完成: 成功 {ok}, 失败 {fail}")


if __name__ == "__main__":
    main()
