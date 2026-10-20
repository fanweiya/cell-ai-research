#!/usr/bin/env python3
"""Generate final summary report from all Nature-style reviews."""
import json, os, re, glob
from collections import Counter, defaultdict

WORKDIR = "/mnt/c/workspace/cell-ai-research"
OUT = os.path.join(WORKDIR, "reviews/nature_reviews")

data = json.load(open(os.path.join(WORKDIR, 'papers.json')))['database']
papers_db = {re.sub(r'v\d+$','',str(p.get('arxiv_id',''))): p for p in data}

reviews = {}
for f in glob.glob(os.path.join(OUT, '*_review.json')):
    pid = os.path.basename(f).replace('_review.json','')
    reviews[pid] = json.load(open(f))

# Extract structured scores
results = []
for pid, r in reviews.items():
    meta = papers_db.get(pid, {})
    priority = meta.get('priority', 0) or 0
    research = meta.get('research_score', 0) or 0
    eng = meta.get('engineering_score', 0) or 0
    
    if 'synthesis' in r:
        # Triple-blind
        s = r['synthesis']
        n_blocking = len(s.get('consensus_blocking_concerns',[]))
        n_other = len(s.get('other_major_concerns',[]))
        reviewers = r.get('reviewers',[])
        total_concerns = sum(len(rv.get('concerns',[])) for rv in reviewers)
        # Count by severity across all reviewers
        severity_count = Counter()
        for rv in reviewers:
            for c in rv.get('concerns',[]):
                sev = c.get('severity','minor')
                severity_count[sev] += 1
        # Count by axis
        axis_count = Counter()
        for rv in reviewers:
            for c in rv.get('concerns',[]):
                axis_count[c.get('axis','?')] += 1
        rec = s.get('overall_recommendation', 'Unknown')
        # Compute quality score (higher = better paper)
        n_major = severity_count.get('major', 0)
        n_minor = severity_count.get('minor', 0)
        quality = max(0, 10 - n_major * 2 - n_minor * 0.5)
        review_type = "triple_blind"
    else:
        # Single review
        concerns = r.get('concerns',[])
        severity_count = Counter(c.get('severity','minor') for c in concerns)
        axis_count = Counter(c.get('axis','?') for c in concerns)
        n_major = severity_count.get('major', 0)
        n_minor = severity_count.get('minor', 0)
        n_blocking = sum(1 for c in concerns if c.get('blocking'))
        n_other = 0
        total_concerns = len(concerns)
        rec = r.get('recommendation_posture', 'Unknown')
        quality = max(0, 10 - n_major * 2 - n_minor * 0.5)
        review_type = "single"
    
    results.append({
        "id": pid,
        "title": str(meta.get('title',''))[:100],
        "priority": priority,
        "research": research,
        "eng": eng,
        "review_type": review_type,
        "recommendation": rec,
        "total_concerns": total_concerns,
        "n_major": n_major,
        "n_minor": n_minor,
        "n_blocking": n_blocking,
        "n_other": n_other,
        "severity_count": dict(severity_count),
        "axis_count": dict(axis_count),
        "quality_score": round(quality, 1),
        "key_issues": []
    })

# Get key blocking concerns for top papers
for pid, r in reviews.items():
    if 'synthesis' in r:
        s = r.get('synthesis', {})
        issues = [c.get('concern','')[:120] for c in s.get('consensus_blocking_concerns',[])]
        for res in results:
            if res['id'] == pid:
                res['key_issues'] = issues
                break
    else:
        concerns = r.get('concerns',[])
        blocking = [c.get('concern','')[:120] for c in concerns if c.get('blocking')]
        for res in results:
            if res['id'] == pid:
                res['key_issues'] = blocking
                break

# Sort by quality descending
results.sort(key=lambda x: -x['quality_score'])

# Statistics
total = len(results)
rec_dist = Counter(r['recommendation'] for r in results)
quality_dist = Counter(int(r['quality_score']) for r in results)
axis_all = Counter()
for r in results:
    for k, v in r['axis_count'].items():
        axis_all[k] += v

print(f"Total papers reviewed: {total}")
print(f"Recommendation distribution: {dict(rec_dist)}")
print(f"Quality score distribution: {dict(sorted(quality_dist.items()))}")
print(f"Axis distribution (total concern counts): {dict(axis_all.most_common(10))}")
print()
print("=== Top 10 (highest quality) ===")
for r in results[:10]:
    print(f"  [{r['quality_score']:4.1f}] {r['id']} | {r['review_type']} | {r['recommendation']} | {r['n_major']}M/{r['n_minor']}m | {r['title'][:60]}")
print()
print("=== Bottom 10 (lowest quality) ===")
for r in results[-10:]:
    print(f"  [{r['quality_score']:4.1f}] {r['id']} | {r['review_type']} | {r['recommendation']} | {r['n_major']}M/{r['n_minor']}m | {r['title'][:60]}")

# Save full data
json.dump(results, open(os.path.join(OUT, 'all_reviews_ranked.json'), 'w'), ensure_ascii=False, indent=2)
print(f"\nSaved all_reviews_ranked.json")
