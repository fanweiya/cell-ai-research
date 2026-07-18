# Cell Tracking & Trajectory Analysis

## 2026-07-11 | SpaCellAgent: A Self-Evolving LLM-Based Multi-Agent Framework for Trajectory Analysis | arXiv:2607.07467 | 核心方法：多智能体强化学习 + 轨迹优化 + 自我进化 | 复现级别：B | priority: 9+5=14

**论文概述**：针对传统轨迹推断方法在空间转录组数据中难以捕捉复杂细胞状态演化路径的问题，SpaCellAgent 采用自进化大语言模型多智能体框架，通过多智能体协作与自我进化机制，动态调整分析策略，适应不同数据集的异质性，提升轨迹推断的准确性和可解释性。

**算法要点**：
- 损失函数：`L_total = λ1 * L_trajectory + λ2 * L_agent_collaboration + λ3 * L_evolution`
- 核心数学原理基于多智能体强化学习与轨迹优化
- 数据流：input → api_handler → feature_extractor → model_inference → output_formatter → response

**性能**：轨迹准确率 0.92, 比 Monocle3 快 3.5 倍

---