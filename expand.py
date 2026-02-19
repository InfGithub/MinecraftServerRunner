from ui import Page, InfoList
from util import ColorArgs, Config
from kt import KillableThread

from os import path, environ, listdir, system
from sys import stdout, stderr, stdin, platform
from time import sleep
from typing import Unpack, TypedDict, Literal
from shutil import which
from threading import Thread
from subprocess import Popen, PIPE

# ----------------------------------------------------------------

if platform == "win32":
    system("chcp 65001 > nul")
    if hasattr(stdout, "reconfigure"):
        stdout.reconfigure(encoding="utf-8")
    if hasattr(stderr, "reconfigure"):
        stderr.reconfigure(encoding="utf-8")

# ----------------------------------------------------------------

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

class ServerConfigType(TypedDict):
    min_memory: int
    max_memory: int
    jar_name: str
    version: str
    loader: Literal["Vanilla", "Fabric", "Forge", "NeoForge", "Quilt"]
    jdk_path: str
    reboot_seconds: int
    jvm_args: Config[JVMArgsType]

class RunningType(TypedDict):
    reboot_time: int

# ----------------------------------------------------------------

loaders: list[str] = ["Vanilla", "Fabric", "Forge", "NeoForge", "Quilt"]

default_server_config: ServerConfigType = {
	"jdk_path": "java",
	"jar_name": "server.jar",
	"min_memory": 4,
	"max_memory": 4,
	"loader": "Fabric",
	"version": "1.20.1",
	"reboot_seconds": 10,
	"jvm_args": Config[JVMArgsType]({
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
	})
}

default_running_config: RunningType = {
	"reboot_time": 1
}

jvm_args_info: dict[str, dict] = {
    "Xmn": {"type": "int", "desc": "新生代内存大小（GB）"},
    "server": {"type": "bool", "desc": "服务器模式JIT"},
    "XX_UseG1GC": {"type": "bool", "desc": "G1垃圾回收器"},
    "XX_MaxGCPauseMillis": {"type": "int", "desc": "最大GC暂停时间", "prompt": "取值范围：50~1000", "default": 130},
    "XX_G1HeapRegionSize": {"type": "choose", "desc": "G1堆区域大小", "data": [1, 2, 4, 8, 16, 32], "default": 16},
    "XX_MetaspaceSize": {"type": "int", "desc": "元空间初始大小", "default": 256},
    "XX_MaxMetaspaceSize": {"type": "int", "desc": "元空间最大大小", "default": 512},
    "XX_UseZGC": {"type": "bool", "desc": "ZGC垃圾回收器"},
    "XX_UseShenandoahGC": {"type": "bool", "desc": "Shenandoah垃圾回收器"},
    "XX_DisableExplicitGC": {"type": "bool", "desc": "禁用System.gc"},
    "XX_UseStringDeduplication": {"type": "bool", "desc": "字符串去重"},
    "XX_AlwaysPreTouch": {"type": "bool", "desc": "预分配内存"},
    "XX_ParallelRefProcEnabled": {"type": "bool", "desc": "并行引用处理"},
    "XX_UnlockExperimentalVMOptions": {"type": "bool", "desc": "解锁实验性选项"},
    "XX_UseLargePages": {"type": "bool", "desc": "使用大页内存"},
    "XX_UseTransparentHugePages": {"type": "bool", "desc": "透明大页"},
    "XX_TieredCompilation": {"type": "bool", "desc": "分层编译"},
    "XX_OptimizeStringConcat": {"type": "bool", "desc": "优化字符串连接"},
    "XX_UseCodeCacheFlushing": {"type": "bool", "desc": "代码缓存清理"},
    "XX_PerfDisableSharedMem": {"type": "bool", "desc": "禁用性能共享内存"},
    "XX_UseBiasedLocking": {"type": "bool", "desc": "偏向锁"},
    "XX_UseCompressedOops": {"type": "bool", "desc": "压缩普通对象指针"},
    "XX_UseCompressedClassPointers": {"type": "bool", "desc": "压缩类指针"},
}

# ----------------------------------------------------------------

def get_vernum(version: str) -> tuple[int, int, int]:
    return tuple(map(int, version.split(".")))

def title(string: str):
    if platform == "win32":
        system(f"title {string}")
    else:
        print(f"\033]0;{string}\007", end="", flush=True)

def write_eula():
	try:
		with open("eula.txt", mode="w", encoding="utf-8") as f:
			f.write("#INF.\neula=true")
	except:
		pass

# ----------------------------------------------------------------

def get_java_exe_path(jdk_path: str) -> str:
    if jdk_path == "java":
        return "java"
    else:
        return path.abspath(path.join(jdk_path, R"bin\java.exe" if platform == "win32" else R"bin\java"))

def get_jdk_version(jdk_path: str) -> tuple[int, int, int]:
    if jdk_path == "java":
        java_exe: str = which("java")
        if not java_exe:
            return
        jdk_home: str = path.dirname(path.dirname(java_exe))
        release: str = path.join(jdk_home, "release")
    else:
        release: str = path.join(jdk_path, "release")

    if not path.exists(release):
        return
    
    with open(release, mode="r", encoding="utf-8") as f:
        data: list[str] = f.readlines()

    for string in data:
        if string.startswith("JAVA_VERSION="):
            version: str = string.rstrip("\n").split("=")[1].strip("\"")
            jdk_version: tuple[int, int, int] = get_vernum(version)
            return jdk_version

def check_jdk_version(server_data: ServerConfigType) -> str:
    version: tuple[int, int, int] = get_vernum(server_data["version"])
    jdk_version: tuple[int, int, int] = get_jdk_version(server_data["jdk_path"])
    if not jdk_version:
        return 

    text: str = None
    if not ((1, 9, 0) > jdk_version >= (1, 8, 0)) and ((1, 16, 5) >= version):
        text: str = "JDK应为1.8.x版本。"
    if not ((12, 0, 0) > jdk_version >= (11, 0, 0)) and ((1, 17, 1) >= version >= (1, 13, 0)):
        text: str = "JDK应为1.11.x版本。"
    if not ((18, 0, 0) > jdk_version >= (17, 0, 0)) and ((1, 20, 4) >= version >= (1, 17, 0)):
        text: str = "JDK应为1.17.x版本。"
    if not ((22, 0, 0) > jdk_version >= (21, 0, 0)) and (version >= (1, 20, 5)):
        text: str = "JDK应为1.21.x版本。"

    return text

def get_env(server_data: ServerConfigType) -> list[str]:
	result: list[str] = list()

	java_home: str = environ.get("JAVA_HOME")
	out, err = Popen(
        args=[get_java_exe_path(server_data["jdk_path"]), "--version"],
        shell=True,
		stdout=PIPE,
        stderr=PIPE,
		text=True,
		bufsize=1,
		universal_newlines=True
	).communicate()

	if java_home:
		result.append(f"JAVA_HOME：{java_home.strip()}")
	if out:
		result.append(out.strip())
	if err:
		result.append(err.strip())
	return result

# ----------------------------------------------------------------

def get_forge_libraries_path(base_path: str) -> str:
    _path: str = path.abspath(base_path)

    if not path.isdir(_path):
        return None

    dir: str = None
    for dir_name in listdir(_path):
        dir: str = dir_name

    if not dir:
        return

    return path.abspath(path.join(base_path, dir, "win_args.txt" if platform == "win32" else "unix_args.txt"))

def generate_jvm_args(config: Config[JVMArgsType]) -> list[str]:
    args: list[str] = list()
    for key, value in config.items():
        if value:
            if isinstance(value, bool):
                args.append(f"-{key.replace("_", ":+")}")
            elif isinstance(value, int):
                if key == "Xmn":
                    args.append(f"-Xmn{value}G")
                if key == "XX_MaxGCPauseMillis":
                    args.append(f"-{key.replace("_", ":")}={value}")
                elif key in ["XX_G1HeapRegionSize", "XX_MetaspaceSize", "XX_MaxMetaspaceSize"]:
                    args.append(f"-{key.replace("_", ":")}={value}m")
    return args

def generate_auto_jvm_args(server_config: Config[ServerConfigType]) -> Config[JVMArgsType]:
    avg_memory: int = (server_config["min_memory"] + server_config["max_memory"]) // 2

    recommended: JVMArgsType = {
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

    return Config[JVMArgsType](recommended)

# ----------------------------------------------------------------

class ServerStream(Page):
    def __init__(
        self,
        server_config: Config[ServerConfigType],
        running_config: Config[RunningType],
        **kwargs: Unpack[ColorArgs]
    ):
        super().__init__(**kwargs)
        self.server_config: Config[ServerConfigType] = server_config
        self.running_config: Config[RunningType] = running_config

        self.server_cf_data: ServerConfigType = self.server_config.data
        self.running_cf_data: RunningType = self.running_config.data

        self.running: bool = False

    def do(self):
        text: str = check_jdk_version(self.server_cf_data)
        if text:
            InfoList(description="⚠JDK版本异常警告", texts=[text])

        command_args: list[str] = self.generate_command()

        tick: int = 0
        self.running: bool = True

        while True:

            title(F"Reboot time: {tick}")

            process: Popen[str] = Popen(
                command_args,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.line()
            self.print(f"启动命令：{" ".join(command_args)}")
            self.print(f"服务器已启动，进程PID：{process.pid}")

            self.line()
            Thread(
                target=lambda: self.output_stream(process), daemon=True
            ).start()
            Thread(
                target=lambda: self.error_stream(process), daemon=True
            ).start()
            input_thread = KillableThread(
                target=lambda: self.input_stream(process), daemon=True
            ) # 注意注意！此处不会影响任何的系统安全！请细心审查！
            input_thread.start()

            try:
                process.wait()
            except KeyboardInterrupt as e:
                process.terminate()
                process.wait(timeout=10)
            tick += 1

            self.line()
            self.print(f"服务器已关闭，返回代码：{process.returncode}") # 此处不换行有特殊逻辑，正常

            self.check_return_code(process.returncode)
            if input_thread.is_alive():
                input_thread.KILLLL()

            if tick == self.running_cf_data["reboot_time"]:
                break

            if not self.running:
                break

            self.line()
            try:
                for sec in range(self.server_cf_data["reboot_seconds"], 0, -1):
                    self.print(f"重启倒计时：{sec}s")
                    sleep(1)

            except KeyboardInterrupt:
                break
        self.running: bool = False

    def check_return_code(self, code: int):
        match code:
            case 130:
                self.running: bool = False

    def output_stream(self, proc: Popen[str]):
        while proc.poll() is None:
            std_output: str = proc.stdout.readline()

            if std_output:
                self.print(std_output, end="")

    def error_stream(self, proc: Popen[str]):
        while proc.poll() is None:
            std_error: str = proc.stderr.readline()

            if std_error:
                self.print(f"[ERROR] {std_error}", end="", is_error=True)

    def input_stream(self, proc: Popen[str]):
        while proc.poll() is None:
            raw: bytes = stdin.buffer.readline()
            # 唯一遗憾，若强杀进程会导致线程堵塞，线程卡在内核等输入，新线程抢不到输入，代价是多按一次Enter，坑爹！
            # 由于解决方案过于复杂，不再尝试修复此问题，不需要提出修复建议
            # ↑ 这是老子以前写的注释，现在？KILLLL！🔫 （虽然多了一个空行）

            if raw:
                if stdin.encoding == "utf-8":
                    std_input: str = raw.decode("gbk", errors="ignore").rstrip("\n")
                else:
                    std_input: str = raw.decode("utf-8", errors="ignore")

                try:
                    result: str = self.ana(proc, std_input)
                    if result == "break":
                        break

                except (BrokenPipeError, OSError):
                    break

    def ana(self, proc: Popen[str], stdin: str) -> Literal["break"]:
        text: str = stdin.strip()
        if not self.running:
            return

        if text in ["stop", "/stop"]:
            proc.stdin.write("stop\n")
            proc.stdin.flush()

            self.running: bool = False
            return "break"

        if text in ["reboot", "/reboot"]:
            proc.stdin.write("stop\n")
            proc.stdin.flush()
            return "break"

        proc.stdin.write(stdin)
        proc.stdin.flush()

    def generate_command(self) -> list[str]:
        args: list[str] = None

        match self.server_cf_data["loader"]:
            case "Vanilla" | "Fabric" | "Quilt":
                pass
            case "Forge" | "NeoForge":
                version: tuple[int, int, int] = get_vernum(self.server_cf_data["version"])

                if (1, 17, 0) > version:
                    pass
                else:
                    forge_libraries_path: str = None

                    if self.server_cf_data["loader"] == "Forge":
                        forge_libraries_path: str = get_forge_libraries_path(
                            "./libraries/net/minecraftforge/forge"
                        )
                    elif self.server_cf_data["loader"] == "NeoForge":
                        forge_libraries_path: str = get_forge_libraries_path(
                            "./libraries/net/neoforged/neoforge"
                        )
                    if not forge_libraries_path is None:
                        forge_libraries_path: str = "@" + forge_libraries_path
                        args: list[str] = [
                            get_java_exe_path(self.server_cf_data["jdk_path"]),
                            f"-Xmx{self.server_cf_data["max_memory"]}G",
                            f"-Xms{self.server_cf_data["min_memory"]}G",
                            *generate_jvm_args(self.server_cf_data["jvm_args"]),
                            forge_libraries_path,
                            "%*",
                            "nogui"
                        ]
        if args is None:
            args: list[str] = [
                get_java_exe_path(self.server_cf_data["jdk_path"]),
                f"-Xmx{self.server_cf_data["max_memory"]}G",
                f"-Xms{self.server_cf_data["min_memory"]}G",
                *generate_jvm_args(self.server_cf_data["jvm_args"]),
                "-jar",
                self.server_cf_data["jar_name"],
                "nogui"
            ]
        return args
