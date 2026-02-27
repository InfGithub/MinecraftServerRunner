from util import Config, LANG

from os import remove, path
from sys import platform
from shutil import rmtree
from typing import Literal, Callable
from subprocess import check_output, CalledProcessError

caches: list[str] = [
    "__pycache__/",
    "logs/",
    "debug/"
    "dynamic-data-pack-cache/",
    "usercache.json",
    "mods/.connector/",
    "usernamecache.json"
]

vasts: list[str] = caches + [
    ".fabric/",
    "fabricloader.log",
    "moddata/",
    "moonlight-global-datapacks/",
    "patchouli_books/",
    "tacz_backup/",
    # "tlm_custom_pack/", 不能删！这是玩家自定义皮肤
    ".gunsmithlib/",
    ".mixin.out/",
]

resets: list[str] = vasts + [
    "world/",
    "banned-ips.json",
    "banned-players.json",
    "ops.json",
    "whitelist.json",
]

def clean(
    dtype: Literal[0, 1, 2] = 0,
    print_function: Callable = print,
    complete_function: Callable = None
):
    if dtype == 0:
        data_list = caches
    elif dtype == 1:
        data_list = vasts
    elif dtype == 2:
        data_list = resets
    else:
        return

    for name in data_list:
        if not path.exists(name):
            continue

        try:
            if path.isdir(name):
                rmtree(name)
            else:
                remove(name)
            print_function(LANG("tool.text.delete", name))

        except Exception as e:
            print_function(f"异常：{e}")

    if complete_function:
        complete_function()

def check_network(encoding: Literal["ascii", "gbk"] = "gbk") -> list[str]:
    try:
        if platform == "win32":
            return check_output(
                "ipconfig", shell=True, text=True, encoding=encoding
            ).splitlines()
 
        else:
            try:
                return check_output("ifconfig", shell=True, text=True).splitlines()
            except:
                return check_output("ip addr", shell=True, text=True).splitlines()

    except CalledProcessError as e:
        return [LANG("tool.text.error.run", e)]
    except Exception as e:
        return [LANG("tool.text.error.info", e)]

def write_eula():
    try:
        with open("eula.txt", mode="w", encoding="utf-8") as f:
            f.write("#INF.\neula=true")
    except:
        return

def string_is_float(string: str) -> bool:
    if not "." in string:
        return False
    if not string.count(".") == 1:
        return False

    alpha, beta = string.split(".")

    anumber: str = alpha[1:] if alpha.startswith("-") else alpha

    if not anumber:
        pass
    elif not anumber.isdigit():
        return False
    if not beta:
        pass
    elif not beta.isdigit():
        return False

    return True

def load_properties(file_path: str = "server.properties") -> Config:
    properties: dict = dict()

    if not path.exists(file_path):
        return

    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            text: list[str] = f.readlines()
    except:
        return

    for line in text:

        string: str = line.strip()

        if string.startswith("#"):
            continue
        if string.startswith("="):
            continue
        if not "=" in string:
            continue


        alpha, *beta = string.split("=")
        beta: str = beta[0] if len(beta) == 1 else "=".join(beta)

        if beta == "":
            beta = None
        elif beta.isdigit():
            beta = int(beta)
        elif beta == "true":
            beta = True
        elif beta == "false":
            beta = False
        elif string_is_float(beta):
            beta = float(beta)

        properties[alpha] = beta

    return Config(properties)

def save_properties(config: Config, file_path: str = "server.properties"):
    text: list[str] = list()

    for key, value in config.items():
        if value is None:
            text.append(f"{key}=\n")
        elif isinstance(value, bool):
            text.append(f"{key}={"true" if value else "false"}\n")
        elif isinstance(value, int):
            text.append(f"{key}={value}\n")
        elif isinstance(value, float):
            text.append(f"{key}={value}\n")
        elif isinstance(value, str):
            text.append(f"{key}={value}\n")
    try:
        with open(file_path, mode="w", encoding="utf-8") as f:
            f.writelines(text)
    except Exception as err:
        return