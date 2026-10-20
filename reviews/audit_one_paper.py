#!/usr/bin/env python3
"""Audit one paper: nature-statistics style statistical audit + ARS citation spot-check.
Usage: python3 audit_one_paper.py <arxiv_id> <output_json>"""
import sys, json, re, os

paper_id, out_path = sys.argv[1], sys.argv[2]
txt = open(f'/mnt/c/workspace/cell-ai-research/data/paper_context/{paper_id}.txt').read()

report = {"id": paper_id, "chars": len(txt)}

# ---------- nature-statistics style checks ----------
low = txt.lower()
checks = {
    "has_p_value": bool(re.search(r'p\s*[<=]\s*0?\.\d+|p-value', low)),
    "has_ci": bool(re.search(r'confidence interval|95%\s*ci|±|\+/-', low)),
    "has_std": bool(re.search(r'standard deviation|std\b|±', low)),
    "has_seeds_or_repeats": bool(re.search(r'three\s+(independent\s+)?(runs|seeds)|five\s+(runs|seeds)|n\s*=\s*[35]\s*(runs|seeds)|random\s+seed', low)),
    "has_significance_test": bool(re.search(r'wilcoxon|t-test|paired|anova|mann-whitney|kolmogorov|significance test|statistically significant', low)),
    "has_fdr": bool(re.search(r'benjamini|fdr|bonferroni|multiple comparison', low)),
    "mentions_ablation": 'ablation' in low,
    "mentions_dataset_split": bool(re.search(r'\d+:\d+:\d+|train.{0,20}val.{0,20}test|split', low)),
    "cell_count_as_n_risk": bool(re.search(r'\b\d{4,}\s+cells\b.*test|evaluated on \d{4,} cells', low)),
}
stat_issues = []
if not checks["has_p_value"]: stat_issues.append("P0: 全文无 p 值 / 显著性检验")
if not checks["has_std"] and not checks["has_ci"]: stat_issues.append("P0: 无标准差/置信区间（单点估计）")
if not checks["has_seeds_or_repeats"]: stat_issues.append("P1: 未报告多随机种子/重复实验")
if checks["has_significance_test"] and not checks["has_fdr"]: stat_issues.append("P2: 有检验但未见多重比较校正说明")
if checks["cell_count_as_n_risk"]: stat_issues.append("P1: 疑似将细胞数当作独立样本 n")
report["statistics"] = {"checks": checks, "issues": stat_issues,
                        "score": max(0, 10 - 4*sum(1 for i in stat_issues if i.startswith('P0')) - 2*sum(1 for i in stat_issues if i.startswith('P1')) - 1*sum(1 for i in stat_issues if i.startswith('P2')))}

# ---------- extract sample claims ----------
claims = re.findall(r'[^.]*(?:outperform|improv|surpass|achieves the best)[^.]*\.', low)[:3]
report["key_claims"] = [c.strip()[:200] for c in claims]

# ---------- reference spot-check (up to 8 real-looking refs w/ titles) ----------
refs_found = []
# try to find cited method names with known titles
KNOWN = {
 "cellpose": ("Cellpose: a generalist algorithm for cellular segmentation", "10.1038/s41592-020-01018-x"),
 "segment anything": ("Segment Anything", None),
 "sam ": ("Segment Anything", None),
 "stardist": ("Cell Detection with Star-Convex Polygons", "10.1007/978-3-030-00934-2_30"),
 "cellvit": ("CellViT: Vision Transformers for Precise Cell Segmentation and Classification", None),
 "dinov2": ("DINOv2: Learning Robust Visual Features without Supervision", None),
 "dinov3": ("DINOv3", None),
 "medsam": ("Segment Anything in Medical Images (MedSAM)", None),
 "hovernet": ("Hover-Net: Simultaneous segmentation and classification of nuclei in multi-tissue histology images", "10.1038/s41598-019-57214-4"),
 "unet": ("U-Net: Convolutional Networks for Biomedical Image Segmentation", "10.1007/978-3-319-24574-4_28"),
 "vit": ("An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale", None),
 "stardist": ("Cell Detection with Star-Convex Polygons", "10.1007/978-3-030-00934-2_30"),
}
for k,(t,d) in KNOWN.items():
    if k in low and len(refs_found) < 8:
        refs_found.append({"title": t, "doi": d})
report["ref_spotcheck_targets"] = refs_found
json.dump(report, open(out_path,'w'), indent=1, ensure_ascii=False)
print(f"OK {paper_id}: stat_score={report['statistics']['score']} issues={len(stat_issues)} refs={len(refs_found)}")
