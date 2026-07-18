# docs

> 提供DART微流控芯片分析系统的配置、部署和坐标系统文档。

docs模块包含四个核心Markdown文档，分别阐述芯片配置规范、Docker部署指南、运行时配置参考以及坐标系统转换原理。这些文档共同构成了系统的技术文档体系，指导用户如何定义芯片设计、部署API服务、配置批处理流程以及理解底层坐标变换逻辑。

## Files

### `docs/CHIP_CONFIG.md`

定义芯片配置JSON文件的完整规范，包括芯片名称、版本、腔室类型、标记位置及蓝图映射。

- `chamber_types` (field) - JSON对象，映射腔室类型名称到其几何形状（GeoJSON多边形）和标记位置（十字和圆圈标记的微米坐标）。
- `blueprint_map` (field) - JSON数组，列出所有ROI的ID、在蓝图坐标系中的X/Y位置以及对应的结构类型。
- `ChipStructureLibrary` (class) - 在dart_mlci/chip.py中实现，用于加载和查询芯片配置的核心类，支持通过ROI ID查找腔室信息和蓝图映射。

### `docs/DOCKER_GUIDE.md`

提供DART API的Docker容器化部署指南，包括构建、运行、环境变量配置及多芯片支持。

- `DART_MODEL_PATH` (env_var) - 环境变量，指定YOLO模型权重文件的路径，默认指向容器内的artifacts/models/v26_detect_s_imgsz1280.pt。
- `DART_CHIP_CONFIGS_DIR` (env_var) - 环境变量，指定存放芯片配置JSON文件的目录，支持多芯片加载。
- `docker-compose` (command) - 用于一键构建和启动DART API服务的Docker Compose命令。

### `docs/configuration.md`

详解运行时配置（folder_config.json）的字段含义、段选器选择及输出文件结构。

- `folder_config.json` (config_file) - 批处理脚本process_folder.py使用的JSON配置文件，定义输入输出目录、像素大小、段选器类型及文件夹映射。
- `segmenter` (field) - 配置字段，选择细胞分割算法，支持'cellpose-sam'（默认）或'omnipose'。
- `stack.tif` (output_file) - 每层堆栈的输出文件，包含分割掩码（uint16，每层H×W，标签值代表不同细胞实例）。

### `docs/coordinate_systems.md`

解释DART掩蔽校准流程中使用的三种坐标系统及其转换关系，重点说明Y轴反转的处理逻辑。

- `BLUEPRINT` (coordinate_system) - 蓝图坐标系统，单位为微米，采用笛卡尔坐标系（Y轴向上），原点通常在芯片设计左上角。
- `IMAGE_PIXEL` (coordinate_system) - 图像像素坐标系统，单位为像素，采用标准图像坐标系（Y轴向下），原点为图像左上角。
- `STAGE` (coordinate_system) - 显微镜载物台坐标系统，单位为微米，原点为硬件参考点，Y轴方向通常向下。
- `Y-axis Inversion` (concept) - 蓝图与图像坐标系统之间的关键转换：由于Y轴方向相反，计算偏移量时Y坐标需使用加法而非减法。

## Key Concepts

- **芯片配置即真理**: 每个芯片设计对应一个JSON配置文件，作为腔室几何形状、标记位置和蓝图映射的唯一数据源，通过ChipStructureLibrary类进行查询。
- **坐标系统转换**: 系统核心难点在于蓝图（笛卡尔，Y向上）与图像（标准图像，Y向下）之间的坐标转换，特别是Y轴反转在计算偏移量时的特殊处理。
- **容器化部署**: 通过Docker和Docker Compose实现DART API的标准化部署，支持CPU/GPU模式，环境变量控制模型路径、芯片配置目录和像素大小。
- **批处理流水线**: process_folder.py脚本使用folder_config.json配置，自动执行从图像读取、标记检测、旋转校正到掩蔽裁剪和细胞分割的全流程。

## Internal Relationships

- `CHIP_CONFIG.md` → `configuration.md`: CHIP_CONFIG.md定义的芯片配置JSON是configuration.md中folder_config.json可选参数chip_config的具体实现格式。
- `DOCKER_GUIDE.md` → `CHIP_CONFIG.md`: DOCKER_GUIDE.md中的DART_CHIP_CONFIGS_DIR环境变量指向的目录应包含符合CHIP_CONFIG.md规范的芯片配置文件。
- `coordinate_systems.md` → `CHIP_CONFIG.md`: coordinate_systems.md解释的蓝图坐标系统（微米、Y轴向上）是CHIP_CONFIG.md中polygon和marker位置数据的坐标基准。
- `DOCKER_GUIDE.md` → `configuration.md`: DOCKER_GUIDE.md描述的Docker部署环境运行process_folder.py脚本时，需要挂载或配置configuration.md定义的folder_config.json。
