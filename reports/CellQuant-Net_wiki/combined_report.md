# CellQuant-Net — 综合分析报告

- **GitHub**: Falah-Jabar-Rahim/CellQuant-Net
- **评分**: 8.0/10
- **分析时间**: 2026-07-15T18:23:53.844004

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/CellQuant-Net_wiki`
- 📄 生成文件:
  - architecture.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/CP-Net.md
  - modules/input.md
  - modules/output.md
  - modules/root.md
  - modules/WSI_QA.md
- 输出: Project: CellQuant-Net
Files:   51
Lines:   10,711
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │    40 │
│ text     │     5 │
│ unknown  │     2 │
│ yaml     │     2 │
│ markdown │     1 │
│ shell    │     1 │
└──────────┴───────┘
CellQuant-Net/
├── ⚙️ README.md (markdown)
├── 📁 WSI_QA/
│   ├── ⚙️ config.py (python)
│   ├── 📄 configs/DHUnet_224.yaml (yaml)
│   ├── 📄 datasets/dataset.py (python)
│   ├── 📄 network/ConvNeXt/ConvNeXt.py (python)
│   ├── 📄 network/ConvNeXt/ConvNeXtUnet.py (python)
│   ├── 📄 network/ConvNeXt/__init__.py (python)
│   ├── 📄 network/ConvNeXt/convNet.py (python)
│   ├── 📄 network/DHUnet.py (python)
│   ├── 📄 network/SwinTransformer/SwinTransformer.py (python)
│   ├── 📄 network/SwinTransformer/SwinUnet.py (python)
│   ├── 📄 network/SwinTransformer/__init__.py (python)
│   ├── 📄 
│   │   network/SwinTransformer/swin_transformer_unet_skip_expand_decoder_sys.py
│   │   (python)
│   ├── 📄 network/TransFuse/DeiT.py (p

## 原有子代理分析报告

```
现在让我基于获取的信息生成分析报告。基于对 CellQuant-Net 仓库的深入分析，我将输出结构化报告。

## 项目概述

CellQuant-Net (论文: arXiv 2607.00802 "CellPrior-Net: Prior-Guided Nuclei Detection and Classification for H&E Whole-Slide Images") 是一个用于 H&E 全切片图像(WSI)的细胞核检测、分类和定量分析的计算病理学流程。

**主要解决的问题：**
- H&E 染色 WSIs 中细胞核检测与分类的准确性挑战（形态多变、染色差异、扫描设备不同、器官来源多样）
- 现有方法计算量大，分析千兆像素级 WSI 耗时过长
- 图像质量不均（伪影、模糊、折叠等）影响下游分析

**核心方案：** 提出 CellPrior-Net (CP-Net) + 质量评估(WRI-QA) + 细胞连通性分析，实现端到端的高通量细胞核量化。

## 架构分析

### 目录结构
```
CellQuant-Net/
├── CP-Net/               # 核心检测模块
│   ├── model/
│   │   ├── model.py      # CellPriorNet 主模型
│   │   └── unirepLKnet.py # UniRepLKNet  backbone
│   ├── dataset.py        # 数据集加载
│   ├── post_process.py   # 后处理（分水岭、实例分割）
│   ├── cell_connectivitey.py # 细胞邻域分析
│   └── test_cp_net.py    # 推理脚本
├── WSI_QA/               # 质量评估模块
│   ├── network/
│   │   ├── DHUnet.py     # 双分支 U-Net 架构
│   │   ├── SwinTransformer/
│   │   └── ConvNeXt/
│   └── test_qa.py        # QA 推理
├── install.sh            # 安装脚本
├── requirements.txt      # 依赖
└── run_cellquant_net.py  # 主运行脚本
```

**关键依赖：**
- PyTorch, CUDA 12.8
- MONAI, timm, albumentations
- CuPy (GPU 加速)、scikit-image
- OpenCV, pandas, networkx

## 核心算法

### CP-Net (CellPrior-Net)

**1. 双通道先验融合机制**
- 从苏木精(H)通道提取两种先验：
  - **DoG (Difference of Gaussians)**: 多尺度高斯差，检测核周边结构
  - **RingBank**: 环形核滤波器，捕捉核边界
- 先验图与 RGB 图像拼接为 4 通道输入
- 融合策略：mean / wsum / mul / max

**2. 网络架构**
- **Backbone**: UniRepLKNet (大核深度可分离卷积)
- **Decoder**: 基于 RepLKNet 改进，融合多尺度特征
- **双输出头**：
  - 二分类头 (核 vs 背景)
  - 类型分类头 (核亚型)

**3. 后处理**
- GPU 加速的形态学侵蚀
- 多尺度大小分割 (small/medium/big/vbig)
- 基于 H/V 方向图的分水岭分割
- Numba 加速的 CPU 并行

### WSI-QA (质量评估)

- **双分支 U-Net (DHUnet)**: 局部分支 (ConvNeXt) + 全局分支 (SwinTransformer)
- **注意力融合模块 (AFF/iAFF/DAF)**: 融合局部细节与全局上下文
- 四分类：背景、组织、折叠、模糊

## 代码质量

**优点：**
- 模块化设计清晰，各组件职责明确
- GPU 加速充分利用 (CuPy、DLPack 零拷贝)
- 包含详细注释和参数说明
- 提供多种预设模型 (PanNuke, CoNSeP, ILCD 等)

**待改进：**
- 文档不完整 (缺少 API 文档、训练脚本)
- 测试覆盖不足 (仅推理测试)
- 部分代码重复 (H 通道提取在 dataset.py 和 spli_H.py)
- 依赖较重，安装复杂 (需手动构建 C++ 扩展)

## 可复现性

**具备条件：**
- ✅ 明确的系统要求 (Ubuntu 20.04/22.04, CUDA 12.8, Python 3.9)
- ✅ `install.sh` 自动化安装脚本
- ✅ `requirements.txt` 列出所有依赖
- ✅ `README.md` 提供快速测试流程
- ✅ 多数据集预训练模型
- ⚠️ 但缺少训练代码，仅包含推理脚本
- ⚠️ 部分模型权重需联系作者获取

**复现难度：中等偏高**
- 需要 NVIDIA GPU (24GB VRAM 推荐)
- 依赖 `depthwise_conv2d_implicit_gemm` C++ 扩展编译
- 仅支持推理，自行训练需从头实现

## 与高通量细胞图像分析项目 (YOLO+SAM 管线) 的相关性

### 可直接复用的模块

1. **H 通道提取算法** (`extract_H_channel`)
   - 基于免疫组织化学 staining deconvolution 的经典方法
   - 可复用到我项目的 H&E 预处理步骤

2. **细胞核先验构建** (`spli_H.py`, `model/model.py`)
   - DoG + RingBank 组合用于增强细胞核感知
   - 可作为 Priors 模块集成到 YOLO 输入分支

3. **GPU 加速后处理** (`post_process.py`)
   - GPU 形态学操作 + 分水岭分割
   - 多尺度大小切割策略可优化实例分割

4. **细胞邻域分析** (`cell_connectivitey.py`)
   - 基于坐标和类型的空间网络构建
   - TILs/Tumor 浸润评分计算可直接应用

5. **质量评估模块** (`WSI_QA/`)
   - DHUnet 双分支架构适用于图像质量过滤
   - 实验性模块可降级为轻量 CNN

### 值得参考的创新点

1. **显式先验引导网络**: 将 H 通道先验作为 4 通道输入
   - 可探索将类似先验融入 YOLO 的 backbone 前几层

2. **多尺度大小感知分割**: GPU 切割不同大小核
   - 避免传统 NMS 过杀，提升密集细胞的分割

3. **端到端管线设
```

> 完整报告: [reports/CellQuant-Net.md](CellQuant-Net.md)