"""可插拔 RTOS 适配器 (SPI) + FreeRTOS 参考实现 + 跨平台概念对照卡。
偏移一律来自该构建 DWARF，不硬编码版本偏移。无真实构建的 RTOS 仅给概念卡，不假装解析。"""
import struct
from . import model

class RamReader:
    def __init__(self, blob, base):
        self.blob, self.base = blob, base
    def has(self, addr, n=4):
        off = addr - self.base
        return 0 <= off and off + n <= len(self.blob)
    def u32(self, addr):
        off = addr - self.base
        return struct.unpack_from("<I", self.blob, off)[0]
    def raw_hex(self, addr, n=4):
        off = addr - self.base
        return "0x" + self.blob[off:off + n][::-1].hex()
    def cstr(self, addr, maxlen=16):
        off = addr - self.base
        raw = self.blob[off:off + maxlen]
        return raw.split(b"\x00")[0].decode("ascii", errors="replace")

class RTOSAdapter:
    name = "generic"
    def required_symbols(self): raise NotImplementedError
    def dwarf_types(self): raise NotImplementedError
    def detect(self, symbols): return False
    def decode(self, ram, symbols, offsets, device): raise NotImplementedError

class FreeRTOSAdapter(RTOSAdapter):
    name = "FreeRTOS"
    LIST_CAP = 32
    def required_symbols(self):
        return ["pxCurrentTCB", "pxReadyTasksLists", "pxDelayedTaskList",
                "pxOverflowDelayedTaskList", "xDelayedTaskList1", "xDelayedTaskList2",
                "xTickCount", "xNextTaskUnblockTime", "xSchedulerRunning"]
    def dwarf_types(self):
        return ["List_t", "MiniListItem_t", "ListItem_t", "TCB_t"]
    def detect(self, symbols):
        return all(s in symbols for s in ["pxCurrentTCB", "xTickCount", "pxReadyTasksLists"])

    def _walk(self, ram, list_addr, off, sentinel=True):
        """从 xListEnd.pxNext 起遍历，回到 &xListEnd 止；校验地址/哨兵/上限。"""
        li = off["ListItem_t"]["fields"]
        end_marker = list_addr + off["List_t"]["fields"]["xListEnd"]["offset"]
        nxt = ram.u32(end_marker + off["MiniListItem_t"]["fields"]["pxNext"]["offset"])
        nodes, addrs = [], []
        end_val = ram.u32(end_marker + off["MiniListItem_t"]["fields"]["xItemValue"]["offset"])
        sentinel_ok = (end_val == 0xFFFFFFFF)
        for _ in range(self.LIST_CAP + 1):
            if nxt == end_marker:
                break
            if not ram.has(nxt, 20):
                sentinel_ok = False
                break
            addrs.append(nxt)
            item = {"addr": hex(nxt),
                    "xItemValue": ram.u32(nxt + li["xItemValue"]["offset"]),
                    "pvOwner": ram.u32(nxt + li["pvOwner"]["offset"])}
            nodes.append(item)
            nxt = ram.u32(nxt + li["pxNext"]["offset"])
        ok, checks = model.validate_list_walk(addrs, ram.base, len(ram.blob), self.LIST_CAP, sentinel_ok)
        return nodes, ok, checks

    def _tcb(self, ram, addr, off):
        f = off["TCB_t"]["fields"]
        if not ram.has(addr, off["TCB_t"]["size"]):
            return None
        return {"addr": hex(addr),
                "name": ram.cstr(addr + f["pcTaskName"]["offset"], f["pcTaskName"]["size"]),
                "priority": ram.u32(addr + f["uxPriority"]["offset"]),
                "name_hex": ram.raw_hex(addr + f["pcTaskName"]["offset"], f["pcTaskName"]["size"])}

    def decode(self, ram, symbols, offsets, device):
        off = offsets["types"]
        S = {k: int(v["addr"], 16) for k, v in symbols.items()}
        sampled = device.get("sampled_at")
        def m(addr, label):
            return model.measured(ram.u32(addr), hex(addr), ram.raw_hex(addr), sampled)
        scalars = {}
        for key in ["xTickCount", "xSchedulerRunning", "xNextTaskUnblockTime"]:
            if key in S and ram.has(S[key]):
                scalars[key] = m(S[key], key)
        cur_ptr = ram.u32(S["pxCurrentTCB"]) if ram.has(S["pxCurrentTCB"]) else None
        current = self._tcb(ram, cur_ptr, off) if cur_ptr else None
        # 优先级 1 就绪链表
        list_size = off["List_t"]["size"]
        ready1_addr = S["pxReadyTasksLists"] + 1 * list_size
        ready_nodes, ready_ok, ready_checks = self._walk(ram, ready1_addr, off)
        ready = []
        for n in ready_nodes:
            tcb = self._tcb(ram, n["pvOwner"], off)
            ready.append({"item": n, "tcb": tcb,
                          "is_current": cur_ptr is not None and n["pvOwner"] == cur_ptr})
        # 当前延时链表
        delayed = None
        if ram.has(S["pxDelayedTaskList"]):
            dl_ptr = ram.u32(S["pxDelayedTaskList"])
            dnodes, dok, dchecks = self._walk(ram, dl_ptr, off)
            entries = []
            for n in dnodes:
                tcb = self._tcb(ram, n["pvOwner"], off)
                entries.append({"item": n, "tcb": tcb, "wake_tick": n["xItemValue"],
                                "is_current": cur_ptr is not None and n["pvOwner"] == cur_ptr})
            delayed = {"list_addr": hex(dl_ptr), "entries": entries, "valid": dok, "checks": dchecks,
                       "which": "xDelayedTaskList1" if dl_ptr == S.get("xDelayedTaskList1")
                       else ("xDelayedTaskList2" if dl_ptr == S.get("xDelayedTaskList2") else "?")}
        valid = ready_ok and (delayed is None or delayed["valid"]) and current is not None
        return {"rtos": self.name, "scalars": scalars, "current_tcb_ptr": hex(cur_ptr) if cur_ptr else None,
                "current": current, "ready_priority1": {"list_addr": hex(ready1_addr), "entries": ready,
                                                       "valid": ready_ok, "checks": ready_checks},
                "delayed": delayed, "valid": valid}

# 其余 RTOS：MVP 不提供解析器（无真实构建不假装），仅概念对照 + 适配器占位。
class _ConceptOnly(RTOSAdapter):
    def __init__(self, name): self.name = name
    def detect(self, symbols): return False
    def required_symbols(self): return []
    def dwarf_types(self): return []

ADAPTERS = [FreeRTOSAdapter(), _ConceptOnly("RT-Thread"), _ConceptOnly("ThreadX"), _ConceptOnly("Zephyr")]

def detect_adapter(symbols):
    for a in ADAPTERS:
        if isinstance(a, FreeRTOSAdapter) and a.detect(symbols):
            return a
    return None

# 跨平台概念对照卡 (§13)：同一概念多平台写法，concept-only，不做解析。
CONCEPT_CARDS = [
    {"concept": "系统节拍 tick",
     "freertos": "configTICK_RATE_HZ + xTickCount",
     "rtthread": "RT_TICK_PER_SECOND + rt_tick_get()",
     "threadx": "TX_TIMER_TICKS_PER_SECOND + tx_time_get()",
     "zephyr": "CONFIG_SYS_CLOCK_TICKS_PER_SEC + k_uptime_ticks()",
     "stm32hal": "HAL_GetTick() (uwTick, 默认 1kHz)",
     "esp": "CONFIG_FREERTOS_HZ + xTaskGetTickCount()"},
    {"concept": "相对延时",
     "freertos": "vTaskDelay(ticks)",
     "rtthread": "rt_thread_delay(ticks)",
     "threadx": "tx_thread_sleep(ticks)",
     "zephyr": "k_sleep(K_TICKS(t))",
     "stm32hal": "HAL_Delay(ms) (忙等, 非 RTOS)",
     "esp": "vTaskDelay(pdMS_TO_TICKS(ms))"},
    {"concept": "创建任务",
     "freertos": "xTaskCreate(fn,name,stack,arg,prio,handle)",
     "rtthread": "rt_thread_create(name,entry,arg,stack,prio,timeslice)",
     "threadx": "tx_thread_create(&t,name,entry,arg,stack,prio,...)",
     "zephyr": "k_thread_create(&t,stack,SIZE,entry,...)",
     "stm32hal": "— (裸机无任务)",
     "esp": "xTaskCreatePinnedToCore(...)"},
    {"concept": "GPIO 置位",
     "freertos": "— (RTOS 不管 GPIO)",
     "rtthread": "rt_pin_write(pin, PIN_HIGH)",
     "threadx": "— (依赖厂商 BSP)",
     "zephyr": "gpio_pin_set_dt(&spec, 1)",
     "stm32hal": "HAL_GPIO_WritePin(port,pin,GPIO_PIN_SET)",
     "esp": "gpio_set_level(pin, 1)"},
]