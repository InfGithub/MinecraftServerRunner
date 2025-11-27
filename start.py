from json import loads, dumps
from os import environ, walk, system, get_terminal_size
from os.path import isabs, join, normpath
from time import sleep
from typing import Tuple, Dict, List, Union, TypedDict, Callable, Any
import sys, subprocess

loaders: List[str] = ["Vanilla", "Fabric", "Quilt", "Forge", "NeoForge"]

string = """\
 __  __   ___   ___                            ___
|  \/  | / __| / __| ___  _ _ __ __ ___  _ _  | _ \ _  _  _ _   _ _   ___  _ _
| |\/| || (__  \__ \/ -_)| '_|\ V // -_)| '_| |   /| || || ' \ | ' \ / -_)| '_|
|_|  |_| \___| |___/\___||_|   \_/ \___||_|   |_|_\ \_,_||_||_||_||_|\___||_|
\t\tMinecraft Server Runner v2.1\t\tAuthor: Inf\t\t"""

class JVMArgsType(TypedDict, total=False):
    Xmn: int
    server: bool
    XX_UseG1GC: bool
    XX_MaxGCPauseMillis: int
    XX_G1HeapRegionSize: int
    XX_MetaspaceSize: int
    XX_MaxMetaspaceSize: int
    XX_UseZGC: bool
    XX_UseShenandoahGC: bool
    XX_DisableExplicitGC: bool
    XX_UseStringDeduplication: bool
    XX_AlwaysPreTouch: bool
    XX_ParallelRefProcEnabled: bool
    XX_UnlockExperimentalVMOptions: bool
    XX_UseLargePages: bool
    XX_UseTransparentHugePages: bool
    XX_TieredCompilation: bool
    XX_OptimizeStringConcat: bool
    XX_UseCodeCacheFlushing: bool
    XX_PerfDisableSharedMem: bool
    XX_UseBiasedLocking: bool
    XX_UseCompressedOops: bool
    XX_UseCompressedClassPointers: bool

class SettingsType(TypedDict):
    min_memory: int
    max_memory: int
    jar_name: str
    version: str
    loader: str
    jdk_path: str | None
    allow_force_run: bool
    allow_force_reboot: bool
    reboot_time: int
    jvm_args: JVMArgsType

class JVMArgsInfoType(TypedDict):
    type: str
    desc: str
    default: Any
    range: Tuple[int, int] | None
    options: List[int] | None

default_settings: SettingsType = {
    "min_memory": 8,
    "max_memory": 16,
    "jar_name": "server.jar",
    "version": "1.20.1",
    "loader": "Fabric",
    "jdk_path": None,
    "allow_force_run": False,
    "allow_force_reboot": False,
    "reboot_time": 10,
    "jvm_args": {}
}

jvm_args_info: Dict[str, JVMArgsInfoType] = {
    "Xmn": {"type": "memory_gb", "desc": "新生代内存大小", "default": None},
    "server": {"type": "switch", "desc": "服务器模式JIT", "default": None},
    "XX_UseG1GC": {"type": "switch", "desc": "G1垃圾回收器", "default": None},
    "XX_MaxGCPauseMillis": {"type": "number", "desc": "最大GC暂停时间", "range": (50, 1000), "default": 130},
    "XX_G1HeapRegionSize": {"type": "power2", "desc": "G1堆区域大小", "options": [1,2,4,8,16,32], "default": 16},
    "XX_MetaspaceSize": {"type": "memory_mb", "desc": "元空间初始大小", "default": 256},
    "XX_MaxMetaspaceSize": {"type": "memory_mb", "desc": "元空间最大大小", "default": 512},
    "XX_UseZGC": {"type": "switch", "desc": "ZGC垃圾回收器", "default": None},
    "XX_UseShenandoahGC": {"type": "switch", "desc": "Shenandoah垃圾回收器", "default": None},
    "XX_DisableExplicitGC": {"type": "switch", "desc": "禁用System.gc", "default": None},
    "XX_UseStringDeduplication": {"type": "switch", "desc": "字符串去重", "default": None},
    "XX_AlwaysPreTouch": {"type": "switch", "desc": "预分配内存", "default": None},
    "XX_ParallelRefProcEnabled": {"type": "switch", "desc": "并行引用处理", "default": None},
    "XX_UnlockExperimentalVMOptions": {"type": "switch", "desc": "解锁实验性选项", "default": None},
    "XX_UseLargePages": {"type": "switch", "desc": "使用大页内存", "default": None},
    "XX_UseTransparentHugePages": {"type": "switch", "desc": "透明大页", "default": None},
    "XX_TieredCompilation": {"type": "switch", "desc": "分层编译", "default": None},
    "XX_OptimizeStringConcat": {"type": "switch", "desc": "优化字符串连接", "default": None},
    "XX_UseCodeCacheFlushing": {"type": "switch", "desc": "代码缓存清理", "default": None},
    "XX_PerfDisableSharedMem": {"type": "switch", "desc": "禁用性能共享内存", "default": None},
    "XX_UseBiasedLocking": {"type": "switch", "desc": "偏向锁", "default": None},
    "XX_UseCompressedOops": {"type": "switch", "desc": "压缩普通对象指针", "default": None},
    "XX_UseCompressedClassPointers": {"type": "switch", "desc": "压缩类指针", "default": None},
}

jvm_args_mapping: Dict[str, Callable] = {
    "Xmn": lambda v: f"-Xmn{v}G",
    "server": lambda v: "-server",
    "XX_UseG1GC": lambda v: "-XX:+UseG1GC",
    "XX_MaxGCPauseMillis": lambda v: f"-XX:MaxGCPauseMillis={v}",
    "XX_G1HeapRegionSize": lambda v: f"-XX:G1HeapRegionSize={v}M",
    "XX_MetaspaceSize": lambda v: f"-XX:MetaspaceSize={v}m",
    "XX_MaxMetaspaceSize": lambda v: f"-XX:MaxMetaspaceSize={v}m",
    "XX_UseZGC": lambda v: "-XX:+UseZGC",
    "XX_UseShenandoahGC": lambda v: "-XX:+UseShenandoahGC",
    "XX_DisableExplicitGC": lambda v: "-XX:+DisableExplicitGC",
    "XX_UseStringDeduplication": lambda v: "-XX:+UseStringDeduplication",
    "XX_AlwaysPreTouch": lambda v: "-XX:+AlwaysPreTouch",
    "XX_ParallelRefProcEnabled": lambda v: "-XX:+ParallelRefProcEnabled",
    "XX_UnlockExperimentalVMOptions": lambda v: "-XX:+UnlockExperimentalVMOptions",
    "XX_UseLargePages": lambda v: "-XX:+UseLargePages",
    "XX_UseTransparentHugePages": lambda v: "-XX:+UseTransparentHugePages",
    "XX_TieredCompilation": lambda v: "-XX:+TieredCompilation",
    "XX_OptimizeStringConcat": lambda v: "-XX:+OptimizeStringConcat",
    "XX_UseCodeCacheFlushing": lambda v: "-XX:+UseCodeCacheFlushing",
    "XX_PerfDisableSharedMem": lambda v: "-XX:+PerfDisableSharedMem",
    "XX_UseBiasedLocking": lambda v: "-XX:+UseBiasedLocking",
    "XX_UseCompressedOops": lambda v: "-XX:+UseCompressedOops",
    "XX_UseCompressedClassPointers": lambda v: "-XX:+UseCompressedClassPointers",
}

def get_jvm_args(data: SettingsType) -> str:
    args: List = list()
    for key, value in data["jvm_args"].items():
        if key in jvm_args_mapping:
            if jvm_args_info[key]["type"] == "switch":
                if value:
                    args.append(jvm_args_mapping[key](value))
            else:
                args.append(jvm_args_mapping[key](value))
    return " ".join(args)

def generate_recommended_jvm_args(data: SettingsType) -> JVMArgsType:
    avg_memory: int = (data["min_memory"] + data["max_memory"]) // 2
    
    recommended: Dict[str, bool] = {
        "server": True,
        "XX_UseG1GC": True,
        "XX_DisableExplicitGC": True,
        "XX_AlwaysPreTouch": True,
        "XX_ParallelRefProcEnabled": True,
        "XX_UseStringDeduplication": True,
        "XX_UnlockExperimentalVMOptions": True,
        "XX_TieredCompilation": True,
        "XX_UseCompressedOops": True,
        "XX_UseCompressedClassPointers": True
    }
    
    if avg_memory <= 8:
        recommended.update({
            "XX_MaxGCPauseMillis": 200,
            "XX_G1HeapRegionSize": 8,
            "XX_MetaspaceSize": 256,
            "XX_MaxMetaspaceSize": 512
        })
    elif avg_memory <= 16:
        recommended.update({
            "XX_MaxGCPauseMillis": 130,
            "XX_G1HeapRegionSize": 16,
            "XX_MetaspaceSize": 256,
            "XX_MaxMetaspaceSize": 512
        })
    else:
        recommended.update({
            "XX_MaxGCPauseMillis": 100,
            "XX_G1HeapRegionSize": 32,
            "XX_MetaspaceSize": 512,
            "XX_MaxMetaspaceSize": 1024,
            "XX_UseLargePages": True
        })
    recommended["Xmn"] = max(1, avg_memory // 4)
    
    return recommended

def lined() -> int:
    try:
        terminal_columns = get_terminal_size().columns
    except:
        terminal_columns = 64
    print("-" * terminal_columns)
    return 0

def title(string: str) -> int:
    try:
        if sys.platform == "win32":
            system(f"title {string}")
            return 0
        else:
            print(f"\033]0;{string}\007", end="", flush=True)
            return 0
    except:
        return 1

def eula_write() -> Tuple[int, Union[Exception, None]]:
    try:
        with open("eula.txt", mode="w", encoding="utf-8") as f:
            f.write("eula=true")
        return 0, None
    except Exception as e:
        return 1, e

def settings_read() -> Tuple[int, Union[Exception, str, SettingsType, None]]:
    try:
        with open("settings.json", mode="r", encoding="utf-8") as f:
            text = f.read()
        result = loads(text)
        return 0, result
    except Exception as e:
        return 1, e

def settings_write(data: SettingsType) -> Tuple[int, Union[Exception, None]]:
    try:
        with open("settings.json", mode="w", encoding="utf-8") as f:
            f.write(dumps(data, indent=4))
        return 0, None
    except Exception as e:
        return 1, e

def get_java_path(data: SettingsType) -> str:
    if data["jdk_path"] is None:
        return "java"
    else:
        java_exe = "bin/java.exe" if sys.platform == "win32" else "bin/java"
        return f"\"{normpath(join(data["jdk_path"], java_exe))}\""

def allow_run(data: SettingsType) -> Tuple[int, Union[Exception, str, None]]:
    if data["allow_force_run"]:
        return 0, None

    try:
        version = tuple([int(i) for i in data["version"].split(".")])
        out, _ = subprocess.Popen(
            args=[get_java_path(data), "--version"],
            shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE).communicate()
        outs = out.decode("ascii")
        jdk_version = tuple([int(i) for i in outs.split("\n")[0].split()[1].split(".")])
        assert len(jdk_version) == 3
    except Exception as e:
        return 1, e

    if  ((1, 9, 0) > jdk_version >= (1, 8, 0) and (1, 16, 5) >= version) or \
        ((1, 12, 0) > jdk_version >= (1, 11, 0) and (1, 17, 1) >= version >= (1, 13, 0)) or \
        ((1, 18, 0) > jdk_version >= (1, 17, 0) and (1, 20, 4) >= version >= (1, 17, 0)) or \
        ((1, 22, 0) > jdk_version >= (1, 21, 0) and version >= (1, 20, 5)):
        return 0, None
    else:
        return 1, "JdkVersionError"

def get_command(data: SettingsType) -> Tuple[int, Union[str, Exception]]:
    version = tuple([int(i) for i in data["version"].split(".")])
    if data["loader"] in ["Vanilla", "Fabric", "Quilt"] or (data["loader"] == "Forge" and (1, 16, 5) >= version):
        return 0, f"{get_java_path(data)} -jar -Xms{data["min_memory"]}G -Xmx{data["max_memory"]}G {get_jvm_args(data)} {data["jar_name"]} nogui"
    else:
        if data["loader"] == "Forge":
            try:
                return 0, f"{get_java_path(data)} -Xms{data["min_memory"]}G -Xmx{data["max_memory"]}G {get_jvm_args(data)} @libraries/net/minecraftforge/forge/{list(walk("./libraries/net/minecraftforge/forge/"))[0][1][0]}/ %* nogui"
            except IndexError as e:
                return 1, f"ForgeDirectoryError - {e}"
            except Exception as e:
                return 1, e
        else:
            return 1, "LoaderError"

def init_windows_encoding() -> Tuple[int, Union[Exception, None]]:
    try:
        if sys.platform == "win32":
            system("chcp 65001 > nul")
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8")
        return 0, None
    except Exception as e:
        return 1, e

def get_recommended_value(key: str, data: SettingsType) -> Any:
    avg_memory: int = (data["min_memory"] + data["max_memory"]) // 2
    recommendations: Dict[str, int] = {
        "Xmn": max(1, avg_memory // 4),
        "XX_MaxGCPauseMillis": 200 if avg_memory <= 8 else 130 if avg_memory <= 16 else 100,
        "XX_G1HeapRegionSize": 8 if avg_memory <= 8 else 16 if avg_memory <= 16 else 32,
        "XX_MetaspaceSize": 256,
        "XX_MaxMetaspaceSize": 512 if avg_memory <= 16 else 1024,
    }
    return recommendations.get(key, jvm_args_info.get(key, {}).get("default"))

def handle_jvm_arg_input(config: Dict) -> Any:
    print(f"配置 {config["key"]} | {config["description"]}")
    lined()
    print(f"原值：{config["current_value"]}")
    if config["recommended_value"] is not None:
        print(f"推荐值：{config["recommended_value"]}")
    lined()
    
    value = input("请输入值（开关型Y=启用/N=禁用，留空取消）：").strip()
    
    if value == "":
        return "CANCEL"
    
    arg_type = config["type"]
    
    if arg_type == "switch":
        if value.upper() == "Y":
            return True
        elif value.upper() == "N":
            return False
        else:
            return "INVALID"
    elif arg_type == "number":
        if value.isdigit():
            int_val = int(value)
            if "range" in config and config["range"][0] <= int_val <= config["range"][1]:
                return int_val
        return "INVALID"
    elif arg_type == "memory_gb":
        return int(value) if value.isdigit() else "INVALID"
    elif arg_type == "memory_mb":
        return int(value) if value.isdigit() else "INVALID"
    elif arg_type == "power2":
        if value.isdigit():
            int_val = int(value)
            if int_val in config.get("options", []):
                return int_val
        return "INVALID"
    
    return value

def show_jvm_args_config(data: SettingsType):
    while True:
        print("[0] 返回配置界面")
        print("[1] 清除所有JVM参数")
        print("[2] 一键生成推荐配置")
        lined()
        
        args_list = list(jvm_args_info.keys())
        for i, key in enumerate(args_list, 3):
            current = data["jvm_args"].get(key)
            desc = jvm_args_info[key]["desc"]
            
            if jvm_args_info[key]["type"] == "switch":
                if current is True:
                    display_value = "启用"
                elif current is False:
                    display_value = "未启用"
                else:
                    display_value = "未设置"
            else:
                display_value = current if current is not None else "未设置"
            
            print(f"[{i}] {key:35} | {desc:20} ··· {display_value}")
        
        lined()
        choice = input("选择：")
        
        if choice == "0":
            lined()
            break
        elif choice == "1":
            value = input("是否确认清除所有JVM参数(Y/N)：")
            if value.upper() == "Y":
                data["jvm_args"] = {}
                print("所有JVM参数清除成功！")
            lined()
        elif choice == "2":
            print("一键生成推荐JVM参数配置")
            lined()
            recommended = get_recommended_value(data)
            print("推荐的JVM参数配置：")
            for k, v in recommended.items():
                if jvm_args_info[k]["type"] == "switch":
                    print(f"  - {k}: {"启用" if v is True else "未启用"}")
                else:
                    print(f"  - {k}: {v}")
            lined()
            value = input("是否应用此配置？(Y/N): ")
            if value.upper() == "Y":
                data["jvm_args"] = recommended
                print("推荐配置已应用！")
            else:
                print("配置未应用。")
            lined()
        else:
            try:
                choice_num = int(choice)
                if 3 <= choice_num < len(args_list) + 3:
                    key = args_list[choice_num - 3]
                    config = {
                        "key": key,
                        "description": jvm_args_info[key]["desc"],
                        "type": jvm_args_info[key]["type"],
                        "current_value": data["jvm_args"].get(key),
                        "recommended_value": get_recommended_value(key, data)
                    }
                    if "range" in jvm_args_info[key]:
                        config["range"] = jvm_args_info[key]["range"]
                    if "options" in jvm_args_info[key]:
                        config["options"] = jvm_args_info[key]["options"]
                    
                    result = handle_jvm_arg_input(config)
                    
                    if result == "CANCEL":
                        print("操作取消")
                    elif result == "INVALID":
                        print("输入值无效，请检查数据类型和范围")
                    elif jvm_args_info[key]["type"] == "switch":
                        if result is True:
                            data["jvm_args"][key] = True
                            print(f"{key} 已启用")
                        elif result is False:
                            data["jvm_args"][key] = False
                            print(f"{key} 已禁用")
                    elif result is not None:
                        data["jvm_args"][key] = result
                        print(f"{key} 设置成功")
                    lined()
                else:
                    print("输入的内容无效。")
                    lined()
            except ValueError:
                print("输入的内容无效。")
                lined()

def main() -> int:
    init_windows_encoding()
    title("Minecraft Server Runner")
    lined()
    print(string)
    lined()
    
    while True:
        print("[0] 启动服务器")
        print("[1] 启动服务器（自动重启）")
        print("[2] 修改EULA协议")
        print("[3] 修改启动配置")
        print("[4] 检测运行环境")
        print("[5] 终止 Minecraft Server Runner")
        lined()

        value = input("选择：")
        lined()

        if value == "0":
            result = settings_read()
            if result[0] == 0:
                data = result[1]
            else:
                data = default_settings
                print(f"配置文件读取失败，已返回默认值。错误信息：'{result[1]}'")
                lined()
            
            allow = allow_run(data)
            command = get_command(data)
            if allow[0] == 0 and command[0] == 0:
                print("服务器环境正常。")
                print("服务器启动命令：")
                lined()
                print(command[1])
                lined()
                print("[0] 启动服务器")
                print("[1] 返回任务执行界面")
                lined()
                value = input("选择：")
                lined()
                if value == "0":
                    run_result = subprocess.run(args=command[1], shell=True)
                    lined()
                    print(f"服务器已终止，返回码：{run_result.returncode}")
                    lined()
                elif value == "1":
                    pass
                else:
                    print("输入的内容无效。")
                    lined()
            else:
                if allow[0] != 0:
                    print(f"服务器环境异常：{allow[1]}")
                    print("请考虑修改配置文件，或启用强制启动。")
                else:
                    print(f"服务器启动命令异常：{command[1]}")
                    print("请考虑修改配置文件，或检查文件目录。")
                lined()
                input("Press Any Key...")
                lined()
                
        elif value == "1":
            result = settings_read()
            if result[0] == 0:
                data = result[1]
            else:
                data = default_settings
                print(f"配置文件读取失败，已返回默认值。错误信息：'{result[1]}'")
                lined()
            
            allow = allow_run(data)
            command = get_command(data)
            if allow[0] == 0 and command[0] == 0:
                print("服务器环境正常。")
                print("服务器启动命令：")
                lined()
                print(command[1])
                lined()
                print("[0] 启动服务器")
                print("[1] 返回任务执行界面")
                lined()
                value = input("选择：")
                lined()
                if value == "0":
                    print("输入执行次数，负值代表无限循环，0值立刻退出。")
                    if data["allow_force_reboot"]:
                        print("警告：您已启用强制重启，跳过服务器异常终止检查！")
                    lined()
                    value = input("输入：")
                    lined()
                    try:
                        times = int(value)
                        if times > 1024 or times < 0:
                            times = 1024
                        for t in range(times):
                            title(f"Server Reboot Time: {t}")
                            run_result = subprocess.run(args=command[1], shell=True)
                            lined()
                            return_code = run_result.returncode
                            if return_code == 0 and not data["allow_force_reboot"]:
                                print(f"服务器正常终止，跳出重启循环。返回码：{return_code}")
                                lined()
                                break
                            else:
                                if t < times - 1:
                                    print(f"服务器{"正常" if return_code == 0 else "异常"}终止，准备重启。返回码：{return_code}")
                                    lined()
                                    for y in range(data["reboot_time"], 0, -1):
                                        print(f"将在 {y}s 后重启...")
                                        sleep(1.000)
                                    lined()
                                else:
                                    print(f"服务器{"正常" if return_code == 0 else "异常"}终止。返回码：{return_code}")
                                    lined()
                        title("Minecraft Server Runner")
                    except Exception as e:
                        print(f"输入的内容无效：{e}")
                        lined()
                elif value == "1":
                    pass
                else:
                    print("输入的内容无效。")
                    lined()
            else:
                if allow[0] != 0:
                    print(f"服务器环境异常：{allow[1]}")
                    print("请考虑修改配置文件，或启用强制启动。")
                else:
                    print(f"服务器启动命令异常：{command[1]}")
                    print("请考虑修改配置文件，或检查文件目录。")
                lined()
                input("Press Any Key...")
                lined()
                
        elif value == "2":
            print("请先阅读并同意此协议：https://aka.ms/MinecraftEULA")
            value = input("输入Y(Yes)即代表您同意此协议：")
            if value.upper() == "Y":
                result = eula_write()
                if result[0] == 0:
                    print("EULA协议修改成功！")
                else:
                    print(f"EULA协议修改失败，错误信息：'{result[1]}'")
            lined()
            
        elif value == "3":
            result = settings_read()
            if result[0] == 0:
                data = result[1]
            else:
                data = default_settings
                print(f"配置文件读取失败，已返回默认值。错误信息：'{result[1]}'")
                lined()

            while True:
                jvm_args_count = len(data["jvm_args"])
                jvm_enabled_count = sum(1 for v in data["jvm_args"].values() if v is True)
                
                print(f"[0] 设置初始堆内存大小 ··· {data["min_memory"]}G")
                print(f"[1] 设置最大堆内存大小 ··· {data["max_memory"]}G")
                print(f"[2] 设置核心文件名称   ··· {data["jar_name"]}")
                print(f"[3] 设置模组加载器     ··· {data["loader"]}")
                print(f"[4] 设置游戏版本       ··· {data["version"]}")
                print(f"[5] 配置JDK绝对路径    ··· {data["jdk_path"]}")
                print(f"[6] 配置强制启动       ··· {"启用" if data["allow_force_run"] else "未启用"}")
                print(f"[7] 配置强制重启       ··· {"启用" if data["allow_force_reboot"] else "未启用"}")
                print(f"[8] 配置重启等待时间   ··· {data["reboot_time"]} s")
                print(f"[9] 配置高级JVM参数    ··· 已设置 {jvm_args_count} 个参数 ({jvm_enabled_count} 个启用)")
                print(f"[ ] 返回任务执行界面")
                lined()

                value = input("选择：")
                lined()

                if value == "0":
                    print("配置初始堆内存大小（GB）")
                    print(f"原数值：{data["min_memory"]}")
                    lined()
                    value = input("请输入将修改的数值：")
                    if value.isdigit():
                        data["min_memory"] = int(value)
                        print("初始堆内存大小修改成功！")
                    else:
                        print("初始堆内存大小修改失败，请检查数据类型。")
                    lined()
                elif value == "1":
                    print("配置最大堆内存大小（GB）")
                    print(f"原数值：{data["max_memory"]}")
                    lined()
                    value = input("请输入将修改的数值：")
                    if value.isdigit():
                        data["max_memory"] = int(value)
                        print("最大堆内存大小修改成功！")
                    else:
                        print("最大堆内存大小修改失败，请检查数据类型。")
                    lined()
                elif value == "2":
                    print("配置核心文件名称")
                    print("请注意输入文件拓展名：.jar")
                    print(f"原名称：{data["jar_name"]}")
                    lined()
                    value = input("请输入将修改的名称：")
                    if value.endswith(".jar"):
                        data["jar_name"] = value
                        print("核心文件名称修改成功！")
                    else:
                        print("核心文件名称修改失败，请检查数据类型。")
                    lined()
                elif value == "3":
                    print("配置模组加载器")
                    print(f"原模组加载器：{data["loader"]}")
                    lined()
                    for i, loader in enumerate(loaders):
                        print(f"[{i}] {loader}")
                    value = input("请选择将修改的加载器：")
                    if value.isdigit():
                        int_value = int(value)
                        if 0 <= int_value < len(loaders):
                            data["loader"] = loaders[int_value]
                            print("模组加载器修改成功！")
                        else:
                            print("模组加载器修改失败，请检查索引范围。")
                    else:
                        print("模组加载器修改失败，请检查数据类型。")
                    lined()
                elif value == "4":
                    print("配置游戏版本")
                    print(f"原游戏版本：{data["version"]}")
                    lined()
                    value = input("请输入将修改的游戏版本：")
                    value_split = value.split(".")
                    if all([i.isdigit() for i in value_split]) and len(value_split) == 3:
                        data["version"] = value
                        print("游戏版本修改成功！")
                    else:
                        print("游戏版本修改失败，请检查数据类型。")
                    lined()
                elif value == "5":
                    print("配置JDK绝对路径")
                    print("请注意输入完整的绝对路径，空字符串则自动使用java命令。")
                    print("示例：C:/Program Files/Zulu/zulu-17")
                    print(f"原路径：{data["jdk_path"]}")
                    lined()
                    value = input("请输入将修改的路径：")
                    if value == "":
                        data["jdk_path"] = None
                        print("JDK绝对路径修改成功！")
                    else:
                        if isabs(value):
                            data["jdk_path"] = value
                            print("JDK绝对路径修改成功！")
                        else:
                            print("JDK绝对路径修改失败，请检查路径完整性。")
                    lined()
                elif value == "6":
                    print("配置强制启动服务器（绕过版本检测）")
                    print(f"原值：{"启用" if data["allow_force_run"] else "未启用"}")
                    lined()
                    print("[0] 启用")
                    print("[1] 不启用")
                    lined()
                    value = input("请选择将修改的值：")
                    data["allow_force_run"] = value != "1"
                    print(f"强制启动配置成功：{"启用" if data["allow_force_run"] else "未启用"}")
                    lined()
                elif value == "7":
                    print("配置强制重启服务器（绕过版本检测）")
                    print(f"原值：{"启用" if data["allow_force_reboot"] else "未启用"}")
                    lined()
                    print("[0] 启用")
                    print("[1] 不启用")
                    lined()
                    value = input("请选择将修改的值：")
                    data["allow_force_reboot"] = value != "1"
                    print(f"强制重启配置成功：{"启用" if data["allow_force_reboot"] else "未启用"}")
                    lined()
                elif value == "8":
                    print("配置重启等待时间（秒）")
                    print(f"原数值：{data["reboot_time"]}")
                    lined()
                    value = input("请输入将修改的数值：")
                    if value.isdigit():
                        data["reboot_time"] = int(value)
                        print("重启等待时间修改成功！")
                    else:
                        print("重启等待时间修改失败，请检查数据类型。")
                    lined()
                elif value == "9":
                    show_jvm_args_config(data)
                else:
                    result = settings_write(data)
                    if result[0] != 0:
                        print(f"配置文件修改失败，错误信息：'{result[1]}'")
                        lined()
                    break
                    
        elif value == "4":
            out, err = subprocess.Popen(
                args=["java", "--version"],
                shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()
            outs = out.decode("ascii")
            errs = err.decode("ascii")
            java_home = environ.get("JAVA_HOME")
            if java_home is not None:
                print(f"JAVA_HOME：{java_home}")
                lined()
            print(outs, end="")
            if errs != "":
                print(errs)
            lined()
            input("Press Any Key...")
            lined()

        elif value == "5":
            return 0
        else:
            print("输入的内容无效。")
            lined()

if __name__ == "__main__":
    main()