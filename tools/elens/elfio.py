"""通用 ELF/DWARF 读取（任意 Cortex-M 工具链：Keil AXF / GCC elf）。
Flash 加载镜像提取 + 从构建自身 DWARF 核定结构偏移（不硬编码版本偏移, FR-3）。"""
import re, struct, subprocess
from pathlib import Path

PT_LOAD = 1

def read_elf(path):
    data = Path(path).read_bytes()
    if data[:4] != b"\x7fELF":
        raise ValueError(f"不是 ELF: {path}")
    ei_class, ei_data = data[4], data[5]
    if ei_class != 1 or ei_data != 1:
        raise ValueError("MVP 仅支持 32 位小端 ELF (Cortex-M)")
    e_machine, = struct.unpack_from("<H", data, 18)
    e_phoff, = struct.unpack_from("<I", data, 28)
    e_phentsize, e_phnum = struct.unpack_from("<HH", data, 42)
    segs = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = \
            struct.unpack_from("<8I", data, off)
        segs.append({"type": p_type, "offset": p_offset, "vaddr": p_vaddr,
                     "paddr": p_paddr, "filesz": p_filesz, "memsz": p_memsz, "flags": p_flags})
    return {"machine": e_machine, "segments": segs, "data": data}

def flash_image(path, flash_base, flash_size):
    """提取落在 Flash 区域的 PT_LOAD 段，拼成加载镜像（用于 §6.3 身份比对）。"""
    elf = read_elf(path)
    lo, hi = flash_base, flash_base + flash_size
    segs = [(s["paddr"], elf["data"][s["offset"]:s["offset"] + s["filesz"]])
            for s in elf["segments"]
            if s["type"] == PT_LOAD and lo <= s["paddr"] < hi and s["filesz"] > 0]
    if not segs:
        raise ValueError(f"无 Flash 加载段（flash_base={hex(flash_base)}）")
    segs.sort()
    base = segs[0][0]
    end = max(a + len(b) for a, b in segs)
    img = bytearray(end - base)
    for a, b in segs:
        img[a - base:a - base + len(b)] = b
    return base, bytes(img)

def dwarf_offsets(path, types, gdb):
    """FR-3：gdb ptype /o 从 DWARF 离线核定偏移，仅读构建产物。"""
    cmds = []
    for t in types:
        cmds += ["-ex", f"ptype /o {t}"]
    proc = subprocess.run([str(gdb), "-batch", *cmds, str(path)],
                          capture_output=True, text=True, timeout=180)
    out = proc.stdout
    field_re = re.compile(r"/\*\s*(\d+)\s*\|\s*(\d+)\s*\*/\s*([^;]+);")
    size_re = re.compile(r"total size \(bytes\):\s*(\d+)")
    result, idx = {}, 0
    for block in re.split(r"type = ", out)[1:]:
        if idx >= len(types):
            break
        fields = {}
        for off, sz, decl in field_re.findall(block):
            fname = decl.split()[-1].lstrip("*")
            fname = re.sub(r"\[\d+\]$", "", fname)
            fields[fname] = {"offset": int(off), "size": int(sz)}
        sm = size_re.search(block)
        result[types[idx]] = {"size": int(sm.group(1)) if sm else None, "fields": fields}
        idx += 1
    return result, out