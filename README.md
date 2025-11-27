# MinecraftServerRunner

## 描述
这是一个用于启动 Minecraft 服务器的 Python 程序。
## 注意事项
1. 请下载与服务器版本对应的 `Java` ，推荐[Azul](https://www.azul.com/downloads/)。
2. 请将 `Java` 添加到 **系统环境变量** 。如是使用 `Azul` ，安装时勾选全部服务即可一键设置环境变量。
3. 使用时，请将程序与 `Minecraft` 服务器核心放置在一起。
4. `options.json` 文件是程序的配置文件。如缺失则程序无法运行。

## 配置options.json
默认配置如下： 

```json5
{
    "min_memory": 8,          // 初始堆内存大小 (GB)
    "max_memory": 16,         // 最大堆内存大小 (GB)
    "jar_name": "server.jar", // 服务器核心jar文件名
    "version": "1.20.1",      // Minecraft游戏版本
    "loader": "Fabric",       // 模组加载器: Vanilla, Fabric, Quilt, Forge, NeoForge
    "jdk_path": null,         // JDK安装路径，null表示使用系统默认Java
    "allow_force_run": true,  // 是否允许强制启动（绕过版本检测）
    "allow_force_reboot": false, // 是否允许强制重启（绕过异常检测）
    "reboot_time": 10,        // 重启等待时间（秒）
    "jvm_args": {}            // 高级JVM参数配置
}
```
