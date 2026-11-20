"""单元测试：用合成内存夹具验证 FR-5 链表遍历 / §6.3 身份比对 / FR-3 偏移 wiring。
夹具仅为算法测试，明确标注 SYNTHETIC，绝不作为产品快照导出。"""
import json, struct, tempfile
from pathlib import Path
from elens.rtos import FreeRTOSAdapter, RamReader
from elens import model, maps, svd, facts

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
print("ALL TESTS PASSED (synthetic fixtures, not product data)")