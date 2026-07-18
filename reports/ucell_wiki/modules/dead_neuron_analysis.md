# dead_neuron_analysis

> 提供一套完整的工具，用于在推理阶段检测和分析FRM模型中的死亡神经元。

该模块通过注册前向钩子（forward hooks）收集模型特定层（如SwiGLU）的激活数据，计算每个神经元的统计指标（均值、标准差、最大值、最小值、零激活比例等），并据此识别在推理过程中持续保持零或接近零激活状态的神经元。这些死亡神经元通常指示模型存在初始化不良、梯度流动问题、架构不匹配或过度正则化等隐患。模块支持快速层级分析和详细的神经元级分析，并自动集成项目现有的数据加载流程。

## Files

### `dead_neuron_analysis/detect_dead_neurons.py`

执行快速的层级层面死亡神经元检测，输出汇总报告和统计摘要。

- `DeadNeuronDetector` (class) - 核心检测器类，负责注册钩子、收集激活统计信息并生成报告。
- `register_hooks` (method) - 遍历模型模块，为匹配指定类（如SwiGLU）的层注册前向钩子。
- `_make_hook` (method) - 工厂函数，为每个目标层创建捕获激活值并计算统计量（均值、标准差、零激活比例等）的钩子函数。

### `dead_neuron_analysis/analyze_neurons_advanced.py`

执行详细的神经元级分析，输出每个神经元的激活直方图、重要性排名及详细统计CSV。

- `AdvancedNeuronAnalyzer` (class) - 高级分析器类，在DeadNeuronDetector基础上进一步计算每个神经元的详细统计指标。
- `_make_detailed_hook` (method) - 创建钩子函数，不仅收集统计量，还保存原始激活张量以便后续进行神经元级别的详细分析。
- `get_neuron_stats` (method) - 计算并返回每个神经元的详细统计信息，包括均值、标准差、最大/最小值、活跃样本比例等。

## Key Concepts

- **死亡神经元 (Dead Neurons)**: 在推理过程中，激活值持续为零或接近零（低于设定阈值，默认1e-5）的神经元。这通常意味着该神经元未参与有效计算，可能由初始化不当、梯度消失或架构问题导致。
- **前向钩子 (Forward Hooks)**: PyTorch机制，用于在模型前向传播过程中拦截并记录特定层的输出张量，是本模块收集激活数据的核心手段。
- **数据依赖性 (Data Dependency)**: 死亡神经元的检测结果高度依赖于输入数据。模块强制使用真实数据（SCS数据集）而非随机噪声，以确保结果反映模型在实际生产环境中的表现。
- **层级统计 vs 神经元统计**: detect_dead_neurons.py提供层级的汇总统计（如该层死亡神经元比例），而analyze_neurons_advanced.py提供每个神经元的独立统计，支持更深入的故障诊断。

## Internal Relationships

- `detect_dead_neurons.py` → `analyze_neurons_advanced.py`: 两者结构相似，analyze_neurons_advanced.py可视为detect_dead_neurons.py的增强版，提供了更细粒度的神经元级分析。
- `detect_dead_neurons.py` → `data.py`: 通过导入data.scs函数，自动使用项目现有的数据加载流程和真实数据集进行分析。
- `analyze_neurons_advanced.py` → `data.py`: 同样依赖data.scs进行数据加载，确保分析基于真实推理数据。
- `detect_dead_neurons.py` → `ucell.layers`: 导入并筛选需要监控的层类型（如SwiGLU）。
- `analyze_neurons_advanced.py` → `ucell.layers`: 导入并筛选需要监控的层类型（如SwiGLU）。
