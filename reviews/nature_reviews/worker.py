#!/usr/bin/env python3
"""Parallel worker for Phase 2 single reviews. Consumes remaining IDs and processes them."""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(__file__))
from review_pipeline import review_single, load_paper, load_context, get_domain

WORKDIR = "/mnt/c/workspace/cell-ai-research"
OUT_DIR = os.path.join(WORKDIR, "reviews/nature_reviews")

def main():
    rest = json.load(open('/tmp/rest_ids.json'))
    done_set = set(os.listdir(OUT_DIR))
    done_set = {f.replace('_review.json','') for f in done_set if f.endswith('_review.json')}
    
    # Filter to remaining
    remaining = [pid for pid in rest if pid not in done_set]
    print(f"Worker {sys.argv[1]}: {len(remaining)} papers remaining")
    
    for i, pid in enumerate(remaining):
        if pid in done_set:
            continue
        ctx = load_context(pid)
        domain = get_domain(load_paper(pid))
        print(f"[{i+1}/{len(remaining)}] {pid}", end="", flush=True)
        try:
            result = review_single(pid, ctx, domain)
            out_path = os.path.join(OUT_DIR, f'{pid}_review.json')
            json.dump(result, open(out_path,'w'), ensure_ascii=False, indent=2)
            print(" done", flush=True)
        except Exception as e:
            print(f" FAILED: {e}", flush=True)
        time.sleep(0.3)
        done_set.add(pid)
    
    print(f"Worker {sys.argv[1]} finished")

if __name__ == "__main__":
    main()
