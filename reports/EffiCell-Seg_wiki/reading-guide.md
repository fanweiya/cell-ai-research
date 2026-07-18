# Reading Guide

本代码库是一个基于 DINOv3 骨干网络和 SAM 风格解码器的细胞实例分割框架。建议按‘配置与概览 -> 核心模型 -> 数据与评估 -> 工具与细节’的顺序阅读，以快速建立整体认知并深入关键逻辑。

## Step 1: 理解项目概览与配置 (~5 min)

**Files:** `README.md`, `.zread/wiki/drafts/wiki.json`

首先阅读 README.md 了解项目目标、依赖和运行方式；接着查看 wiki.json 获取项目文档结构和关键概念索引，建立对 EffiCell-Seg 的整体认知。

## Step 2: 掌握核心模型架构 (~15 min)

**Files:** `model.py`, `segment_anything/modeling/sam.py`, `segment_anything/modeling/image_encoder.py`

model.py 是项目主模型入口，sam.py 实现 SAM 风格解码器，image_encoder.py 封装 DINOv3 骨干网络。重点查看模型如何组合骨干与解码器，以及提示引导机制的实现。

## Step 3: 学习数据加载与预处理 (~10 min)

**Files:** `dataloader.py`, `extract_features.py`

dataloader.py 定义数据加载逻辑，extract_features.py 负责特征提取。关注数据如何输入模型、特征如何被冻结骨干网络处理，以及预处理流程。

## Step 4: 理解评估与指标计算 (~10 min)

**Files:** `eval.py`, `metrics.py`

eval.py 实现模型评估流程，metrics.py 定义分割质量指标。查看评估如何调用模型、输出结果，以及指标如何量化分割性能。

## Step 5: 深入 SAM 风格解码器细节 (~15 min)

**Files:** `segment_anything/modeling/mask_decoder.py`, `segment_anything/modeling/prompt_encoder.py`, `segment_anything/modeling/transformer.py`

mask_decoder.py 生成掩码，prompt_encoder.py 编码提示，transformer.py 处理特征交互。重点理解提示如何影响掩码生成，以及 Transformer 在其中的作用。

## Step 6: 探索自动掩码生成与预测接口 (~10 min)

**Files:** `segment_anything/automatic_mask_generator.py`, `segment_anything/predictor.py`

automatic_mask_generator.py 实现自动掩码生成策略，predictor.py 提供预测接口。了解如何从提示到最终分割结果的完整推理流程。

## Step 7: 熟悉项目工具与缓存机制 (~5 min)

**Files:** `.codegraph/.gitignore`, `segment_anything/__init__.py`

.gitignore 了解忽略规则，__init__.py 查看模块导出。虽然文件较小，但有助于理解项目结构和依赖管理。

## Tips

- 先通读 README 和 wiki.json 建立宏观认知，再深入代码细节。
- 重点关注 model.py 和 sam.py 的交互，这是理解提示引导分割的关键。
- 遇到复杂模块时，先查看调用链，再深入函数内部。
- 结合数据加载和评估流程，理解模型如何被训练和验证。
