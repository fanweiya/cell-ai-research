# Chain-of-Prompts (CoP)

> 单点击细胞类型实现训练-free群体交互分割

该项目实现了一种无需训练的细胞实例分割方法，通过Chain-of-Prompts (CoP)技术将每个细胞类型只需一次点击即可分割所有同类细胞。相比传统方法需要为每个细胞单独点击，CoP将交互复杂度从O(N)降低到O(T)，在11个基准测试中平均减少97.6%的标注点击量。

## Tech Stack

- **Python** 3.10+ (language)
- **PyTorch** 2.1+ (framework)
- **SAM 3** latest (model)
- **Gradio** 4.0+ (ui)

## Key Features

- 训练-free的细胞分割
- 单点击多实例分割
- 支持11个基准测试
- 统一SAM接口
- 交互式演示Notebook

## Getting Started

1. 克隆项目仓库并进入目录
2. 安装依赖：pip install -r requirements.txt
3. 配置CUDA版本安装匹配的PyTorch
4. 运行示例或启动Gradio演示界面
