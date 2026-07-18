# 架构

**类型：** 插件系统

ImPartial 实现了基于插件的架构，与 MONAI Label 和 ImageJ/Fiji 集成。核心 Python 库提供深度学习模型和训练逻辑，而 ImageJ 插件则作为桌面客户端，用于交互式标注和推理。MONAI Label API 实现了服务器端模型服务和主动学习工作流。

## 组件图

```mermaid
graph TD
  core_library --> monai_label_api
  core_library --> imagej_plugin
  imagej_plugin --> monai_label_api
  configuration --> core_library
  configuration --> monai_label_api
```

## 组件

### core_library

包含模型、训练、推理和工具函数的核心 Python 库

文件：`impartial/dataprocessing/`、`impartial/general/`、`setup.py`、`requirements.txt`

### monai_label_api

用于模型服务和主动学习的 MONAI Label 服务器集成

文件：`monailabel-app/api/main.py`、`monailabel-app/api/lib/`、`monailabel-app/Impartial_classes.py`、`monailabel-app/Impartial_dataloaders.py`、`monailabel-app/Impartial_functions.py`

### imagej_plugin

通过 ImageJ/Fiji 进行交互式标注、训练和推理的桌面客户端

文件：`imagej-plugin/src/main/java/org/nadeemlab/impartial/`、`imagej-plugin/pom.xml`

### configuration

针对不同数据集和模型的配置文件

文件：`config/`、`impartial/general/config.py`

## 序列图

```mermaid
sequenceDiagram
  participant User
  participant ImageJ
  participant MONAI_API
  participant CoreLib
  User->>ImageJ: 上传图像
  ImageJ->>MONAI_API: 发送至服务器
  MONAI_API->>CoreLib: 执行推理
  CoreLib-->>MONAI_API: 返回预测结果
  MONAI_API-->>ImageJ: 显示结果
  User->>ImageJ: 添加涂鸦
  ImageJ->>MONAI_API: 提交标注
  MONAI_API->>CoreLib: 重新训练模型
  CoreLib-->>MONAI_API: 更新后的模型
```

## 数据流

用户通过 ImageJ 插件上传图像，插件将其发送至 MONAI Label API 服务器。服务器使用核心库执行推理并返回预测结果。用户添加涂鸦作为部分标注，这些标注被发送回服务器以进行主动学习和模型重新训练。