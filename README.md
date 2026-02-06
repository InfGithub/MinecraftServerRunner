# Minecraft Server Runner

## 描述

这是一个用于启动 **Minecraft Java 版** 服务器的 **Python** 程序。

![License](https://img.shields.io/badge/License-MIT-blue.svg)

## 注意事项

1. 请下载与服务器版本对应的 `JDK` ，推荐[Azul](https://www.azul.com/downloads/)。
2. 请将 `JDK` 添加到 **系统环境变量** 。如是使用 `Azul` ，安装时勾选全部服务即可一键设置环境变量。
3. 使用时，请将程序与 `Minecraft` 服务器核心放置在一起。

## 启动程序

```bash
python start_inline.py
```

## 配置文件

程序使用 `config.json` 作为配置文件。如果文件不存在，程序会自动创建默认配置。

首次运行时将自动生成配置文件。

```json
{
    "min_memory": 4, // 初始堆内存大小 (GB)
    "max_memory": 4, // 最大堆内存大小 (GB)
    "jar_name": "server.jar", // 服务器核心jar文件名
    "version": "1.20.1", // Minecraft游戏版本
    "loader": "Fabric", // 模组加载器: Vanilla, Fabric, Quilt, Forge, NeoForge
    "jdk_path": "java", // JDK安装路径
    "reboot_seconds": 10, // 重启等待时间（秒）
    "jvm_args": {
        // 高级JVM参数配置
        "server": true,
        "XX_UseG1GC": true,
        "XX_DisableExplicitGC": true,
        "XX_AlwaysPreTouch": true,
        "XX_ParallelRefProcEnabled": true,
        "XX_UseStringDeduplication": true,
        "XX_UnlockExperimentalVMOptions": true,
        "XX_TieredCompilation": true,
        "XX_UseCompressedOops": true,
        "XX_UseCompressedClassPointers": true
    }
}
```

## 环境配置

-   无需额外安装依赖包
-   使用标准库模块
-   Python 版本>=3.12

## 程序特点

-   单次/多次启动
-   智能识别重启策略
-   程序内配置
-   可自动 JVM 调优
-   环境兼容性检测

## 高级功能

-   **JVM 参数调优**:
    -   垃圾回收器选择 (G1GC, ZGC, ShenandoahGC)
    -   内存优化参数
    -   性能调优选项
-   **跨平台支持**: Windows & Linux
-   **强制模式**: 绕过版本检测强制运行

## 其他事项

-   **start.py** 已被废弃，请使用新版内联后的 **start_inline.py**！
-   由于是手动 **内联** ，此版本无法 **维护** ，模块版请查看 **/src/** 目录！

## 参与贡献

欢迎提交 **Issue** 和 **Pull Request**！
