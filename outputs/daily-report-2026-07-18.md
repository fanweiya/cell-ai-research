# Cell AI Research Engineering Daily — 2026-07-18

## 发现:5 新 | 通过relevance:74 | 完整分析:20 | 跳过:4 | 错误:0 | 运行中:0

### 🆕 本期新发现（2026-06-01 ~ 2026-07-15，本轮补登）

| # | arXiv | 标题 | 任务族 | R | E | P | 状态 |
|---|-------|------|--------|---|---|---|------|
| 1 | 2607.14410v1 | LATTICE: Graph Self-Supervised Learning for Multimodal Spatial Omics | spatial/ssL | 8 | 2 | 10 | 新发现✅ |
| 2 | 2606.21605v1 | μMatch: Foundation Models for Semi-supervised Domain Adaptation in EM | segmentation/EM | 9 | 3 | 12 | 新发现✅ |
| 3 | 2606.02424v1 | GC-MoE: Genomics-Guided Cell-Type-Specific MoE for Histology-Based scST | spatial/MoE | 9 | 3 | 12 | 新发现✅ |
| 4 | 2606.28465v1 | SVC-Probe: Perturbation Generalization in Spatial Foundation-Model Embeddings | representation/benchmark | 7 | 3 | 10 | 新发现✅ |
| 5 | 2607.13508v1 | CDS: Counterfactual Directionality Score for Spatial Graphs | spatial/causal | 7 | 2 | 9 | 新发现✅ |

---

## 🔬 Research Ranking — TOP 10（按 P=R+E 排序，已完整分析）

### A级 | EffiCell-Seg: Rethinking VFM Adaptation for Efficient Cell Segmentation | arXiv:2606.21913 | R:10 E:4 = **P:17** | 算法:confirmed | task:[segmentation, foundation_models]
- **核心思想**：利用预训练 VFM (DINOv3) 编码的结构先验（全局显著性定位 + 局部形态特征）做高效细胞分割。CSP-Encoder 合成结构先验图（语义显著性 + PCA形态），SM-Decoder 通过双向交叉引导联合预测几何距离场和语义图。仅 **~5M 可训练参数**，比全微调 VFM 少 130 倍。
- **代码**: ✅ github.com/xq141839/EffiCell-Seg（4⭐，Python，2026-06）
- **reproduction**: C（有代码，需 DINOv3 权重 + 数据集，~3天）

### A级 | ARGUS: Unsupervised Cell Tracking | arXiv:2607.08297 | R:9 E:4 = **P:14** | 算法:confirmed | task:[tracking, video]
- **核心思想**：四阶段无监督框架：自适应检测(skimage Otsu) → Farneback光流作为每像素运动先验 → 匈牙利线性分配 → 序列级轨迹修复。纯CPU/skimage，无需训练、无需GPU。CTC基准检测0.905-0.971，追踪0.897-0.964，3帧5-6秒。
- **代码**: ✅ github.com/Gitinc/argus（1⭐，Jupyter Notebook）
- **reproduction**: **A（一键运行，纯CPU）**

### A级 | Pic2Spec: Virtual Raman Spectroscopy from Brightfield Images | arXiv:2607.07651 | R:10 E:2 = **P:14** | 算法:confirmed | task:[virtual_imaging, representation_learning]
- **核心思想**：VAE跨模态生成框架，学习共享潜在生化表征连接明场形态特征与Raman振动光谱。哺乳动物+细菌细胞验证：余弦相似度98%、Pearson相关95%。生成的谱能区分基因型状态、预测GFP表达（优于传统图像分析20%）。
- **代码**: ❌ 无公开代码
- **reproduction**: D（需 Raman+明场配对数据，~30天）

### A级 | CellDETR: Detection-Guided Cell Representation Learning | arXiv:2606.29463 | R:10 E:2 = **P:13** | 算法:confirmed | task:[representation_learning, detection]
- **核心思想**：基于Deformable DETR的检测引导框架。位置-表征解耦模块将中心(x,y)和尺寸(w,h)分别投影；Box约束注意力用tanh+box缩放限制采样范围到检测框内；细胞级对比学习将DINO-SSL从patch级扩展到cell级，支持无标注WSI预训练。PanNuke数据上超越SOTA。
- **代码**: ✅ 论文声明开源
- **reproduction**: C（需PanNuke + Xenuim ST注释，~5天）

### A级 | DriftST: One-Step Generative ST from H&E | arXiv:2607.04740 | R:10 E:3 = **P:14** | 算法:inferred | task:[spatial_biology, virtual_imaging]
- **核心思想**：单步生成式推理从H&E组织学图像推断空间转录组基因表达，绕开迭代/自回归方法。
- **代码**: ✅ github.com/yyh030806/DriftST（4⭐，PyTorch）
- **reproduction**: C

### A级 | SheafStain: Sheaf-Theoretic Virtual Staining | arXiv:2606.11846 | R:10 E:2 = **P:14** | 算法:inferred | task:[virtual_imaging]
- **核心思想**：层叠理论Schrödinger桥实现空间一致性虚拟染色。
- **代码**: 论文链接
- **reproduction**: C

### B级 | CellPrior-Net: Prior-Guided Nuclei Detection for H&E WSI | arXiv:2607.00802 | R:8 E:3 = **P:13** | 算法:confirmed
- **核心思想**：H通道DoG多尺度滤波先验 + 轻量CNN，4通道输入（H&E + DoG mask）联合输出核分割+分类（免疫/肿瘤/其他）。8个基准数据集验证，新贡献ILCD数据集（40例肝癌WSI）。
- **代码**: ✅ github.com/Falah-Jabar-Rahim/CellQuant-Net（1⭐，Python）
- **reproduction**: C

### B级 | UCell: Rethinking Small Model Scaling | arXiv:2604.00243 | R:8 E:3 = **P:13** | 算法:confirmed
- **核心思想**：10-30M参数递归计算图架构，单细胞分割性能比肩10-20倍大模型。可从头训练（无需自然图像预训练），支持one-shot/few-shot微调。
- **代码**: ✅
- **reproduction**: C

### B级 | ImPartial: Multi-channel Segmentation with Scribbles | arXiv:2605.24128 | R:8 E:3 = **P:13** | 算法:confirmed
- **核心思想**：U-Net + 自监督多通道量化重建（混合高斯分布建模），L_joint = (1-λ)L_seg + λL_mix。scribble弱监督即达全监督水平，适用于多通道/可变通道配置。
- **代码**: ✅ github.com/nadeemlab/ImPartial（45⭐，活跃维护）
- **reproduction**: C

### B级 | Boundary-Aware Instance Segmentation (SDF) | arXiv:2603.21206 | R:8 E:3 = **P:13** | 算法:confirmed
- **核心思想**：SDF（符号距离函数）预测替代二值掩码，sigmoid映射到概率图实现锐利边界。U-Net多尺度 + 可微Modified Hausdorff Distance (MHD)损失。prompt-free，密集细胞场景超越SAM系方法。
- **代码**: ✅
- **reproduction**: C

---

## 📊 流水线状态

- **完整分析**: 20/74 passed papers（从14→20，本轮+6）
- **待分析**: 54 papers（subagent.py 后端不可用，pipeline阻塞在早期阶段）
- **新论文入库**: 5（2607.14410, 2606.21605, 2606.02424, 2606.28465, 2607.13508）
- **DB总计**: 78 papers（74 passed, 4 failed）

## ⚠️ 已知问题

1. **subagent.py 后端不可用**：Agents-A1 API (10.0.0.245:8037) 内部IP无法从当前环境访问，导致54篇论文停留在 github_search/task_analysis 等早期阶段
2. **建议**：若恢复 Agents-A1 访问，可批量重跑 subagent.py 完成剩余54篇的自动分析
3. **本轮替代方案**：手动从PDF提取方法章节，直接更新DB（6篇高优先级论文已完整分析）

## 🧬 领域分布（通过relevance的74篇）

- **Segmentation**: ~30篇（主流，含foundation model应用、弱监督、SDF、递归架构）
- **Spatial Biology / Virtual Imaging**: ~20篇（ST推理、虚拟染色、跨模态）
- **Representation Learning**: ~12篇（细胞级对比学习、MoE、自监督）
- **Tracking / Video**: ~6篇（光流、Transformer、3D时域）
- **Detection / Counting**: ~4篇（Yolo、核检测）
- **Causal / Graph Analysis**: ~2篇（CDS、方向性评分）
