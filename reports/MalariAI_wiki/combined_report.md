# MalariAI — 综合分析报告

- **GitHub**: Anaskaysar/MalariAI
- **评分**: 7.5/10
- **分析时间**: 2026-07-15T18:29:44.817135

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/MalariAI_wiki`
- 📄 生成文件:
  - architecture.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/data.md
  - modules/notebooks.md
  - modules/Phase1-EDA.md
  - modules/Phase2-BaselineA.md
  - modules/Phase3-PipelineB.md
- 输出: Project: MalariAI
Files:   459
Lines:   44,049
      Languages       
┏━━━━━━━━━━━━┳━━━━━━━┓
┃ Language   ┃ Files ┃
┡━━━━━━━━━━━━╇━━━━━━━┩
│ json       │   429 │
│ python     │    12 │
│ unknown    │     8 │
│ markdown   │     4 │
│ html       │     2 │
│ dockerfile │     1 │
│ text       │     1 │
│ css        │     1 │
│ javascript │     1 │
└────────────┴───────┘
MalariAI/
├── 📁 Phase4-WebApp/
│   ├── ⚙️ Dockerfile (dockerfile)
│   ├── ⚙️ requirements.txt (text)
│   ├── 📄 app.py (python)
│   ├── 📄 README_deploy.md (markdown)
│   ├── 📄 malariai_medical_ui.html (html)
│   ├── 📄 pipeline.py (python)
│   ├── 📄 static/css/style.css (css)
│   ├── 📄 static/js/app.js (javascript)
│   └── 📄 templates/index.html (html)
├── ⚙️ README.md (markdown)
├── 📁 data/
│   └── ⚙️ MP-IDB/README.md (markdown)
├── 📁 .codegraph/
│   └── 📄 .gitignore (unknown)
├── 📄 .gitignore (unknown)
├── 📁 Phase1-EDA/
│   ├── 📄 dataset.py (python)
│   └── 📄 eda.py (python)
├── 📁 Phase2-BaselineA/
│   ├── 📄 Phase2_FasterRC

## 原有子代理分析报告

```
让我读取现有的文件来生成分析。现在我已经有了足够的核心代码信息。让我整理一份完整的分析报告：

## 项目概述

MalariAI 是一个用于疟疾血液涂片细胞分割和阶段的软件包，旨在解决三个关键问题：
1. **不完整标注**（P1）- 端到端检测器将未标注细胞视为背景
2. **密集重叠/非极大值抑制失败**（P2）- NMS 丢弃高密度区域的有效细胞检测
3. **黑盒输出**（P3）- 缺乏空间证据的可解释性

论文来源：arXiv 2607.00385，目标投稿期刊 CMIG (Computerized Medical Imaging and Graphics)。主要采用两阶段解耦框架：
- **阶段1**：距离变换引导的分水岭算法，无需完整标注即可分割所有细胞
- **阶段2**：EfficientNet-B0 + Focal Loss 进行分类，并用 Grad-CAM++ 生成可解释性热力图

## 架构分析

### 目录结构
```
MalariAI/
├── data/                    # 数据处理
│   ├── malaria/             # BBBC041 数据集
│   ├── MP-IDB/              # 跨数据集验证
│   ├── prepare_data.py      # JSON 转 CSV 工具
│   └── prepare_mpidb.py     # MP-IDB 标注转换
├── Phase1-EDA/              # 探索性数据分析
│   ├── dataset.py           # PyTorch Dataset 类（全局使用）
│   └── eda.py               # 数据分布分析
├── Phase2-BaselineA/        # Faster R-CNN 基线
│   └── train_frcnn.py       # 检测模型训练
├── Phase3-PipelineB/        # 核心 MalariAI 管线
│   ├── stage1_watershed.py  # 分水岭分割
│   ├── stage2_train.py      # EfficientNet-B0 训练
│   ├── stage2_inference.py  # 端到端推理
│   └── gradcam.py           # Grad-CAM++ 实现
├── src/
│   └── pipeline_b_v2/       # 改进版本
│       ├── stage1_v2.py     # CLAHE + 分辨率感知峰值检测
│       └── e2e_eval.py      # 端到端评估
└── Phase4-WebApp/           # Flask Web 应用
```

### 核心依赖
- `torch`, `torchvision` (模型和训练)
- `opencv-python`, `numpy` (图像处理)
- `scipy`, `scikit-image` (形态学操作)
- `PIL` (图像显示和变换)
- `matplotlib` (可视化)

## 核心算法

### 阶段1：分水岭分割（stage1_watershed.py）

```python
def watershed_cells(bgr: np.ndarray) -> List[Tuple[int, int, int, int]]:
    # 1. Otsu 阈值化：细胞暗于背景
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # 2. 形态学开操作去噪
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    # 3. 欧氏距离变换
    dist = ndi.distance_transform_edt(opened)
    # 4. 局部最大峰值检测（每个细胞一个种子）
    coords = peak_local_max(dist, min_distance=min_dist,
                           threshold_abs=dist_thr * dist.max(),
                           labels=opened.astype(bool))
    # 5. 标记种子，分水岭分割
    markers, _ = ndi.label(mask)
    labels = watershed(-dist, markers, mask=opened.astype(bool), compactness=0.1)
    # 6. 提取边界框
    boxes = [(xs.min(), ys.min(), xs.max(), ys.max()) for each label]
    return boxes
```

关键参数：`MIN_DIST=12`（峰值最小距离），`OPEN_KSIZE=3`（开操作核），`DIST_THRESH=0.25`（距离阈值）。

### 阶段2：EfficientNet-B0 分类器（stage2_train.py）

```python
class FocalLoss(nn.Module):
    def __init__(self, alpha: torch.Tensor, gamma: float = 2.0):
        self.register_buffer("alpha", alpha)
        self.gamma = gamma
    
    def forward(self, logits, targets):
        ce = F.cross_entropy(logits, targets, reduction="none")
        pt = torch.exp(-ce)
        at = self.alpha[targets]
        loss = at * (1.0 - pt) ** self.gamma * ce
        return loss.mean()
```

实现细节：
- 使用 ImageNet 预训练权重，替换分类头为 7 类
- Focal Loss 参数：gamma=2.0，alpha 基于训练集类别频率平衡
- 优化器：AdamW (lr=1e-4, weight_decay=1e-4)
- 学习率调度：CosineAnnealingLR (T_max=epochs)

### Grad-CAM++ 实现（gradcam.py）

改进自原始 Gra
```

> 完整报告: [reports/MalariAI.md](MalariAI.md)