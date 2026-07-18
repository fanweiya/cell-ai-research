# dataset_txt

> 定义白细胞图像细粒度形态标注的类别属性映射与数据加载配置

该模块负责将白细胞的形态学特征（如细胞大小、核形、胞浆颜色等）映射为模型可处理的数值标签，并提供CSV格式的数据索引文件以支持数据集的划分与加载。attribute.yml 定义了所有形态学属性的类别及其对应的整数编码，确保标注数据与模型输入的一致性。pbc_attr_v1_ccrop_val.csv 是验证集的数据清单，包含图像名称、细胞类型、12个形态学属性字段、文件路径及分割标识（split），用于训练流程中读取样本元数据。

## Files

### `dataset_txt/attribute.yml`

定义白细胞形态学属性的类别标签及其数值编码

- `cell_size` (mapping) - 细胞大小属性映射：big=0, small=1
- `cell_shape` (mapping) - 细胞形状属性映射：irregular=0, round=1
- `nucleus_shape` (mapping) - 细胞核形状属性映射：irregular=0, segmented-bilobed=1, segmented-multilobed=2, unsegmented-band=3, unsegmented-indented=4, unsegmented-round=5
- `nuclear_cytoplasmic_ratio` (mapping) - 核质比属性映射：high=0, low=1
- `chromatin_density` (mapping) - 染色质密度属性映射：densely=0, loosely=1
- `cytoplasm_vacuole` (mapping) - 胞浆空泡属性映射：no=0, yes=1
- `cytoplasm_texture` (mapping) - 胞浆质地属性映射：clear=0, frosted=1
- `cytoplasm_colour` (mapping) - 胞浆颜色属性映射：blue=0, light blue=1, purple blue=2
- `granule_type` (mapping) - 颗粒类型属性映射：coarse=0, nil=1, round=2, small=3
- `granule_colour` (mapping) - 颗粒颜色属性映射：nil=0, pink=1, purple=2, red=3
- `granularity` (mapping) - 颗粒性属性映射：no=0, yes=1

### `dataset_txt/pbc_attr_v1_ccrop_val.csv`

存储验证集图像及其形态学标注的CSV索引文件

- `img_name` (column) - 图像文件名
- `label` (column) - 细胞类型标签（如Neutrophil, Lymphocyte等）
- `cell_size` (column) - 细胞大小属性（文本值，需映射为数值）
- `cell_shape` (column) - 细胞形状属性（文本值）
- `nucleus_shape` (column) - 细胞核形状属性（文本值）
- `nuclear_cytoplasmic_ratio` (column) - 核质比属性（文本值）
- `chromatin_density` (column) - 染色质密度属性（文本值）
- `cytoplasm_vacuole` (column) - 胞浆空泡属性（文本值）
- `cytoplasm_texture` (column) - 胞浆质地属性（文本值）
- `cytoplasm_colour` (column) - 胞浆颜色属性（文本值）
- `granule_type` (column) - 颗粒类型属性（文本值）
- `granule_colour` (column) - 颗粒颜色属性（文本值）
- `granularity` (column) - 颗粒性属性（文本值）
- `path` (column) - 图像文件相对路径
- `split` (column) - 数据集划分标识（val表示验证集）

## Key Concepts

- **细粒度形态标注**: 对白细胞进行多属性联合标注，包括细胞大小、形状、核形态、核质比、染色质密度、胞浆特征及颗粒特性，用于像素级分割与分类任务
- **属性编码映射**: 将人类可读的形态学术语（如'round', 'light blue'）映射为模型可处理的整数索引，确保数据一致性
- **验证集索引**: 通过CSV文件管理验证集样本的元数据，包含图像路径、细胞类型及12个形态学属性，支持数据加载器按split过滤

## Internal Relationships

- `pbc_attr_v1_ccrop_val.csv` → `attribute.yml`: CSV中的形态学属性文本值需依据attribute.yml定义的映射关系转换为数值标签
