# HASSL — 综合分析报告

- **GitHub**: tum-ai/HASSL
- **评分**: 8.5/10
- **分析时间**: 2026-07-15T18:26:41.634153

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/HASSL_wiki`
- 📄 生成文件:
  - architecture.md
  - dependencies.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/.github.md
  - modules/dinov3.md
  - modules/docs.md
  - modules/notebooks.md
- 输出: Project: HASSL
Files:   169
Lines:   28,872
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │   135 │
│ yaml     │    15 │
│ markdown │     5 │
│ unknown  │     5 │
│ c        │     3 │
│ text     │     2 │
│ cpp      │     2 │
│ toml     │     1 │
│ html     │     1 │
└──────────┴───────┘
HASSL/
├── ⚙️ README.md (markdown)
├── 📁 dinov3/
│   ├── ⚙️ configs/config.py (python)
│   ├── ⚙️ eval/detection/config.py (python)
│   ├── ⚙️ eval/segmentation/models/utils/ops/setup.py (python)
│   ├── ⚙️ eval/setup.py (python)
│   ├── 📄 __init__.py (python)
│   ├── 📄 checkpointer/__init__.py (python)
│   ├── 📄 checkpointer/checkpointer.py (python)
│   ├── 📄 configs/__init__.py (python)
│   ├── 📄 configs/ssl_default_config.yaml (yaml)
│   ├── 📄 configs/train/dinov3_neglambds.yaml (yaml)
│   ├── 📄 configs/train/dinov3_vit7b16_gram_anchor.yaml (yaml)
│   ├── 📄 configs/train/dinov3_vit7b16_high_res_adapt.yaml (yaml)
│   ├── 📄 configs/train/dinov3_vit7b16_

## 原有子代理分析报告

```
现在让我总结分析结果并输出报告。基于我对 HASSL 仓库的深入分析，我来生成结构化报告：

## 项目概述

HASSL（Hierarchy-Aware Self-Supervised Learning）是一个针对单细胞显微镜图像的层次感知自监督学习框架，对应论文 **"HASSL: Hierarchy-Aware Self-Supervised Learning Framework for Single Cell Microscopy"** (arXiv:2607.04353, 2026年7月)。

**核心问题**：在生物细胞图像中，当前自监督学习模型常常抑制层次结构，粗粒度的成像因素（如成像模式、染色协议）会掩盖精细的形态学特征，导致潜在空间中语义上不同的细胞看起来相同，层次相关的亚型坍缩到同一个簇中。

**解决方案**：HASSL 在 DINOv3 基础上引入两个核心组件：
1. **Double-Teacher Distillation**：结合分割教师（使用 CellposeSAM 零样本分割掩码）和标准 EMA 图像教师，引导学生模型关注细胞形态而非采集模式
2. **Hierarchy-Aware Contrastive Loss**：基于 HDBSCAN 在批次嵌入中构建层次原型树，通过稳定性权重（λ）在每一层次挖掘正负样本，拉拢细胞向祖先聚类中心靠拢，同时推开不同亚型

**数据集**：在 230 万细胞、20 个显微镜数据集、208 个细胞类上训练和评估。

**性能提升**：相比最先进自监督基线，Top-K 准确率提升 2.8%，最深层次结构 Top-9 检索提升 6.3%，药物扰动分类 F1 分数提升 7.8%。

## 架构分析

### 目录结构
```
HASSL/
├── dinov3/              # 基于 DINOv3 核心代码
│   ├── data/            # 数据集、数据增强、加载器
│   ├── layers/          # 网络层，包括 clustering.py（HDBSCAN 原型构建）
│   ├── loss/            # 损失函数，包括 triplet_hierachical_loss.py（层级对比损失）
│   ├── models/          # 模型架构
│   ├── train/           # 训练架构（ssl_meta_arch.py 为核心）
│   └── eval/            # 评估脚本
├── notebooks/           # 提取嵌入的 Jupyter 示例
├── manifests/           # 预设的训练/验证/测试清单
└── docs/                # 项目文档
```

### 主要模块依赖关系
1. **基础框架**：DINOv3（PyTorch，FSDP2，混合精度）
2. **核心依赖**：
   - `hdbscan==0.8.41`：层次聚类
   - `torch==2.10.0`：深度学习框架
   - `wandb==0.25.0`：实验追踪
   - `omegaconf==2.3.0`：配置管理
3. **数据格式**：自定义 `.npy` 图像和掩码格式，通过 manifest CSV 管理

### 数据流水线
- **数据集类**：`NCells` (dinov3/data/datasets/n_cells.py) 支持多源数据集
- **数据增强**：DINO 风格多尺度裁剪 + 颜色抖动
- **特殊处理**：支持分割掩码（CellposeSAM）作为额外输入

## 核心算法实现原理

### 1. Double-Teacher Distillation
在 `ssl_meta_arch.py` 的 `seg` 模块实现（第 421-466 行）：

```python
if getattr(self.cfg, "seg", None) and self.cfg.seg.enabled:
    # Seg -> Seg loss (student segmentation vs teacher segmentation)
    seg2seg = dino_loss(seg_student, seg_teacher)
    # Seg -> Image loss (student image vs teacher segmentation)
    seg2img = dino_loss(student, seg_teacher)
    # 权重动态调整：min(0.2, (iteration/125000)*0.2)
    seg_extra_loss = w * (seg2seg + seg2img)
```

**关键设计**：分割教师使用 CellposeSAM 零样本掩码，与学生-图像对进行知识蒸馏。这就像是一个注意力机制，引导模型关注细胞结构而非背景或成像伪影。

### 2. HDBSCAN 原型层次构建
`clustering.py` 中的 `build_triplet_lists_with_paths` 函数：

- 输入：批次嵌入 X (N, D)
- 使用 HDBSCAN 构建聚类树
- 修剪单子树边（singleton-child edges），保留有意义的层次结构
- 为每个样本构建：
  - **Positive**：路径上所有祖先原型（深度>0）及其 λ 值
  - **Negative**：同层其他簇原型 + 同簇内更细粒度原型
- 输出： positives, negatives, lambdas, neg_lambdas

### 3. 层级三元组对比损失
`triplet_hierachical_loss.py` 实现：

```python
# 对每个锚点
positive_sum = Σ (dist(anchor, pos_i)² × λ_i) / P
negative_sum = Σ (max(0, 2 - dist(anchor, neg_i))² × λ_neg_i) / N
loss = positive_sum + negative_sum
```

**创新点**：
- 使用稳定性 λ 作为权重，强调可靠的层次关系
- 拉普拉斯平滑处理距离，避免极端值
- 支持全局或局部权重缩放

### 4. 训练流程
1. 标准 DINOv3 双师生蒸馏（Image-Image）
2. 分割教师蒸馏（Seg-Image）
3. HDBSCAN 聚类批次嵌入
4. 构建 triplet 正负样本
5. 计算层级三元组损失
6. 多任务联合优化

## 代码质量

### ✅ 优点
1. **模块化设计清晰**：各组件职责分离，易于理解和维护
2. **配置系统完善**：YAML 配置 + 动态命令行覆盖
3. **分布式训练支持**：FSDP2、混合精度、梯度累积
4. **日志追踪
```

> 完整报告: [reports/HASSL.md](HASSL.md)