#!/usr/bin/env python3
"""批量补跑缺失的 research analysis 阶段（task/algorithm/critic）。

用法:
    python3 backfill_analysis.py [--dry-run]
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

WORKDIR = "/mnt/c/workspace/cell-ai-research"
PAPERS_FILE = os.path.join(WORKDIR, "papers.json")
RESULTS_DIR = os.path.join(WORKDIR, "results")
SUBAGENT = os.path.join(WORKDIR, "subagent.py")
PY = sys.executable

# 文件名里 stage 的规范化
STAGE_ALIAS = {
    "algo": "algorithm_analysis",
    "critic": "critic_analysis",
}


def scan_existing_results():
    """扫描 results 目录，返回 {pid: {stage: filepath}}"""
    paper_stages = {}
    for f in os.listdir(RESULTS_DIR):
        if not f.endswith(".json"):
            continue
        base = f[:-5]
        m = re.match(r"((?:\d{4}\.\d{4,5}|biorxiv:\S+?)v\d+)_(.+)", base)
        if not m:
            continue
        pid = m.group(1)
        stage = STAGE_ALIAS.get(m.group(2), m.group(2))
        if stage not in ("task_analysis", "algorithm_analysis", "critic_analysis",
                         "code_analysis", "reproduction", "relevance_analysis"):
            continue
        paper_stages.setdefault(pid, {})[stage] = os.path.join(RESULTS_DIR, f)
    return paper_stages


def needs_analysis(paper, stage, existing):
    status = paper.get("status", {})
    if status.get(stage) in ("done", "error", "skipped"):
        return False
    pid = paper["arxiv_id"]
    if pid in existing and stage in existing.get(pid, {}):
        # 已有结果文件但状态没回填 → 直接标记 done，不重跑
        return "backfill"
    return "run"


def main():
    silent_only = "--silent-only" in sys.argv
    dry_run = "--dry-run" in sys.argv
    papers_data = json.load(open(PAPERS_FILE, "r", encoding="utf-8"))
    existing = scan_existing_results()

    # 先做"已有结果但状态 pending"的静默回填
    backfilled = 0
    for paper in papers_data["database"]:
        status = paper.get("status", {})
        pid = paper["arxiv_id"]
        if pid in existing:
            for stage in ("task_analysis", "algorithm_analysis", "critic_analysis"):
                if stage in existing[pid] and status.get(stage) == "pending":
                    status[stage] = "done"
                    backfilled += 1
        paper["status"] = status

    if silent_only:
        if not dry_run and backfilled:
            json.dump(papers_data, open(PAPERS_FILE, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        print(f"✅ 静默回填 {backfilled} 个已有结果的状态 (silent-only)")
        return

    # 收集真正需要补跑的
    stages_order = ["task_analysis", "algorithm_analysis", "critic_analysis"]
    todo = []
    for paper in papers_data["database"]:
        if paper.get("relevance") != "passed":
            continue
        pid = paper["arxiv_id"]
        status = paper.get("status", {})
        for stage in stages_order:
            if status.get(stage) == "pending":
                prio = paper.get("priority") or 5
                todo.append((pid, stage, prio))

    # 按优先级排序
    todo.sort(key=lambda x: (-x[2], stages_order.index(x[1])))

    if dry_run:
        print(f"[dry-run] 可静默回填: {backfilled}")
        print(f"[dry-run] 需要补跑: {len(todo)} 个任务")
        for pid, stage, prio in todo[:20]:
            print(f"  {pid} {stage} (priority={prio})")
        return

    # 静默回填保存
    json.dump(papers_data, open(PAPERS_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"✅ 静默回填 {backfilled} 个已有结果的状态")

    print(f"需要补跑 {len(todo)} 个分析任务（串行执行）")
    ok = fail = 0
    for i, (pid, stage, prio) in enumerate(todo, 1):
        output = os.path.join(RESULTS_DIR, f"{pid}_{stage}.json")
        cmd = [PY, SUBAGENT, "--task", stage, "--paper_id", pid,
               "--input", pid, "--output", output, "--priority", str(prio),
               "--retry", "1", "--timeout", "180"]
        print(f"[{i}/{len(todo)}] {pid} {stage} ...", flush=True)
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            # subagent 成功与否看输出文件
            if os.path.exists(output):
                data = json.load(open(output, encoding="utf-8"))
                if data.get("status") == "done":
                    ok += 1
                    # 立即回填状态
                    for paper in papers_data["database"]:
                        if paper["arxiv_id"] == pid:
                            paper.setdefault("status", {})[stage] = "done"
                            break
                    json.dump(papers_data, open(PAPERS_FILE, "w", encoding="utf-8"),
                              ensure_ascii=False, indent=2)
                    print(f"    ✓ done ({time.time()-t0:.0f}s)")
                else:
                    fail += 1
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
