# cellnet — 综合分析报告

- **GitHub**: beijn/cellnet
- **评分**: ?/10
- **分析时间**: 2026-07-15T18:33:23.059779

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/cellnet_wiki`
- 📄 生成文件:
  - architecture.md
  - dependencies.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/baselines.md
  - modules/bin.md
  - modules/cellnet.md
  - modules/root.md
- 输出: Project: cellnet
Files:   34
Lines:   2,409
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │    16 │
│ unknown  │    13 │
│ yaml     │     2 │
│ markdown │     1 │
│ toml     │     1 │
│ shell    │     1 │
└──────────┴───────┘
cellnet/
├── ⚙️ README.md (markdown)
├── ⚙️ pyproject.toml (toml)
├── 📁 bin/
│   ├── 📄 clean (unknown)
│   ├── 📄 code-tunnel (unknown)
│   ├── 📄 data-sync (unknown)
│   ├── 📄 imports.sh (shell)
│   ├── 📄 install (unknown)
│   ├── 📄 job-ipynb (unknown)
│   ├── 📄 normalize_paths (unknown)
│   ├── 📄 release (unknown)
│   ├── 📄 submit-job (unknown)
│   └── 📄 test-release (unknown)
├── 📁 .codegraph/
│   └── 📄 .gitignore (unknown)
├── 📄 .gitignore (unknown)
├── 📁 baselines/
│   └── 📄 cpsam.py (python)
├── 📄 cellnet-vs-countess-all.csv (unknown)
├── 📄 cellnet.yml (yaml)
├── 📁 cellnet/
│   ├── 📄 __init__.py (python)
│   ├── 📄 data.py (python)
│   ├── 📄 debug.py (python)
│   ├── 📄 evaluate.py (python)
│   ├── 📄 internet.py (

## 原有子代理分析报告

```
Now I have sufficient information to write a comprehensive analysis report. Let me structure my response:

## 项目概述

**CellNet** 是一个用于在相差显微镜图像中自动化细胞定位和计数的机器学习项目。该仓库是 Wellcome Sanger Institute、哥廷根大学计算细胞分析实验室和塔图大学生物医学计算机视觉实验室的合作成果。

论文来源：arXiv 2606.12286，题为 "**CellNet: Localizing Cells using Sparse and Noisy Point Annotations**" (2026)。

核心创新点：
- 将细胞定位与计数转化为**回归任务**，通过预测高斯热图而非传统分割掩码
- 能够从**稀疏且带噪声的点标注**中学习，大幅降低标注成本
- 在小数据条件下表现良好，适合生物医学研究资源受限场景

主要解决的问题：
- 传统细胞分割需要像素级标注，耗时费力
- 相差显微图像质量较低，细胞边界模糊
- 现有方法（如 Cellpose）在低质量图像上表现不稳定

---

## 架构分析

### 目录结构

```
cellnet/
├── cellnet/                  # 核心包
│   ├── __init__.py           # 导出 init_model, count，定义 API 版本
│   ├── data.py               # 数据加载、预处理、数据集类
│   ├── evaluate.py           # 评估指标 (sMAPE, MAE, precision/recall/F1)
│   ├── plot.py               # 可视化模块
│   └── release.py            # 模型推理和发布逻辑
├── baselines/                # 基线方法
│   └── cpsam.py              # Cellpose-SAM 基线
├── bin/                      # 工具脚本
│   ├── install               # 安装脚本
│   ├── submit-job            # 集群作业提交
│   ├── job-ipynb             # 笔记本作业执行
│   └── normalize_paths       # 路径标准化
├── data/                     # 数据目录（需自行准备）
├── train.py                  # 主训练脚本（Jupyter笔记本格式）
├── train_livecell.py         # LiveCell 数据集训练脚本
├── preprocess_annotations.py # Label Studio 标注转换工具
├── eval.py                   # 模型评估脚本
├── pyproject.toml            # 项目依赖配置
├── cellnet.yml               # Conda 环境配置
└── README.md                 # 完整文档
```

### 依赖关系

**核心依赖**：
- `torch~=2.6.0` (PyTorch)
- `segmentation-models-pytorch>=0.5.0` (UNet等模型)
- `albumentations==1.4.22` (图像增强)
- `numpy<2.0`, `scipy`, `matplotlib`, `pandas`, `scikit-image`

**可选依赖**：
- CPU 版本：`torch` from `pytorch-cpu` index
- CUDA 12.4：`torch` from `pytorch-cu124` index

### 主要模块

1. **数据管道** (`data.py`)
   - `CellnetDataset`: PyTorch Dataset，处理图像和关键点标注
   - `Keypoints2Heatmap`: 关键点→高斯热图生成
   - `mask_sparse`: 生成前景掩码（用于负样本）
   - `load_image`, `load_points`: 数据加载器

2. **模型定义** (`train.py`)
   - 使用 `segmentation_models_pytorch` 构建解码器
   - 支持多种架构：Unet, UnetPlusPlus, FPN, PSPNet 等
   - 支持多种编码器：ResNet, EfficientNet, MoNet 等

3. **训练流程** (`train.py`)
   - 多实验配置系统 (`EXPERIMENTS` 字典)
   - 交叉验证支持
   - 学习率调度和早停机制

4. **推理接口** (`release.py`)
   - `init_model()`: 自动下载和缓存模型
   - `count()`: 批量细胞计数
   - `wrap_padded`: 形状对齐推理（避免边界伪影）

---

## 核心算法

### 方法原理

CellNet 的核心思想是将细胞计数问题建模为**密度图回归**任务：

1. **标注转换**：
   - 将稀疏的点标注（中心点）转换为高斯热图
   - 公式：`H(x,y) = exp(-||x-y||² / (2σ²))`
   - σ 是关键超参数，默认 `σ=5×1.5=7.5`（与图像尺度相关）

2. **模型训练**：
   - 输入：单通道相差显微图像 (1×H×W)
   - 输出：预测热图 (1×H×W)
   - 损失函数：**MSE + BCE** 组合
     - MSE: 回归热图数值
     - BCE: 确保前景区域激活
   - 优化器：Adam (lr=5e-3)，StepLR 调度

3. **热图→计数**：
   - 计数 = `热图总和 × ymax`
   - `ymax` 在训练时计算，用于归一化热图和真实热图至相同尺度

4. **数据增强**：
   - 随机裁剪 (256×256)
   - 随机亮度/对比度调整 (±0.25)
   - D4 对称变换 (旋转/镜像)
   - 标准归一化 (ImageNet 统计或图像自适应)

5. **推理优化**：
   - `wrap_padded`: 将输入扩展到 32 的倍数，预测后裁剪
   - 避免边界伪影，同时满足 UNet 下采样要求

### 关键实现细节

```python
# 关键点 → 热图 (data.
```

> 完整报告: [reports/cellnet.md](cellnet.md)