"""EmbeddedLens CLI：import / sample / export / build。
管线与工程解耦；内置示例 freertos_f103 来自真实 FREERTOS_2 构建。"""
import argparse, json, re, sys
from pathlib import Path
from elens import maps, elfio, svd, facts, model, sample, frames, export, rtos

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT.parent / "examples"
GDB = Path(r"C:\STM32Tools\xpack-arm-none-eabi-gcc-14.2.1-1.1\bin\arm-none-eabi-gdb.exe")
OPENOCD = Path(r"C:\STM32Tools\xpack-openocd-0.12.0-7\bin\openocd.exe")
_OCD_ROOT = OPENOCD.parent.parent
OCD_SCRIPTS = next((p for p in (_OCD_ROOT / "openocd/scripts", _OCD_ROOT / "share/openocd/scripts") if p.exists()),
                   _OCD_ROOT / "openocd/scripts")
PROJ = Path(r"D:\FREERTOS\TIETOU\FREERTOS_2")

EXAMPLE_CFG = {
    "name": "freertos_f103",
    "map": PROJ / "MDK-ARM/FREERTOS_2/FREERTOS_2.map",
    "axf": PROJ / "MDK-ARM/FREERTOS_2/FREERTOS_2.axf",
    "svd": Path(r"D:\KELI_MDK\Keil\STM32F1xx_DFP\2.4.1\SVD\STM32F103xx.svd"),
    "peripheral": "GPIOC", "register": "ODR",
    "header": PROJ / "Drivers/CMSIS/Device/ST/STM32F1xx/Include/stm32f103xe.h",
    "hal_gpio": PROJ / "Drivers/STM32F1xx_HAL_Driver/Inc/stm32f1xx_hal_gpio.h",
    "source_dir": PROJ, "profile": sample.F103_PROFILE,
}

def _kernel_version(source_dir):
    th = Path(source_dir) / "FreeRtos/Inc/task.h"
    if th.exists():
        m = re.search(r'#define\s+tskKERNEL_VERSION_NUMBER\s+"([^"]+)"', th.read_text(encoding="utf-8", errors="replace"))
        if m:
            return {"version": m.group(1), "file": str(th)}
    return None

def run_import(cfg, out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    prof = cfg["profile"]
    mp = maps.parse_map(cfg["map"])
    symbols, removed = mp["symbols"], mp["removed_sections"]
    adapter = rtos.detect_adapter(symbols)
    if adapter is None:
        print("[import] 未检测到受支持的 RTOS 内核符号（MVP 仅 FreeRTOS 适配器）。")
        sys.exit(2)
    linked, reason = maps.check_rtos_linked(symbols, removed, adapter.required_symbols())
    # 静态 idle TCB/栈别名（若存在）
    for key, pat in [("static_idle_tcb", "xIdleTaskTCB"), ("static_idle_stack", "uxIdleTaskStack")]:
        hit = next((n for n in symbols if pat in n), None)
        if hit:
            symbols[key] = dict(symbols[hit], alias_of=hit)
    sym_doc = {"source": {"file": str(cfg["map"]), "sha256": model.sha256_file(cfg["map"])},
               "format": mp["format"], "symbols": symbols, "rtos_linked": linked, "reason": reason,
               "removed_sections_count": len(removed)}
    (out_dir / "symbols.json").write_text(json.dumps(sym_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[import] map={mp['format']} symbols={len(symbols)} rtos={adapter.name} linked={linked}")
    if not linked:
        print("[import] FR-1 启动检测失败：" + reason); sys.exit(2)

    types, raw = elfio.dwarf_offsets(cfg["axf"], adapter.dwarf_types(), cfg.get("gdb", GDB))
    (out_dir / "gdb_ptype_raw.txt").write_text(raw, encoding="utf-8")
    checks = {"List_t_size_matches_map": types.get("List_t", {}).get("size") == symbols.get("xDelayedTaskList1", {}).get("size"),
              "TCB_size_matches_idle": types.get("TCB_t", {}).get("size") == symbols.get("static_idle_tcb", {}).get("size")}
    off_doc = {"source": {"axf": str(cfg["axf"]), "sha256": model.sha256_file(cfg["axf"]),
                          "method": "gdb ptype /o (DWARF, 仅读构建产物)"}, "types": types, "cross_check": checks}
    (out_dir / "offsets.json").write_text(json.dumps(off_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[import] DWARF sizes: " + ", ".join(f"{k}={v['size']}B" for k, v in types.items()) + f" checks={checks}")

    base, img = elfio.flash_image(cfg["axf"], prof["flash_base"], prof["flash_size"])
    (out_dir / "flash_from_axf.bin").write_bytes(img)
    pack = model.bind_pack(cfg["axf"], cfg["map"], base, img, "offsets.json", "symbols.json")
    pack["flash_image"]["file"] = str(out_dir / "flash_from_axf.bin")
    (out_dir / "firmware_pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[import] flash {hex(base)} +{len(img)}B sha={pack['flash_image']['sha256'][:16]}…")

    reg = svd.parse_register(cfg["svd"], cfg["peripheral"], cfg["register"])
    hdr = svd.parse_gpio_typedef(cfg["header"])
    odr_hdr = next((f for f in hdr["GPIO_TypeDef"]["fields"] if f["name"] == cfg["register"]), None)
    base_macro = cfg["peripheral"] + "_BASE"
    agree = (int(reg["peripheral"]["base_address"], 16) == int(hdr["gpio_bases"].get(base_macro, "0"), 16)
             and odr_hdr is not None and reg["register"]["offset"] == odr_hdr["offset"])
    struct = {**reg, **hdr, "cross_check": {"svd_header_agree": agree}}
    (out_dir / "structure.json").write_text(json.dumps(struct, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[import] SVD {cfg['peripheral']}.{cfg['register']}@{reg['register']['address']} "
          f"fields={len(reg['register']['fields'])} derivedFrom={reg['peripheral']['derivedFrom']} agree={agree}")

    fa = facts.extract_facts(cfg["source_dir"])
    if cfg.get("hal_gpio"):
        fa["hal_gpio_pin_state"] = facts.hal_pin_states(cfg["hal_gpio"])
    fa["kernel"] = _kernel_version(cfg["source_dir"])
    (out_dir / "facts.json").write_text(json.dumps(fa, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "profile.json").write_text(json.dumps(prof, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[import] facts tasks={[t['name'] for t in fa['tasks']]} delays={len(fa['delay_calls'])} "
          f"writes={len(fa['gpio_writes'])} pins={ {k:(v.get('port'),v.get('bit')) for k,v in fa['pins'].items()} }")
    return {"symbols": sym_doc, "offsets": off_doc, "structure": struct, "facts": fa, "pack": pack}, adapter

def load_artifacts(ex_dir):
    ex_dir = Path(ex_dir)
    a = {k: json.loads((ex_dir / f).read_text(encoding="utf-8")) for k, f in
         [("symbols", "symbols.json"), ("offsets", "offsets.json"), ("structure", "structure.json"),
          ("facts", "facts.json"), ("pack", "firmware_pack.json")]}
    pp = ex_dir / "profile.json"
    if pp.exists():
        a["profile"] = json.loads(pp.read_text(encoding="utf-8"))
    return a

def load_snapshots(ex_dir):
    p = Path(ex_dir) / "snapshots.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def cmd_import_example(args):
    run_import(EXAMPLE_CFG, EXAMPLES / EXAMPLE_CFG["name"])

def cmd_import(args):
    prof = json.loads(Path(args.profile).read_text(encoding="utf-8")) if args.profile else dict(sample.F103_PROFILE)
    cfg = {"name": args.name, "map": Path(args.map), "axf": Path(args.axf),
           "svd": Path(args.svd), "peripheral": args.peripheral, "register": args.register,
           "header": Path(args.header), "source_dir": Path(args.source_dir), "profile": prof}
    if args.hal_gpio:
        cfg["hal_gpio"] = Path(args.hal_gpio)
    if args.gdb:
        cfg["gdb"] = Path(args.gdb)
    out = Path(args.out) if args.out else EXAMPLES / args.name
    run_import(cfg, out)

def cmd_sample(args):
    ex = EXAMPLES / args.example
    a = load_artifacts(ex)
    adapter = rtos.detect_adapter(a["symbols"]["symbols"])
    prof = dict(a.get("profile") or EXAMPLE_CFG["profile"])
    odr = a["structure"]["register"]["offset"]
    svd_base = int(a["structure"]["peripheral"]["base_address"], 16)
    if prof.get("gpio_base") != svd_base:
        print(f"[sample] GPIO 基址按 SVD 权威值对齐 {hex(prof.get('gpio_base', 0))} → {hex(svd_base)} "
              f"({a['structure']['peripheral']['name']})")
        prof["gpio_base"] = svd_base
    if args.manual:
        if args.frames != 1:
            print("[sample] 手工采集仅支持单帧，忽略 --frames/--interval")
        new_shots = [sample.import_manual(args.manual, prof, a["pack"], a["symbols"]["symbols"],
                                          a["offsets"], adapter, odr_offset=odr)]
    else:
        new_shots = sample.sample_session(prof, a["pack"], a["symbols"]["symbols"], a["offsets"], adapter,
                                          ex / "sample_run", args.openocd, args.scripts, odr_offset=odr,
                                          frames=args.frames, interval_s=args.interval)
    snaps = load_snapshots(ex)
    snaps.extend(new_shots)
    (ex / "snapshots.json").write_text(json.dumps(snaps, ensure_ascii=False, indent=1), encoding="utf-8")
    for i, snap in enumerate(new_shots):
        diag = snap.get("diagnostic") or {}
        print(f"[sample] frame {i + 1}/{len(new_shots)} status={snap.get('status')} "
              f"identity={snap.get('identity', {}).get('status')} valid={snap.get('valid')} "
              f"stage={diag.get('stage', '?')}/{diag.get('code', '?')}")
    sid = (new_shots[0].get("session") or {}).get("id", "-") if new_shots else "-"
    ok = sum(1 for s in new_shots if s.get("valid"))
    print(f"[sample] session={sid} frames={len(new_shots)} valid={ok}")
    failed = next((s for s in new_shots if s.get("status") == "probe_failed"), None)
    if failed:
        print("[sample] 采样失败（诚实记录，不编造）：" + (failed.get("diagnostic") or {}).get("message", "")[:200])

def cmd_export(args):
    ex = EXAMPLES / args.example
    a = load_artifacts(ex)
    snaps = load_snapshots(ex)
    adapter = rtos.detect_adapter(a["symbols"]["symbols"])
    prof = a.get("profile") or EXAMPLE_CFG["profile"]
    payload = frames.build_payload(args.example, a, snaps, prof, adapter.name if adapter else "?")
    out = export.export(payload, args.out)
    print(f"[export] {out} ({out.stat().st_size} B) snapshots={len(snaps)} valid={sum(1 for s in snaps if s.get('valid'))}")

def cmd_build(args):
    cmd_import_example(args)
    cmd_export(args)

def main():
    p = argparse.ArgumentParser(prog="elens")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("import-example").set_defaults(fn=cmd_import_example)
    ip = sub.add_parser("import", help="导入任意工程（map/axf/svd/header/源码），生成可采样产物")
    ip.add_argument("--map", required=True); ip.add_argument("--axf", required=True)
    ip.add_argument("--svd", required=True); ip.add_argument("--header", required=True)
    ip.add_argument("--source-dir", required=True)
    ip.add_argument("--peripheral", default="GPIOC"); ip.add_argument("--register", default="ODR")
    ip.add_argument("--hal-gpio"); ip.add_argument("--gdb")
    ip.add_argument("--name", default="custom"); ip.add_argument("--profile"); ip.add_argument("--out")
    ip.set_defaults(fn=cmd_import)
    sp = sub.add_parser("sample"); sp.add_argument("--example", default="freertos_f103")
    sp.add_argument("--manual"); sp.add_argument("--openocd", default=str(OPENOCD))
    sp.add_argument("--scripts", default=str(OCD_SCRIPTS))
    sp.add_argument("--frames", type=int, default=1, help="连续采样的帧数（默认 1）")
    sp.add_argument("--interval", type=float, default=1.0, help="帧间隔秒数（主机侧等待，目标保持运行）")
    sp.set_defaults(fn=cmd_sample)
    ep = sub.add_parser("export"); ep.add_argument("--example", default="freertos_f103")
    ep.add_argument("--out", default=str(ROOT.parent / "dist" / "embedded-lens.html")); ep.set_defaults(fn=cmd_export)
    bp = sub.add_parser("build"); bp.add_argument("--example", default="freertos_f103")
    bp.add_argument("--out", default=str(ROOT.parent / "dist" / "embedded-lens.html")); bp.set_defaults(fn=cmd_build)
    args = p.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()