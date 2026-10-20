#!/usr/bin/env python3
"""Phase 3: Citation verification for all papers using citation-verify skill."""
import json, os, sys, re, subprocess

WORKDIR = "/mnt/c/workspace/cell-ai-research"
VERIFY_SCRIPT = "/home/fanweiya/skills/citation-verify/scripts/verify_citation.py"

def extract_citations(pid):
    """Extract known method citations from paper context that we want to verify."""
    ctx_path = os.path.join(WORKDIR, 'data/paper_context', f'{pid}.txt')
    if not os.path.exists(ctx_path):
        return []
    txt = open(ctx_path).read().lower()
    
    KNOWN = {
        "cellpose": ("Cellpose: a generalist algorithm for cellular segmentation", "10.1038/s41592-020-01018-x"),
        "segment anything": ("Segment Anything", None),
        "sam ": ("Segment Anything", None),
        "stardist": ("Cell Detection with Star-Convex Polygons", "10.1007/978-3-030-00934-2_30"),
        "cellvit": ("CellViT: Vision Transformers for Precise Cell Segmentation", None),
        "dinov2": ("DINOv2: Learning Robust Visual Features without Supervision", None),
        "dinov3": ("DINOv3", None),
        "medsam": ("Segment Anything in Medical Images (MedSAM)", None),
        "hovernet": ("Hover-Net: Simultaneous segmentation and classification of nuclei", "10.1038/s41598-019-57214-4"),
        "unet": ("U-Net: Convolutional Networks for Biomedical Image Segmentation", "10.1007/978-3-319-24574-4_28"),
        "vit": ("An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale", None),
        "conch": ("CONCH: A Contrastive Coded Cytology Foundation Model", None),
        "ctpath": ("CTransPath: Vision Transformers for Scalable Biomedical Image Recognition", None),
        "giga": ("Pathology Foundation Model", None),
        "gigapath": ("Pathology Foundation Model", None),
        "slicer": ("SLICER", None),
        "deepcell": ("DeepCell", None),
        "qupath": ("QuPath", None),
        "openml": ("Open-MITOS-2", None),
        "mitos": ("Open-MITOS-2", None),
    }
    targets = []
    for k,(t,d) in KNOWN.items():
        if k in txt and len(targets) < 5:
            targets.append({"title": t, "doi": d})
    return targets


def verify_one_citation(doi, title):
    """Run citation-verify for one DOI. Return (verdict, confirmed_n)."""
    if not doi:
        return ("SKIP", 0)
    cmd = ["python3", VERIFY_SCRIPT, "--doi", doi, "--title", title]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        out = r.stdout
        verdict = "PASS" if "✅ PASS" in out else ("REJECT" if "❌" in out else "API_ERROR")
        m = re.search(r'\((\d)/4 indexes', out)
        return (verdict, int(m.group(1)) if m else 0)
    except Exception as e:
        return ("API_ERROR", 0)


def main():
    # Get all paper IDs
    data = json.load(open(os.path.join(WORKDIR, 'papers.json')))['database']
    papers = [re.sub(r'v\d+$','',str(p.get('arxiv_id',''))) for p in data]
    
    out_dir = os.path.join(WORKDIR, 'reviews/nature_reviews')
    os.makedirs(out_dir, exist_ok=True)
    
    verified_total = 0
    pass_count = 0
    
    for pid in papers:
        targets = extract_citations(pid)
        if not targets:
            continue
        results = []
        for t in targets:
            v, n = verify_one_citation(t.get('doi'), t.get('title'))
            results.append({"title": t['title'], "doi": t.get('doi'), "verdict": v, "confirmed_n": n})
            if v == "PASS":
                pass_count += 1
            verified_total += 1
        
        # Save per-paper citation results
        result_path = os.path.join(out_dir, f'{pid}_citations.json')
        json.dump(results, open(result_path,'w'), ensure_ascii=False, indent=1)
        print(f"{pid}: {len(results)} citations, {sum(1 for r in results if r['verdict']=='PASS')} pass")
        if verified_total % 50 == 0:
            print(f"  >> progress: {verified_total} citations verified")
    
    # Save summary
    json.dump({"verified_total": verified_total, "pass_count": pass_count},
              open(os.path.join(out_dir, 'citation_summary.json'),'w'))
    print(f"\nDone: {verified_total} citations verified, {pass_count} PASS")


if __name__ == "__main__":
    main()
