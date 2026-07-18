# artifacts

> 存储微流控芯片蓝图、校准数据和图像配置，用于显微镜图像与芯片结构的实时对齐。

artifacts 模块负责管理微流控芯片的几何蓝图、标记点位置、显微镜校准参数和图像路径。chamber_structure.json 定义通用腔室多边形；chips/sak.json 定义特定芯片（SAK）的腔室类型、多边形及标记点；images/calibration_sample/calibration_config.json 提供校准图像路径、物镜像素尺寸和模型路径。这些文件共同支持图像与蓝图的坐标转换和特征匹配。

## Files

### `artifacts/chamber_structure.json`

定义标准腔室类型的多边形坐标，作为芯片结构的通用几何模板。

### `artifacts/chips/sak.json`

定义 SAK 芯片的具体配置，包括各腔室类型的多边形和标记点坐标。

### `artifacts/images/calibration_sample/calibration_config.json`

存储校准图像元数据，包括图像路径、载物台位置和像素尺寸，用于图像与蓝图的坐标映射。

## Key Concepts

- **多边形蓝图**: 使用 GeoJSON Polygon 格式定义微流控腔室的二维几何形状，坐标单位为微米。
- **标记点**: 每个腔室定义的 cross 和 circle 标记点，用于图像特征匹配和坐标对齐。
- **校准映射**: 通过校准图像的载物台位置和像素尺寸，将图像坐标转换为芯片蓝图坐标。

## Internal Relationships

- `artifacts/chips/sak.json` → `artifacts/chamber_structure.json`: sak.json 复用 chamber_structure.json 中定义的腔室类型名称，但提供具体芯片的坐标和标记点。
- `artifacts/images/calibration_sample/calibration_config.json` → `artifacts/chips/sak.json`: calibration_config.json 通过 chip_name 字段引用特定芯片配置，确保校准数据与芯片蓝图匹配。
