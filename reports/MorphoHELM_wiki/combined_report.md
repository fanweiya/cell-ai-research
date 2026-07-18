# MorphoHELM — 综合分析报告

- **GitHub**: microsoft/MorphoHELM
- **评分**: 8.0/10
- **分析时间**: 2026-07-15T18:30:26.125057

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/MorphoHELM_wiki`
- 📄 生成文件:
  - architecture.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/benchmarks.md
  - modules/configs.md
  - modules/data-preprocessing.md
  - modules/data.md
  - modules/data_installation.md
- 输出: Project: MorphoHELM
Files:   140
Lines:   16,045
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │    66 │
│ unknown  │    56 │
│ yaml     │    11 │
│ markdown │     4 │
│ toml     │     1 │
│ text     │     1 │
│ json     │     1 │
└──────────┴───────┘
MorphoHELM/
├── ⚙️ README.md (markdown)
├── 📁 benchmarks/
│   ├── ⚙️ config.py (python)
│   ├── 📄 configs/benchmarks.yaml (yaml)
│   ├── 📄 enrichment/bbbc036_moa/run_bbbc036_moa.py (python)
│   ├── 📄 enrichment/cpg_moa/build_moa_profiles.py (python)
│   ├── 📄 enrichment/cpg_moa/plot_enrichment_vs_cutoff.py (python)
│   ├── 📄 enrichment/cpg_moa/plot_moa_pooled_or_skewness.py (python)
│   ├── 📄 enrichment/cpg_moa/plot_moa_results.py (python)
│   ├── 📄 enrichment/cpg_moa/run_cpg_moa.py (python)
│   ├── 📄 enrichment/cpg_moa/run_cpg_moa_enrichment.py (python)
│   ├── 📄 enrichment/cpg_moa/run_moa_enrichment.py (python)
│   ├── 📄 enrichment/crispr/crispr_enrichment_utils.py (python)
│   ├── 📄 enri

## 原有子代理分析报告

```
看起来本地路径不存在，但 MCP 工具可以从 GitHub 读取代码。让我基于 GitHub 代码分析结果来生成深度报告。

## 项目概述

**MorphoHELM** 是微软推出的 **Cell Painting** 表征评测基准框架，对应论文 *"MorphoHELM: A Comprehensive Benchmark for Evaluating Representations for Microscopy-Based Morphology Assays"* (arXiv 2605.15383)。核心目标是建立统一的 Cell Painting 表征评测标准，跨数据集和任务比较经典形态特征（CellProfiler）与深度模型（DINOv2、ResNet、CLOOME等），并发现**没有一种深度表征能在所有任务上占优**。

**主要解决的问题：**
- Cell Painting 表征方法碎片化，缺乏统一评测框架
- 不同数据集（CPG0016、BBBC036）和任务（MoA分类、CRISPR富集、复现性分析）间难以公平比较
- 深度模型与经典方法的系统性对比缺失

---

## 架构分析

### 目录结构
```
MorphoHELM/
├── data_installation/          # 数据下载与光照校正
├── raw_to_huggingface/         # 转换为HuggingFace数据集
├── feature-extraction/         # 特征提取核心
│   ├── src/
│   │   ├── models/             # 模型包装器（DINOv2, ResNet, CLOOME等）
│   │   ├── utils/              # 工具函数
│   │   └── run_inference.py    # 推理入口
│   └── configs/                # 推理配置
├── data-preprocessing/         # 数据预处理与标准化
├── benchmarks/                 # 基准测试模块
│   ├── enrichment/             # 富集分析
│   └── replicate_analysis/     # 复现性分析
└── configs/                    # 全局配置
```

### 主要模块
1. **数据安装**：下载公开原始图像→光照校正→保存为uint8 PNG
2. **HuggingFace转换**：将校正后图像转为HF数据集格式
3. **特征提取**：支持8种模型（DINOv2、ResNet、VGG19、OpenPhenom、CLOOME、SubCell）
4. **聚合**：将多GPU推理结果聚合为well-level parquet
5. **标准化**：Plate-level CenterScale → PCA → MAD稳健化
6. **基准测试**：MoA富集、CRISPR富集、kNN复现性、mAP评估

### 依赖关系
- 核心：numpy, pandas, pyyaml, Pillow, scipy, scikit-learn
- ML框架：torch, torchvision, transformers, timm, datasets
- 数据加载：HuggingFace `cellpainting_huggingface_loader`（本地包）

---

## 核心算法

### 1. 光照校正算法
```python
def correct_cpg0016_to_uint8(image, illumination):
    corrected = image / illumination  # 逐像素除法
    vmin, vmax = np.percentile(corrected, (0.05, 99.95))
    corrected = (corrected - vmin) / (vmax - vmin)  # 百分位对比度拉伸
    return to_uint8(corrected)
```
- 对CPG0016使用**百分位裁剪**（0.05%和99.95%）
- 对BBBC036使用**全范围归一化**
- 两者最终转换为uint8 PNG

### 2. 多模型统一接口
所有模型继承 `ModelWrapper`基类：
```python
class ModelWrapper:
    def _load_model(self): abstract
    def infer(self, data_input): abstract
    def postprocess(self, data_input, model_output): abstract
```
- 支持单通道模型（DINOv2、ResNet）和**多通道模型**（CLOOME、SubCell）
- 单通道模型将单通道重复3通道并应用ImageNet标准化
- 多通道模型保持5通道原样，使用特定预处理

### 3. 特征聚合策略
根据模型类型采用不同聚合方式：
- **单通道模型**：按(plate, well, fov, channel)平均→跨通道拼接
- **OpenPhenom**：按(plate, well, fov)平均
- **CLOOME/SubCell**：按(plate, well)平均（5通道已堆叠）

### 4. 标准化流程
默认配置：`CSAll_Plate__PCA64__MADCtrl_Plate__NoSph`
1. **Plate-level CenterScale**：每块板内所有细胞归一化
2. **PCA降维**：64个主成分
3. **MAD稳健化**：基于对照样本的Median Absolute Deviation标准化
4. **不球化**（NoSph）

---

## 代码质量

### 优点
✅ **文档极其详尽**：README超过1500行，包含完整使用流程和参数说明
✅ **模块化设计**。各阶段解耦（安装、推理、聚合、标准化、基准），易于替换组件
✅ **配置驱动**。使用YAML管理实验配置，支持多模式（local/amlt）
✅ **错误处理**。大量验证逻辑（Validate函数），失败即停避免静默错误
✅ **并行化完善**。支持GPU多进程、CPU多进程、流式聚合

### 不足
⚠️ **测试覆盖有限**：未见专用测试目录，仅在README中有smoke test描述
⚠️ **重量级依赖**。需要大量空间和GPU内存，小型实验门槛高
⚠️ **文档复制粘贴痕迹**。坐标“you are”等调试信息未清理
⚠️ **错误日志分散**。每个GPU进程单独记录，调试需聚合多文件

### 可读性评分：8/10
代码注释充分，函数命名清晰，但部分工
```

> 完整报告: [reports/MorphoHELM.md](MorphoHELM.md)