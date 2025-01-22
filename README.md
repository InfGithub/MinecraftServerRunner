# MinecraftServerRunner

## 描述
这是一个用于启动 Minecraft 服务器的 Python 程序。
## 选择你喜欢的版本
### start.py：CLI界面启动器
- 优点：直观，易懂
- 缺点：选择多，代码多
### start_cmd.py：命令行工具
- 优点：一行搞定，新增删除生成文件功能
- 缺点：不直观
- 使用`-h`或`--help`获取使用方法
## 注意事项
1. 请下载与服务器版本对应的 `Java` ，推荐[Azul](https://www.azul.com/downloads/)。
2. 请将 `Java` 添加到 **系统环境变量** 。如是使用 `Azul` ，安装时勾选全部服务即可一键设置环境变量。
3. 使用时，请将程序与 `Minecraft` 服务器核心放置在一起。
4. `options.json` 文件是程序的配置文件。如缺失则程序无法运行。

## 配置options.json
默认如下： 

```json5
{
    "Xms": 1, //最小内存（Gib）
    "Xmx": 1, //最大内存（Gib）
    "jarcore_name": "fabric-server-1.20.1-0.16.10.jar", //服务器核心名称（jar）
    "jarcore_loader": "Fabric", //服务器加载器（可选：Vanilla,Fabric,Quilt,Forge,Neoforge）
    "Version": "1.20.1", //服务器游戏版本
    "Forcedrun": true //强制运行服务器，绕过版本检查
}
```
