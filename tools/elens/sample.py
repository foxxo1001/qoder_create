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

class _StageError(Exception):
    def __init__(self, stage, code, message):
        super().__init__(message)
        self.stage, self.code = stage, code

def _launch(profile, out_dir, openocd, scripts_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    log = out_dir / "openocd.log"
    args = [str(openocd), "-s", str(scripts_dir),
            "-f", profile["interface_cfg"], "-f", profile["target_cfg"],
            "-c", "tcl_port 6666", "-c", "init"]
    proc = None
    try:
        with log.open("w") as log_stream:
            try:
                proc = subprocess.Popen(args, stdout=log_stream, stderr=subprocess.STDOUT)
            except FileNotFoundError as e:
                raise _StageError("tool", "tool_not_found", str(e))
            except Exception as e:
                raise _StageError("tool", "tool_start_failed", str(e))
        connect_error = None
        for _ in range(40):
            if proc.poll() is not None:
                raise _StageError("connect", "openocd_exited",
                                  "OpenOCD 退出：" + log.read_text(errors="replace")[-400:])
            try:
                return proc, TclRPC()
            except OSError as e:
                connect_error = e
                time.sleep(0.2)
        raise _StageError("connect", "tcl_connect_failed",
                          "无法连接 OpenOCD TCL 端口: " + str(connect_error))
    except Exception:
        if proc is not None and proc.poll() is None:
            proc.terminate()
        raise

def _capture_frame(rpc, profile, pack, files, odr_offset=0x0C):
    """halt-read-resume 一帧；读失败仍尝试恢复自己暂停的目标。"""
    flash_bin, ram_bin, gpio_bin = files
    halt_resp = resume_resp = ""
    resume_ok = None  # 尚未尝试恢复；不能当作已成功或已失败的响应。
    notes = []
    stage, code = "halt", "unknown"
    try:
        halt_resp = rpc.cmd("halt")
        t0 = time.monotonic()
        try:
            if not _cmd_ok(halt_resp):
                code = "halt_failed"
                raise RuntimeError("halt 失败: " + halt_resp)
            stage, code = "read", "unknown"
            for path, base, size in (
                (flash_bin, profile["flash_base"], pack["flash_image"]["size"]),
                (ram_bin, profile["ram_base"], profile["ram_dump_size"]),
                (gpio_bin, profile["gpio_base"], profile["gpio_dump_size"]),
            ):
                read_resp = rpc.cmd(f"dump_image {path.as_posix()} {hex(base)} {size}")
                if not _cmd_ok(read_resp):
                    code = "read_failed"
                    raise RuntimeError("dump_image 失败: " + read_resp)
        except Exception as e:
            notes.append(str(e))  # 恢复也失败时仍保留先前的 halt/read 原因。
            raise
        finally:
            prior_stage, prior_code = stage, code
            stage, code = "resume", "unknown"
            resume_ok = False
            resume_resp = rpc.cmd("resume")   # 读失败仍恢复自己暂停的目标
            t1 = time.monotonic()
            resume_ok = _cmd_ok(resume_resp)
            if not resume_ok:
                code = "resume_failed"
                raise RuntimeError("恢复目标失败（resume 响应异常）: " + resume_resp)
            stage, code = prior_stage, prior_code
        return {"ok": True, "pause_ms": round((t1 - t0) * 1000, 2),
                "halt_resp": halt_resp, "resume_resp": resume_resp, "resume_ok": resume_ok,
                "error": None, "stage": stage, "code": code, "notes": notes}
    except Exception as e:
        if str(e) not in notes:
            notes.append(str(e))
        return {"ok": False, "pause_ms": None,
                "halt_resp": halt_resp, "resume_resp": resume_resp, "resume_ok": resume_ok,
                "error": e, "stage": stage, "code": code, "notes": notes}

def _failed_snapshot(stage, code, error, session, halt_resp="", resume_resp="",
                     resume_ok=None, notes=None, identity=None):
    notes = list(notes or [])
    if str(error) not in notes:
        notes.append(str(error))
    return {"id": "sample-" + str(int(time.time())), "host_time": _now(), "source": "openocd",
            "status": "probe_failed",
            "identity": identity or {"status": "unverified", "reason": str(error)},
            "diagnostic": {"stage": stage, "code": code, "message": str(error)},
            "halt_resp": halt_resp, "resume_resp": resume_resp, "resume_ok": resume_ok,
            "valid": False, "decoded": None, "raw_scalars": {}, "notes": notes,
            "session": session}

def _frame_files(out_dir, index, frames):
    d = out_dir if frames == 1 else out_dir / f"frame_{index + 1:02d}"
    d.mkdir(parents=True, exist_ok=True)
    return d / "board_flash.bin", d / "board_ram.bin", d / "board_gpio.bin"

def _finish_frame(profile, pack, symbols, offsets, adapter, files, cap, session, odr_offset):
    if not cap["ok"]:
        return _failed_snapshot(cap["stage"], cap["code"], cap["error"], session,
                                cap["halt_resp"], cap["resume_resp"], cap["resume_ok"], cap["notes"])
    flash_bin, ram_bin, gpio_bin = files
    identity = None
    try:
        board_flash = flash_bin.read_bytes() if flash_bin.exists() else None
        pack_flash = {"base": pack["flash_image"]["base"], "size": pack["flash_image"]["size"],
                      "bytes": Path(pack["flash_image"]["file"]).read_bytes()}
        identity = model.verify_identity(board_flash, pack_flash)
    except Exception as e:
        return _failed_snapshot("identity", "unknown", e, session,
                                cap["halt_resp"], cap["resume_resp"], cap["resume_ok"], cap["notes"])
    try:
        ram = ram_bin.read_bytes() if ram_bin.exists() else b""
        gpio = gpio_bin.read_bytes() if gpio_bin.exists() else b""
    except Exception as e:
        return _failed_snapshot("read", "unknown", e, session,
                                cap["halt_resp"], cap["resume_resp"], cap["resume_ok"],
                                cap["notes"], identity)
    try:
        snap = _build_snapshot(profile, pack, symbols, offsets, adapter, ram, gpio,
                               identity, cap["pause_ms"], "openocd", cap["halt_resp"], cap["resume_resp"],
                               resume_ok=cap["resume_ok"], odr_offset=odr_offset)
    except Exception as e:
        return _failed_snapshot("structure", "unknown", e, session,
                                cap["halt_resp"], cap["resume_resp"], cap["resume_ok"],
                                cap["notes"], identity)
    snap["ram_dump_file"] = str(ram_bin)
    snap["session"] = session
    return snap

def sample_session(profile, pack, symbols, offsets, adapter, out_dir, openocd, scripts_dir,
                   odr_offset=0x0C, frames=1, interval_s=0.0):
    """一次 OpenOCD 会话内连续 halt-read-resume 多帧；帧间目标保持运行。
    只有结构校验失败（可能撕裂）继续下一帧；其余失败记录后停止，避免连环无效帧。"""
    frames = max(1, int(frames))
    interval_s = max(0.0, float(interval_s))
    out_dir = Path(out_dir)
    base_meta = {"id": "sess-" + str(int(time.time() * 1000)), "started_at": _now(),
                 "frame_count": frames, "interval_s": interval_s}
    proc = rpc = None
    shots = []
    try:
        proc, rpc = _launch(profile, out_dir, openocd, scripts_dir)
        last_ok = False
        for i in range(frames):
            if i:
                time.sleep(interval_s)   # 采样间隔由主机控制，目标在帧间保持运行
            files = _frame_files(out_dir, i, frames)
            cap = _capture_frame(rpc, profile, pack, files, odr_offset)
            snap = _finish_frame(profile, pack, symbols, offsets, adapter, files, cap,
                                 {**base_meta, "frame_index": i}, odr_offset)
            shots.append(snap)
            last_ok = cap["ok"]
            if not cap["ok"]:
                break
            if snap.get("status") != "ok" or \
               snap.get("diagnostic", {}).get("code") not in ("ok", "structure_invalid"):
                break
        if rpc is not None and last_ok:
            try:
                rpc.cmd("shutdown")
            except Exception as e:
                shots[-1].setdefault("notes", []).append("关闭 OpenOCD 会话失败: " + str(e))
        return shots
    except _StageError as e:
        return [_failed_snapshot(e.stage, e.code, e, {**base_meta, "frame_index": 0})]
    except Exception as e:
        if shots:
            shots.append(_failed_snapshot("tool", "unknown", e,
                                          {**base_meta, "frame_index": len(shots)}))
            return shots
        return [_failed_snapshot("tool", "unknown", e, {**base_meta, "frame_index": 0})]
    finally:
        if rpc: rpc.close()
        if proc is not None and proc.poll() is None:
            proc.terminate()

def sample_board(profile, pack, symbols, offsets, adapter, out_dir, openocd, scripts_dir, odr_offset=0x0C):
    return sample_session(profile, pack, symbols, offsets, adapter, out_dir, openocd, scripts_dir,
                          odr_offset=odr_offset, frames=1, interval_s=0.0)[0]

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
    diagnostic = {"stage": "complete", "code": "ok", "message": ""}
    if not resume_ok:
        notes.append("恢复目标失败（resume 响应异常）: " + (resume_resp or ""))
        diagnostic = {"stage": "resume", "code": "resume_failed", "message": resume_resp or ""}
    if identity["status"] != "verified":
        notes.append("固件身份未通过核验 → 停止解释 RTOS 对象，仅展示原始读数 (§6.3)")
        if resume_ok:
            code = {"mismatch": "identity_mismatch", "unverified": "identity_unverified"}.get(identity["status"], "unknown")
            diagnostic = {"stage": "identity", "code": code, "message": identity.get("reason", "")}
    elif reader is None:
        notes.append("无 RAM 数据")
        if resume_ok:
            diagnostic = {"stage": "read", "code": "ram_missing", "message": notes[-1]}
    elif resume_ok:
        dev = {"sampled_at": host_time, "ram_base": profile["ram_base"]}
        decoded = adapter.decode(reader, symbols, offsets, dev)
        valid = decoded.get("valid", False)
        if not valid:
            notes.append("结构校验失败帧标为不可用 (FR-4/FR-5)")
            diagnostic = {"stage": "structure", "code": "structure_invalid", "message": notes[-1]}
    return {"id": "snap-" + str(int(time.time() * 1000)), "host_time": host_time,
            "pause_ms": pause_ms, "source": source, "status": "ok" if resume_ok else "probe_failed",
            "identity": identity, "halt_resp": halt_resp, "resume_resp": resume_resp,
            "resume_ok": resume_ok, "diagnostic": diagnostic,
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