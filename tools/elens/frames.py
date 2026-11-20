"""帧构造：把真实 artifacts + 快照装配成导出载荷；术语卡按工程事实通用生成（不写死任务名）。"""
from . import model
from .rtos import CONCEPT_CARDS

def build_terms(facts, structure):
    """每张卡回答：传了什么 / 哪个工程事实决定效果 / 效果在图上哪里可见。"""
    terms = []
    tick = facts["config"].get("configTICK_RATE_HZ", {}).get("value")
    for d in facts["delay_calls"]:
        if tick:
            sec = d["ticks"] / tick
            terms.append({
                "kind": "delay", "title": f"vTaskDelay({d['ticks']})",
                "source": {"file": d["file"], "line": d["line"], "fn": d.get("in_fn")},
                "passed": model.authoritative(d["ticks"], d["file"], line=d["line"]),
                "decider": model.authoritative(tick, facts["config"]["configTICK_RATE_HZ"]["file"],
                                               line=facts["config"]["configTICK_RATE_HZ"]["line"]),
                "derived": model.derived(round(sec, 4), f"{d['ticks']} tick ÷ {tick} Hz ≈ {sec:g} s",
                                         {"ticks": d["ticks"], "hz": tick}),
                "visible": "延时链表中的实测到期 tick（采样后可见）",
                "links": {"config": "configTICK_RATE_HZ", "graph": "delayed"},
            })
    # GPIO 同状态多处写入：同一函数内多处写同一状态 → 输出为何不变（通用，按 fn+pin 分组）
    by_fn_pin = {}
    for w in facts["gpio_writes"]:
        by_fn_pin.setdefault((w["in_fn"], w["pin_macro"]), []).append(w)
    for (fn, pin), ws in by_fn_pin.items():
        states = {w["state"] for w in ws}
        if len(ws) >= 2 and len(states) == 1:
            st = next(iter(states))
            sem = "置位操作（写 1）" if st == "GPIO_PIN_SET" else "复位操作（写 0）" if st == "GPIO_PIN_RESET" else "按 HAL 定义的写入"
            terms.append({
                "kind": "gpio_dual", "title": f"{fn}: {len(ws)} 处写入都是 {st}",
                "writes": [{"file": w["file"], "line": w["line"], "state": w["state"],
                            "pin_macro": w["pin_macro"]} for w in ws],
                "note": f"{st} 表示{sem}，置哪一位由 pin 参数决定（{pin}），不可混淆。"
                        "同函数内所有写入状态相同 → 引脚电平不会切换。",
                "links": {"graph": "register"},
            })
    return terms

def build_payload(example_dir, artifacts, snapshots, profile, adapter_name):
    sym, off, struct, facts, pack = (artifacts[k] for k in
                                     ["symbols", "offsets", "structure", "facts", "pack"])
    identity = {"status": "no-sample", "reason": "尚未采集板上数据"}
    for s in snapshots:
        if s.get("identity", {}).get("status") == "verified":
            identity = s["identity"]; break
        if s.get("identity", {}).get("status") == "mismatch":
            identity = s["identity"]
    return {
        "meta": {"tool": "EmbeddedLens", "version": "0.1.0-mvp", "example": example_dir},
        "device": {"name": profile["device"], "core": profile["core"],
                   "svd": struct["svd"], "flash_base": hex(profile["flash_base"]),
                   "ram_base": hex(profile["ram_base"])},
        "build": {"rtos": adapter_name, "rtos_linked": sym.get("rtos_linked", True),
                  "axf_sha": pack["axf"]["sha256"], "map_sha": pack["map"]["sha256"],
                  "kernel": facts.get("kernel")},
        "identity": identity,
        "structure": struct, "facts": facts, "offsets": off, "symbols": sym["symbols"],
        "snapshots": snapshots, "concepts": CONCEPT_CARDS,
        "terms": build_terms(facts, struct),
        "honesty": {"states": model.STATE_LABEL,
                    "contract": "每个数字归入四态之一并附溯源；禁止编造；身份未核验停止解释 RTOS (§6)"},
    }