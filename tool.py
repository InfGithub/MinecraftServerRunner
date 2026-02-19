from os import remove, path
from sys import platform
from shutil import rmtree
from typing import Literal, Callable
from subprocess import check_output, CalledProcessError

caches: list[str] = [
    "__pycache__/",
    "logs/",
    "dynamic-data-pack-cache/",
    "usercache.json",
    "mods/.connector/"
]

vasts: list[str] = caches + [
    ".fabric/",
    "fabricloader.log",
    "moddata/",
    "moonlight-global-datapacks/",
    "patchouli_books/",
    "tacz_backup/",
    "tlm_custom_pack/",
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
    print_function: Callable = print
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
            print_function(f"删除：{name}")

        except Exception as e:
            print_function(f"异常：{e}")

def check_network(encoding: Literal["ascii", "gbk"] = "gbk") -> list[str]:
    try:
        if platform == "win32":
            return check_output(
                "ipconfig", shell=True, text=True, encoding=encoding
            ).splitlines()
 
        elif platform == "unix":
            try:
                return check_output("ifconfig", shell=True, text=True).splitlines()
            except:
                return check_output("ip addr", shell=True, text=True).splitlines()

    except CalledProcessError as e:
        return [f"执行命令失败: {e}"]
    except Exception as e:
        return [f"获取网络信息出错: {e}"]

def write_eula():
	try:
		with open("eula.txt", mode="w", encoding="utf-8") as f:
			f.write("#INF.\neula=true")
	except:
		pass