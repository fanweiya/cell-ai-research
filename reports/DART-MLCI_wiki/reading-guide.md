# Reading Guide

本代码库是一个用于DART微流控芯片图像分析的系统，涉及从图像预处理、芯片校准到实验处理和可视化的完整流程。建议按配置->入口->核心逻辑->工具链的顺序阅读，以建立整体认知。

## Step 1: 理解项目配置与依赖 (~15 min)

**Files:** `README.md`, `pyproject.toml`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`

首先阅读README.md了解项目概述和快速开始指南；然后查看pyproject.toml和requirements.txt理解项目依赖和构建配置；最后看Dockerfile和docker-compose.yml了解容器化部署方式。这有助于建立环境认知。

## Step 2: 掌握核心API入口 (~20 min)

**Files:** `dart_mlci/api/main.py`

作为API主入口，main.py定义了Web服务接口和路由。重点关注API端点设计、中间件配置和请求处理流程，这是理解系统对外交互的关键。

## Step 3: 理解配置管理模块 (~15 min)

**Files:** `dart_mlci/config.py`

config.py包含所有配置参数和常量定义。重点关注环境配置、路径设置、模型参数和实验配置结构，这是理解系统行为的基础。

## Step 4: 探索核心实验处理逻辑 (~30 min)

**Files:** `scripts/process_experiment.py`, `scripts/process_folder.py`

这两个脚本是核心处理逻辑，分别处理单个实验和批量文件夹。重点关注图像预处理流程、芯片校准算法、细胞分割方法和结果生成机制。

## Step 5: 学习校准与验证流程 (~25 min)

**Files:** `scripts/calibrate_map.py`, `scripts/calibrate_pixel_scale.py`, `scripts/prepare_calibration_data.py`

这些脚本负责芯片校准和像素尺度验证。重点关注坐标映射算法、校准数据生成流程和验证方法，理解如何确保图像与芯片结构的精确对齐。

## Step 6: 了解数据生成与可视化 (~20 min)

**Files:** `scripts/generate_dart_frame_video.py`, `scripts/generate_sak_videos.py`, `scripts/generate_golden_files.py`

这些脚本用于生成视频和参考文件。重点关注视频生成逻辑、帧处理方式和golden文件的作用，理解如何创建演示和验证材料。

## Step 7: 掌握分析与基准测试 (~20 min)

**Files:** `scripts/analyze_growth.py`, `scripts/benchmark.py`

分析脚本处理实验数据并生成生长曲线，基准测试脚本评估系统性能。重点关注数据分析方法和性能指标计算，理解如何量化实验结果。

## Step 8: 理解辅助工具与脚本 (~15 min)

**Files:** `scripts/batch_masking.py`, `scripts/generate_chip_config.py`

这些是辅助工具，用于批量掩膜处理和芯片配置生成。重点关注掩膜生成逻辑和配置自动化流程，理解如何提高工作效率。

## Tips

- 先阅读README.md建立整体概念，再深入具体代码
- 重点关注数据流向：从图像输入到结果输出的完整路径
- 注意配置文件中的路径设置，理解相对路径和绝对路径的使用
- 结合测试文件理解预期行为，特别是process_experiment.py的测试用例
- 遇到复杂算法时，先理解输入输出接口，再深入实现细节
