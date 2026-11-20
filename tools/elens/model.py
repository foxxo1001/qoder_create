"""数据诚实契约 (§6)：四态值模型 + 溯源 + 固件包绑定 + 快照结构校验。"""
import hashlib, datetime
from pathlib import Path

MEASURED = "measured"        # 实测值：SWD 从板上读到
AUTHORITATIVE = "authoritative"  # 权威定义：SVD / 设备头 / DWARF
DERIVED = "derived"          # 推导值：实测 + 定义计算
UNKNOWN = "unknown"          # 不可知：无法从证据得出

STATE_LABEL = {MEASURED: "实测值", AUTHORITATIVE: "权威定义", DERIVED: "推导值", UNKNOWN: "不可知"}

def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def value(state, val, **prov):
    """每个显示的数字必须归入四态之一并附带溯源。"""
    return {"state": state, "value": val, "prov": prov}

def measured(val, addr, hexraw, sampled_at, source="openocd"):
    return value(MEASURED, val, addr=addr, hex=hexraw, sampled_at=sampled_at, source=source)

def authoritative(val, file, version=None, line=None):
    return value(AUTHORITATIVE, val, file=file, version=version, line=line)

def derived(val, formula, inputs):
    return value(DERIVED, val, formula=formula, inputs=inputs)

def unknown(reason):
    return value(UNKNOWN, None, reason=reason)

# ---- 固件包 (§6.3)：板上 Flash 身份 + 同次构建 AXF + map + 核定偏移，绑定一体 ----
def bind_pack(axf, mapfile, flash_base, flash_bytes, offsets_ref, symbols_ref):
    return {
        "bound_at": now(),
        "axf": {"path": str(axf), "sha256": sha256_file(axf)},
        "map": {"path": str(mapfile), "sha256": sha256_file(mapfile)},
        "flash_image": {"base": hex(flash_base), "size": len(flash_bytes),
                        "sha256": sha256_bytes(flash_bytes)},
        "offsets_ref": offsets_ref, "symbols_ref": symbols_ref,
        "note": "固件包绑定为一体；采样前须与板上 Flash 比对 (§6.3)",
    }

def verify_identity(board_flash, pack_flash):
    """比对板上 Flash 与固件包 Flash。返回 identity 记录。"""
    bf, pf = board_flash, pack_flash
    if bf is None:
        return {"status": "unverified", "reason": "未取得板上 Flash，无法核验固件身份",
                "range": None}
    base = pf["base"]
    n = min(len(bf), pf["size"])
    mism = [i for i in range(n) if bf[i] != pf["bytes"][i]]
    if len(bf) != pf["size"]:
        return {"status": "mismatch", "reason": f"长度不一致 板上{len(bf)}B vs 构建{pf['size']}B",
                "range": f"{base}+{n}", "mismatch_count": len(mism)}
    if mism:
        return {"status": "mismatch", "reason": f"{len(mism)} 字节不匹配（首个偏移 {mism[0]}）",
                "range": f"{base}+{n}", "mismatch_count": len(mism),
                "first_mismatch_offset": mism[0]}
    return {"status": "verified", "reason": "板上 Flash 与同次构建完全一致",
            "range": f"{base}+{n}", "mismatch_count": 0}

# ---- 快照结构校验 (FR-4/FR-5)：地址范围、哨兵、节点数上限 ----
def in_ram(addr, ram_base, ram_size):
    return ram_base <= addr < ram_base + ram_size

def validate_list_walk(nodes, ram_base, ram_size, cap, sentinel_ok):
    checks = []
    checks.append({"check": "node_count_cap", "ok": len(nodes) <= cap,
                   "detail": f"{len(nodes)} <= {cap}"})
    checks.append({"check": "addresses_in_ram", "ok": all(in_ram(n, ram_base, ram_size) for n in nodes),
                   "detail": "所有节点地址落在 RAM 范围"})
    checks.append({"check": "sentinel", "ok": sentinel_ok, "detail": "链表尾哨兵 xItemValue 校验"})
    ok = all(c["ok"] for c in checks)
    return ok, checks