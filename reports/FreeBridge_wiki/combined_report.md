# FreeBridge — 综合分析报告

- **GitHub**: Y-Research-SBU/FreeBridge
- **评分**: 7.5/10
- **分析时间**: 2026-07-15T18:25:16.429420

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/FreeBridge_wiki`
- 📄 生成文件:
  - architecture.md
  - dependencies.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/configs.md
  - modules/data_prep.md
  - modules/freebridge.md
  - modules/root.md
- 输出: Project: FreeBridge
Files:   43
Lines:   8,335
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │    32 │
│ markdown │     3 │
│ yaml     │     3 │
│ shell    │     2 │
│ unknown  │     2 │
│ html     │     1 │
└──────────┴───────┘
FreeBridge/
├── ⚙️ README.md (markdown)
├── ⚙️ setup.py (python)
├── 📁 scripts/
│   └── 📄 train.sh (shell)
├── 📁 .codegraph/
│   └── 📄 .gitignore (unknown)
├── 📄 .gitignore (unknown)
├── 📄 CONTRIBUTING.md (markdown)
├── 📄 LICENSE.md (markdown)
├── 📁 configs/
│   ├── 📄 experiment/bbbc021.yaml (yaml)
│   └── 📄 train.yaml (yaml)
├── 📁 data_prep/
│   ├── 📄 __init__.py (python)
│   ├── 📄 build_bbbc021_endpoints.py (python)
│   ├── 📄 cellvae_adapter.py (python)
│   ├── 📄 crop_bbbc021_singlecell.py (python)
│   ├── 📄 export_latents_from_vae.py (python)
│   ├── 📄 export_latents_mu.py (python)
│   ├── 📄 finetune_decoder_lpips.py (python)
│   ├── 📄 gen_cells.py (python)
│   ├── 📄 make_split.py (python)
│   ├── 📄 run_week.s

## 原有子代理分析报告

```
现在我已经收集了足够的信息来生成分析报告。让我整理一下：

## **项目概述**

**FreeBridge** 是一个基于 **变分 Schrödinger 桥梁（Variational Schrödinger Bridges）** 的方法，用于从**仅端点数据**中建模单细胞扰动响应。论文发表在 **MICCAI 2026** (arXiv:2606.11286)。

**主要解决的问题**：
- 单细胞图像分析中，只有处理前（对照）和处理后（扰动）两种端点状态，无法获得细胞随时间变化的轨迹
- 需要推断生物学合理的连续扰动轨迹
- 确保生成的中间状态保持在观测到的细胞形态流形上

**核心理念**：将自由能与流形约束结合，使用经验支持成本（empirical support cost）来约束中间状态在控制与扰动端点构成的流形上。

---

## **架构分析**

### 目录结构
```
FreeBridge/
├── configs/              # Hydra配置
│   ├── experiment/       # 实验配置模板
│   └── train.yaml        # 主配置
├── data_prep/            # 数据预处理脚本
│   ├── crop_bbbc021_singlecell.py   # 细胞图像裁剪
│   ├── train_vae_full.py             # 训练VAE编解码器
│   ├── export_latents_from_vae.py    # 导出VAE潜在变量
│   ├── build_bbbc021_endpoints.py    # 构建端点数据集
│   └── ...
├── freebridge/           # 核心算法代码
│   ├── pl_model.py          # Lightning训练模块（主流程）
│   ├── sde.py               # SDE求解器
│   ├── state_cost.py        # 状态成本函数（核心创新）
│   ├── dataset.py           # 数据集和采样器
│   ├── gaussian_path.py     # 高斯路径建模
│   ├── match_loss.py        # 匹配损失函数
│   ├── network.py           # 神经网络构建
│   ├── unet.py              # UNet网络（图像任务）
│   └── ...
├── scripts/           # 训练脚本
├── train.py         # 训练入口
└── sample_bbbc021_latents.py  # 推理采样脚本
```

### 核心模块关系
1. **数据流**：原始细胞图像 → VAE编码 → 潜在端点 → 桥梁匹配训练
2. **训练流程**（Lightning模块）：
   - M-step：桥匹配损失训练漂移网络
   - R-step（验证步）：拟合高斯路径（带支持成本）
   - 交替优化

### 依赖
- PyTorch Lightning **1.x** (1.8.5.post0) - 注意：不支持2.x
- Hydra 1.2.x (配置管理)
- PyTorch 2.0.1 + CUDA 11.7
- 常用科学计算库：numpy, scipy, torchmetrics等

---

## **核心算法实现原理**

### **1. 自由Bridge 核心公式（Schrödinger Bridge）**

```
漂移 = 基础漂移 + 桥梁漂移
free drift + diffusion drift
```

在 `pl_model.py` 中，核心是交替优化：

**M-step（训练步）**：桥匹配损失
```python
# match_loss.bm_loss() - 给定时钟，学习与桥漂移
loss = (pred_vt - vt)²
```
或者使用**熵作用匹配（EAM）**：
```python
# match_loss.eam_loss_trajs()
# 更精确，但计算量大
```

**R-step（R-step）**：高斯路径拟合（带支持成本）
```python
# gaussian_path.fit()
# 优化样条系数，最小化：cost_s (支持成本) + cost_c (桥成本)
```

### **2. 经验支持成本（Empirical Support Cost） - 核心创新**

在 `state_cost.py` 的 `EmpiricalSupportStateCost` 类中实现：

```python
V_t(z) = λ * d_emp(z)²
```

其中 `d_emp(z)` 是点 z 到**当前小批量端点集合**（控制+扰动）的欧氏距离。这确保了中间状态不会偏离观测到的细胞形态流形。

特性：
- 使用当前批量端点作为支持集（`support_bank`）
- 支持分块计算（chunked cdist）避免内存爆炸
- λ 可调节：0 退化为 CellFlux 基线，0.5 最佳

### **3. 高斯路径建模**

在 `gaussian_path.py` 的 `EndPointGaussianPath` 类：

```
路径 = 均值样条 (EndPointSpline) + 标准差样条 (StdSpline)
```

- 均值路径：描述从对照到扰动的趋势
- 标准差路径：伴随扩散系数
- 支持事件化采样：`sample_xt()` 生成路径的分布表示

### **4. SDE 数值积分**

在 `sde.py` 的 `sdeint` 函数：
```python
# forward Euler-Maruyama
x + u*dt + g*dW
```
从源分布采样正向积分得到目标；或反向积分。

### **5. 数据流**

1. VAE编码器将细胞图像编码为64维潜在向量
2. 控制p0和扰动p1作为独立端点分布
3. 训练中交替进行M/R步
4. R步后，用拟合的高斯路径更新训练数据

---

## **代码质量评估**

### **优点**
1. **结构清晰**：模块职责明确，separation of concerns优秀
2. **Lightning 1.x 兼容**：良好的版本兼容性处理（try/except多个版本）
3. **松弛的边界检查**：在关键数学计算前均有shape验证
4. **记忆管理**：注意使用detach、gc.collect()、cuda.empty_cache()
5. **HPC友好**：支持多GPU DDP、SLURM集成

### **待改进**
1. **文档不足**：
   - 代码注释偏少，数学公式需对照论文
 
```

> 完整报告: [reports/FreeBridge.md](FreeBridge.md)