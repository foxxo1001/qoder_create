"""单元测试：用合成内存夹具验证 FR-5 链表遍历 / §6.3 身份比对 / FR-3 偏移 wiring。
夹具仅为算法测试，明确标注 SYNTHETIC，绝不作为产品快照导出。"""
import json, struct, tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from elens.rtos import FreeRTOSAdapter, RamReader
from elens import model, maps, svd, facts, frames, sample

EX = Path(__file__).resolve().parent.parent / "examples" / "freertos_f103"
off = json.loads((EX / "offsets.json").read_text(encoding="utf-8"))
sym = json.loads((EX / "symbols.json").read_text(encoding="utf-8"))["symbols"]
S = {k: int(v["addr"], 16) for k, v in sym.items()}
BASE, SIZE = 0x20000000, 0x1800
blob = bytearray(SIZE)

def w32(addr, v): struct.pack_into("<I", blob, addr - BASE, v)
def wstr(addr, s): blob[addr - BASE:addr - BASE + len(s)] = s.encode()

def make_tcb(addr, name, prio):
    f = off["types"]["TCB_t"]["fields"]
    w32(addr + f["uxPriority"]["offset"], prio)
    wstr(addr + f["pcTaskName"]["offset"], name)
    return addr

def make_list(addr, node_addrs):
    L = off["types"]["List_t"]["fields"]; M = off["types"]["MiniListItem_t"]["fields"]; LI = off["types"]["ListItem_t"]["fields"]
    end = addr + L["xListEnd"]["offset"]
    w32(addr + L["uxNumberOfItems"]["offset"], len(node_addrs))
    w32(end + M["xItemValue"]["offset"], 0xFFFFFFFF)
    chain = node_addrs + [end]
    w32(end + M["pxNext"]["offset"], chain[0])
    for i, n in enumerate(node_addrs):
        w32(n + LI["pxNext"]["offset"], chain[i + 1])
        w32(n + LI["pxPrevious"]["offset"], chain[i - 1] if i else end)
    w32(end + M["pxPrevious"]["offset"], node_addrs[-1] if node_addrs else end)
    return end

idle = make_tcb(S["static_idle_tcb"], "IDLE", 0)
led1 = make_tcb(0x20000400, "led1", 1)
led3 = make_tcb(0x20000500, "led3", 1)
tcb_f = off["types"]["TCB_t"]["fields"]; li_f = off["types"]["ListItem_t"]["fields"]
n1 = led1 + tcb_f["xStateListItem"]["offset"]; n3 = led3 + tcb_f["xStateListItem"]["offset"]
w32(n1 + li_f["xItemValue"]["offset"], 1000); w32(n1 + li_f["pvOwner"]["offset"], led1)
w32(n3 + li_f["xItemValue"]["offset"], 1000); w32(n3 + li_f["pvOwner"]["offset"], led3)
make_list(S["xDelayedTaskList1"], [n1, n3])
make_list(S["pxReadyTasksLists"] + off["types"]["List_t"]["size"], [])  # prio1 空
w32(S["pxDelayedTaskList"], S["xDelayedTaskList1"])
w32(S["pxCurrentTCB"], idle)
w32(S["xTickCount"], 500)
w32(S["xSchedulerRunning"], 1)

ad = FreeRTOSAdapter()
dec = ad.decode(RamReader(bytes(blob), BASE), sym, off, {"sampled_at": "TEST"})
assert dec["current"]["name"] == "IDLE", dec["current"]
assert dec["scalars"]["xTickCount"]["value"] == 500
names = [e["tcb"]["name"] for e in dec["delayed"]["entries"]]
wakes = [e["wake_tick"] for e in dec["delayed"]["entries"]]
assert names == ["led1", "led3"], names
assert wakes == [1000, 1000], wakes
assert dec["delayed"]["valid"] and dec["valid"]
assert dec["ready_priority1"]["entries"] == []
print("[test] FR-5 链表遍历 OK: current=IDLE delayed=", names, "wakes=", wakes, "valid=", dec["valid"])

# 哨兵破坏 → 校验失败
bad = bytearray(blob); struct.pack_into("<I", bad, S["xDelayedTaskList1"] + 8 - BASE, 0x1234)
dec2 = ad.decode(RamReader(bytes(bad), BASE), sym, off, {"sampled_at": "TEST"})
assert not dec2["delayed"]["valid"] and not dec2["valid"]
print("[test] 哨兵破坏 → 帧不可用 OK")

# §6.3 身份比对
pf = {"base": "0x8000000", "size": 8, "bytes": b"\x01\x02\x03\x04\x05\x06\x07\x08"}
assert model.verify_identity(b"\x01\x02\x03\x04\x05\x06\x07\x08", pf)["status"] == "verified"
assert model.verify_identity(b"\x01\x02\xFF\x04\x05\x06\x07\x08", pf)["status"] == "mismatch"
assert model.verify_identity(None, pf)["status"] == "unverified"
print("[test] §6.3 身份比对 verified/mismatch/unverified OK")

# FR-1 启动检测：缺失 / 被丢弃 / 正常链接（合成符号表）
req = FreeRTOSAdapter().required_symbols()
full = {s: {"addr": "0x20000000", "object": "tasks.o"} for s in req}
ok, why = maps.check_rtos_linked(full, [], req)
assert ok and why is None
miss = {s: v for s, v in full.items() if s != "xTickCount"}
ok, why = maps.check_rtos_linked(miss, [], req)
assert not ok and "符号缺失" in why and "xTickCount" in why
disc = dict(full); disc["pxCurrentTCB"] = {"addr": "0x20000000", "object": "removed.o"}
ok, why = maps.check_rtos_linked(disc, ["removed.o"], req)
assert not ok and "被丢弃" in why and "pxCurrentTCB" in why
print("[test] FR-1 启动检测 linked/missing/discarded OK")

# FR-2 SVD cluster + derivedFrom（合成 SVD，明确标注 TEST）
SVD_TEST = """<device><version>1.0-test</version><peripherals>
<peripheral><name>BASEP</name><baseAddress>0x40000000</baseAddress><registers>
<register><name>CTRL</name><addressOffset>0x0</addressOffset><size>32</size>
<fields><field><name>EN</name><bitOffset>0</bitOffset><bitWidth>1</bitWidth></field></fields></register>
<cluster><name>CH</name><addressOffset>0x10</addressOffset>
<register><name>STAT</name><addressOffset>0x4</addressOffset><size>32</size>
<fields><field><name>RDY</name><bitOffset>3</bitOffset><bitWidth>1</bitWidth></field></fields></register></cluster>
</registers></peripheral>
<peripheral derivedFrom="BASEP"><name>DERP</name><baseAddress>0x40001000</baseAddress></peripheral>
</peripherals></device>"""
with tempfile.TemporaryDirectory() as td:
    sp = Path(td) / "test.svd"; sp.write_text(SVD_TEST, encoding="utf-8")
    r = svd.parse_register(sp, "BASEP", "CH.STAT")
    assert r["register"]["offset"] == 0x14 and r["register"]["address"] == "0x40000014"
    assert r["register"]["defined_in"] == "BASEP"
    assert r["register"]["fields"][0]["name"] == "RDY" and r["register"]["fields"][0]["bit_offset"] == 3
    d = svd.parse_register(sp, "DERP", "CTRL")
    assert d["peripheral"]["derivedFrom"] == "BASEP" and d["register"]["address"] == "0x40001000"
    assert d["register"]["defined_in"] == "BASEP" and d["register"]["fields"][0]["name"] == "EN"
    dc = svd.parse_register(sp, "DERP", "CH.STAT")
    assert dc["register"]["address"] == "0x40001014" and dc["register"]["offset"] == 0x14
print("[test] FR-2 SVD cluster+derivedFrom OK (synthetic SVD)")

# HAL 引脚枚举：只认 GPIO_PinState 枚举块，忽略后续宏干扰（合成头文件）
HAL_TEST = ("typedef enum\n{\n  GPIO_PIN_RESET = 0u,\n  GPIO_PIN_SET\n} GPIO_PinState;\n"
            "#define IS_GPIO_PIN_ACTION(A) (((A) == GPIO_PIN_RESET) || ((A) == GPIO_PIN_SET))\n")
with tempfile.TemporaryDirectory() as td:
    hp = Path(td) / "hal_gpio.h"; hp.write_text(HAL_TEST, encoding="utf-8")
    st = facts.hal_pin_states(hp)
    assert st["GPIO_PIN_RESET"]["value"] == 0 and st["GPIO_PIN_RESET"]["line"] == 3, st
    assert st["GPIO_PIN_SET"]["value"] == 1 and st["GPIO_PIN_SET"]["line"] == 4, st
print("[test] HAL GPIO_PIN_RESET=0/SET=1 枚举块解析 OK (synthetic header)")

# config 整数解析：后缀 / 任意类型 cast / 拒绝表达式垃圾
assert facts._config_int("72000000u") == 72000000
assert facts._config_int("0xFFUL") == 255
assert facts._config_int("( ( unsigned long ) 72000000 )") == 72000000
assert facts._config_int("( (uint32_t)5 )") == 5
assert facts._config_int("( configFOO + 1 )") is None
assert facts._config_int("(") is None and facts._config_int("[Platform") is None
print("[test] config 整数解析 suffix/cast/拒绝垃圾 OK")

# HAL 单行枚举 + 块内注释提及另一成员（合成头文件）
HAL_ONE = ("typedef enum { GPIO_PIN_RESET = 0u, /* GPIO_PIN_SET */ GPIO_PIN_SET } GPIO_PinState;\n"
           "#define X GPIO_PIN_RESET\n")
HAL_CMT = "typedef enum\n{\n  /* GPIO_PIN_SET means 1 */\n  GPIO_PIN_RESET = 0u,\n  GPIO_PIN_SET\n} GPIO_PinState;\n"
with tempfile.TemporaryDirectory() as td:
    h1 = Path(td) / "h1.h"; h1.write_text(HAL_ONE, encoding="utf-8")
    s1 = facts.hal_pin_states(h1)
    assert s1["GPIO_PIN_RESET"]["value"] == 0 and s1["GPIO_PIN_SET"]["value"] == 1, s1
    h2 = Path(td) / "h2.h"; h2.write_text(HAL_CMT, encoding="utf-8")
    s2 = facts.hal_pin_states(h2)
    assert s2["GPIO_PIN_RESET"]["value"] == 0 and s2["GPIO_PIN_RESET"]["line"] == 4, s2
    assert s2["GPIO_PIN_SET"]["value"] == 1 and s2["GPIO_PIN_SET"]["line"] == 5, s2
print("[test] HAL 单行枚举/块内注释抗干扰 OK (synthetic header)")
# GPIO 术语只描述已识别调用，不把静态写入当成实际电平变化。
def gpio_write(line, state="GPIO_PIN_SET", fn="task_a", port="LED_GPIO_Port", pin="LED_Pin"):
    return {"file": "SYNTHETIC.c", "line": line, "in_fn": fn,
            "port_macro": port, "pin_macro": pin, "state": state}


def gpio_terms(writes):
    return frames.build_terms({"config": {}, "delay_calls": [], "gpio_writes": writes}, {})


scope_note = "调用存在不等于实际执行；其他任务、中断、Toggle/直接寄存器写和硬件接法未覆盖，不能证明电平恒定或周期闪烁"
for states in [("GPIO_PIN_SET",) * 3, ("GPIO_PIN_RESET",) * 2,
               ("GPIO_PIN_SET", "GPIO_PIN_RESET")]:
    writes = [gpio_write(i + 1, state) for i, state in enumerate(states)]
    cards = gpio_terms(writes)
    assert len(cards) == 1 and cards[0]["kind"] == "gpio_dual", cards
    card = cards[0]
    assert card["writes"] == writes, card
    assert scope_note in card["note"] and "已识别" in card["title"], card
    assert all(state in card["title"] and state in card["notice"] for state in states), card
    assert all(label in card["notice"] for label in ("task_a", "LED_GPIO_Port", "LED_Pin")), card

assert gpio_terms([]) == [] and gpio_terms([gpio_write(1)]) == []
for other_group in ({"fn": "task_b"}, {"port": "OTHER_GPIO_Port"}, {"pin": "OTHER_Pin"}):
    assert gpio_terms([gpio_write(1), gpio_write(2, **other_group)]) == []
    writes = [gpio_write(1), gpio_write(2), gpio_write(3, "GPIO_PIN_RESET", **other_group)]
    assert gpio_terms(writes)[0]["writes"] == writes[:2]
    writes.append(gpio_write(4, "GPIO_PIN_RESET", **other_group))
    cards = gpio_terms(writes)
    assert len(cards) == 2 and [c["writes"] for c in cards] == [writes[:2], writes[2:]], cards

delay_terms = frames.build_terms({
    "config": {"configTICK_RATE_HZ": {"value": 1000, "file": "SYNTHETIC.h", "line": 1}},
    "delay_calls": [{"ticks": 500, "file": "SYNTHETIC.c", "line": 2, "in_fn": "task_a"}],
    "gpio_writes": [],
}, {})
assert delay_terms[0]["kind"] == "delay" and delay_terms[0]["derived"]["value"] == 0.5
print("[test] GPIO 同状态/混合状态及函数/端口/引脚分组与范围声明 OK (synthetic facts)")


# 所有进程、TCL 连接和等待都被 Mock；仅在临时目录写 SYNTHETIC 数据。
def mock_sample(*, start_error=None, connect_error=None, exited=False, responses=None,
                dumps=None, decoder=None, frames=1):
    responses = responses or {}
    data = {"board_flash.bin": pf["bytes"], "board_ram.bin": bytes(blob),
            "board_gpio.bin": bytes(sample.F103_PROFILE["gpio_dump_size"])}
    data.update(dumps or {})
    decoder = decoder if decoder is not None else Mock(wraps=ad, spec=FreeRTOSAdapter)
    proc = Mock()
    proc.poll.return_value = 1 if exited else None
    rpc = Mock(spec=sample.TclRPC)

    def command(text):
        verb = text.split(" ", 1)[0]
        path = Path(text[len("dump_image "):].rsplit(" ", 2)[0]) if verb == "dump_image" else None
        result = responses.get(path.name if path else verb, "")
        if isinstance(result, Exception):
            raise result
        if path and not result and data[path.name] is not None:
            path.write_bytes(data[path.name])
        return result

    def start(*args, **kwargs):
        if start_error is not None:
            raise start_error
        kwargs["stdout"].write("SYNTHETIC OpenOCD exit log\n")
        kwargs["stdout"].flush()
        return proc

    rpc.cmd.side_effect = command
    with tempfile.TemporaryDirectory(prefix="elens-synthetic-") as td:
        pack_file = Path(td) / "SYNTHETIC_flash.bin"
        pack_file.write_bytes(pf["bytes"])
        pack = {"flash_image": {"base": pf["base"], "size": pf["size"], "file": str(pack_file)}}
        with patch.object(sample.subprocess, "Popen", side_effect=start) as launch, \
             patch.object(sample, "TclRPC", return_value=rpc, side_effect=connect_error) as connect, \
             patch.object(sample.time, "sleep"), \
             patch.object(sample.socket, "create_connection", side_effect=AssertionError("禁止真实连接")):
            snaps = sample.sample_session(sample.F103_PROFILE, pack, sym, off, decoder,
                                          td, "SYNTHETIC_openocd", "SYNTHETIC_scripts",
                                          frames=frames, interval_s=0.25)
        snap = snaps[0] if frames == 1 else snaps
        launch.assert_called_once()
        if start_error is not None:
            connect.assert_not_called()
            proc.terminate.assert_not_called()
        elif not exited:
            proc.terminate.assert_called_once()
        if start_error is None and connect_error is None and not exited:
            rpc.close.assert_called_once()
        else:
            rpc.cmd.assert_not_called()
        if connect_error is not None:
            assert connect.call_count == 40
    commands = [c.args[0] for c in rpc.cmd.call_args_list]
    assert all(c in ("halt", "resume", "shutdown") or c.startswith("dump_image ") for c in commands), commands
    return snap, commands, decoder


def assert_unavailable(snap, stage, code):
    assert snap["valid"] is False, snap
    assert snap["diagnostic"]["stage"] == stage and snap["diagnostic"]["code"] == code, snap
    assert isinstance(snap["diagnostic"]["message"], str), snap
    assert "resume_ok" in snap, snap


for error, code in [(FileNotFoundError("SYNTHETIC tool not found"), "tool_not_found"),
                    (PermissionError("SYNTHETIC launch denied"), "tool_start_failed")]:
    snap, commands, decoder = mock_sample(start_error=error)
    assert_unavailable(snap, "tool", code)
    assert snap["status"] == "probe_failed" and snap["resume_ok"] is None, snap
    assert snap["identity"]["reason"] == str(error) == snap["diagnostic"]["message"]
    assert str(error) in snap["notes"] and snap["decoded"] is None
    decoder.decode.assert_not_called()

snap, commands, decoder = mock_sample(connect_error=ConnectionRefusedError("SYNTHETIC TCL refused"))
assert_unavailable(snap, "connect", "tcl_connect_failed")
assert snap["status"] == "probe_failed" and snap["resume_ok"] is None
assert "SYNTHETIC TCL refused" in snap["diagnostic"]["message"]
assert snap["diagnostic"]["message"] == snap["identity"]["reason"] == snap["notes"][0]
snap, commands, decoder = mock_sample(exited=True)
assert_unavailable(snap, "connect", "openocd_exited")
assert "SYNTHETIC OpenOCD exit log" in snap["diagnostic"]["message"]

for response, code, expected_commands, resumed in [
    ("Error: SYNTHETIC halt failed", "halt_failed", ["halt", "resume"], True),
    (TimeoutError("SYNTHETIC halt timeout"), "unknown", ["halt"], None),
]:
    snap, commands, decoder = mock_sample(responses={"halt": response})
    assert_unavailable(snap, "halt", code)
    assert snap["status"] == "probe_failed" and snap["resume_ok"] is resumed
    assert str(response) in snap["diagnostic"]["message"] and commands == expected_commands
    decoder.decode.assert_not_called()

for dump_name in ("board_flash.bin", "board_ram.bin", "board_gpio.bin"):
    for response, code in [("Error: SYNTHETIC read failed", "read_failed"),
                           (OSError("SYNTHETIC read disconnected"), "unknown")]:
        snap, commands, decoder = mock_sample(responses={dump_name: response})
        assert_unavailable(snap, "read", code)
        assert snap["status"] == "probe_failed" and snap["resume_ok"] is True
        assert str(response) in snap["diagnostic"]["message"]
        assert commands[0] == "halt" and commands[-1] == "resume" and commands.count("resume") == 1
        decoder.decode.assert_not_called()

for response, code in [("Error: SYNTHETIC resume failed", "resume_failed"),
                       (TimeoutError("SYNTHETIC resume timeout"), "unknown")]:
    for read_response in (None, OSError("SYNTHETIC prior read failure")):
        responses = {"resume": response}
        if read_response is not None:
            responses["board_ram.bin"] = read_response
        snap, commands, decoder = mock_sample(responses=responses)
        assert_unavailable(snap, "resume", code)
        assert snap["status"] == "probe_failed" and snap["resume_ok"] is False and snap["decoded"] is None
        assert str(response) in snap["diagnostic"]["message"]
        assert commands[-1] == "resume" and commands.count("resume") == 1
        if read_response is not None:
            assert str(read_response) in snap["notes"], snap
        decoder.decode.assert_not_called()

snap, commands, decoder = mock_sample()
assert snap["valid"] and snap["status"] == "ok" and snap["resume_ok"] is True, snap
assert snap["diagnostic"] == {"stage": "complete", "code": "ok", "message": ""}
assert snap["identity"]["status"] == "verified" and snap["decoded"]["current"]["name"] == "IDLE"
assert len(commands) == 6 and commands[0] == "halt" and commands[-2:] == ["resume", "shutdown"]
decoder.decode.assert_called_once()

for flash, status in [(b"\xff" * pf["size"], "mismatch"), (None, "unverified")]:
    snap, commands, decoder = mock_sample(dumps={"board_flash.bin": flash})
    assert_unavailable(snap, "identity", "identity_" + status)
    assert snap["identity"]["status"] == status and snap["decoded"] is None
    assert snap["diagnostic"]["message"] == snap["identity"]["reason"]
    assert any("固件身份未通过核验" in note for note in snap["notes"])
    decoder.decode.assert_not_called()

snap, commands, decoder = mock_sample(dumps={"board_ram.bin": b""})
assert_unavailable(snap, "read", "ram_missing")
assert snap["diagnostic"]["message"] == "无 RAM 数据" and "无 RAM 数据" in snap["notes"]
decoder.decode.assert_not_called()
snap, commands, decoder = mock_sample(dumps={"board_ram.bin": bytes(bad)})
assert_unavailable(snap, "structure", "structure_invalid")
assert snap["identity"]["status"] == "verified" and not snap["decoded"]["valid"]
assert snap["diagnostic"]["message"] in snap["notes"]

decoder = Mock(spec=FreeRTOSAdapter)
decoder.decode.side_effect = ValueError("SYNTHETIC decode failure")
snap, commands, decoder = mock_sample(decoder=decoder)
assert_unavailable(snap, "structure", "unknown")
assert snap["identity"]["status"] == "verified" and snap["resume_ok"] is True
assert snap["diagnostic"]["message"] == "SYNTHETIC decode failure"
assert "SYNTHETIC decode failure" in snap["notes"]

# 直接构帧同样必须阻断恢复失败的数据，不能只改 sample_board 的异常路径。
decoder = Mock(spec=FreeRTOSAdapter)
snap = sample._build_snapshot(sample.F103_PROFILE, {}, sym, off, decoder, bytes(blob), bytes(32),
                              model.verify_identity(pf["bytes"], pf), 1, "SYNTHETIC",
                              resume_resp="Error: SYNTHETIC resume failed", resume_ok=False)
assert_unavailable(snap, "resume", "resume_failed")
assert snap["status"] == "probe_failed" and snap["decoded"] is None and snap["resume_ok"] is False
assert snap["diagnostic"]["message"] == snap["resume_resp"]
decoder.decode.assert_not_called()
print("[test] 采样各阶段诊断/原始原因/恢复失败阻断 OK (synthetic fixtures + Mock only)")

# 多帧会话：一次 OpenOCD 会话连拍；帧间目标保持运行；身份失败/恢复失败即停止。
snaps3, commands3, decoder3 = mock_sample(frames=3)
assert isinstance(snaps3, list) and len(snaps3) == 3, snaps3
assert all(s["valid"] and s["status"] == "ok" for s in snaps3)
assert len({s["session"]["id"] for s in snaps3}) == 1
assert [s["session"]["frame_index"] for s in snaps3] == [0, 1, 2]
assert all(s["session"]["frame_count"] == 3 and s["session"]["interval_s"] == 0.25 for s in snaps3)
assert decoder3.decode.call_count == 3
verbs = [c.split(" ", 1)[0] for c in commands3]
assert verbs == ["halt", "dump_image", "dump_image", "dump_image", "resume"] * 3 + ["shutdown"], verbs
print("[test] 多帧会话 3 帧同会话/序号/命令序列 OK (synthetic fixtures + Mock only)")

snaps1, commands1, _ = mock_sample()
assert snaps1["session"]["frame_count"] == 1 and snaps1["session"]["frame_index"] == 0
assert snaps1["session"]["id"].startswith("sess-")
print("[test] 单帧采样带会话元数据 OK (synthetic fixtures + Mock only)")

snaps_bad_id, commands_bad_id, decoder_bad_id = mock_sample(
    frames=3, dumps={"board_flash.bin": b"\xff" * pf["size"]})
assert len(snaps_bad_id) == 1 and snaps_bad_id[0]["identity"]["status"] == "mismatch", snaps_bad_id
assert snaps_bad_id[0]["diagnostic"]["code"] == "identity_mismatch"
assert snaps_bad_id[0]["session"]["frame_index"] == 0
decoder_bad_id.decode.assert_not_called()
assert [c.split(" ", 1)[0] for c in commands_bad_id][-1] == "shutdown"
print("[test] 身份不匹配记录首帧后停止会话 OK (synthetic fixtures + Mock only)")

snaps_resume, commands_resume, decoder_resume = mock_sample(
    frames=3, responses={"resume": "Error: SYNTHETIC resume failed"})
assert len(snaps_resume) == 1 and snaps_resume[0]["status"] == "probe_failed", snaps_resume
assert snaps_resume[0]["diagnostic"]["stage"] == "resume" and snaps_resume[0]["diagnostic"]["code"] == "resume_failed"
assert snaps_resume[0]["resume_ok"] is False
decoder_resume.decode.assert_not_called()
assert [c.split(" ", 1)[0] for c in commands_resume] == ["halt", "dump_image", "dump_image", "dump_image", "resume"]
print("[test] 恢复失败中断会话且不继续采样 OK (synthetic fixtures + Mock only)")

print("ALL TESTS PASSED (synthetic fixtures, not product data)")
