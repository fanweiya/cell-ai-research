# EffiCell-Seg

> 一种基于冻结的 DINOv3 骨干网络和 SAM 风格解码器的提示引导细胞实例分割框架。

EffiCell-Seg 通过结合冻结的 DINOv3 视觉模型特征与 SAM 风格解码器，实现单个细胞的分割。它利用类 token 相似性和补丁特征的 PCA 生成自提示，随后采用双分支解码器预测前景和几何输出。几何分支可在四种不同范式（tsfd、hovernet、stardist、cellpose）之间切换，以适应各种分割需求。

该项目支持两种运行模式：在线模式在训练期间运行 DINOv3 骨干网络，而缓存模式则预先计算一次特征以加速大型模型的训练。项目通过 PyTorch 支持分布式训练，并支持 LoRA 以实现参数高效微调。

## 技术栈

- **Python** 3.10+（编程语言）
- **PyTorch** 2.1+（框架）
- **DINOv3** timm（视觉模型）
- **LoRA** peft（参数高效微调）
- **MONAI** latest（医学影像）

## 核心功能

- 冻结的 DINOv3 骨干网络用于特征提取
- 基于类 token 相似性和 PCA 的自提示生成
- 可切换的几何分支，支持四种分割范式
- 在线与缓存特征提取模式
- 双分支解码器，采用交叉注意力融合
- 支持 LoRA 参数高效微调

## 快速开始

1. 克隆仓库并进入项目目录
2. 创建 Python 3.10 的 conda 环境并激活
3. 安装核心依赖：torch、torchvision、timm、peft、monai、opencv-python、scikit-image、scipy、pandas、numpy、tqdm
4. 准备数据集：将图像、实例标签图（.npy）和 ids.json 文件放入 ./datasets/<DATASET>/processed 目录