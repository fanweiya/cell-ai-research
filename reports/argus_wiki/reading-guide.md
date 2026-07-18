# Reading Guide

本指南旨在帮助你快速理解ARGUS项目的架构与核心逻辑。建议从配置和文档入手，建立整体认知，随后深入核心算法，最后关注工具函数。

## Step 1: 项目概览与环境配置 (~10 min)

**Files:** `README.md`, `requirements.txt`, `.gitignore`

首先阅读README.md了解项目目标、安装步骤和核心功能；查看requirements.txt确认依赖项；通过.gitignore了解被忽略的文件类型，建立项目边界感。

## Step 2: 核心算法逻辑 (~30 min)

**Files:** `src/algo_funcs.py`, `src/algo_funcs_old.py`

这是项目的核心，包含细胞追踪的主要算法。重点关注数据输入输出格式、追踪逻辑、以及新旧版本的差异（如有）。

## Step 3: 数据格式化与处理 (~15 min)

**Files:** `src/ctc_reformat.py`, `src/utils.py`

了解数据如何被预处理和格式化，特别是ctc_reformat.py中的转换逻辑，以及utils.py中的通用辅助函数。

## Step 4: 可视化与结果展示 (~15 min)

**Files:** `src/display_funcs.py`

查看图像如何被渲染和展示，理解可视化模块如何与核心算法交互，以及输出结果的呈现方式。

## Step 5: 参数扫描与实验流程 (~15 min)

**Files:** `src/parameter_scan.py`

了解项目如何自动化运行不同参数组合，这是评估算法性能的关键部分。

## Step 6: 交互式实验与评估 (~20 min)

**Files:** `notebooks/compute_cell_paths.ipynb`, `notebooks/format_tracks_for_CTC.ipynb`

通过Jupyter Notebook查看实际的数据处理流程和结果评估示例，理解算法在真实数据上的应用。

## Tips

- 在阅读核心算法时，建议同时运行notebook中的示例代码以加深理解。
- 注意区分algo_funcs.py和algo_funcs_old.py，了解项目演进历史。
- 遇到复杂逻辑时，先查看函数签名和文档字符串，再深入代码细节。
