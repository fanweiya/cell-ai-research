# postprocessing

> 处理Vision Transformer模型输出的HV图，生成实例分割掩码并提供可视化分析工具

该模块负责将模型预测的HV（水平/垂直）图转换为最终的细胞实例分割结果。核心流程包括：根据放大倍数自适应调整形态学参数、通过分水岭算法分离粘连细胞、移除小噪声对象、提取实例信息（如类型、边界框、面积）。模块包含主处理类HVPostProcessor和辅助的可视化分析脚本。

## Files

### `postprocessing/__init__.py`

模块入口，导出公共API

- `HVPostProcessor` (class) - HV图后处理主类，封装分割算法和参数配置
- `process_hv_maps` (function) - 处理HV图的独立函数（在hv_postprocess中定义）
- `process_model_outputs` (function) - 处理模型原始输出的独立函数（在hv_postprocess中定义）

### `postprocessing/hv_postprocess.py`

实现HV图到实例分割的核心算法

- `HVPostProcessor` (class) - 后处理类，根据放大倍数(20x/40x)和是否处理真值(gt)初始化参数，执行分割流程
- `post_process_segmentation` (method) - 主入口函数，接收预测图（3通道或4通道），返回实例掩码和实例信息字典
- `_process_hv_maps` (method) - 核心算法，将HV图转换为实例分割掩码，使用形态学操作和分水岭算法
- `_extract_instance_info` (method) - 从实例掩码中提取每个实例的详细信息（类型、边界框、面积、中心点）
- `remove_small_objects` (function) - 移除二值图像中面积小于min_size的连通区域，过滤噪声
- `get_bounding_box` (function) - 计算二值图像中非零像素的边界框坐标

### `postprocessing/utils.py`

提供WSI切片可视化、批量推理和结果分析工具

- `wsi_inference` (module) - 外部导入的推理模块，用于对WSI补丁进行细胞和细胞核分割
- `tifffile` (module) - 用于读取和写入大型TIFF格式WSI文件
- `cv2.drawContours` (function) - 在图像上绘制细胞轮廓用于可视化

## Key Concepts

- **HV图 (Horizontal/Vertical Maps)**: 
- **自适应参数**: 
- **分水岭分割**: 
- **实例信息提取**: 

## Internal Relationships

- `postprocessing/__init__.py` → `postprocessing/hv_postprocess.py`: __init__.py 导入 hv_postprocess.py 中的类和方法作为模块公共接口
- `postprocessing/hv_postprocess.py` → `postprocessing/utils.py`: 无直接导入关系，但utils.py 依赖 hv_postprocess.py 生成的实例掩码进行可视化
- `postprocessing/utils.py` → `wsi_inference`: utils.py 调用 wsi_inference 模块执行WSI补丁的推理，获取细胞和细胞核分割结果
