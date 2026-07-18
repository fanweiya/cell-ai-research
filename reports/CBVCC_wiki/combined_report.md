# CBVCC — 综合分析报告

- **GitHub**: rcabini/CBVCC
- **评分**: 7.0/10
- **分析时间**: 2026-07-15T18:23:21.072059

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/CBVCC_wiki`
- 📄 生成文件:
  - architecture.md
  - dependencies.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/metrics.md
  - modules/root.md
- 输出: Project: CBVCC
Files:   14
Lines:   1,367
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │     9 │
│ unknown  │     2 │
│ markdown │     1 │
│ yaml     │     1 │
│ php      │     1 │
└──────────┴───────┘
CBVCC/
├── ⚙️ README.md (markdown)
├── 📁 .codegraph/
│   └── 📄 .gitignore (unknown)
├── 📄 LICENSE (unknown)
├── 📄 environment.yml (yaml)
├── 📄 eval_code.php (php)
├── 📁 metrics/
│   ├── 📄 compute_quality_metrics.py (python)
│   ├── 📄 descriptives.py (python)
│   ├── 📄 generate_gt.py (python)
│   ├── 📄 ncell_curves.py (python)
│   ├── 📄 overall_metrics.py (python)
│   ├── 📄 roc_curves.py (python)
│   ├── 📄 snr_curves.py (python)
│   └── 📄 upload_files.py (python)
└── 📄 run_analysis.py (python)
⠋ Done!

Wiki generated: /mnt/c/workspace/cell-ai-research/reports/CBVCC_wiki/

## 原有子代理分析报告

```
现在我已经收集了足够的信息。让我基于分析结果输出结构化报告：

## 项目概述

**CBVCC** (Cell Behavior Video Classification Challenge) 是一个针对活细胞行为视频分类的基准挑战评测仓库。

- **论文来源**: Cell Behavior Video Classification Challenge, a benchmark for computer vision methods in time-lapse microscopy (arXiv 2601.10250)
- **主要问题**: 分类 intravital microscopy (IVM) 拍摄的细胞行为视频，识别细胞运动模式：
  - 方向突然变化的行为
  - 一致线性运动
  - 静止细胞
  - 纯背景
- **核心任务**: 二分类（Class 0 vs Class 1），实质是区分"异常运动" vs "正常/静止/背景"

## 架构分析

### 目录结构
```
CBVCC/
├── metrics/              # 核心模块
│   ├── compute_quality_metrics.py   # 视频质量指标计算
│   ├── generate_gt.py             # 生成标签CSV
│   ├── overall_metrics.py         # 综合评价指标
│   ├── roc_curves.py              # ROC曲线绘制
│   ├── ncell_curves.py            # 细胞数量-分数关系
│   ├── snr_curves.py              # SNR-分数关系
│   ├── descriptives.py            # 分布可视化
│   └── upload_files.py            # 文件处理与数据构建
├── run_analysis.py          # 主分析脚本
├── eval_code.php            # PHP评估脚本
├── environment.yml          # 环境配置
└── README.md                 # 使用说明
```

### 主要模块与依赖关系

1. **数据输入层**
   - 视频 patches (.avi) - 按数据集划分
   - 追踪文件 (.csv) - 细胞追踪结果
   - 提交预测文件 (.csv) - 参赛队伍结果

2. **处理层**
   - `generate_gt.py`: 从目录结构自动生成 ground truth CSV
   - `compute_quality_metrics.py`: 计算 SNR、细胞数量等质量指标

3. **评估层**
   - `overall_metrics.py`: 计算 AUC、Precision、Recall、Balanced Accuracy
   - `roc_curves.py`: 可视化 ROC 曲线

4. **分析层**
   - `ncell_curves.py`: 分析细胞数量对性能的影响
   - `snr_curves.py`: 分析 SNR 对性能的影响

### 技术依赖
- Python 3.9
- OpenCV (视频处理)
- Pandas (数据处理)
- Scikit-learn (评价指标)
- Matplotlib/Seaborn (可视化)
- SciPy (距离计算)
- TensorFlow/Keras (环境文件中包含，但代码未直接使用)

## 核心算法

### 1. 视频质量指标计算 (`compute_quality_metrics.py`)

核心算法流程：
```python
# 关键参数
SAMPLING_DISTANCE = 1
TH_DISTANCE_BG = 20 / 0.8      # 背景区域阈值
TH_DISTANCE_FG = 3 / 0.8       # 前景区域阈值

# 计算指标
SNR = |FG_avg - BG_avg| / BG_std        # 信噪比
CR = FG_avg / BG_avg                    # 对比度
DEN = 细胞间最小距离                    # 细胞密度
```

**实现原理**:
- 从视频中提取灰度帧，预处理为三维数组 (H, W, T)
- 读取追踪 CSV 文件，获取每帧细胞坐标
- 对每帧使用距离变换 (distance_transform_edt) 分割前景/背景
- 在前景和背景区域分别计算灰度统计量
- 汇总每视频的平均 SNR、细胞数量 (N.TRACKS) 等

### 2. 综合评价指标 (`overall_metrics.py`)

采用 CBVCC 官方评分公式：
```python
score = 0.4 * AUC + 0.2 * (Precision + Recall + Balanced Accuracy)
```

其中：
- AUC: ROC曲线下面积
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- Balanced Accuracy = (Sensitivity + Specificity) / 2

### 3. 数据匹配逻辑 (`upload_files.py`)

核心挑战：将预测提交与 ground truth 匹配
```python
def get_nearest_file(timestamp, file_timestamp_dict):
    """根据时间戳找到最近的预测文件"""
    closest_timestamp = min(file_timestamp_dict.keys(), 
                           key=lambda x: abs(x - timestamp))
    return file_timestamp_dict[closest_timestamp]
```

涉及的时间戳 extraction 和文件名规范化：
- 预测文件命名格式：`predicted{timestamp}.csv`
- 视频文件名：类似 `01_1.avi` → `_` 分隔，数字部分补零

## 代码质量

### 优点
- **模块清晰**: 每个脚本职责单一，功能解耦
- **依赖明确**: 使用标准库 + 流行科学计算栈
- **可视化丰富**: 自动输出 ROC 曲线、分布图、质量指标散点图
- **文档完整**: README 包含详细使用示例、数据集结构、评估流程

### 缺点
- **错误处理一般**: 视频读取失败时仅有简单异常捕获和打印
- **缺少单元测试**: 没有 pytest/u
```

> 完整报告: [reports/CBVCC.md](CBVCC.md)