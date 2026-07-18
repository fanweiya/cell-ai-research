# data_prep

> 预处理BBBC021单细胞图像数据，训练VAE编码器，提取潜变量，并构建控制/扰动组的端点数据集。

该模块负责从原始显微镜图像到单细胞潜变量表示的完整流水线。包括数据下载与分割、单细胞裁剪、VAE模型训练、潜变量提取、以及根据实验条件将潜变量分组为控制源和扰动目标。核心流程为：原始图像 -> 单细胞裁剪 -> VAE编码 -> 潜变量矩阵 -> 按条件分组。

## Files

### `data_prep/__init__.py`

模块初始化文件，当前为空。

### `data_prep/build_bbbc021_endpoints.py`

将VAE提取的潜变量张量按正则表达式匹配条件，分割为控制（src）和扰动（tgt）的numpy数组。

- `_split` (function) - 加载.pt文件，根据控制/目标正则表达式筛选索引，返回对应的潜变量数组。
- `main` (function) - 解析命令行参数，处理训练集和验证集，保存src_train.npy, tgt_train.npy, src_val.npy, tgt_val.npy。

### `data_prep/cellvae_adapter.py`

提供统一的VAE编码/解码接口，支持动态加载任意Checkpoint格式的预训练模型。

- `_import_obj` (function) - 通过字符串导入模块和类，格式如 'train_vae_full:VAE'。
- `_load_ckpt_state_dict` (function) - 兼容多种Checkpoint格式（PyTorch Lightning, 自定义训练等）并提取state_dict。
- `_strip_prefix` (function) - 移除state_dict键名中的常见前缀（如model., vae., module.）。
- `CellVAEAdapterConfig` (class) - 数据类，配置VAE加载参数（ckpt路径、模型导入路径、设备、输出范围等）。
- `CellVAEAdapter` (class) - 封装VAE模型，提供encode和decode方法，处理设备迁移和输出范围归一化。

### `data_prep/crop_bbbc021_singlecell.py`

从原始多通道显微图像中，基于掩膜（mask）裁剪出单个细胞的ROI图像。

- `robust_rescale_to_u8` (function) - 基于百分位数的鲁棒直方图拉伸，将图像重缩放为0-255的uint8。
- `crop_square_with_padding` (function) - 以指定中心点裁剪正方形区域，超出边界时自动填充。
- `find_channel_files_any` (function) - 扫描原始数据目录，识别多通道TIF文件并建立通道索引。
- `guess_mask_path` (function) - 根据原始图像文件名在掩膜目录中模糊匹配对应的细胞分割掩膜文件。

### `data_prep/export_latents_from_vae.py`

使用训练好的VAE模型对图像列表进行批量编码，导出潜变量张量和对应路径。

- `_load_list_paths` (function) - 读取路径列表文件，解析绝对/相对路径，过滤非图像和缺失文件。
- `PathImageDataset` (class) - PyTorch Dataset，加载图像并预处理为RGB张量。
- `main` (function) - 加载VAE，遍历图像数据集，提取mu或采样z，保存为包含'Z'和'paths'的.pt文件。

### `data_prep/export_latents_mu.py`

从Checkpoint文件反推并重建VAE模型结构，用于潜变量提取（与train_vae_full.py结构对应）。

- `_infer_stride_padding` (function) - 根据卷积核大小推断步长和填充参数。
- `_build_vae_from_sd` (function) - 解析Checkpoint的state_dict，动态构建Enc和Dec网络层。
- `load_vae_from_ckpt` (function) - 加载Checkpoint，构建VAE模型，返回模型、zdim和img_size。

### `data_prep/finetune_decoder_lpips.py`

在固定编码器的情况下，仅微调VAE解码器以优化感知损失（LPIPS），提升重建图像的结构细节。

- `CropDataset` (class) - 图像数据集，支持0-1或-1到1的范围归一化。
- `save_pair` (function) - 保存原始图像与重建图像的对比网格图。
- `main` (function) - 加载VAE，冻结编码器，使用L1+LPIPS损失函数训练解码器。

### `data_prep/gen_cells.py`

从潜变量文件中随机采样，通过VAE解码生成细胞图像网格。

- `main` (function) - 加载潜变量和VAE配置，解码指定数量的潜变量，保存网格图和单张图像。

### `data_prep/make_split.py`

按实验组（site或well）对单细胞图像进行训练/验证/测试分割，防止数据泄露。

- `site_key` (function) - 从文件名提取分组键（site或well级别）。
- `main` (function) - 遍历周文件夹，按组打乱并划分训练集、验证集和测试集，保存为txt列表。

### `data_prep/run_week.sh`

Bash脚本，自动化下载BBBC021特定周次的原始图像和掩膜数据，并执行单细胞裁剪。

- `main` (function) - 下载ZIP和TAR文件，解压，调用crop_bbbc021_singlecell.py进行裁剪，清理临时文件。

### `data_prep/train_vae_full.py`

定义并训练用于BBBC021单细胞图像的卷积VAE模型。

- `Enc` (class) - 卷积编码器，将96x96 RGB图像映射为潜变量分布的mu和logvar。
- `Dec` (class) - 转置卷积解码器，将潜变量重构为96x96 RGB图像。
- `VAE` (class) - 组合编码器和解码器，实现前向传播和重参数化技巧。
- `vae_loss` (function) - 计算重建误差（MSE）和KL散度的加权和。
- `main` (function) - 解析命令行参数，启动训练循环，保存包含model、zdim、img_size的Checkpoint。

## Key Concepts

- **单细胞潜变量提取**: 通过训练好的VAE将单细胞图像压缩为低维潜变量向量（z），用于后续的微扰响应建模。
- **数据分组与防泄露**: 在分割数据集时，确保来自同一显微视野（site）或同一井（well）的细胞被划分到同一个集合中，避免训练集和验证集之间存在数据泄露。
- **条件分组**: 通过正则表达式匹配图像文件名中的控制/扰动标识，将潜变量分为源（控制）和目标（扰动）两组，用于构建Schrödinger Bridge的端点分布。
- **感知损失微调**: 使用LPIPS（Learned Perceptual Image Patch Similarity）替代传统的像素级损失来微调解码器，以获得更清晰、结构更准确的细胞图像重建。

## Internal Relationships

- `data_prep/export_latents_from_vae.py` → `data_prep/export_latents_mu.py`: export_latents_from_vae.py 导入 load_vae_from_ckpt 以从Checkpoint重建VAE模型。
- `data_prep/build_bbbc021_endpoints.py` → `data_prep/export_latents_from_vae.py`: build_bbbc021_endpoints.py 处理 export_latents_from_vae.py 生成的.pt潜变量文件。
- `data_prep/cellvae_adapter.py` → `data_prep/train_vae_full.py`: cellvae_adapter.py 通过动态导入加载 train_vae_full.py 中的VAE类定义。
- `data_prep/gen_cells.py` → `data_prep/cellvae_adapter.py`: gen_cells.py 使用 CellVAEAdapter 进行潜变量解码生成图像。
- `data_prep/run_week.sh` → `data_prep/crop_bbbc021_singlecell.py`: run_week.sh 脚本在数据准备阶段调用 crop_bbbc021_singlecell.py 执行裁剪。
- `data_prep/make_split.py` → `data_prep/crop_bbbc021_singlecell.py`: make_split.py 处理 crop_bbbc021_singlecell.py 输出的单细胞图像目录。
- `data_prep/export_latents_mu.py` → `data_prep/train_vae_full.py`: export_latents_mu.py 中的模型构建逻辑与 train_vae_full.py 中的Enc/Dec结构保持一致。
