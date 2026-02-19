from os import remove, path
from shutil import rmtree
from typing import Literal

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

                print(f"删除：{name}")

        except Exception as e:
                print(f"异常：{e}")