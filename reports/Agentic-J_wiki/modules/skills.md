# 技能库

> 一个全面的库，包含经过验证的 Fiji/ImageJ 自动化模式、插件文档以及可重复显微镜图像分析的工作流阶段。

本仓库包含用于在 Fiji 中自动化显微镜图像分析的一系列技能（文档和代码）。它涵盖了广泛的插件，包括 3D ImageJ Suite、BigStitcher、Bio-Formats、BoneJ、CSBDeep、DeepImageJ、ilastik、LabelMe、MorphoLibJ、NeuronJ、OrientationJ、SNT、StarDist、TrackMate、TransformJ 等。每个技能都提供了经过验证的 Groovy/Python 脚本、API 参考、用户界面指南和故障排除说明。该仓库还包含一个具有 7 个阶段的管理员管道，用于管理从数据收集到质量保证的项目。

## 文件

### `skills/3d_imagej_suite_documentation/OVERVIEW.md`

提供 3D ImageJ Suite 插件的概述，包括其安装、涵盖的工作流和自动化指南。

### `skills/3d_imagej_suite_documentation/SCRIPT_API.md`

记录 3D ImageJ Suite 的经过验证的 Groovy API 调用，包括 FastFilters3D、ImageHandler 和 SimpleMeasure。

### `skills/3d_imagej_suite_documentation/GROOVY_WORKFLOW_3D_SEGMENT_AND_MEASURE.groovy`

一个可运行的 Fiji 工作流，用于平滑、阈值分割、3D 标记和 CSV 导出。

### `skills/bigstitcher_documentation/OVERVIEW.md`

描述 BigStitcher 的功能、支持的格式和处理管道。

### `skills/bigstitcher_documentation/WORKFLOW_TILE_STITCHING.groovy`

一个使用 BigStitcher 宏可记录命令进行批量瓦片拼接的 Groovy 脚本。

### `skills/bioimageformat_documentation/OVERVIEW.md`

解释 Bio-Formats 在读取/写入 150 多种显微镜格式并转换为 OME-TIFF 方面的作用。

### `skills/bioimageformat_documentation/WORKFLOW_BATCH_CONVERT.groovy`

一个使用 Bio-Formats 导入器和导出器的批量转换脚本。

### `skills/bonej_documentation/SKILL.md`

总结 BoneJ 在厚度、分数和连通性测量方面的经过验证的自动化路径。

### `skills/bonej_documentation/GROOVY_WORKFLOW_THICKNESS_AND_FRACTION.groovy`

一个用于 BoneJ 厚度和面积/体积分数测量的工作流。

### `skills/csbdeep_documentation/SKILL.md`

记录 CSBDeep 的 SciJava 命令表面，用于运行 CARE 模型。

### `skills/csbdeep_documentation/GROOVY_WORKFLOW_RUN_YOUR_NETWORK.groovy`

一个从本地 ZIP 文件或 URL 运行通用 CSBDeep 网络的脚本。

### `skills/deepimagej_documentation/SKILL.md`

解释通过 'DeepImageJ Run' 菜单命令实现 DeepImageJ 的自动化。

### `skills/deepimagej_documentation/GROOVY_WORKFLOW_BRIGHTFIELD_NUCLEI_SEGMENTATION.groovy`

一个运行 brightfield_nuclei 模型的工作流。

### `skills/ilastik_documentation/SKILL.md`

记录 ilastik4ij 的 HDF5 传输和预测工作流。

### `skills/ilastik_documentation/GROOVY_WORKFLOW_PIXEL_CLASSIFICATION.groovy`

一个运行已训练像素分类项目的脚本。

### `skills/morpholibj_documentation/SKILL.md`

总结通过距离变换分水岭算法实现 MorphoLibJ 细胞分割管道的方法。

### `skills/morpholibj_documentation/GROOVY_WORKFLOW_CELL_SEGMENTATION.groovy`

一个使用 MorphoLibJ 的完整细胞分割工作流。

### `skills/snt_documentation/SKILL.md`

记录 SNT 的 API，用于 SWC 分析、形态测量、Sholl 分析和数据库下载。

### `skills/snt_documentation/GROOVY_WORKFLOW_SWC_ANALYSIS.groovy`

一个分析 SWC 重建并导出形态测量和 Sholl 指标的脚本。

### `skills/trackmate_documentation/SKILL.md`

记录 TrackMate 的 Java API，用于粒子追踪和 Cellpose 集成。

### `skills/trackmate_documentation/GROOVY_WORKFLOW_PARTICLE_TRACKING.groovy`

一个完全自动化的单粒子追踪管道。

### `skills/trackmate_documentation/GROOVY_WORKFLOW_CELLPOSE_SINGLE_IMAGE.groovy`

一个使用 TrackMate-Cellpose 进行单图像分割的脚本。

### `skills/stardists_documentation/SKILL.md`

记录 StarDist 的 Groovy API，用于细胞和细胞核检测。

### `skills/stardists_documentation/GROOVY_WORKFLOW_CELL_SEGMENTATION.groovy`

一个使用 StarDist 进行细胞分割、计数和比较的脚本。

### `skills/transformj_documentation/SKILL.md`

记录通过 ImageScience 类实现 TransformJ 的几何变换。

### `skills/transformj_documentation/GROOVY_WORKFLOW_GEOMETRIC_TRANSFORM.groovy`

一个用于几何变换（缩放、平移、旋转等）的参数化工作流。

### `skills/turboreg_documentation/SKILL.md`

记录 TurboReg 用于配准的手动参数字符串构建方法。

### `skills/turboreg_documentation/WORKFLOW_BATCH_REGISTRATION.groovy`

一个将堆栈配准到参考图像的批量配准脚本。

### `skills/stackreg_documentation/SKILL.md`

记录 StackReg 的宏可记录 API，用于切片到切片的配准。

### `skills/stackreg_documentation/WORKFLOW_BATCH_REGISTRATION.groovy`

一个使用 StackReg 的批量配准脚本。

### `skills/imagej_groovy_patterns/SKILL.md`

一个关于常见 Groovy/ImageJ 编码陷阱及其修复方法的索引。

### `skills/imagej_groovy_patterns/pitfall_thresholding_direction.md`

解释在 IJ.setAutoThreshold 中使用 'dark' 后缀的重要性。

### `skills/imagej_groovy_patterns/pitfall_z_vs_t_dimensions.md`

解释如何为时间序列数据正确设置 Z 和 T 维度。

### `skills/workflow/supervisor_pipeline_phases/SKILL.md`

定义用于管理 ImageJ 分析项目的 7 阶段管理员管道。

### `skills/workflow/supervisor_pipeline_phases/phase_1_gathering.md`

信息收集阶段的说明。

### `skills/workflow/supervisor_pipeline_phases/phase_2_planning.md`

任务规划和管道设计的说明。

### `skills/workflow/supervisor_pipeline_phases/phase_4b_processing.md`

图像处理步骤和验证的指南。

### `skills/workflow/workflow-documentation/SKILL.md`

生成工作流文档的模板和说明。

## 核心概念

- **经过验证的自动化路径**：每个技能都记录了一种特定的、经过测试的 Fiji 插件自动化方法，通常使用直接的 Java API 调用（例如 CommandService）或宏可记录的字符串，而不是猜测 IJ.run() 命令。
- **Groovy 脚本**：Groovy 是本仓库中用于 Fiji 自动化的主要脚本语言，允许直接访问 Java 类和服务。
- **无头执行**：许多工作流设计为在无头模式下运行（例如，通过 fiji-linux-x64 --headless --run），从而实现服务器上的批量处理。
- **项目账本**：一个中央状态管理系统，由管理员管道使用，用于跨阶段跟踪项目元数据、决策和已完成步骤。
- **插件管理器**：一个在技能注册表中搜索并推荐最适合给定科学任务的插件的工具，确保使用经过验证的自动化路径。
- **陷阱规避**：该仓库包含常见错误（陷阱）及其标准修复方法的集合，例如处理 RGB 与多通道图像或正确设置 Z/T 维度。
- **可重复性**：强调记录参数、版本控制和容器化执行，确保分析可以完全精确地复现。

## 内部关系

- `skills/3d_imagej_suite_documentation/GROOVY_WORKFLOW_3D_SEGMENT_AND_MEASURE.groovy` → `skills/3d_imagej_suite_documentation/SCRIPT_API.md`：工作流脚本使用了 API 参考文件中记录的经过验证的 API 调用。
- `skills/bigstitcher_documentation/WORKFLOW_TILE_STITCHING.groovy` → `skills/bigstitcher_documentation/OVERVIEW.md`：工作流实现了概述中描述的拼接管道。
- `skills/bonej_documentation/GROOVY_WORKFLOW_THICKNESS_AND_FRACTION.groovy` → `skills/bonej_documentation/SCRIPT_API.md`：工作流使用了 API 参考中记录的 CommandService 调用。
- `skills/snt_documentation/GROOVY_WORKFLOW_SWC_ANALYSIS.groovy` → `skills/snt_documentation/SCRIPT_API.md`：工作流使用了 API 中记录的 Tree、TreeStatistics 和 ShollAnalyzer 类。
- `skills/trackmate_documentation/GROOVY_WORKFLOW_PARTICLE_TRACKING.groovy` → `skills/trackmate_documentation/SCRIPT_API.md`：工作流使用了 API 参考中记录的 TrackMate Java API 类。
- `skills/trackmate_documentation/GROOVY_WORKFLOW_CELLPOSE_SINGLE_IMAGE.groovy` → `skills/trackmate_documentation/CELLPOSE_DETECTOR_API.md`：工作流使用了 API 文件中记录的 Cellpose 检测器设置和模式。
- `skills/stardists_documentation/GROOVY_WORKFLOW_CELL_SEGMENTATION.groovy` → `skills/stardists_documentation/SCRIPT_API.md`：工作流使用了 API 参考中记录的 StarDist2D 命令 API。
- `skills/transformj_documentation/GROOVY_WORKFLOW_GEOMETRIC_TRANSFORM.groovy` → `skills/transformj_documentation/GROOVY_API.md`：工作流使用了 API 中记录的 ImageScience 变换类。
- `skills/turboreg_documentation/WORKFLOW_BATCH_REGISTRATION.groovy` → `skills/turboreg_documentation/GROOVY_SCRIPT_API.md`：工作流根据 API 文档构建 TurboReg 参数字符串。
- `skills/imagej_groovy_patterns/pitfall_thresholding_direction.md` → `skills/imagej_groovy_patterns/SKILL.md`：陷阱文件列在索引中，并为常见错误提供了特定的修复方法。
- `skills/workflow/supervisor_pipeline_phases/phase_4b_processing.md` → `skills/workflow/supervisor_pipeline_phases/SKILL.md`：阶段文件详细说明了管道概述中定义的 imagej_coder 代理的步骤。