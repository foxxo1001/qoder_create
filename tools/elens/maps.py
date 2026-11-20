"""通用 map 符号提取：Keil armlink map 与 GNU ld map。FR-1 含丢弃段启动检测。"""
import re
from pathlib import Path

def parse_keil_map(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    sym_re = re.compile(
        r"^\s{4}(\S+)\s+0x([0-9a-fA-F]{8})\s+(Data|Number|Section|Thumb Code|ARM Code)\s+(\d+)\s+(\S.*)$")
    symbols = {}
    for line in text.splitlines():
        m = sym_re.match(line)
        if not m:
            continue
        name, addr, kind, size, obj = m.groups()
        if kind in ("Data", "Number") and not name.startswith("[Anonymous"):
            symbols.setdefault(name, {"addr": "0x" + addr.lower(), "size": int(size),
                                      "kind": kind, "object": obj.strip()})
    removed, in_removed = set(), False
    for line in text.splitlines():
        if "Removing Unused input sections" in line or "Discarded input sections" in line:
            in_removed = True
            continue
        if in_removed:
            m = re.match(r"^\s+(\S+\.o\(\S+\))", line)
            if m:
                removed.add(m.group(1))
            elif line.strip() and not line.startswith(" "):
                in_removed = False
    return {"format": "keil", "symbols": symbols, "removed_sections": sorted(removed)}

def parse_gnu_map(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    symbols = {}
    # GNU ld map: 地址行后跟符号名，或 .bss/.data 段内 "0xADDR  name"
    cur_sec = None
    for line in text.splitlines():
        sm = re.match(r"^(\.\w[\w.]*)\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)", line)
        if sm:
            cur_sec = sm.group(1)
        m = re.match(r"^\s+0x([0-9a-fA-F]{8,16})\s+(\S+)", line)
        if m and cur_sec in (".bss", ".data", ".noinit"):
            addr, name = m.groups()
            if not name.startswith("."):
                symbols.setdefault(name, {"addr": "0x" + addr.lower(), "size": None,
                                          "kind": "Data", "object": cur_sec})
    return {"format": "gnu", "symbols": symbols, "removed_sections": []}

def parse_map(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if "ARM Linker" in text or "Image Symbol Table" in text:
        return parse_keil_map(path)
    return parse_gnu_map(path)

def check_rtos_linked(symbols, removed, required):
    missing = [s for s in required if s not in symbols]
    discarded = [s for s in required if s in symbols and symbols[s].get("object") in removed]
    if missing:
        return False, f"符号缺失: {', '.join(missing)} —— 该固件可能未链接 RTOS 内核，无法读取内核状态"
    if discarded:
        return False, f"符号落入被丢弃的输入段: {', '.join(discarded)} —— 该固件未链接 RTOS 内核"
    return True, None