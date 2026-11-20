"""通用 CMSIS-SVD 解析（厂商无关）：derivedFrom / cluster / 位域。
MVP 按需解析所选外设寄存器，不整片展开。"""
import xml.etree.ElementTree as ET
from pathlib import Path

def _txt(el, tag, default=""):
    c = el.find(tag)
    return c.text.strip() if c is not None and c.text else default

def list_peripherals(svd_path):
    root = ET.parse(svd_path).getroot()
    out = []
    for p in root.findall("./peripherals/peripheral"):
        out.append({"name": _txt(p, "name"), "base": _txt(p, "baseAddress"),
                    "derivedFrom": p.get("derivedFrom"),
                    "description": _txt(p, "description")})
    return out

def parse_register(svd_path, peripheral, register):
    root = ET.parse(svd_path).getroot()
    peripherals = {_txt(p, "name"): p for p in root.findall("./peripherals/peripheral")}
    if peripheral not in peripherals:
        raise ValueError(f"SVD 无外设 {peripheral}")

    def resolve(p, seen=None):
        seen = seen or set()
        name = _txt(p, "name")
        if name in seen:
            raise ValueError(f"derivedFrom 循环: {name}")
        seen.add(name)
        df = p.get("derivedFrom")
        regs = {}
        if df:
            regs.update(resolve(peripherals[df], seen)["registers"])
        for r in p.findall("./registers/register"):
            fields = []
            for f in r.findall("./fields/field"):
                fields.append({"name": _txt(f, "name"),
                               "bit_offset": int(_txt(f, "bitOffset", "0")),
                               "bit_width": int(_txt(f, "bitWidth", "1")),
                               "description": _txt(f, "description"),
                               "access": _txt(f, "access", _txt(r, "access", ""))})
            regs[_txt(r, "name")] = {
                "name": _txt(r, "name"), "offset": int(_txt(r, "addressOffset", "0"), 0),
                "size_bits": int(_txt(r, "size", "32"), 0),
                "description": _txt(r, "description"), "fields": fields, "defined_in": name}
        for cl in p.findall("./registers/cluster"):
            cn, coff = _txt(cl, "name"), int(_txt(cl, "addressOffset", "0"), 0)
            for r in cl.findall("./register"):
                rn = f"{cn}.{_txt(r, 'name')}"
                cfields = [{"name": _txt(f, "name"), "bit_offset": int(_txt(f, "bitOffset", "0")),
                            "bit_width": int(_txt(f, "bitWidth", "1")), "description": _txt(f, "description"),
                            "access": _txt(f, "access", _txt(r, "access", ""))}
                           for f in r.findall("./fields/field")]
                regs[rn] = {"name": rn, "offset": coff + int(_txt(r, "addressOffset", "0"), 0),
                            "size_bits": int(_txt(r, "size", "32"), 0),
                            "description": _txt(r, "description"), "fields": cfields,
                            "defined_in": name, "cluster": cn}
        return {"name": name, "base": int(_txt(p, "baseAddress", "0"), 0), "registers": regs}

    per = resolve(peripherals[peripheral])
    if register not in per["registers"]:
        raise ValueError(f"{peripheral} 无寄存器 {register}")
    reg = per["registers"][register]
    return {
        "svd": {"file": str(svd_path), "version": _txt(root, "version", "?")},
        "peripheral": {"name": peripheral, "base_address": hex(per["base"]),
                       "derivedFrom": peripherals[peripheral].get("derivedFrom")},
        "register": {"name": register, "address": hex(per["base"] + reg["offset"]),
                     "offset": reg["offset"], "size_bits": reg["size_bits"],
                     "description": reg["description"], "defined_in": reg["defined_in"],
                     "fields": sorted(reg["fields"], key=lambda f: f["bit_offset"])},
    }

def parse_gpio_typedef(header_path):
    """从设备头提取 GPIO_TypeDef 布局与 GPIOx_BASE（权威定义, 与 SVD 交叉校验）。"""
    import re
    text = Path(header_path).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"typedef struct\s*\{([^{}]*)\}\s*GPIO_TypeDef;", text, re.S)
    fields, off = [], 0
    if m:
        for line in m.group(1).splitlines():
            fm = re.search(r"__IO\s+uint(\d+)_t\s+(\w+)\s*(\[(\d+)\])?\s*;", line)
            if fm:
                bits, name, _, arr = fm.groups()
                sz = int(bits) // 8 * (int(arr) if arr else 1)
                fields.append({"name": name, "offset": off, "size": sz})
                off += sz
    macros = {}
    for bm in re.finditer(r"#define\s+(\w+)\s+([^\n]+)", text):
        val = re.sub(r"/\*.*?\*/", "", bm.group(2)).split("//")[0].strip()
        macros[bm.group(1)] = val

    def resolve(name, seen=None):
        seen = seen or set()
        if name in seen or name not in macros:
            return None
        seen.add(name)
        total = 0
        for tok in macros[name].split("+"):
            tok = re.sub(r"[UL]+$", "", tok.strip().strip("()").strip())
            if re.fullmatch(r"0x[0-9a-fA-F]+", tok):
                total += int(tok, 16)
            elif re.fullmatch(r"\d+", tok):
                total += int(tok)
            elif tok in macros:
                r = resolve(tok, seen)
                if r is None:
                    return None
                total += r
            else:
                return None
        return total

    bases = {}
    for name in macros:
        if re.fullmatch(r"GPIO[A-Z]_BASE", name):
            v = resolve(name)
            if v is not None:
                bases[name] = hex(v)
    return {"header": {"file": str(header_path)},
            "GPIO_TypeDef": {"fields": fields, "size": off}, "gpio_bases": bases}