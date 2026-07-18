# data

> CLOC 数据集准备、转换、重建和审计的完整工具链

该模块负责将多个源数据集转换为 CLOC 统一格式，处理受版权限制的派生图像重建，并提供流式审计工具以确保标注路径的完整性。核心流程包括：下载原始数据集 -> 运行转换脚本生成统一图像 -> 根据配方重建增强图像（裁剪、高分辨率、拼接） -> 审计所有路径和结构。

## Files

### `data/tools/convert_all_sources.py`

总入口脚本，按 manifests/conversion_manifest.json 定义顺序执行所有源图像转换步骤

- `main` (function) - 解析参数，加载转换清单，执行干跑或实际转换，生成报告
- `render_command` (function) - 将清单中的命令模板渲染为实际可执行命令，处理{workspace}等占位符和--overwrite标志

### `data/tools/rebuild_restricted_derived_images.py`

总入口脚本，按 manifests/restricted_derived_rebuild_manifest.json 执行受限制派生图像的重建

- `main` (function) - 解析重建清单，验证依赖文件，执行重建步骤并生成报告
- `expand_command` (function) - 将重建步骤的命令模板展开为实际命令，处理{overwrite_flag}、{verify_flag}、{path_prefix_args}等占位符

### `data/tools/audit_annotation_image_paths.py`

流式检查 split JSON 中 image_path 的磁盘存在性，避免加载数 GB 的大文件

- `scan_split` (function) - 逐行解析 JSON，提取 image_path 和 image_from，统计存在/缺失数量并按来源分组
- `iter_top_level_record_blobs` (function) - 生成器，从大 JSON 文件中流式产出顶层记录块，避免内存溢出

### `data/tools/auditors/audit_original_image_paths.py`

专门审计状态为 original 的图像路径存在性

- `scan_split` (function) - 过滤 status 为 original 的记录，检查路径存在性并生成报告

### `data/tools/auditors/audit_stitched_release_closure.py`

审计拼接增强图像的发布闭包，检查哪些记录被重建配方覆盖且输出存在

- `iter_stitched_records` (function) - 从 split JSON 中流式提取 status 为 stitched 的记录
- `iter_stitched_record_summaries` (function) - 快速扫描 stitched 记录的元数据（image_path, image_from, modality），避免解析大数组

### `data/tools/auditors/check_source_dataset_layout.py`

验证用户下载的源数据集目录结构是否符合重建配方的预期

- `check_dataset_layout` (function) - 根据预定义的结构检查规则（如 Cityscapes 需要 leftImg8bit 目录）验证数据集根目录

### `data/tools/auditors/verify_annotation_paths_by_filter.py`

按前缀和来源过滤后，流式验证特定图像路径的存在性

- `scan_split` (function) - 支持--prefix和--source参数，仅检查匹配条件的记录

### `data/tools/auditors/verify_objects365_patch_sample.py`

针对 Objects365 的 patch 结构进行抽样验证，无需下载完整数据集

- `iter_objects365_paths` (function) - 从 split JSON 中提取 Objects365 的图像路径
- `patch_key` (function) - 从路径提取 patch 键（如 train/patch0）用于分组抽样

### `data/tools/converters/convert_brifiseg_3channels_to_unified_images.py`

将 BriFiSeg 的三通道 nii.gz 数据合并为 RGB PNG

- `render_three_channels` (function) - 加载三个通道的 nii.gz 数据，归一化到 0-255 并堆叠为 RGB 数组

### `data/tools/converters/convert_cellbindb_tif_to_images_png.py`

将 CellBinDB 的 TIFF 图像转换为 RGB PNG

- `discover_records` (function) - 扫描 source_root 下所有 *-img.tif 文件，生成转换记录

### `data/tools/converters/convert_conic_npy_to_images_png.py`

将 CoNIC 的 images.npy 数组导出为 PNG

- `load_patch_names` (function) - 解析 patch_info.csv 获取图像名称
- `save_png` (function) - 将 numpy 数组保存为 PNG 文件

### `data/tools/converters/convert_deepbacs_tif_to_pngimages.py`

根据标注引用，将 DeepBacs 的 TIFF 转换为 PNG

- `iter_deepbacs_annotation_paths` (function) - 流式扫描标注 JSON，提取 DeepBacs 图像路径
- `normalize_to_uint8_rgb` (function) - 将 TIFF 转换为 RGB，对 16 位图像进行 min-max 归一化

### `data/tools/converters/convert_livecell_tif_to_images_png.py`

根据标注引用，将 LIVECell 的 TIFF 转换为 PNG

- `iter_livecell_annotation_paths` (function) - 流式扫描标注 JSON，提取 LIVECell 图像路径
- `source_for_target` (function) - 根据目标 PNG 路径反推源 TIFF 路径

### `data/tools/converters/convert_monusac_tif_to_png_images.py`

将 MoNuSAC 的 TIFF 转换为 PNG

- `convert_one` (function) - 处理 RGBA TIFF，可选择是否反转通道顺序以匹配历史 CLOC 数据

### `data/tools/converters/convert_monuseg_tif_to_png.py`

将 MoNuSeg 的 TIFF 转换为 PNG

- `iter_tiffs` (function) - 扫描 MoNuSeg 训练和测试数据集中的所有 TIFF 文件

### `data/tools/converters/convert_nuinsseg_tissue_images_to_png.py`

将 NuInsSeg 的组织图像转换为 RGB PNG

- `discover_records` (function) - 扫描每个器官目录下的 tissue images 文件夹

### `data/tools/converters/convert_soybean_pod_bmp_to_png.py`

将 Soybean Pod 的 BMP 图像转换为 PNG

- `image_equal` (function) - 比较两张图像像素是否完全相同，用于验证

### `data/tools/rebuilders/rebuild_cropped_from_recipe.py`

根据配方重建裁剪增强图像

- `crop_from_source_image` (function) - 从源图像裁剪并填充到最小尺寸 384x384
- `output_path_for_entry` (function) - 根据配方条目推断输出图像在 augmented/ 目录下的路径

### `data/tools/rebuilders/rebuild_high_resolution_from_recipe.py`

根据配方重建高分辨率派生图像

- `rebuild_entry` (function) - 根据策略（grid/cropped/zoomed）处理源图像

### `data/tools/rebuilders/rebuild_stitched_from_recipe.py`

根据配方重建拼接/马赛克图像

- `rebuild_one` (function) - 创建画布，按配方拼接多个 patch 图像

### `data/tools/recipes/rebuild_objects365_high_resolution.py`

Objects365 高分辨率图像重建脚本，支持生成配方和实际重建两种模式

- `grid_cells` (function) - 计算图像网格切割方案
- `collect_targets` (function) - 从标注 JSON 中收集高分辨率记录

### `data/manifests/conversion_manifest.json`

定义所有源数据集转换步骤的清单

### `data/manifests/restricted_derived_rebuild_manifest.json`

定义受限制派生图像重建步骤的清单

### `data/tools/downloaders/download_objects365_patches_no_proxy.sh`

下载 Objects365 图像 patch 的 shell 脚本

## Key Concepts

- **流式 JSON 解析**: 
- **配方驱动重建**: 
- **路径前缀映射**: 
- **受限制图像发布**: 
- **验证与报告**: 

## Internal Relationships

- `data/tools/convert_all_sources.py` → `data/manifests/conversion_manifest.json`: 转换总脚本读取转换清单，按顺序调用各数据集的转换脚本
- `data/tools/rebuild_restricted_derived_images.py` → `data/manifests/restricted_derived_rebuild_manifest.json`: 重建总脚本读取重建清单，按顺序调用各增强类型的重建脚本
- `data/tools/auditors/audit_annotation_image_paths.py` → `data/annotations/*_split.json`: 审计脚本直接扫描标注 JSON 文件，检查其中 image_path 的磁盘存在性
- `data/tools/converters/convert_deepbacs_tif_to_pngimages.py` → `data/annotations/*_split.json`: DeepBacs 转换脚本读取标注以确定需要转换的 TIFF 文件，避免全量转换
- `data/tools/converters/convert_livecell_tif_to_images_png.py` → `data/annotations/*_split.json`: LIVECell 转换脚本读取标注以确定需要转换的 TIFF 文件
- `data/tools/rebuilders/rebuild_cropped_from_recipe.py` → `data/tools/recipes/*.json`: 裁剪重建脚本读取配方 JSON，获取裁剪参数和源路径
- `data/tools/rebuilders/rebuild_high_resolution_from_recipe.py` → `data/tools/recipes/*.json`: 高分辨率重建脚本读取配方 JSON，获取源路径和处理策略
- `data/tools/rebuilders/rebuild_stitched_from_recipe.py` → `data/tools/recipes/*.json`: 拼接重建脚本读取配方 JSON，获取 patch 信息和拼接参数
