from ui import Page, InfoList
from util import ColorArgs, Config

from os import path, environ, listdir, system
from sys import stdout, stderr, stdin, platform
from time import sleep
from typing import Unpack, TypedDict, Literal
from threading import Thread
from subprocess import Popen, PIPE

if platform == "win32":
    system("chcp 65001 > nul")
    if hasattr(stdout, "reconfigure"):
        stdout.reconfigure(encoding="utf-8")
    if hasattr(stderr, "reconfigure"):
        stderr.reconfigure(encoding="utf-8")

loaders: list[str] = ["Vanilla", "Fabric", "Forge", "NeoForge", "Quilt"]

def title(string: str):
    if platform == "win32":
        system(f"title {string}")
    else:
        print(f"\033]0;{string}\007", end="", flush=True)

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

def get_java_exe_path(jdk_path: str) -> str:
    if jdk_path == "java":
        return "java"
    else:
        return path.abspath(path.join(jdk_path, R"bin\java.exe" if platform == "win32" else R"bin\java"))

def check_jdk_version(server_data: ServerConfigType) -> str:
    version: tuple[int, int, int] = tuple([int(item) for item in server_data["version"].split(".")])

    out, _ = Popen(
        args=[get_java_exe_path(server_data["jdk_path"]), "--version"],
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    ).communicate()
    jdk_version: tuple[int, int, int] = tuple([int(item) for item in out.split("\n")[0].split()[1].split(".")])

    text: str = ""
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

def check_stop_command(text: str) -> bool:
    text: str = text.strip()
    if text in ["stop", "/stop"]:
        return True
    return False

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

def get_forge_libraries_path(base_path: str = "./libraries/net/minecraftforge/forge") -> str:

    if not path.isdir(base_path):
        return None

    latest_dir: str = None
    latest_version: tuple[int, int, int] = (-1, -1, -1)

    for dir_name in listdir(base_path):
        dir_path: str = path.join(base_path, dir_name)
        if not path.isdir(dir_path):
            continue

        version_parts: list[str] = dir_name.split("-")
        if len(version_parts) < 2:
            continue

        forge_version_str: str = version_parts[1]
        forge_version_nums: list[int] = list()
        for part in forge_version_str.split("."):
            forge_version_nums.append(int(part) if part.isdigit() else 0)

        while len(forge_version_nums) < 3:
            forge_version_nums.append(0)

        current_version: tuple[int, int, int] = tuple(forge_version_nums)  # type: ignore

        if current_version > latest_version:
            latest_dir = dir_path
            latest_version = current_version

    return latest_dir

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
            Thread(
                target=lambda: self.input_stream(process), daemon=True
            ).start()

            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
                process.wait(timeout=10)
            tick += 1

            self.line()
            self.print(f"服务器已关闭，返回代码：{process.returncode}")

            if tick == self.running_cf_data["reboot_time"]:
                break

            self.line()
            try:
                for sec in range(self.server_cf_data["reboot_seconds"], 0, -1):
                    self.print(f"重启倒计时：{sec}s")
                    sleep(1)

            except KeyboardInterrupt:
                break

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
            std_input: str = stdin.readline()
            # 唯一遗憾，若强杀进程会导致线程堵塞，线程卡在内核等输入，新线程抢不到输入，代价是多按一次Enter，坑爹！
            # 由于解决方案过于复杂，不再尝试修复此问题，不需要提出修复建议

            if std_input:
                try:
                    proc.stdin.write(std_input)
                    proc.stdin.flush()

                    if check_stop_command(std_input):
                        break
                except (BrokenPipeError, OSError):
                    break

    def generate_command(self) -> list[str]:
        args: list[str] = None

        match self.server_cf_data["loader"]:
            case "Vanilla" | "Fabric" | "Quilt":
                pass
            case "Forge":
                version: tuple[int, int, int] = tuple([int(item) for item in self.server_cf_data["version"].split(".")])

                if (1, 17, 0) > version:
                    pass
                else:
                    forge_libraries_path: str = get_forge_libraries_path()
                    if not forge_libraries_path is None:
                        args: list[str] = [
                            get_java_exe_path(self.server_cf_data["jdk_path"]),
                            f"-Xmx{self.server_cf_data["max_memory"]}G",
                            f"-Xms{self.server_cf_data["min_memory"]}G",
                            *generate_jvm_args(self.server_cf_data["jvm_args"]),
                            "-jar",
                            self.server_cf_data["jar_name"],
                            forge_libraries_path.replace(".", "@"),
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