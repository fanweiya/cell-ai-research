# patch_stardist

> 修复TrackMate-StarDist 2.0.0在ImageJ中因XML反序列化导致的ClassCastException。

该模块通过Javassist在运行时动态修改TrackMate-StarDist JAR中的字节码，解决TARGET_CHANNEL配置项从XML加载时为String类型而非Integer类型引发的异常。主要流程包括：构建包含所有Fiji JAR的ClassPool，定位并修改StarDistDetectorConfigurationPanel.setSettings()和StarDistDetectorFactory.getDetector()方法，在方法入口处插入类型转换逻辑，最后通过java.util.zip原地更新JAR文件。

## Files

### `patch_stardist/PatchStarDist.java`

核心补丁执行器，负责动态修改TrackMate-StarDist JAR中的字节码以修复类型转换问题。

- `main` (function) - 执行补丁流程：构建ClassPool，加载Fiji JAR，定位目标类和方法，插入类型转换代码，最后重组并覆盖原JAR文件。
- `FIX_PANEL` (constant) - 注入到setSettings方法前的Javassist字节码字符串，用于将TARGET_CHANNEL从String转换为Integer。
- `FIX_FACTORY` (constant) - 注入到getDetector方法前的Javassist字节码字符串，功能与FIX_PANEL相同，作用于不同的方法上下文。

## Key Concepts

- **Javassist字节码操作**: 使用Javassist库在编译后动态修改Java类的方法体，无需重新编译源代码即可修复运行时错误。
- **JAVAPatch**: 通过ZipInputStream和ZipOutputStream手动重组JAR文件，仅替换被修改的class文件，避免依赖外部zip命令行工具。
- **XML反序列化类型不匹配**: TrackMate-StarDist从XML加载配置时，TARGET_CHANNEL被解析为String，但代码期望Integer，导致ClassCastException。
