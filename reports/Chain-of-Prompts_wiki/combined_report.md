# Chain-of-Prompts — 综合分析报告

- **GitHub**: https://github.com/shjo-april/Chain-of-Prompts
- **分析时间**: 2026-07-16T09:28:15.994647

---

## CodeGraph 知识图谱分析

### 关键符号
- `[1m`
- `Search Results for "class":`
- `[0m`
- `[36mmethod      [0m[37mget_classifier[0m`
- `[2m  core/sam/modeling/sam2/backbones/repvit.py:371[0m`
- `[2m  (self) -> nn.Module[0m`
- `[36mmethod      [0m[37mreset_classifier[0m`
- `[2m  core/sam/modeling/sam2/backbones/repvit.py:374[0m`
- `[1m`
- `Search Results for "def ":`
### 索引状态
```
[1m
CodeGraph Status
[0m
[36mProject:[0m /mnt/c/workspace/cell-ai-research/code/Chain-of-Prompts

[1mIndex Statistics:[0m
  Files:     92
  Nodes:     1,830
  Edges:     4,144
  DB Size:   6.07 MB
  Backend:   [32mnode:sqlite — built-in (full WAL)[0m
  Journal:   [32mwal[0m

[1mNodes by Kind:[0m
  method          767
  import          519
  function        251
  class           175
  file            82
  variable        36

[1mFiles by Language:[0m
  python          82
  yaml      
```

## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/Chain-of-Prompts_wiki`
- 📄 生成文件:
  - architecture.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/core.md
  - modules/examples.md
  - modules/root.md
- 输出: Project: Chain-of-Prompts
Files:   100
Lines:   41,272
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │    81 │
│ yaml     │    10 │
│ unknown  │     3 │
│ markdown │     2 │
│ text     │     2 │
│ json     │     2 │
└──────────┴───────┘
Chain-of-Prompts/
├── ⚙️ README.md (markdown)
├── ⚙️ requirements.txt (text)
├── 📁 .codegraph/
│   └── 📄 .gitignore (unknown)
├── 📄 .gitignore (unknown)
├── 📄 DATASETS.md (markdown)
├── 📄 LICENSE (unknown)
├── 📁 core/
│   ├── 📄 cop.py (python)
│   ├── 📄 sam/SAM_LICENSE.txt (text)
│   ├── 📄 sam/__init__.py (python)
│   ├── 📄 sam/automatic_mask_generator.py (python)
│   ├── 📄 sam/build_sam.py (python)
│   ├── 📄 sam/build_sam_baseline.py (python)
│   ├── 📄 sam/configs/__init__.py (python)
│   ├── 📄 sam/configs/edgetam.yaml (yaml)
│   ├── 📄 sam/configs/sam2.1_hiera_b+.yaml (yaml)
│   ├── 📄 sam/configs/sam2.1_hiera_l.yaml (yaml)
│   ├── 📄 sam/configs/sam2.1_hiera_s.yaml (yaml)
│   ├── 📄 sam/configs/sam2.1_hier

## 原有子代理分析报告

```
基于我对 Chain-of-Prompts 项目的深入分析，我现在可以生成完整的结构化报告：

## 项目概述

**Chain-of-Prompts (CoP)** 是一个训练无关（training-free）的细胞实例分割方法，对应论文 *One Click per Cell Type Suffices: Training-free Group Interaction for Cell Instance Segmentation* (arXiv 2605.29429, MICCAI 2026 Early Accept)。

**核心问题**：现有细胞分割方法存在两个痛点：
1. 特定细胞类型的模型在未见细胞类型上泛化性差
2. 交互式基础模型（如 SAM 3）需要每个细胞实例一次点击（O(N) 复杂度）

**解决方案**：CoP 将交互成本从**每个实例一次点击**降低为**每种细胞类型一次点击**（O(T)），无需训练。在 11 个基准测试上平均减少 97.6% 点击量（42.5 倍），同时保留超过 90% 的 per-instance 上限性能。

## 架构分析

### 目录结构
```
Chain-of-Prompts/
├── core/
│   ├── cop.py                 # 核心算法：HSG + FPR + 解码
│   └── sam/                   # SAM 统一接口
│       ├── __init__.py        # ImageSAM / VideoSAM 封装
│       ├── build_sam.py       # 后端构建器
│       ├── predictor.py       # 各后端预测器
│       ├── configs/           # 模型配置
│       └── modeling/          # sam1/sam2/sam3/zim 模型代码
├── examples/                  # 演示图像 + 参考数据
├── assets/                    # 论文图表
├── demo.ipynb                 # 交互式演示
├── data_H@E_typed/            # H&E + 细胞类型注释（CoNIC, CoNSeP, PanNuke）
├── data_H@E_untyped/          # H&E + 无类型（MoNuSeg, TNBC, CryoNuSeg, CPM-17）
├── data_non-H@E_untyped/      # 非 H&E 显微镜图像（CellBinDB, Cellpose, Kromp, LIVECell）
├── requirements.txt
└── DATASETS.md                # 数据集许可说明
```

### 依赖关系
- **Python ≥ 3.10, PyTorch ≥ 2.1, CUDA ≥ 11.8**
- 核心依赖：numpy, opencv-python, matplotlib, Pillow
- SAM 接口依赖：hydra-core, iopath, huggingface_hub, sanghyunjo
- 演示工具：jupyter, ipykernel, gradio

### 主要模块
1. **`ChainOfPrompts`类** (`core/cop.py`)：端到端 API
2. **`ImageSAM`类** (`core/sam/__init__.py`)：SAM 系列统一封装
3. **预测器** (`core/sam/predictor.py`)：支持 SAM1/SAM2/SAM3/ZIM
4. **模型实现** (`core/sam/modeling/`)：完整 SAM 模型代码

## 核心算法

CoP 包含两个无训练步骤，完全利用冻结 SAM 编码器的特征：

### 1. 层次相似性门控（HSG, Hierarchical Similarity Gating）
输入：用户点击位置 + 编码器多尺度特征
- **高分辨率相似性**：计算点击位置特征与高分辨率特征图的余弦相似性
- **非参数门控**：阈值 = 相似性均值 + 标准差，提取前景区域
- **连通分量分析**：提取面积 ≥ min_area 的组件，计算加权质心
- **低分辨率门控**：对候选点用低分辨率特征再次过滤，确保类别一致性
- **输出**：可靠同类型点集（精确度 >96%）

### 2. 最远提示递归（FPR, Farthest Prompt Recursion）
输入：初始点击 + HSG 输出
- **迭代循环**：对当前点击运行 HSG → 去重 → 选择与已使用提示最远的可靠点
- **终止条件**：无新点发现 或 达到 max_iterations
- **输出**：全覆盖同类型点集

### 3. 训练无关掩码解码
- 对每个 propagated point 调用 SAM mask decoder
- **Guard 机制**：拒绝与两个以上现实例重叠的掩码
- **NMS**：IoU > 0.5 的重复掩码被过滤
- **颜色编码**：确定性颜色映射便于可视化

### 关键实现细节
- 图像仅编码**一次**，特征图缓存在内存中
- 所有操作通过 `torch.no_grad()` 避免反向传播
- 使用 `autocast(dtype=torch.float32)` 控制精度
- 坐标转换通过 `img_to_feat()` / `feat_to_img()` 完成

## 代码质量

### 优点
- **文档完整性**：README.md 详尽，包含方法概述、快速开始、数据集说明、许可证
- **代码可读性高**：`core/cop.py` 只有 385 行，逻辑清晰，注释充分
- **模块化设计**：HSG、FPR、解码分别封装为独立函数
- **API 简洁**：`ChainOfPrompts` 提供统一接口，隐藏复杂细节
- **测试覆盖**：提供 demo.ipynb 和示例数据，便于快速验证

### 不足
- **缺乏单元测试**：无 pytest/unittest 测试集
- **批处理支持弱**：设计为单图像处理，不适合批量推理
- **依赖复杂性**：需要 SAM 3 等 gated 模型权重，setup 门槛较高
- **错误处理**：边界情况处理较少（如无效点击、空特征）

### 评估
- **代码规范**：⭐⭐⭐⭐ (4/5) - 良好的命名、注释，但缺少类型提示
- **可维护性**：⭐⭐⭐⭐ (4/5) - 模块化好，但依赖外部 SAM 代码
- **测试**：⭐⭐ (2/5) - 仅有 demo，无自动化测试

## 可复现性

### 安装资源
- ✅ **requirements.txt*
```

> 完整报告: [reports/Chain-of-Prompts.md](Chain-of-Prompts.md)