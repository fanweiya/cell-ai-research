# MalariAI

> 疟疾血涂片细胞分割与分期分类系统

MalariAI 是一个两阶段解耦框架，用于密集疟疾血涂片的通用细胞分割和可解释分期分类。第一阶段使用距离变换引导的水滴算法隔离所有细胞，不受标注完整性影响；第二阶段使用 EfficientNet-B0 结合 Focal Loss 进行多类感染分期识别，并通过 Grad-CAM++ 生成空间注意力热力图。

## Tech Stack

- **Python** 3.10+ (language)
- **PyTorch** 2.1+ (framework)
- **Flask** 3.0+ (web_framework)
- **OpenCV** 4.8+ (computer_vision)
- **EfficientNet-B0** N/A (model)

## Key Features

- 标注无关的细胞分割
- 解决密集重叠细胞检测
- 多类感染分期分类
- Grad-CAM++ 可解释性热力图
- 跨数据集零样本验证
- Web 应用部署

## Getting Started

1. 克隆项目仓库并进入目录
2. 创建虚拟环境并安装依赖：pip install -r requirements.txt
3. 将训练好的模型权重放置于 Phase4-WebApp/checkpoints/best.pth
4. 运行 Flask 应用：python Phase4-WebApp/app.py
