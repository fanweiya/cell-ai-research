# scripts

> 存储和描述用于在ImageJ/Fiji中运行的Groovy脚本及其元数据。

该模块包含预定义的Groovy脚本文件及其对应的JSON描述文件。脚本文件包含实际的ImageJ宏代码，而JSON文件提供脚本的名称、描述、输入要求、语言类型和文件名等元数据，便于系统识别、加载和执行这些脚本。

## Files

### `src/scripts/saved_scripts/Hello_World_Dialog.groovy`

定义一个显示模态对话框并打印确认信息的Groovy脚本。

- `IJ.showMessage` (function) - 调用ImageJ API显示包含'Hello, world!'的模态对话框。
- `println` (function) - 向控制台输出确认消息'OK: Hello, world! dialog shown'。

### `src/scripts/saved_scripts/Hello_World_Dialog.json`

为Hello_World_Dialog.groovy脚本提供元数据描述，包括名称、功能说明、输入要求、脚本语言及文件名。

## Key Concepts

- **Groovy脚本**: 在ImageJ/Fiji环境中运行的脚本语言，用于自动化图像分析任务。
- **元数据描述**: 使用JSON格式存储脚本的元信息，便于AI代理解析和执行脚本。

## Internal Relationships

- `src/scripts/saved_scripts/Hello_World_Dialog.json` → `src/scripts/saved_scripts/Hello_World_Dialog.groovy`: JSON文件通过'script_file'字段引用Groovy脚本文件名，用于系统加载和执行对应的脚本。
