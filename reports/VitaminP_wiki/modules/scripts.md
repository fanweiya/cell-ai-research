# scripts

> 提供病理图像数据集的预处理、模型训练和推理的命令行工具

该模块包含用于将公共病理数据集转换为Zarr格式、训练VitaminP模型、训练GAN生成合成MIF图像以及运行WSI推理的脚本。所有脚本都遵循严格的分割策略以防止数据泄漏，并支持多种数据集格式。

## Files

### `data_preprocessing/README.md`

文档说明数据预处理脚本的用法、输出布局和各数据集的具体处理方式

### `data_preprocessing/_common.py`

为所有数据预处理脚本提供共享的辅助函数和常量

- `base_parser` (function) - 创建包含输入/输出目录和随机种子的通用参数解析器
- `read_rgb` (function) - 使用OpenCV读取RGB图像并转换为正确颜色空间
- `read_mat_instance` (function) - 从MATLAB文件中读取实例分割掩码
- `tile_pair` (function) - 将图像和掩码分割成512x512的图块
- `write_image_mask_zarr` (function) - 将图像和掩码堆叠并保存为Zarr格式
- `write_he_sample` (function) - 为单个样本写入H&E图像的Zarr数据
- `write_mif_sample` (function) - 为单个样本写入MIF图像的Zarr数据

### `data_preprocessing/preprocess_bc.py`

将BC/DeepLIIF数据集转换为Zarr格式

- `semantic_panel_to_instances` (function) - 将语义标签面板转换为实例分割掩码
- `convert_files` (function) - 处理一批文件并写入Zarr数据

### `data_preprocessing/preprocess_consep.py`

将CoNSeP数据集转换为Zarr格式

- `convert_split` (function) - 处理一个分割集（训练/验证/测试）

### `data_preprocessing/preprocess_cpm15.py`

将CPM-15数据集转换为Zarr格式（无预定义分割）

### `data_preprocessing/preprocess_cpm17.py`

将CPM-17数据集转换为Zarr格式

- `convert_split` (function) - 处理一个分割集

### `data_preprocessing/preprocess_cryonuseg.py`

将CryoNuSeg数据集转换为Zarr格式

- `collect_pairs` (function) - 收集图像-掩码对
- `convert_split` (function) - 处理一个分割集

### `data_preprocessing/preprocess_dsb2018.py`

将DSB2018数据集的RLE掩码解码并转换为Zarr格式

- `rle_decode` (function) - 解码RLE编码的像素掩码
- `classify` (function) - 自动分类图像模态（H&E或荧光）

### `data_preprocessing/preprocess_kumar.py`

将Kumar数据集转换为Zarr格式

- `convert_source` (function) - 处理一个源目录（train/val/test）

### `data_preprocessing/preprocess_lizard.py`

将Lizard数据集转换为Zarr格式

- `collect_pairs` (function) - 收集图像-掩码对
- `convert_split` (function) - 处理一个分割集

### `data_preprocessing/preprocess_monusac.py`

将MoNuSAC数据集的XML标注转换为Zarr格式

- `xml_to_mask` (function) - 将XML标注转换为实例分割掩码
- `convert_split` (function) - 处理一个分割集

### `data_preprocessing/preprocess_monuseg.py`

将MoNuSeg数据集的XML标注转换为Zarr格式

- `xml_to_mask` (function) - 将XML标注转换为实例分割掩码
- `collect_pairs` (function) - 收集图像-XML对
- `convert_split` (function) - 处理一个分割集

### `data_preprocessing/preprocess_nuinsseg.py`

将NuInsSeg数据集转换为Zarr格式

- `collect_pairs` (function) - 收集图像-掩码对
- `convert_split` (function) - 处理一个分割集

### `data_preprocessing/preprocess_pannuke.py`

将PanNuke数据集转换为Zarr格式（创建2x2马赛克）

- `load_folds` (function) - 加载PanNuke的folds数据
- `make_mosaic` (function) - 将4个256x256图块合并为512x512马赛克
- `convert_tasks` (function) - 处理一批马赛克任务

### `data_preprocessing/preprocess_panoptils.py`

将PanopTILs数据集的CSV多边形标注转换为Zarr格式

- `polygon_mask` (function) - 将CSV中的多边形转换为实例分割掩码

### `data_preprocessing/preprocess_tissuenet.py`

将TissueNet数据集转换为Zarr格式（支持MIF模态）

- `normalize_uint16` (function) - 将图像通道归一化到uint16
- `offset_instances` (function) - 为马赛克中的实例ID添加偏移
- `write_direct` (function) - 直接写入512x512样本
- `write_mosaics` (function) - 写入4个256x256图块组成的马赛克

### `data_preprocessing/preprocess_tnbc.py`

将TNBC数据集转换为Zarr格式（患者级别分割）

- `convert_slide` (function) - 处理单个患者的幻灯片

### `data_preprocessing/preprocess_xenium_crc.py`

同步Xenium/ORION-CRC数据的H&E和MIF掩码

### `run_wsi_inference.py`

提供Whole Slide Image (WSI) 推理的命令行接口

- `parse_args` (function) - 解析命令行参数
- `main` (function) - 执行WSI推理的主流程

### `train.py`

训练VitaminP模型的主脚本

- `main` (function) - 解析参数、设置训练环境并启动训练

### `train_gan.py`

训练Pix2Pix GAN以生成合成MIF图像

- `main` (function) - 解析参数、设置GAN训练环境并启动训练

## Key Concepts

- **Zarr格式**: 所有预处理脚本都将数据转换为Zarr v2格式存储，使用Blosc压缩，支持高效的大数组读写
- **数据分割策略**: 所有分割（训练/验证/测试）都在图块化之前完成，确保同一来源的样本不会泄漏到不同集合中
- **512x512图块**: 大多数数据集被分割成512x512的图块，部分数据集（如PanNuke、TissueNet）会将4个256x256图块合并为512x512马赛克
- **实例分割**: 所有脚本都处理实例分割掩码，每个细胞/核有一个唯一的整数ID
- **多模态支持**: 脚本支持H&E和MIF两种模态，部分数据集（如DSB2018、TissueNet）可以自动或手动区分模态

## Internal Relationships

- `data_preprocessing/preprocess_*.py` → `data_preprocessing/_common.py`: 所有预处理脚本都导入_common中的辅助函数，如base_parser、read_rgb、tile_pair等
- `train.py` → `dataset.py`: 训练脚本导入Config和create_dataloaders来加载预处理后的数据
- `train.py` → `vitaminp/*.py`: 训练脚本导入各种VitaminP模型类和VitaminPTrainer
- `run_wsi_inference.py` → `vitaminp/inference/*.py`: 推理脚本导入WSIPredictor、ChannelConfig等推理相关组件
- `train_gan.py` → `vitaminp/gan.py`: GAN训练脚本导入Pix2PixTrainer
