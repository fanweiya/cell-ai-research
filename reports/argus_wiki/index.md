# ARGUS

> 时间分辨显微图像细胞追踪框架

ARGUS是一个用于时间分辨显微图像中细胞检测、追踪、分析和可视化的完整框架。它结合了经典图像处理、光流方法和现代追踪算法，旨在提供鲁棒、通用且计算高效的解决方案。

## Tech Stack

- **Python** 3.10+ (language)
- **ITK** 5.4.2 (library)
- **NumPy** 1.x (library)
- **OpenCV** 4.11.0 (library)
- **Matplotlib** 3.x (library)

## Key Features

- 多方法预处理（去噪、亮度校正）
- 局部最大值检测与质心估计
- 光流辅助追踪与距离关联
- 轨迹可视化与均方位移分析
- 自动视频生成

## Getting Started

1. git clone https://github.com/your-repo/ARGUS.git
2. cd ARGUS
3. pip install -r requirements.txt
4. jupyter notebook
