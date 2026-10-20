#!/usr/bin/env python3
"""Run full Nature-style review pipeline for all 239 papers.
Top 11 (priority>=14): triple blind review (R1/R2/R3 + synthesis)
Rest 227: deep single review
Then: citation-verify spot-check on all.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(__file__))
from review_pipeline import (
    review_top_paper, review_single, load_paper, load_context, get_domain
)

WORKDIR = "/mnt/c/workspace/cell-ai-research"
OUT_DIR = os.path.join(WORKDIR, "reviews/nature_reviews")
os.makedirs(OUT_DIR, exist_ok=True)

top11 = json.load(open('/tmp/top11_ids.json'))
rest = json.load(open('/tmp/rest_ids.json'))

def already_done(pid):
    return os.path.exists(os.path.join(OUT_DIR, f'{pid}_review.json'))

# Phase 1: Top 11 triple blind
print(f"=== PHASE 1: Top 11 Triple Blind Reviews ===")
top_done, top_fail = 0, []
for i, pid in enumerate(top11):
    if already_done(pid):
        print(f"[{i+1}/11] {pid} - SKIP (already done)")
        top_done += 1
        continue
    paper = load_paper(pid)
    ctx = load_context(pid)
    domain = get_domain(paper)
    print(f"[{i+1}/11] {pid} (domain={domain}, ctx={len(ctx)} chars)")
    try:
        result = review_top_paper(pid, ctx, domain)
        out_path = os.path.join(OUT_DIR, f'{pid}_review.json')
        json.dump(result, open(out_path,'w'), ensure_ascii=False, indent=2)
        top_done += 1
        print(f"  -> saved {out_path}")
    except Exception as e:
        top_fail.append((pid, str(e)))
        print(f"  -> FAILED: {e}")
    time.sleep(1)

print(f"\nPhase 1 complete: {top_done}/11 done, {len(top_fail)} failed")
if top_fail:
    print("Failed:", top_fail)

# Phase 2: Rest 227 single review
print(f"\n=== PHASE 2: {len(rest)} Single Reviews ===")
single_done, single_fail = 0, []
for i, pid in enumerate(rest):
    if already_done(pid):
        single_done += 1
        if (i+1) % 50 == 0:
            print(f"[{i+1}/{len(rest)}] progress: {single_done} done, {len(single_fail)} failed")
        continue
    paper = load_paper(pid)
    ctx = load_context(pid)
    domain = get_domain(paper)
    print(f"[{i+1}/{len(rest)}] {pid} (domain={domain})", end="")
    try:
        result = review_single(pid, ctx, domain)
        out_path = os.path.join(OUT_DIR, f'{pid}_review.json')
        json.dump(result, open(out_path,'w'), ensure_ascii=False, indent=2)
        single_done += 1
    except Exception as e:
        single_fail.append((pid, str(e)))
        print(f" FAILED: {e}")
    time.sleep(0.5)
    if (i+1) % 20 == 0:
        print(f"  ** progress: {single_done} done, {len(single_fail)} failed **")

print(f"\nPhase 2 complete: {single_done}/{len(rest)} done, {len(single_fail)} failed")
if single_fail:
    print("Failed:", [f[0] for f in single_fail[:10]])

# Phase 3: Summary
total = top_done + single_done + 1  # +1 for EffiCell-Seg already done
print(f"\n=== TOTAL: {total}/239 papers reviewed ===")
print(f"Top triple-blind: {top_done}/11")
print(f"Single reviews: {single_done}/{len(rest)}")
print(f"EffiCell-Seg: 1 (already done)")
if top_fail or single_fail:
    all_fail = top_fail + single_fail
    json.dump(all_fail, open(os.path.join(OUT_DIR, 'failed.json'),'w'))
    print(f"Failed list saved to failed.json ({len(all_fail)} papers)")
