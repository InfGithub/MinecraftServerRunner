from util import (
    ColorArgs, Config, ServerConfigType, RunningType, JVMArgsType, BackupSettings,
    LANG, default_running_config, default_server_config
)
from ui import Page, InfoList
from kt import KillableThread

from os import path, environ, listdir, system, mkdir, remove
from sys import stdout, stderr, stdin, platform
from time import sleep, strftime
from typing import Unpack, Literal
from shutil import which
from threading import Thread, Event
from subprocess import Popen, PIPE

# ----------------------------------------------------------------

if platform == "win32":
    system("chcp 65001 > nul")
    if hasattr(stdout, "reconfigure"):
        stdout.reconfigure(encoding="utf-8")
    if hasattr(stderr, "reconfigure"):
        stderr.reconfigure(encoding="utf-8")

# ----------------------------------------------------------------

loaders: list[str] = ["Vanilla", "Fabric", "Forge", "NeoForge", "Quilt"]

jvm_args_info: dict[str, dict] = {
    "Xmn": {"type": "int", "desc": LANG("core.jvm.args.info.Xmn")},
    "server": {"type": "bool", "desc": LANG("core.jvm.args.info.server")},
    "XX_UseG1GC": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseG1GC")},
    "XX_MaxGCPauseMillis": {
        "type": "int", "desc": LANG("core.jvm.args.info.XX_MaxGCPauseMillis"),
        "prompt": LANG("core.jvm.args.info.XX_MaxGCPauseMillis.range"), "default": 130
    },
    "XX_G1HeapRegionSize": {
        "type": "choose", "desc": LANG("core.jvm.args.info.XX_G1HeapRegionSize"),
        "data": [1, 2, 4, 8, 16, 32], "default": 16
    },
    "XX_MetaspaceSize": {"type": "int", "desc": LANG("core.jvm.args.info.XX_MetaspaceSize"), "default": 256},
    "XX_MaxMetaspaceSize": {"type": "int", "desc": LANG("core.jvm.args.info.XX_MaxMetaspaceSize"), "default": 512},
    "XX_UseZGC": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseZGC")},
    "XX_UseShenandoahGC": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseShenandoahGC")},
    "XX_DisableExplicitGC": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_DisableExplicitGC")},
    "XX_UseStringDeduplication": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseStringDeduplication")},
    "XX_AlwaysPreTouch": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_AlwaysPreTouch")},
    "XX_ParallelRefProcEnabled": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_ParallelRefProcEnabled")},
    "XX_UnlockExperimentalVMOptions": {
        "type": "bool", "desc": LANG("core.jvm.args.info.XX_UnlockExperimentalVMOptions")
    },
    "XX_UseLargePages": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseLargePages")},
    "XX_UseTransparentHugePages": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseTransparentHugePages")},
    "XX_TieredCompilation": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_TieredCompilation")},
    "XX_OptimizeStringConcat": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_OptimizeStringConcat")},
    "XX_UseCodeCacheFlushing": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseCodeCacheFlushing")},
    "XX_PerfDisableSharedMem": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_PerfDisableSharedMem")},
    "XX_UseBiasedLocking": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseBiasedLocking")},
    "XX_UseCompressedOops": {"type": "bool", "desc": LANG("core.jvm.args.info.XX_UseCompressedOops")},
    "XX_UseCompressedClassPointers": {
        "type": "bool", "desc": LANG("core.jvm.args.info.XX_UseCompressedClassPointers")
    }
}

# ----------------------------------------------------------------

try:
    from schedule import run_pending, every
    from tarfile import open as taropen
    default_running_config["schedule_installed"] = True

except ImportError:
    default_running_config["schedule_installed"] = False

# ----------------------------------------------------------------

def get_vernum(version: str) -> tuple[int, int, int]:
    return tuple(map(int, version.split(".")))

def title(string: str):
    if platform == "win32":
        system(f"title {string}")
    else:
        print(f"\033]0;{string}\007", end="", flush=True)

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
        text: str = LANG("core.text.error.jdk.version.tip", "1.8.x")
    if not ((12, 0, 0) > jdk_version >= (11, 0, 0)) and ((1, 17, 1) >= version >= (1, 13, 0)):
        text: str = LANG("core.text.error.jdk.version.tip", "11.x.x")
    if not ((18, 0, 0) > jdk_version >= (17, 0, 0)) and ((1, 20, 4) >= version >= (1, 17, 0)):
        text: str = LANG("core.text.error.jdk.version.tip", "17.x.x")
    if not ((22, 0, 0) > jdk_version >= (21, 0, 0)) and (version >= (1, 20, 5)):
        text: str = LANG("core.text.error.jdk.version.tip", "21.x.x")

    return text

def get_env(server_data: ServerConfigType, running_data: RunningType) -> list[str]:
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
    if not running_data:
        result.append(LANG("core.text.tip.module.schedule.missing"))

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
            InfoList(description="core.text.error.jdk.version", texts=[text])

        command_args: list[str] = self.generate_command()

        self.tick: int = 0
        self.running: bool = True
        self.checking_backup: bool = (
            self.running_cf_data["schedule_installed"] and
            self.server_cf_data["backup_settings"]["enable"]
        )
        self.backup_event: Event = Event()

        while True:
            self.backup_event.clear()
            title(F"Reboot time: {self.tick}")

            process: Popen[str] = Popen(
                command_args,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.print(LANG("core.text.run.command", " ".join(command_args)))
            self.print(LANG("core.text.start.pid", process.pid))

            self.line()
            Thread(
                target=lambda: self.output_stream(process), daemon=True
            ).start()
            Thread(
                target=lambda: self.error_stream(process), daemon=True
            ).start()
            input_thread: KillableThread = KillableThread(
                target=lambda: self.input_stream(process), daemon=True
            ) # 注意注意！此处不会影响任何的系统安全！请细心审查！
            input_thread.start()
            Thread(
                target=lambda: self.checking_backup_thread(process), daemon=True
            ).start()

            try:
                process.wait()
            except KeyboardInterrupt as e:
                process.terminate()
                process.wait(timeout=10)

            self.line()
            self.print(LANG("core.text.stop.code", process.returncode)) # 此处不换行有特殊逻辑，正常

            self.line()
            self.check_return_code(process.returncode)

            if self.checking_backup:
                self.backup_event.wait()

            if input_thread.is_alive():
                input_thread.KILLLL()

            if self.tick == self.running_cf_data["reboot_time"]:
                break

            if not self.running:
                break

            self.line()
            try:
                for sec in range(self.server_cf_data["reboot_seconds"], 0, -1):
                    self.print(LANG("core.text.reboot.ticks", sec))
                    sleep(1)

            except KeyboardInterrupt:
                break
        self.running: bool = False

    def check_return_code(self, code: int):
        match code:
            case 130:
                self.running: bool = False
                self.checking_backup: bool = False
            case 0:
                pass
            case _:
                if self.checking_backup:
                    self.backup_event.set()

    def output_stream(self, proc: Popen[str]):
        while proc.poll() is None:
            std_output: str = proc.stdout.readline()

            if std_output:
                self.print(std_output, end="")

    def error_stream(self, proc: Popen[str]):
        while proc.poll() is None:
            std_error: str = proc.stderr.readline()

            if std_error:
                self.print(std_error, end="", is_error=True)

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
            self.backup_event.set()
            return "break"

        if text in ["reboot", "/reboot"]:
            proc.stdin.write("stop\n")
            proc.stdin.flush()

            self.tick -= 1
            self.backup_event.set()
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

    def backup_at_running(self, proc: Popen[str]):
        if not self.running:
            return

        self.tick -= 1
        proc.stdin.write("stop\n")
        proc.stdin.flush()
        proc.wait()

        self.backup() # 备份操作
        self.print(LANG("core.text.backup.complete"))
        self.line()

        self.backup_event.set()

    def checking_backup_thread(self, proc: Popen[str]):
        if not self.checking_backup:
            return

        for backup_time in self.server_cf_data["backup_settings"]["backup_time"]:
            try:
                every().day.at(backup_time).do(lambda: self.backup_at_running(proc))
            except Exception as err:
                self.print(LANG("core.text.error.backup.format", backup_time))
                self.line()
                return

        while self.checking_backup and proc.poll() is None:
            run_pending()
            sleep(1)

    def backup(self):
        backup_settings: BackupSettings = self.server_cf_data["backup_settings"]
        properties: dict = self.running_cf_data["properties"]

        if not path.exists(backup_settings["backup_path"]):
            mkdir(backup_settings["backup_path"])

        world_name: str = properties["level-name"]
        files: list[str] = sorted(listdir(backup_settings["backup_path"]))

        if len(files) >= backup_settings["backup_max"]:
            file_path: str = path.join(backup_settings["backup_path"], files[0])
            try:
                remove(file_path)
                self.print(LANG("core.text.delete.file", file_path))
                self.line()
            except Exception as e:
                self.print(LANG("ui.text.error", e))

        try:
            with taropen(
                path.join(
                    backup_settings["backup_path"],
                    f"{world_name}{strftime("%Y%m%d_%H%M%S")}.tar.gz"
                ),
                mode="w:gz"
            ) as f:
                f.add(world_name, arcname=world_name)
        except Exception as e:
            self.print(LANG("ui.text.error", e))
            self.line()