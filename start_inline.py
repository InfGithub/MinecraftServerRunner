from os import path, environ, listdir, system
from sys import stdout, stderr, stdin, platform
from json import dumps, loads, JSONDecodeError
from time import sleep
from typing import Any, Literal, TypedDict, TypeVar, Dict, Generic, Unpack, Callable
from threading import Thread
from subprocess import Popen, PIPE

T = TypeVar("T", bound=Dict[str, Any])

def convert(obj):
    if isinstance(obj, Config):
        return convert(obj.data)  # 递归处理嵌套的 Config
    elif isinstance(obj, dict):
        return {key: convert(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [convert(item) for item in obj]
    else:
        return obj

def rebuild(cls, obj):
    if isinstance(obj, dict): # 递归转换字典为 Config 对象
        config: Config = cls(obj)
        for key, value in obj.items():
            config[key] = rebuild(cls, value)
        return config
    elif isinstance(obj, list):
        return [rebuild(cls, item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(rebuild(cls, item) for item in obj)
    else:
        return obj

class Config(Generic[T]):
	def __init__(self, data: T = None):
		if data is None:
			data: T = dict()
		self.data: T = data

	def set(self, key: str, value: Any):
		self.data[key] = value

	def __repr__(self) -> str:
		return f"Config(data={self.data})"

	def get(self, key: str) -> Any:
		if key in self.data:
			return self.data[key]
		raise KeyError(f"Unknown Key: {key}")

	def __getitem__(self, key: str):
		return self.get(key)

	def __setitem__(self, key: str, value: Any):
		self.set(key, value)

	def __contains__(self, key: str) -> bool:
		return key in self.data

	def __delitem__(self, key: str):
		self.data.pop(key, None)

	def save(self, file_path: str = "config.json"):
		text: str = dumps(
			convert(self.data),
			indent=4,
			ensure_ascii=False,
			sort_keys=True
		)

		with open(file_path, mode="w", encoding="utf-8") as file:
			file.write(text)

	@classmethod
	def load_from(cls, file_path: str = "config.json", default: T = None):
		if not default:
			default: T = dict()
		try:
			with open(file_path, mode="r", encoding="utf-8") as file:
				text: str = file.read()

			data: T = loads(text)
			return rebuild(cls, data)
		except (FileNotFoundError, JSONDecodeError):
			return cls[T](default)

	def items(self):
		return self.data.items()

type Color = Literal[
	"reset",
	"bold",
	"underline",
	"black",
	"red",
	"green",
	"yellow",
	"blue",
	"magenta",
	"cyan",
	"white",
	"bright_black",
	"bright_red",
	"bright_green",
	"bright_yellow",
	"bright_blue",
	"bright_magenta",
	"bright_cyan",
	"bright_white",
	"bg_black",
	"bg_red",
	"bg_green",
	"bg_yellow",
	"bg_blue",
	"bg_magenta",
	"bg_cyan",
	"bg_white",
	"bg_bright_black",
	"bg_bright_red",
	"bg_bright_green",
	"bg_bright_yellow",
	"bg_bright_blue",
	"bg_bright_magenta",
	"bg_bright_cyan",
	"bg_bright_white"
]

colors_tab: dict[Color, str] = {
	"reset": "\033[0m",
	"bold": "\033[1m",
	"underline": "\033[4m",
	"black": "\033[30m",
	"red": "\033[31m",
	"green": "\033[32m",
	"yellow": "\033[33m",
	"blue": "\033[34m",
	"magenta": "\033[35m",
	"cyan": "\033[36m",
	"white": "\033[37m",
	"bright_black": "\033[90m",
	"bright_red": "\033[91m",
	"bright_green": "\033[92m",
	"bright_yellow": "\033[93m",
	"bright_blue": "\033[94m",
	"bright_magenta": "\033[95m",
	"bright_cyan": "\033[96m",
	"bright_white": "\033[97m",
	"bg_black": "\033[40m",
	"bg_red": "\033[41m",
	"bg_green": "\033[42m",
	"bg_yellow": "\033[43m",
	"bg_blue": "\033[44m",
	"bg_magenta": "\033[45m",
	"bg_cyan": "\033[46m",
	"bg_white": "\033[47m",
	"bg_bright_black": "\033[100m",
	"bg_bright_red": "\033[101m",
	"bg_bright_green": "\033[102m",
	"bg_bright_yellow": "\033[103m",
	"bg_bright_blue": "\033[104m",
	"bg_bright_magenta": "\033[105m",
	"bg_bright_cyan": "\033[106m",
	"bg_bright_white": "\033[107m",
	"": ""
}

class ColorArgs(TypedDict, total=False):
	base_color: Color | list[Color]
	error_color: Color

def colorize(text: str, *colors: Color) -> str:
	return f"{"".join([colors_tab[color] for color in colors])}{text}{colors_tab["reset"]}"

type InputSetAllowedType = Literal["int", "str", "bool"]

class Page:
	def __init__(self, base_color: Color | list[Color] = "", error_color: Color = "red"):
		if isinstance(base_color, str):
			self.base_colors = [base_color] if base_color else list()
		else:
			self.base_colors = base_color
		self.error_color = error_color

	def print(self, text: str, is_error: bool = False, *colors: Color, **kwargs):
			print(colorize(
				text, *colors, *self.base_colors, self.error_color if is_error else ""
				), **kwargs
			)

	def do(self):
		raise NotImplementedError("Unknown Action Function 'do'")

	def line(self, text: str = "-" * 64, **kwargs):
		print(colorize(text, *self.base_colors), **kwargs)

	def input(self, prompt: str) -> str:
		self.print(prompt, end="")
		return input()

class Choose(Page):
	def __init__(
		self,
		text: list[str],
		data: list[Page | Any],
		description: str,
		prompt: str = None,
		callback: bool = True,
		config: Config = None,
		config_key: str = None,
		exit_call_function: Callable = None,
		end_line: bool = True,
		value_mapping: dict[int, Any] = None,
		current_value_key: str = None,
		display_current_value: bool = True,
		**kwargs: Unpack[ColorArgs]
	):
		super().__init__(**kwargs)
		self.text: list[str] = text
		self.data: list[Page | Any] = data
		self.description: str = description
		self.prompt: str = prompt
		self.callback: bool = callback
		self.config: Config = config
		self.config_key: str = config_key
		self.index_max: int = len(self.data) - 1
		self.exit_call_function: Callable = exit_call_function
		self.end_line: bool = end_line
		self.value_mapping: dict[int, Any] = value_mapping
		self.current_value_key: str = current_value_key

		if self.config and self.current_value_key is None and display_current_value:
			self.current_value_key: str = self.config_key

	def do(self):
		self.print(f"{self.description}")
		self.line()

		tips: list[str] = list()
		if self.prompt:
			tips.append(f"提示：{self.prompt}")
		if self.callback:
			tips.append(f"按下Ctrl+C退出此页面。")
		if not self.current_value_key is None:
			tips.append(f"当前值：{self.config[self.current_value_key]}")

		if tips:
			for text in tips:
				self.print(text)
			self.line()

		for index, item in enumerate(self.text):
			self.print(f"[{index}] {item}")

		self.line()

		while True:
			try:
				result: str = self.input("输入：")
			except KeyboardInterrupt as err:
				print()

				if self.callback:
					if self.exit_call_function:
						self.exit_call_function()
					self.line()
					self.print(f"已退出此页面。")
					if self.end_line:
						self.line()
					return
				else:
					self.line()
					self.print(f"异常：捕获{err}。", is_error=True)
					self.line()
					continue

			if not result:
				self.print(f"异常：输入为空。", is_error=True)
				self.line()
				continue

			if not result.isdigit():
				self.print(
					f"异常：数据类型错误，应为{int}类型，取值范围：0 - {self.index_max}。",
					is_error=True
				)
				self.line()
				continue

			value: int = int(result)

			if value > self.index_max:
				self.print(f"异常：索引溢出，取值范围：0 - {self.index_max}。", is_error=True)
				self.line()
				continue

			var: Page | Any = self.data[value]

			if isinstance(var, Page):
				self.line()
				var.do()
			else:
				if self.value_mapping:
					if value in self.value_mapping: # 提供映射表以映射值
						var = self.value_mapping[value]
				self.config.set(self.config_key, var)
				if self.end_line:
					self.line()
				self.print(f"修改成功，已退出此页面。")
				self.line()
				return

class InputSet(Page):
	def __init__(
		self,
		description: str,
		config: Config,
		config_key: str,
		data_type: InputSetAllowedType,
		prompt: str = None,
		callback: bool = True,
		exit_call_function: Callable = None,
		complete_call_function: Callable = None,
		current_value_key: str = None,
		display_current_value: bool = True,
		default: str = None,
		**kwargs: Unpack[ColorArgs]
	):
		super().__init__(**kwargs)
		self.description: str = description
		self.prompt: str = prompt
		self.callback: bool = callback
		self.config: Config = config
		self.config_key: str = config_key
		self.data_type: InputSetAllowedType = data_type
		self.exit_call_function: Callable = exit_call_function
		self.complete_call_function: Callable = complete_call_function
		self.current_value_key: str = current_value_key
		self.default: str = default

		if self.config and self.current_value_key is None and display_current_value:
			self.current_value_key: str = self.config_key

	def do(self):
		self.print(f"{self.description}")
		self.line()

		tips: list[str] = list()
		if self.prompt:
			tips.append(f"提示：{self.prompt}")
		if self.callback:
			tips.append(f"按下Ctrl+C退出此页面。")
		if self.data_type == "bool":
			tips.append(f"输入y/n来指定布尔值。")
		if not self.current_value_key is None:
			tips.append(f"当前值：{self.config[self.current_value_key]}")
		if not self.default is None:
			tips.append(f"输入为空时使用默认值：{self.default}。")

		if tips:
			for text in tips:
				self.print(text)
			self.line()

		while True:
			try:
				result: str = self.input("输入：")
			except KeyboardInterrupt as err:
				print()

				if self.callback:
					if self.exit_call_function:
						self.exit_call_function()
					self.print(f"已退出此页面。")
					return
				else:
					self.line()
					self.print(f"异常：捕获{err}。", is_error=True)
					self.line()
					continue

			if not result:
				if self.default is None:
					self.print(f"异常：输入为空。", is_error=True)
					self.line()
					continue
				else:
					result: str = self.default
					self.line()

			if self.data_type == "int":
				if not result.lstrip("-").isdigit():
					self.print(f"异常：数据类型错误，应为{int}类型。", is_error=True)
					self.line()
					continue

				value: int = int(result)

			elif self.data_type == "str":
				value: str = result

			elif self.data_type == "bool":
				char: str = result[0].lower()
				if not char in {"y", "n"}:
					self.print(f"异常：数据内容错误，应为y/n。", is_error=True)
					self.line()
					continue

				is_yeah: bool = char == "y"
				value: bool = is_yeah

			self.config.set(self.config_key, value)
			self.print(f"修改成功，已退出此页面。")
			self.line()

			if self.complete_call_function:
				self.complete_call_function()
			return

class InfoList(Page):
	def __init__(
		self,
		texts: list[str] = None,
		description: str = None,
		call_function: Callable[[], list[str]] = None,
		complete_call_function: Callable = None,
		enable_exit_prompt: bool = False,
		**kwargs: Unpack[ColorArgs]
	):
		super().__init__(**kwargs)
		if not texts:
			texts: list[str] = list()
		self.texts: list[str] = texts
		self.description: str = description
		self.call_function: Callable[[], list[str]] = call_function
		self.complete_call_function: Callable = complete_call_function
		if enable_exit_prompt:
			self.texts.insert(0, "按下Ctrl+C以退出，将不会进行操作。")

	def do(self):
		if self.description:
			self.print(self.description)
			self.line()

		if self.texts:
			for item in self.texts:
				self.print(item)
			self.line()

		if self.call_function:
			result: list[str] = self.call_function()

			if result:
				for item in result:
					self.print(item)
				self.line()
		try:
			self.input("按下任意键以继续。")
			if self.complete_call_function:
				self.complete_call_function()
		except KeyboardInterrupt as err:
			print()
		self.line()

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

def get_forge_libraries_path(base_path: str) -> str:
    _path: str = path.abspath(base_path)

    if not path.isdir(_path):
        return None

    dir: str = None
    for dir_name in listdir(_path):
        dir: str = dir_name

    if not dir:
        return

    if platform == "win32":
        return path.abspath(path.join(base_path, dir, "win_args.txt"))
    else:
        return path.abspath(path.join(base_path, dir, "unix_args.txt"))

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
                        self.running: bool = False

                except (BrokenPipeError, OSError):
                    break

    def generate_command(self) -> list[str]:
        args: list[str] = None

        match self.server_cf_data["loader"]:
            case "Vanilla" | "Fabric" | "Quilt":
                pass
            case "Forge" | "NeoForge":
                version: tuple[int, int, int] = tuple([int(item) for item in self.server_cf_data["version"].split(".")])

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

def write_eula():
	try:
		with open("eula.txt", mode="w", encoding="utf-8") as f:
			f.write("#INF.\neula=true")
	except:
		pass

server_config: Config[ServerConfigType] = Config[ServerConfigType].load_from(
	file_path="config.json",
		default={
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
)

running_config: Config[RunningType] = Config[RunningType]({
	"reboot_time": 1
})

title("Minecraft Server Runner v2.2")
InfoList(
	description="Minecraft Server Runner v2.2\tAuthor: Inf",
	texts=[
		R" __  __   ___   ___                            ___",
		R"|  \/  | / __| / __| ___  _ _ __ __ ___  _ _  | _ \ _  _  _ _   _ _   ___  _ _",
		R"| |\/| || (__  \__ \/ -_)| '_|\ V // -_)| '_| |   /| || || ' \ | ' \ / -_)| '_|",
		R"|_|  |_| \___| |___/\___||_|   \_/ \___||_|   |_|_\ \_,_||_||_||_||_|\___||_|"
	],
	base_color="bright_yellow"
).do()

eula_ui: InfoList = InfoList(
	description="再次按下任意键，以修改eula.txt。",
	texts=["继续前，请先阅读并同意此协议：https://aka.ms/MinecraftEULA"],
	enable_exit_prompt=True,
	complete_call_function=write_eula,
)

def run_server():
	running_config["reboot_time"] = 1
	ServerStream(
		server_config=server_config,
		running_config=running_config,
		base_color="red"
	).do()

run_server_ui: InfoList = InfoList(
	description="再次按下任意键，以启动服务器。",
	enable_exit_prompt=True,
	complete_call_function=run_server
)

def multi_run_server():
	ServerStream(
		server_config=server_config,
		running_config=running_config,
		base_color="red"
	).do()

multi_run_server_ui: InputSet = InputSet(
	description="请输入重启次数。",
	prompt="输入负值可无限循环。",
	config=running_config,
	config_key="reboot_time",
	data_type="int",
	complete_call_function=multi_run_server,
	display_current_value=False
)

env_ui: InfoList = InfoList(
	description="运行环境信息。",
	call_function=lambda: get_env(server_config.data)
)

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

def replace_jvm_args_config_auto():
	server_config["jvm_args"] = generate_auto_jvm_args(server_config)

jvm_args_config_ui_list: list[Page] = [InfoList(
	description="确定生成JVM参数吗？",
	enable_exit_prompt=True,
	complete_call_function=replace_jvm_args_config_auto
)]

for key, value in jvm_args_info.items():
	if key == "XX_G1HeapRegionSize":
		jvm_args_config_ui_list.append(
			Choose(
				description=value["desc"],
				text=value["data"],
				data=value["data"],
				config=server_config["jvm_args"],
				config_key=key,
				prompt=f"建议值：{value["default"]}"
			)
		)
	else:
		prompt: list[str] = list()
		if "prompt" in value:
			prompt.append(value["prompt"])
		if "default" in value:
			prompt.append(f"建议值：{value["default"]}")
		jvm_args_config_ui_list.append(
			InputSet(
				description=value["desc"],
				data_type=value["type"],
				config=server_config["jvm_args"],
				config_key=key,
				prompt="\n".join(prompt)
			)
		)
key_max_length: int = max([len(key) for key, value in jvm_args_info.items()])
jvm_args_config_ui_text_list: list[str] = [
	"自动生成适宜的JVM参数",
	*[f"{key} {"." * (key_max_length - len(key) + 6)} {value["desc"]}" for key, value in jvm_args_info.items()]
]

jvm_args_config_ui: Choose = Choose(
	description="请选择将要修改的参数。",
	text=jvm_args_config_ui_text_list,
	data=jvm_args_config_ui_list
)

config_ui: Choose = Choose(
	text=[
		"设置初始堆内存大小",
		"设置最大堆内存大小",
		"设置核心文件名称",
		"设置模组加载器",
		"设置游戏版本",
		"配置JDK绝对路径",
		"配置重启等待时间",
		"配置高级JVM参数"
	],
	data=[
		InputSet(
			description="配置初始堆内存大小（GB）",
			config=server_config,
			config_key="min_memory",
			data_type="int"
		),
		InputSet(
			description="配置最大堆内存大小（GB）",
			config=server_config,
			config_key="max_memory",
			data_type="int"
		),
		InputSet(
			description="配置核心文件名称",
			prompt="请注意输入文件拓展名：.jar",
			config=server_config,
			config_key="jar_name",
			data_type="str"
		),
		Choose(
			description="配置模组加载器",
			text=loaders,
			data=loaders,
			config=server_config,
			config_key="loader",
			end_line=False,
			value_mapping=dict(enumerate(loaders))
		),
		InputSet(
			description="配置游戏版本",
			config=server_config,
			config_key="version",
			data_type="str"
		),
		InputSet(
			description="配置JDK绝对路径",
			prompt="请注意输入完整的绝对路径。\n示例：C:/Program Files/Zulu/zulu-17",
			config=server_config,
			config_key="jdk_path",
			data_type="str",
			default="java"
		),
		InputSet(
			description="配置重启等待时间（秒）",
			config=server_config,
			config_key="reboot_seconds",
			data_type="int"
		),
		jvm_args_config_ui
	],
	description="请选择将要修改的配置。",
	exit_call_function=server_config.save
)

Choose(
	text=[
		"启动服务器",
		"启动服务器（自动重启）",
		"修改EULA协议",
		"修改启动配置",
		"检测运行环境",
	],
	data=[
		run_server_ui,
		multi_run_server_ui,
		eula_ui,
		config_ui,
		env_ui
	],
	description="请选择将要使用的功能。",
	base_color="blue"
).do()