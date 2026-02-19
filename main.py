from ui import InfoList, Choose, InputSet, Page
from util import Config
from expand import (
	loaders, default_server_config,
	default_running_config, jvm_args_info,
	title, get_env, generate_auto_jvm_args,
	ServerConfigType, RunningType, ServerStream
)
from tool import clean, check_network, write_eula

# ----------------------------------------------------------------

server_config: Config[ServerConfigType] = Config[ServerConfigType].load_from(
	file_path="config.json", default=default_server_config
)

running_config: Config[RunningType] = Config[RunningType](
	data=default_running_config
)

# ----------------------------------------------------------------

def multi_run_server():
	ServerStream(
		server_config=server_config,
		running_config=running_config,
		base_color="red"
	).do()

def run_server():
	running_config["reboot_time"] = 1
	multi_run_server()

def replace_jvm_args_config_auto():
	server_config["jvm_args"] = generate_auto_jvm_args(server_config)

# ----------------------------------------------------------------

run_server_ui: InfoList = InfoList(
	description="再次按下任意键，以启动服务器。",
	enable_exit_prompt=True,
	complete_call_function=run_server
)

# ----------------------------------------------------------------

multi_run_server_ui: InputSet = InputSet(
	description="请输入重启次数。",
	prompt="输入负值可无限循环。",
	config=running_config,
	config_key="reboot_time",
	data_type="int",
	complete_call_function=multi_run_server,
	display_current_value=False
)

# ----------------------------------------------------------------

jvm_args_config_ui_list: list[Page] = [InfoList(
	description="确定生成JVM参数吗？",
	enable_exit_prompt=True,
	complete_call_function=replace_jvm_args_config_auto
)]

# ----------------------------------------------------------------

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
key_max_length: int = max([len(key) for key in jvm_args_info.keys()])

# ----------------------------------------------------------------

jvm_args_config_ui_text_list: list[str] = [
	"自动生成适宜的JVM参数",
	*[f"{key} {"." * (key_max_length - len(key) + 6)} {value["desc"]}" for key, value in jvm_args_info.items()]
]

# ----------------------------------------------------------------

jvm_args_config_ui: Choose = Choose(
	description="请选择将要修改的参数。",
	text=jvm_args_config_ui_text_list,
	data=jvm_args_config_ui_list
)

# ----------------------------------------------------------------

config_ui: Choose = Choose(
	text=[
		"设置初始堆内存大小", "设置最大堆内存大小", "设置核心文件名称", "设置模组加载器",
		"设置游戏版本", "配置JDK绝对路径", "配置重启等待时间", "配置高级JVM参数"
	],
	data=[
		InputSet(
			description="配置初始堆内存大小（GB）", config=server_config,
			config_key="min_memory", data_type="int"
		),
		InputSet(
			description="配置最大堆内存大小（GB）", config=server_config,
			config_key="max_memory", data_type="int"
		),
		InputSet(
			description="配置核心文件名称", prompt="请注意输入文件拓展名：.jar",
			config=server_config, config_key="jar_name",
			data_type="str"
		),
		Choose(
			description="配置模组加载器", text=loaders, data=loaders,
			config=server_config, config_key="loader", end_line=False,
			value_mapping=dict(enumerate(loaders))
		),
		InputSet(
			description="配置游戏版本", config=server_config,
			config_key="version", data_type="str"
		),
		InputSet(
			description="配置JDK绝对路径",
			prompt="请注意输入完整的绝对路径。\n示例：C:/Program Files/Zulu/zulu-17",
			config=server_config, config_key="jdk_path",
			data_type="str", default="java"
		),
		InputSet(
			description="配置重启等待时间（秒）", config=server_config,
			config_key="reboot_seconds", data_type="int"
		),
		jvm_args_config_ui
	],
	description="请选择将要修改的配置。",
	exit_call_function=server_config.save
)

# ----------------------------------------------------------------

env_ui: InfoList = InfoList(
	description="运行环境信息。",
	call_function=lambda: get_env(server_config.data)
)

clean_ui: InputSet = InputSet(
	description="选择清理等级",
	prompt="[0] 日志+缓存 [1] 日志+临时数据 [2] 重置",
	config=running_config,
	config_key="clean_type",
	data_type="int",
	display_current_value=False,
	base_color="red"
)
clean_ui.complete_call_function = lambda: clean(
	running_config["clean_type"], clean_ui.print
)

net_ui: InfoList = InfoList(
	description="网络信息",
	call_function=lambda: check_network(),
	base_color="magenta"
)

eula_ui: InfoList = InfoList(
	description="再次按下任意键，以修改eula.txt。",
	texts=["继续前，请先阅读并同意此协议：https://aka.ms/MinecraftEULA"],
	enable_exit_prompt=True,
	complete_call_function=write_eula,
)

# ----------------------------------------------------------------

tool_ui: Choose = Choose(
	description="选择要执行的功能",
	text=[
		"检测运行环境",
		"清理文件数据",
		"查看网络信息",
		"修改EULA协议"
	],
	data=[
		env_ui,
		clean_ui,
		net_ui,
		eula_ui
	]
)

# ----------------------------------------------------------------

if __name__ == "__main__":

	title(f"Minecraft Server Runner")
	InfoList(
		description=f"Minecraft Server Runner\tAuthor: Inf",
		texts=[
			R" __  __   ___   ___                            ___",
			R"|  \/  | / __| / __| ___  _ _ __ __ ___  _ _  | _ \ _  _  _ _   _ _   ___  _ _",
			R"| |\/| || (__  \__ \/ -_)| '_|\ V // -_)| '_| |   /| || || ' \ | ' \ / -_)| '_|",
			R"|_|  |_| \___| |___/\___||_|   \_/ \___||_|   |_|_\ \_,_||_||_||_||_|\___||_|"
		],
		base_color="bright_yellow"
	).do()

	Choose(
		text=[
			"启动服务器",
			"启动服务器（自动重启）",
			"修改启动配置",
			"工具箱"
		],
		data=[
			run_server_ui,
			multi_run_server_ui,
			config_ui,
			tool_ui
		],
		description="请选择将要使用的功能。",
		base_color="blue"
	).do()