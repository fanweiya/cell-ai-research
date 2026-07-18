# Reading Guide

本代码库是一个用于CBVCC挑战赛的视频分类评估工具包。建议按从宏观配置到核心逻辑，再到具体指标实现的顺序阅读，以快速理解整体架构和关键功能。

## Step 1: 理解项目概览与依赖 (~10 min)

**Files:** `README.md`, `environment.yml`

首先阅读README.md了解项目背景、主要功能和使用方法；接着查看environment.yml确认Python依赖包和版本，确保开发环境一致。

## Step 2: 掌握核心评估流程 (~15 min)

**Files:** `run_analysis.py`, `eval_code.php`

run_analysis.py是Python主入口，展示如何调用指标模块；eval_code.php是PHP接口，可能用于外部调用或集成。重点关注函数调用链和参数传递方式。

## Step 3: 学习指标计算核心 (~20 min)

**Files:** `metrics/overall_metrics.py`, `metrics/compute_quality_metrics.py`

overall_metrics.py可能汇总所有指标，compute_quality_metrics.py实现具体质量指标计算。寻找指标定义、计算逻辑和输出格式。

## Step 4: 理解统计描述与可视化 (~15 min)

**Files:** `metrics/descriptives.py`, `metrics/roc_curves.py`, `metrics/snr_curves.py`, `metrics/ncell_curves.py`

这些文件负责生成统计描述和可视化图表。关注数据预处理、绘图库选择（如matplotlib）和图表生成逻辑。

## Step 5: 探索辅助工具与数据生成 (~10 min)

**Files:** `metrics/generate_gt.py`, `metrics/upload_files.py`

generate_gt.py可能用于生成真实值数据，upload_files.py处理文件上传。了解数据准备流程和外部数据交互方式。

## Step 6: 检查代码图缓存机制 (~5 min)

**Files:** `.codegraph/.gitignore`

虽然文件较小，但需理解.codegraph目录的用途，它管理代码图数据的本地缓存和通信，可能影响代码分析工具的性能。

## Tips

- 先运行run_analysis.py了解完整流程，再深入具体指标实现
- 注意metrics目录中各文件的依赖关系，避免孤立阅读
- 关注数据流向：从输入视频到最终可视化报告的完整路径
