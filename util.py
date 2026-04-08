from typing import Any, Literal, TypedDict, TypeVar, Dict, Generic
from json import dumps, loads, JSONDecodeError
from lang import Lang, LanguageID
from logger import Logger

T = TypeVar("T", bound=Dict[str, Any])

# ----------------------------------------------------------------

class Language:
	def __init__(self, language: LanguageID = "zh_cn"):
		self.language: Dict[str, str] = Lang.get(language, dict())
	
	def __call__(self, index: str, *args: Any) -> str:
		text: str = self.language.get(index, index)
		if args:
			text %= args
		return text
	
	def set_language(self, language: LanguageID):
		self.language: Dict[str, str] = Lang.get(language, dict())

# ----------------------------------------------------------------

type Color = Literal[
	"reset", "bold", "underline",
	"black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
	"bright_black", "bright_red", "bright_green", "bright_yellow",
	"bright_blue", "bright_magenta", "bright_cyan", "bright_white", "bg_black",
	"bg_red", "bg_green", "bg_yellow", "bg_blue", "bg_magenta", "bg_cyan",
	"bg_white", "bg_bright_black", "bg_bright_red", "bg_bright_green",
	"bg_bright_yellow", "bg_bright_blue", "bg_bright_magenta","bg_bright_cyan",
	"bg_bright_white"
]

colors_tab: dict[Color, str] = {
	"reset": "\033[0m", "bold": "\033[1m", "underline": "\033[4m", "": "",
	"black": "\033[30m", "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
	"blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m", "white": "\033[37m",
	"bright_black": "\033[90m", "bright_red": "\033[91m", "bright_green": "\033[92m",
	"bright_yellow": "\033[93m", "bright_blue": "\033[94m", "bright_magenta": "\033[95m",
	"bright_cyan": "\033[96m", "bright_white": "\033[97m",
	"bg_black": "\033[40m", "bg_red": "\033[41m", "bg_green": "\033[42m",
	"bg_yellow": "\033[43m", "bg_blue": "\033[44m", "bg_magenta": "\033[45m",
	"bg_cyan": "\033[46m", "bg_white": "\033[47m", "bg_bright_black": "\033[100m",
	"bg_bright_red": "\033[101m", "bg_bright_green": "\033[102m",
	"bg_bright_yellow": "\033[103m", "bg_bright_blue": "\033[104m",
	"bg_bright_magenta": "\033[105m", "bg_bright_cyan": "\033[106m",
	"bg_bright_white": "\033[107m",
}

class ColorArgs(TypedDict, total=False):
	base_color: Color | list[Color]
	error_color: Color

def colorize(text: str, *colors: Color) -> str:
	return f"{"".join([colors_tab[color] for color in colors])}{text}{colors_tab["reset"]}"

# ----------------------------------------------------------------

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

# ----------------------------------------------------------------

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
		raise KeyError(Lang("util.unknown.key", key))

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

class BackupSettings(TypedDict):
    enable: bool
    backup_time: list[str]
    backup_max: int
    backup_path: str

class ServerConfigType(TypedDict):
    min_memory: int
    max_memory: int
    jar_name: str
    version: str
    loader: Literal["Vanilla", "Fabric", "Forge", "NeoForge", "Quilt"]
    jdk_path: str
    reboot_seconds: int
    jvm_args: JVMArgsType
    backup_settings: BackupSettings
    language: LanguageID

class RunningType(TypedDict):
    reboot_time: int
    schedule_installed: bool
    properties: dict

# ----------------------------------------------------------------

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
    }),
    "backup_settings": Config[JVMArgsType]({
        "enable": False,
        "backup_time": ["04:00:00"],
        "backup_max": 5,
        "backup_path": "backup/"
    }),
    "language": "zh_cn"
}

default_running_config: RunningType = {
    "reboot_time": 1
}

# ----------------------------------------------------------------

server_config: Config[ServerConfigType] = Config[ServerConfigType].load_from(
    file_path="config.json", default=default_server_config
)

running_config: Config[RunningType] = Config[RunningType](
    data=default_running_config
)

LANG: Language = Language(server_config["language"])

# ----------------------------------------------------------------

logger: Logger = Logger(
    level="DEBUG"
)