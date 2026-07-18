# deployment

> 构建和配置 micro_sam 的跨平台安装程序及启动菜单

该模块负责使用 conda-build 和 mamba-pack 工具将 micro_sam 打包为可安装的应用程序。它定义了不同操作系统（Ubuntu、Windows）的构建配置，动态设置版本号，并处理 Windows 下的依赖项（freetype.dll）和开始菜单快捷方式创建。

## Files

### `deployment/construct_ubuntu-latest.yaml`

定义 Linux (Ubuntu) 环境下的 conda 构建配置

### `deployment/construct_windows-latest.yaml`

定义 Windows 环境下的 conda 构建配置，包含 post_install 脚本引用

### `deployment/env.yaml`

定义构建环境的核心依赖包列表

### `deployment/post_install.bat`

Windows 安装后脚本，用于解决 freetype.dll 依赖问题

### `deployment/version_getter.py`

CI/CD 流程中动态更新构建配置文件中的版本号

- `main` (function) - 根据环境变量 RUNNER_OS 选择对应的构建配置文件，加载当前 micro_sam 版本并更新 YAML 文件

### `deployment/windows_menu.json`

定义 Windows 开始菜单中 micro_sam 的快捷方式配置

### `deployment/windows_menu_setup.py`

安装后执行，复制图标和菜单配置并调用 menuinst 创建 Windows 开始菜单项

- `main` (function) - 将 logo.ico 和 windows_menu.json 复制到 conda 环境的 Menu 目录，并安装菜单项

## Key Concepts

- **conda-build / mamba-pack**: 用于将 Python 包及其依赖项打包为跨平台安装程序的工具链，本模块通过 YAML 配置文件定义构建参数。
- **post_install 脚本**: 在安装程序执行完毕后自动运行的脚本，用于处理构建工具无法解决的运行时依赖（如 Windows 下的 DLL 文件缺失问题）。
- **menuinst**: 用于在 Conda 环境中创建操作系统原生菜单项（如 Windows 开始菜单）的库。
- **动态版本注入**: 通过 Python 脚本在 CI 运行时读取 __version__.py 并更新构建 YAML，确保构建产物包含正确的版本号。

## Internal Relationships

- `deployment/version_getter.py` → `deployment/construct_ubuntu-latest.yaml`: version_getter.py 读取并修改 Ubuntu 构建配置以注入版本号
- `deployment/version_getter.py` → `deployment/construct_windows-latest.yaml`: version_getter.py 读取并修改 Windows 构建配置以注入版本号
- `deployment/construct_windows-latest.yaml` → `deployment/post_install.bat`: Windows 构建配置指定在 install 后执行 post_install.bat 脚本
- `deployment/windows_menu_setup.py` → `deployment/windows_menu.json`: windows_menu_setup.py 复制并使用 windows_menu.json 配置来创建菜单
- `deployment/env.yaml` → `deployment/construct_ubuntu-latest.yaml`: 构建配置引用 env.yaml 作为环境定义（通过 __MICROSAM_BUILD_ENV__ 占位符）
- `deployment/env.yaml` → `deployment/construct_windows-latest.yaml`: 构建配置引用 env.yaml 作为环境定义（通过 __MICROSAM_BUILD_ENV__ 占位符）
