from os import remove, path
from shutil import rmtree
from typing import Literal, Callable, TypedDict
from psutil import net_if_stats, net_if_addrs

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

class IPV4(TypedDict):
    address: str | None
    netmask: str | None
    broadcast: str | None

class IPV6(TypedDict):
    address: str | None
    netmask: str | None

class CheckNetworkResultType(TypedDict):
    status: Literal["up", "down"]
    speed: int
    mtu: int
    ipv4: list[IPV4]
    ipv6: list[IPV6]
    mac: str | None

def calculate_broadcast(ip: str, netmask: str) -> str | None: # 计算广播地址
    try:
        ip_parts: list[int] = [int(x) for x in ip.split(".")]
        mask_parts: list[int] = [int(x) for x in netmask.split(".")]
        network: list[int] = [ip_parts[i] & mask_parts[i] for i in range(4)]
        broadcast: list[int] = list()
        for index in range(4):
            if mask_parts[index] == 255:
                broadcast.append(network[index])
            else:
                host_bits = 8 - bin(mask_parts[index]).count("1")
                broadcast.append(network[index] | ((1 << host_bits) - 1))
        return ".".join(str(x) for x in broadcast)
    except:
        pass

def check_network() -> list[str]:
    result: dict[str, CheckNetworkResultType] = dict()
    stats, addrs = net_if_stats(), net_if_addrs()

    for interface in stats.keys():
        if interface == "lo" or "loopback" in interface.lower():
            continue

        result[interface] = {
            "status": "up" if stats[interface].isup else "down",
            "speed": stats[interface].speed,
            "mtu": stats[interface].mtu,
            "ipv4": list(),
            "ipv6": list(),
            "mac": None
        }

        if interface in addrs:
            for addr in addrs[interface]:
                if addr.family == 2:
                    broadcast_addr = addr.broadcast

                    if broadcast_addr is None and addr.netmask:
                        broadcast_addr = calculate_broadcast(addr.address, addr.netmask)

                    result[interface]["ipv4"].append({
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": broadcast_addr
                    })
                elif addr.family == 23:
                    result[interface]["ipv6"].append({
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
                elif addr.family == -1:
                    result[interface]["mac"] = addr.address

    strings: list[str] = list()
    for interface, item in result.items():
        strings.append(f"网卡：{interface}")
        strings.append(f"\t状态：{"已连接" if item["status"] else "未连接"}")
        strings.append(f"\t速度：{item["speed"]} Mbps")
        strings.append(f"\tMTU：{item["mtu"]}")
        if item["ipv4"]:
            strings.append(f"\tIPV4：")
            for ipv4 in item["ipv4"]:
                strings.append(f"\t\t地址：{ipv4["address"]}")
                strings.append(f"\t\t子网掩码：{ipv4["netmask"]}")
                strings.append(f"\t\t广播：{ipv4["broadcast"]}")
        if item["ipv6"]:
            strings.append(f"\tIPV6：")
            for ipv6 in item["ipv6"]:
                strings.append(f"\t\t地址：{ipv6["address"]}")
                if ipv6["netmask"]:
                    strings.append(f"\t\t子网掩码：{ipv6["netmask"]}")
        if item["mac"]:
            strings.append(f"\tMAC：{item["mac"]}")
    return strings

def write_eula():
	try:
		with open("eula.txt", mode="w", encoding="utf-8") as f:
			f.write("#INF.\neula=true")
	except:
		pass