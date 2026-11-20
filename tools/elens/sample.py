"""FR-4 采样器：OpenOCD halt-read-resume（主机单调时钟测暂停）+ §6.3 Flash 身份核验。
读失败仍尝试恢复自己暂停的目标；无探针/无板时诚实返回失败，不编造。另含 Keil 手工采集导入。"""
import json, socket, subprocess, time, datetime
from pathlib import Path
from . import model, elfio
from .rtos import RamReader

F103_PROFILE = {
    "device": "STM32F103RCT6", "core": "Cortex-M3",
    "target_cfg": "target/stm32f1x.cfg", "interface_cfg": "interface/stlink.cfg",
    "flash_base": 0x08000000, "flash_size": 0x40000,
    "ram_base": 0x20000000, "ram_dump_size": 0x1800,
    "gpio_base": 0x40011000, "gpio_dump_size": 0x20,
}

def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")

def _cmd_ok(resp):
    r = (resp or "").lower()
    return not any(k in r for k in ("error", "failed", "invalid", "unknown command"))

class TclRPC:
    def __init__(self, port=6666, timeout=8):
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        self.sock.settimeout(timeout)
    def cmd(self, c):
        self.sock.sendall(c.encode() + b"\x1a")
        buf = b""
        while not buf.endswith(b"\x1a"):
            chunk = self.sock.recv(65536)
            if not chunk:
                break
            buf += chunk
        return buf[:-1].decode(errors="replace").strip()
    def close(self):
        try: self.sock.close()
        except OSError: pass

def sample_board(profile, pack, symbols, offsets, adapter, out_dir, openocd, scripts_dir, odr_offset=0x0C):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    flash_bin = out_dir / "board_flash.bin"
    ram_bin = out_dir / "board_ram.bin"
    gpio_bin = out_dir / "board_gpio.bin"
    log = out_dir / "openocd.log"
    args = [str(openocd), "-s", str(scripts_dir),
            "-f", profile["interface_cfg"], "-f", profile["target_cfg"],
            "-c", "tcl_port 6666", "-c", "init"]
    proc = subprocess.Popen(args, stdout=log.open("w"), stderr=subprocess.STDOUT)
    rpc = None
    try:
        for _ in range(40):
            if proc.poll() is not None:
                raise ConnectionError("OpenOCD 退出（探针未连接/被独占/供电异常）：" + log.read_text(errors="replace")[-400:])
            try:
                rpc = TclRPC(); break
            except OSError:
                time.sleep(0.2)
        if rpc is None:
            raise ConnectionError("无法连接 OpenOCD TCL 端口")
        halt_resp = rpc.cmd("halt")
        t0 = time.monotonic()
        try:
            if not _cmd_ok(halt_resp):
                raise RuntimeError("halt 失败: " + halt_resp)
            rpc.cmd(f"dump_image {flash_bin.as_posix()} {hex(profile['flash_base'])} {pack['flash_image']['size']}")
            rpc.cmd(f"dump_image {ram_bin.as_posix()} {hex(profile['ram_base'])} {profile['ram_dump_size']}")
            rpc.cmd(f"dump_image {gpio_bin.as_posix()} {hex(profile['gpio_base'])} {profile['gpio_dump_size']}")
        finally:
            resume_resp = rpc.cmd("resume")   # 读失败仍恢复自己暂停的目标
            t1 = time.monotonic()
        resume_ok = _cmd_ok(resume_resp)
        pause_ms = round((t1 - t0) * 1000, 2)
        rpc.cmd("shutdown")
        board_flash = flash_bin.read_bytes() if flash_bin.exists() else None
        pack_flash = {"base": pack["flash_image"]["base"], "size": pack["flash_image"]["size"],
                      "bytes": Path(pack["flash_image"]["file"]).read_bytes()}
        identity = model.verify_identity(board_flash, pack_flash)
        ram = ram_bin.read_bytes() if ram_bin.exists() else b""
        gpio = gpio_bin.read_bytes() if gpio_bin.exists() else b""
        snap = _build_snapshot(profile, pack, symbols, offsets, adapter, ram, gpio,
                               identity, pause_ms, "openocd", halt_resp, resume_resp,
                               resume_ok=resume_ok, odr_offset=odr_offset)
        snap["ram_dump_file"] = str(ram_bin)
        return snap
    except Exception as e:
        return {"id": "sample-" + str(int(time.time())), "host_time": _now(), "source": "openocd",
                "status": "probe_failed", "identity": {"status": "unverified", "reason": str(e)},
                "valid": False, "decoded": None, "raw_scalars": {}, "notes": [str(e)]}
    finally:
        if rpc: rpc.close()
        if proc.poll() is None:
            proc.terminate()

def _build_snapshot(profile, pack, symbols, offsets, adapter, ram, gpio, identity,
                    pause_ms, source, halt_resp="", resume_resp="", resume_ok=True, odr_offset=0x0C):
    host_time = _now()
    S = {k: int(v["addr"], 16) for k, v in symbols.items()}
    reader = RamReader(ram, profile["ram_base"]) if ram else None
    raw = {}
    if reader:
        for key in ["xTickCount", "xSchedulerRunning", "xNextTaskUnblockTime", "pxCurrentTCB"]:
            if key in S and reader.has(S[key]):
                raw[key] = model.measured(reader.u32(S[key]), hex(S[key]), reader.raw_hex(S[key]), host_time, source)
    odr_addr = profile["gpio_base"] + odr_offset
    gpio_odr = (model.measured(int.from_bytes(gpio[odr_offset:odr_offset + 4], "little"), hex(odr_addr),
                               "0x" + gpio[odr_offset:odr_offset + 4][::-1].hex(), host_time, source)
                if len(gpio) >= odr_offset + 4 else model.unknown("未采集到 GPIOC 寄存器"))
    decoded, valid, notes = None, False, []
    if not resume_ok:
        notes.append("恢复目标失败（resume 响应异常）: " + (resume_resp or "")[:200])
    if identity["status"] != "verified":
        notes.append("固件身份未通过核验 → 停止解释 RTOS 对象，仅展示原始读数 (§6.3)")
    elif reader is None:
        notes.append("无 RAM 数据")
    else:
        dev = {"sampled_at": host_time, "ram_base": profile["ram_base"]}
        decoded = adapter.decode(reader, symbols, offsets, dev)
        valid = decoded.get("valid", False)
        if not valid:
            notes.append("结构校验失败帧标为不可用 (FR-4/FR-5)")
    return {"id": "snap-" + str(int(time.time() * 1000)), "host_time": host_time,
            "pause_ms": pause_ms, "source": source, "status": "ok",
            "identity": identity, "halt_resp": halt_resp, "resume_resp": resume_resp,
            "ram_dump": {"base": hex(profile["ram_base"]), "size": len(ram),
                         "sha256": model.sha256_bytes(ram)} if ram else None,
            "raw_scalars": raw, "gpio_odr": gpio_odr, "decoded": decoded,
            "valid": valid, "notes": notes}

def import_manual(json_path, profile, pack, symbols, offsets, adapter, odr_offset=0x0C):
    """PRD D1 兜底：Keil µVision Memory 窗口手工采集，标明来源。"""
    doc = json.loads(Path(json_path).read_text(encoding="utf-8"))
    ram = bytes.fromhex(doc["ram_hex"]) if doc.get("ram_hex") else b""
    gpio = bytes.fromhex(doc["gpio_hex"]) if doc.get("gpio_hex") else b""
    if doc.get("flash_hex"):
        pf = {"base": pack["flash_image"]["base"], "size": pack["flash_image"]["size"],
              "bytes": Path(pack["flash_image"]["file"]).read_bytes()}
        identity = model.verify_identity(bytes.fromhex(doc["flash_hex"]), pf)
    else:
        identity = {"status": "unverified", "reason": "手工采集未提供 Flash 比对数据，固件身份未核验"}
    snap = _build_snapshot(profile, pack, symbols, offsets, adapter, ram, gpio, identity,
                           doc.get("pause_ms"), "keil-manual", odr_offset=odr_offset)
    snap["host_time"] = doc.get("host_time", snap["host_time"])
    snap["manual_note"] = "Keil 手工采集 · 来源 µVision Memory 窗口"
    return snap