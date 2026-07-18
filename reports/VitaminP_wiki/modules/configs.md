# configs

> 管理基于Vision Transformer的病理细胞分割框架的训练、推理和作业配置。

该模块包含所有用于配置模型训练、推理和Kubernetes作业的文件。主要分为三类：1) inference/ 目录下的YAML文件，用于定义在Kubernetes集群中运行推理任务的Job规范，包含具体的命令行参数和硬件资源需求；2) jobs/ 目录下的YAML文件，用于定义训练和GAN任务的Job规范；3) training/ 目录下的YAML文件，用于定义数据加载、样本划分、数据增强和预处理的具体参数。训练配置文件展示了数据集从单一CRC/Xenium逐步扩展到包含TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg、BC、ConSep、Kumar、CPM-17等数十个数据集的混合训练策略。

## Files

### `configs/inference/inference.yaml`

定义H&E图像推理的Kubernetes Job，使用flex大模型对WSI进行细胞分割。

### `configs/inference/inference_mif.yaml`

定义MIF（多免疫荧光）图像推理的Kubernetes Job，处理ome.tiff格式文件。

### `configs/inference/inference_xenium.yaml`

定义Xenium空间转录组数据推理的Kubernetes Job，包含动态生成Python脚本的逻辑。

### `configs/inference/inference_xenium_he.yaml`

定义Xenium H&E图像配准后推理的Kubernetes Job。

### `configs/inference/inference_xenium_qptiff.yaml`

定义QPTIFF格式全切片图像推理的Kubernetes Job，支持多通道提取和合并。

### `configs/jobs/job.yaml`

定义标准模型训练任务的Kubernetes Job，支持dual、syn、flex等模型类型和UNI预训练。

### `configs/jobs/job_gan.yaml`

定义Pix2Pix GAN训练任务的Kubernetes Job，用于H&E到MIF的图像合成。

### `configs/training/config_fold1.yaml`

定义CRC和Xenium数据集的3折交叉验证第1折配置，包含数据路径、样本划分和增强参数。

### `configs/training/config_fold2.yaml`

定义CRC和Xenium数据集的3折交叉验证第2折配置。

### `configs/training/config_fold3.yaml`

定义CRC和Xenium数据集的3折交叉验证第3折配置。

### `configs/training/config_fold4.yaml`

定义仅CRC数据集的第1折配置，包含HV图生成和过滤参数。

### `configs/training/config_fold5.yaml`

定义仅Xenium数据集的第1折配置。

### `configs/training/config_fold6.yaml`

定义GAN训练的数据配置，采用90/10训练/验证划分。

### `configs/training/config_fold11.yaml`

定义合成CRC和Xenium数据集的混合训练配置第1折。

### `configs/training/config_fold12.yaml`

定义合成CRC和Xenium数据集的混合训练配置第2折。

### `configs/training/config_fold13.yaml`

定义合成CRC和Xenium数据集的混合训练配置第3折。

### `configs/training/config_fold21.yaml`

定义包含CRC、Xenium和TissueNet的混合数据集配置第1折。

### `configs/training/config_fold22.yaml`

定义包含CRC、Xenium、TissueNet的混合数据集配置第1折（num_workers=16）。

### `configs/training/config_fold23.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke的混合数据集配置。

### `configs/training/config_fold24.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard的混合数据集配置。

### `configs/training/config_fold25.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg的混合数据集配置。

### `configs/training/config_fold26.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC的混合数据集配置。

### `configs/training/config_fold27.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg的混合数据集配置。

### `configs/training/config_fold28.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg的混合数据集配置。

### `configs/training/config_fold29.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg、BC的混合数据集配置。

### `configs/training/config_fold30.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg、BC、ConSep的混合数据集配置。

### `configs/training/config_fold31.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg、BC、ConSep、Kumar、CPM-17的混合数据集配置。

### `configs/training/config_fold32.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg、BC、ConSep、Kumar、CPM-17的混合数据集配置（完整列表）。

### `configs/training/config_fold33.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg、BC、ConSep、Kumar、CPM-17的混合数据集配置（训练集微调）。

### `configs/training/config_fold34.yaml`

定义包含CRC、Xenium、TissueNet、PanNuke、Lizard、MoNuSeg、TNBC、NuInsSeg、CryoNuSeg、BC、ConSep、Kumar、CPM-17、MoNuSAC的混合数据集配置。

### `configs/training/newmethod.yaml`

定义新方法实验的数据配置，使用DSB2018和CPM15数据集，采用激进的数据增强策略。

## Key Concepts

- **混合数据集训练**: 通过逐步增加不同来源的病理图像数据集（CRC、Xenium、TissueNet、PanNuke等）来增强模型的泛化能力，配置文件从简单的双数据集扩展到包含15+个数据集的复杂混合训练。
- **3折交叉验证**: 早期配置文件（fold1-3）采用标准的3折交叉验证策略，将数据划分为训练、验证和测试集，确保模型评估的可靠性。
- **合成数据增强**: 使用GAN生成的合成数据（config_fold11-13）来扩充训练集，解决特定数据集样本不足的问题。
- **Kubernetes作业编排**: 所有推理和训练任务都通过Kubernetes Job进行编排，配置文件包含详细的资源需求（GPU、CPU、内存）、节点选择器和存储卷挂载信息。
- **数据缓存策略**: 配置文件包含数据缓存设置（cache_dir、cache_filename），用于加速大规模病理图像数据的加载过程。
- **多通道图像处理**: 推理配置支持处理多种图像格式（SVS、OME.TIFF、QPTIFF）和多通道数据（H&E、MIF、Xenium），并包含通道映射和合并逻辑。

## Internal Relationships

- `configs/inference/inference.yaml` → `configs/training/config_fold1.yaml`: 推理配置与训练配置共享相同的数据路径和预处理参数，但推理配置专注于模型加载和预测参数。
- `configs/jobs/job.yaml` → `configs/training/config_fold1.yaml`: 训练Job通过命令行参数引用具体的训练配置文件（如config_fold1.yaml）。
- `configs/training/config_fold1.yaml` → `configs/training/config_fold11.yaml`: config_fold11是config_fold1的变体，将数据源从原始CRC/Xenium切换到合成数据。
- `configs/training/config_fold21.yaml` → `configs/training/config_fold22.yaml`: config_fold22在config_fold21基础上增加了num_workers和persistent_workers以优化多GPU训练。
- `configs/training/config_fold23.yaml` → `configs/training/config_fold24.yaml`: config_fold24在config_fold23基础上增加了Lizard数据集。
- `configs/training/config_fold24.yaml` → `configs/training/config_fold25.yaml`: config_fold25在config_fold24基础上增加了MoNuSeg数据集。
- `configs/training/config_fold25.yaml` → `configs/training/config_fold26.yaml`: config_fold26在config_fold25基础上增加了TNBC数据集。
- `configs/training/config_fold26.yaml` → `configs/training/config_fold27.yaml`: config_fold27在config_fold26基础上增加了NuInsSeg数据集。
- `configs/training/config_fold27.yaml` → `configs/training/config_fold28.yaml`: config_fold28在config_fold27基础上增加了CryoNuSeg数据集。
- `configs/training/config_fold28.yaml` → `configs/training/config_fold29.yaml`: config_fold29在config_fold28基础上增加了BC数据集。
- `configs/training/config_fold29.yaml` → `configs/training/config_fold30.yaml`: config_fold30在config_fold29基础上增加了ConSep数据集。
- `configs/training/config_fold30.yaml` → `configs/training/config_fold31.yaml`: config_fold31在config_fold30基础上增加了Kumar和CPM-17数据集。
