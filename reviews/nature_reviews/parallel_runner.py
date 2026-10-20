#!/usr/bin/env python3
"""Run multiple parallel workers to speed up remaining reviews."""
import json, os, subprocess, sys, time

WORKDIR = "/mnt/c/workspace/cell-ai-research"
OUT_DIR = os.path.join(WORKDIR, "reviews/nature_reviews")

def get_done():
    files = os.listdir(OUT_DIR)
    return set(f.replace('_review.json','') for f in files if f.endswith('_review.json'))

rest = json.load(open('/tmp/rest_ids.json'))
done = get_done()
remaining = [pid for pid in rest if pid not in done]
print(f"Total remaining: {len(remaining)} papers")

# Split into 4 chunks for 4 workers
num_workers = 2
chunk_size = (len(remaining) + num_workers - 1) // num_workers
chunks = [remaining[i*chunk_size:(i+1)*chunk_size] for i in range(num_workers)]

# Save per-worker manifests
for i, chunk in enumerate(chunks):
    json.dump(chunk, open(f'/tmp/worker_{i}_ids.json', 'w'))
    print(f"Worker {i}: {len(chunk)} papers")

# Launch workers as background subprocesses
procs = []
for i in range(num_workers):
    cmd = [sys.executable, "-c", f"""
import json, os, sys, time
sys.path.insert(0, '{OUT_DIR}')
from review_pipeline import review_single, load_paper, load_context, get_domain

ids = json.load(open('/tmp/worker_{i}_ids.json'))
for j, pid in enumerate(ids):
    out_path = os.path.join('{OUT_DIR}', f'{{pid}}_review.json')
    if os.path.exists(out_path): continue
    ctx = load_context(pid)
    domain = get_domain(load_paper(pid))
    try:
        res = review_single(pid, ctx, domain)
        json.dump(res, open(out_path, 'w'), ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'w{i} {{pid}} FAIL: {{e}}', flush=True)
    time.sleep(0.2)
print(f'Worker {i} done', flush=True)
"""]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    procs.append(p)
    print(f"Launched worker {i} (PID: {p.pid})")

# Monitor progress
start = time.time()
while True:
    d = len(get_done())
    pct = d * 100 // 239
    elapsed = int(time.time() - start)
    print(f"[{elapsed:3d}s] Total done: {d}/239 ({pct}%)", flush=True)
    if d >= 239:
        break
    # Check if all workers exited
    alive = sum(1 for p in procs if p.poll() is None)
    if alive == 0:
        print(f"All workers finished. Final count: {d}/239")
        break
    time.sleep(10)
