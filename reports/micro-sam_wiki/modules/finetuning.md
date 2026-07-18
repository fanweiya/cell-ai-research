# finetuning

> 提供针对显微镜图像的微调、推理和评估脚本，用于将Segment Anything模型适配到特定生物医学数据集。

该模块包含用于微调Segment Anything (SAM) 模型以适用于显微镜图像的代码，分为通用模型（Generalists）和专用模型（Specialists）两大类。通用模型在多个数据集上联合训练以增强泛化能力，而专用模型则针对特定数据集（如LIVECell, DeepBacs, CREMI等）进行微调。模块还包含完整的评估流程，支持自动掩码生成(AMG)、自动实例分割(AIS)和迭代提示交互分割。

## Files

### `finetuning/livecell_finetuning.py`

针对LIVECell数据集微调SAM的专用脚本。

- `get_dataloaders` (function) - 使用torch_em获取LIVECell的训练和验证数据加载器。
- `finetune_livecell` (function) - 执行微调的核心函数，配置模型、优化器并调用sam_training.train_sam。

### `finetuning/livecell_inference.py`

在LIVECell测试集上运行推理的脚本。

- `run_livecell_inference` (function) - 执行LIVECell的推理流程。

### `finetuning/run_all_finetuning.py`

批量提交多个微调实验的脚本（通过Slurm）。

- `submit_slurm` (function) - 根据实验名称和模型类型生成并提交Slurm作业。
- `write_batch_script` (function) - 生成包含SBATCH指令和Python命令的批处理脚本。

### `finetuning/evaluation/util.py`

评估模块的通用工具函数，包括路径获取、数据集下载和模型加载。

- `get_paths` (function) - 根据数据集名称和分割类型获取图像和标签路径。
- `get_default_arguments` (function) - 解析评估脚本的通用命令行参数。
- `download_all_datasets` (function) - 自动下载评估所需的数据集。

### `finetuning/evaluation/precompute_embeddings.py`

预计算图像嵌入（Image Embeddings），供后续推理使用。

- `main` (function) - 加载模型并对验证集和测试集预计算嵌入。

### `finetuning/evaluation/evaluate_amg.py`

运行自动掩码生成(AMG)评估。

- `run_amg_inference` (function) - 调用micro_sam的AMG推理函数。
- `eval_amg` (function) - 计算并保存AMG的评估指标。

### `finetuning/evaluation/evaluate_instance_segmentation.py`

运行自动实例分割(AIS)评估，使用附加的解码器。

- `run_instance_segmentation_with_decoder_inference` (function) - 调用带有解码器的实例分割推理函数。
- `eval_instance_segmentation_with_decoder` (function) - 计算并保存AIS的评估指标。

### `finetuning/evaluation/iterative_prompting.py`

运行迭代提示交互分割评估。

- `_run_iterative_prompting` (function) - 执行迭代提示推理，支持从点或框开始。
- `_evaluate_iterative_prompting` (function) - 评估迭代提示的结果。

### `finetuning/evaluation/cellpose_baseline.py`

运行CellPose基准测试脚本。

- `run_cellpose_segmentation` (function) - 对指定数据集运行CellPose分割。
- `evaluate_dataset` (function) - 评估CellPose分割结果。

### `finetuning/generalists/training/light_microscopy/train_lm_generalist.py`

在多个光显微镜数据集上微调SAM通用模型的脚本。

- `finetune_lm_generalist` (function) - 配置并启动光显微镜通用模型的训练流程。

### `finetuning/generalists/training/light_microscopy/obtain_lm_datasets.py`

构建光显微镜通用模型的联合数据加载器。

- `get_concat_lm_datasets` (function) - 组合多个光显微镜数据集（如LiveCell, EmbedSeg等）形成训练集。

### `finetuning/generalists/training/electron_microscopy/mito_nuc/train_mito_nuc_em_generalist.py`

在多个电子显微镜数据集（线粒体和细胞核）上微调SAM通用模型的脚本。

- `finetune_mito_nuc_em_generalist` (function) - 配置并启动EM通用模型的训练流程。

### `finetuning/generalists/training/electron_microscopy/mito_nuc/obtain_mito_nuc_em_datasets.py`

构建EM通用模型的数据加载器。

- `get_concat_mito_nuc_datasets` (function) - 组合MitoEM和Platynereis等EM数据集。

### `finetuning/specialists/training/light_microscopy/deepbacs_finetuning.py`

针对DeepBacs数据集微调SAM的专用脚本。

- `finetune_deepbacs` (function) - 执行DeepBacs数据集的微调，包含UNETR解码器。

### `finetuning/specialists/training/light_microscopy/tissuenet_finetuning.py`

针对TissueNet数据集微调SAM的专用脚本。

- `finetune_tissuenet` (function) - 执行TissueNet数据集的微调。

### `finetuning/specialists/training/electron_microscopy/boundaries/cremi_finetuning.py`

针对CREMI数据集（边界分割）微调SAM的专用脚本。

- `finetune_cremi` (function) - 执行CREMI数据集的微调。

### `finetuning/specialists/training/electron_microscopy/organelles/asem_finetuning.py`

针对ASEM数据集（细胞器分割）微调SAM的专用脚本。

- `finetune_asem` (function) - 执行ASEM数据集的微调。

### `finetuning/specialists/resource-efficient/covid_if_finetuning.py`

在有限资源下针对COVID-IF数据集微调SAM的脚本。

- `finetune_covid_if` (function) - 支持不同GPU/CPU资源配置和LoRA微调的COVID-IF训练。

### `finetuning/specialists/resource-efficient/run_resource_efficient_finetuning.py`

批量提交资源受限环境下的微调实验脚本。

- `write_batch_sript` (function) - 生成针对不同硬件配置（GTX1080, V100, CPU等）的Slurm脚本。

## Key Concepts

- **通用模型 (Generalist Models)**: 在多个相关数据集上联合训练的SAM模型，旨在提高对不同显微镜图像域的泛化能力。例如光显微镜通用模型和电子显微镜通用模型。
- **专用模型 (Specialist Models)**: 针对单个特定数据集（如LIVECell, DeepBacs）微调的SAM模型，通常在该数据集上能达到更高的性能。
- **自动掩码生成 (AMG)**: Segment Anything的原始功能，无需提示即可生成大量候选掩码。
- **自动实例分割 (AIS)**: micro-sam的扩展功能，通过添加UNETR解码器，直接从图像预测实例分割掩码，无需用户提示。
- **迭代提示 (Iterative Prompting)**: 交互式分割方法，用户通过放置正/负点或框来引导模型，模型自动迭代添加提示以优化分割结果。
- **资源高效微调 (Resource Efficient Finetuning)**: 针对显存或计算资源受限环境设计的微调策略，包括使用更小的模型(vit_t)、冻结部分网络、减少批次大小和LoRA技术。
- **UNETR解码器**: 用于自动实例分割的附加解码器，基于SAM的图像编码器构建，输出实例分割所需的距离图。
- **Slurm作业提交**: 模块中大量使用Slurm脚本（.sbatch文件）来在集群上并行提交训练和评估任务。

## Internal Relationships

- `finetuning/livecell_finetuning.py` → `micro_sam.training`: 导入micro_sam.training模块以获取可训练的SAM模型和训练器。
- `finetuning/evaluation/evaluate_amg.py` → `micro_sam.evaluation.inference`: 调用run_amg函数执行自动掩码生成推理。
- `finetuning/evaluation/evaluate_instance_segmentation.py` → `micro_sam.evaluation.inference`: 调用run_instance_segmentation_with_decoder函数执行实例分割推理。
- `finetuning/evaluation/iterative_prompting.py` → `micro_sam.evaluation.inference`: 调用run_inference_with_iterative_prompting函数执行迭代提示推理。
- `finetuning/generalists/training/light_microscopy/train_lm_generalist.py` → `finetuning/generalists/training/light_microscopy/obtain_lm_datasets.py`: 导入obtain_lm_datasets.py以获取联合光显微镜数据集加载器。
- `finetuning/evaluation/util.py` → `micro_sam.evaluation.livecell`: 导入livecell模块中的路径获取函数。
- `finetuning/specialists/training/light_microscopy/deepbacs_finetuning.py` → `torch_em.data.datasets`: 使用torch_em获取DeepBacs数据集加载器。
- `finetuning/run_all_finetuning.py` → `finetuning/livecell_finetuning.py`: 作为顶层脚本，调用各个具体的微调脚本（如livecell_finetuning.py）。
