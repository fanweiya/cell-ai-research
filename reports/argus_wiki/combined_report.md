# argus — 综合分析报告

- **GitHub**: Gitinc/argus
- **评分**: 7.0/10
- **分析时间**: 2026-07-15T18:32:43.262446

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/argus_wiki`
- 📄 生成文件:
  - architecture.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/notebooks.md
  - modules/root.md
  - modules/src.md
- 输出: Project: argus
Files:   13
Lines:   5,467
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │     6 │
│ unknown  │     5 │
│ markdown │     1 │
│ text     │     1 │
└──────────┴───────┘
argus/
├── ⚙️ README.md (markdown)
├── ⚙️ requirements.txt (text)
├── 📁 .codegraph/
│   └── 📄 .gitignore (unknown)
├── 📄 .gitignore (unknown)
├── 📄 LICENSE (unknown)
├── 📁 notebooks/
│   ├── 📄 compute_cell_paths.ipynb (unknown)
│   └── 📄 format_tracks_for_CTC.ipynb (unknown)
└── 📁 src/
    ├── 📄 algo_funcs.py (python)
    ├── 📄 algo_funcs_old.py (python)
    ├── 📄 ctc_reformat.py (python)
    ├── 📄 display_funcs.py (python)
    ├── 📄 parameter_scan.py (python)
    └── 📄 utils.py (python)
⠋ Done!

Wiki generated: /mnt/c/workspace/cell-ai-research/reports/argus_wiki/
Tokens used: 19,420 in / 5,032 out

## 原有子代理分析报告

```
现在我已经充分了解了这个仓库。让我开始撰写报告。

## 项目概述

**ARGUS** (Gitinc/argus) 是一个用于时序显微图像中细胞追踪的鲁棒、通用且计算高效的框架。其名称来源于希腊神话中的百眼巨人阿尔戈斯 (Argus Panoptes)，象征"全知全能"。

### 论文来源
- **论文标题**: ARGUS: Accelerated, Robust, General, and Unsupervised Cell Tracking Solutions
- **arXiv**: 2607.08297
- **代码仓库**: https://github.com/Gitinc/argus

### 核心问题
解决细胞追踪任务中的以下挑战：
- **多样化成像条件**: 需要在不同对比度、信噪比の下工作
- **无需训练**: 不依赖深度学习模型，适用于没有标注数据的情况  
- **计算效率**: 可在 CPU 上运行，适合长时序和高通量工作流
- **鲁棒性**: 处理细胞分裂、遮挡、移出视野等情况

---

## 架构分析

### 目录结构
```
ARGUS/
├─ notebooks/           # 交互式 Jupyter Notebook 示例
├─ src/                 # 核心算法实现
│  ├─ algo_funcs.py     # 主要算法函数 (检测 + 追踪)
│  ├─ algo_funcs_old.py # 旧版算法 (可能已废弃)
│  ├─ ctc_reformat.py   # CTC 格式转换工具
│  ├─ display_funcs.py  # 可视化和分析函数
│  └─ parameter_scan.py # 参数扫描脚本
├─ results/             # 示例输出视频
└─ requirements.txt     # 依赖列表
```

### 核心模块依赖关系

```
依赖关系链:
notebooks → src.algo_funcs (核心) → src.display_funcs (可视化)
                            ↓
                      src.ctc_reformat (输出格式)
                            ↓
                      ctc_metrics (外部评估包)
```

### 技术栈
- **图像加载/处理**: PIL, scikit-image, OpenCV, ITK
- **PDE/滤波**: BM3D, 小波变换, monogenic 滤波
- **追踪算法**: Farneback 光流 + 匈牙利算法
- **并行计算**: multiprocessing, concurrent.futures
- **可视化**: matplotlib (出版质量)
- **外部依赖**: `ctc_metrics` (用于 CTC 评估)

---

## 核心算法

### 1. 细胞检测模块

ARGUS 提供三种检测策略：

#### a) 质心检测 (`locate_all_cells_centroids`)
- **原理**: Otsu 阈值 + 区域属性 (regionprops) 提取质心
- **适用**: 较大细胞 (形态清晰)
- **关键参数**: `cell_size` (期望细胞大小), `min_distance` (最小间距)

```python
# 核心逻辑
thresh = skimage.filters.threshold_otsu(image)  # 自适应阈值
labeled_mask = skimage.measure.label(thresh_img)
centers = [region.centroid for region in regionprops(labeled_mask)]
# 非极大值抑制 (based on min_distance)
```

#### b) 局部极大值检测 (`locate_all_cells_local_maxima`)
- **原理**: 在分割后的区域内寻找局部极大值点
- **适用**: 小细胞或欠分割场景
- **关键参数**: `min_size`, `expected_mask_size`, `min_distance`

```python
# 核心逻辑
for region in area_props:
    region_maxima = peak_local_max(region_image, min_distance)
    # 若区域过大，则人工拆分 (保留 max_allowed 个极大值)
```

#### c) Monogenic 滤波检测 (`locate_all_cells_monogenic_filter`)
- **原理**: 利用单色滤波 (monogenic filter) 提取相位对称性特征
- **适用**: 纹理丰富或边界清晰的图像
- **关键参数**: `cw_monogenic` (特征尺度), `T` (阈值)

### 2. 追踪算法 (`track_points_optical_flow`)

这是 ARGUS 的核心，结合了光流预测和线性分配：

#### 流程:
1. **光流计算**: 使用 OpenCV 的 Farneback 算法计算相邻帧稠密光流
2. **点匹配**: 匈牙利算法 (Hungarian assignment) 将预测位置与检测点匹配
3. **轨迹管理**: 支持分裂 (mitosis)、遮挡、新生轨迹
4. **幽灵位置**: 未检测到细胞时使用光流预测位置 (ghost position)

```python
# 核心追踪循环
for t, (flow_y, flow_x) in enumerate(flows):
    # 1. 对活跃轨迹进行光流预测
    predicted = _advect_points(current_points, flow_x, flow_y)
    
    # 2. 匈牙利匹配
    matches, unmatched_points = hungarian_assignment(predicted, detected, max_distance)
    
    # 3. 处理匹配冲突 (collision)
    collided = _find_collisions(matches, active_indices, label_of)
    
    # 4. 扩展匹配轨迹，标记未匹配轨迹为遮挡
    for k, entry in enumerate(active_indices):
        if matched:
            _extend_track(entry, matc
```

> 完整报告: [reports/argus.md](argus.md)