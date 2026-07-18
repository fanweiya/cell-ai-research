# 架构

**类型：** 流水线

DART-MLCI 实现了一个用于微流控芯片分析的模块化图像处理流水线，结合了标记检测、几何对齐和细胞分割。该系统支持命令行工具（CLI）和 FastAPI 服务，核心处理逻辑与编排脚本之间有着清晰的分离。

## 组件图

```mermaid
graph TD
  CLI_Scripts --> Core_Library
  CLI_Scripts --> Calibration_Module
  CLI_Scripts --> Registration_Module
  API_Service --> Core_Library
  API_Service --> Calibration_Module
  API_Service --> Registration_Module
  Core_Library --> Visualization
  Calibration_Module --> Registration_Module
  Configuration --> Core_Library
  Configuration --> API_Service
```

## 组件

### core_library

核心图像处理与分析逻辑

文件：`dart_mlci/__init__.py`, `dart_mlci/analysis.py`, `dart_mlci/chip.py`, `dart_mlci/detection.py`, `dart_mlci/mask.py`, `dart_mlci/match.py`, `dart_mlci/rotation.py`, `dart_mlci/pipeline.py`

### calibration_module

标定与坐标系对齐

文件：`dart_mlci/calibration/__init__.py`, `dart_mlci/calibration/core.py`, `dart_mlci/calibration/validation.py`, `dart_mlci/map.py`

### registration_module

图像配准与对齐算法

文件：`dart_mlci/registration/__init__.py`, `dart_mlci/registration/_base.py`, `dart_mlci/registration/_ncc.py`, `dart_mlci/registration/_phase_corr.py`

### api_service

用于远程处理的 FastAPI REST API

文件：`dart_mlci/api/main.py`, `dart_mlci/api/models.py`, `dart_mlci/api/settings.py`, `dart_mlci/api/utils.py`

### cli_scripts

用于批量处理和分析的命令行工具

文件：`scripts/process_folder.py`, `scripts/process_experiment.py`, `scripts/calibrate_map.py`, `scripts/batch_masking.py`, `scripts/benchmark.py`, `scripts/analyze_growth.py`

### visualization

图像渲染与视频生成

文件：`dart_mlci/visualization/__init__.py`, `dart_mlci/visualization/drawing.py`, `dart_mlci/visualization/plotting.py`, `dart_mlci/visualization/rendering.py`, `dart_mlci/visualization/video.py`

### configuration

统一的配置管理

文件：`dart_mlci/config.py`, `dart_mlci/constants.py`, `dart_mlci/types.py`

## 序列图

```mermaid
sequenceDiagram
  participant User
  participant CLI as CLI 脚本
  participant Core as 核心库
  participant API as API 服务
  participant Storage as 文件存储
  
  User->>CLI: 运行 process_folder.py
  CLI->>Core: 加载图像和配置
  Core->>Core: 标记检测
  Core->>Core: 标记匹配
  Core->>Core: 图像旋转
  Core->>Core: ROI 掩膜
  Core->>Storage: 保存结果
  
  User->>API: POST /process-image
  API->>Core: 处理图像请求
  Core->>Core: 执行流水线步骤
  API->>User: 返回 JSON 响应
```

## 数据流

图像从输入源（TIFF 堆栈或单张图像）开始，流经一个顺序流水线：使用 YOLO 进行标记检测、十字/圆形标记的几何匹配、旋转校正以及 ROI 掩膜。处理后的数据可进一步用于细胞分割和生长统计分析，结果以 CSV 文件和可视化形式存储。