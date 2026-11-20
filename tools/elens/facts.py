"""通用工程事实提取：config / 任务创建 / 延时调用 / GPIO 写 / 引脚映射，全部带文件+行号。
模式由 profile 提供，换工程/换 RTOS 换模式，不写死任务名。"""
import re
from pathlib import Path

FREERTOS_STM32_PATTERNS = {
    "config_file": "FreeRTOSConfig.h",
    "config_re": r"\s*#define\s+(config\w+)\s+(.+?)\s*$",
    "create_re": r'xTaskCreate(?:Static)?\(\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\w+)\s*,\s*(\d+)',
    "delay_re": r"vTaskDelay(?:Until)?\(\s*(\d+)\s*\)",
    "gpio_re": r"HAL_GPIO_WritePin\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\)",
    "pin_re": r"#define\s+(\w+)_(Pin|GPIO_Port)\s+(\S+)",
    "fn_re": r"void\s+(\w+)\s*\(\s*void\s*\*",
}

def _lines(p):
    return Path(p).read_text(encoding="utf-8", errors="replace").splitlines()

def _config_int(s):
    bare = re.sub(r"[uUlL]+$", "", s.strip())
    try:
        return int(bare, 0)
    except ValueError:
        pass
    cm = re.fullmatch(r"\(\s*(?:\(\s*[\w\s]+?\s*\)\s*)?(\d+[uUlL]*)\s*\)", s.strip())
    if cm:
        return int(re.sub(r"[uUlL]+$", "", cm.group(1)), 0)
    return None

def extract_facts(source_dir, patterns=None, config_path=None, main_c=None, main_h=None):
    pat = patterns or FREERTOS_STM32_PATTERNS
    source_dir = Path(source_dir)
    config_path = Path(config_path) if config_path else source_dir / "Core/Inc" / pat["config_file"]
    main_c = Path(main_c) if main_c else source_dir / "Core/Src/main.c"
    main_h = Path(main_h) if main_h else source_dir / "Core/Inc/main.h"
    config = {}
    if config_path.exists():
        for i, ln in enumerate(_lines(config_path), 1):
            m = re.match(pat["config_re"], ln)
            if m and not ln.strip().startswith("*"):
                name, val = m.groups()
                clean = re.sub(r"/\*.*?\*/", "", val).split("//")[0].strip()
                v = _config_int(clean)
                if v is None:
                    continue  # 表达式/符号宏不作为数值事实，避免垃圾值
                config[name] = {"value": v, "file": str(config_path), "line": i}
    tasks, delays, writes, cur_fn = [], [], [], None
    if main_c.exists():
        for i, ln in enumerate(_lines(main_c), 1):
            fm = re.match(pat["fn_re"], ln)
            if fm: cur_fn = fm.group(1)
            tm = re.search(pat["create_re"], ln)
            if tm:
                fn, name, stack, param, prio = tm.groups()
                tasks.append({"name": name, "entry": fn, "stack_words": int(stack),
                              "priority": int(prio), "file": str(main_c), "line": i})
            dm = re.search(pat["delay_re"], ln)
            if dm:
                delays.append({"ticks": int(dm.group(1)), "file": str(main_c), "line": i, "in_fn": cur_fn})
            wm = re.search(pat["gpio_re"], ln)
            if wm:
                writes.append({"port_macro": wm.group(1), "pin_macro": wm.group(2),
                               "state": wm.group(3), "file": str(main_c), "line": i, "in_fn": cur_fn})
    pins = {}
    if main_h.exists():
        for i, ln in enumerate(_lines(main_h), 1):
            m = re.match(pat["pin_re"], ln)
            if m:
                led, kind, val = m.groups()
                pins.setdefault(led, {"file": str(main_h)})[kind] = {"macro": val, "line": i}
        for p in pins.values():
            if "Pin" in p:
                pm = re.search(r"GPIO_PIN_(\d+)", p["Pin"]["macro"])
                p["bit"] = int(pm.group(1)) if pm else None
            if "GPIO_Port" in p:
                p["port"] = p["GPIO_Port"]["macro"]
            p["confirmed_from_source"] = "Pin" in p and "GPIO_Port" in p
    return {"config": config, "tasks": tasks, "delay_calls": delays,
            "gpio_writes": writes, "pins": pins}

def hal_pin_states(hal_gpio_header):
    out = {}
    p = Path(hal_gpio_header)
    if not p.exists():
        return out
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"typedef\s+enum\s*\{([^{}]*)\}\s*GPIO_PinState\s*;", text, re.S)
    if not m:
        return out
    start_line = text[:m.start(1)].count("\n") + 1
    last = None
    for j, raw in enumerate(m.group(1).splitlines()):
        ln = re.sub(r"/\*.*?\*/", "", raw).split("//")[0]
        for em in re.finditer(r"\b(GPIO_PIN_RESET|GPIO_PIN_SET)\b\s*(?:=\s*(\d+)[uUlL]*)?", ln):
            name, explicit = em.groups()
            v = int(explicit) if explicit is not None else ((last + 1) if last is not None else 0)
            last = v
            out[name] = {"value": v, "file": str(p), "line": start_line + j}
    return out