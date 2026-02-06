from ui import InfoList, Choose, InputSet, Page
from util import Config
from expand import (
	loaders,
	title, get_env, generate_auto_jvm_args,
	ServerConfigType, JVMArgsType, RunningType, ServerStream
)

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
    "XX_MaxGCPauseMillis": {"type": " int", "desc": "最大GC暂停时间", "prompt": "取值范围：50~1000", "default": 130},
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