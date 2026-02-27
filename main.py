from util import LANG, server_config, running_config
from ui import InfoList, Choose, InputSet, Page
from core import (
    loaders, default_running_config, jvm_args_info,
    title, get_env, generate_auto_jvm_args,
    ServerStream
)
from tool import clean, check_network, write_eula, load_properties, save_properties

# ----------------------------------------------------------------

default_running_config["properties"] = load_properties()

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

def save_cfg():
    server_config.save()
    save_properties(default_running_config["properties"])

# ----------------------------------------------------------------

run_server_ui: InfoList = InfoList(
    description=LANG("main.text.run.server.desc"),
    enable_exit_prompt=True,
    complete_call_function=run_server
)

# ----------------------------------------------------------------

multi_run_server_ui: InputSet = InputSet(
    description=LANG("main.text.multi.run.server.desc"),
    prompt=LANG("main.text.multi.run.server.prompt"),
    config=running_config,
    config_key="reboot_time",
    data_type="int",
    complete_call_function=multi_run_server,
    display_current_value=False
)

# ----------------------------------------------------------------

jvm_args_config_ui_list: list[Page] = [InfoList(
    description=LANG("main.text.jvm.args.config.list.desc"),
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
                prompt=LANG("main.text.jvm.args.config.list.prompt", value["default"])
            )
        )
    else:
        prompt: list[str] = list()
        if "prompt" in value:
            prompt.append(value["prompt"])
        if "default" in value:
            prompt.append(LANG("main.text.jvm.args.config.list.prompt", value["default"]))
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
    LANG("main.text.jvm.args.config.text.list.desc"),
    *[f"{key} {"." * (key_max_length - len(key) + 6)} {value["desc"]}" for key, value in jvm_args_info.items()]
]

# ----------------------------------------------------------------

jvm_args_config_ui: Choose = Choose(
    description=LANG("main.text.jvm.args.config.desc"),
    text=jvm_args_config_ui_text_list,
    data=jvm_args_config_ui_list
)

# ----------------------------------------------------------------

backup_config_ui: Choose = Choose(
    description=LANG("main.text.backup.config.desc"),
    text=[
        LANG("main.text.backup.config.text1"),
        LANG("main.text.backup.config.text2"),
        LANG("main.text.backup.config.text3"),
        LANG("main.text.backup.config.text4")
    ],
    data=[
        InputSet(
            description=LANG("main.text.backup.config.text1"),
            config=server_config["backup_settings"],
            config_key="enable",
            data_type="bool"
        ),
        InputSet(
            description=LANG("main.text.backup.config.text2"),
            config=server_config["backup_settings"],
            config_key="backup_time",
            data_type="list"
        ),
        InputSet(
            description=LANG("main.text.backup.config.text3"),
            config=server_config["backup_settings"],
            config_key="backup_max",
            data_type="int"
        ),
        InputSet(
            description=LANG("main.text.backup.config.text4"),
            config=server_config["backup_settings"],
            config_key="backup_path",
            data_type="str",
            prompt=LANG("main.text.backup.config.text4.prompt")
        )
    ]
)

# ----------------------------------------------------------------

config_ui: Choose = Choose(
    text=[
        LANG("main.text.config.text1"),
        LANG("main.text.config.text2"),
        LANG("main.text.config.text3"),
        LANG("main.text.config.text4"),
        LANG("main.text.config.text5"),
        LANG("main.text.config.text6"),
        LANG("main.text.config.text7"),
        LANG("main.text.config.text8"),
        LANG("main.text.config.text9"),
    ],
    data=[
        InputSet(
            description=LANG("main.text.backup.config.text1"), config=server_config,
            config_key="min_memory", data_type="int"
        ),
        InputSet(
            description=LANG("main.text.backup.config.text2"), config=server_config,
            config_key="max_memory", data_type="int"
        ),
        InputSet(
            description=LANG("main.text.backup.config.text3"),
            prompt=LANG("main.text.backup.config.text3.prompt"),
            config=server_config, config_key="jar_name",
            data_type="str"
        ),
        Choose(
            description=LANG("main.text.backup.config.text4"), text=loaders, data=loaders,
            config=server_config, config_key="loader", end_line=False,
            value_mapping=dict(enumerate(loaders))
        ),
        InputSet(
            description=LANG("main.text.backup.config.text5"), config=server_config,
            config_key="version", data_type="str"
        ),
        InputSet(
            description=LANG("main.text.backup.config.text6"),
            prompt=LANG("main.text.backup.config.text6.prompt"),
            config=server_config, config_key="jdk_path",
            data_type="str", default="java"
        ),
        InputSet(
            description=LANG("main.text.backup.config.text7"), config=server_config,
            config_key="reboot_seconds", data_type="int"
        ),
        jvm_args_config_ui,
        backup_config_ui
    ],
    description=LANG("main.text.config.desc")
)

# ----------------------------------------------------------------

env_ui: InfoList = InfoList(
    description=LANG("main.text.env.desc"),
    call_function=lambda: get_env(
        server_config.data,
        running_config.data
    )
)

clean_ui: InputSet = InputSet(
    description=LANG("main.text.clean.desc"),
    prompt=LANG("main.text.clean.prompt"),
    config=running_config,
    config_key="clean_type",
    data_type="int",
    display_current_value=False,
    base_color="red"
)
clean_ui.complete_call_function = lambda: clean(
    running_config["clean_type"],
    print_function=clean_ui.print,
    complete_function=clean_ui.line
)

net_ui: InfoList = InfoList(
    description=LANG("main.text.net.desc"),
    call_function=lambda: check_network(),
    base_color="magenta"
)

eula_ui: InfoList = InfoList(
    description=LANG("main.text.eula.desc"),
    texts=[LANG("main.text.eula.text", "https://aka.ms/MinecraftEULA")],
    enable_exit_prompt=True,
)
eula_ui.complete_call_function=write_eula

# ----------------------------------------------------------------

tool_ui: Choose = Choose(
    description=LANG("main.text.tool.desc"),
    text=[
        LANG("main.text.tool.text1"),
        LANG("main.text.tool.text2"),
        LANG("main.text.tool.text3"),
        LANG("main.text.tool.text4"),
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
        description=f"Minecraft Server Runner | Author: Inf",
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
            LANG("main.text.ui.text1"),
            LANG("main.text.ui.text2"),
            LANG("main.text.ui.text3"),
            LANG("main.text.ui.text4"),
        ],
        data=[
            run_server_ui,
            multi_run_server_ui,
            config_ui,
            tool_ui
        ],
        description=LANG("main.text.ui.desc"),
        base_color="blue",
        exit_call_function=save_cfg
    ).do()