# DART-MLCI — 综合分析报告

- **GitHub**: SMLCI/DART-MLCI
- **评分**: 9.0/10
- **分析时间**: 2026-07-15T18:24:34.502318

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/DART-MLCI_wiki`
- 📄 生成文件:
  - architecture.md
  - dependencies.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/.github.md
  - modules/artifacts.md
  - modules/dart_experiment.md
  - modules/dart_mlci.md
- 输出: Project: dart-mlci
Files:   145
Lines:   57,789
      Languages       
┏━━━━━━━━━━━━┳━━━━━━━┓
┃ Language   ┃ Files ┃
┡━━━━━━━━━━━━╇━━━━━━━┩
│ python     │   103 │
│ json       │    12 │
│ markdown   │    10 │
│ shell      │     7 │
│ yaml       │     5 │
│ unknown    │     5 │
│ dockerfile │     1 │
│ toml       │     1 │
│ text       │     1 │
└────────────┴───────┘
dart-mlci/
├── ⚙️ Dockerfile (dockerfile)
├── ⚙️ README.md (markdown)
├── 📁 dart_mlci/
│   ├── ⚙️ config.py (python)
│   └── 📄 api/main.py (python)
├── ⚙️ docker-compose.yml (yaml)
├── ⚙️ pyproject.toml (toml)
├── ⚙️ requirements.txt (text)
├── 📁 scripts/
│   ├── 📄 analyze_growth.py (python)
│   ├── 📄 batch_masking.py (python)
│   ├── 📄 benchmark.py (python)
│   ├── 📄 calibrate_map.py (python)
│   ├── 📄 calibrate_pixel_scale.py (python)
│   ├── 📄 generate_chip_config.py (python)
│   ├── 📄 generate_dart_frame_video.py (python)
│   ├── 📄 generate_golden_files.py (python)
│   ├── 📄 generate_sak_videos.py (python)
│   ├── 📄 ma

## 原有子代理分析报告

```
现在我已经收集了足够的信息来分析这个仓库。让我创建结构化报告：

## DART-MLCI 项目深度分析报告

### 1. 项目概述

**DART-MLCI** (Design-Aware and Real-Time capable Microfluidic Live-Cell Image analysis) 是一个用于高通量微流控活细胞图像实时分析的软件系统，源自论文 **"DART: A design-aware microfluidic chip paradigm for real-time live-cell image analysis"** (arXiv:2606.18523, 2026)。

**核心问题**：高通量微流控活细胞成像产生大量单细胞数据，但定位包含特定细胞群的区域 (ROI) 以及去除周围微流控结构的操作是半自动的，随着ROI数量增加而变得繁琐，阻碍了实时图像分析。

**解决方案**：通过嵌入式的标记物(fiducial markers)和深度学习标记检测，将CAD蓝图与物理芯片对齐，实现：
- **Fine alignment** (掩膜流水线)：标记物检测、配对匹配、旋转校正、多边形掩膜、ROI裁剪
- **Coarse alignment** (映射校准)：芯片蓝图与显微镜平台坐标的仿射对齐

### 2. 架构分析

**目录结构**：
```
DART-MLCI/
├── dart_mlci/              # 核心Python包
│   ├── __init__.py         # 公开API
│   ├── detection.py        # YOLO标记检测模型
│   ├── match.py            # 标记物匹配算法
│   ├── pipeline.py         # 步骤式处理流水线
│   ├── chip.py             # 芯片配置和结构库
│   ├── mask.py             # 掩膜操作和ROI多边形
│   ├── rotation.py         # 图像和标记物旋转
│   ├── map.py              # 芯片蓝图映射
│   ├── calibration/        # 校准模块
│   ├── registration/       # 图像配准模块
│   └── api/                # FastAPI服务
├── tests/                  # 测试套件
├── artifacts/              # 示例数据和模型
├── scripts/                # 处理脚本
└── docs/                   # 文档
```

**关键依赖**：
- **Ultralytics YOLO**：标记物检测
- **OpenCV + Kornia**：图像旋转和变换
- **Shapely + Rasterio**：几何处理和 masks
- **PyTorch**：深度学习
- **FastAPI**：REST API

### 3. 核心算法

**标记检测** (`detection.py`)：
- 使用YOLO模型检测两种标记：cross和circle
- 置信度过滤和边界框中心提取

**标记匹配** (`match.py`)：
- 通过线性分配算法将检测到的cross和circle标记配对
- 计算匹配距离与期望距离的误差，容忍度设置为5像素
- 考虑置信度加权

**旋转估计** (`rotation.py`)：
- 计算成对标记方向向量与蓝图方向向量的夹角
- 使用带符号角度 (`signed_angle_between`) 获取-180°~180°范围
- 多对标记时取平均，并检查角度一致性

**图像旋转**：
- 支持CPU (OpenCV) 和 GPU (Kornia) 两种路径
- 自动扩展边界以容纳旋转后的完整图像

**掩膜应用** (`mask.py`)：
- 基于匹配标记将ROI多边形定位到图像
- 选择距离图像边界最远的ROI
- 支持旋转-free模式，通过旋转多边形而非图像来节省计算

**芯片配置** (`chip.py`)：
- 统一JSON格式描述芯片设计： chamber多边形、标记位置、蓝图映射
- 从GeoJSON坐标缩放到像素坐标

### 4. 代码质量

**优点**：
- ✅ 模块化设计清晰，各模块职责单一
- ✅ 类型注解完善，使用dataclass
- ✅ 单元测试覆盖核心逻辑
- ✅ 遵循PEP8，使用ruff格式化
- ✅ 详细的文档字符串
- ✅ 版本控制和CI/CD完善

**不足**：
- ⚠️ 部分函数过于通用化，存在双路径（GPU/CPU）可能引入复杂性
- ⚠️ 一些硬编码的坐标转换逻辑在`calibration/core.py`中需要仔细观察
- ⚠️ 缺少集成测试（标记为integration，默认不运行）

### 5. 可复现性

**非常优秀**：
- ✅ `pyproject.toml` 明确声明依赖
- ✅ `Dockerfile` 完整，包含CUDA版本控制
- ✅ `reproduce.sh` 脚本自动化实验复现
- ✅ 自动下载模型和示例数据（~40MB）
- ✅ 详细的配置文档 (`docs/configuration.md`, `docs/CHIP_CONFIG.md`)
- ✅ 支持PyPI安装 (`pip install dart-mlci`)

**安装**：
```bash
pip install ".[dev]"       # 核心 + 开发依赖
pip install ".[api]"       # API服务
pip install ".[segmentation]"  # 分割模型依赖
```

### 6. 与高通量细胞图像分析项目 (YOLO+SAM) 的相关性

**可直接复用的模块**：

1. **标记检测框架** (`MarkerDetectionModel`)：
   - YOLO模型的封装和推理接口
   - 可替换为你的YOLO检测器

2. **标记匹配算法** (`match_markers`)：
   - 适用于需要根据模板匹配成对标记物的场景
   - 线性分配 + 距离约束

3. **芯片配置系统** (`ChipStructureLibrary`)：
   - 统一的JSON配置描述芯片蓝图
   - 支持从几何坐标到像素坐标的转换

4. **流水线架构** (`pipeline.py` 中的Step类)：
   - 链式调用设计 (`detect → match → rotate → mask`)
   - 缓存机制 (`ChamberPipelineCache`) 避免重复初始化

5. **掩膜生成** (`apply_mask`)：
   - 基于多边形
```

> 完整报告: [reports/DART-MLCI.md](DART-MLCI.md)