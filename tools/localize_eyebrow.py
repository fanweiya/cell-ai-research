"""把图解页页头的英文任务代码换成中文，再重新渲染。"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLAINERS = ROOT / "explainers"
RENDER = ROOT / "tools" / "visual-explainer" / "plugins" / "visual-explainer" / "kit" / "render.mjs"

LABELS = {
    "segmentation": "分割",
    "cell_segmentation": "细胞分割",
    "classification": "分类",
    "histopathology": "组织病理",
    "detection": "检测",
    "cell_imaging": "细胞成像",
    "reconstruction": "重建",
    "spatial_transcriptomics": "空间转录组",
    "tracking": "追踪",
    "virtual_imaging": "虚拟成像",
    "virtual_staining": "虚拟染色",
    "pathology": "病理",
    "diagnosis": "诊断",
    "multimodal": "多模态",
    "video": "视频",
    "spatial": "空间",
    "spatial_biology": "空间生物学",
    "foundation_model": "基础模型",
    "foundation_models": "基础模型",
    "benchmark": "基准评测",
    "counting": "计数",
    "representation_learning": "表征学习",
    "representation": "表征学习",
    "integration": "整合",
    "3d_imaging": "三维成像",
    "self_supervised": "自监督",
    "active_learning": "主动学习",
    "few_shot_learning": "小样本学习",
    "microscopy": "显微成像",
    "weakly_supervised": "弱监督",
    "embedding": "嵌入",
    "report_generation": "报告生成",
    "attention": "注意力",
    "evaluation": "评测",
    "calcium_imaging": "钙成像",
    "neural_dynamics": "神经动力学",
    "interpretability": "可解释性",
    "single_cell": "单细胞",
    "multi_agent": "多智能体",
    "t_cell": "T 细胞",
    "clustering": "聚类",
    "stain_transfer": "染色迁移",
    "generation": "生成",
    "medical_imaging": "医学影像",
    "organoid_analysis": "类器官分析",
    "tracking benchmark": "追踪基准",
}

SPLIT = re.compile(r"[、,/／;；]+")
EYEBROW = re.compile(r'(<(?:p|div) class="(?:ve-)?eyebrow">[^<]*?· )([^·<]+)( · [^<]*</(?:p|div)>)')


def localize(text: str) -> tuple[str, list[str]]:
    tokens = [token.strip() for token in SPLIT.split(text) if token.strip()]
    out: list[str] = []
    unknown: list[str] = []
    for token in tokens:
        label = LABELS.get(token)
        if label is None:
            if re.search(r"[A-Za-z]", token):
                unknown.append(token)
                continue
            label = token
        if label not in out:
            out.append(label)
    return "/".join(out[:3]), unknown


def find_source(pid: str) -> Path | None:
    for path in (
        ROOT / "data" / "explainers" / "agent" / pid / "out" / f"{pid}.src.html",
        ROOT / "data" / "explainers" / "src" / f"{pid}.src.html",
    ):
        if path.exists():
            return path
    return None


def main() -> int:
    changed = 0
    skipped: list[str] = []
    unknown: set[str] = set()
    for page in sorted(EXPLAINERS.glob("*.html")):
        pid = page.stem
        source_path = find_source(pid)
        if source_path is None:
            skipped.append(pid)
            continue
        source = source_path.read_text(encoding="utf-8")
        match = EYEBROW.search(source)
        if not match:
            skipped.append(pid)
            continue
        label, missing = localize(match.group(2))
        unknown.update(missing)
        if not label or label == match.group(2):
            continue
        updated = source[: match.start(2)] + label + source[match.end(2) :]
        out = EXPLAINERS / f"{pid}.html"
        backup = out.read_bytes()
        source_path.write_text(updated, encoding="utf-8")
        result = subprocess.run(
            ["node", str(RENDER), str(source_path), "-o", str(out), "--no-check"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode != 0:
            source_path.write_text(source, encoding="utf-8")
            out.write_bytes(backup)
            skipped.append(pid)
            continue
        changed += 1
    print(f"改写 {changed} 篇，跳过 {len(skipped)} 篇")
    if unknown:
        print("未收录的代码：" + "、".join(sorted(unknown)))
    if skipped[:10]:
        print("跳过样例：" + "、".join(skipped[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
