# Phase4-WebApp

> 提供基于Flask的Web界面，用于上传血涂片图像并执行疟原虫细胞分割与分期分类推理。

该模块是一个完整的Web应用，部署在HuggingFace Spaces上。它接收用户上传的Giemsa染色血涂片图像，通过后端Python管道（pipeline.py）执行三个核心步骤：1) 使用分水岭算法分割单个细胞；2) 使用EfficientNet-B0模型对分割出的细胞进行7类分类（背景、RBC、滋养体、环状体、裂殖体、配子体、白细胞）；3) 生成Grad-CAM++热力图以提供可解释性。前端通过HTML/CSS/JS构建临床仪表盘，实时展示统计指标、细胞网格、分割结果和感染率报告。

## Files

### `Dockerfile`

定义容器化部署环境，安装Python 3.10、OpenCV依赖及Python包，并配置端口7860以适配HuggingFace Spaces。

### `requirements.txt`

声明应用依赖，包括Flask、PyTorch (CPU版)、OpenCV-headless、Pillow、NumPy、SciPy、scikit-image和Matplotlib。

### `app.py`

Flask应用入口，处理HTTP请求、文件上传、模型初始化和推理调用。

- `MalariAI` (class) - 从pipeline.py导入的推理类，封装了分水岭分割、分类和Grad-CAM生成逻辑。
- `analyze` (function) - 处理POST请求的视图函数，接收上传的图像，保存临时文件，调用model.analyze()并返回JSON结果。
- `index` (function) - 首页路由，返回HTML模板。

### `pipeline.py`

核心推理逻辑，整合分水岭分割、EfficientNet-B0分类和Grad-CAM++可视化。

- `watershed_cells_with_labels` (function) - 执行分水岭分割算法，返回细胞边界框列表和标签掩码。
- `extract_masked_crop` (function) - 根据边界框提取细胞裁剪图，并将背景填充为白色以优化分类输入。
- `MalariAI` (class) - 主推理类，初始化加载模型权重，提供analyze()方法处理单张图像，输出包含分割图、细胞列表、分类结果和Grad-CAM图的JSON。

### `templates/index.html`

前端HTML结构，定义临床仪表盘布局，包括顶部栏、统计条、三列网格（输入/结果/报告）及加载遮罩。

### `static/css/style.css`

定义UI样式，采用医疗级配色和卡片布局，确保响应式设计和视觉清晰度。

### `static/js/app.js`

前端交互逻辑，处理文件拖拽上传、调用后端API、解析JSON响应并动态更新DOM元素（统计数字、图像、进度条）。

- `handleFileSelect` (function) - 读取选中的文件并预览图像。
- `renderResults` (function) - 解析后端返回的数据并更新页面统计和可视化组件。

## Key Concepts

- **分水岭分割 (Watershed Segmentation)**: 
- **EfficientNet-B0分类**: 
- **Grad-CAM++**: 
- **Flask API**: 

## Internal Relationships

- `app.py` → `pipeline.py`: app.py导入并实例化MalariAI类，调用其analyze方法执行推理。
- `app.py` → `templates/index.html`: app.py通过Flask的render_template函数渲染前端页面。
- `templates/index.html` → `static/css/style.css`: HTML页面引用CSS文件以应用样式。
- `templates/index.html` → `static/js/app.js`: HTML页面通过script标签加载JS文件以处理用户交互和API通信。
- `pipeline.py` → `requirements.txt`: pipeline.py使用的库（torch, opencv, scipy等）在requirements.txt中声明。
