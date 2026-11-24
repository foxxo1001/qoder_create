"""V4 单文件 HTML 导出：零外部依赖，内嵌真实数据与溯源，复用 bar()/stepper() 引擎。
浅色克制单强调色；四态标注；无数据诚实空态。"""
import json
from pathlib import Path

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EmbeddedLens · 嵌入式透视镜</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
--paper:#f2efe7;--surface:#faf8f2;--surface-2:#f5f2ea;--surface-3:#ece8dd;
--ink:#15181c;--ink-2:#383d43;--muted:#5f5d56;--faint:#918e84;
--line:#cfc9b8;--line-2:#e0dbc9;
--accent:#14406b;--accent-2:#1d5a94;--accent-soft:#e8edf3;--accent-tint:#cfdce8;
--ok:#2e6b34;--ok-soft:#e8f0e6;--warn:#96660f;--warn-soft:#f6eedb;--bad:#9e2b25;--bad-soft:#f6e7e4;
--idle:#8a8578;--bar-a:#14406b;--bar-b:#1d5a94;--bar-cur:#2e6b34;
--serif:Georgia,"Times New Roman","Songti SC","SimSun",serif;
--mono:"Cascadia Code","JetBrains Mono",Consolas,ui-monospace,SFMono-Regular,monospace;
--sans:"Segoe UI",system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
--r:3px;--ease:cubic-bezier(.22,.61,.36,1)}
html{scroll-behavior:smooth}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:14.5px;line-height:1.65;-webkit-font-smoothing:antialiased;min-height:100vh}
.wrap{width:100%;min-width:0;position:relative}
.wrap::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.28;mask-image:linear-gradient(#000,transparent 500px)}
#ldgrid,.wrap::before{background-image:linear-gradient(var(--line-2) 1px,transparent 1px),linear-gradient(90deg,var(--line-2) 1px,transparent 1px);background-size:56px 56px}
body.landing-on .wrap{visibility:hidden}
::selection{background:var(--accent-tint);color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
::-webkit-scrollbar{width:11px;height:11px}
::-webkit-scrollbar-track{background:var(--surface-2)}
::-webkit-scrollbar-thumb{background:var(--line);border:3px solid var(--surface-2);border-radius:99px}
::-webkit-scrollbar-thumb:hover{background:var(--accent-tint)}
*{scrollbar-width:thin;scrollbar-color:var(--line) var(--surface-2)}
.mono{font-family:var(--mono);font-feature-settings:"tnum" 1,"zero" 1}
.note{font-size:12.5px;color:var(--muted);line-height:1.6}
svg.ic{width:15px;height:15px;flex:0 0 auto;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;vertical-align:-2px}

/* datasheet masthead */
.masthead{display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:76px;padding:18px 0;border-bottom:1px solid var(--line)}
.workspace-label{display:flex;align-items:center;gap:12px;color:var(--muted);font-size:12px}
.workspace-label b{color:var(--ink);font-weight:600}
.workspace-label .slash{color:var(--line)}
.brand{min-width:0;padding:10px 8px 32px}
.brand-lockup{display:flex;align-items:center;gap:10px}
.mark{width:29px;height:29px;color:var(--accent);flex:0 0 auto}
.mark svg{width:29px;height:29px;stroke:currentColor;fill:none;stroke-width:1.5;stroke-linecap:round}
.brand-name{font-family:var(--serif);font-size:18px;font-weight:700;letter-spacing:-.035em;line-height:1.2}
.brand-name span{color:var(--accent)}
.brand-caption{font-family:var(--serif);font-size:10px;color:var(--muted);letter-spacing:.24em;margin-top:6px}
.kicker{font-family:var(--mono);font-size:9px;letter-spacing:.17em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}
h1{font-family:var(--serif);font-size:30px;font-weight:700;letter-spacing:-.015em;line-height:1.05}
.view-head{display:flex;align-items:center;justify-content:space-between;gap:18px;margin:30px 0 24px}
.view-head h2{font-family:var(--serif);font-size:27px;font-weight:700;letter-spacing:.025em;padding:0;margin:0 0 6px;border:0;gap:0}
.view-head p{font-size:12px;color:var(--muted)}
.view-index{font-family:var(--mono);font-size:10px;color:var(--faint);letter-spacing:.1em;white-space:nowrap}
.section-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px}
.section-head h3{font-size:14px;font-weight:650}
.section-head .note{font-size:11px}
.learn-more{margin-top:22px;border-top:1px solid var(--line-2);font-size:12px;color:var(--muted)}
.learn-more>summary{padding:15px 0 0;cursor:pointer;list-style:none;display:flex;align-items:center;gap:9px;color:var(--ink-2);font-weight:600}
.learn-more>summary::-webkit-details-marker{display:none}
.learn-more>summary::before{content:'+';font:16px var(--mono);color:var(--accent)}
.learn-more[open]>summary::before{content:'−'}
.learn-more .plain{margin:14px 0 0}
.learn-more .lesson-body{margin-top:16px}
.view-foot{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:18px 0 0;font-size:11px;color:var(--muted)}
.view-foot .mono{font-size:10px;letter-spacing:.06em}
.spec{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));font-family:var(--mono);font-size:12px;padding:14px 0;border-bottom:1px solid var(--line)}
.spec .row{display:flex;flex-direction:column;gap:4px;padding:0 18px;border-left:1px solid var(--line-2);min-width:0}
.spec .row:first-child{border-left:none;padding-left:0}
.spec .k{color:var(--muted);font-size:9px;letter-spacing:.12em}
.spec .val{color:var(--ink);font-weight:600;overflow-wrap:anywhere}

/* badges */
.badges{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}
.tag{font-family:var(--mono);font-size:11px;border:1px solid var(--line);border-radius:var(--r);padding:4px 10px;background:var(--surface);color:var(--ink-2);display:inline-flex;align-items:center;gap:7px}
.tag::before{content:"";width:6px;height:6px;background:var(--faint);flex:0 0 auto}
.tag.ok{border-color:#bcd3ba;color:var(--ok);background:var(--ok-soft)} .tag.ok::before{background:var(--ok)}
.tag.warn{border-color:#e0cfa8;color:var(--warn);background:var(--warn-soft)} .tag.warn::before{background:var(--warn)}
.tag.bad{border-color:#e0bdb8;color:var(--bad);background:var(--bad-soft)} .tag.bad::before{background:var(--bad)}
.tag.acc{border-color:var(--accent-tint);color:var(--accent);background:var(--accent-soft)} .tag.acc::before{background:var(--accent)}

/* ruled sections */
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:26px;margin-bottom:20px;position:relative;min-width:0}
h2{font-family:var(--sans);font-size:16px;font-weight:650;margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid var(--line-2);display:flex;align-items:center;gap:11px;letter-spacing:-.01em;flex-wrap:wrap}
h2 .n{font-family:var(--mono);font-size:10.5px;font-weight:600;background:transparent;color:var(--accent);border:1px solid var(--accent-tint);border-radius:var(--r);padding:3px 7px;letter-spacing:.05em}
.seal{width:26px;height:26px;border-radius:var(--r);display:inline-grid;place-items:center;flex:0 0 auto;border:1px solid var(--line)}
.seal svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.seal.ok{background:var(--ok-soft);color:var(--ok);border-color:#bcd3ba}
.seal.warn{background:var(--warn-soft);color:var(--warn);border-color:#e0cfa8}
.seal.bad{background:var(--bad-soft);color:var(--bad);border-color:#e0bdb8}
.fp{font-family:var(--mono);font-size:11px;background:var(--surface-2);border:1px solid var(--line-2);border-radius:var(--r);padding:3px 9px;color:var(--ink-2);display:inline-block;margin:3px 6px 0 0}

/* index nav */
.tabs{display:flex;flex-direction:column;gap:6px;margin:0;position:relative;padding:0}
.tab{border:none;background:transparent;border-radius:var(--r);padding:12px;cursor:pointer;font-family:var(--sans);font-size:12px;font-weight:500;color:var(--muted);display:flex;align-items:center;gap:11px;transition:color .2s,background .2s;user-select:none;text-align:left;min-height:44px;width:100%}
.tab:hover{color:var(--ink);background:var(--surface-3)}
.tab.on{color:var(--accent);background:var(--accent-soft);font-weight:650}
.tab[data-v="plat"]{margin-top:22px}
.tab-ink{position:absolute;left:0;top:0;width:3px;height:2px;background:var(--accent);border-radius:2px;pointer-events:none;will-change:transform,width,height}
.view{display:none} .view.on{display:block}

/* four-state values */
.v{font-family:var(--mono);cursor:pointer;border-bottom:1px dotted var(--faint);white-space:nowrap;transition:color .18s,border-color .18s}
.v:hover{border-bottom-color:var(--accent);color:var(--accent)}
.v .bdg{font-style:normal;font-size:9.5px;font-family:var(--sans);font-weight:600;margin-left:5px;padding:1.5px 6px;border-radius:var(--r);vertical-align:1px}
.v.m .bdg{background:var(--accent-soft);color:var(--accent)}
.v.a .bdg{background:var(--surface-3);color:var(--ink-2)}
.v.d .bdg{background:var(--ok-soft);color:var(--ok)}
.v.u .bdg{background:var(--warn-soft);color:var(--warn)}
.v.u{color:var(--warn)}

/* tables */
table{width:100%;border-collapse:collapse;font-size:12.8px}
th,td{border-bottom:1px solid var(--line-2);padding:9px 11px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:650;font-size:10.5px;font-family:var(--mono);text-transform:uppercase;letter-spacing:.07em;background:var(--surface-2)}
tbody tr{transition:background .15s} tbody tr:hover{background:var(--accent-soft)}
td.m{font-family:var(--mono)}
.cmp{table-layout:fixed}
.cmp th,.cmp td{padding:8px 9px}
.cmp th:first-child,.cmp td:first-child{width:10%}
.cmp td.m{font-size:11.3px;line-height:1.5;overflow-wrap:anywhere;word-break:break-word}

/* controls */
.demo-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:15px}
.btns{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.btn{border:1px solid var(--accent);border-radius:var(--r);padding:8px 16px;cursor:pointer;background:var(--accent);color:#fbfaf6;font-weight:650;font-size:13px;font-family:var(--sans);display:inline-flex;align-items:center;gap:7px;transition:background .18s,transform .18s var(--ease)}
.btn:hover{background:var(--accent-2);transform:translateY(-1px)}
.btn:active{transform:none}
.btn.sec{background:var(--surface);color:var(--ink-2);border:1px solid var(--line);font-weight:550}
.btn.sec:hover{border-color:var(--accent);color:var(--accent);background:var(--surface)}
.idx{font-family:var(--mono);font-size:12px;color:var(--muted);min-width:52px;text-align:center;background:var(--surface-2);border:1px solid var(--line-2);border-radius:var(--r);padding:5px 8px}

/* instrument readouts */
.heapbar{display:flex;height:46px;border-radius:var(--r);overflow:hidden;border:1px solid var(--line);background:var(--surface-3)}
.blk{flex:0 0 0%;opacity:0;height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;transition:flex-grow .55s var(--ease),opacity .4s,box-shadow .2s}
.blk:hover{box-shadow:inset 0 0 0 2px rgba(250,248,242,.5)}
.blk .lbl{font-family:var(--mono);font-size:10.5px;font-weight:600;color:#fbfaf6;white-space:nowrap;padding:0 5px}
.blbl{flex:0 0 0%;opacity:0;font-family:var(--mono);font-size:10px;color:var(--muted);text-align:center;overflow:hidden;white-space:nowrap;transition:flex-grow .55s var(--ease),opacity .4s;padding-top:5px}
.c-a{background:var(--bar-a)} .c-b{background:var(--bar-b)} .c-c{background:var(--accent-2)}
.c-idle{background:var(--idle)} .c-cur{background:var(--bar-cur)}
.cap{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin-top:9px}
.grid2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px}
.grid2>div{min-width:0}

/* empty + notes */
.empty{border:1px dashed var(--line);border-radius:var(--r);padding:24px;text-align:left;color:var(--muted);background:var(--surface-2)}
.empty b{color:var(--warn);font-size:15px;font-family:var(--serif)}
.snote{border:1px solid var(--line);border-left:3px solid var(--accent);background:var(--surface-2);border-radius:var(--r);padding:12px 15px;margin:11px 0;font-size:12.8px;color:var(--ink-2)}
.snote b{color:var(--accent)}

/* register map */
.bits{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:9px;margin:20px 0}
.bit{border:1px solid var(--line);border-radius:var(--r);padding:15px 4px;text-align:center;font-family:var(--mono);font-size:11px;background:var(--surface);transition:border-color .18s,background .18s;position:relative}
.bit:hover{border-color:var(--accent)}
.bit .bn{font-size:9px;color:var(--muted);display:block;margin-bottom:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bit .bv{font-size:25px;font-weight:500;color:var(--faint);line-height:1}
.bit .bit-pin{display:block;min-height:15px;margin-top:10px;color:var(--accent);font-size:9px}
.register-map{padding:22px;border:1px solid var(--line-2);border-radius:var(--r);background:var(--surface-2)}
.register-map .section-head{margin:0}
.map-legend{display:flex;gap:16px;align-items:center;flex-wrap:wrap;font-size:11px;color:var(--muted)}
.map-legend span{display:inline-flex;align-items:center;gap:6px}
.map-legend i{width:7px;height:7px;background:var(--accent-tint);border:1px solid var(--accent);border-radius:2px}
.map-legend i.unknown{background:var(--surface);border-color:var(--line)}
.bit.hi{border-color:var(--accent-tint);background:var(--accent-soft)}
.bit.hi::after{content:"";position:absolute;top:4px;right:4px;width:5px;height:5px;background:var(--accent)}
.bit.set{border-color:var(--accent);background:var(--accent-soft)}
.bit.set .bv{color:var(--accent)}
.bit{appearance:none;-webkit-appearance:none;cursor:pointer;width:100%;display:block;color:var(--ink);background:var(--surface)}
.bit.sel{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-tint)}
.bit.sel .bv{color:var(--accent)}
.bit:hover{border-color:var(--accent-tint)}
.bit.res{opacity:.55}
.map-legend i.set{background:var(--accent);border-color:var(--accent)}
.map-legend i.clear{background:var(--surface);border-color:var(--line)}
.reg-frames{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 18px}
.reg-frame-chip{border:1px solid var(--line);background:var(--surface);border-radius:var(--r);padding:5px 9px;font-family:var(--mono);font-size:10.5px;color:var(--ink-2);cursor:pointer;display:inline-flex;gap:6px;align-items:center;transition:border-color .18s,background .18s}
.reg-frame-chip b{font-weight:600;color:var(--ink)}
.reg-frame-chip.on{border-color:var(--accent);background:var(--accent-soft);color:var(--accent)}
.reg-frame-chip.on b{color:var(--accent)}
.reg-frame-chip:hover{border-color:var(--accent-tint)}
.reg-layout{display:grid;grid-template-columns:minmax(0,1.12fr) minmax(300px,.88fr);gap:20px;align-items:start;margin-top:18px}
.reg-layout .register-map{margin:0}
.reg-bits-foot{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-top:10px}
.bit-detail{border:1px solid var(--line);border-radius:var(--r);background:var(--surface);padding:18px;position:sticky;top:14px;min-width:0}
.bit-detail h4{font-family:var(--serif);font-size:17px;font-weight:700;margin:0;display:flex;align-items:center;gap:8px;flex-wrap:wrap;letter-spacing:.01em}
.bit-detail .bd-sub{font-family:var(--mono);font-size:10px;color:var(--faint);margin:4px 0 12px;letter-spacing:.05em}
.bit-detail dl{display:grid;grid-template-columns:86px minmax(0,1fr);gap:9px 12px;font-size:12px;margin:0}
.bit-detail dt{color:var(--muted);font-size:11px}
.bit-detail dd{margin:0;color:var(--ink-2);min-width:0;overflow-wrap:anywhere}
.bd-write{font-family:var(--mono);font-size:10.5px;border-top:1px dashed var(--line-2);padding:5px 0;line-height:1.5}
.bd-write:first-child{border-top:0}
.bit-hist{display:flex;gap:5px;flex-wrap:wrap}
.hist-chip{border:1px solid var(--line);background:var(--surface-2);border-radius:var(--r);padding:3px 6px;font-family:var(--mono);font-size:10px;color:var(--muted);cursor:pointer}
.hist-chip b{color:var(--ink);margin-left:4px}
.hist-chip.on{background:var(--accent-soft);border-color:var(--accent-tint);color:var(--accent)}
.hist-chip.sel{box-shadow:0 0 0 2px var(--accent-tint)}
.readout-bin{font-family:var(--mono);font-size:12px;color:var(--ink-2);letter-spacing:.06em;margin-top:6px;overflow-wrap:anywhere}

/* term cards */
.term{border:1px solid var(--line);border-radius:var(--r);padding:17px;margin-bottom:12px;background:var(--surface);transition:all .3s var(--ease)}
.term.lit{border-color:var(--accent);background:var(--accent-soft);box-shadow:0 0 0 3px var(--accent-tint)}
.term h3{font-size:13.5px;font-family:var(--mono);font-weight:650;margin-bottom:10px;color:var(--ink);display:flex;align-items:center;gap:8px}
.src{font-family:var(--mono);font-size:11.5px;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r);padding:6px 10px;cursor:pointer;display:inline-block;margin:3px 5px 3px 0;color:var(--ink-2);transition:all .18s}
.src:hover,.src.lit{border-color:var(--accent);background:var(--accent-soft);color:var(--accent)}
.src:hover{transform:translateY(-1px)}
.chip{display:inline-flex;align-items:center;gap:5px;font-family:var(--mono);font-size:11.5px;border:1px solid var(--line);border-radius:var(--r);padding:4px 10px;margin:3px 5px 3px 0;background:var(--surface);color:var(--ink-2);transition:all .18s}
.chip[data-jump]{cursor:pointer} .chip[data-jump]:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-soft);transform:translateY(-1px)}
.chip.lit{border-color:var(--accent);background:var(--accent-soft);color:var(--accent);box-shadow:0 0 0 3px var(--accent-tint)}

/* deep term cards */
.term-deep{padding:24px;margin-bottom:18px}
.term-deep>*{min-width:0}
.term-details{margin-top:20px;border-top:1px solid var(--line-2)}
.term-details>summary{cursor:pointer;padding-top:14px;font-size:12px;color:var(--accent);font-weight:600}
.term-detail-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0 24px}
.term-detail-grid>.srcrow,.term-detail-grid>.tadv{grid-column:1/-1}
.term-detail-grid .srcrow{margin-top:18px}
.term-detail-grid>*{min-width:0}
.term .thead{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:5px}
.term .thead h3{margin:0}
.srcrow{margin:4px 0 8px}
.tlead{font-size:13.3px;color:var(--ink-2);line-height:1.7;margin:6px 0 12px}
.tlead b{color:var(--accent);font-weight:650}
.tq{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);border-radius:var(--r);background:var(--surface-2);margin:12px 0 0}
.tq>div{padding:10px 13px 11px;border-right:1px solid var(--line-2);min-width:0}
.tq>div:last-child{border-right:none}
.tq .k{display:block;font-family:var(--mono);font-size:9.5px;letter-spacing:.07em;color:var(--muted);margin-bottom:4px}
.tq .big{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;font-family:var(--mono);font-size:15.5px;font-weight:700;color:var(--ink);line-height:1.35}
.tq .big em{font-style:normal;font-size:10.5px;font-weight:600;color:var(--muted)}
.tq .n{display:block;font-size:11.3px;color:var(--muted);line-height:1.6;margin-top:5px}
.tsec{margin-top:15px;padding-top:12px;border-top:1px solid var(--line-2)}
.tsec .hd{font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--accent);margin-bottom:8px}
.flow{list-style:none;padding:0;margin:0;counter-reset:fl}
.flow li{counter-increment:fl;position:relative;padding:0 0 9px 31px;font-size:12.8px;color:var(--ink-2);line-height:1.62}
.flow li::before{content:counter(fl,decimal-leading-zero);position:absolute;left:0;top:0;font-family:var(--mono);font-size:9.5px;font-weight:700;color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent-tint);border-radius:var(--r);padding:1px 4px}
.flow li::after{content:"";position:absolute;left:11px;top:20px;bottom:0;width:1px;background:var(--line-2)}
.flow li:last-child{padding-bottom:0} .flow li:last-child::after{display:none}
.flow code,.tlead code,.calc code,.kv code{font-family:var(--mono);font-size:11.3px;background:var(--surface-2);border:1px solid var(--line-2);border-radius:var(--r);padding:1px 5px;color:var(--ink)}
.flow b,.kv b{color:var(--ink);font-weight:650}
.kv{display:grid;grid-template-columns:auto 1fr;gap:6px 15px;margin:0;font-size:12.6px}
.kv dt{font-family:var(--mono);font-size:10.5px;color:var(--muted);white-space:nowrap;padding-top:1px}
.kv dd{margin:0;color:var(--ink-2);line-height:1.62}
.calc{font-family:var(--mono);font-size:11.6px;line-height:1.7;background:var(--surface-2);border:1px dashed var(--line);border-radius:var(--r);padding:9px 12px;color:var(--ink-2);margin:0 0 8px;overflow-wrap:anywhere}
.tadv{margin-top:14px;border-top:1px solid var(--line-2);padding-top:9px}
.tadv>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:10.5px;letter-spacing:.04em;color:var(--muted)}
.tadv>summary::-webkit-details-marker{display:none}
.tadv>summary::before{content:"+";color:var(--accent);font-weight:700;font-size:13px}
.tadv[open]>summary::before{content:"–"}
.tadv>summary:hover{color:var(--accent)}
.tadv .body{font-size:12.5px;color:var(--ink-2);line-height:1.7;margin-top:8px}
.tadv .body b{color:var(--accent)}

/* timeline */
.tl{display:flex;gap:5px;align-items:flex-end;height:52px;margin:11px 0}
.tl .pt{flex:1;background:var(--accent-tint);border:1px solid var(--accent-tint);border-radius:2px 2px 0 0;min-width:18px;position:relative;transition:opacity .3s}
.tl .gap{flex:0 0 28px;display:flex;align-items:center;justify-content:center;color:var(--warn);font-size:10px;font-family:var(--mono)}

/* legend */
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin-top:12px}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend .v{cursor:default;border-bottom:none}

/* range */
input[type=range]{-webkit-appearance:none;appearance:none;height:4px;border-radius:99px;background:var(--line);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:16px;height:16px;border-radius:var(--r);background:var(--accent);border:2px solid var(--surface);box-shadow:0 1px 4px rgba(27,30,33,.3);cursor:pointer}
input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:var(--r);background:var(--accent);border:2px solid var(--surface);cursor:pointer}
input[type=range]::-moz-range-track{height:4px;border-radius:99px;background:var(--line)}

/* marginalia provenance */
#scrim{position:fixed;inset:0;background:rgba(27,30,33,.3);opacity:0;pointer-events:none;transition:opacity .3s;z-index:49}
#scrim.on{opacity:1;pointer-events:auto}
#prov{position:fixed;right:0;top:0;height:100vh;width:350px;max-width:92vw;background:var(--surface);border-left:1px solid var(--line);padding:24px;box-shadow:-10px 0 34px rgba(27,30,33,.14);transform:translateX(102%);transition:transform .38s var(--ease);font-size:12.5px;z-index:50;overflow-y:auto}
#prov.on{transform:none}
#prov h4{font-family:var(--serif);font-size:16px;margin-bottom:15px;color:var(--accent);display:flex;align-items:center;gap:9px;font-weight:700}
#prov .row{display:flex;gap:10px;padding:8px 0;border-bottom:1px dotted var(--line)}
#prov .row b{font-family:var(--mono);min-width:82px;color:var(--muted);font-weight:600;font-size:11px}
#prov .row span{word-break:break-word;color:var(--ink-2)}
#prov .x{margin-left:auto;cursor:pointer;color:var(--muted);background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r);width:28px;height:28px;display:grid;place-items:center;transition:all .18s}
#prov .x:hover{color:var(--bad);border-color:#e0bdb8;background:var(--bad-soft)}

/* plain-language lede */
.plain{display:flex;gap:11px;align-items:flex-start;background:var(--accent-soft);border:1px solid var(--accent-tint);border-radius:var(--r);padding:12px 15px;margin:0 0 17px;font-size:13px;color:var(--ink-2);line-height:1.65}
.plain .ptag{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.04em;color:var(--accent);background:var(--surface);border:1px solid var(--accent-tint);border-radius:var(--r);padding:2px 7px;flex:0 0 auto;margin-top:2px}
.plain b{color:var(--accent);font-weight:650}

/* glossary term + tooltip */
.gl{border-bottom:1px dotted var(--accent-2);cursor:help;color:inherit;border-radius:2px;padding:0 1px;transition:background .15s,color .15s}
.gl:hover,.gl:focus-visible{background:var(--accent-soft);color:var(--accent)}
#glpop{position:fixed;z-index:90;max-width:302px;background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:var(--r);box-shadow:0 10px 34px rgba(27,30,33,.2);padding:12px 14px;font-size:12.8px;line-height:1.65;color:var(--ink-2);opacity:0;pointer-events:none;transform:translateY(4px);transition:opacity .18s,transform .18s}
#glpop.on{opacity:1;transform:none}
#glpop .gt{font-family:var(--mono);font-size:11.5px;font-weight:700;color:var(--accent);display:block;margin-bottom:5px}

/* modal overlays (import + glossary) */
#impwrap,#glwrap,#readwrap{position:fixed;inset:0;z-index:60;display:none;align-items:flex-start;justify-content:center;padding:38px 16px;background:rgba(27,30,33,.34);overflow-y:auto}
#impwrap.on,#glwrap.on,#readwrap.on{display:flex}
.imppanel,.glpanel{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);width:100%;padding:28px 30px;box-shadow:0 18px 60px rgba(27,30,33,.22);position:relative}
.imppanel{max-width:680px} .glpanel{max-width:680px}
.imp-x{position:absolute;top:18px;right:18px;cursor:pointer;color:var(--muted);background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r);width:30px;height:30px;display:grid;place-items:center;font-size:19px;line-height:1;transition:all .18s}
.imp-x:hover{color:var(--bad);border-color:#e0bdb8}
.imp-h{font-family:var(--serif);font-size:23px;font-weight:700;color:var(--ink);margin:0 0 6px;letter-spacing:-.01em}
.imp-lead{font-size:13.5px;color:var(--muted);line-height:1.6;margin:0 0 16px;max-width:60ch}
.imp-callout{background:var(--accent-soft);border:1px solid var(--accent-tint);border-radius:var(--r);padding:13px 15px;font-size:12.8px;color:var(--ink-2);line-height:1.65;margin-bottom:18px}
.imp-callout b{color:var(--accent)}
.imp-example{display:flex;align-items:center;gap:13px;flex-wrap:wrap;background:var(--surface-2);border:1px dashed var(--accent-tint);border-radius:var(--r);padding:13px 15px;margin-bottom:22px}
.imp-example .txt{font-size:12.8px;color:var(--ink-2);flex:1;min-width:190px;line-height:1.55}
.imp-example .txt b{color:var(--accent)}
.imp-step{font-family:var(--mono);font-size:11px;letter-spacing:.05em;color:var(--accent);margin:0 0 6px;display:flex;align-items:center;gap:9px}
.imp-step::after{content:"";flex:1;height:1px;background:var(--line)}
.imp-row{display:flex;gap:15px;align-items:flex-start;padding:15px 0;border-bottom:1px solid var(--line-2)}
.imp-row:last-of-type{border-bottom:none}
.imp-num{width:26px;height:26px;flex:0 0 auto;border-radius:50%;background:var(--accent);color:#fbfaf6;font-family:var(--mono);font-size:12px;font-weight:700;display:grid;place-items:center;margin-top:2px}
.imp-rowtxt{flex:1;min-width:0}
.imp-rowtitle{font-size:14px;font-weight:650;color:var(--ink);margin-bottom:3px}
.imp-rowtitle .ext{font-family:var(--mono);font-size:11px;color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent-tint);border-radius:var(--r);padding:1px 6px;margin-left:7px}
.imp-rowdesc{font-size:12.5px;color:var(--ink-2);line-height:1.55}
.imp-rowhint{font-size:11px;color:var(--muted);margin-top:5px;font-family:var(--mono);word-break:break-all;line-height:1.5}
.imp-rowfile{flex:0 0 auto;display:flex;flex-direction:column;align-items:flex-end;gap:7px;min-width:118px}
.imp-pick{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:7px;border:1px solid var(--accent);background:var(--accent-soft);color:var(--accent);border-radius:var(--r);padding:8px 14px;font-size:12.5px;font-weight:650;cursor:pointer;overflow:hidden;transition:all .18s;white-space:nowrap}
.imp-pick:hover{background:var(--accent-tint)}
.imp-pick:focus-within{outline:2px solid var(--accent);outline-offset:2px}
.imp-pick input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer;font-size:0}
.imp-pick.done{border-color:#bcd3ba;background:var(--ok-soft);color:var(--ok)}
.imp-chip{font-family:var(--mono);font-size:10.5px;color:var(--ok);background:var(--ok-soft);border:1px solid #bcd3ba;border-radius:var(--r);padding:2px 8px;max-width:158px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.imp-adv{margin-top:20px;border:1px solid var(--line);border-radius:var(--r);background:var(--surface-2)}
.imp-adv>summary{cursor:pointer;padding:12px 15px;font-size:13px;font-weight:650;color:var(--ink-2);list-style:none;display:flex;align-items:center;gap:9px}
.imp-adv>summary::-webkit-details-marker{display:none}
.imp-adv>summary::before{content:"+";font-family:var(--mono);color:var(--accent);font-weight:700;font-size:15px}
.imp-adv[open]>summary::before{content:"\2013"}
.imp-adv>summary:hover{color:var(--accent)}
.imp-advbody{padding:2px 15px 16px}
.imp-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px 18px;margin:10px 0}
.imp-field{display:flex;flex-direction:column;gap:5px;min-width:0}
.imp-field>label{font-size:12px;font-weight:600;color:var(--ink-2)}
.imp-field .fh{font-size:11px;color:var(--muted);line-height:1.5;font-weight:400}
.imp-field input[type=text],.imp-field select{font-family:var(--mono);font-size:12px;border:1px solid var(--line);border-radius:var(--r);padding:7px 9px;background:var(--surface);color:var(--ink);width:100%}
.imp-field input[type=number]{font-family:var(--mono);font-size:12px;border:1px solid var(--line);border-radius:var(--r);padding:7px 9px;background:var(--surface);color:var(--ink);width:100%}
.imp-field input[type=text]:focus,.imp-field select:focus,.imp-field input[type=number]:focus{outline:2px solid var(--accent);outline-offset:1px}
.imp-mini{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.imp-mini .imp-pick{padding:6px 11px;font-size:11.5px}
.imp-actions{display:flex;gap:9px;flex-wrap:wrap;align-items:center;margin-top:22px;padding-top:18px;border-top:1px solid var(--line)}
.btn.big{padding:11px 22px;font-size:14px}
#impstatus{font-size:12.8px;margin-top:14px;white-space:pre-wrap;word-break:break-word;color:var(--ink-2);line-height:1.7;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px}
#impstatus:empty{display:none}
#impstatus.err{color:var(--bad);border-color:#e0bdb8;background:var(--bad-soft)}
#impstatus.ok{border-left:3px solid var(--ok)}
.readpanel{max-width:620px}
.readpanel .imp-grid{grid-template-columns:1.3fr .6fr .8fr}
.read-status{border:1px solid var(--line);background:var(--surface-2);border-radius:var(--r);padding:12px 14px;font-size:12.5px;line-height:1.7;color:var(--ink-2);margin:14px 0;white-space:pre-line;overflow-wrap:anywhere}
.read-status.ok{border-left:3px solid var(--ok)}
.read-status.err{border-left:3px solid var(--bad);background:var(--bad-soft);color:var(--bad);border-color:#e0bdb8}
.read-status.busy{border-left:3px solid var(--accent)}
.read-cmd{display:none;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px;font-size:11.5px;line-height:1.7;color:var(--ink-2);white-space:pre-wrap;overflow-wrap:anywhere;margin:0 0 14px}
.read-cmd.on{display:block}
.read-note{font-size:12px;color:var(--muted);line-height:1.65;margin:12px 0 0}
/* glossary dictionary */
.gl-search{width:100%;font-family:var(--sans);font-size:13px;border:1px solid var(--line);border-radius:var(--r);padding:9px 12px;background:var(--surface-2);color:var(--ink);margin:14px 0 4px}
.gl-search:focus{outline:2px solid var(--accent);outline-offset:1px}
.gl-cat{font-family:var(--mono);font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--accent);margin:16px 0 6px;border-bottom:1px dotted var(--line);padding-bottom:5px}
.gl-item{padding:9px 0;border-bottom:1px solid var(--line-2)}
.gl-item:last-child{border-bottom:none}
.gl-item .t{font-family:var(--mono);font-size:12.5px;font-weight:700;color:var(--ink);display:block;margin-bottom:3px}
.gl-item .p{font-size:12.8px;color:var(--ink-2);line-height:1.6}
.gl-empty{color:var(--muted);font-size:13px;padding:20px 0;text-align:center}
.mast-actions{display:flex;gap:9px;flex-wrap:wrap;align-items:center}
.mast-actions .btn{font-size:12px;padding:7px 12px;min-height:36px}
.project-panel{margin-top:18px;border:1px solid var(--line);background:var(--surface);border-radius:var(--r)}
.project-panel>summary{display:flex;align-items:center;gap:14px;padding:12px 16px;cursor:pointer;list-style:none;flex-wrap:wrap}
.project-panel>summary::-webkit-details-marker{display:none}
.project-name{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:11px;min-width:0;overflow-wrap:anywhere}
.project-name .ic{color:var(--accent);width:18px;height:18px}
.project-name b{font-weight:600}
.project-detail-label{margin-left:auto;font-size:10px;color:var(--muted);white-space:nowrap}
.project-detail-label::after{content:' +';color:var(--accent)}
.project-panel[open] .project-detail-label::after{content:' −'}
.project-body{border-top:1px solid var(--line-2);padding:0 16px 16px}
.project-body .spec{margin-bottom:14px}
.status-strip{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.status-strip .tag{font-size:10px;padding:0;border:0;background:transparent}
.status-strip .tag::before{border-radius:50%;width:5px;height:5px}
.status-strip .tag+.tag{border-left:1px solid var(--line-2);padding-left:14px}
.identity-panel{border:1px solid var(--line);border-radius:5px;background:var(--surface);min-width:0;font-size:12px}
.identity-panel>summary{display:flex;align-items:center;gap:10px;flex-wrap:wrap;cursor:pointer;padding:11px 14px;list-style:none}
.identity-panel>summary::-webkit-details-marker{display:none}
.identity-label{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.identity-label .seal{width:22px;height:22px}
.identity-label .tag{padding:2px 7px}
.identity-state{color:var(--warn);font-size:11px;line-height:1.5}
.identity-state.verified{color:var(--ok)}
.identity-hint{margin-left:auto;font-size:10px;color:var(--muted);white-space:nowrap}
.identity-hint::after{content:" +";color:var(--accent)}
.identity-panel[open] .identity-hint::after{content:" −"}
.identity-body{border-top:1px solid var(--line-2);padding:16px;overflow-wrap:anywhere}
.identity-body .plain{margin-bottom:12px}
.workbench{display:grid;grid-template-columns:214px minmax(0,1fr);align-items:start;min-height:100vh;position:relative}
.workbench-nav{position:sticky;top:0;height:100vh;min-width:0;display:flex;flex-direction:column;border-right:1px solid var(--line);padding:22px 15px;background:var(--surface);overflow-y:auto}
.nav-head{display:flex;align-items:center;justify-content:space-between;gap:8px;min-height:36px;margin:0 8px 10px}
.nav-label{font-size:10px;letter-spacing:.12em;color:var(--muted);min-width:0}
.nav-toggle{display:grid;place-items:center;flex:0 0 28px;width:28px;height:28px;padding:0;border:0;border-radius:4px;background:transparent;color:var(--muted);cursor:pointer}
.nav-toggle:hover{color:var(--accent);background:var(--accent-soft)}
.nav-toggle .ic{width:17px;height:17px}
.nav-chevron{transform-origin:15.5px 12px;transition:transform .18s var(--ease)}
.tab-icon{display:inline-flex;align-items:center;justify-content:center}
.nav-note{font-size:10px;color:var(--muted);line-height:1.9;margin:auto 8px 0;padding-top:34px}
.nav-note b{display:flex;align-items:center;gap:7px;color:var(--ink-2);font-size:11px;font-weight:500;margin-bottom:6px}
.nav-note b::before{content:'';width:5px;height:5px;border-radius:50%;background:var(--ok)}
.nav-note p{padding-top:8px;margin-top:18px;border-top:1px solid var(--line-2);font-family:var(--mono);font-size:9px;letter-spacing:.06em}
.workbench-main{min-width:0;width:100%;max-width:1536px;margin:0 auto;padding:0 clamp(24px,3.2vw,52px) 28px}
.workbench-main .view{scroll-margin-top:24px}
.workbench-main .note,.workbench-main .src,.workbench-main .chip,.workbench-main .v{overflow-wrap:anywhere;word-break:normal;white-space:normal}
.workbench-main .src,.workbench-main .chip{max-width:100%}
.readout-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;margin:0 0 24px}
.readout{padding:0 22px 0 0;min-width:0}
.readout+.readout{border-left:1px solid var(--line-2);padding:0 0 0 24px}
.readout-label{font-size:10px;color:var(--muted);margin-bottom:8px;font-family:var(--mono);letter-spacing:.08em}
.readout-value{font-size:26px;line-height:1.5;font-weight:500;letter-spacing:-.025em}
.readout .note{margin-top:6px;font-size:11px}
.snapshot-empty{text-align:center;padding:42px 24px 38px;background:var(--surface)}
.empty-symbol{width:66px;height:66px;border:1px solid var(--accent-tint);background:var(--accent-soft);color:var(--accent);border-radius:50%;display:grid;place-items:center;margin:0 auto 20px;outline:1px solid var(--line-2);outline-offset:5px}
.empty-symbol .ic{width:30px;height:30px}
.snapshot-empty h3{font-family:var(--serif);font-size:18px;font-weight:700;margin-bottom:10px}
.snapshot-empty>p{font-size:12px;color:var(--muted);max-width:48ch;margin:0 auto;line-height:1.9}
.snapshot-empty .btns{justify-content:center;margin:22px 0 0}
.snapshot-empty .btn{font-size:12px}
.snapshot-empty .empty-metrics{display:grid;grid-template-columns:repeat(3,1fr);margin:30px auto 0;max-width:580px;border-top:1px solid var(--line-2);padding-top:24px}
.empty-metrics>div+div{border-left:1px solid var(--line-2)}
.empty-metrics dt{font-size:10px;color:var(--muted);margin-bottom:6px}
.empty-metrics dd{font-family:var(--mono);color:var(--faint);font-size:13px}
.sample-log{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:0 18px;margin-bottom:20px;font-size:12px}
.sample-log>summary{cursor:pointer;padding:14px 0;color:var(--warn);font-weight:500}
.sample-log .note{padding:0 0 16px;white-space:pre-wrap;overflow-wrap:anywhere}
.current-task{padding:16px 20px;border:1px solid var(--accent-tint);border-radius:var(--r);background:var(--accent-soft);margin:18px 0 24px;font-size:12px}
.scheduler-lists>div{border:1px solid var(--line-2);padding:20px;border-radius:var(--r);background:var(--surface-2)}
.scheduler-lists .heapbar{margin-top:16px;height:62px}
.scheduler-timeline{padding-top:20px;border-top:1px solid var(--line-2);margin-top:24px}
.swim-summary{display:flex;justify-content:space-between;align-items:baseline;gap:14px;flex-wrap:wrap;margin:10px 0 12px}
.swim-summary b{font-size:13px;color:var(--ink)}
.swim-summary .note{margin-left:10px}
.swim-wrap{overflow-x:auto;border:1px solid var(--line-2);border-radius:var(--r);background:var(--surface);margin-bottom:10px}
.swim{width:100%;border-collapse:separate;border-spacing:0;font-size:11px;min-width:540px;table-layout:fixed}
.swim th:first-child{width:150px}
.swim th,.swim td{border-bottom:1px solid var(--line-2);padding:0;text-align:center;vertical-align:middle}
.swim thead th{background:var(--surface-2);font-family:var(--mono);font-size:9.5px;color:var(--muted);letter-spacing:0;text-transform:none;padding:6px 8px;white-space:nowrap}
.swim thead th:first-child{position:sticky;left:0;z-index:2;text-align:left}
.swim thead th b{display:block;color:var(--ink);font-size:10.5px;font-weight:650}
.swim thead th span{display:block;font-size:9px;color:var(--faint)}
.swim thead th.fbad{background:var(--bad-soft);color:var(--bad)}
.swim thead th.fbad span{color:var(--bad)}
.swim thead th.on,.swim td.cell.on{box-shadow:inset 0 0 0 2px var(--accent)}
.swim tbody th{position:sticky;left:0;z-index:1;background:var(--surface);text-align:left;padding:7px 12px;min-width:128px;border-right:1px solid var(--line-2)}
.swim tbody th b{display:block;font-size:11.5px;color:var(--ink);font-family:var(--sans)}
.swim tbody th span{display:block;font-family:var(--mono);font-size:9px;color:var(--faint);white-space:nowrap}
.swim td.cell{height:42px;border-left:1px solid var(--line-2);cursor:pointer;transition:filter .15s}
.swim td.cell:hover{filter:brightness(.97)}
.swim .st{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;height:100%;font-family:var(--mono);font-size:10px;line-height:1.25}
.swim .st em{font-style:normal;font-size:8.5px;opacity:.8}
.swim .s-run{background:var(--ok-soft);color:var(--ok);box-shadow:inset 3px 0 0 var(--ok)}
.swim .s-ready{background:var(--accent-soft);color:var(--accent)}
.swim .s-delay{background:var(--warn-soft);color:var(--warn)}
.swim .s-absent{background:var(--surface);color:var(--faint)}
.swim .s-bad{background:var(--bad-soft);color:var(--bad)}
.swim-legend{display:flex;gap:14px;flex-wrap:wrap;font-size:10.5px;color:var(--muted);margin:9px 0 8px}
.swim-legend span{display:inline-flex;align-items:center;gap:6px}
.swim-legend i{width:10px;height:10px;border-radius:2px;display:inline-block;flex:0 0 auto}
.swim-legend .i-run{background:var(--ok-soft);border-left:3px solid var(--ok)}
.swim-legend .i-ready{background:var(--accent-soft);border:1px solid var(--accent-tint)}
.swim-legend .i-delay{background:var(--warn-soft);border:1px solid #e6d3a4}
.swim-legend .i-absent{background:var(--surface);border:1px dashed var(--faint)}
.swim-legend .i-bad{background:var(--bad-soft);border:1px solid var(--bad)}
.table-scroll{width:100%;overflow-x:auto;border:1px solid var(--line-2);border-radius:4px;margin-top:14px}
.table-scroll .pin-table{min-width:600px;table-layout:fixed}
.pin-table th:nth-child(1){width:14%}.pin-table th:nth-child(2){width:20%}.pin-table th:nth-child(3){width:21%}
.pin-table td{overflow-wrap:anywhere}
.pin-table tr.pin-other{opacity:.65}
.table-scroll .cmp{min-width:860px}
.cmp th:first-child,.cmp td:first-child{position:sticky;left:0;background:var(--surface-2);z-index:1}
.replay-layout.on{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:0 20px;align-items:start}
.replay-layout>.view-head{grid-column:1/-1}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none}
.replay-empty{font-size:12px;color:var(--warn);padding-top:14px}
input[type=range]:focus-visible{outline:2px solid var(--accent);outline-offset:6px}
.replay-settings{padding:16px;border:1px solid var(--line-2);border-radius:4px;background:var(--surface-2);margin:18px 0}
.replay-settings label{display:block;font-size:12px;font-weight:600;color:var(--ink-2)}
.replay-range{display:flex;align-items:center;gap:12px;margin-top:12px}
.replay-range input{flex:1;min-width:0}
.replay-range .chip{margin:0;flex-shrink:0}
.delivery-note{line-height:1.8}
.delivery-item{display:flex;align-items:center;gap:9px;font-size:12px;color:var(--ink-2);margin-top:16px}
.delivery-item .ic{color:var(--ok)}
.mapping-details{padding:18px 24px}
.mapping-details>summary{cursor:pointer;display:flex;align-items:center;gap:10px;list-style:none;font-size:13px}
.mapping-details>summary::-webkit-details-marker{display:none}
.mapping-details>summary::after{content:'+';margin-left:auto;font:16px var(--mono);color:var(--accent)}
.mapping-details[open]>summary::after{content:'−'}
.mapping-details>summary .note{font-size:10px}
.data-contract{border-top:1px solid var(--line);margin-top:6px;font-size:12px;color:var(--muted)}
.data-contract>summary{cursor:pointer;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:14px 0;list-style:none}
.data-contract>summary::after{content:"+";color:var(--accent)}
.data-contract[open]>summary::after{content:"−"}
.data-contract>summary::-webkit-details-marker{display:none}
.data-contract .legend{padding-bottom:16px;gap:12px 18px}
.study-nav{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:22px;padding-bottom:14px;border-bottom:1px solid var(--line)}
.study-nav button{font:12px var(--sans);padding:9px 16px;min-height:40px;border:1px solid transparent;border-radius:var(--r);background:transparent;color:var(--muted);cursor:pointer}
.study-nav button[aria-pressed="true"]{color:var(--accent);border-color:var(--accent-tint);background:var(--accent-soft);font-weight:650}
.study-lessons{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px}
.study-lesson{padding:17px 20px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);text-align:left;cursor:pointer;color:var(--ink);font-family:var(--sans);min-width:0}
.study-lesson[aria-pressed="true"]{border-color:var(--accent);box-shadow:inset 3px 0 var(--accent)}
.study-lesson b{display:block;font-family:var(--serif);font-size:16px;margin:5px 0}
.study-lesson span{font-size:11px;color:var(--muted)}
.study-layout{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(240px,.7fr);gap:20px;align-items:start}
.study-layout>*{min-width:0}
.study-step{font:10px var(--mono);color:var(--accent);letter-spacing:.12em;display:block;margin-bottom:10px}
.study-question h3{font-family:var(--serif);font-size:20px;margin-bottom:10px}
.study-question fieldset{border:0;margin:20px 0}
.study-question legend{font-size:12px;color:var(--muted);margin-bottom:10px}
.study-choice{display:flex;align-items:flex-start;gap:10px;padding:12px;border:1px solid var(--line-2);border-radius:var(--r);margin:8px 0;font-size:12px;cursor:pointer;line-height:1.65}
.study-choice:has(input:checked){border-color:var(--accent);background:var(--accent-soft)}
.study-choice input{accent-color:var(--accent);margin-top:4px;flex-shrink:0}
.study-select{display:block;font:11px var(--mono);width:100%;margin-top:8px;padding:9px;border:1px solid var(--line);background:var(--surface);color:var(--ink);min-width:0;max-width:100%}
.study-feedback{margin-top:20px;padding:16px;border:1px solid var(--accent-tint);border-left:3px solid var(--accent);background:var(--accent-soft);font-size:12px;line-height:1.85}
.study-feedback b{display:block;color:var(--accent);margin-bottom:6px}
.study-feedback.agree{border-color:#bcd3ba;border-left-color:var(--ok);background:var(--ok-soft)}
.study-feedback.agree b{color:var(--ok)}
.study-evidence>summary{cursor:pointer;font-size:13px;color:var(--accent);font-weight:600}
.study-evidence dl{margin:16px 0 0}
.study-evidence dt{font-size:10px;color:var(--muted);margin-top:15px}
.study-evidence dd{font-size:12px;margin-top:4px;overflow-wrap:anywhere}
.study-evidence .btns{margin-top:20px}
.study-next{padding-left:18px;margin-top:14px;font-size:12px;color:var(--ink-2);line-height:1.85}
.study-next li+li{margin-top:10px}
.study-status{font-size:12px;color:var(--muted);margin-bottom:18px;white-space:pre-wrap;overflow-wrap:anywhere}
.study-status:empty{display:none}
.study-status.error{color:var(--bad)}
.compare-slots{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.compare-slot{min-width:0}
.compare-slot h3{font-family:var(--serif);font-size:19px;margin:4px 0 12px}
.compare-slot .btn{font-size:11px;padding:7px 10px;min-height:38px}
.compare-file{position:relative;overflow:hidden;cursor:pointer}
.compare-file input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%}
.compare-file:focus-within{outline:2px solid var(--accent);outline-offset:2px}
.compare-meta{font-size:11px;line-height:1.9;overflow-wrap:anywhere;margin:12px 0 18px;color:var(--muted)}
.compare-table{table-layout:fixed;min-width:650px}
.compare-table th:first-child{width:16%}.compare-table th:last-child{width:14%}
.compare-table td{overflow-wrap:anywhere;font-size:12px;line-height:1.8}
.compare-table tr.changed{background:var(--accent-soft)}
.compare-table .compare-source{display:block;font:10px var(--mono);color:var(--muted);margin-top:6px}
.diagnosis-list{list-style:none;margin:14px 0;padding:0}
.diagnosis-list li{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:12px 0;border-bottom:1px solid var(--line-2);font-size:12px}
.diagnosis-log{font:11px/1.8 var(--mono);white-space:pre-wrap;overflow-wrap:anywhere;margin-top:15px}
@media(max-width:1100px){
.study-layout{grid-template-columns:1fr}
.term-detail-grid{grid-template-columns:1fr}
.replay-layout.on{grid-template-columns:1fr}
.project-panel>summary{gap:10px 16px}
}
@media(min-width:901px){
.workbench.is-nav-collapsed{grid-template-columns:72px minmax(0,1fr)}
.is-nav-collapsed .workbench-nav{padding-left:12px;padding-right:12px}
.is-nav-collapsed .brand{padding-left:9px;padding-right:0}
.is-nav-collapsed .nav-head{justify-content:center;margin-left:0;margin-right:0}
.is-nav-collapsed .nav-label,.is-nav-collapsed .nav-note,.is-nav-collapsed .tab-label,.is-nav-collapsed .brand-text{display:none}
.is-nav-collapsed .tab{justify-content:center;padding:13px 8px}
.is-nav-collapsed .nav-chevron{transform:rotate(180deg)}
}
@media(max-width:900px){
.workbench{grid-template-columns:1fr}
.workbench-nav{top:0;z-index:30;height:auto;border-right:none;padding:0 18px;overflow:visible;border-bottom:1px solid var(--line)}
.brand,.nav-head,.nav-note{display:none}
.tabs{flex-direction:row;gap:4px;overflow-x:auto;flex-wrap:nowrap;padding:8px 0}
.tab{flex:0 0 auto;width:auto;white-space:nowrap;padding:10px 12px}
.tab[data-v="plat"]{margin-top:0}
.workbench-main{padding:0 24px 24px}
.masthead{min-height:66px;padding:14px 0}
.view-head{margin-top:24px}
}
@media(max-width:760px){
.study-lessons,.compare-slots{grid-template-columns:1fr}
.study-lesson{padding:14px 16px}
.study-nav{gap:2px}
.study-nav button{padding:10px 12px}
.study-question h3{font-size:18px}
.imp-grid{grid-template-columns:1fr}
.readpanel .imp-grid{grid-template-columns:1fr}
.imppanel,.glpanel{padding:22px 18px}
.imp-row{flex-wrap:wrap}
.imp-rowfile{flex-direction:row;align-items:center;width:100%;min-width:0;margin-top:9px;padding-left:41px}
.imp-chip{max-width:46vw}
#glpop{max-width:calc(100vw - 24px)}
.workbench-main{padding:0 16px 24px}
.masthead{gap:12px;flex-wrap:wrap;padding:14px 0}
.workspace-label{font-size:11px}
.mast-actions .btn{min-height:40px}
.project-panel>summary{padding:12px;gap:10px}
.project-name{font-size:10px}
.status-strip{order:3;flex-basis:100%;gap:10px}
.status-strip .tag+.tag{padding-left:10px}
.view-head{margin:24px 0 18px;gap:12px}
.view-head h2{font-size:23px}
.view-index{font-size:9px}
.register-map{padding:14px}
.register-map .section-head{align-items:flex-start;flex-direction:column;gap:8px}
.reg-layout{grid-template-columns:1fr}
.bit-detail{position:static}
.bits{gap:7px}
.bit{padding:12px 3px}
.bit .bv{font-size:22px}
.snapshot-empty{padding:30px 16px}
.swim{min-width:480px}
.swim th:first-child{width:104px}
.swim tbody th{min-width:96px;padding:6px 8px}
.swim td.cell{height:38px}
.swim-summary .note{margin-left:0;display:block}
.snapshot-empty h3{font-size:16px}
.snapshot-empty .empty-metrics{margin-top:24px}
.view-foot{align-items:flex-start;flex-direction:column;gap:5px}
.tab-icon .ic{width:16px!important;height:16px!important}
.scheduler-lists>div{padding:16px}
.spec{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 0;padding:12px 0}
.spec .row{padding:0 12px}
.spec .row:nth-child(odd){border-left:none;padding-left:0}
.identity-panel>summary{gap:7px;padding:10px 12px}
.identity-state{flex-basis:100%;order:3}
.identity-hint{font-size:9px}
.readout-grid{gap:16px;grid-template-columns:1fr 1fr}
.readout{padding:0}
.readout+.readout{padding-left:16px}
.readout-value{font-size:18px}
.readout-label{font-size:9px;letter-spacing:0}
.term-deep{padding:18px}
.data-contract>summary{font-size:11px}
.grid2{grid-template-columns:1fr}
.bits{grid-template-columns:repeat(4,1fr)}
.card{padding:18px}
#prov{width:100vw;max-width:100vw}
.tabs{overflow-x:auto;flex-wrap:nowrap}
.tab{padding:12px 14px 10px;white-space:nowrap}
.cmp{table-layout:auto;min-width:680px}
.tq{grid-template-columns:1fr}
.tq>div{border-right:none;border-bottom:1px solid var(--line-2)}
.tq>div:last-child{border-bottom:none}
.kv{grid-template-columns:1fr;gap:2px}
.kv dt{padding-top:5px}
}
@media(prefers-reduced-motion:reduce){
*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}
}

/* ===== 介绍页（首页） ===== */
body.landing-on{overflow:hidden}
#landing{position:fixed;inset:0;z-index:70;display:grid;grid-template-columns:minmax(0,1.06fr) minmax(0,.94fr);grid-template-rows:1fr auto;background:var(--paper);overflow:hidden}
#landing[hidden]{display:none}
#ldgrid{position:absolute;inset:0;pointer-events:none;opacity:.5;-webkit-mask-image:radial-gradient(120% 100% at 62% 38%,#000 45%,transparent 100%);mask-image:radial-gradient(120% 100% at 62% 38%,#000 45%,transparent 100%)}
.ld-rail{position:absolute;top:50%;transform:translateY(-50%);writing-mode:vertical-rl;font-family:var(--mono);font-size:9px;letter-spacing:.34em;color:var(--faint);user-select:none}
.ld-rail.l{left:16px;rotate:180deg}
.ld-rail.r{right:16px}
.ld-main{grid-row:1;grid-column:1;display:flex;flex-direction:column;justify-content:center;padding:clamp(26px,5vw,72px);max-width:780px;position:relative;z-index:2}
.ld-kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;color:var(--accent);display:flex;align-items:center;gap:9px;margin-bottom:22px}
.ld-dot{width:7px;height:7px;border-radius:50%;background:var(--accent);animation:ldpulse 2.2s infinite;flex:0 0 auto}
@keyframes ldpulse{0%{box-shadow:0 0 0 0 var(--accent-tint)}70%{box-shadow:0 0 0 9px rgba(20,64,107,0)}100%{box-shadow:0 0 0 0 rgba(20,64,107,0)}}
.ld-title{display:block;font-family:var(--serif);font-size:clamp(46px,7vw,96px);line-height:.95;letter-spacing:-.03em;font-weight:700;margin:0}
.ld-title .ld-word{display:inline-block;overflow:hidden;vertical-align:top;white-space:nowrap}
.ld-title .ld-word + .ld-word{margin-left:.06em}
.ld-word.accent{color:var(--accent)}
.ld-word .ch{display:inline-block;will-change:transform}
.ld-zh{display:block;font-family:var(--serif);font-weight:400;font-size:clamp(15px,1.6vw,20px);letter-spacing:.3em;color:var(--muted);margin-top:16px}
.ld-manifesto{font-family:var(--serif);font-size:clamp(17px,2vw,23px);color:var(--ink);margin:26px 0 0;letter-spacing:.02em}
.ld-sub{color:var(--muted);font-size:13.5px;line-height:1.85;max-width:47ch;margin:12px 0 0}
.ld-actions{display:flex;align-items:center;gap:18px;margin-top:30px;flex-wrap:wrap}
.ld-cta{position:relative;display:inline-flex;align-items:center;gap:12px;font-size:14px;font-weight:650;letter-spacing:.03em;color:#fff;background:var(--accent);border:1px solid var(--accent);padding:15px 24px;border-radius:var(--r);cursor:pointer;will-change:transform}
.ld-cta:hover{background:var(--accent-2)}
.ld-cta .ic{width:17px;height:17px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.ld-cta-ring{position:absolute;inset:-4px;border:1px solid var(--accent);border-radius:calc(var(--r) + 3px);opacity:0;pointer-events:none}
.ld-hint{font-family:var(--mono);font-size:10.5px;color:var(--faint);letter-spacing:.06em}
.ld-meta{display:flex;gap:24px;flex-wrap:wrap;margin-top:36px;padding-top:18px;border-top:1px solid var(--line);font-size:11px;color:var(--muted)}
.ld-meta span{display:flex;flex-direction:column;gap:3px;min-width:128px}
.ld-meta b{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;color:var(--ink-2);font-weight:600}
.ld-build{margin-top:16px;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;color:var(--faint)}
.ld-stage{--line:rgba(168,196,213,.16);--accent:#95cddd;--accent-tint:rgba(149,205,221,.2);--muted:#a5b8c3;--faint:#748d9d;--surface:#192c3a;grid-row:1;grid-column:2;position:relative;min-width:0;margin:24px 24px 24px 0;display:grid;place-items:center;perspective:900px;overflow:hidden;border:1px solid rgba(52,79,95,.7);border-radius:16px;background:radial-gradient(ellipse at 40% 30%,#243e50 0,#142936 42%,#091722 88%);box-shadow:0 20px 45px -28px rgba(8,22,32,.65),inset 0 1px rgba(211,231,242,.08)}
.ld-stage::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.14;background-image:linear-gradient(rgba(138,178,202,.16) 1px,transparent 1px),linear-gradient(90deg,rgba(138,178,202,.16) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(#000,transparent 78%)}
#ldgl{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab;touch-action:none}
#ldgl:active{cursor:grabbing}
.ld-zoom{position:absolute;right:22px;bottom:54px;display:none;gap:7px;z-index:3}
.ld-stage.gl-ok .ld-zoom{display:flex}
.ld-zoom button{font-family:var(--mono);font-size:11px;line-height:1;color:#c5d5dd;background:rgba(29,51,66,.85);border:1px solid var(--line);border-radius:5px;min-width:34px;height:34px;padding:0 10px;cursor:pointer;box-shadow:inset 0 1px rgba(217,236,247,.04)}
.ld-zoom button:hover{color:var(--accent);border-color:var(--accent)}
.ld-stage.gl-ok .ld-scope{display:none}
.ld-q{position:absolute;left:66%;top:22%;font-family:var(--mono);font-size:12px;color:var(--faint);display:none;pointer-events:none;animation:ldq 7s ease-in-out infinite}
.ld-stage.gl-ok .ld-q{display:none}
@keyframes ldq{0%,100%{opacity:.28}50%{opacity:.85}}
.ld-stage-tag{position:absolute;font-family:var(--mono);font-size:8.5px;letter-spacing:.16em;color:var(--faint);z-index:2}
.ld-stage-tag.tl{left:12px;top:12px}
.ld-stage-tag.tr{right:12px;top:12px}
.ld-ruler{position:absolute;top:44px;bottom:104px;width:12px;z-index:2;opacity:.6;background-image:repeating-linear-gradient(180deg,var(--line) 0 1px,transparent 1px 9px)}
.ld-ruler.l{left:0;border-right:1px solid var(--line)}
.ld-ruler.r{right:0;border-left:1px solid var(--line)}
.ld-scope{position:relative;width:min(76%,520px);aspect-ratio:1;z-index:1}
#ldsvg{width:100%;height:100%;overflow:visible}
.ld-ring-o{fill:none;stroke:var(--line);stroke-width:1}
.ld-ring-d{fill:none;stroke:var(--accent-tint);stroke-width:1.2;stroke-dasharray:2 8}
.ld-ring-i{fill:none;stroke:var(--accent-tint);stroke-width:1}
.ld-ticks line{stroke:var(--line);stroke-width:1}
.ld-ticks line.mj{stroke:var(--accent);opacity:.5}
.ld-node{fill:var(--accent);opacity:.8}
.ld-node.b{fill:var(--accent-2);opacity:.5}
.ld-cross{stroke:var(--accent);stroke-width:1;opacity:.45}
.ld-chip{fill:var(--surface);stroke:var(--accent);stroke-width:1.5;cursor:pointer;transition:stroke .25s,filter .25s}
.ld-chip:hover{stroke:var(--accent-2);filter:drop-shadow(0 0 7px var(--accent-tint))}
.ld-pins line{stroke:var(--line);stroke-width:3;stroke-linecap:round}
.ld-pins line.mj{stroke:var(--accent);opacity:.6}
.ld-core{fill:var(--accent)}
.ld-hit{fill:transparent;cursor:pointer}
.ld-angles text{font-family:var(--mono);font-size:9px;letter-spacing:.14em;fill:var(--faint)}
.ld-secret{font-family:var(--mono);font-size:11px;fill:var(--faint)}
.ld-sweep{position:absolute;inset:8.5%;border-radius:50%;pointer-events:none;background:conic-gradient(from 0deg,transparent 0 74%,rgba(20,64,107,.05) 90%,rgba(20,64,107,.12) 97.5%,transparent 100%);animation:ldsweep 10s linear infinite}
@keyframes ldsweep{to{rotate:360deg}}
.ld-tag{position:absolute;display:inline-flex;align-items:center;gap:7px;font-family:var(--mono);font-size:8.5px;letter-spacing:.18em;color:#b1c5d1;padding:6px 9px;border:1px solid var(--line);border-radius:3px;background:rgba(14,32,44,.72);z-index:2;pointer-events:none}
.ld-tag i{width:4px;height:4px;border-radius:50%;background:var(--accent);flex:0 0 auto}
.ld-tag.t1{right:11%;top:15%}
.ld-tag.t2{left:9%;top:29%}
.ld-tag.t3{right:8%;bottom:27%}
.ld-tag.t4{left:11%;bottom:15%}
.ld-wave{position:absolute;left:24px;right:168px;bottom:54px;height:26px;width:calc(100% - 192px);z-index:2;opacity:.22;pointer-events:none}
.ld-wave polyline{fill:none;stroke:var(--accent);stroke-width:1.1;stroke-dasharray:6 5;animation:ldwave 3.4s linear infinite}
@keyframes ldwave{to{stroke-dashoffset:-44}}
.ld-stage-foot{position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:space-between;gap:10px;padding:9px 14px;border-top:1px solid var(--line);font-family:var(--mono);font-size:8.5px;letter-spacing:.14em;color:var(--faint);z-index:2}
.egg-trigger{align-self:flex-start;display:inline-flex;align-items:center;gap:10px;margin-top:20px;padding:7px 0;font-family:var(--mono);font-size:10px;letter-spacing:.1em;border:0;border-bottom:1px dashed var(--line);color:var(--muted);background:none;cursor:pointer}
.egg-trigger:hover{color:var(--accent);border-color:var(--accent)}
.egg-trigger span{font-size:9px;border:1px solid var(--line);border-radius:3px;padding:2px 6px;color:var(--accent)}
.egg-dialog{--egg-ink:#dce7e7;--egg-muted:#9eb2b7;--egg-line:#314851;--egg-accent:#91dfce;position:fixed;inset:0;margin:auto;width:min(1160px,calc(100vw - 40px));max-width:none;max-height:calc(100dvh - 40px);padding:0;border:1px solid #465e64;border-radius:14px;background:#101f28;color:var(--egg-ink);box-shadow:0 32px 100px #0008;overflow:auto}
.egg-dialog::backdrop{background:rgba(4,15,23,.75);backdrop-filter:blur(9px)}
.egg-dialog :focus-visible{outline:2px solid var(--egg-accent);outline-offset:3px}
.egg-dialog [hidden]{display:none!important}
.egg-head{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:20px 24px;border-bottom:1px solid var(--egg-line);background:#152832}
.egg-eyebrow{font-family:var(--mono);font-size:9px;letter-spacing:.2em;color:var(--egg-accent);margin-bottom:5px}
.egg-head h2{font-family:var(--serif);font-size:22px;color:#f1f3ec;margin:0;padding:0;border:0;font-weight:500;letter-spacing:.06em}
.egg-close{display:grid;place-items:center;width:40px;height:40px;border:1px solid var(--egg-line);border-radius:5px;color:var(--egg-ink);background:#1b3039;cursor:pointer;font-size:23px;flex:none}
.egg-close:hover{border-color:var(--egg-accent)}
.egg-layout{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(300px,.8fr)}
.egg-visual{position:relative;min-height:530px;min-width:0;overflow:hidden;background:radial-gradient(ellipse at 40% 40%,#27464b,#0a1720 75%);border-right:1px solid var(--egg-line)}
.egg-viewport{position:absolute;inset:0}
.egg-viewport #ldgl{cursor:default;touch-action:pan-y}
.egg-visual-label{position:absolute;top:20px;left:22px;right:22px;display:flex;justify-content:space-between;gap:10px;font-family:var(--mono);font-size:9px;color:var(--egg-muted);letter-spacing:.1em;pointer-events:none}
.egg-visual-label span:first-child{color:var(--egg-accent)}
.egg-caption{position:absolute;left:22px;right:22px;bottom:20px;font-size:11px;line-height:1.7;color:var(--egg-muted);background:#0b1a22cc;border-left:2px solid var(--egg-accent);padding:10px 12px;pointer-events:none}
.egg-caption strong{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.1em;color:var(--egg-accent);margin-bottom:4px}
.egg-fallback{width:100%;height:100%;padding:50px 24px 80px}
.has-webgl .egg-fallback{display:none}
.egg-fallback .egg-svg-lid{transition:transform .65s var(--ease),opacity .65s}
.egg-dialog[data-step="1"] .egg-svg-lid{transform:translateY(-60px);opacity:.35}
.egg-console{padding:26px;min-width:0;display:flex;flex-direction:column;gap:18px}
.egg-steps{display:flex;gap:7px}
.egg-step{flex:1;min-width:0;padding:11px 7px;border:1px solid var(--egg-line);border-radius:5px;color:var(--egg-muted);background:transparent;cursor:pointer;text-align:left;font-family:var(--mono);font-size:11px;letter-spacing:.05em}
.egg-step small{display:block;font-family:var(--sans);font-size:10px;letter-spacing:0;margin-top:4px;color:inherit}
.egg-step[aria-pressed="true"]{background:#1a393b;border-color:#5aa996;color:var(--egg-accent)}
.egg-step:hover{border-color:#769c9f}
.egg-story h3{font-family:var(--serif);font-size:26px;font-weight:500;line-height:1.35;margin-bottom:9px;color:#edf1e9}
.egg-story p{font-size:13px;color:var(--egg-muted);line-height:1.9;min-height:74px}
.egg-targets{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.egg-target{min-height:39px;padding:8px;border:1px solid var(--egg-line);border-radius:4px;background:#142832;color:var(--egg-muted);font-family:var(--mono);font-size:11px;cursor:pointer}
.egg-target[aria-pressed="true"]{border-color:var(--egg-accent);color:var(--egg-accent);background:#203c3e}
.egg-readout{border:1px solid var(--egg-line);border-radius:5px;padding:14px;background:#0c1a22;min-height:119px}
.egg-readout .egg-symbol{font-family:var(--mono);font-size:12px;color:var(--egg-accent);overflow-wrap:anywhere}
.egg-readout p{font-size:12px;line-height:1.8;color:var(--egg-muted);margin-top:7px}
.egg-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:auto}
.egg-next,.egg-workspace{padding:11px 15px;border-radius:5px;font-size:12px;font-weight:600;cursor:pointer;min-height:42px}
.egg-next{color:#10252a;background:var(--egg-accent);border:1px solid var(--egg-accent);flex:1}
.egg-next:hover{background:#bbf0df}
.egg-workspace{border:1px solid var(--egg-line);color:var(--egg-ink);background:transparent}
.egg-disclaimer{font-size:10px;color:var(--egg-muted);padding-top:12px;border-top:1px solid var(--egg-line);line-height:1.7}
@media(max-width:760px){
.egg-dialog{width:calc(100vw - 16px);max-height:calc(100dvh - 16px);border-radius:9px}
.egg-head{padding:14px 16px}
.egg-head h2{font-size:20px}
.egg-layout{grid-template-columns:1fr}
.egg-visual{height:270px;min-height:0;border-right:0;border-bottom:1px solid var(--egg-line)}
.egg-console{padding:18px;gap:14px}
.egg-story h3{font-size:23px}
.egg-story p{min-height:0}
.egg-visual-label{top:12px;left:16px;right:16px;font-size:8px}
.egg-caption{left:16px;right:16px;bottom:12px;font-size:10px;padding:6px 10px}
.egg-step,.egg-target{min-height:44px}
}
.ld-marquee{grid-row:2;grid-column:1/-1;border-top:1px solid var(--line);background:var(--surface-2);overflow:hidden;padding:13px 0;position:relative;z-index:2}
.ld-probe{position:fixed;left:0;top:0;width:10px;height:10px;border-radius:50%;background:#fff;mix-blend-mode:difference;pointer-events:none;opacity:0;z-index:72;will-change:transform}
.ld-marq{display:flex;white-space:nowrap;font-family:var(--mono);font-size:10px;letter-spacing:.24em;color:var(--faint);will-change:transform}
.ld-marq span{padding-right:2.6em;flex:none}
#ldiris{position:fixed;inset:0;z-index:85;background:var(--paper);display:none;pointer-events:none}
#ldhome{position:fixed;right:16px;bottom:16px;z-index:40;display:inline-flex;align-items:center;gap:7px;font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;color:var(--muted);background:var(--surface);border:1px solid var(--line);border-radius:99px;padding:7px 13px;cursor:pointer;box-shadow:0 2px 10px rgba(27,30,33,.07)}
#ldhome:hover{color:var(--accent);border-color:var(--accent)}
body.landing-on #ldhome{display:none}
#ldhome .ic{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:1.8}
@media(max-width:900px){
.ld-rail{display:none}
#landing{grid-template-columns:1fr;grid-template-rows:auto auto auto;overflow-y:auto;align-content:start}
.ld-main{padding:clamp(24px,6vw,40px);max-width:none}
.ld-stage{grid-row:2;grid-column:1;height:clamp(370px,70vw,550px);margin:0 18px 24px;perspective:none}
#ldgl{touch-action:pan-y}
.ld-tag,.ld-wave,.ld-ruler{display:none}
.ld-stage-tag{font-size:8px}
.ld-stage-foot{font-size:7px;letter-spacing:.06em;padding:12px}
.ld-stage-foot span:first-child{display:none}
.ld-zoom{right:16px;bottom:50px}
.ld-zoom button{min-width:44px;height:44px}
.ld-sweep{display:none}
.ld-title{font-size:clamp(46px,10vw,72px)}
.ld-meta{gap:14px;margin-top:28px}
.ld-meta span{min-width:104px}
.ld-marquee{grid-row:3;padding:10px 0}
}
</style></head><body class="landing-on">
<div id="landing" aria-label="EmbeddedLens 介绍页">
  <div id="ldgrid" aria-hidden="true"></div>
  <div class="ld-rail l" aria-hidden="true">FIELD INSTRUMENT · SWD PROBE · HALT / READ / RESUME</div>
  <div class="ld-main">
    <div class="ld-kicker"><span class="ld-dot" aria-hidden="true"></span>EMBEDDED LENS · FIELD INSTRUMENT No.01</div>
    <h1 class="ld-title" aria-label="EmbeddedLens 嵌入式透视镜"><span class="ld-word" aria-hidden="true">Embedded</span><span class="ld-word accent" aria-hidden="true">Lens</span><span class="ld-zh">嵌入式透视镜</span></h1>
    <p class="ld-manifesto">看见芯片里正在发生的事。</p>
    <p class="ld-sub">零插桩、零串口、不改固件。接上调试器读一拍真实内存，配厂商权威定义——调度、延时、引脚电平，每个数字都能说清它从哪来。</p>
    <div class="ld-actions">
      <button class="ld-cta" id="ldenter"><span class="ld-cta-ring" aria-hidden="true"></span>进入透视镜<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
      <span class="ld-hint">或按 Enter 进入</span>
    </div>
    <div class="ld-meta">
      <span><b>HALT · READ · RESUME</b>停核读一拍，随即恢复</span>
      <span><b>四态溯源</b>实测 / 权威 / 推导 / 不可知</span>
      <span><b>SINGLE FILE</b>单文件离线，双击即看</span>
    </div>
    <div class="ld-build" id="ldbuild"></div>
    <button class="egg-trigger" id="eggunlock" type="button" aria-haspopup="dialog">芯片里藏了一个实验 <span>SWD</span></button>
  </div>
  <div class="ld-stage" id="ldstage" aria-hidden="true">
    <span class="ld-stage-tag tl">ASSEMBLY / 001</span>
    <span class="ld-stage-tag tr">STM32 · CORTEX-M3</span>
    <div class="ld-ruler l"></div>
    <div class="ld-ruler r"></div>
    <canvas id="ldgl"></canvas>
    <div class="ld-zoom" aria-hidden="true"><button id="ldzout" tabindex="-1" aria-label="缩小">−</button><button id="ldzin" tabindex="-1" aria-label="放大">+</button><button id="ldzreset" tabindex="-1" aria-label="复位视角">RESET</button></div>
    <span class="ld-q" id="ldq" aria-hidden="true">?</span>
    <div class="ld-scope" id="ldscope">
      <svg viewBox="0 0 560 560" id="ldsvg">
        <g id="ldticks"></g>
        <circle class="ld-ring-o" cx="280" cy="280" r="232"/>
        <circle class="ld-ring-d" cx="280" cy="280" r="196"/>
        <g id="ldrev">
          <circle class="ld-ring-i" cx="280" cy="280" r="150"/>
          <circle class="ld-node" cx="280" cy="132" r="4"/>
          <circle class="ld-node b" cx="414" cy="342" r="3"/>
          <circle class="ld-node b" cx="152" cy="356" r="3"/>
        </g>
        <path class="ld-cross" d="M280 96v54M280 410v54M96 280h54M410 280h54"/>
        <g class="ld-angles">
          <text x="280" y="30" text-anchor="middle">000</text>
          <text x="538" y="284" text-anchor="end">090</text>
          <text x="280" y="548" text-anchor="middle">180</text>
          <text x="22" y="284">270</text>
        </g>
        <rect class="ld-chip" x="236" y="236" width="88" height="88" rx="12"/>
        <g id="ldpins" class="ld-pins"></g>
        <circle class="ld-core" cx="280" cy="280" r="5"/>
        <circle class="ld-hit" id="ldhit" cx="280" cy="280" r="72"/>
        <text class="ld-secret" id="ldsecret" x="352" y="208">?</text>
      </svg>
      <div class="ld-sweep" aria-hidden="true"></div>
    </div>
    <span class="ld-tag t1"><i></i>LQFP-64</span>
    <span class="ld-tag t2"><i></i>SWD</span>
    <span class="ld-tag t3"><i></i>GPIO</span>
    <span class="ld-tag t4"><i></i>3D ASSEMBLY</span>
    <svg class="ld-wave" viewBox="0 0 420 48" preserveAspectRatio="none" aria-hidden="true"><polyline points="0,34 12,34 14,18 18,18 20,34 42,34 46,26 50,26 52,34 78,34 80,10 84,10 86,34 104,34 108,30 112,30 114,34 150,34 152,22 156,22 158,34 186,34 190,38 194,38 196,34 230,34 232,14 236,14 238,34 260,34 264,28 268,28 270,34 300,34 302,20 306,20 308,34 336,34 340,32 344,32 346,34 380,34 382,12 386,12 388,34 420,34"/></svg>
    <div class="ld-stage-foot"><span>MODEL / DETAIL STUDY</span><span>拖动旋转 · 滚轮 / 双指缩放</span><span>3D 示意 · 非实时读数</span></div>
  </div>
  <div class="ld-probe" id="ldprobe" aria-hidden="true"></div>
  <div class="ld-marquee" aria-hidden="true"><div class="ld-marq" id="ldmarq"><span>SWD · SNAPSHOT · TICK · READY · DELAYED · PROVENANCE · NO FABRICATION · </span><span>SWD · SNAPSHOT · TICK · READY · DELAYED · PROVENANCE · NO FABRICATION · </span></div></div>
</div>
<div id="ldiris" aria-hidden="true"></div>
<dialog class="egg-dialog" id="eggdialog" aria-labelledby="eggtitle" aria-describedby="eggdisclaimer">
  <header class="egg-head"><div><div class="egg-eyebrow">SECRET LAB / INSIDE THE CHIP</div><h2 id="eggtitle">芯片调试舱</h2></div><button class="egg-close" id="eggclose" type="button" aria-label="退出芯片调试舱" autofocus>×</button></header>
  <div class="egg-layout">
    <div class="egg-visual">
      <div class="egg-viewport" id="eggviewport" aria-hidden="true"><svg class="egg-fallback" viewBox="0 0 480 340" aria-hidden="true">
        <g fill="none" stroke="#35585c"><path d="M45 235 225 110 438 223 256 337Z"/><path d="m90 243 139-97 167 89-140 96Z"/><path d="m144 215 87-62 107 57-84 60Z"/></g>
        <g fill="#163536" stroke="#91dfce"><path d="m155 202 75-52 100 53-75 53Z"/><path d="m190 200 42-29 62 32-42 30Z"/></g><text x="242" y="205" text-anchor="middle" fill="#b9f1de" font-family="monospace" font-size="12">CORE</text>
        <g class="egg-svg-lid"><path d="m110 145 117-80 151 80v24L259 252 110 169Z" fill="#1d303b" stroke="#87aeb6"/><path d="m110 145 117-80 151 80-119 83Z" fill="#2c4350" stroke="#87aeb6"/><text x="237" y="145" fill="#e1ece8" font-family="monospace" text-anchor="middle" font-size="18">CORTEX-M3</text></g>
      </svg></div>
      <div class="egg-visual-label"><span id="eggvisualstate">CORE / HALTED</span><span>CONCEPT MODEL · 结构示意</span></div>
      <div class="egg-caption"><strong id="eggcaptiontitle">HALT / 把时间停在这一拍</strong><span id="eggcaption">点击下一步，掀开外壳看看观察链路。</span></div>
    </div>
    <section class="egg-console" aria-label="调试过程演练">
      <div class="egg-steps" aria-label="选择演练阶段"><button class="egg-step" data-egg-step="0" type="button" aria-pressed="true">01 HALT<small>暂停</small></button><button class="egg-step" data-egg-step="1" type="button" aria-pressed="false">02 READ<small>检查</small></button><button class="egg-step" data-egg-step="2" type="button" aria-pressed="false">03 RESUME<small>恢复</small></button></div>
      <div class="egg-story" aria-live="polite" aria-atomic="true"><h3 id="eggheading"></h3><p id="eggbody"></p></div>
      <div class="egg-targets" id="eggtargets" aria-label="选择检查对象" hidden><button class="egg-target" data-egg-target="0" type="button" aria-pressed="true">固件身份</button><button class="egg-target" data-egg-target="1" type="button" aria-pressed="false">当前任务</button><button class="egg-target" data-egg-target="2" type="button" aria-pressed="false">节拍计数</button><button class="egg-target" data-egg-target="3" type="button" aria-pressed="false">引脚输出</button></div>
      <div class="egg-readout" aria-live="polite" aria-atomic="true"><div class="egg-symbol" id="eggsymbol"></div><p id="eggdetail"></p></div>
      <div class="egg-actions"><button class="egg-next" id="eggnext" type="button">掀开芯片 · 下一步</button><button class="egg-workspace" id="eggworkspace" type="button">去看真实数据</button></div>
      <p class="egg-disclaimer" id="eggdisclaimer">教学彩蛋 · 未连接硬件。分层与内部电路仅为概念示意，不是真实芯片剖面，也不是采样结果。</p>
    </section>
  </div>
</dialog>
<button id="ldhome" aria-label="返回介绍页"><svg class="ic" viewBox="0 0 24 24"><path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/></svg>介绍页</button>
<div class="wrap">
<div class="workbench" id="workbench">
<aside class="workbench-nav">
  <div class="brand"><div class="brand-lockup">
    <div class="mark" aria-hidden="true"><svg viewBox="0 0 44 44"><circle cx="22" cy="22" r="15"/><circle cx="22" cy="22" r="5.5"/><path d="M22 2v8M22 34v8M2 22h8M34 22h8"/><path d="M11.4 11.4l3 3M29.6 29.6l3 3M32.6 11.4l-3 3M14.4 29.6l-3 3"/></svg></div>
    <div class="brand-text"><div class="brand-name">Embedded<span>Lens</span></div><div class="brand-caption">嵌入式透视镜</div></div>
  </div></div>
  <div class="nav-head"><div class="nav-label">观察与理解</div>
    <button class="nav-toggle" id="navtoggle" type="button" aria-expanded="true" aria-controls="tabs nav-note" aria-label="收起功能导航" title="收起功能导航"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/><path class="nav-chevron" d="m17 9-3 3 3 3"/></svg></button>
  </div>
  <nav class="tabs" id="tabs" role="tablist" aria-label="视图切换"></nav>
  <div class="nav-note" id="nav-note"><b>只读观察，安心探索</b>不写入 · 不烧录 · 不改固件<br>每个数字，都能找到来源。<p>EMBEDDED LENS / WORKSPACE</p></div>
</aside>
<main class="workbench-main" aria-label="嵌入式状态与教学视图">
<header class="masthead">
  <div class="workspace-label"><b>工作空间</b><span class="slash">/</span><span>观察工作台</span></div>
  <div class="mast-actions">
    <button class="btn" id="readopen"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 2v6M15 2v6"/><path d="M6 8h12v3a6 6 0 0 1-12 0z"/><path d="M12 17v5"/></svg>一键读取</button>
    <button class="btn sec" id="glopen"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>名词小词典</button>
    <button class="btn sec" id="impopen"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>导入我的工程</button>
  </div>
</header>
<details class="project-panel" id="projectpanel">
  <summary><span class="project-name" id="projectname"></span><span class="status-strip" id="topbadges"></span><span class="project-detail-label">工程详情</span></summary>
  <div class="project-body"><div class="spec" id="spec"></div><details class="identity-panel" id="identitycard"></details></div>
</details>
<div class="view on" id="view-learn" role="tabpanel" aria-labelledby="tab-learn" tabindex="0"></div>
<div class="view" id="view-sched" role="tabpanel" aria-labelledby="tab-sched" tabindex="0"></div>
<div class="view" id="view-reg" role="tabpanel" aria-labelledby="tab-reg" tabindex="0"></div>
<div class="view" id="view-term" role="tabpanel" aria-labelledby="tab-term" tabindex="0"></div>
<div class="view" id="view-plat" role="tabpanel" aria-labelledby="tab-plat" tabindex="0"></div>
<div class="view replay-layout" id="view-replay" role="tabpanel" aria-labelledby="tab-replay" tabindex="0"></div>
<details class="data-contract"><summary><b>数据与溯源约定</b><span>实测 · 权威 · 推导 · 不可知</span></summary><div class="note" id="contract"></div>
<div class="note" style="margin:10px 0 8px">每个数字都标了「它从哪来」。点下面带虚线的词，看大白话解释：</div>
<div class="legend"><span><b class="v m">实测值<i class="bdg">实测</i></b> <span class="gl" data-gl="实测值" tabindex="0" role="button">真的从芯片读出来的数</span></span>
<span><b class="v a">权威定义<i class="bdg">权威</i></b> <span class="gl" data-gl="权威定义" tabindex="0" role="button">厂商说明书/编译信息的标准答案</span></span>
<span><b class="v d">推导值<i class="bdg">推导</i></b> <span class="gl" data-gl="推导值" tabindex="0" role="button">实测+定义算出来，附公式</span></span>
<span><b class="v u">不可知<i class="bdg">不可知</i></b> <span class="gl" data-gl="不可知" tabindex="0" role="button">证据不够，老实说不知道</span></span></div></details>
</main>
</div>
</div>
<div id="impwrap" role="dialog" aria-modal="true" aria-label="导入我的工程">
  <div class="imppanel">
    <button class="imp-x" id="impclose" aria-label="关闭">&times;</button>
    <div class="imp-h">导入我的工程</div>
    <p class="imp-lead">把 Keil 编译出来的几个文件选进来，工具就能读懂你的芯片和代码，画成看得懂的图。文件只在你自己电脑里读取，<b>不会上传</b>。</p>
    <div class="imp-callout">
      <b>先说清楚：</b>这一步读懂的是「芯片说明书」和「你的代码」。至于芯片<b>此刻</b>的真实状态，要接上 ST-LINK 调试器采样才知道；没接的地方会老实标「不可知」，绝不瞎编。工具<b>只读不写</b>，不会改动或烧录你的芯片。
    </div>
    <div class="imp-example">
      <div class="txt"><b>第一次用？</b>先看内置示例，立刻明白每个页面在讲什么，再换成你自己的文件。</div>
      <button class="btn sec" id="impreset">先看内置示例</button>
    </div>

    <div class="imp-step">只需 3 个文件</div>
    <div class="imp-row">
      <div class="imp-num">1</div>
      <div class="imp-rowtxt">
        <div class="imp-rowtitle">地址清单<span class="ext">.map</span></div>
        <div class="imp-rowdesc">Keil 编译后自动生成的「符号表」，记录每个变量/函数在内存里的地址。工具靠它找到操作系统内核。</div>
        <div class="imp-rowhint">位置：MDK-ARM/工程名/工程名.map</div>
      </div>
      <div class="imp-rowfile">
        <label class="imp-pick"><input type="file" id="f_map" accept=".map,.txt" aria-label="选择 map 文件"><span>选择文件</span></label>
        <span class="imp-chip" id="c_map" hidden></span>
      </div>
    </div>
    <div class="imp-row">
      <div class="imp-num">2</div>
      <div class="imp-rowtxt">
        <div class="imp-rowtitle">芯片说明书<span class="ext">.svd</span></div>
        <div class="imp-rowdesc">芯片厂商提供的寄存器说明（CMSIS-SVD），告诉工具每个引脚位的含义。载入后自动选好 GPIO 输出寄存器。</div>
        <div class="imp-rowhint">位置：Keil 安装目录/…/STM32F1xx_DFP/…/SVD/STM32F103xx.svd</div>
      </div>
      <div class="imp-rowfile">
        <label class="imp-pick"><input type="file" id="f_svd" accept=".svd,.xml" aria-label="选择 SVD 文件"><span>选择文件</span></label>
        <span class="imp-chip" id="c_svd" hidden></span>
      </div>
    </div>
    <div class="imp-row">
      <div class="imp-num">3</div>
      <div class="imp-rowtxt">
        <div class="imp-rowtitle">你的主程序<span class="ext">main.c</span></div>
        <div class="imp-rowdesc">你写的代码。工具从中读出创建了哪些任务、延时多久、在哪里点灯。</div>
        <div class="imp-rowhint">位置：Core/Src/main.c</div>
      </div>
      <div class="imp-rowfile">
        <label class="imp-pick"><input type="file" id="f_mainc" accept=".c" aria-label="选择 main.c"><span>选择文件</span></label>
        <span class="imp-chip" id="c_mainc" hidden></span>
      </div>
    </div>

    <details class="imp-adv">
      <summary>更多选项（可选 · 让结果更完整）</summary>
      <div class="imp-advbody">
        <div class="imp-grid">
          <div class="imp-field"><label>引脚定义 <span class="fh">main.h，确认哪个引脚接了灯</span></label>
            <div class="imp-mini"><label class="imp-pick"><input type="file" id="f_mainh" accept=".h" aria-label="选择 main.h"><span>选择文件</span></label><span class="imp-chip" id="c_mainh" hidden></span></div></div>
          <div class="imp-field"><label>节拍配置 <span class="fh">FreeRTOSConfig.h，把延时换算成秒</span></label>
            <div class="imp-mini"><label class="imp-pick"><input type="file" id="f_cfg" accept=".h" aria-label="选择 FreeRTOSConfig.h"><span>选择文件</span></label><span class="imp-chip" id="c_cfg" hidden></span></div></div>
          <div class="imp-field"><label>设备头文件 <span class="fh">如 stm32f103xe.h，和说明书交叉核对</span></label>
            <div class="imp-mini"><label class="imp-pick"><input type="file" id="f_hdr" accept=".h" aria-label="选择设备头"><span>选择文件</span></label><span class="imp-chip" id="c_hdr" hidden></span></div></div>
          <div class="imp-field"><label>程序文件 <span class="fh">.axf/.elf，提取固件指纹做身份核验</span></label>
            <div class="imp-mini"><label class="imp-pick"><input type="file" id="f_axf" accept=".axf,.elf,.out" aria-label="选择 axf"><span>选择文件</span></label><span class="imp-chip" id="c_axf" hidden></span></div></div>
          <div class="imp-field"><label>结构偏移 <span class="fh">offsets.json，命令行 gdb 核定的结果</span></label>
            <div class="imp-mini"><label class="imp-pick"><input type="file" id="f_off" accept=".json" aria-label="选择 offsets.json"><span>选择文件</span></label><span class="imp-chip" id="c_off" hidden></span></div></div>
          <div class="imp-field"><label>看哪个外设/寄存器 <span class="fh">默认 GPIOC 的输出寄存器 ODR</span></label>
            <div class="imp-mini"><select id="sel_per" aria-label="外设"><option value="">先载入说明书…</option></select><select id="sel_reg" aria-label="寄存器"><option value="">先选外设…</option></select></div></div>
          <div class="imp-field"><label>芯片型号</label><input type="text" id="p_device" value="STM32F103RCT6"></div>
          <div class="imp-field"><label>内核</label><input type="text" id="p_core" value="Cortex-M3"></div>
          <div class="imp-field"><label>Flash 起始地址</label><input type="text" id="p_flash" value="0x08000000"></div>
          <div class="imp-field"><label>RAM 起始地址</label><input type="text" id="p_ram" value="0x20000000"></div>
        </div>
      </div>
    </details>

    <div class="imp-actions">
      <button class="btn big" id="impgo"><svg class="ic" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>开始解读</button>
      <button class="btn sec" id="impexphtml" disabled>导出网页</button>
      <button class="btn sec" id="impexpjson" disabled>导出数据</button>
      <label class="btn sec" style="cursor:pointer">导入数据文件<input type="file" id="f_json" accept=".json" hidden></label>
    </div>
    <div id="impstatus"></div>
  </div>
</div>

<div id="readwrap" role="dialog" aria-modal="true" aria-label="一键读取开发板">
  <div class="imppanel readpanel">
    <button class="imp-x" id="readclose" aria-label="关闭">&times;</button>
    <div class="imp-h">一键读取开发板</div>
    <p class="imp-lead">通过本机 EmbeddedLens Bridge 调用 OpenOCD，短暂停核读取真实内存后立即恢复。只读，不写内存、不烧录、不复位。</p>
    <div class="imp-callout"><b>为什么需要本机桥接？</b>浏览器不能直接访问 ST-LINK/USB。请先在本机运行桥接，再点「开始读取」；线上页面也可调用本机 127.0.0.1 的桥接。</div>
    <div class="read-status busy" id="readstatus">正在连接本机桥接…</div>
    <div class="imp-grid">
      <div class="imp-field"><label for="read-example">工程</label><select id="read-example" aria-label="选择工程"><option value="">先连接桥接…</option></select></div>
      <div class="imp-field"><label for="read-frames">帧数</label><input type="number" id="read-frames" min="1" max="20" step="1" value="5" aria-label="连续采样帧数"></div>
      <div class="imp-field"><label for="read-interval">帧间隔 / 秒</label><input type="number" id="read-interval" min="0" max="10" step="0.5" value="1" aria-label="帧间隔秒数"></div>
    </div>
    <pre class="read-cmd mono" id="readcmd">在项目根目录运行：
python tools\elens_bridge.py

然后保持窗口开启，回到这里点「重试连接」。</pre>
    <div class="imp-actions">
      <button class="btn big" id="readgo" disabled>开始读取</button>
      <button class="btn sec" id="readretry">重试连接</button>
      <button class="btn sec" id="readcopy">复制启动命令</button>
      <a class="btn sec" id="readlocal" href="http://127.0.0.1:8765/" target="_blank" rel="noopener">打开本机页面</a>
    </div>
    <p class="read-note">读取时会短暂停核并立即恢复；帧间隔由主机控制，目标在帧间保持运行。固件身份核验不通过时只记录原始读数，不解释 RTOS 状态。</p>
  </div>
</div>

<div id="glwrap" role="dialog" aria-modal="true" aria-label="名词小词典">
  <div class="glpanel">
    <button class="imp-x" id="glclose" aria-label="关闭">&times;</button>
    <div class="imp-h">名词小词典</div>
    <p class="imp-lead">看不懂的专业词，这里用大白话解释。页面里带虚线下划线的词，点一下也能随时看解释。</p>
    <input type="text" class="gl-search" id="glsearch" placeholder="搜索名词，比如「任务」「寄存器」「tick」…" aria-label="搜索名词">
    <div id="glbody"></div>
  </div>
</div>

<div id="scrim" onclick="closeProv()"></div>
<aside id="prov" aria-label="数据溯源"><h4><svg class="ic" viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>溯源<button class="x" onclick="closeProv()" aria-label="关闭溯源"><svg class="ic" viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></svg></button></h4><div id="provbody"></div></aside>
__GSAP_LIBS__
<script>
let LENS = __LENS_JSON__;
const STATE={measured:['实测','m'],authoritative:['权威','a'],derived:['推导','d'],unknown:['不可知','u']};
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
const IC={learn:'<path d="m3 8 9-5 9 5-9 5-9-5zM6 10v7c4 4 8 4 12 0v-7M21 8v9"/>',sched:'<path d="M3 12h4l3 8 4-16 3 8h4"/>',reg:'<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/>',term:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',plat:'<path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>',replay:'<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',prev:'<path d="M15 18l-6-6 6-6"/>',next:'<path d="M9 18l6-6-6-6"/>',reset:'<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',play:'<path d="M6 4l14 8-14 8V4z"/>',stop:'<rect x="6" y="6" width="12" height="12" rx="1.5"/>',check:'<path d="M20 6 9 17l-5-5"/>',alert:'<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',shield:'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4M12 16h.01"/>',arrow:'<path d="M5 12h14M13 6l6 6-6 6"/>'};
function ic(n,s){return `<svg class="ic" viewBox="0 0 24 24"${s?` style="width:${s}px;height:${s}px"`:''}>${IC[n]||''}</svg>`;}
function openProv(){document.getElementById('prov').classList.add('on');document.getElementById('scrim').classList.add('on');if(window.__provIn)window.__provIn();}
function closeProv(){document.getElementById('prov').classList.remove('on');document.getElementById('scrim').classList.remove('on');}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeProv();});
function val(v,hex){
  if(!v||v.value==null&&v.state!=='unknown') return '<span class="v u">—<i class="bdg">不可知</i></span>';
  const st=STATE[v.state]||['?','u'];
  let disp=v.value;
  if(hex&&typeof v.value==='number') disp='0x'+(v.value>>>0).toString(16).toUpperCase();
  if(v.state==='unknown') disp='不可知';
  return `<span class="v ${st[1]}" data-prov='${esc(JSON.stringify(v))}'>${esc(disp)}<i class="bdg">${st[0]}</i></span>`;
}
function provShow(v){
  const st=STATE[v.state]||['?','u'];
  let h=`<div class="row"><b>态</b><span>${st[0]}值</span></div>`;
  for(const[k,val]of Object.entries(v.prov||{})) h+=`<div class="row"><b>${esc(k)}</b><span class="mono">${esc(typeof val==='object'?JSON.stringify(val):String(val))}</span></div>`;
  document.getElementById('provbody').innerHTML=h;
  openProv();
}
document.addEventListener('click',e=>{
  const t=e.target.closest('.v'); if(t&&t.dataset.prov){provShow(JSON.parse(t.dataset.prov));return;}
  const c=e.target.closest('.swim td.cell'); if(c&&c.dataset.prov)provShow(JSON.parse(c.dataset.prov));
});
document.addEventListener('keydown',e=>{
  if((e.key==='Enter'||e.key===' ')&&e.target.matches&&e.target.matches('.swim td.cell[role="button"]')){e.preventDefault();e.target.click();}
});
function bar(barEl,lblEl){const m=new Map(),lm=new Map();return function(list){
  const want=new Set(list.map(b=>b.k));
  list.forEach((b,i)=>{let el=m.get(b.k),le=lm.get(b.k);
    if(!el){el=document.createElement('div');el.className='blk '+(b.cls||'');
      const s=document.createElement('span');s.className='lbl';el.appendChild(s);barEl.appendChild(el);m.set(b.k,el);
      le=document.createElement('div');le.className='blbl';lblEl.appendChild(le);lm.set(b.k,le);
      el.style.flexGrow=0;el.style.opacity=0;le.style.flexGrow=0;le.style.opacity=0;
      requestAnimationFrame(()=>requestAnimationFrame(()=>{el.style.opacity=1;el.style.flexGrow=b.s;le.style.opacity=1;le.style.flexGrow=b.s;}));
    }else{el.style.opacity=1;el.style.flexGrow=b.s;le.style.opacity=1;le.style.flexGrow=b.s;}
    el.style.order=i;le.style.order=i;el.className='blk '+(b.cls||'');
    if(b.task){el.dataset.task=b.task;el.style.cursor='pointer';el.title='点击跳回源码调用';}
    el.querySelector('.lbl').textContent=b.l||'';le.textContent=b.lt||b.l||'';});
  m.forEach((el,k)=>{if(!want.has(k)){const le=lm.get(k);el.style.opacity=0;el.style.flexGrow=0;le.style.opacity=0;le.style.flexGrow=0;
    setTimeout(()=>{el.remove();le.remove();m.delete(k);lm.delete(k);},600);}});};}
function stepper(n,render){let i=0;render(0);return{next(){i=Math.min(n-1,i+1);render(i);},prev(){i=Math.max(0,i-1);render(i);},reset(){i=0;render(0);},get i(){return i;}};}
const $=id=>document.getElementById(id);
let snaps=[],validSnaps=[];
function refreshSnaps(){snaps=LENS.snapshots.filter(s=>s.status==='ok');validSnaps=studyFrames(LENS);}
refreshSnaps();

/* ---- 名词小词典：大白话解释 + 行内提示 ---- */
const GLOSSARY=[
 {cat:'基础概念',items:[
  {t:'RTOS',p:'实时操作系统。让一颗单片机「同时」跑多个任务（点灯、读传感器、通信），靠快速轮流切换实现。FreeRTOS 是最常用的一种。'},
  {t:'FreeRTOS',p:'一款免费、开源的实时操作系统，广泛用于 STM32 等单片机。本工具目前能读它的真实内核状态。'},
  {t:'任务',p:'一段独立运行、各管一摊的代码，比如「让 LED 闪烁」。每个任务有自己的名字和优先级。'},
  {t:'优先级',p:'任务的「重要程度」，数字越大越优先。高优先级任务一旦就绪，会抢在低优先级前面运行。'},
  {t:'调度',p:'RTOS 决定「下一个该谁运行」的规则：总挑就绪任务里优先级最高的那个。'},
  {t:'tick',p:'系统节拍，RTOS 的「心跳」。每滴答一次，内核检查一遍「有没有任务到点」。间隔由 configTICK_RATE_HZ 决定：100 Hz → 10 ms 一次；1000 Hz → 1 ms 一次。延时就是数滴答次数。'},
  {t:'Hz',p:'赫兹，频率单位「每秒多少次」。心跳 1000 Hz = 每秒 1000 次 = 每次 1 毫秒。'},
  {t:'就绪链表',p:'「已经准备好、随时能运行」的任务排成的队伍，按优先级分组。'},
  {t:'延时链表',p:'「正在睡觉、等时间到」的任务排成的队伍，按到期 tick 从小到大排序，表头就是最早醒来的任务。内核每个节拍只看表头，不必扫描整条链。'},
  {t:'TCB',p:'任务控制块。RTOS 给每个任务建的一张「身份卡」，存着名字、优先级、状态等。'},
  {t:'当前任务',p:'此刻正占着 CPU 运行的那个任务（内核变量 pxCurrentTCB 指向它）。'},
  {t:'到期 tick',p:'延时任务计划醒来的心跳编号 = 调用 vTaskDelay 那一刻的 xTickCount + 延时滴答数。注意：到期 ≠ 立刻运行，还要等调度器选中；快照只能看到这个值，不能拿「采样时的 tick + 延时数」反推它。'},
  {t:'xTickCount',p:'内核的节拍计数器，每来一次心跳 +1。它是所有相对延时的时间基准：到期 tick = 调用时的 xTickCount + 滴答数。'},
  {t:'xNextTaskUnblockTime',p:'内核记的「下一个该醒的时刻」：延时链表非空时等于表头任务的到期 tick；链表空时是一个很大的占位值（portMAX_DELAY）。每个节拍先比较这一个数，省时间。'},
  {t:'vTaskDelayUntil',p:'「绝对节拍」延时：以上一次唤醒的时刻 + 固定周期作为下一次唤醒点，而不是「从现在起睡多久」。适合固定周期采样，不会因为本圈代码执行时间而越拖越慢。'},
  {t:'适配器',p:'工具里负责「读懂某种 RTOS 内核数据」的插件。换一种 RTOS 就换一个适配器。'},
  {t:'vTaskDelay',p:'FreeRTOS 的相对延时：让当前任务睡指定滴答数。内核把它从就绪链表摘下，按到期 tick 插进延时链表；到期时刻 = 调用时 tick + 滴答数，不含本圈代码的执行时间。'},
  {t:'configTICK_RATE_HZ',p:'FreeRTOS 配置里的心跳频率（Hz）。100 → 1 tick = 10 ms；1000 → 1 ms。它是全工程延时的「时间尺子」，改它要重新编译，不只是改一处延时。'},
  {t:'HAL_GPIO_WritePin',p:'ST 官方库的写引脚函数：给某端口某引脚写高电平或低电平（点灯/灭灯）。'},
  {t:'GPIO_PIN_SET',p:'HAL 的「置位」参数：把 pin 指定的那一位写成 1（高电平）。它是置位，不是翻转；已经为 1 的位不会变成 0。'},
  {t:'GPIO_PIN_RESET',p:'HAL 的「复位」参数：把 pin 指定的那一位写成 0（低电平）。和 SET 配对使用，引脚电平才会发生变化。'},
 ]},
 {cat:'芯片与寄存器',items:[
  {t:'寄存器',p:'芯片里控制硬件的「小格子」。往某位写 1 或 0，就能控制引脚电平、开关外设等。'},
  {t:'GPIO',p:'通用输入输出引脚，可以接 LED、按键等。每个引脚对应寄存器里的一位。'},
  {t:'ODR',p:'GPIO 的「输出数据寄存器」。某位写 1，对应引脚输出高电平；写 0 输出低电平。高电平是否让灯亮取决于硬件接法（共阳/共阴、是否反相），源码里看不出来。'},
  {t:'位段',p:'一个寄存器里的某几位，各有专门含义。工具把 32 位画成一格一格，方便看懂。'},
  {t:'SVD',p:'芯片厂商写的「寄存器说明书」（CMSIS-SVD，XML 文件），列出每个寄存器的地址和每一位的含义。是权威定义，不是猜的。'},
  {t:'derivedFrom',p:'SVD 里的省事写法：「这个外设和那个长得一样，直接沿用它的定义」。比如 GPIOC 沿用 GPIOA。'},
  {t:'GPIO_TypeDef',p:'设备头文件里描述 GPIO 寄存器排布的结构体，用来和 SVD 交叉核对，确保地址一致。'},
 ]},
 {cat:'文件与构建',items:[
  {t:'map 文件',p:'编译链接后生成的「地址清单」，列出每个变量/函数被放到内存哪个地址。工具靠它找到内核对象。'},
  {t:'AXF',p:'Keil 编译链接后的最终程序文件（ELF 格式，含调试信息）。从中可提取烧进芯片的 Flash 镜像。'},
  {t:'DWARF',p:'编译时留下的调试信息，记录结构体里每个成员排在第几字节。工具靠它准确读出任务名等，而不是猜版本偏移。'},
  {t:'结构偏移',p:'结构体里某个成员距离起始地址的字节数，比如任务名在 TCB 的第几字节。必须由 DWARF 核定。'},
  {t:'固件身份核验',p:'把芯片里实际烧录的程序，和你这次编译的程序逐字节比对，确认是同一个。不一致就停止解释，避免张冠李戴。'},
  {t:'SHA-256',p:'文件的「数字指纹」。内容变一点，指纹就完全不同。用来确认两个文件是否一模一样。'},
 ]},
 {cat:'采样与诚实',items:[
  {t:'停核采样',p:'用调试器让芯片暂停一瞬间，读出内存真实数据，再马上恢复运行。像给正在跑的程序拍快照，不改固件、不加代码。'},
  {t:'SWD',p:'调试器（如 ST-LINK）和芯片之间通信的两线协议。工具通过它读内存，只读不写。'},
  {t:'ST-LINK',p:'ST 芯片常用的调试器/烧录器，连接电脑和芯片，工具靠它做停核采样。'},
  {t:'离散快照',p:'一次次单独拍的快照，不是连续录像。两次之间芯片还在跑，可能错过中间变化（漏采）。'},
  {t:'实测值',p:'真的用调试器从芯片里读出来的数，带内存地址和采样时间。'},
  {t:'权威定义',p:'来自厂商说明书（SVD）、设备头或编译信息（DWARF）的「标准答案」，不是猜的。'},
  {t:'推导值',p:'用实测值 + 权威定义算出来的结果，比如 100 滴答 ÷ 100 Hz = 1 秒，附公式。'},
  {t:'不可知',p:'证据不够时，工具诚实地说「不知道」，绝不编造一个数糊弄你。'},
  {t:'溯源',p:'每个数字都能点开看「它从哪来」——内存地址、文件行号或计算公式。'},
  {t:'哨兵',p:'链表末尾的特殊标记值。工具靠它确认「读到尾了、没读飞」，是一种安全校验。'},
 ]},
];
const GLMAP={};GLOSSARY.forEach(c=>c.items.forEach(i=>GLMAP[i.t]=i.p));
function g(t,label){const p=GLMAP[t];const txt=label==null?t:label;if(!p)return esc(txt);
  return `<span class="gl" data-gl="${esc(t)}" tabindex="0" role="button" aria-label="${esc(t)}：点击查看通俗解释">${esc(txt)}</span>`;}
const glpop=document.createElement('div');glpop.id='glpop';glpop.setAttribute('role','tooltip');document.body.appendChild(glpop);
let glActive=null,glPinned=null;
const hoverable=window.matchMedia('(hover:hover)').matches;
function showGl(el){const t=el.dataset.gl,p=GLMAP[t];if(!p)return;
  glpop.innerHTML=`<span class="gt">${esc(t)}</span>${esc(p)}`;glpop.classList.add('on');
  const r=el.getBoundingClientRect(),pw=glpop.offsetWidth,ph=glpop.offsetHeight;
  let left=Math.max(10,Math.min(r.left+r.width/2-pw/2,window.innerWidth-pw-10));
  let top=r.bottom+8;if(top+ph>window.innerHeight-10)top=Math.max(10,r.top-ph-8);
  glpop.style.left=left+'px';glpop.style.top=top+'px';glActive=el;}
function hideGl(){glpop.classList.remove('on');glActive=null;}
document.addEventListener('click',e=>{const el=e.target.closest('.gl');
  if(el){e.preventDefault();if(glPinned===el){glPinned=null;hideGl();}else{glPinned=el;showGl(el);}return;}
  if(!e.target.closest('#glpop')){glPinned=null;hideGl();}});
document.addEventListener('mouseover',e=>{const el=e.target.closest('.gl');if(el&&hoverable&&!glPinned)showGl(el);});
document.addEventListener('mouseout',e=>{const el=e.target.closest('.gl');if(el&&hoverable&&!glPinned&&glActive===el)hideGl();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){glPinned=null;hideGl();return;}
  const el=e.target.closest&&e.target.closest('.gl');if(el&&(e.key==='Enter'||e.key===' ')){e.preventDefault();glPinned=el;showGl(el);}});
window.addEventListener('scroll',()=>{glPinned=null;hideGl();},true);
window.addEventListener('resize',()=>{glPinned=null;hideGl();});
function renderGlossary(filter){const f=(filter||'').trim().toLowerCase();let h='',any=false;
  GLOSSARY.forEach(c=>{const items=c.items.filter(i=>!f||i.t.toLowerCase().includes(f)||i.p.toLowerCase().includes(f));
    if(!items.length)return;any=true;
    h+=`<div class="gl-cat">${esc(c.cat)}</div>`+items.map(i=>`<div class="gl-item"><span class="t">${esc(i.t)}</span><span class="p">${esc(i.p)}</span></div>`).join('');});
  $('glbody').innerHTML=any?h:'<div class="gl-empty">没有匹配的词。试试「任务」「寄存器」「tick」。</div>';}
$('glopen').addEventListener('click',()=>{closeProv();glPinned=null;hideGl();renderGlossary('');$('glsearch').value='';$('glwrap').classList.add('on');setTimeout(()=>$('glsearch').focus(),60);});
$('glclose').addEventListener('click',()=>$('glwrap').classList.remove('on'));
$('glwrap').addEventListener('click',e=>{if(e.target===$('glwrap'))$('glwrap').classList.remove('on');});
$('glsearch').addEventListener('input',e=>renderGlossary(e.target.value));
document.addEventListener('keydown',e=>{if(e.key==='Escape')$('glwrap').classList.remove('on');});

/* ---- 顶部徽章 + 身份 ---- */
function renderTop(){
  const b=LENS.build,d=LENS.device;
  $('spec').innerHTML=[['DEVICE',d.name],['CORE',d.core],['RTOS',b.rtos],['KERNEL',b.kernel?b.kernel.version:'?'],['BUILD',b.axf_sha?b.axf_sha.slice(0,12):'未提供 AXF']].map(r=>`<div class="row"><span class="k">${r[0]}</span><span class="val">${esc(r[1])}</span></div>`).join('');
  $('projectname').innerHTML=`${ic('reg')}<b>${esc(d.name)}</b>`;
  const id=LENS.identity;
  const cls=id.status==='verified'?'ok':(id.status==='mismatch'?'bad':'warn');
  const sealIc={verified:'check',mismatch:'alert',unverified:'shield','no-sample':'shield'}[id.status]||'shield';
  const txt={verified:'固件身份已核验',mismatch:'固件身份不匹配',unverified:'身份未核验','no-sample':'尚未采样'}[id.status]||id.status;
  $('topbadges').innerHTML=`<span class="tag ${b.rtos_linked?'ok':'bad'}">${esc(b.rtos)} ${b.rtos_linked?'已链接':'未链接'}</span><span class="tag ${cls}">${esc(txt)}</span><span class="tag">${validSnaps.length} 有效帧 / ${LENS.snapshots.length} 次采集</span>`;
  $('identitycard').innerHTML=`<summary><span class="identity-label"><span class="seal ${cls}">${ic(sealIc)}</span><b>固件身份</b><span class="tag ${cls}">${esc(txt)}</span></span>
    <span class="identity-state${id.status==='verified'?' verified':''}">${id.status==='verified'?'固件与构建产物已匹配':'未核验：仅展示定义与原始读数'}</span><span class="identity-hint">核验详情</span></summary>
    <div class="identity-body"><div class="plain"><span class="ptag">${g('固件身份核验')}</span><span>确认「芯片里烧的程序」和「你这次编译的程序」是不是同一个。只有对得上，工具才敢解释内核状态；对不上就只给原始读数，避免张冠李戴。</span></div>
    <div class="note">${esc(id.reason||'')}${id.range?` · 比对范围 ${esc(id.range)}`:''}</div>
    <div style="margin-top:9px"><span class="fp">${g('AXF')} sha256 ${b.axf_sha?esc(b.axf_sha.slice(0,20))+'…':'未提供'}</span><span class="fp">${g('map 文件','map')} sha256 ${b.map_sha?esc(b.map_sha.slice(0,20))+'…':'未提供'}</span></div>
    ${id.status!=='verified'?'<div class="snote" style="margin-top:11px">身份未通过核验时，界面只展示原始读数与权威定义，停止解释 RTOS 对象。</div>':''}</div>`;
  $('contract').textContent=LENS.honesty.contract;
}

/* ---- Tab 切换 ---- */
const TABS=[['learn','学习实验'],['sched','调度快照'],['reg','寄存器位段'],['term','术语溯源'],['plat','平台对照'],['replay','回放/导出']];
$('tabs').innerHTML=TABS.map((t,i)=>`<button type="button" class="tab${i===0?' on':''}" id="tab-${t[0]}" data-v="${t[0]}" role="tab" tabindex="${i===0?0:-1}" aria-selected="${i===0}" aria-controls="view-${t[0]}" aria-label="${t[1]}" title="${t[1]}"><span class="tab-icon" aria-hidden="true">${ic(t[0],17)}</span><span class="tab-label">${t[1]}</span></button>`).join('');
const compactNav=matchMedia('(max-width:900px)'),navToggle=$('navtoggle');
function syncNavToggle(){
  const expanded=!$('workbench').classList.contains('is-nav-collapsed'),label=expanded?'收起功能导航':'展开功能导航';
  navToggle.setAttribute('aria-expanded',String(expanded));navToggle.setAttribute('aria-label',label);navToggle.title=label;
}
navToggle.addEventListener('click',()=>{$('workbench').classList.toggle('is-nav-collapsed');syncNavToggle();});syncNavToggle();
function revealNavTab(tab){
  if(!compactNav.matches)return;
  const nav=$('tabs'),left=tab.offsetLeft,right=left+tab.offsetWidth;
  if(left<nav.scrollLeft)nav.scrollLeft=left;else if(right>nav.scrollLeft+nav.clientWidth)nav.scrollLeft=right-nav.clientWidth;
}
function navOrientation(){
  $('tabs').setAttribute('aria-orientation',compactNav.matches?'horizontal':'vertical');
  const selected=document.querySelector('.tab.on');
  if(compactNav.matches&&document.activeElement===navToggle)selected.focus({preventScroll:true});
  revealNavTab(selected);
}
compactNav.addEventListener('change',navOrientation);addEventListener('resize',navOrientation);navOrientation();
function selTab(t){document.querySelectorAll('.tab').forEach(x=>{const on=x===t;x.classList.toggle('on',on);x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;});
  const view=$('view-'+t.dataset.v);
  document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v===view));
  const workspace=$('workbench'),y=workspace.getBoundingClientRect().top;
  if(y<-16)window.scrollTo({top:window.scrollY+y-16,behavior:'instant'});
  revealNavTab(t);
  if(window.__onTabShown)window.__onTabShown(view,t);
  history.replaceState(null,'','#'+t.dataset.v);}
$('tabs').addEventListener('click',e=>{const t=e.target.closest('.tab');if(t)selTab(t);});
$('tabs').addEventListener('keydown',e=>{const t=e.target.closest('.tab');if(!t)return;
  if(e.key==='Enter'||e.key===' '){e.preventDefault();selTab(t);}
  else if(['ArrowRight','ArrowLeft','ArrowDown','ArrowUp','Home','End'].includes(e.key)){
    e.preventDefault();const all=[...document.querySelectorAll('.tab')],i=all.indexOf(t);
    const index=e.key==='Home'?0:e.key==='End'?all.length-1:(i+(['ArrowRight','ArrowDown'].includes(e.key)?1:all.length-1))%all.length;
    const n=all[index];n.focus({preventScroll:true});selTab(n);}});

/* ---- V1 调度快照 ---- */
function taskBlock(e,cls){const t=e.tcb||{};return{k:(t.addr||e.item.addr),s:1,cls:cls,task:(t.name||''),l:`${t.name||'?'} p${t.priority??'?'}`,lt:`${t.name||'?'} · 到期 ${e.wake_tick??''}`};}
/* ---- 会话泳道：同一会话的多帧停核快照，逐任务显示状态 ---- */
const DIAG_CN={identity_mismatch:'固件身份不匹配',identity_unverified:'固件身份未核验',structure_invalid:'结构校验失败',resume_failed:'目标恢复失败',read_failed:'内存读取失败',ram_missing:'RAM 数据缺失',halt_failed:'停核失败',openocd_exited:'OpenOCD 退出',tcl_connect_failed:'调试器连接失败',tool_not_found:'采样工具未找到',tool_start_failed:'采样工具启动失败',probe_failed:'采样失败'};
function frameSessionId(s){return (s&&s.session&&s.session.id)||'legacy';}
function frameSessionFrames(cur){const id=frameSessionId(cur);return LENS.snapshots.filter(x=>frameSessionId(x)===id);}
function frameUsable(s){return !!s&&s.status==='ok'&&s.valid===true&&!!s.identity&&s.identity.status==='verified'&&s.resume_ok!==false&&!!s.decoded;}
function swimTaskState(s,name){
  if(!frameUsable(s)){const code=s&&s.diagnostic&&s.diagnostic.code;const msg=String((s&&s.diagnostic&&s.diagnostic.message)||'').slice(0,160);
    return{k:'bad',label:'✕',detail:(DIAG_CN[code]||code||'帧不可用')+(msg?' · '+msg:'')};}
  const dec=s.decoded,c=dec.current;
  if(c&&c.name===name)return{k:'run',label:'运行',detail:`运行中：pxCurrentTCB → ${c.addr}`,tcb:c,list:'pxCurrentTCB',name:name};
  const r=((dec.ready_priority1&&dec.ready_priority1.entries)||[]).find(e=>e.tcb&&e.tcb.name===name);
  if(r)return{k:'ready',label:'就绪',detail:`就绪：优先级 1 链表节点 ${r.item.addr} → TCB ${r.tcb.addr}`,tcb:r.tcb,item:r.item,list:'pxReadyTasksLists[1]',name:name};
  const d=((dec.delayed&&dec.delayed.entries)||[]).find(e=>e.tcb&&e.tcb.name===name);
  if(d)return{k:'delay',label:'延时',detail:`延时：到期 tick ${d.wake_tick} · 节点 ${d.item.addr}`,tcb:d.tcb,item:d.item,wake:d.wake_tick,list:'pxDelayedTaskList',name:name};
  return{k:'absent',label:'·',detail:'该帧未在已读取对象中观察到',name:name};
}
function swimProv(s,st){
  const tick=s.decoded&&s.decoded.scalars&&s.decoded.scalars.xTickCount&&s.decoded.scalars.xTickCount.value;
  const base={frame:s.session?`F${(s.session.frame_index??0)+1}`:'帧',host_time:s.host_time,session:(s.session&&s.session.id)||null,source:s.source};
  if(st.k==='bad')return{state:'unknown',value:null,prov:{...base,reason:st.detail,diagnostic:(s.diagnostic&&s.diagnostic.code)||null,note:'该帧不可用，任务状态不可知'}};
  if(st.k==='absent')return{state:'unknown',value:null,prov:{...base,reason:'该帧未在 pxCurrentTCB、优先级 1 就绪链表或当前延时链表中出现',note:'其他优先级就绪链表与溢出延时链表本期不读取；未出现不等于任务不存在'}};
  const q={...base,task:st.name,state_cn:st.label,list:st.list,tcb:st.tcb&&st.tcb.addr,priority:st.tcb&&st.tcb.priority,sampled_at:s.host_time};
  if(Number.isInteger(tick))q.tick=tick;
  if(st.k==='delay'){
    q.wake_tick=st.wake;q.item=st.item&&st.item.addr;
    q.item_hex=st.item&&Number.isInteger(st.item.xItemValue)?'0x'+(st.item.xItemValue>>>0).toString(16):null;
    if(Number.isInteger(tick)&&Number.isInteger(st.wake)){q.remaining_ticks=st.wake-tick;q.remaining_formula=`到期 ${st.wake} − 采样时 xTickCount ${tick}（仅该快照时刻）`;}
  }
  return{state:'derived',value:st.label,prov:q};
}
function renderSwim(cur){
  const el=$('swim');if(!el)return;
  const group=frameSessionFrames(cur),usable=group.filter(frameUsable);
  const rows=new Map();
  const add=t=>{if(!t||!t.name)return;const r=rows.get(t.name)||{name:t.name,priority:null,addr:null};if(r.priority==null&&Number.isInteger(t.priority))r.priority=t.priority;if(!r.addr&&t.addr)r.addr=t.addr;rows.set(t.name,r);};
  for(const t of (LENS.facts.tasks||[]))if(t&&t.name)rows.set(t.name,{name:t.name,priority:Number.isInteger(t.priority)?t.priority:null,addr:null,entry:t.entry});
  for(const s of usable){const d=s.decoded;add(d.current);((d.ready_priority1&&d.ready_priority1.entries)||[]).forEach(e=>add(e.tcb));((d.delayed&&d.delayed.entries)||[]).forEach(e=>add(e.tcb));}
  const list=[...rows.values()].sort((a,b)=>(b.priority??-1)-(a.priority??-1)||a.name.localeCompare(b.name));
  const ticks=usable.map(s=>s.decoded.scalars&&s.decoded.scalars.xTickCount&&s.decoded.scalars.xTickCount.value).filter(Number.isInteger);
  const delta=ticks.length>1?ticks[ticks.length-1]-ticks[0]:null;
  const bad=group.length-usable.length;
  const sm=cur.session||{};
  const started=sm.started_at?String(sm.started_at).replace('T',' ').slice(0,19):'';
  const label=started?`会话 · ${esc(started)}`:'历史记录（无会话元数据）';
  let summary=`<div class="swim-summary"><div><b>${label}</b> <span class="note">${group.length} 帧 · ${usable.length} 有效${bad?` · ${bad} 帧不可用`:''}${ticks.length>1?` · tick ${ticks[0]} → ${ticks[ticks.length-1]}（Δ ${delta<0?'回绕/不可比':delta}）`:''}</span></div>${sm.interval_s!=null&&group.length>1?`<span class="note mono">请求间隔 ${esc(sm.interval_s)} s（主机）</span>`:''}</div>`;
  let h=`${summary}<div class="swim-wrap" role="region" tabindex="0" aria-label="同一会话的多帧任务状态泳道"><table class="swim" style="min-width:${150+group.length*56}px"><thead><tr><th scope="col">任务 / TASK</th>`;
  group.forEach((s,j)=>{const ok=frameUsable(s),t=ok&&s.decoded.scalars&&s.decoded.scalars.xTickCount,fi=Number.isInteger(s.session&&s.session.frame_index)?s.session.frame_index:j;
    const code=s&&s.diagnostic&&s.diagnostic.code;
    h+=`<th scope="col" class="fhead${ok?'':' fbad'}${s===cur?' on':''}" title="${esc(String(s.host_time||'')+(ok?' · 暂停 '+s.pause_ms+' ms':' · '+(DIAG_CN[code]||code||'不可用')))}"><b>F${fi+1}</b><span>${ok&&t?esc(t.value):'不可用'}</span></th>`;});
  h+='</tr></thead><tbody>';
  for(const r of list){
    h+=`<tr><th scope="row" title="${esc((r.entry?r.entry+' · ':'')+(r.priority!=null?'优先级 '+r.priority:'优先级未知'))}"><b>${esc(r.name)}</b><span>${r.priority!=null?'p'+r.priority:''}${r.addr?` · ${esc(r.addr)}`:''}</span></th>`;
    for(const s of group){const st=swimTaskState(s,r.name),prov=swimProv(s,st),clickable=st.k!=='bad'&&st.k!=='absent';
      const fi=Number.isInteger(s.session&&s.session.frame_index)?s.session.frame_index:group.indexOf(s);
      const al=st.k==='bad'?'帧不可用':st.k==='absent'?'未在已读取对象中出现':st.label;
      h+=`<td class="cell s-${st.k}${s===cur?' on':''}" ${clickable?'tabindex="0" role="button"':''} data-prov='${esc(JSON.stringify(prov))}' title="${esc(st.detail)}" aria-label="${esc(r.name)} · F${fi+1} · ${esc(al)}"><span class="st">${st.label}${st.k==='delay'?`<em>${esc(st.wake)}</em>`:''}</span></td>`;}
    h+='</tr>';
  }
  h+='</tbody></table></div>';
  h+=`<div class="swim-legend"><span><i class="i-run"></i>运行中（当前选中）</span><span><i class="i-ready"></i>就绪（优先级 1）</span><span><i class="i-delay"></i>延时（数字＝到期 tick）</span><span><i class="i-absent"></i>未在已读链表中出现</span><span><i class="i-bad"></i>帧不可用</span></div>
    <div class="note">每列是一帧停核快照；帧与帧之间目标仍在运行，可能漏采，不能据此推断任务切换时刻。只读取当前任务、优先级 1 就绪链表、当前延时链表与所选寄存器；其他优先级就绪链表和溢出延时链表不在观察范围，未出现的任务标为不可知，不代表不存在。</div>`;
  el.innerHTML=h;
}
function renderSched(){
  const root=$('view-sched');
  const heading=`<div class="view-head"><div><h2>调度快照</h2><p>看清任务的就绪、延时与当前选中状态。</p></div><span class="view-index">01 / SCHEDULER</span></div>`;
  if(!validSnaps.length){
    root.innerHTML=heading+`<div class="card snapshot-empty"><div class="empty-symbol" aria-hidden="true">${ic('sched')}</div>
      <h3>等待第一帧真实快照</h3><p>当前没有身份已核验的板上数据。<br>你仍然可以查看寄存器定义与源码解读，实测状态会在采样后呈现。</p>
      <div class="btns"><button class="btn" data-readopen>一键读取${ic('arrow')}</button><button class="btn sec" data-jump="reg">查看寄存器定义</button><button class="btn sec" data-jump="term">查看源码解读</button></div>
      <dl class="empty-metrics"><div><dt>当前任务</dt><dd>不可知</dd></div><div><dt>系统 tick</dt><dd>不可知</dd></div><div><dt>到期 tick</dt><dd>不可知</dd></div></dl>
      <details class="learn-more"><summary>如何获得真实快照？</summary><div class="lesson-body note" style="text-align:left">连接 ST-LINK 后运行 <span class="mono">elens sample --frames 5 --interval 1</span>（一次会话连拍 5 帧），或导入 Keil 手工采集，再重新导出网页。固件身份核验通过后，才会解释任务与调度状态；没有证据的数值始终标为「不可知」。</div></details></div>`;
    const ls=LENS.snapshots[LENS.snapshots.length-1];
    const raw=[...((ls&&ls.notes)||[]), ...((ls&&ls.identity&&ls.identity.reason)?[ls.identity.reason]:[])];
    const msgs=[...new Set(raw)];
    if(msgs.length){
      const full=msgs.join('\n\n');
      root.insertAdjacentHTML('beforeend',`<details class="sample-log"><summary>最近一次采样未产出可用帧 · 查看探针日志</summary><div class="mono note">${esc(full)}</div><button class="btn sec" data-study-open="diagnosis" style="margin-bottom:16px">查看排查步骤</button></details>`);
    }
    return;
  }
  root.innerHTML=heading+`<div class="card"><div class="section-head"><h3>任务状态</h3><span class="note">${g('停核采样','停核快照')} · ${g('离散快照')}</span></div>
    <div class="demo-head"><div class="note" id="sdesc"></div>
      <div class="btns"><span class="idx" id="sidx"></span>
      <button class="btn sec" id="sprev">${ic('prev')}上一帧</button><button class="btn" id="snext">下一帧${ic('next')}</button><button class="btn sec" id="sreset">${ic('reset')}重置</button></div></div>
    <div id="snotes"></div>
    <div id="scur" class="current-task"></div>
    <div class="grid2 scheduler-lists">
      <div><div class="note mono">优先级 1 ${g('就绪链表')} <span id="raddr"></span></div>
        <div class="heapbar" id="rbar"></div><div id="rlbl" style="display:flex"></div><div class="cap" id="rcap"></div></div>
      <div><div class="note mono">当前${g('延时链表')} <span id="daddr"></span></div>
        <div class="heapbar" id="dbar"></div><div id="dlbl" style="display:flex"></div><div class="cap" id="dcap"></div></div>
    </div>
    <div class="scheduler-timeline"><div class="section-head"><h3>会话泳道</h3><span class="note">离散采样 · 帧间可能漏采</span></div><div id="swim"></div></div>
    <div class="note">到期 ≠ 实际执行 ≠ GPIO 动作；当前选中任务可同时位于就绪链表。</div>
    <details class="learn-more"><summary>读懂调度视图与内核原始值</summary><div class="plain"><span>左边是<b>准备好能跑</b>的任务，右边是<b>正在延时</b>的任务。点任务块可跳回源码。${g('到期 tick','延时到期')}只代表具备重新就绪条件，并不保证立即执行。</span></div><div id="sraw" class="lesson-body"></div></details></div>`;
  const rb=bar($('rbar'),$('rlbl')),db=bar($('dbar'),$('dlbl'));
  const st=stepper(validSnaps.length,i=>{
    const s=validSnaps[i],dec=s.decoded;
    $('sdesc').innerHTML=`停核快照 · 主机采样 ${esc(s.host_time)} · 暂停 ${val({state:'measured',value:s.pause_ms,prov:{source:'主机单调时钟',unit:'ms'}})} ms · 来源 ${esc(s.source)}`;
    $('snotes').innerHTML=(s.notes&&s.notes.length)?`<div class="snote"><b>采样警示</b><br>${s.notes.map(n=>esc(n)).join('<br>')}</div>`:'';
    const c=dec.current;
    $('scur').innerHTML=c?`<b class="mono">${g('当前任务','当前选中任务')}：${esc(c.name)}</b> · ${g('优先级')} ${val({state:'measured',value:c.priority,prov:{addr:c.addr,field:'uxPriority'}})} · ${g('TCB')} ${val({state:'measured',value:c.addr,prov:{addr:dec.current_tcb_ptr,hex:c.name_hex}})} <span class="note">（名字读自 TCB.pcTaskName）</span>`:'当前任务不可知';
    $('raddr').textContent=dec.ready_priority1.list_addr;
    rb(dec.ready_priority1.entries.map(e=>taskBlock(e,e.is_current?'c-cur':'c-a')));
    $('rcap').textContent=`节点 ${dec.ready_priority1.entries.length} · 校验 ${dec.ready_priority1.valid?'通过':'失败'}`;
    const dl=dec.delayed;
    $('daddr').textContent=dl?dl.list_addr:'—';
    db(dl?dl.entries.map(e=>taskBlock(e,'c-b')):[]);
    $('dcap').textContent=dl?`${dl.which} · 节点 ${dl.entries.length} · 校验 ${dl.valid?'通过':'失败'}`:'无延时链表';
    let raw='';for(const[k,v]of Object.entries(dec.scalars))raw+=`<span class="chip">${k} = ${val(v,k!=='xSchedulerRunning')}</span>`;
    $('sraw').innerHTML=raw;
    renderSwim(s);
    $('sidx').textContent=(i+1)+' / '+validSnaps.length;
    if(window.__frameIn)window.__frameIn();
  });
  $('snext').onclick=st.next;$('sprev').onclick=st.prev;$('sreset').onclick=st.reset;
  const nameToEntry={};(LENS.facts.tasks||[]).forEach(t=>nameToEntry[t.name]=t.entry);
  const rev=e=>{const blk=e.target.closest('.blk');if(!blk||!blk.dataset.task)return;
    const fn=nameToEntry[blk.dataset.task];document.querySelector('.tab[data-v="term"]').click();
    const card=document.querySelector('#view-term .term[data-fn~="'+fn+'"]');
    if(card){if(window.__scrollToEl)window.__scrollToEl(card);else card.scrollIntoView({behavior:'smooth',block:'center'});card.classList.add('lit');setTimeout(()=>card.classList.remove('lit'),1600);}};
  $('dbar').addEventListener('click',rev);$('rbar').addEventListener('click',rev);
}

/* ---- V2 寄存器位段 ---- */
let REG_BIT=null,REG_PICK=null,REG_ALL=false;
function regFrameLabel(s,j){const fi=s&&s.session&&Number.isInteger(s.session.frame_index)?s.session.frame_index:j;return 'F'+(fi+1);}
function regTick(s){const t=s&&s.decoded&&s.decoded.scalars&&s.decoded.scalars.xTickCount;return t&&Number.isInteger(t.value)?t.value:null;}
function regAddrOk(s,addr){const o=s&&s.gpio_odr;return !!(o&&o.prov&&String(o.prov.addr||'').toLowerCase()===String(addr).toLowerCase());}
function regFrames(addr){return validSnaps.filter(s=>s.gpio_odr&&s.gpio_odr.state==='measured'&&regAddrOk(s,addr));}
function regFieldAt(fields,b){for(const f of fields)if(b>=f.bit_offset&&b<f.bit_offset+f.bit_width)return f;return null;}
function regFieldValue(v,f){const w=f.bit_width||1;return w>=32?(v>>>0):((v>>>f.bit_offset)&((1<<w)-1));}
function regBitOf(s,b){const o=s&&s.gpio_odr;return o&&o.state==='measured'?((o.value>>>b)&1):null;}
function regDetailHtml(per,pins,pinBits,writesByBit,frames,pick,b){
  const r=LENS.structure.register,f=regFieldAt(r.fields||[],b);
  const v=pick?regBitOf(pick,b):null;
  const meas=v===null?uval('没有与定义地址一致、身份已核验的采样'):val({state:'measured',value:v,prov:{addr:r.address,bit:b,register:'0x'+((pick.gpio_odr.value>>>0).toString(16)),sampled_at:(pick.gpio_odr.prov||{}).sampled_at||pick.host_time,source:(pick.gpio_odr.prov||{}).source||pick.source,frame:regFrameLabel(pick,frames.indexOf(pick))}});
  const fw=f?(f.bit_width||1):1,maskStr=fw>=32?'0xffffffff':'0x'+((1<<fw)-1).toString(16);
  const fieldVal=(v!==null&&f)?val({state:'derived',value:regFieldValue(pick.gpio_odr.value,f),prov:{formula:`(VALUE >>> ${f.bit_offset}) & ${maskStr}`,inputs:{register:'0x'+((pick.gpio_odr.value>>>0).toString(16)),offset:f.bit_offset,width:f.bit_width}}}):null;
  const pinName=pinBits[b],pin=pinName?pins[pinName]:null;
  const ws=writesByBit[b]||[],hs=LENS.facts.hal_gpio_pin_state||{};
  const hist=frames.map((s,j)=>{const x=regBitOf(s,b);return `<button type="button" class="hist-chip${x?' on':''}${s===pick?' sel':''}" data-regframe="${esc(s.id)}" title="${esc(String(s.host_time||''))} · tick ${regTick(s)??'—'}">${regFrameLabel(s,j)}<b>${x===null?'?':x}</b></button>`;}).join('');
  const writes=ws.length?ws.map(w=>`<div class="bd-write"><span class="mono">${esc(fileBase(w.file))}:${esc(w.line)}</span> · ${esc(w.in_fn||'未识别函数')} → ${esc(w.port_macro)} / ${esc(w.pin_macro)} = ${esc(w.state)}${hs[w.state]?` (${hs[w.state].value})`:''}</div>`).join(''):'<span class="note">未识别到写这一位的 HAL 调用；不代表没有其他写者（中断、Toggle 或直接寄存器写）。</span>';
  const range=f?(f.bit_width>1?`bit ${f.bit_offset+f.bit_width-1}:${f.bit_offset}`:`bit ${f.bit_offset}`):null;
  return `<aside class="bit-detail" id="bitdetail" aria-live="polite">
    <h4>bit ${b}${f?` · ${esc(f.name)}`:''}<span class="tag ${f?'acc':''}">${f?'SVD 定义':'未定义'}</span></h4>
    <div class="bd-sub">${esc(per.name)} / ${esc(r.name)}${range?' · '+esc(range):' · SVD 未给出位定义'}</div>
    <dl>
      <dt>实测位值</dt><dd>${meas}</dd>
      ${f?`<dt>本段字段值</dt><dd>${fieldVal??uval('无实测值，字段值不可知')} <span class="note">宽 ${f.bit_width} 位 · 访问 ${esc(f.access||'未提供')}</span></dd>`:''}
      <dt>SVD 说明</dt><dd>${f?esc(f.description||'SVD 未提供描述'):'SVD 未定义此位，不猜测其含义。'}</dd>
      <dt>引脚映射</dt><dd>${pin?`${esc(pinName)} · ${esc(pin.port)} bit ${pin.bit}<span class="note">${esc(fileBase(pin.file))}:${pin.Pin?pin.Pin.line:''}</span>`:'无源码确认的引脚映射（不可知）'}</dd>
      <dt>源码写入</dt><dd>${writes}</dd>
      <dt>各帧实测</dt><dd><div class="bit-hist">${hist||'<span class="note">无地址一致的有效帧</span>'}</div><div class="note" style="margin-top:6px">离散采样，帧间变化不可知；位值不代表灯的实际亮灭。</div></dd>
    </dl></aside>`;
}
function renderReg(){
  const r=LENS.structure.register,per=LENS.structure.peripheral,pins=LENS.facts.pins||{};
  const fields=(r.fields||[]).slice().sort((a,b)=>a.bit_offset-b.bit_offset);
  const maxField=fields.reduce((m,f)=>Math.max(m,f.bit_offset+f.bit_width),0);
  const bitCount=Math.max(8,Math.min(64,Math.max(Number(r.size_bits)||8,maxField)));
  const defaultBits=Math.min(bitCount,Math.ceil(Math.max(16,maxField)/8)*8);
  const displayBits=REG_ALL?bitCount:defaultBits;
  const pinBits={};
  for(const[k,p]of Object.entries(pins))if(p.confirmed_from_source&&Number.isInteger(p.bit)&&p.port===per.name)pinBits[p.bit]=k;
  const writesByKey={};
  for(const w of (LENS.facts.gpio_writes||[])){const k=String(w.pin_macro||'').replace(/_Pin$/,'');if(k)(writesByKey[k]=writesByKey[k]||[]).push(w);}
  const writesByBit={};
  for(const[b,k]of Object.entries(pinBits)){const ws=writesByKey[k]||[];if(ws.length)writesByBit[b]=ws;}
  const frames=regFrames(r.address);
  const omitted=validSnaps.length-frames.length;
  const pick=frames.find(s=>s.id===REG_PICK)||frames[frames.length-1]||null;
  const odr=pick?pick.gpio_odr:null;
  if(!Number.isInteger(REG_BIT)||REG_BIT<0||REG_BIT>=displayBits){
    const wb=Object.keys(writesByBit).map(Number).filter(Number.isInteger).sort((a,b)=>a-b);
    const pb=Object.keys(pinBits).map(Number).filter(Number.isInteger).sort((a,b)=>a-b);
    REG_BIT=wb[0]??pb[0]??(fields.length?fields[0].bit_offset:0);
  }
  let bits='';
  for(let b=0;b<displayBits;b++){
    const f=regFieldAt(fields,b),set=odr?((odr.value>>>b)&1):null,pinName=pinBits[b];
    const label=f?(f.bit_width>1&&b!==f.bit_offset?'↳':f.name):('b'+b);
    const range=f?(f.bit_width>1?`bit ${f.bit_offset+f.bit_width-1}:${f.bit_offset}`:`bit ${f.bit_offset}`):'SVD 未定义';
    const desc=f?`${f.name} · ${range} · ${f.description||''}`:'SVD 未定义此位，不猜测含义';
    bits+=`<button type="button" class="bit${pinName?' hi':''}${set===1?' set':''}${b===REG_BIT?' sel':''}${f?'':' res'}" data-bit="${b}" aria-pressed="${b===REG_BIT}" aria-label="bit ${b} ${esc(f?f.name:'未定义')} ${set===null?'实测不可知':'实测 '+set}" title="${esc(desc)}"><span class="bn">${esc(label)}</span><span class="bv">${set===null?'?':set}</span><span class="bit-pin">${pinName?esc(pinName):(f?'':'—')}</span></button>`;
  }
  const digits=Math.max(4,Math.min(16,Math.ceil((Number(r.size_bits)||32)/4)));
  const strip=frames.map((s,j)=>{const v=s.gpio_odr.value>>>0;return `<button type="button" class="reg-frame-chip${s===pick?' on':''}" data-regframe="${esc(s.id)}" aria-pressed="${s===pick}" title="${esc(String(s.host_time||''))} · tick ${regTick(s)??'—'}">${regFrameLabel(s,j)} <b>0x${v.toString(16).toUpperCase().padStart(digits,'0')}</b></button>`;}).join('');
  const tick=regTick(pick);
  const frameNote=pick?`${regFrameLabel(pick,frames.indexOf(pick))} · ${esc(String(pick.host_time||''))}${tick!==null?` · tick ${tick}`:''} · 身份已核验`:'尚无与定义地址一致、身份已核验的采样读数，不推测引脚状态';
  const bin=odr?('0b'+((odr.value>>>0).toString(2).padStart(Math.min(bitCount,32),'0')).replace(/(.{4})(?=.)/g,'$1 ')):'';
  const detail=regDetailHtml(per,pins,pinBits,writesByBit,frames,pick,REG_BIT);
  const fieldRows=fields.map(f=>{const hi=f.bit_offset+f.bit_width-1,pin=f.bit_width===1?pinBits[f.bit_offset]:null,ws=pin?writesByKey[pin]||[]:[];
    return `<tr><td class="m">${hi===f.bit_offset?'bit '+f.bit_offset:hi+':'+f.bit_offset}</td><td class="m">${esc(f.name)}</td><td>${f.bit_width}</td><td>${esc(f.access||'—')}</td><td>${pin?`${esc(pin)}${ws.length?` · ${ws.length} 处写入`:''}`:'—'}</td><td>${esc(f.description||'')}</td></tr>`;}).join('');
  let pintab='';
  for(const[k,p]of Object.entries(pins)){
    const ws=writesByKey[k]||[],states=[...new Set(ws.map(w=>w.state))],here=p.port===per.name;
    pintab+=`<tr${here?'':' class="pin-other"'}><td>${esc(k)}</td><td class="m">${esc(p.port)} · bit ${p.bit??'?'}</td><td>${ws.length?`${ws.length} 处 · ${states.map(esc).join(' / ')}`:'无'}</td><td>${p.confirmed_from_source?'<span class="tag ok">源码已确认</span>':'未确认'}</td><td class="m note">${esc(p.file)}:${p.Pin?p.Pin.line:''}</td></tr>`;
  }
  const hs=LENS.facts.hal_gpio_pin_state||{};
  const hsNote=Object.keys(hs).length?`HAL 枚举：${Object.entries(hs).map(([k,v])=>`${k}=${v.value}`).join(' / ')}`:'';
  $('view-reg').innerHTML=`<div class="view-head"><div><h2>寄存器位段</h2><p>从一位的实测值，追到 SVD 定义、源码写入与采样时刻。</p></div><span class="view-index">02 / REGISTER</span></div>
    <div class="card"><div class="section-head"><h3 class="mono">${esc(per.name)} <span style="color:var(--faint)">/</span> ${esc(r.name)}</h3><span class="note mono">${esc(r.size_bits)}-BIT REGISTER</span></div>
    <div class="readout-grid"><div class="readout"><div class="readout-label">定义地址 / ADDRESS</div>
      <div class="readout-value">${val({state:'authoritative',value:r.address,prov:{file:LENS.structure.svd.file,version:LENS.structure.svd.version,offset:r.offset}})}</div>
      <div class="note">定义来自 ${esc(r.defined_in)}${per.derivedFrom?` (${g('derivedFrom')} ${esc(per.derivedFrom)})`:''}</div></div>
      <div class="readout"><div class="readout-label">采样读数 / VALUE</div>
      <div class="readout-value">${odr?val(odr,true):uval('没有与定义地址一致、身份已核验的采样读数')}</div>
      ${bin?`<div class="readout-bin">${esc(bin)}</div>`:''}
      <div class="note">${frameNote}${omitted>0?` · 另有 ${omitted} 个有效帧没有地址一致的寄存器读数，未采用`:''}</div></div></div>
    <div class="reg-frames"><span class="note mono">采样帧</span>${strip||'<span class="note">无地址一致且身份已核验的帧</span>'}<span class="note">点击切换本视图所用帧 · 只采用地址一致且身份已核验的读数</span></div>
    <div class="reg-layout">
      <div class="register-map"><div class="section-head"><h3>引脚位图</h3><div class="map-legend"><span><i></i>源码确认</span><span><i class="set"></i>实测 1</span><span><i class="clear"></i>实测 0</span><span><i class="unknown"></i>? 不可知</span></div></div>
        <div class="bits">${bits}</div><div class="reg-bits-foot"><div class="note">高亮映射：${Object.keys(pinBits).length?Object.entries(pinBits).map(([b,k])=>'bit '+b+' → '+esc(k)).join(' · '):'无已确认引脚'} · 点击任一位查看 SVD 定义、实测来源与源码写入；${fields.length?'↳ 表示同一位段的延续位，bN 表示 SVD 未定义':'SVD 未提供字段'}。${bitCount>displayBits?` 当前显示 bit 0–${displayBits-1}，高 ${bitCount-displayBits} 位 SVD 未定义，未展开。`:''}</div>${bitCount>defaultBits?`<button type="button" class="chip" data-regall="1" aria-pressed="${REG_ALL}">${REG_ALL?'只看已定义范围':`显示全部 ${bitCount} 位`}</button>`:''}</div></div>
      ${detail}
    </div>
    <div class="view-foot"><span>位值不代表灯的亮灭，实际效果取决于硬件接法。</span><span class="mono">${esc(r.description)}</span></div>
    <details class="learn-more"><summary>如何阅读寄存器位图与证据？</summary><div class="plain"><span>每个格子对应${g('寄存器')}中的一位。字段名来自 SVD；对于 ${g('ODR')}，位值 1 表示输出锁存器置位，0 表示复位；实际引脚电平还取决于引脚模式。实测值只在地址一致且身份核验的帧中显示，「?」表示不可知。源码写入只说明写入意图，不等于代码已执行或引脚电平；其他任务、中断、Toggle、直接寄存器写和硬件接法未覆盖。GPIO_PIN_SET 是置位操作，置哪一位由 pin 参数决定。</span></div></details></div>
    <details class="card mapping-details"><summary><b>SVD 字段定义</b><span class="note">权威定义 · ${fields.length} 个字段</span></summary>
      <div class="table-scroll" tabindex="0" role="region" aria-label="SVD 字段定义表"><table><thead><tr><th>位段</th><th>名称</th><th>宽</th><th>访问</th><th>关联引脚/写入</th><th>说明</th></tr></thead><tbody>${fieldRows}</tbody></table></div>
      <div class="note mono" style="margin-top:12px">来源：${esc(LENS.structure.svd.file)}（版本 ${esc(LENS.structure.svd.version)}）· 仅解析所选寄存器所需定义。</div></details>
    <details class="card mapping-details"><summary><b>引脚映射与写入证据</b><span class="note">设备头 + 源码 · ${Object.keys(pins).length} 项</span></summary>
      <div class="table-scroll" tabindex="0" role="region" aria-label="引脚映射与写入证据表"><table class="pin-table"><thead><tr><th>符号</th><th>端口/位</th><th>已识别写入</th><th>确认</th><th>来源</th></tr></thead><tbody>${pintab}</tbody></table></div>
      <div class="note">${hsNote?hsNote+' · ':''}写入状态是参数意图，不等于代码已执行或引脚电平；其他写者未覆盖。灰度行表示引脚不在当前所选寄存器端口。</div>
      <div class="note mono" style="margin-top:12px">${g('GPIO_TypeDef')} 布局来自 ${esc(LENS.structure.header.file)} · SVD/头文件一致性：${LENS.structure.cross_check&&LENS.structure.cross_check.svd_header_agree?'一致':'需复核'}</div></details>`;
}
document.addEventListener('click',e=>{
  const all=e.target.closest('#view-reg [data-regall]');
  if(all){REG_ALL=!REG_ALL;renderReg();const n=document.querySelector('#view-reg [data-regall]');if(n)n.focus({preventScroll:true});return;}
  const bit=e.target.closest('#view-reg .bit[data-bit]');
  if(bit){REG_BIT=Number(bit.dataset.bit);renderReg();const n=document.querySelector('#view-reg .bit[data-bit="'+REG_BIT+'"]');if(n)n.focus({preventScroll:true});return;}
  const chip=e.target.closest('#view-reg [data-regframe]');
  if(chip){REG_PICK=chip.dataset.regframe;renderReg();const n=[...document.querySelectorAll('#view-reg [data-regframe]')].find(x=>x.dataset.regframe===REG_PICK);if(n)n.focus({preventScroll:true});}
});

/* ---- V3 术语溯源 ---- */
function dval(disp,formula,inputs){const o={state:'derived',value:disp,prov:{formula:formula,inputs:inputs||null}};
  return `<span class="v d" data-prov='${esc(JSON.stringify(o))}'>${esc(disp)}<i class="bdg">推导</i></span>`;}
function uval(reason){const o={state:'unknown',value:null,prov:{reason:reason}};
  return `<span class="v u" data-prov='${esc(JSON.stringify(o))}'>不可知<i class="bdg">不可知</i></span>`;}
function msFmt(x){const n=+x;return Number.isInteger(n)?String(n):String(+n.toFixed(2));}
function secFmt(x){return String(+x.toFixed(6));}
function fileBase(p){return String(p||'').split(/[\\/]/).pop();}

function delayTermCard(grp,gi){
  const t=grp[0],ticks=t.passed.value,hz=t.decider.value;
  if(ticks===0)return `<div class="term term-deep" data-fn="${esc(grp.map(x=>x.source.fn||'').join(' '))}"><div class="thead"><h3>vTaskDelay(0)</h3></div><p class="tlead">让出本次执行机会，不设置正延时；是否切换到其他任务仍由调度器决定。</p><div class="note">参数 ${val(t.passed)} tick · ${grp.map(x=>esc(fileBase(x.source.file))+':'+esc(x.source.line)).join(' / ')}</div></div>`;
  const period=1000/hz,lo=(ticks-1)*period,hi=ticks*period,sec=ticks/hz;
  const byFn=new Map();
  grp.forEach(x=>{const fn=x.source.fn||'未命名函数';if(!byFn.has(fn))byFn.set(fn,[]);byFn.get(fn).push(x);});
  const fns=[...byFn.keys()];
  const counts=[...byFn.values()].map(a=>a.length);
  const uniformCount=counts.every(c=>c===counts[0])?counts[0]:null;
  const srcs=grp.map(x=>`<span class="src" data-link="cfg-${gi}">${esc(fileBase(x.source.file))}:${esc(x.source.line)} ${esc(x.source.fn||'')} → vTaskDelay(${esc(x.passed.value)})</span>`).join('');
  const cfgFile=fileBase(t.decider.prov&&t.decider.prov.file)||'配置文件';
  const cfgLine=t.decider.prov&&t.decider.prov.line!=null?String(t.decider.prov.line):'';
  const cfgLoc=cfgLine?`${cfgFile}:${cfgLine}`:cfgFile;
  const tickless=(LENS.facts&&LENS.facts.config&&LENS.facts.config.configUSE_TICKLESS_IDLE)||null;
  const slicing=(LENS.facts&&LENS.facts.config&&LENS.facts.config.configUSE_TIME_SLICING)||null;
  const wrap=Math.pow(2,32)/hz/86400;
  const last=validSnaps[validSnaps.length-1];
  let seen='';
  if(last){
    const names=new Set(((LENS.facts&&LENS.facts.tasks)||[]).filter(x=>fns.indexOf(x.entry)>=0).map(x=>x.name));
    const dl=last.decoded&&last.decoded.delayed;
    const e=dl&&dl.entries?dl.entries.find(en=>en.tcb&&names.has(en.tcb.name)):null;
    const tc=last.decoded&&last.decoded.scalars&&last.decoded.scalars.xTickCount;
    if(e&&e.wake_tick!=null){
      const wv={state:'measured',value:e.wake_tick,prov:{addr:(e.item&&e.item.addr)||null,field:'xItemValue（延时链表节点）',hex:'0x'+(e.wake_tick>>>0).toString(16),sampled_at:last.sampled_at||last.host_time||null,source:last.source||null}};
      let rem='';
      if(tc&&tc.value!=null){const rv={state:'derived',value:e.wake_tick-tc.value,prov:{formula:`到期 ${e.wake_tick} − 采样时的 xTickCount ${tc.value}`,inputs:{wake:e.wake_tick,tick:tc.value}}};
        rem=` · 采样时 xTickCount = ${val(tc)} → 还差 ${val(rv)} tick`;}
      seen=`最后一个有效帧的延时链表里读到了该任务的节点：到期 tick = ${val(wv)}（实测）${rem}。`;
    }else{seen='最后一个有效帧的延时链表里没有找到这些任务的节点（可能正好在就绪链表或被选中运行）。样本是离散的，这不等于它们没有延时。';}
  }else{
    seen=`当前载荷没有可用的实测帧（采样记录见 V1）→ 到期 tick ${uval('没有有效快照；需接调试器采样或导入手工采集')}。不要用「采样 tick + ${ticks}」反推：到期 tick 是调用那一刻算的，两者不是同一时刻。`;
  }
  const half=Math.max(1,Math.round(ticks/2));
  const hz2=hz*10;
  return `<div class="term term-deep" data-fn="${esc(fns.join(' '))}">
    <div class="thead"><h3>vTaskDelay(${esc(ticks)})</h3><span class="tag acc">${byFn.size} 个函数 · ${grp.length} 处调用</span></div>
    <p class="tlead">这行代码设置 <b>${ticks} 个节拍</b>的相对延时，tick 不是固定的毫秒单位。本工程心跳 <b>${hz} Hz</b>，名义上是 <b>${secFmt(sec)} 秒</b>；它只决定「最早什么时候能再跑」，不保证准时执行。</p>
    <div class="tq">
      <div><span class="k">① 传了什么</span><span class="big">${val(t.passed)}<em>tick</em></span><span class="n">节拍数。代码里看不出实际时长——单位换算由 ② 决定。</span></div>
      <div><span class="k">② 谁决定效果</span><span class="big">${val(t.decider)}<em>Hz</em></span><span class="n">${g('configTICK_RATE_HZ')}（${esc(cfgLoc)}）→ 1 tick = ${dval(msFmt(period)+' ms',`1 s ÷ ${hz} = ${msFmt(period)} ms`,{hz:hz})}。</span></div>
      <div><span class="k">③ 等于多久</span><span class="big">${val(t.derived)}<em>s</em></span><span class="n">${esc(t.derived.prov&&t.derived.prov.formula||'')}；按心跳边界唤醒，实际落在 ${dval(msFmt(lo)+'–'+msFmt(hi)+' ms',`(${ticks}−1) × ${msFmt(period)} ms ～ ${ticks} × ${msFmt(period)} ms；不含调度延迟`,{ticks:ticks,period_ms:msFmt(period)})}。</span></div>
    </div>
    <details class="term-details"><summary>查看调用来源、内核过程与换算依据</summary><div class="term-detail-grid"><div class="srcrow">${srcs}</div>
    <div class="tsec"><div class="hd">内核里发生了什么（FreeRTOS 相对延时）</div>
      <ol class="flow">
        <li>先把当前任务从<b>就绪链表</b>摘下——它暂时退出「谁来跑」的竞争。</li>
        <li>算到期时刻：<code>到期 tick = 调用时的 <b>xTickCount</b> + ${ticks}</code>。这是 32 位无符号加法，加过头就进${g('延时链表','溢出延时链表')}。</li>
        <li>按到期先后<b>升序</b>插进延时链表 <code>pxDelayedTaskList</code>；表头就是最早醒来的任务。</li>
        <li>之后每个节拍只看一个数：<code>${g('xNextTaskUnblockTime')}</code>（链表非空时 = 表头最早到期值；链表空时是占位用的最大值）。到点后把任务搬回就绪链表。</li>
        <li>搬回只代表「有资格跑」：还要等调度器选中；同优先级任务是否按时间片轮转，由 configUSE_TIME_SLICING 决定（本工程配置见下方「同优先级」一行）。</li>
      </ol>
      <div class="note">${seen}</div>
    </div>
    <div class="tsec"><div class="hd">精度与换算</div>
      <dl class="kv">
        <dt>心跳周期</dt><dd>${dval(msFmt(period)+' ms',`1 ÷ ${hz} Hz`,{hz:hz})}。这是全工程的「时间尺子」，不是这行代码自带的。</dd>
        <dt>实际睡眠</dt><dd>${dval(msFmt(lo)+'–'+msFmt(hi)+' ms',`(${ticks}−1) × ${msFmt(period)} ms ～ ${ticks} × ${msFmt(period)} ms；调用时刻离下一次心跳越近，越接近下限`,{ticks:ticks,period_ms:msFmt(period)})}；若被更高优先级长期占用，还会更晚（不可知）。</dd>
        <dt>时间分辨率</dt><dd>${dval(msFmt(period)+' ms',`1 tick = ${msFmt(period)} ms；只能按整数拍设置`,{period_ms:msFmt(period)})}。写不出半拍：<code>vTaskDelay(1)</code> 的实际睡眠是 0–${msFmt(period)} ms。</dd>
        <dt>一圈要睡几次</dt><dd>${uniformCount
          ?`每个函数里相同的调用有 ${uniformCount} 处（共 ${grp.length} 处）：若一圈内都执行到，仅延时约 ${dval(secFmt(uniformCount*sec)+' s',`${uniformCount} × ${ticks} tick ÷ ${hz} Hz`,{calls:uniformCount,ticks:ticks,hz:hz})}，再加本圈执行时间（未测量 → 不可知）。本工具按调用点数量推算，不解析控制流。`
          :`各函数调用数不同（${fns.map(f=>esc(f)+'：'+byFn.get(f).length+' 处').join('，')}），一圈延时代价取决于控制流（不可知）；单次延时名义 ${secFmt(sec)} s。`}要固定节拍用 ${g('vTaskDelayUntil')}。</dd>
        <dt>回绕</dt><dd>tick 按默认配置是 32 位计数（若启用 configUSE_16_BIT_TICKS 则为 16 位），${hz} Hz 下约 ${dval(wrap.toFixed(1)+' 天',`2^32 ÷ ${hz} Hz ÷ 86400 s/天`,{hz:hz})}回绕一次；跨回绕点的任务进溢出链表，回绕时两条延时链表互换，延时不会因此变短。</dd>
        ${tickless?`<dt>省电暂停</dt><dd>configUSE_TICKLESS_IDLE = ${tickless.value}${tickless.value===0?'（权威配置）：心跳固定不停，不会为省电暂停。':'（权威配置）：开启 tickless 时心跳可能被省电逻辑暂停/补偿，实际时长需另判。'}</dd>`:''}
        ${slicing?`<dt>同优先级</dt><dd>configUSE_TIME_SLICING = ${slicing.value}${slicing.value?'（权威配置）：同优先级任务按 1 个 tick 的时间片轮转。':'（权威配置）：同优先级不按时间片轮转。'}</dd>`:''}
      </dl>
    </div>
    <div class="tsec"><div class="hd">图上怎么验证（三向联动）</div>
      <div class="calc">内核存的「到期 tick」= 调用那一刻的 xTickCount + ${ticks}<br>采样时能算的「还差几拍」= 到期 tick − 采样时的 xTickCount（两者不是同一个时刻）</div>
      <div class="note">V1 右栏「当前延时链表」的任务块标签就是到期 tick；内核变量 <code>xNextTaskUnblockTime</code> 在链表非空时应等于表头最早到期值（空链表时是占位最大值）。能不能读到，取决于采样是否成功。</div>
      <div style="margin-top:6px"><span class="chip" data-jump="sched">${ic('arrow',14)}跳到延时链表</span><span class="chip" id="cfg-${gi}">${g('configTICK_RATE_HZ')} = ${val(t.decider)} <span class="note">${esc(cfgLoc)}</span></span></div>
    </div>
    <div class="tsec"><div class="hd">想改效果，改哪里</div>
      <dl class="kv">
        <dt>改代码参数</dt><dd><code>vTaskDelay(${half})</code> → 名义 ${dval(secFmt(half/hz)+' s',`${half} tick ÷ ${hz} Hz`,{ticks:half,hz:hz})}；这 ${grp.length} 处相同调用都会受影响，心跳不变。</dd>
        <dt>改心跳配置</dt><dd>假设把 ${g('configTICK_RATE_HZ')} 从 ${hz} 提到 ${hz2}：同样 ${ticks} tick 变成 ${dval(secFmt(ticks/hz2)+' s',`${ticks} tick ÷ ${hz2} Hz`,{ticks:ticks,hz:hz2})}，分辨率变成 ${dval(msFmt(1000/hz2)+' ms',`1 ÷ ${hz2} Hz`,{hz:hz2})}；代价是心跳中断更频繁，且影响全工程所有延时、需要重新编译烧录（本工具只读，不改固件）。</dd>
      </dl>
    </div>
    <details class="tadv"><summary>边界与陷阱（数据诚实契约 §6.2）</summary><div class="body">
      <b>到期 ≠ 执行 ≠ 点灯。</b>到期只代表任务重新具备运行条件；真正执行要等调度器选中，GPIO 动作又发生在执行之后。三者之间可能隔着若干 tick，离散快照还可能完全漏掉中间过程。<br>
      <b>相对延时。</b>周期 = 延时 + 本圈执行时间，逐圈累积会漂移；固定节拍用 ${g('vTaskDelayUntil')}。<br>
      <b>证据边界。</b>「到期 tick 是多少」必须以采样读到的链表值或内核变量为准；推导只解释公式，不能替代实测。
    </div></details></div></details>
  </div>`;
}

function gpioTermCard(t){
  const ws=t.writes||[],w=ws[0]||{},key=String(w.pin_macro||'').replace(/_Pin$/,''),pin=LENS.facts.pins[key];
  const mapped=pin&&pin.confirmed_from_source&&Number.isInteger(pin.bit),port=mapped?pin.port:null,bit=mapped?pin.bit:null;
  const r=LENS.structure.register,per=LENS.structure.peripheral,last=studyLast(LENS),odr=last&&last.gpio_odr;
  const canRead=mapped&&port===per.name&&r.name==='ODR'&&odr&&odr.state==='measured'&&odr.prov&&String(odr.prov.addr).toLowerCase()===String(r.address).toLowerCase();
  const observed=canRead?val({state:'measured',value:(odr.value>>>bit)&1,prov:{...odr.prov,bit,source:last.source,sampled_at:last.host_time}}):uval('没有该端口 ODR 对应位的身份已核验采样');
  const states=[...new Set(ws.map(x=>x.state))],allStates=[...new Set(LENS.facts.gpio_writes.filter(x=>x.pin_macro===w.pin_macro&&x.port_macro===w.port_macro).map(x=>x.state))];
  const srcs=ws.map(x=>`<span class="src" data-jump="reg">${esc(fileBase(x.file))}:${esc(x.line)} HAL_GPIO_WritePin(${esc(x.port_macro||'…')},${esc(x.pin_macro)},${esc(x.state)})</span>`).join('');
  const pinV=mapped?val({state:'authoritative',value:`${port} · bit ${bit}`,prov:{file:pin.file,line:pin.Pin&&pin.Pin.line,macro:w.pin_macro}}):uval('源码未确认端口与引脚位映射');
  const stateV=states.map(state=>{const source=ws.find(x=>x.state===state);return val({state:'authoritative',value:state,prov:{file:source.file,line:source.line}});}).join(' / ');
  return `<div class="term term-deep"><div class="thead"><h3>${esc(w.in_fn||'GPIO 调用')} · ${esc(w.pin_macro)}</h3><span class="tag acc">${ws.length} 处已识别调用 · ${states.length===1?'相同参数':'多种参数'}</span></div>
    <p class="tlead">这组源码的写入参数为 <b>${states.map(esc).join(' / ')}</b>；${states.length===1?'这些调用本身没有构成置位与复位交替的序列':'识别到了多种写入参数，但不证明这些路径都实际执行'}。这不能证明引脚始终不变或灯周期闪烁，其他任务、中断、Toggle 与直接寄存器写仍可能影响输出。</p>
    <div class="tq"><div><span class="k">① 写入意图</span><span class="big">${stateV}</span><span class="n">SET 是置位，RESET 是复位，都不是自动翻转。</span></div><div><span class="k">② 写入位置</span><span class="big">${pinV}</span><span class="n">依据源码映射，不推测硬件接法。</span></div><div><span class="k">③ 本次采样位值</span><span class="big">${observed}</span><span class="n">ODR 是输出锁存值；实际电平、灯亮灭与持续时间需要额外证据。</span></div></div>
    <details class="term-details"><summary>查看源码位置、硬件行为与验证方法</summary><div class="term-detail-grid"><div class="srcrow">${srcs}</div><div class="tsec"><div class="hd">目前能确认什么</div><ol class="flow"><li>这些调用行中出现了上述参数，不等于运行时一定执行到。</li><li>当前已提取的同端口宏、同引脚宏写入包含 ${allStates.map(esc).join(' / ')||'未知参数'}；宏别名及未提取的路径仍可能遗漏。</li><li>离散快照只能说明采样时刻，不能证明两次采样之间没有切换。</li></ol></div><div class="tsec"><div class="hd">如何继续验证</div><div class="note">先核对引脚模式与硬件接法，再查找全部写入者。若要验证闪烁周期，需要连续时序证据；当前工具不提供连续 trace，也不由灯的亮灭反推调度状态。</div><div class="btns" style="margin-top:12px"><button class="btn sec" data-jump="reg">查看寄存器位段</button><button class="btn sec" data-study-open="guide" data-study-topic="gpio">做一次预测实验</button></div></div></div></details></div>`;
}

function renderTerm(){
  const terms=LENS.terms||[];
  let h=`<div class="view-head"><div><h2>术语溯源</h2><p>从代码参数，到工程事实，再到芯片上的实际效果。</p></div><span class="view-index">03 / EXPLAIN</span></div><div class="term-list">`;
  const delayGroups=new Map();
  terms.forEach(t=>{if(t.kind==='delay'){const k=t.passed.value+'|'+t.decider.value;if(!delayGroups.has(k))delayGroups.set(k,[]);delayGroups.get(k).push(t);}});
  const rendered=new Set();let gi=0;
  terms.forEach(t=>{
    if(t.kind==='delay'){
      const k=t.passed.value+'|'+t.decider.value;
      if(rendered.has(k))return;rendered.add(k);
      h+=delayTermCard(delayGroups.get(k),gi++);
    }else if(t.kind==='gpio_dual'){
      h+=gpioTermCard(t);
    }
  });
  if(!terms.some(t=>t.kind==='delay'||t.kind==='gpio_dual'))h+=`<div class="card empty"><b>尚无可解读的调用</b><p>导入工程源码与配置后，这里会呈现已识别的关键调用及其依据。</p></div>`;
  h+=`</div>`;
  $('view-term').innerHTML=h;
}
function termClick(e){
  const study=e.target.closest('[data-study-open]');if(study){if(study.dataset.studyTopic)LEARNING.lesson=study.dataset.studyTopic;openStudy(study.dataset.studyOpen);return;}
  const s=e.target.closest('.src[data-link]');
  if(s){const c=$(s.dataset.link);if(c){c.classList.add('lit');setTimeout(()=>c.classList.remove('lit'),1500);if(window.__pulse)window.__pulse(c);}return;}
  const j=e.target.closest('[data-jump]');
  if(j){const tab=document.querySelector(`.tab[data-v="${j.dataset.jump}"]`);if(tab){tab.click();
    const sel={sched:'#dbar',reg:'.bits'}[j.dataset.jump];
    if(sel&&window.__jumpTo)window.__jumpTo(sel);}}
}

/* ---- 平台对照 ---- */
function renderPlat(){
  const cols=['freertos','rtthread','threadx','zephyr','stm32hal','esp'];
  const heads={freertos:'FreeRTOS',rtthread:'RT-Thread',threadx:'ThreadX',zephyr:'Zephyr',stm32hal:'STM32 HAL',esp:'ESP-IDF'};
  let rows=LENS.concepts.map(c=>`<tr><td><b>${esc(c.concept)}</b></td>${cols.map(k=>`<td class="m">${esc(c[k]||'—')}</td>`).join('')}</tr>`).join('');
  $('view-plat').innerHTML=`<div class="view-head"><div><h2>平台对照</h2><p>同一个概念，在不同嵌入式生态中的表达。</p></div><span class="view-index">04 / REFERENCE</span></div>
    <div class="card"><div class="section-head"><h3>跨平台概念索引</h3><span class="note">6 个平台</span></div>
    <div class="note">仅 ${g('FreeRTOS')} 支持真实数据解析，其余平台仅作概念与 API 写法对照，不代表已支持采样。</div>
    <div class="table-scroll" tabindex="0" role="region" aria-label="跨平台概念对照表"><table class="cmp"><tr><th>概念</th>${cols.map(k=>`<th>${heads[k]}</th>`).join('')}</tr>${rows}</table></div></div>`;
}

/* ---- V4 回放/导出 ---- */
function renderReplay(){
  $('view-replay').innerHTML=`<div class="view-head"><div><h2>回放与导出</h2><p>按自己的节奏观察快照，将证据保存在一个文件里。</p></div><span class="view-index">05 / REPLAY</span></div>
    <div class="card"><div class="section-head"><h3>快照回放</h3><span class="tag">${validSnaps.length} 有效帧</span></div><div class="note">按间隔重放已采集的离散快照，不改变芯片参数。</div>
    <div class="replay-settings"><label for="rint">回放间隔</label><div class="note">仅回放设置，真实数据模式下不得修改目标参数。</div>
      <div class="replay-range"><input type="range" id="rint" min="200" max="3000" step="100" value="1000"><span class="chip" id="rintv">1000 ms</span></div></div>
    <div class="btns"><button class="btn" id="rplay" ${validSnaps.length?'':'disabled'}>${ic('play')}开始回放</button><button class="btn sec" id="rstop" ${validSnaps.length?'':'disabled'}>${ic('stop')}停止</button></div>
    ${validSnaps.length?'':'<p class="replay-empty">尚无有效快照，完成采样后即可回放。</p>'}</div>
    <div class="card delivery-note"><div class="section-head"><h3>随文件一起带走</h3><span class="note mono">.HTML</span></div>
    <div class="note">当前网页就是一份离线成果。数据与来源内嵌在同一文件中，双击即可查看，不依赖网络。</div>
    <div class="delivery-item">${ic('check')}完整视图与交互</div><div class="delivery-item">${ic('check')}工程定义与采样记录</div><div class="delivery-item">${ic('check')}每个数字的来源与依据</div>
    <details class="learn-more"><summary>导出方式与数据边界</summary><div class="lesson-body note">导入工程并完成解读后，可在「导入我的工程」中导出网页或数据。当前文件也可直接保存、复制与分享。内嵌 device / build / identity / structure / facts / offsets / symbols / snapshots / concepts / terms；只改变回放设置，不写内存、不改固件、不烧录。</div></details></div>`;
  $('rint').oninput=e=>$('rintv').textContent=e.target.value+' ms';
  $('rplay').onclick=()=>{if(!validSnaps.length)return;const tab=document.querySelector('.tab[data-v="sched"]');tab.click();
    let i=0;const nextBtn=$('snext');clearInterval(replayTimer);
    replayTimer=setInterval(()=>{nextBtn.click();i++;if(i>=validSnaps.length){clearInterval(replayTimer);replayTimer=null;}},+$('rint').value);};
  $('rstop').onclick=()=>{clearInterval(replayTimer);replayTimer=null;};
}

function download(name,text,type){const blob=new Blob([text],{type:type+';charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}
function exportPage(name){
  const clone=document.documentElement.cloneNode(true);
  ['#impwrap','#glwrap','#readwrap','#prov','#scrim'].forEach(s=>clone.querySelector(s)?.classList.remove('on'));
  const json=JSON.stringify(LENS).replace(/</g,'\\u003c'),learning=JSON.stringify(LEARNING).replace(/</g,'\\u003c');
  let html='<!DOCTYPE html>\n'+clone.outerHTML;
  html=html.replace(/^let LENS = [^\n]*;\nconst STATE=/m,()=>'let LENS = '+json+';\nconst STATE=');
  html=html.replace(/^let LEARNING = [^\n]*;/m,()=>'let LEARNING = '+learning+';');
  download(name,html,'text/html');
}
let LEARNING = {mode:'guide',lesson:'delay',call:0,gpio:0,answers:{},before:null,after:null};
let studyNotice='',studyError=false;
const studyLoads={before:0,after:0};
function studyFrames(p){return (p.snapshots||[]).filter(s=>s.status==='ok'&&s.valid===true&&s.identity&&s.identity.status==='verified'&&s.resume_ok!==false&&s.decoded);}
function studyLast(p){const a=studyFrames(p);return a[a.length-1]||null;}
function studyUnknown(reason){return val({state:'unknown',value:null,prov:{reason}});}
function studySource(x){return `${fileBase(x.file)||'未提供文件'}:${x.line??'?'} · ${x.in_fn||'未识别函数'}`;}
function studyGroups(p){const groups=new Map();for(const w of p.facts.gpio_writes||[]){const key=JSON.stringify([w.in_fn,w.port_macro,w.pin_macro]);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(w);}return [...groups.values()];}
function studyQuestion(){
  const facts=LENS.facts,cfg=facts.config.configTICK_RATE_HZ,hz=cfg&&Number.isFinite(cfg.value)&&cfg.value>0?cfg.value:null;
  const delays=facts.delay_calls||[],groups=studyGroups(LENS);
  if(LEARNING.lesson==='delay'){
    if(!delays.length)return null;
    const i=Math.min(LEARNING.call,delays.length-1),d=delays[i],ticks=d.ticks,zero=ticks===0;
    const correct=zero?'yield':hz?'frequency':'unknown';
    const options=[['milliseconds',`${ticks} tick 总是等于 ${ticks} ms，与配置无关`],['frequency',hz?`按 ${hz} Hz 换算，名义 ${secFmt(ticks/hz)} s，但不保证立即执行`:'按节拍频率换算，但目前还没有频率依据'],['yield','这次调用只让出本次执行机会，不设置正延时'],['unknown','缺少换算依据，当前无法给出名义时长']];
    const nominal=zero?'0 tick 不设置正延时':hz?`${ticks} tick ÷ ${hz} Hz = ${secFmt(ticks/hz)} s`:'缺少有效的 configTICK_RATE_HZ，不能把 tick 当毫秒';
    const feedback={milliseconds:'tick 是节拍数，不是固定的毫秒单位；只有特定频率下两个数值才会恰好相同。',frequency:zero?'vTaskDelay(0) 不进入正延时等待，不能按普通睡眠时间解释。':hz?'名义时长来自参数与节拍配置；到期只代表重新具备就绪条件，不代表准时执行。':'当前没有频率证据，不能给出可靠的时间换算。',yield:zero?'vTaskDelay(0) 让出本次执行机会，随后是否运行其他任务仍由调度器决定。':'这里参数大于 0，是相对延时，不是单纯的零延时让出。',unknown:hz||zero?'这个问题已有足够的源码与配置依据；但真实执行时刻仍然不可知。':'正确保留了未知项：补充该工程的节拍配置后，才能进行换算。'};
    const last=studyLast(LENS),tc=last&&last.decoded.scalars&&last.decoded.scalars.xTickCount;
    return {context:JSON.stringify([LENS.build.axf_sha,LENS.build.map_sha,d,cfg]),correct,options,feedback,title:`vTaskDelay(${ticks}) 应该怎样理解？`,select:`<label class="note" for="study-call">选择当前工程中的调用</label><select class="study-select" id="study-call">${delays.map((x,j)=>`<option value="${j}" ${j===i?'selected':''}>${esc(studySource(x))} · ${esc(x.ticks)} tick</option>`).join('')}</select>`,evidence:`<dt>源码参数</dt><dd>${val({state:'authoritative',value:ticks,prov:{file:d.file,line:d.line,unit:'tick'}})} tick · ${esc(studySource(d))}</dd><dt>节拍配置</dt><dd>${hz?val({state:'authoritative',value:hz,prov:{file:cfg.file,line:cfg.line,unit:'Hz'}})+' Hz':studyUnknown('未提供有效的节拍频率')}</dd><dt>换算依据，而非实测时长</dt><dd>${esc(nominal)}</dd><dt>最后有效快照中的 tick</dt><dd>${tc?val(tc):studyUnknown('没有身份核验通过的有效快照')}<div class="note">采样 tick 不是调用时刻；不能用它反推真实到期 tick 或执行耗时。</div></dd>`,next:['在 IDE 中只修改一个延时参数，或只修改节拍频率，先写下你的预期。','重新编译后按自己的实验流程更新固件，再导入同次构建产物并采样核验。','分别保留修改前后数据包，在「前后对比」里核对配置、名义时长与实测证据。']};
  }
  if(!groups.length)return null;
  const i=Math.min(LEARNING.gpio,groups.length-1),ws=groups[i],w=ws[0],states=[...new Set(ws.map(x=>x.state))];
  return {context:JSON.stringify([LENS.build.axf_sha,LENS.build.map_sha,ws]),correct:'bounded',title:'这些 GPIO 调用能证明什么？',options:[['steady','同状态写入就能证明引脚始终不变'],['toggle','存在 SET 与 RESET 调用就能证明灯周期闪烁'],['bounded','只能解释已识别调用；真实电平与时序仍需验证'],['scheduler','灯没闪就表示任务没有被调度']],feedback:{steady:'同状态调用本身不构成翻转序列，但其他任务、中断、Toggle 或直接写寄存器仍可能改变输出。',toggle:'调用存在不等于代码实际执行；还要确认控制流、引脚模式、硬件接法与时间证据。',bounded:'证据边界判断正确：源码说明写入意图，ODR 快照说明采样时的锁存值，都不能单独证明持续闪烁。',scheduler:'灯的状态不是调度证据；应查看身份核验后的任务快照，而不是由亮灭反推任务是否在运行。'},select:`<label class="note" for="study-gpio">选择已识别的 GPIO 调用组</label><select class="study-select" id="study-gpio">${groups.map((g,j)=>`<option value="${j}" ${i===j?'selected':''}>${esc(g[0].in_fn||'未识别函数')} · ${esc(g[0].port_macro)} / ${esc(g[0].pin_macro)}</option>`).join('')}</select>`,evidence:`<dt>本组已识别的写入状态</dt><dd>${states.map(esc).join(' / ')} · ${ws.length} 处调用</dd><dt>源码位置</dt><dd>${ws.map(x=>`${esc(studySource(x))}<br>${val({state:'authoritative',value:x.state,prov:{file:x.file,line:x.line,port_macro:x.port_macro,pin_macro:x.pin_macro}})}`).join('<br>')}</dd><dt>能确认的范围</dt><dd>这些调用的写入参数；不证明它们已经执行，也不覆盖其他任务、中断、Toggle、直接寄存器写或硬件反相。</dd><dt>寄存器证据</dt><dd>${studyRegister(LENS).html}<div class="note">只读所选寄存器的采样时刻，不据此判断灯是否一直亮或一直闪。</div></dd>`,next:['先在源码中查找该引脚的所有写入者，包括中断、Toggle 和直接寄存器写。','在 IDE 中只改一个因素；重新构建和实验后，采集与新固件匹配的数据包。','比较两份数据中的写入意图与寄存器读数；相同的离散读数不能证明期间没有变化。']};
}
function studyRegister(p){
  const s=studyLast(p),v=s&&s.gpio_odr,r=p.structure.register;
  if(!v||v.state!=='measured'||!Number.isInteger(v.value)||!v.prov||String(v.prov.addr).toLowerCase()!==String(r.address).toLowerCase())return {key:null,html:studyUnknown('没有与所选寄存器地址一致、身份核验通过且来源完整的有效读数')};
  return {key:v.value,html:val(v,true)+`<span class="compare-source">${esc(s.host_time)} · ${esc(s.source)}</span>`};
}
function studyGuide(){
  const q=studyQuestion();
  const lessons=`<div class="study-lessons"><button class="study-lesson" data-study-lesson="delay" aria-pressed="${LEARNING.lesson==='delay'}"><span class="mono">EXPERIMENT / 01</span><b>tick 不是毫秒</b><span>参数 → 配置 → 名义时长</span></button><button class="study-lesson" data-study-lesson="gpio" aria-pressed="${LEARNING.lesson==='gpio'}"><span class="mono">EXPERIMENT / 02</span><b>灯为什么不闪？</b><span>写入意图 → 采样证据 → 结论边界</span></button></div>`;
  if(!q)return lessons+`<div class="card empty"><b>当前工程缺少这个实验的源码依据</b><p>导入包含数字常量 vTaskDelay 调用或 HAL_GPIO_WritePin 调用的源码；节拍换算还需要 FreeRTOSConfig.h。</p><div class="btns" style="margin-top:16px"><button class="btn" data-study-import>导入工程</button></div></div>`;
  const saved=LEARNING.answers[LEARNING.lesson],a=saved&&saved.context===q.context?saved:null,done=a&&a.submitted,agree=done&&a.choice===q.correct;
  return lessons+`<div class="study-layout"><div><form class="card study-question" id="study-answer"><span class="study-step">01 / 先预测，再查证</span><h3>${esc(q.title)}</h3><p class="note">使用当前工程的真实定义与源码事实，不会生成虚拟采样。</p><div style="margin-top:18px">${q.select}</div><fieldset><legend>选择你认为最准确的解释</legend>${q.options.map(([id,text])=>`<label class="study-choice"><input type="radio" name="study-choice" value="${id}" ${a&&a.choice===id?'checked':''} required><span>${esc(text)}</span></label>`).join('')}</fieldset><div class="btns"><button class="btn" type="submit">提交预测，查看反馈</button><button class="btn sec" type="button" data-study-retry>重新预测</button></div>${done?`<div class="study-feedback ${agree?'agree':''}" role="status"><b>${agree?'与当前证据一致':'再检查一下证据'}</b>${esc(q.feedback[a.choice])}<br>这次回答只针对当前问题，不代表已经掌握整个概念。</div>`:''}</form><div class="card"><span class="study-step">03 / 做一次可验证的改动</span><ol class="study-next">${q.next.map(x=>`<li>${esc(x)}</li>`).join('')}</ol><div class="btns" style="margin-top:20px"><button class="btn sec" data-study-mode="compare">打开前后对比${ic('arrow')}</button><button class="btn sec" data-study-mode="diagnosis">检查采样记录</button></div></div></div><aside><details class="card study-evidence" ${done?'open':''}><summary>02 / 查看证据与来源</summary><dl>${q.evidence}</dl><div class="btns"><button class="btn sec" data-jump="${LEARNING.lesson==='delay'?'term':'reg'}">打开对应视图${ic('arrow')}</button></div></details><div class="card"><div class="section-head"><h3>把实验带走</h3><span class="note mono">OFFLINE</span></div><p class="note">导出的实验网页会保存当前工程、预测反馈和已载入的 A/B 数据包；所有文件只在本机处理。</p><button class="btn sec" data-study-export style="margin-top:16px">导出实验网页</button><p class="note" style="margin-top:12px">当前有效采样 ${studyFrames(LENS).length} 帧；没有实测时只做源码与定义实验。</p></div></aside></div>`;
}
function validateStudyPayload(p){
  const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x),str=x=>typeof x==='string',arr=x=>Array.isArray(x);
  if(!obj(p)||!obj(p.device)||!str(p.device.name)||!obj(p.build)||!obj(p.identity)||!obj(p.structure)||!obj(p.structure.register)||!obj(p.structure.peripheral)||!obj(p.structure.svd)||!obj(p.facts)||!obj(p.facts.config)||!obj(p.facts.pins)||!arr(p.facts.delay_calls)||!arr(p.facts.gpio_writes)||!arr(p.facts.tasks)||!arr(p.snapshots))throw new Error('需要完整的 EmbeddedLens 数据包：设备、构建、身份、结构、工程事实与快照记录。');
  const r=p.structure.register;
  if(!str(r.name)||!str(r.address)||!str(p.structure.peripheral.name)||!Number.isInteger(r.size_bits)||r.size_bits<1||r.size_bits>64||!arr(r.fields))throw new Error('寄存器定义不完整。');
  if(p.facts.delay_calls.some(d=>!obj(d)||!Number.isInteger(d.ticks)||d.ticks<0||!str(d.file))||p.facts.gpio_writes.some(w=>!obj(w)||!str(w.pin_macro)||!str(w.state)||!str(w.file))||p.facts.tasks.some(t=>!obj(t)||!str(t.name)||!Number.isInteger(t.priority)))throw new Error('工程事实中的调用或任务格式不正确。');
  const hz=p.facts.config.configTICK_RATE_HZ;
  if(hz!=null&&(!obj(hz)||!Number.isFinite(hz.value)))throw new Error('节拍频率必须是数值。');
  if(p.snapshots.some(s=>!obj(s)||!str(s.status)||(s.decoded!=null&&!obj(s.decoded))))throw new Error('快照记录格式不正确。');
  return p;
}
async function studyReadFile(file){if(file.size>16*1024*1024)throw new Error('数据包超过 16 MB，请只保留本次实验所需的快照。');return validateStudyPayload(JSON.parse(await file.text()));}
function studyCompareRows(p){
  const f=p.facts,hz=f.config.configTICK_RATE_HZ,rate=hz&&Number.isFinite(hz.value)&&hz.value>0?hz.value:null;
  const delays=f.delay_calls.map(d=>({fn:d.in_fn||'未识别函数',ticks:d.ticks,seconds:d.ticks===0?0:rate?d.ticks/rate:null,file:d.file,line:d.line}));
  const writes=f.gpio_writes.map(w=>`${w.in_fn||'未识别函数'} · ${w.port_macro||'?'} / ${w.pin_macro} = ${w.state}`);
  const tasks=f.tasks.map(t=>`${t.name} · 优先级 ${t.priority}`),s=studyLast(p),current=s&&s.decoded.current;
  return [{title:'节拍频率',key:rate,html:rate?val({state:'authoritative',value:rate,prov:{file:hz.file,line:hz.line,unit:'Hz'}})+' Hz':studyUnknown('缺少有效节拍配置')},
    {title:'延时参数与名义时长',key:delays.length?JSON.stringify(delays.map(d=>[d.fn,d.ticks,d.seconds])):null,html:delays.length?delays.map(d=>`${esc(d.fn)} · ${val({state:'authoritative',value:d.ticks,prov:{file:d.file,line:d.line,unit:'tick'}})} tick → ${d.ticks===0?'让出执行机会':d.seconds===null?'时长不可知':esc(secFmt(d.seconds))+' s（推导）'}<span class="compare-source">${esc(fileBase(d.file))}:${esc(d.line)}</span>`).join('<br>'):studyUnknown('未识别到受支持的延时调用')},
    {title:'已识别 GPIO 写入',key:writes.length?JSON.stringify(writes):null,html:writes.length?writes.map(esc).join('<br>'):studyUnknown('未识别到 GPIO 写入')},
    {title:'任务定义',key:tasks.length?JSON.stringify(tasks):null,html:tasks.length?tasks.map(esc).join('<br>'):studyUnknown('未识别到任务定义')},
    {title:'快照选中任务',key:current&&current.name||null,html:current?val({state:'measured',value:current.name,prov:{addr:current.addr,source:s.source,sampled_at:s.host_time}}):studyUnknown('没有身份核验通过的任务快照'),observation:true},
    {title:'所选寄存器读数',...studyRegister(p),register:true,observation:true}];
}
function studyCompare(){
  let h=`<div class="note" style="margin-bottom:18px">先保存 A，再在 IDE 中改动、重新构建与采样，最后载入 B；这里不会修改固件，也不会把两份数据合并成一条运行轨迹。</div><div class="compare-slots">`;
  for(const [slot,label]of[['before','A / 修改前'],['after','B / 修改后']]){const s=LEARNING[slot],p=s&&s.payload;
    h+=`<section class="card compare-slot"><span class="study-step">${label}</span><h3>${p?esc(p.device.name):'等待一份完整数据包'}</h3><div class="compare-meta">${p?`${esc(s.name)}<br>${esc(p.build.rtos)} · 固件 ${esc(p.build.axf_sha||'指纹未提供')}<br>${studyFrames(p).length} 个有效帧 / ${p.snapshots.length} 条记录`:'可以使用当前工程，也可以载入该版本导出的 payload.json。没有实测帧时仍可比较工程事实。'}</div><div class="btns"><button class="btn sec" data-study-capture="${slot}">使用当前工程</button><label class="btn sec compare-file">载入数据包<input type="file" id="study-${slot}-file" data-study-file="${slot}" accept=".json,application/json" aria-label="载入${slot==='before'?'修改前':'修改后'}数据包"></label>${p?`<button class="btn sec" data-study-clear="${slot}">移除</button>`:''}</div></section>`;
  }
  h+='</div>';
  if(!LEARNING.before||!LEARNING.after)return h+`<div class="card empty"><b>保留改前与改后的证据，再判断变化</b><p>不会用模拟数据填充空位；两份数据包就绪后显示对比结果。</p><button class="btn sec" data-study-import style="margin-top:16px">打开工程导入 / 数据导出</button></div>`;
  const a=LEARNING.before.payload,b=LEARNING.after.payload,rowsA=studyCompareRows(a),rowsB=studyCompareRows(b);
  const sameRegister=a.device.name===b.device.name&&a.structure.peripheral.name===b.structure.peripheral.name&&a.structure.register.name===b.structure.register.name&&a.structure.register.size_bits===b.structure.register.size_bits&&a.structure.register.address.toLowerCase()===b.structure.register.address.toLowerCase();
  let changes=0,unknowns=0;
  const rows=rowsA.map((x,i)=>{const y=rowsB[i],comparable=x.key!==null&&y.key!==null&&(!x.register||sameRegister),changed=comparable&&x.key!==y.key;if(changed)changes++;if(!comparable)unknowns++;
    return `<tr class="${changed?'changed':''}"><th scope="row">${x.title}</th><td>${x.html}</td><td>${y.html}</td><td>${!comparable?'证据不足或不可比':changed?(x.observation?'观测不同':'事实有变化'):(x.observation?'本次观测相同':'识别结果相同')}</td></tr>`;}).join('');
  h+=`<div class="card"><div class="section-head"><h3>证据对照</h3><span class="note">${changes} 项不同 · ${unknowns} 项不可判定</span></div><div class="snote"><b>比较边界</b><br>核验结果来自各自数据包，网页没有重新连接开发板。不同构建的 tick 不能直接相减；相同快照值也不能证明两次采样之间没有变化。源码条目按各自提取顺序展示，不自动对齐执行路径。${sameRegister?'':'<br>设备或寄存器定义不一致：原始读数不作数值差异判断。'}</div><div class="table-scroll" role="region" tabindex="0" aria-label="实验前后证据对照"><table class="compare-table"><thead><tr><th>观察项</th><th>A / 修改前</th><th>B / 修改后</th><th>判断</th></tr></thead><tbody>${rows}</tbody></table></div><details class="learn-more"><summary>如何解释这个结果？</summary><div class="lesson-body note">配置或参数变化只能支持对应的名义换算；要证明执行周期或灯闪烁，需要额外的连续时序证据。若只有工程定义，先解释源码变化，不把缺少的实测证据当作反例。一次只改变一个因素，更容易定位因果。</div></details><button class="btn sec" data-study-export style="margin-top:20px">导出实验网页</button></div>`;
  return h;
}
function studyDiagnosis(){
  const snaps=LENS.snapshots,s=snaps[snaps.length-1],diag=s&&s.diagnostic,raw=s?[...(s.notes||[]),s.identity&&s.identity.reason||'',diag&&diag.message||''].filter(Boolean).join('\n'):'尚无采样记录';
  let stage=diag&&diag.stage;
  if(!stage){if(!s)stage='none';else if(s.resume_ok===false||/resume.*失败|恢复目标失败/.test(raw))stage='resume';else if(s.identity&&s.identity.status==='mismatch')stage='identity';else if(s.valid&&s.identity&&s.identity.status==='verified')stage='complete';else if(/ENOENT|WinError 2|No such file/i.test(raw))stage='tool';else if(/halt 失败/i.test(raw))stage='halt';else if(/open failed|无法连接 OpenOCD|探针未连接/i.test(raw))stage='connect';else if(/结构校验/.test(raw))stage='structure';else if(s.identity&&s.identity.status!=='verified')stage='identity';else stage='unknown';}
  const guidance={none:['先准备一次只读采样',['先导入同次构建的 map、AXF、SVD 和已核定的结构偏移。','确认板子供电、ST-LINK 驱动及 SWD 接线，再在本机运行采样命令。']],tool:['采样工具未能启动',['检查 OpenOCD 可执行文件与 scripts 目录是否存在。','可用 CLI 的 --openocd、--scripts 指定本机路径；DWARF 提取用 --gdb 指定工具。']],connect:['连接阶段需要排查',['确认供电、共地、SWDIO/SWCLK 接线及驱动。','检查 Keil 等程序是否正在独占探针；需要由你确认后关闭占用程序。','日志不足以区分这些原因；不要把排查建议当成已经确认的故障。']],halt:['停核请求未成功',['检查探针连接和目标配置是否与芯片匹配。','查看原始 halt 响应；不要使用烧录或复位来绕过问题。']],read:['内存读取阶段未完成',['检查地址范围、目标配置及构建产物是否匹配。','查看原始读取响应，并确认目标是否已恢复；不要用上次文件冒充本次采样。']],resume:['目标恢复失败，先确认开发板状态',['暂停继续采样，使用原调试工具确认目标当前是否仍停核。','界面不能替你确认目标已经恢复；保留日志并排查连接问题。']],identity:['固件身份尚未核验通过',['确认 AXF、map、偏移与板上固件来自同次构建。','手工采集也需要 Flash 比对数据；不要跳过核验来解释 RTOS 对象。']],structure:['内核结构校验未通过',['核对 DWARF 偏移、FreeRTOS 配置与读取地址范围。','离散停核可能落在链表更新中；确认目标已恢复后再采样，不用坏帧解释任务。']],complete:['记录包含可用的核验快照',['可打开调度快照与寄存器，点击数值检查来源。','这里只反映记录中的采样结果，不表示开发板此刻仍连接或仍处于相同状态。']],unknown:['现有记录不足以定位阶段',['先查看原始日志，确认失败发生在启动、连接、停核、读取还是恢复。','不要凭一条模糊错误判断供电、接线或固件损坏。']]};
  const [title,steps]=guidance[stage]||guidance.unknown,hasOffset=LENS.offsets&&LENS.offsets.types&&Object.keys(LENS.offsets.types).length>0;
  const checks=[['RTOS 符号',LENS.build.rtos_linked?'已识别链接':'未确认链接'],['构建指纹',LENS.build.axf_sha?'已提供':'未提供 AXF 指纹'],['结构偏移',hasOffset?'已提供，仍需与构建核对':'未提供'],['最近采样',s?`${s.host_time||'时间未提供'} · ${s.source||'来源未提供'}`:'尚无记录'],['该帧身份',s&&s.identity?({verified:'记录为已核验',mismatch:'不匹配',unverified:'未核验'}[s.identity.status]||s.identity.status):'不可知'],['目标恢复',s&&s.resume_ok===true?'记录为恢复成功':s&&s.resume_ok===false?'恢复失败':'记录未确认'],['可解释状态',s&&studyFrames({snapshots:[s]}).length?'该帧可参与解释':'该帧不参与 RTOS 解释']];
  return `<div class="study-layout"><div class="card"><span class="study-step">DIAGNOSTICS / 依据采样记录</span><h2>${esc(title)}</h2><p class="note">${diag?'阶段来自采样器的结构化记录。':'旧记录的阶段仅由状态与日志线索归类，无法据此确认唯一根因。'}此页不会探测设备或执行命令。</p><ol class="study-next">${steps.map(x=>`<li>${esc(x)}</li>`).join('')}</ol><div class="btns" style="margin-top:20px"><button class="btn" data-readopen>一键读取</button><button class="btn sec" data-study-import>核对工程文件</button><button class="btn sec" data-jump="sched">查看调度快照</button></div><details class="learn-more"><summary>原始诊断记录</summary><div class="diagnosis-log">${esc(raw)}</div></details></div><aside class="card"><div class="section-head"><h3>采样准备清单</h3></div><ul class="diagnosis-list">${checks.map(([k,v])=>`<li><span>${esc(k)}</span><b>${esc(v)}</b></li>`).join('')}</ul><details class="learn-more"><summary>本机命令与手工采集</summary><div class="lesson-body note">从项目目录执行，路径换成你本机的安装位置：<p class="diagnosis-log">python tools/elens.py sample --example &lt;工程名&gt; --frames 5 --interval 1 --openocd &lt;工具路径&gt; --scripts &lt;脚本目录&gt;</p>采样后重新 export，或用 --manual 导入 Keil 手工采集的实际字节；先确认调试环境不会自动下载或复位。离线网页不能直接连接 ST-LINK。</div></details></aside></div>`;
}
function renderLearn(focusId){
  const modes=[['guide','实验引导'],['compare','前后对比'],['diagnosis','采样诊断']];
  if(!modes.some(([k])=>k===LEARNING.mode))LEARNING.mode='guide';
  $('view-learn').innerHTML=`<div class="view-head"><div><h2>学习实验</h2><p>先提出解释，再用你的工程与采样证据检验。</p></div><span class="view-index">00 / LAB NOTEBOOK</span></div><div class="study-nav" role="group" aria-label="学习工具">${modes.map(([k,n])=>`<button id="study-mode-${k}" data-study-mode="${k}" aria-pressed="${LEARNING.mode===k}">${n}</button>`).join('')}</div><div class="study-status ${studyError?'error':''}" role="status">${esc(studyNotice)}</div>${LEARNING.mode==='guide'?studyGuide():LEARNING.mode==='compare'?studyCompare():studyDiagnosis()}`;
  if(focusId){const el=$(focusId);if(el)el.focus({preventScroll:true});}
}
function openStudy(mode){LEARNING.mode=mode;studyNotice='';studyError=false;renderLearn();$('tab-learn').click();$('study-mode-'+mode).focus({preventScroll:true});}
$('view-learn').addEventListener('click',e=>{
  const mode=e.target.closest('[data-study-mode]');if(mode){LEARNING.mode=mode.dataset.studyMode;studyNotice='';studyError=false;renderLearn('study-mode-'+LEARNING.mode);return;}
  const lesson=e.target.closest('[data-study-lesson]');if(lesson){LEARNING.lesson=lesson.dataset.studyLesson;renderLearn();$('study-answer')?.querySelector('input')?.focus({preventScroll:true});return;}
  const capture=e.target.closest('[data-study-capture]');if(capture){const slot=capture.dataset.studyCapture;LEARNING[slot]={name:'当前工程快照',payload:JSON.parse(JSON.stringify(LENS))};studyNotice=`已保存${slot==='before'?'修改前 A':'修改后 B'}，后续导入不会覆盖这份证据。`;studyError=false;renderLearn('study-mode-compare');return;}
  const clear=e.target.closest('[data-study-clear]');if(clear){LEARNING[clear.dataset.studyClear]=null;studyNotice='已移除所选对比数据，不影响当前工程。';renderLearn('study-mode-compare');return;}
  if(e.target.closest('[data-study-import]'))$('impopen').click();
  if(e.target.closest('[data-study-retry]')){delete LEARNING.answers[LEARNING.lesson];renderLearn();$('study-answer')?.querySelector('input')?.focus({preventScroll:true});}
  if(e.target.closest('[data-study-export]')){exportPage('embedded-lens-experiment.html');studyNotice='已导出实验网页，包含当前工程、预测记录及 A/B 数据。';studyError=false;renderLearn();}
});
$('view-learn').addEventListener('submit',e=>{if(e.target.id!=='study-answer')return;e.preventDefault();const choice=new FormData(e.target).get('study-choice'),q=studyQuestion();if(!q||!q.options.some(([id])=>id===choice))return;LEARNING.answers[LEARNING.lesson]={context:q.context,choice,submitted:true};renderLearn();$('study-answer').querySelector('button[type="submit"]').focus({preventScroll:true});});
$('view-learn').addEventListener('change',async e=>{
  const el=e.target;
  if(el.id==='study-call'||el.id==='study-gpio'){LEARNING[el.id==='study-call'?'call':'gpio']=Number(el.value);renderLearn(el.id);return;}
  if(el.name==='study-choice'){const q=studyQuestion();LEARNING.answers[LEARNING.lesson]={context:q.context,choice:el.value,submitted:false};$('study-answer').querySelector('.study-feedback')?.remove();return;}
  if(el.dataset.studyFile&&el.files[0]){const slot=el.dataset.studyFile,file=el.files[0];try{const payload=await studyReadFile(file);LEARNING[slot]={name:file.name,payload};studyNotice=`已载入${slot==='before'?'修改前 A':'修改后 B'}：${file.name}`;studyError=false;}catch(err){studyNotice='未替换原有数据：'+err.message;studyError=true;}renderLearn('study-mode-compare');}
});

let replayTimer=null;
function renderAll(){if(replayTimer){clearInterval(replayTimer);replayTimer=null;}refreshSnaps();renderTop();renderLearn();renderSched();renderReg();renderTerm();renderPlat();renderReplay();
  const on=document.querySelector('.tab.on');if(on&&window.__enterView)window.__enterView($('view-'+on.dataset.v));}
document.querySelector('.workbench-main').addEventListener('click',termClick);
renderAll();
const h0=location.hash.slice(1);if(h0){const t0=document.querySelector('.tab[data-v="'+h0+'"]');if(t0)selTab(t0);}

/* ================= 动效层（GSAP 全内联，零外链；遵守 prefers-reduced-motion） ================= */
(function(){
if(!window.gsap)return;
gsap.registerPlugin(ScrollToPlugin, DrawSVGPlugin);
const RM=matchMedia('(prefers-reduced-motion: reduce)');
const d=x=>RM.matches?0:x;
const EASE='power3.out';
const accent=(getComputedStyle(document.documentElement).getPropertyValue('--accent')||'#14406b').trim();

/* 页头入场（进入功能页时播放 / 重放） */
const mark=document.querySelectorAll('.mark svg > *');
function playAppIntro(){
  if(mark.length)gsap.fromTo(mark,{drawSVG:'0% 0%'},{drawSVG:'0% 100%',duration:d(1),stagger:d(.08),ease:'power2.inOut',overwrite:'auto'});
  gsap.from('.brand-text, .workspace-label, .mast-actions, .project-panel',{opacity:0,y:d(6),duration:d(.4),stagger:d(.04),ease:EASE,clearProps:'opacity,transform',overwrite:'auto'});
  const on=document.querySelector('.tab.on');
  if(on)enterView($('view-'+on.dataset.v));
}
window.__appIntro=playAppIntro;

/* Tab 滑动指示条 */
const tabsEl=$('tabs');
const ink=document.createElement('span');ink.className='tab-ink';ink.setAttribute('aria-hidden','true');tabsEl.appendChild(ink);
function moveInk(tab,animate){
  if(!tab)return;
  const o=compactNav.matches
    ?{x:tab.offsetLeft,y:tab.offsetTop+tab.offsetHeight-2,width:tab.offsetWidth,height:2}
    :{x:0,y:tab.offsetTop+8,width:3,height:tab.offsetHeight-16};
  if(animate&&!RM.matches)gsap.to(ink,{...o,duration:.36,ease:'power3.out',overwrite:'auto'});
  else{gsap.killTweensOf(ink);gsap.set(ink,o);}
}
// 同一帧往返折叠可能不触发尺寸观察器。
navToggle.addEventListener('click',()=>moveInk(document.querySelector('.tab.on'),false));
const navObserver=new ResizeObserver(()=>moveInk(document.querySelector('.tab.on'),false));navObserver.observe(tabsEl);
let rz;addEventListener('resize',()=>{clearTimeout(rz);rz=setTimeout(()=>moveInk(document.querySelector('.tab.on'),false),120);});

/* 视图入场：卡片分层浮现（V2 位格、V3 术语卡再细分） */
function enterView(view){
  if(!view)return;
  const cards=[...view.querySelectorAll(':scope > .card, :scope > .term-list > .term')];
  if(!cards.length)return;
  gsap.fromTo(cards,{opacity:0,y:d(12)},{opacity:1,y:0,duration:d(.5),stagger:d(.07),ease:EASE,overwrite:'auto',clearProps:'transform,opacity'});
  if(view.id==='view-reg')gsap.fromTo(view.querySelectorAll('.bit'),{opacity:0,scale:.95},{opacity:1,scale:1,duration:d(.32),stagger:d(.008),ease:'power2.out',delay:d(.06),overwrite:'auto',clearProps:'transform,opacity'});
}

/* 目标脉冲 + 平滑滚动（三向联动） */
function pulse(el){
  if(!el||RM.matches)return;
  gsap.fromTo(el,{outline:'3px solid '+accent+'55',outlineOffset:'2px'},{outlineOffset:'10px',outline:'3px solid '+accent+'00',duration:.8,ease:'power2.out',clearProps:'outline,outlineOffset'});
}
function scrollToEl(el,offset){if(el)gsap.to(window,{scrollTo:{y:el,offsetY:offset==null?76:offset},duration:d(.6),ease:'power3.inOut'});}
function jumpTo(sel){
  setTimeout(()=>{
    const el=document.querySelector(sel);if(!el)return;
    scrollToEl(el,86);
    if(sel==='.bits'){const his=[...document.querySelectorAll('.bit.hi')];(his.length?his:[el]).forEach((x,i)=>setTimeout(()=>pulse(x),i*60));}
    else pulse(el);
  },RM.matches?0:160);
}

/* 溯源面板：行级入场 */
window.__provIn=()=>{
  if(RM.matches)return;
  const rows=document.querySelectorAll('#provbody .row');
  if(rows.length)gsap.fromTo(rows,{opacity:0,x:10},{opacity:1,x:0,duration:.28,stagger:.03,ease:'power2.out',overwrite:'auto',clearProps:'opacity,transform'});
};

/* V1 换帧反馈 */
window.__frameIn=()=>{
  if(RM.matches)return;
  gsap.fromTo('#scur',{opacity:.45},{opacity:1,duration:.38,ease:'power2.out',overwrite:'auto',clearProps:'opacity'});
  const sx=$('sidx');if(sx)gsap.fromTo(sx,{scale:.88},{scale:1,duration:.3,ease:'back.out(2)',overwrite:'auto',clearProps:'transform'});
};

window.__onTabShown=(view,tab)=>{moveInk(tab,true);enterView(view);};
window.__enterView=enterView;
window.__scrollToEl=scrollToEl;
window.__pulse=pulse;
window.__jumpTo=jumpTo;

/* 初始：指示条就位；首屏入场由介绍页 / 深链决定 */
const onTab=document.querySelector('.tab.on');
if(onTab)moveInk(onTab,false);
requestAnimationFrame(()=>moveInk(document.querySelector('.tab.on'),false));
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>moveInk(document.querySelector('.tab.on'),false));
})();

/* ================= 介绍页：进入 / 返回 / 指针交互 ================= */
(function(){
const landing=$('landing');if(!landing)return;
const enterBtn=$('ldenter'),iris=$('ldiris'),probe=$('ldprobe'),scope=$('ldscope'),home=$('ldhome');
const wrapEl=document.querySelector('.wrap');
const RM2=matchMedia('(prefers-reduced-motion: reduce)');
const G=window.gsap;
const setAppHidden=on=>{if(wrapEl)wrapEl.setAttribute('aria-hidden',on?'true':'false');};
const NS='http://www.w3.org/2000/svg';

/* 刻度环与芯片引脚（纯装饰图形，不含任何数据） */
const ticks=$('ldticks');
if(ticks)for(let i=0;i<72;i++){const a=i/72*Math.PI*2,mj=i%6===0,r=mj?216:224;
  const ln=document.createElementNS(NS,'line');
  ln.setAttribute('x1',(280+Math.cos(a)*232).toFixed(1));ln.setAttribute('y1',(280+Math.sin(a)*232).toFixed(1));
  ln.setAttribute('x2',(280+Math.cos(a)*r).toFixed(1));ln.setAttribute('y2',(280+Math.sin(a)*r).toFixed(1));
  if(mj)ln.setAttribute('class','mj');ticks.appendChild(ln);}
const pins=$('ldpins');
if(pins)for(let i=-1;i<=1;i++){const o=280+i*26;
  [[o,228,o,236],[o,324,o,332],[228,o,236,o],[324,o,332,o]].forEach(q=>{
    const ln=document.createElementNS(NS,'line');
    ln.setAttribute('x1',q[0]);ln.setAttribute('y1',q[1]);ln.setAttribute('x2',q[2]);ln.setAttribute('y2',q[3]);
    if(i===0)ln.setAttribute('class','mj');pins.appendChild(ln);});}

/* 版本行取自内嵌载荷，不写死 */
const dev=LENS.device||{},bd=LENS.build||{};
$('ldbuild').textContent=[dev.name,dev.core,bd.rtos,bd.kernel&&bd.kernel.version].filter(Boolean).join(' · ');

/* ---- 右侧 3D 芯片（Three.js 内联；WebGL 不可用时回落为 SVG 雷达） ---- */
function init3D(){
  const host=$('ldstage'),canvas=$('ldgl'),T=window.THREE;
  if(!T||!canvas||!host)return null;
  let renderer;
  try{renderer=new T.WebGLRenderer({canvas:canvas,antialias:true,alpha:true,preserveDrawingBuffer:true});}
  catch(e){return null;}
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.6));
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
  renderer.outputEncoding=T.sRGBEncoding;
  renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.14;
  const scene=new T.Scene();
  const camera=new T.PerspectiveCamera(32,1,1,2200);

  function makeEnv(){
    const faces=[];
    for(let i=0;i<6;i++){
      const c=document.createElement('canvas');c.width=c.height=128;
      const x=c.getContext('2d'),g=x.createLinearGradient(0,0,0,128);
      g.addColorStop(0,'#7793a5');g.addColorStop(.4,'#344e60');g.addColorStop(1,'#111c26');
      x.fillStyle=g;x.fillRect(0,0,128,128);
      if(i===0||i===2||i===4){
        x.shadowColor=i===2?'#fff1d8':'#b4dcf7';x.shadowBlur=18;
        x.fillStyle=i===2?'#fff3df':'#c9e4f5';x.fillRect(i===4?84:18,12,i===2?82:18,92);
      }
      faces.push(c);
    }
    const cube=new T.CubeTexture(faces);cube.encoding=T.sRGBEncoding;cube.needsUpdate=true;
    const pm=new T.PMREMGenerator(renderer);
    const env=pm.fromCubemap(cube).texture;cube.dispose();pm.dispose();return env;
  }
  scene.environment=makeEnv();
  function noiseTex(){
    const c=document.createElement('canvas');c.width=c.height=256;
    const x=c.getContext('2d'),d=x.createImageData(256,256);
    for(let i=0;i<d.data.length;i+=4){const v=140+Math.random()*90;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255;}
    x.putImageData(d,0,0);
    const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(3,3);return t;
  }
  const rough=noiseTex();

  function col(h){return new T.Color(h).convertSRGBToLinear();}
  scene.add(new T.HemisphereLight(0xd8eaf4,0x142534,.55));
  const key=new T.DirectionalLight(0xffeed6,1.65);key.position.set(-110,230,160);key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);
  key.shadow.camera.left=-185;key.shadow.camera.right=185;key.shadow.camera.top=185;key.shadow.camera.bottom=-185;
  key.shadow.camera.near=1;key.shadow.camera.far=650;key.shadow.bias=-.00025;key.shadow.normalBias=.16;key.shadow.radius=3;scene.add(key);
  const rim=new T.DirectionalLight(0x8cccf2,.95);rim.position.set(130,100,-160);scene.add(rim);
  const fill=new T.DirectionalLight(0xd8eaf7,.45);fill.position.set(100,70,200);scene.add(fill);

  const ground=new T.Mesh(new T.CircleGeometry(270,64),new T.ShadowMaterial({opacity:.36}));
  ground.rotation.x=-Math.PI/2;ground.position.y=-3.5;ground.receiveShadow=true;scene.add(ground);
  const grid=new T.GridHelper(470,24,0x456b81,0x304a5b);
  grid.material.transparent=true;grid.material.opacity=.055;grid.position.y=-3.55;scene.add(grid);

  const board=new T.Group();scene.add(board);
  function box(w,h,d,mat,x,y,z){const m=new T.Mesh(new T.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);m.castShadow=true;board.add(m);return m;}
  function cyl(rt,rb,h,mat,x,y,z,seg){const m=new T.Mesh(new T.CylinderGeometry(rt,rb,h,seg||22),mat);m.position.set(x,y,z);m.castShadow=true;board.add(m);return m;}
  function roundedGeometry(w,h,d,r,holes=[]){
    const b=Math.min(.16,h/4),x=w/2-b,z=d/2-b,shape=new T.Shape();
    shape.moveTo(-x+r,-z);shape.lineTo(x-r,-z);shape.quadraticCurveTo(x,-z,x,-z+r);
    shape.lineTo(x,z-r);shape.quadraticCurveTo(x,z,x-r,z);shape.lineTo(-x+r,z);
    shape.quadraticCurveTo(-x,z,-x,z-r);shape.lineTo(-x,-z+r);shape.quadraticCurveTo(-x,-z,-x+r,-z);
    shape.holes=holes;
    const geometry=new T.ExtrudeGeometry(shape,{depth:h-2*b,bevelEnabled:true,bevelThickness:b,bevelSize:b,bevelSegments:1,steps:1,curveSegments:holes.length?12:4});
    geometry.rotateX(-Math.PI/2);geometry.translate(0,b-h/2,0);return geometry;
  }
  const pcbMat=new T.MeshPhysicalMaterial({color:col(0x0d2e3d),roughness:.42,metalness:.08,clearcoat:.4,clearcoatRoughness:.32,roughnessMap:rough,bumpMap:rough,bumpScale:.015,envMapIntensity:.6});
  const pcbShape=new T.Shape(),px=149.88,pz=79.88,pr=7;
  pcbShape.moveTo(-px+pr,-pz);pcbShape.lineTo(px-pr,-pz);pcbShape.quadraticCurveTo(px,-pz,px,-pz+pr);
  pcbShape.lineTo(px,pz-pr);pcbShape.quadraticCurveTo(px,pz,px-pr,pz);pcbShape.lineTo(-px+pr,pz);
  pcbShape.quadraticCurveTo(-px,pz,-px,pz-pr);pcbShape.lineTo(-px,-pz+pr);pcbShape.quadraticCurveTo(-px,-pz,-px+pr,-pz);
  [[-142,-68],[142,-68],[-142,68],[142,68]].forEach(q=>{
    const hole=new T.Path();hole.absarc(q[0],-q[1],1.85,0,Math.PI*2,true);pcbShape.holes.push(hole);
  });
  const pcb=new T.Mesh(new T.ExtrudeGeometry(pcbShape,{depth:2.96,bevelEnabled:true,bevelThickness:.12,bevelSize:.12,bevelSegments:2,steps:1,curveSegments:8}),pcbMat);
  pcb.name='pcb';pcb.rotation.x=-Math.PI/2;pcb.position.y=.12;pcb.receiveShadow=true;pcb.castShadow=true;board.add(pcb);
  const chipMat=new T.MeshStandardMaterial({color:col(0x131b23),roughness:.82,metalness:.03,envMapIntensity:.22,roughnessMap:rough,bumpMap:rough,bumpScale:.02});
  const goldMat=new T.MeshStandardMaterial({color:col(0xd2ad63),metalness:1,roughness:.3,envMapIntensity:1.05});
  const tinMat=new T.MeshStandardMaterial({color:col(0xc7d1d9),metalness:1,roughness:.34,envMapIntensity:.9});
  const blackMat=new T.MeshStandardMaterial({color:col(0x151d25),roughness:.7,metalness:.04,envMapIntensity:.22});
  const canMat=new T.MeshStandardMaterial({color:col(0xb9c5ce),metalness:.95,roughness:.3,envMapIntensity:.85});
  const whiteMat=new T.MeshStandardMaterial({color:col(0xc6c7bb),roughness:.75,metalness:0});
  const potMat=new T.MeshStandardMaterial({color:col(0x2e6d89),roughness:.5,metalness:.1});
  const traceMat=new T.MeshStandardMaterial({color:col(0x1b4757),roughness:.7,metalness:.08});
  const silkMat=new T.MeshBasicMaterial({color:col(0xa8c3cc)});

  const bodyMat=chipMat;
  const sh=new T.Shape(),s=20,r=1.3;
  sh.moveTo(-s+3.6,-s);sh.lineTo(s-r,-s);sh.quadraticCurveTo(s,-s,s,-s+r);
  sh.lineTo(s,s-r);sh.quadraticCurveTo(s,s,s-r,s);sh.lineTo(-s+r,s);
  sh.quadraticCurveTo(-s,s,-s,s-r);sh.lineTo(-s,-s+3.6);sh.closePath();
  const body=new T.Mesh(new T.ExtrudeGeometry(sh,{depth:4.6,bevelEnabled:true,bevelThickness:.55,bevelSize:.55,bevelSegments:3,steps:1,curveSegments:6}),bodyMat);
  body.rotation.x=-Math.PI/2;body.position.set(-10,4.9,-4);body.castShadow=true;body.receiveShadow=true;board.add(body);

  const leadProfile=new T.Shape();
  leadProfile.moveTo(19.8,6.75);leadProfile.lineTo(21.35,6.75);
  leadProfile.quadraticCurveTo(22.25,6.75,22.7,5.8);leadProfile.lineTo(23.4,4.5);
  leadProfile.quadraticCurveTo(23.7,3.96,24.35,3.96);leadProfile.lineTo(27.4,3.96);
  leadProfile.lineTo(27.4,3.46);leadProfile.lineTo(24.15,3.46);
  leadProfile.quadraticCurveTo(23.05,3.46,22.6,4.35);leadProfile.lineTo(21.95,5.65);
  leadProfile.quadraticCurveTo(21.65,6.25,21.25,6.25);leadProfile.lineTo(19.8,6.25);leadProfile.closePath();
  const leadG=new T.ExtrudeGeometry(leadProfile,{depth:1,bevelEnabled:true,bevelThickness:.06,bevelSize:.06,bevelSegments:1,steps:1,curveSegments:4});
  leadG.rotateY(-Math.PI/2);leadG.translate(.5,0,0);
  const padG=new T.BoxGeometry(1.7,.2,5.2);padG.translate(0,3.3,25.3);
  const solderG=new T.SphereGeometry(1,10,6);solderG.scale(.72,.37,2.15);solderG.translate(0,3.53,25.35);
  const leads=new T.InstancedMesh(leadG,tinMat,64),pads=new T.InstancedMesh(padG,goldMat,64),solder=new T.InstancedMesh(solderG,tinMat,64);
  leads.name='mcu-leads';pads.name='mcu-pads';solder.name='mcu-solder';
  leads.castShadow=true;solder.castShadow=true;
  for(let side=0;side<4;side++){
    const anchor=new T.Matrix4().makeRotationY(side*Math.PI/2);anchor.setPosition(-10,0,-4);
    for(let i=0;i<16;i++){
      const matrix=new T.Matrix4().makeTranslation(-20+2.5*(i+.5),0,0).premultiply(anchor);
      const index=side*16+i;
      leads.setMatrixAt(index,matrix);pads.setMatrixAt(index,matrix);solder.setMatrixAt(index,matrix);
    }
  }
  [leads,pads,solder].forEach(m=>{m.instanceMatrix.needsUpdate=true;board.add(m);});

  function topTexture(){
    const c=document.createElement('canvas');c.width=c.height=1024;
    const x=c.getContext('2d');
    x.fillStyle='rgba(190,196,199,.82)';x.textAlign='left';
    x.font='600 112px "Segoe UI",Arial,sans-serif';x.fillText('STM32',164,354);
    x.font='500 92px Consolas,monospace';x.fillText('F103RCT6',164,482);
    x.strokeStyle='rgba(173,181,188,.34)';x.lineWidth=2;
    x.beginPath();x.moveTo(166,548);x.lineTo(858,548);x.stroke();
    x.fillStyle='rgba(177,187,193,.7)';x.font='500 45px Consolas,monospace';
    x.fillText('ARM  CORTEX-M3',164,644);
    x.font='400 34px Consolas,monospace';x.fillText('LQFP-64',164,714);
    const dot=x.createRadialGradient(114,880,3,122,888,24);
    dot.addColorStop(0,'rgba(0,0,0,.8)');dot.addColorStop(.72,'rgba(0,0,0,.7)');dot.addColorStop(1,'rgba(151,163,173,.5)');
    x.fillStyle=dot;x.beginPath();x.arc(122,888,24,0,Math.PI*2);x.fill();
    const t=new T.CanvasTexture(c);t.anisotropy=4;t.encoding=T.sRGBEncoding;return t;
  }
  const top=new T.Mesh(new T.PlaneGeometry(40,40),new T.MeshStandardMaterial({map:topTexture(),transparent:true,depthWrite:false,roughness:.86,metalness:.04}));
  top.rotation.x=-Math.PI/2;top.position.set(-10,10.08,-4);board.add(top);

  const headerBody=new T.InstancedMesh(roundedGeometry(11.2,3,4.8,.55),blackMat,48);
  const headerPins=new T.InstancedMesh(new T.BoxGeometry(1.6,5.1,1.6),goldMat,48);
  const tipGeometry=new T.CylinderGeometry(.52,1.13,1.2,4);tipGeometry.rotateY(Math.PI/4);
  const headerTips=new T.InstancedMesh(tipGeometry,goldMat,48);
  headerBody.name='header-housings';headerPins.name='header-pins';headerTips.name='header-tips';
  [-72,72].forEach((z,row)=>{
    for(let i=0;i<24;i++){
      const index=row*24+i,x=-134.5+i*11.7;
      const housingMatrix=new T.Matrix4().makeScale((i===0||i===23)?.72:1,1,1);housingMatrix.setPosition(x,4.7,z);
      headerBody.setMatrixAt(index,housingMatrix);
      headerPins.setMatrixAt(index,new T.Matrix4().makeTranslation(x,8.7,z));
      headerTips.setMatrixAt(index,new T.Matrix4().makeTranslation(x,11.85,z));
    }
  });
  [headerBody,headerPins,headerTips].forEach(m=>{m.instanceMatrix.needsUpdate=true;m.castShadow=true;board.add(m);});

  const usbSection=new T.Shape();
  usbSection.moveTo(-4.8,-2.8);usbSection.lineTo(4.8,-2.8);usbSection.lineTo(6,2.8);usbSection.lineTo(-6,2.8);usbSection.closePath();
  const usbCavity=new T.Path();
  usbCavity.moveTo(-4.35,-2.25);usbCavity.lineTo(-5.35,2.25);usbCavity.lineTo(5.35,2.25);usbCavity.lineTo(4.35,-2.25);usbCavity.closePath();usbSection.holes.push(usbCavity);
  const usbGeometry=new T.ExtrudeGeometry(usbSection,{depth:14,bevelEnabled:true,bevelThickness:.12,bevelSize:.12,bevelSegments:1,steps:1});usbGeometry.rotateY(-Math.PI/2);
  const usbShell=new T.Mesh(usbGeometry,canMat);usbShell.name='usb-shell';usbShell.position.set(-135.2,6.35,0);usbShell.castShadow=true;board.add(usbShell);
  box(.55,4.4,9.3,blackMat,-135.2,6.35,0);
  box(10.5,.6,7,blackMat,-141,5.35,0);
  for(let i=0;i<5;i++){const contact=box(5.5,.18,.65,goldMat,-144,5.75,-2.6+i*1.3);contact.name='usb-contact';}
  [-1,1].forEach(side=>box(3.2,.45,1.4,tinMat,-138.5,3.45,side*6.4));
  [-2.7,2.7].forEach(z=>box(2.3,.08,.75,blackMat,-140.8,9.28,z));
  const bridge=new T.Mesh(roundedGeometry(18,2.2,6,.45),blackMat);bridge.position.set(-104,4.3,18);bridge.castShadow=true;board.add(bridge);
  for(let i=0;i<8;i++){
    const x=-104-7.7+i*2.2;
    [13,23].forEach(z=>box(1,.8,4,tinMat,x,3.6,z));
  }
  [{x:-56,z:-30,w:18,d:8.4,h:5.2},{x:-56,z:22,w:8,d:4,h:2.6}].forEach(q=>{
    [-1,1].forEach(side=>{
      const px=q.x+side*q.w*.28;
      cyl(.85,.85,.2,goldMat,px,3.3,q.z,12);
      cyl(.3,.3,1.3,tinMat,px,3.85,q.z,10);
    });
    box(q.w+1,.3,q.d+.8,canMat,q.x,4.4,q.z);
    const outline=new T.Shape(),a=q.w/2,b=q.d/2,r=.9;
    outline.moveTo(-a+r,-b);outline.lineTo(a-r,-b);outline.quadraticCurveTo(a,-b,a,-b+r);
    outline.lineTo(a,b-r);outline.quadraticCurveTo(a,b,a-r,b);outline.lineTo(-a+r,b);
    outline.quadraticCurveTo(-a,b,-a,b-r);outline.lineTo(-a,-b+r);outline.quadraticCurveTo(-a,-b,-a+r,-b);
    const shell=new T.Mesh(new T.ExtrudeGeometry(outline,{depth:q.h,bevelEnabled:true,bevelThickness:.2,bevelSize:.25,bevelSegments:2,steps:1,curveSegments:5}),canMat);
    shell.rotation.x=-Math.PI/2;shell.position.set(q.x,4.55,q.z);shell.castShadow=true;board.add(shell);
  });
  /* LDO + 两颗电解电容（黑壳银顶 + 负极白条） */
  box(11,3.2,7,blackMat,-66,4.8,34);
  box(6,1.6,4,canMat,-66,4.2,39);
  [[-112,48],[-94,48]].forEach(q=>{
    cyl(4.5,4.5,9,blackMat,q[0],7.7,q[1]);
    cyl(4.5,4.5,.6,canMat,q[0],12.4,q[1]);
    [-1,1].forEach(sign=>{
      const vent=box(5.7,.08,.22,blackMat,q[0],12.72,q[1]);vent.rotation.y=sign*Math.PI/4;vent.castShadow=false;
    });
    box(1,6,.5,silkMat,q[0]+4.2,7.7,q[1]);
  });
  /* 电源拨动开关 */
  box(10,3,6,blackMat,-134,4.7,48);
  box(3,2,2,canMat,-134,6.7,48);
  function tactile(x,z,size,radius){
    box(size,.4,size,blackMat,x,3.4,z);
    const well=new T.Path();well.absarc(0,0,2.7,0,Math.PI*2,true);
    const base=new T.Mesh(roundedGeometry(size,2.65,size,.55,[well]),blackMat);
    base.name='switch-housing';base.position.set(x,4.925,z);base.castShadow=true;board.add(base);
    const aperture=new T.Path();aperture.absarc(0,0,radius>2?2.6:2.25,0,Math.PI*2,true);
    const lid=new T.Mesh(roundedGeometry(size-.8,.4,size-.8,.5,[aperture]),canMat);
    lid.name='switch-cover';lid.position.set(x,6.45,z);lid.castShadow=true;board.add(lid);
    [-1,1].forEach(side=>[-2.4,2.4].forEach(dz=>box(2.5,.35,1.1,tinMat,x+side*(size/2+.4),3.45,z+dz)));
    return cyl(radius,radius,1.6,blackMat,x,6.9,z,40);
  }
  const plunger=tactile(-42,48,9,2.2);
  box(12,3,8,blackMat,-42,4.7,-48);
  [-46,-38].forEach(x=>[-51,-45].forEach(z=>box(1.8,5,1.8,goldMat,x,8,z)));
  const key1Top=tactile(36,-50,8,1.8),key2Top=tactile(62,-50,8,1.8);
  /* 蜂鸣器（顶开孔） */
  cyl(7,7,7,blackMat,36,6.7,50);
  cyl(2,2,.4,new T.MeshStandardMaterial({color:col(0x05070a),roughness:.9}),36,10.3,50);
  /* 蓝白电位器 + 金属螺丝 */
  box(9,6,9,potMat,62,6.2,50);
  cyl(2,2,1,canMat,62,9.7,50);
  box(2.6,.4,.6,blackMat,62,10.3,50);
  box(19.6,.55,16.2,blackMat,52,3.475,14);
  box(12,.9,10,blackMat,50,4.2,14);
  [6,22].forEach(z=>box(20,2.6,.5,canMat,52,4.9,z));
  box(.5,2.6,16,canMat,42.25,4.9,14);
  const sdWindows=[-4.8,4.8].map(z=>{
    const cut=new T.Path();cut.moveTo(-3,z-1.25);cut.lineTo(-3,z+1.25);cut.lineTo(1,z+1.25);cut.lineTo(1,z-1.25);cut.closePath();return cut;
  });
  const sdCover=new T.Mesh(roundedGeometry(20,.45,17,.7,sdWindows),canMat);
  sdCover.name='sd-cover';sdCover.position.set(52,6.35,14);sdCover.castShadow=true;board.add(sdCover);
  [-1,1].forEach(side=>box(2.6,.35,1.7,tinMat,47,3.45,14+side*8.5));
  const cardShape=new T.Shape();
  cardShape.moveTo(-10,-6);cardShape.lineTo(7.8,-6);cardShape.lineTo(10,-3.8);cardShape.lineTo(10,6);cardShape.lineTo(-10,6);cardShape.closePath();
  const cardGeometry=new T.ExtrudeGeometry(cardShape,{depth:.8,bevelEnabled:true,bevelThickness:.08,bevelSize:.08,bevelSegments:1,steps:1});cardGeometry.rotateX(-Math.PI/2);
  const card=new T.Mesh(cardGeometry,blackMat);card.name='sd-card';card.position.set(61,4.75,14);card.castShadow=true;board.add(card);
  [10,12,14,16,18].forEach(z=>box(4,.12,.25,silkMat,67,5.7,z));
  const memory=new T.Mesh(roundedGeometry(8,2,5,.35),blackMat);memory.position.set(36,4.2,-26);memory.castShadow=true;board.add(memory);
  for(let i=0;i<4;i++){
    const x=36-3+i*2;
    [-29.5,-22.5].forEach(z=>box(.8,.7,2.4,tinMat,x,3.6,z));
  }
  box(12,1.25,9,whiteMat,-134,3.825,32);
  const jstCavity=new T.Path();jstCavity.moveTo(-4.9,-3.1);jstCavity.lineTo(-4.9,3.1);jstCavity.lineTo(4.9,3.1);jstCavity.lineTo(4.9,-3.1);jstCavity.closePath();
  const jst=new T.Mesh(roundedGeometry(12,4.7,9,.55,[jstCavity]),whiteMat);
  jst.name='jst-housing';jst.position.set(-134,6.8,32);jst.castShadow=true;board.add(jst);
  [-137,-131].forEach(x=>{const pin=box(1.2,3.7,1.2,goldMat,x,6.25,32);pin.name='jst-contact';});
  box(2,1,1.2,whiteMat,-134,8.65,28.3);
  /* 晶振负载电容 / 去耦电容（0603 MLCC）与 0805 */
  const resMat=new T.MeshStandardMaterial({color:col(0x1b1e22),roughness:.7,metalness:.1});
  const mlccMat=new T.MeshStandardMaterial({color:col(0xc7a86a),roughness:.55,metalness:.15});
  const indMat=new T.MeshStandardMaterial({color:col(0x3a3f45),roughness:.5,metalness:.3});
  const tantMat=new T.MeshStandardMaterial({color:col(0xc9a13a),roughness:.45,metalness:.25});
  function smd(x,z,mat,w,d,h){
    box(w,h,d,mat,x,3.2+h/2,z);
    [-1,1].forEach(sx=>box(w*.24,h+.2,d+.2,tinMat,x+sx*(w/2-w*.12),3.2+h/2,z));
  }
  function res(x,z){smd(x,z,resMat,7.5,3.7,1.8);}
  function cap(x,z){smd(x,z,mlccMat,7.5,3.7,2);}
  /* MCU 四边去耦电容（避开引脚末端外扩 8 个单位） */
  [-28,-18,-8,2].forEach(x=>cap(x,-48));
  [-32,-22,-12,-2].forEach(x=>cap(x,40));
  [-6,2,10].forEach(z=>cap(-56,z));
  [-18,-8,2].forEach(z=>cap(36,z));
  /* 晶振负载电容 */
  cap(-52,-44);cap(-52,-20);cap(-66,14);cap(-48,30);
  /* LDO 输入输出：钽电容 + MLCC + 功率电感 + 磁珠 + 防反二极管 */
  smd(-80,26,tantMat,12,7,6);smd(-80,44,tantMat,12,7,6);
  cap(-54,28);cap(-54,44);
  smd(-96,26,indMat,13,10,5);
  smd(-110,34,resMat,7,4,2.6);
  smd(-124,34,blackMat,7,4,2.4);
  box(1,2.6,4.4,silkMat,-124,4.4,32.6);
  /* USB 串阻与上拉、ESD */
  res(-124,6);res(-124,-2);res(-118,-14);
  box(6,2.4,8,blackMat,-134,4.4,-16);
  for(let i=0;i<3;i++){box(1,.8,3,tinMat,-137+i*3,3.6,-21);box(1,.8,3,tinMat,-137+i*3,3.6,-11);}
  /* 复位上拉与电容 */
  res(-30,48);cap(-30,60);
  /* LED 限流电阻 */
  [-56,-28,-4,20].forEach(z=>res(92,z));
  /* OLED I2C 上拉 */
  res(-124,-64);res(-112,-64);
  /* 电位器与 SD 上拉、排阻 */
  res(50,36);cap(74,36);res(36,28);
  [8,20].forEach(x=>res(x,-50));
  /* 驱动三极管 SOT-23 */
  [[24,36],[88,28]].forEach(q=>{
    box(5,2.2,6,blackMat,q[0],4.3,q[1]);
    box(1.2,.8,2.6,tinMat,q[0]-1.6,3.5,q[1]+4);
    box(1.2,.8,2.6,tinMat,q[0]+1.6,3.5,q[1]+4);
    box(1.2,.8,2.6,tinMat,q[0],3.5,q[1]-4);
  });
  /* SWD 1×4 */
  box(10,3,26,blackMat,134,4.7,-24);
  [-34,-29,-24,-19].forEach(z=>box(1.8,6,1.8,goldMat,134,9,z));
  /* LED：PWR / LED1(PC3) / LED3(PC1) / TX */
  function ledMesh(color,emissive){
    return new T.Mesh(new T.CylinderGeometry(2.4,2.4,2.4,22),
      new T.MeshStandardMaterial({color:col(color),emissive:col(emissive),emissiveIntensity:.9,roughness:.25,metalness:.1}));
  }
  const ledPwr=ledMesh(0xffb35c,0xff9a3c);ledPwr.position.set(104,4.6,-56);board.add(ledPwr);
  const led=ledMesh(0x9cc4e8,0x7fb2e5);led.position.set(104,4.6,-28);board.add(led);
  const led3=ledMesh(0x9cc4e8,0x7fb2e5);led3.position.set(104,4.6,-4);board.add(led3);
  const ledTx=ledMesh(0xffb35c,0xff9a3c);ledTx.position.set(104,4.6,20);board.add(ledTx);
  /* 测试焊盘 + 右侧原型焊盘区 */
  for(let i=0;i<8;i++)box(3,.4,3,goldMat,20+i*10,3.5,64);
  for(let r=0;r<4;r++)for(let c=0;c<6;c++)box(2.2,.35,2.2,tinMat,84+c*8,3.4,30+r*8);
  [[-142,-68],[142,-68],[-142,68],[142,68]].forEach(q=>{
    const ring=new T.Mesh(new T.RingGeometry(1.85,3.4,32),goldMat);
    ring.rotation.x=-Math.PI/2;ring.position.set(q[0],3.24,q[1]);board.add(ring);
    const wall=new T.Mesh(new T.CylinderGeometry(1.85,1.85,3.2,24,1,true),new T.MeshStandardMaterial({color:col(0xb99b61),metalness:1,roughness:.36,side:T.DoubleSide}));
    wall.position.set(q[0],1.6,q[1]);board.add(wall);
  });
  /* 走线：USB→串口桥→主控、主控→排针 */
  [6,10].forEach(z=>box(18,.4,1.2,traceMat,-122,3.4,z));
  [14,18].forEach(z=>box(52,.4,1.2,traceMat,-70,3.4,z));
  [-24,-16,-8,0].forEach(x=>{
    box(1.2,.4,40,traceMat,x,3.4,46);
    box(1.2,.4,32,traceMat,x,3.4,-52);
  });
  /* OLED 模块：小板 + 金属框 + 黑玻璃 + 自发光字 */
  box(68,2,38,pcbMat,-100,4.2,-38);
  [[-100,-56,68,1],[-100,-20,68,1],[-133,-38,1,36],[-67,-38,1,36]].forEach(q=>{
    const m=new T.Mesh(new T.BoxGeometry(q[2],.8,q[3]),canMat);m.position.set(q[0],5.1,q[1]);board.add(m);});
  box(58,.6,26,new T.MeshStandardMaterial({color:col(0x05080c),roughness:.35,metalness:.2}),-100,5.4,-38);
  function oledTexture(){
    const c=document.createElement('canvas');c.width=512;c.height=224;
    const x=c.getContext('2d');
    x.fillStyle='#0a0f14';x.fillRect(0,0,512,224);
    x.strokeStyle='rgba(156,196,232,.9)';x.lineWidth=3;
    x.beginPath();x.arc(444,86,42,0,Math.PI*2);x.stroke();
    x.beginPath();x.arc(444,86,16,0,Math.PI*2);x.stroke();
    x.beginPath();x.moveTo(444,32);x.lineTo(444,140);x.moveTo(390,86);x.lineTo(498,86);x.stroke();
    x.fillStyle='#cfe4f8';x.textAlign='left';
    x.font='600 34px "Segoe UI",Arial,sans-serif';x.fillText('EMBEDDED LENS',22,58);
    x.fillStyle='#9cc4e8';x.font='400 28px Consolas,monospace';x.fillText('HALT → READ → RESUME',22,120);
    x.fillStyle='rgba(156,196,232,.72)';x.font='400 24px Consolas,monospace';x.fillText('SWD · 2-WIRE',22,178);
    const t=new T.CanvasTexture(c);t.anisotropy=4;t.encoding=T.sRGBEncoding;return t;
  }
  const oledMap=oledTexture();
  const oled=new T.Mesh(new T.PlaneGeometry(58,26),new T.MeshPhysicalMaterial({map:oledMap,emissiveMap:oledMap,emissive:col(0x9dd8e2),emissiveIntensity:.4,roughness:.26,metalness:.08,clearcoat:1,clearcoatRoughness:.18}));
  oled.rotation.x=-Math.PI/2;oled.position.set(-100,5.75,-38);board.add(oled);
  /* 丝印位号与名称 */
  function pcbTexture(){
    const c=document.createElement('canvas');c.width=1536;c.height=816;
    const x=c.getContext('2d');
    x.save();x.scale(c.width/300,c.height/160);x.translate(150,80);
    [[-10,-4,31,31],[-100,-38,39,23],[-112,48,7,7],[-94,48,7,7],[52,14,15,13],[36,50,10,10],[-56,-30,13,8]].forEach(q=>{
      x.save();x.translate(q[0],q[1]);x.scale(q[2],q[3]);
      const shade=x.createRadialGradient(0,0,.35,0,0,1);shade.addColorStop(0,'rgba(0,8,15,.4)');shade.addColorStop(.62,'rgba(0,8,15,.2)');shade.addColorStop(1,'rgba(0,8,15,0)');
      x.fillStyle=shade;x.fillRect(-1,-1,2,2);x.restore();
    });
    x.restore();
    x.save();x.scale(c.width/300,c.height/160);x.translate(140,76);
    for(let side=0;side<4;side++){
      x.save();x.rotate(-side*Math.PI/2);
      for(let i=0;i<16;i+=2){
        const off=-20+2.5*(i+.5),end=32.2+(i%3)*.8,fan=off+(i<8?-.8:.8);
        x.strokeStyle='rgba(82,141,170,.62)';x.lineWidth=.28;
        x.beginPath();x.moveTo(off,27.9);x.lineTo(off,29.2);x.lineTo(fan,30.3);x.lineTo(fan,end);x.stroke();
        x.fillStyle='rgba(193,178,134,.82)';x.beginPath();x.arc(fan,end,.58,0,Math.PI*2);x.fill();
        x.fillStyle='#0a2333';x.beginPath();x.arc(fan,end,.28,0,Math.PI*2);x.fill();
      }
      x.restore();
    }
    x.strokeStyle='rgba(216,231,237,.72)';x.lineWidth=.34;
    [-1,1].forEach(sx=>[-1,1].forEach(sz=>{
      x.beginPath();x.moveTo(sx*24.8,sz*29.8);x.lineTo(sx*29.8,sz*29.8);x.lineTo(sx*29.8,sz*24.8);x.stroke();
    }));
    x.fillStyle='rgba(216,231,237,.86)';
    x.beginPath();x.moveTo(-32.5,29.6);x.lineTo(-29.6,32.5);x.lineTo(-32.5,32.5);x.closePath();x.fill();
    x.restore();
    function label(txt,wx,wz,size,col){x.fillStyle=col||'rgba(214,232,248,.85)';x.font='500 '+size+'px Consolas,monospace';x.textAlign='center';
      x.fillText(txt,(wx+150)/300*1536,816*(.5+wz/160));}
    label('U1',28,32,24);label('1',-37,29,15);
    label('Y1',-56,-44,20);label('Y2',-64,22,20);
    label('U2',-104,30,20);label('U3',-66,54,20);
    label('OLED',-100,-16,22);
    label('SD',52,28,20);
    label('BUZ',24,50,20);
    label('KEY1',26,-50,18);label('KEY2',52,-50,18);
    label('RST',-42,34,20);label('BOOT0',-42,-38,20);
    label('SWD',134,-44,22);
    label('PC3',104,-18,20);label('PC1',104,6,20);
    label('PWR',104,-46,20);label('TX',104,10,18);
    label('J1',-134,44,20);label('VBAT',-116,32,18);
    label('PROTO',104,66,18);
    label('C1',-28,-54,16);label('C5',-22,48,16);label('C9',-64,-6,16);label('C12',44,-18,16);
    label('C15',-52,-52,16);label('C16',-52,-12,16);label('C17',-74,14,16);label('C18',-56,38,16);
    label('C19',-80,16,16);label('C20',-80,54,16);label('C21',-54,20,16);label('C22',-54,54,16);
    label('L1',-96,36,16);label('FB1',-110,42,16);label('D1',-124,42,16);
    label('Q1',24,44,16);label('Q2',88,20,16);
    label('R1',-124,14,16);label('R3',-118,-22,16);label('R4',-30,56,16);label('R5',84,-56,16);
    label('R9',-124,-58,16);label('R10',-112,-58,16);
    label('R11',50,28,16);label('R12',36,20,16);label('R13',8,-58,16);label('R14',20,-58,16);
    label('ESD',-134,-6,14);
    const pinTop=['3V3','GND','PA0','PA1','PA2','PA3','PA4','PA5','PA6','PA7','PB0','PB1','PB2','PB3','PB4','PB5','PB6','PB7','PB8','PB9','PC13','PC14','PC15','VBAT'];
    const pinBot=['GND','5V','PA8','PA9','PA10','PA11','PA12','PA13','PA14','PA15','PB10','PB11','PB12','PB13','PB14','PB15','PC0','PC1','PC2','PC3','PC4','PC5','PC6','PC7'];
    pinTop.forEach((p,i)=>label(p,-134.5+i*11.7,-62,15,'rgba(214,232,248,.78)'));
    pinBot.forEach((p,i)=>label(p,-134.5+i*11.7,60,15,'rgba(214,232,248,.78)'));
    label('E M B E D D E D  L E N S',0,68,30,'rgba(159,196,232,.6)');
    const t=new T.CanvasTexture(c);t.anisotropy=4;t.encoding=T.sRGBEncoding;return t;
  }
  const pcbTop=new T.Mesh(new T.PlaneGeometry(300,160),new T.MeshBasicMaterial({map:pcbTexture(),transparent:true,depthWrite:false}));
  pcbTop.rotation.x=-Math.PI/2;pcbTop.position.y=3.26;board.add(pcbTop);

  const ringGroup=new T.Group();ringGroup.position.set(-10,22,-4);scene.add(ringGroup);
  const ring=new T.Mesh(new T.TorusGeometry(38,.4,8,120),
    new T.MeshBasicMaterial({color:col(0x71b2c2),transparent:true,opacity:.16}));
  ring.rotation.x=-Math.PI/2+.26;ringGroup.add(ring);

  const state={yaw:.56,pitch:.87,radius:420,zoom:1,lookX:0,lookY:0,auto:!RM2.matches,freeze:false,dragging:false,pinching:false,inspecting:false};
  let renderHost=host,inspection=null,inspectionParts=null;
  function fit(){
    const w=renderHost.clientWidth,h=renderHost.clientHeight;if(!w||!h)return;
    renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
    const tan=Math.tan(16*Math.PI/180),half=state.inspecting?66:178;
    state.radius=Math.max(half/tan,half/(tan*camera.aspect));
  }
  fit();
  const sizeObserver=new ResizeObserver(fit);sizeObserver.observe(host);
  function buildInspection(){
    if(inspectionParts)return;
    const group=new T.Group();group.name='inspection-core';group.position.set(-10,5,-4);group.visible=false;board.add(group);
    const die=new T.Mesh(new T.BoxGeometry(19,1.4,19),new T.MeshStandardMaterial({color:col(0x184849),metalness:.65,roughness:.32}));group.add(die);
    const c=document.createElement('canvas');c.width=c.height=512;const x=c.getContext('2d');
    x.fillStyle='#123330';x.fillRect(0,0,512,512);x.strokeStyle='#458f7d';x.lineWidth=2;
    for(let i=20;i<500;i+=20){x.beginPath();x.moveTo(i,0);x.lineTo(i,512);x.moveTo(0,i);x.lineTo(512,i);x.stroke();}
    [[32,32,212,212,'CORE'],[270,32,210,130,'FLASH'],[270,188,210,292,'SRAM'],[32,270,212,210,'I/O']].forEach(q=>{
      x.fillStyle='#142b2e';x.fillRect(q[0],q[1],q[2],q[3]);x.strokeStyle='#94ddba';x.strokeRect(q[0],q[1],q[2],q[3]);
      x.fillStyle='#caf5d5';x.font='26px Consolas,monospace';x.fillText(q[4],q[0]+12,q[1]+40);
    });
    const tex=new T.CanvasTexture(c);tex.encoding=T.sRGBEncoding;
    const surface=new T.Mesh(new T.PlaneGeometry(18.5,18.5),new T.MeshBasicMaterial({map:tex}));surface.rotation.x=-Math.PI/2;surface.position.y=.72;group.add(surface);
    const points=[];
    for(let side=0;side<4;side++)for(let i=0;i<6;i++){
      const rotation=new T.Matrix4().makeRotationY(side*Math.PI/2),off=-7.5+i*3;
      [[off,.6,9],[off,3,13],[off,3,13],[off,-1.2,19]].forEach(p=>points.push(new T.Vector3(...p).applyMatrix4(rotation)));
    }
    group.add(new T.LineSegments(new T.BufferGeometry().setFromPoints(points),new T.LineBasicMaterial({color:col(0xd8bf7c),transparent:true,opacity:.82})));
    const focus=new T.Mesh(new T.PlaneGeometry(7,7),new T.MeshBasicMaterial({color:col(0xa4ffd7),transparent:true,opacity:.3,depthWrite:false}));
    focus.rotation.x=-Math.PI/2;focus.position.y=.8;group.add(focus);
    const shellMaterial=body.material.clone(),labelMaterial=top.material.clone();
    [shellMaterial,labelMaterial].forEach(m=>{m.transparent=true;m.depthWrite=false;});
    inspectionParts={group,focus,shellMaterial,labelMaterial};
  }
  function beginInspection(viewport){
    if(inspection)return;
    buildInspection();if(G)G.killTweensOf(state);clearTimeout(idle);pts.clear();
    inspection={parent:canvas.parentNode,next:canvas.nextSibling,yaw:state.yaw,pitch:state.pitch,zoom:state.zoom,lookX:state.lookX,lookY:state.lookY,auto:state.auto,freeze:state.freeze,
      boardPosition:board.position.clone(),boardRotation:board.rotation.clone(),bodyY:body.position.y,topY:top.position.y,bodyMaterial:body.material,topMaterial:top.material,castShadow:body.castShadow};
    state.inspecting=true;state.dragging=false;state.pinching=false;state.auto=false;state.freeze=true;state.yaw=.62;state.pitch=.84;state.zoom=1;state.lookX=state.lookY=0;
    board.position.set(0,0,0);board.rotation.set(0,0,0);body.castShadow=false;
    body.material=inspectionParts.shellMaterial;top.material=inspectionParts.labelMaterial;body.material.emissive.setHex(0);
    renderHost=viewport;viewport.appendChild(canvas);sizeObserver.observe(viewport);fit();
  }
  function setInspectionTarget(index){
    if(!inspectionParts)return;
    const locations=[[4.8,-6],[-4.8,-4.8],[4.8,3.5],[-4.8,4.8]];
    inspectionParts.focus.position.set(locations[index][0],.8,locations[index][1]);
  }
  function setInspectionStep(step){
    if(!inspection)return;
    const open=step===1,parts=inspectionParts,targets=[body.position,top.position,body.material,top.material];
    if(G)targets.forEach(t=>G.killTweensOf(t));
    parts.group.visible=open;
    const change=(target,values)=>{if(G&&!RM2.matches)G.to(target,{...values,duration:.7,ease:'power3.inOut',overwrite:true});else Object.assign(target,values);};
    change(body.position,{y:inspection.bodyY+(open?34:0)});change(top.position,{y:inspection.topY+(open?34:0)});
    change(body.material,{opacity:open?.18:1});change(top.material,{opacity:open?.25:1});
    setInspectionTarget(0);
  }
  function endInspection(){
    if(!inspection)return;
    if(G)[body.position,top.position,body.material,top.material].forEach(t=>G.killTweensOf(t));
    const saved=inspection;inspection=null;inspectionParts.group.visible=false;
    body.position.y=saved.bodyY;top.position.y=saved.topY;body.material=saved.bodyMaterial;top.material=saved.topMaterial;body.castShadow=saved.castShadow;
    board.position.copy(saved.boardPosition);board.rotation.copy(saved.boardRotation);
    for(const k of ['yaw','pitch','zoom','lookX','lookY','auto','freeze'])state[k]=saved[k];
    state.inspecting=false;targetZoom=state.zoom;state.dragging=false;state.pinching=false;pts.clear();
    sizeObserver.unobserve(renderHost);saved.parent.insertBefore(canvas,saved.next);renderHost=host;canvas.style.cursor='grab';fit();
    if(!state.auto)idle=setTimeout(()=>{state.auto=!RM2.matches;},2600);
  }

  const ray=new T.Raycaster(),pt=new T.Vector2();
  let downX=0,downY=0,lastX=0,lastY=0,idle=null,targetZoom=1;
  function hitAt(e){
    const b=canvas.getBoundingClientRect();
    pt.x=((e.clientX-b.left)/b.width)*2-1;pt.y=-((e.clientY-b.top)/b.height)*2+1;
    ray.setFromCamera(pt,camera);
    const hits=ray.intersectObjects([body,key1Top,key2Top,plunger,led,led3],false);
    if(!hits.length)return null;
    const o=hits[0].object;
    return o===body?'chip':o===key1Top?'key1':o===key2Top?'key2':o===plunger?'reset':o===led?'led1':o===led3?'led3':null;
  }
  const fx=[];
  function flashLed(mesh,times){
    fx.push({mesh:mesh,until:performance.now()+(times||1)*1500});
    if(G&&!RM2.matches)G.fromTo(mesh.scale,{x:1,y:1,z:1},{x:1.35,y:1.35,z:1.35,duration:.16,yoyo:true,repeat:1,ease:'power2.out'});
  }
  function pressFeedback(kind){
    const target=kind==='key1'?key1Top:kind==='key2'?key2Top:plunger;
    if(G&&!RM2.matches){const y0=target.position.y;G.to(target.position,{y:y0-1.3,duration:.09,yoyo:true,repeat:1,ease:'power1.inOut'});}
    if(kind==='reset'){
      flashLed(led,2);flashLed(led3,2);
      state.auto=false;clearTimeout(idle);idle=setTimeout(()=>{state.auto=!RM2.matches;},1700);
    }else flashLed(kind==='key1'?led:led3,1);
  }
  function zoomTo(z){
    if(state.inspecting)return;
    targetZoom=Math.max(.55,Math.min(2.3,z));
    if(G&&!RM2.matches)G.to(state,{zoom:targetZoom,duration:.32,ease:'power2.out',overwrite:'auto'});
    else state.zoom=targetZoom;
  }
  function resetView(){
    if(state.inspecting)return;
    targetZoom=1;
    if(G&&!RM2.matches)G.to(state,{yaw:.56,pitch:.87,zoom:1,duration:.6,ease:'power3.inOut',overwrite:'auto'});
    else{state.yaw=.56;state.pitch=.87;state.zoom=1;}
  }
  const pts=new Map();let pinchDist=0,touchAxis=null;
  function twoDist(){const a=[...pts.values()];return a.length<2?0:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);}
  canvas.addEventListener('pointerdown',e=>{
    if(state.inspecting)return;
    pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(canvas.setPointerCapture)canvas.setPointerCapture(e.pointerId);
    if(pts.size===2){state.pinching=true;state.dragging=false;state.auto=false;pinchDist=twoDist();clearTimeout(idle);}
    else if(pts.size===1){
      state.dragging=true;state.auto=false;clearTimeout(idle);
      downX=lastX=e.clientX;downY=lastY=e.clientY;touchAxis=e.pointerType==='touch'?null:'rotate';
    }
  });
  canvas.addEventListener('pointermove',e=>{
    if(state.inspecting)return;
    if(pts.has(e.pointerId))pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(state.pinching){
      if(pts.size>=2){const d=twoDist();if(d>0&&pinchDist>0)zoomTo(targetZoom*(pinchDist/d));pinchDist=d;}
      return;
    }
    if(state.dragging){
      if(touchAxis===null){
        const dx=e.clientX-downX,dy=e.clientY-downY;
        if(Math.hypot(dx,dy)<6)return;
        touchAxis=Math.abs(dx)>=Math.abs(dy)?'rotate':'scroll';
      }
      if(touchAxis==='scroll')return;
      state.yaw-=(e.clientX-lastX)*.006;
      state.pitch=Math.max(.45,Math.min(1.38,state.pitch-(e.clientY-lastY)*.005));
      lastX=e.clientX;lastY=e.clientY;
    }else{
      const hov=hitAt(e);
      canvas.style.cursor=hov?'pointer':'grab';
      bodyMat.emissive.setHex(hov==='chip'?0x122436:0x000000);
    }
  });
  function endDrag(e){
    if(state.inspecting)return;
    pts.delete(e.pointerId);
    if(state.pinching){if(pts.size<2){state.pinching=false;idle=setTimeout(()=>{state.auto=!RM2.matches;},2600);}return;}
    if(!state.dragging)return;
    state.dragging=false;
    idle=setTimeout(()=>{state.auto=!RM2.matches;},2600);
    if(e.type!=='pointercancel'&&touchAxis!=='scroll'&&Math.hypot(e.clientX-downX,e.clientY-downY)<6){
      const h=hitAt(e);
      if(h==='chip')registerEggClick();
      else if(h==='key1'||h==='key2'||h==='reset')pressFeedback(h);
      else if(h==='led1')flashLed(led,1);
      else if(h==='led3')flashLed(led3,1);
    }
  }
  canvas.addEventListener('pointerup',endDrag);
  canvas.addEventListener('pointercancel',endDrag);
  canvas.addEventListener('pointerleave',()=>{bodyMat.emissive.setHex(0x000000);canvas.style.cursor='grab';});
  canvas.addEventListener('wheel',e=>{if(state.inspecting)return;e.preventDefault();zoomTo(targetZoom*Math.exp(e.deltaY*.0011));},{passive:false});
  canvas.addEventListener('dblclick',e=>{e.preventDefault();if(!state.inspecting&&hitAt(e)!=='chip')resetView();});
  const zin=$('ldzin'),zout=$('ldzout'),zreset=$('ldzreset');
  if(zin)zin.addEventListener('click',()=>zoomTo(targetZoom/1.22));
  if(zout)zout.addEventListener('click',()=>zoomTo(targetZoom*1.22));
  if(zreset)zreset.addEventListener('click',resetView);

  let prev=0;
  renderer.setAnimationLoop(t=>{
    if(document.hidden||renderHost.offsetParent===null)return;
    const dt=prev?Math.min(.06,(t-prev)/1000):0;prev=t;
    if(state.auto&&!state.dragging&&!state.freeze)state.yaw+=dt*.035;
    const yaw=state.yaw+state.lookX*.22,pitch=state.pitch+state.lookY*.07;
    const sp=Math.sin(pitch),rad=state.radius*state.zoom;
    const centerX=state.inspecting?-10:0,centerY=state.inspecting?18:12,centerZ=state.inspecting?-4:0;
    camera.position.set(centerX+rad*sp*Math.sin(yaw),rad*Math.cos(pitch)+centerY,centerZ+rad*sp*Math.cos(yaw));
    camera.lookAt(centerX,centerY,centerZ);
    if(!state.freeze&&!RM2.matches){board.position.y=Math.sin(t/2100)*.65;board.rotation.z=Math.sin(t/3200)*.005;ringGroup.rotation.y+=dt*.2;}
    led.material.emissiveIntensity=state.freeze?.55:.7+Math.sin(t/700)*.35;
    led3.material.emissiveIntensity=.9;
    for(let i=fx.length-1;i>=0;i--){
      const f=fx[i];
      if(performance.now()>f.until){fx.splice(i,1);continue;}
      f.mesh.material.emissiveIntensity=(Math.floor(t/150)%2===0)?2.4:.05;
    }
    renderer.render(scene,camera);
  });
  host.classList.add('gl-ok');
  return {state:state,beginInspection,setInspectionStep,setInspectionTarget,endInspection,setLook(nx,ny){if(!state.inspecting){state.lookX=nx;state.lookY=ny;}}};
}
const gl=init3D();

/* 标题逐字拆分（入场 + 悬停） */
document.querySelectorAll('.ld-word').forEach(w=>{
  const txt=w.textContent;w.textContent='';
  [...txt].forEach(ch=>{const s=document.createElement('span');s.className='ch';s.textContent=ch;w.appendChild(s);});
});
const chars=document.querySelectorAll('.ld-title .ch');
const words=[...document.querySelectorAll('.ld-word')];

function landingIn(){
  if(!G||RM2.matches){words.forEach(w=>w.style.overflow='visible');
    if(G)G.set('.ld-main, .ld-stage, .ld-marquee, .ld-main > *',{opacity:1,clearProps:'transform'});
    return;}
  words.forEach(w=>w.style.overflow='hidden');
  G.set('.ld-main, .ld-stage, .ld-marquee',{opacity:1,y:0});
  G.set('.ld-title',{opacity:1,y:0});
  G.fromTo('.ld-kicker',{opacity:0,y:10},{opacity:1,y:0,duration:.5,delay:.15,ease:'power3.out',overwrite:'auto'});
  G.fromTo(chars,{yPercent:110},{yPercent:0,duration:.85,stagger:.028,ease:'power4.out',delay:.2,overwrite:'auto'});
  G.fromTo('.ld-zh',{opacity:0},{opacity:1,duration:.8,delay:.55,ease:'power2.out',overwrite:'auto'});
  G.fromTo('.ld-manifesto, .ld-sub',{opacity:0,y:12},{opacity:1,y:0,duration:.6,delay:.5,stagger:.08,ease:'power3.out',overwrite:'auto'});
  G.fromTo('.ld-actions',{opacity:0,y:10},{opacity:1,y:0,duration:.55,delay:.66,ease:'power3.out',overwrite:'auto'});
  G.fromTo('.ld-meta, .ld-build',{opacity:0},{opacity:1,duration:.5,delay:.74,stagger:.07,overwrite:'auto'});
  G.fromTo('.ld-stage',{opacity:0,scale:.94},{opacity:1,scale:1,duration:1.05,delay:.25,ease:'power3.out',overwrite:'auto'});
  G.fromTo('.ld-marquee',{opacity:0},{opacity:1,duration:.5,delay:.85,overwrite:'auto'});
  G.delayedCall(1.5,()=>words.forEach(w=>w.style.overflow='visible'));
}

/* 常驻动效：刻度旋转、节点反向旋转、核心脉冲、跑马灯 */
let marqTween=null,ambient=[];
if(G&&!RM2.matches){
  ambient.push(
    G.to('#ldticks',{rotation:360,svgOrigin:'280 280',duration:110,repeat:-1,ease:'none'}),
    G.to('#ldrev',{rotation:-360,svgOrigin:'280 280',duration:52,repeat:-1,ease:'none'}),
    G.fromTo('.ld-core',{scale:1,opacity:.9},{scale:3,opacity:0,duration:2,repeat:-1,ease:'power1.out',svgOrigin:'280 280',repeatDelay:.6}));
  marqTween=G.to('#ldmarq',{xPercent:-50,duration:32,ease:'none',repeat:-1});
  const mq=document.querySelector('.ld-marquee');
  if(mq){mq.addEventListener('pointerenter',()=>marqTween&&marqTween.pause());
    mq.addEventListener('pointerleave',()=>marqTween&&marqTween.resume());}
}

/* 指针：透镜点跟随 + 3D 视差 + 字符悬停 + CTA 磁吸 */
if(G&&!RM2.matches){
  G.set(scope,{transformPerspective:900});
  const xq=G.quickTo(probe,'x',{duration:.16,ease:'power2.out'});
  const yq=G.quickTo(probe,'y',{duration:.16,ease:'power2.out'});
  const ry=G.quickTo(scope,'rotationY',{duration:.7,ease:'power3.out'});
  const rx=G.quickTo(scope,'rotationX',{duration:.7,ease:'power3.out'});
  const tx=G.quickTo('.ld-main','x',{duration:.9,ease:'power3.out'});
  const ty=G.quickTo('.ld-main','y',{duration:.9,ease:'power3.out'});
  landing.addEventListener('pointermove',e=>{
    if(e.pointerType==='touch'||eggDialog.open)return;
    probe.style.opacity=1;xq(e.clientX-4.5);yq(e.clientY-4.5);
    const nx=e.clientX/innerWidth-.5,ny=e.clientY/innerHeight-.5;
    if(gl)gl.setLook(nx,ny);else{ry(nx*7);rx(-ny*6);}
    tx(-nx*10);ty(-ny*7);
  });
  landing.addEventListener('pointerleave',()=>{probe.style.opacity=0;if(gl)gl.setLook(0,0);else{ry(0);rx(0);}tx(0);ty(0);});
  chars.forEach(ch=>{ch.addEventListener('pointerenter',()=>G.to(ch,{y:-7,duration:.25,ease:'power2.out',overwrite:'auto'}));
    ch.addEventListener('pointerleave',()=>G.to(ch,{y:0,duration:.35,ease:'power3.out',overwrite:'auto'}));});
  const cx=G.quickTo(enterBtn,'x',{duration:.3,ease:'power3.out'});
  const cy=G.quickTo(enterBtn,'y',{duration:.3,ease:'power3.out'});
  enterBtn.addEventListener('pointermove',e=>{const r=enterBtn.getBoundingClientRect();
    cx((e.clientX-r.left-r.width/2)*.22);cy((e.clientY-r.top-r.height/2)*.28);
    G.to('.ld-cta-ring',{opacity:1,scale:1.12,duration:.3,overwrite:'auto'});});
  enterBtn.addEventListener('pointerleave',()=>{cx(0);cy(0);G.to('.ld-cta-ring',{opacity:0,scale:1,duration:.3,overwrite:'auto'});});
}

let busy=false;
function enterApp(ev){
  if(busy||landing.hidden)return;busy=true;
  const r=enterBtn.getBoundingClientRect();
  const x=ev&&ev.clientX?ev.clientX:r.left+r.width/2,y=ev&&ev.clientY?ev.clientY:r.top+r.height/2;
  const R=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y))+60;
  const finish=()=>{
    landing.hidden=true;document.body.classList.remove('landing-on');setAppHidden(false);
    probe.style.opacity=0;window.scrollTo(0,0);
    if(window.__appIntro)window.__appIntro();
    const t=document.querySelector('.tab.on');if(t)t.focus({preventScroll:true});
    busy=false;
  };
  if(eggOn)eggOff(false);
  if(!G||RM2.matches){finish();return;}
  iris.style.display='block';iris.style.opacity=1;
  G.timeline({onComplete:()=>{iris.style.display='none';G.set(iris,{clearProps:'opacity,clipPath'});}})
    .to('.ld-main > *, .ld-stage, .ld-marquee',{opacity:0,y:-12,duration:.32,stagger:.04,ease:'power2.in'},0)
    .fromTo(iris,{clipPath:'circle(0px at '+x+'px '+y+'px)'},{clipPath:'circle('+R+'px at '+x+'px '+y+'px)',duration:.85,ease:'power3.inOut',onComplete:finish},.18)
    .to(iris,{opacity:0,duration:.5,ease:'power2.out'});
}
enterBtn.addEventListener('click',enterApp);
document.addEventListener('keydown',e=>{
  if(!landing.hidden&&!eggDialog.open&&e.key==='Enter'&&!e.target.closest('button,input,textarea,select,[contenteditable="true"]')){e.preventDefault();enterApp();}
});

function showLanding(){
  if(!landing.hidden)return;
  landing.hidden=false;landing.scrollTop=0;document.body.classList.add('landing-on');setAppHidden(true);window.scrollTo(0,0);
  if(eggOn)eggOff(false);
  if(G){G.set(['.ld-main','.ld-stage','.ld-marquee'],{opacity:1,y:0});G.set(enterBtn,{x:0,y:0});
    const ring=document.querySelector('.ld-cta-ring');if(ring)G.set(ring,{opacity:0,scale:1});}
  landingIn();
  enterBtn.focus({preventScroll:true});
}
home.addEventListener('click',showLanding);

const hit=$('ldhit'),eggDialog=$('eggdialog'),eggUnlock=$('eggunlock');
const eggPhases=[
  {title:'先让时间停下来。',body:'暂停的是这次演练中的执行过程。真正采样时，调试器短暂停核，给分散在内存里的信息拍一张尽量一致的快照。',state:'CORE / HALTED',caption:'HALT / 把时间停在这一拍',hint:'下一步将掀开模型外壳。真实 SWD 不需要拆开芯片。',symbol:'HALT → 一次观察窗口',detail:'暂停也会影响目标的运行。因此真实采样要记录暂停时长，并在读取结束后恢复目标。',next:'掀开芯片 · 下一步'},
  {title:'先核身份，再读状态。',body:'外壳下是用于讲解的概念电路。选择下面的检查对象，看看“一个真实读数”需要哪些证据；这里不会生成假数据。',state:'SWD / INSPECTION',caption:'READ / 选择一个检查对象',hint:'高亮仅标记概念功能区，不代表真实硅片布局或 SWD 走线。',next:'合上芯片 · 恢复执行'},
  {title:'让程序继续往前走。',body:'外壳重新合拢，观察窗口结束。真实采样器应恢复原先运行的目标，而不是让程序永远停在调试器里。',state:'CORE / RESUME',caption:'RESUME / 观察结束，恢复运行',hint:'你看到的是一拍，不是连续录像；两拍之间发生了什么，不能靠动画补出来。',symbol:'SNAPSHOT ≠ CONTINUOUS TRACE',detail:'只有身份已核验的真实快照，才能解释任务、tick 与引脚状态。进入工作台后，每个读数仍然需要来源。',next:'再拆一次 · 重新体验'}
];
const eggTargets=[
  ['FLASH ↔ BUILD','先比对板上 Flash 与构建产物。身份不匹配就停止解释 RTOS 对象，不能拿另一份符号表“猜”这块板。'],
  ['pxCurrentTCB','沿当前任务指针找到任务控制块，再结合这一份固件的结构偏移解释名字与优先级。没有内存快照，就不能知道选中了谁。'],
  ['xTickCount','节拍计数必须从板上读取。动画的进度不是 tick，也不能用两次采样之间的时间猜测任务切换。'],
  ['GPIO → ODR','寄存器定义来自 SVD，输出位来自实测。源码只负责确认引脚映射，高电平也不必然等于灯亮。']
];
let eggOn=false,eggStep=0,returnFocus=null,clicks=[],clickTimer=null,kbBuf='',lastKey=0;
function resetEggClicks(){clearTimeout(clickTimer);clickTimer=null;clicks=[];eggUnlock.firstChild.nodeValue='芯片里藏了一个实验 ';}
function chooseEggTarget(index){
  document.querySelectorAll('[data-egg-target]').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.eggTarget===index)));
  $('eggsymbol').textContent=eggTargets[index][0];$('eggdetail').textContent=eggTargets[index][1];
  if(gl)gl.setInspectionTarget(index);
}
function setEggStep(index){
  if(!eggOn)return;eggStep=index;const phase=eggPhases[index];eggDialog.dataset.step=String(index);
  document.querySelectorAll('[data-egg-step]').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.eggStep===index)));
  $('eggheading').textContent=phase.title;$('eggbody').textContent=phase.body;$('eggvisualstate').textContent=phase.state;
  $('eggcaptiontitle').textContent=phase.caption;$('eggcaption').textContent=phase.hint;$('eggnext').textContent=phase.next;
  $('eggtargets').hidden=index!==1;
  if(gl)gl.setInspectionStep(index);
  if(index===1)chooseEggTarget(0);else{$('eggsymbol').textContent=phase.symbol;$('eggdetail').textContent=phase.detail;}
}
function eggOff(restoreFocus=true){
  if(!eggOn)return;eggOn=false;resetEggClicks();kbBuf='';
  if(G){G.killTweensOf(eggDialog);G.set(eggDialog,{clearProps:'opacity,transform'});}
  if(gl)gl.endInspection();
  ambient.forEach(t=>t.resume());if(marqTween)marqTween.resume();
  if(eggDialog.open)eggDialog.close();
  if(restoreFocus&&!landing.hidden){const target=returnFocus&&returnFocus.isConnected&&returnFocus!==document.body?returnFocus:eggUnlock;target.focus({preventScroll:true});}
  returnFocus=null;
}
function eggPlay(){
  if(eggOn||landing.hidden||busy)return;
  returnFocus=document.activeElement;eggOn=true;resetEggClicks();kbBuf='';
  eggDialog.showModal();eggDialog.scrollTop=0;eggDialog.classList.toggle('has-webgl',!!gl);
  ambient.forEach(t=>t.pause());if(marqTween)marqTween.pause();probe.style.opacity=0;
  if(gl)gl.beginInspection($('eggviewport'));setEggStep(0);
  if(G&&!RM2.matches)G.fromTo(eggDialog,{opacity:0,y:12},{opacity:1,y:0,duration:.35,ease:'power3.out',clearProps:'opacity,transform'});
}
function registerEggClick(){
  if(eggOn||landing.hidden)return;
  const now=performance.now();clicks=clicks.filter(t=>now-t<1500);clicks.push(now);clearTimeout(clickTimer);
  if(clicks.length>=3){eggPlay();return;}
  eggUnlock.firstChild.nodeValue='再点芯片 '+(3-clicks.length)+' 次，进入实验 ';
  clickTimer=setTimeout(resetEggClicks,1500);
}
if(hit)hit.addEventListener('click',registerEggClick);
eggUnlock.addEventListener('click',eggPlay);
$('eggclose').addEventListener('click',()=>eggOff());
eggDialog.addEventListener('cancel',e=>{e.preventDefault();eggOff();});
eggDialog.addEventListener('close',()=>{if(!eggDialog.open)eggOff();});
$('eggnext').addEventListener('click',()=>setEggStep((eggStep+1)%3));
document.querySelectorAll('[data-egg-step]').forEach(b=>b.addEventListener('click',()=>setEggStep(+b.dataset.eggStep)));
document.querySelectorAll('[data-egg-target]').forEach(b=>b.addEventListener('click',()=>chooseEggTarget(+b.dataset.eggTarget)));
$('eggworkspace').addEventListener('click',()=>{eggOff(false);document.querySelector('.tab[data-v="sched"]').click();enterApp();});
document.addEventListener('keydown',e=>{
  if(landing.hidden||eggDialog.open||e.metaKey||e.ctrlKey||e.altKey||e.repeat||e.isComposing||e.target.isContentEditable||e.target.closest('input,textarea,select'))return;
  if(e.key&&e.key.length===1){const now=performance.now();kbBuf=now-lastKey>1500?'':kbBuf;lastKey=now;kbBuf=(kbBuf+e.key.toLowerCase()).slice(-3);
    if(kbBuf==='swd')eggPlay();}
});

const deep=TABS.some(([v])=>location.hash==='#'+v);
if(deep){landing.hidden=true;document.body.classList.remove('landing-on');setAppHidden(false);if(window.__appIntro)window.__appIntro();}
else{setAppHidden(true);landingIn();}
})();

/* ================= 浏览器导入向导（权威定义 + 工程事实；实测/偏移诚实标不可知） ================= */
(function(){
const INITIAL=JSON.parse(JSON.stringify(LENS));
const CONCEPTS=INITIAL.concepts, HONESTY=INITIAL.honesty;
const IMP={files:{},svdDoc:null,svdName:'',peripherals:[]};
const REQUIRED_RTOS=["pxCurrentTCB","pxReadyTasksLists","pxDelayedTaskList","pxOverflowDelayedTaskList","xDelayedTaskList1","xDelayedTaskList2","xTickCount","xNextTaskUnblockTime","xSchedulerRunning"];
const status=(msg,cls)=>{const s=$('impstatus');s.textContent=msg;s.className=cls||'';};
const pnum=(s,d)=>{s=String(s==null?'':s).trim().replace(/^#/,'');if(/^0x[0-9a-f]+$/i.test(s))return parseInt(s,16);if(/^\d+$/.test(s))return parseInt(s,10);return d;};
const hx=n=>'0x'+(n>>>0).toString(16);
const authoritative=(v,file,version,line)=>({state:'authoritative',value:v,prov:{file,version:version==null?null:version,line:line==null?null:line}});
const derived=(v,formula,inputs)=>({state:'derived',value:v,prov:{formula,inputs}});
const unknown=reason=>({state:'unknown',value:null,prov:{reason}});
async function sha256(bytes){try{const d=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(d)].map(b=>b.toString(16).padStart(2,'0')).join('');}catch(e){return '';}}

/* ---- map（Keil armlink / GNU ld）---- */
function parseMap(text){
  const lines=text.split(/\r?\n/);
  if(text.includes('ARM Linker')||text.includes('Image Symbol Table')){
    const symRe=/^\s{4}(\S+)\s+0x([0-9a-fA-F]{8})\s+(Data|Number|Section|Thumb Code|ARM Code)\s+(\d+)\s+(\S.*)$/;
    const symbols={};
    for(const ln of lines){const m=symRe.exec(ln);if(!m)continue;const[,name,addr,kind,size,obj]=m;
      if((kind==='Data'||kind==='Number')&&!name.startsWith('[Anonymous')&&!(name in symbols))
        symbols[name]={addr:'0x'+addr.toLowerCase(),size:+size,kind,object:obj.trim()};}
    const removed=new Set();let inR=false;
    for(const ln of lines){
      if(ln.includes('Removing Unused input sections')||ln.includes('Discarded input sections')){inR=true;continue;}
      if(inR){const m=/^\s+(\S+\.o\(\S+\))/.exec(ln);
        if(m)removed.add(m[1]);else if(ln.trim()&&!ln.startsWith(' '))inR=false;}}
    return{format:'keil',symbols,removed_sections:[...removed].sort()};
  }
  const symbols={};let cur=null;
  for(const ln of lines){
    const sm=/^(\.\w[\w.]*)\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)/.exec(ln);if(sm)cur=sm[1];
    const m=/^\s+0x([0-9a-fA-F]{8,16})\s+(\S+)/.exec(ln);
    if(m&&(cur==='.bss'||cur==='.data'||cur==='.noinit')&&!m[2].startsWith('.')&&!(m[2] in symbols))
      symbols[m[2]]={addr:'0x'+m[1].toLowerCase(),size:null,kind:'Data',object:cur};}
  return{format:'gnu',symbols,removed_sections:[]};
}
const detectRTOS=s=>['pxCurrentTCB','xTickCount','pxReadyTasksLists'].every(k=>k in s)?'FreeRTOS':null;
function checkLinked(symbols,removed){
  const missing=REQUIRED_RTOS.filter(s=>!(s in symbols));
  if(missing.length)return{linked:false,reason:'符号缺失: '+missing.join(', ')+' —— 该固件可能未链接 RTOS 内核'};
  const disc=REQUIRED_RTOS.filter(s=>s in symbols&&removed.includes(symbols[s].object));
  if(disc.length)return{linked:false,reason:'符号落入被丢弃的输入段: '+disc.join(', ')+' —— 该固件未链接 RTOS 内核'};
  return{linked:true,reason:null};
}

/* ---- CMSIS-SVD（DOMParser，厂商无关）---- */
const kids=(el,tag)=>el?[...el.children].filter(c=>c.tagName===tag):[];
const txt=(el,tag,d)=>{const c=kids(el,tag)[0];return c&&c.textContent?c.textContent.trim():(d==null?'':d);};
function svdPeripherals(doc){const root=doc.documentElement;const ps=kids(kids(root,'peripherals')[0],'peripheral');
  return ps.map(p=>({name:txt(p,'name'),base:txt(p,'baseAddress'),derivedFrom:p.getAttribute('derivedFrom'),description:txt(p,'description'),el:p}));}
function resolvePeriph(peripherals,name,seen){
  seen=seen||new Set();if(seen.has(name))throw new Error('derivedFrom 循环: '+name);seen.add(name);
  const p=peripherals.find(x=>x.name===name);if(!p)throw new Error('SVD 无外设 '+name);
  const regs={};const df=p.el.getAttribute('derivedFrom');
  if(df)Object.assign(regs,resolvePeriph(peripherals,df,seen).registers);
  const regEl=kids(p.el,'registers')[0];
  const mkFields=r=>kids(kids(r,'fields')[0],'field').map(f=>({name:txt(f,'name'),bit_offset:pnum(txt(f,'bitOffset','0'),0),bit_width:pnum(txt(f,'bitWidth','1'),1),description:txt(f,'description'),access:txt(f,'access',txt(r,'access',''))}));
  for(const r of kids(regEl,'register')){const rn=txt(r,'name');
    regs[rn]={name:rn,offset:pnum(txt(r,'addressOffset','0'),0),size_bits:pnum(txt(r,'size','32'),32),description:txt(r,'description'),fields:mkFields(r),defined_in:name};}
  for(const cl of kids(regEl,'cluster')){const cn=txt(cl,'name'),coff=pnum(txt(cl,'addressOffset','0'),0);
    for(const r of kids(cl,'register')){const rn=cn+'.'+txt(r,'name');
      regs[rn]={name:rn,offset:coff+pnum(txt(r,'addressOffset','0'),0),size_bits:pnum(txt(r,'size','32'),32),description:txt(r,'description'),fields:mkFields(r),defined_in:name,cluster:cn};}}
  return{name,base:pnum(txt(p.el,'baseAddress','0'),0),registers:regs};
}
function parseRegister(doc,peripherals,perName,regName,svdFile){
  const per=resolvePeriph(peripherals,perName);const reg=per.registers[regName];
  if(!reg)throw new Error(perName+' 无寄存器 '+regName);
  const root=doc.documentElement;const df=peripherals.find(x=>x.name===perName).derivedFrom;
  return{svd:{file:svdFile,version:txt(root,'version','?')},
    peripheral:{name:perName,base_address:hx(per.base),derivedFrom:df},
    register:{name:regName,address:hx(per.base+reg.offset),offset:reg.offset,size_bits:reg.size_bits,description:reg.description,defined_in:reg.defined_in,fields:reg.fields.slice().sort((a,b)=>a.bit_offset-b.bit_offset)}};
}

/* ---- 设备头 GPIO_TypeDef + 基址宏 ---- */
function parseHeader(text,file){
  const m=/typedef struct\s*\{([^{}]*)\}\s*GPIO_TypeDef;/s.exec(text);const fields=[];let off=0;
  if(m)for(const ln of m[1].split(/\r?\n/)){const fm=/__IO\s+uint(\d+)_t\s+(\w+)\s*(\[(\d+)\])?\s*;/.exec(ln);
    if(fm){const sz=Math.floor(+fm[1]/8)*(fm[4]?+fm[4]:1);fields.push({name:fm[2],offset:off,size:sz});off+=sz;}}
  const macros={};let bm;const re=/#define\s+(\w+)\s+([^\n]+)/g;
  while((bm=re.exec(text)))macros[bm[1]]=bm[2].replace(/\/\*.*?\*\//g,'').split('//')[0].trim();
  function resolve(name,seen){seen=seen||new Set();if(seen.has(name)||!(name in macros))return null;seen.add(name);let total=0;
    for(let tok of macros[name].split('+')){tok=tok.trim().replace(/^[()]+|[()]+$/g,'').trim().replace(/[UL]+$/,'');
      if(/^0x[0-9a-f]+$/i.test(tok))total+=parseInt(tok,16);
      else if(/^\d+$/.test(tok))total+=+tok;
      else if(tok in macros){const r=resolve(tok,seen);if(r==null)return null;total+=r;}
      else return null;}
    return total;}
  const bases={};for(const name in macros)if(/^GPIO[A-Z]_BASE$/.test(name)){const v=resolve(name);if(v!=null)bases[name]=hx(v);}
  return{header:{file},GPIO_TypeDef:{fields,size:off},gpio_bases:bases};
}

/* ---- 工程事实（config / 任务 / 延时 / GPIO 写 / 引脚）---- */
function configInt(s){const bare=s.trim().replace(/[uUlL]+$/,'');const v=pnum(bare,null);if(v!=null)return v;
  const cm=/^\(\s*(?:\(\s*[\w\s]+?\s*\)\s*)?(\d+[uUlL]*)\s*\)$/.exec(s.trim());
  return cm?pnum(cm[1].replace(/[uUlL]+$/,''),null):null;}
function extractFacts(mainc,mainh,cfg,nc,nh,nf){
  const config={};
  if(cfg)cfg.split(/\r?\n/).forEach((ln,idx)=>{const m=/^\s*#define\s+(config\w+)\s+(.+?)\s*$/.exec(ln);
    if(m&&!ln.trim().startsWith('*')){const clean=m[2].replace(/\/\*.*?\*\//g,'').split('//')[0].trim();const v=configInt(clean);
      if(v!=null)config[m[1]]={value:v,file:nf,line:idx+1};}});
  const tasks=[],delays=[],writes=[];let cur=null;
  if(mainc)mainc.split(/\r?\n/).forEach((ln,idx)=>{
    const fm=/^void\s+(\w+)\s*\(\s*void\s*\*/.exec(ln);if(fm)cur=fm[1];
    const tm=/xTaskCreate(?:Static)?\(\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\w+)\s*,\s*(\d+)/.exec(ln);
    if(tm)tasks.push({name:tm[2],entry:tm[1],stack_words:+tm[3],priority:+tm[5],file:nc,line:idx+1});
    const dm=/vTaskDelay(?:Until)?\(\s*(\d+)\s*\)/.exec(ln);
    if(dm)delays.push({ticks:+dm[1],file:nc,line:idx+1,in_fn:cur});
    const wm=/HAL_GPIO_WritePin\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\)/.exec(ln);
    if(wm)writes.push({port_macro:wm[1],pin_macro:wm[2],state:wm[3],file:nc,line:idx+1,in_fn:cur});});
  const pins={};
  if(mainh)mainh.split(/\r?\n/).forEach((ln,idx)=>{const m=/^#define\s+(\w+)_(Pin|GPIO_Port)\s+(\S+)/.exec(ln);
    if(m){(pins[m[1]]=pins[m[1]]||{file:nh})[m[2]]={macro:m[3],line:idx+1};}});
  for(const p of Object.values(pins)){if(p.Pin){const pm=/GPIO_PIN_(\d+)/.exec(p.Pin.macro);p.bit=pm?+pm[1]:null;}
    if(p.GPIO_Port)p.port=p.GPIO_Port.macro;p.confirmed_from_source=!!p.Pin&&!!p.GPIO_Port;}
  return{config,tasks,delay_calls:delays,gpio_writes:writes,pins,kernel:null};
}

/* ---- ELF Flash 加载镜像（ArrayBuffer）---- */
function elfFlash(buf,flashBase,flashSize){
  const data=new Uint8Array(buf),dv=new DataView(buf);
  if(data[0]!==0x7f||data[1]!==0x45||data[2]!==0x4c||data[3]!==0x46)throw new Error('不是 ELF 文件');
  if(data[4]!==1||data[5]!==1)throw new Error('仅支持 32 位小端 ELF (Cortex-M)');
  const phoff=dv.getUint32(28,true),phentsize=dv.getUint16(42,true),phnum=dv.getUint16(44,true);
  const segs=[];
  for(let i=0;i<phnum;i++){const o=phoff+i*phentsize;
    const type=dv.getUint32(o,true),off=dv.getUint32(o+4,true),paddr=dv.getUint32(o+12,true),filesz=dv.getUint32(o+16,true);
    if(type===1&&filesz>0&&paddr>=flashBase&&paddr<flashBase+flashSize)segs.push({paddr,bytes:data.slice(off,off+filesz)});}
  if(!segs.length)throw new Error('无 Flash 加载段（flash_base='+hx(flashBase)+'）');
  segs.sort((a,b)=>a.paddr-b.paddr);const base=segs[0].paddr;const end=Math.max(...segs.map(s=>s.paddr+s.bytes.length));
  const img=new Uint8Array(end-base);for(const s of segs)img.set(s.bytes,s.paddr-base);
  return{base,img};
}

/* ---- 术语卡（通用生成，不写死任务名）---- */
function buildTerms(facts){
  const terms=[];const cfg=facts.config.configTICK_RATE_HZ;const tick=cfg?cfg.value:null;
  for(const d of facts.delay_calls){if(!Number.isFinite(tick)||tick<=0)continue;const sec=d.ticks/tick;const secStr=String(+sec.toFixed(6));
    terms.push({kind:'delay',title:'vTaskDelay('+d.ticks+')',source:{file:d.file,line:d.line,fn:d.in_fn},
      passed:authoritative(d.ticks,d.file,null,d.line),decider:authoritative(tick,cfg.file,null,cfg.line),
      derived:derived(Math.round(sec*1e4)/1e4,d.ticks+' tick ÷ '+tick+' Hz ≈ '+secStr+' s',{ticks:d.ticks,hz:tick}),
      visible:'延时链表中的实测到期 tick（采样后可见）',links:{config:'configTICK_RATE_HZ',graph:'delayed'}});}
  const groups=new Map();
  for(const w of facts.gpio_writes){const k=JSON.stringify([w.in_fn,w.port_macro,w.pin_macro]);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(w);}
  for(const ws of groups.values()){if(ws.length<2)continue;const states=[...new Set(ws.map(w=>w.state))];
    terms.push({kind:'gpio_dual',title:(ws[0].in_fn||'未识别函数')+': '+ws.length+' 处已识别写入 · '+states.join(' / '),
      writes:ws.map(w=>({file:w.file,line:w.line,in_fn:w.in_fn,port_macro:w.port_macro,state:w.state,pin_macro:w.pin_macro})),
      note:'调用存在不等于实际执行；其他任务、中断、Toggle/直接寄存器写和硬件接法未覆盖，不能证明电平恒定或周期闪烁。',links:{graph:'register'}});}
  return terms;
}

/* ---- 文件输入绑定 ---- */
function bindFile(id,key,after){const inp=$(id),chip=$('c_'+key),pick=inp.closest('.imp-pick');
  const setPick=on=>{if(!pick)return;pick.classList.toggle('done',on);const s=pick.querySelector('span');if(s)s.textContent=on?'重新选择':'选择文件';};
  inp.addEventListener('change',async()=>{const f=inp.files[0];
    if(!f){delete IMP.files[key];chip.hidden=true;setPick(false);return;}
    IMP.files[key]=f;chip.textContent=f.name+' · '+(f.size/1024).toFixed(1)+' KB';chip.hidden=false;setPick(true);
    if(after)try{await after(f);}catch(e){status('读取 '+f.name+' 失败：'+e.message,'err');}});}
bindFile('f_map','map');bindFile('f_axf','axf');bindFile('f_hdr','hdr');
bindFile('f_mainc','mainc');bindFile('f_mainh','mainh');bindFile('f_cfg','cfg');bindFile('f_off','off');
bindFile('f_svd','svd',async f=>{
  const doc=new DOMParser().parseFromString(await f.text(),'application/xml');
  if(doc.getElementsByTagName('parsererror').length)throw new Error('SVD XML 解析失败');
  IMP.svdDoc=doc;IMP.svdName=f.name;IMP.peripherals=svdPeripherals(doc);
  const sel=$('sel_per');sel.innerHTML=IMP.peripherals.map(p=>'<option value="'+p.name+'">'+p.name+'</option>').join('');
  const def=IMP.peripherals.find(p=>p.name==='GPIOC')||IMP.peripherals[0];
  if(def){sel.value=def.name;fillRegs(def.name);}
  status('芯片说明书已载入（'+IMP.peripherals.length+' 个外设），已自动选好 '+sel.value+' 的输出寄存器。要换别的外设/寄存器，展开下面「更多选项」。','ok');
});
function fillRegs(perName){const sel=$('sel_reg');
  try{const per=resolvePeriph(IMP.peripherals,perName);const names=Object.keys(per.registers).sort();
    sel.innerHTML=names.map(n=>'<option value="'+n+'">'+n+'</option>').join('');
    if(names.includes('ODR'))sel.value='ODR';}
  catch(e){sel.innerHTML='<option value="">解析失败</option>';status(e.message,'err');}}
$('sel_per').addEventListener('change',e=>fillRegs(e.target.value));

/* ---- 解析并渲染 ---- */
$('impgo').addEventListener('click',async()=>{
  try{
    const F=IMP.files;
    if(!F.map)throw new Error('请先选第 1 个文件：地址清单（.map）');
    if(!F.svd||!IMP.svdDoc)throw new Error('请先选第 2 个文件：芯片说明书（.svd）');
    if(!F.mainc)throw new Error('请先选第 3 个文件：你的主程序（main.c）');
    const perName=$('sel_per').value,regName=$('sel_reg').value;
    if(!perName||!regName)throw new Error('请在「更多选项」里选好外设与寄存器');
    status('正在读懂你的工程…','');
    const mapText=await F.map.text();
    const mp=parseMap(mapText);const rtos=detectRTOS(mp.symbols);
    if(!rtos)throw new Error('未检测到受支持的 RTOS 内核符号（MVP 仅 FreeRTOS 适配器）。其余 RTOS 见「平台对照」概念卡。');
    for(const[key,pat]of[['static_idle_tcb','xIdleTaskTCB'],['static_idle_stack','uxIdleTaskStack']]){
      const hit=Object.keys(mp.symbols).find(n=>n.includes(pat));
      if(hit)mp.symbols[key]=Object.assign({},mp.symbols[hit],{alias_of:hit});}
    const lk=checkLinked(mp.symbols,mp.removed_sections);
    const mapSha=await sha256(new TextEncoder().encode(mapText));
    const reg=parseRegister(IMP.svdDoc,IMP.peripherals,perName,regName,IMP.svdName);
    let hdr={header:{file:'未提供设备头'},GPIO_TypeDef:{fields:[],size:0},gpio_bases:{}};
    if(F.hdr)hdr=parseHeader(await F.hdr.text(),F.hdr.name);
    const odrHdr=hdr.GPIO_TypeDef.fields.find(f=>f.name===regName);
    const baseMacro=perName+'_BASE';
    const agree=(parseInt(reg.peripheral.base_address,16)===parseInt(hdr.gpio_bases[baseMacro]||'0',16))&&!!odrHdr&&reg.register.offset===odrHdr.offset;
    const structure=Object.assign({},reg,hdr,{cross_check:{svd_header_agree:agree}});
    const facts=extractFacts(F.mainc?await F.mainc.text():'',F.mainh?await F.mainh.text():'',F.cfg?await F.cfg.text():'',
      F.mainc?F.mainc.name:'main.c',F.mainh?F.mainh.name:'main.h',F.cfg?F.cfg.name:'FreeRTOSConfig.h');
    let axfSha='',flashImage=null;
    if(F.axf){const buf=await F.axf.arrayBuffer();axfSha=await sha256(buf);
      const fb=pnum($('p_flash').value,0x08000000);
      try{const fl=elfFlash(buf,fb,0x40000);flashImage={base:hx(fl.base),size:fl.img.length,sha256:await sha256(fl.img)};}
      catch(e){flashImage={error:e.message};}}
    let offsets={source:{method:'未提供（需 CLI gdb 核定 DWARF，或导入 offsets.json）'},types:{},cross_check:{},provided:false};
    if(F.off){try{offsets=JSON.parse(await F.off.text());offsets.provided=true;}catch(e){throw new Error('offsets.json 解析失败：'+e.message);}}
    const payload={
      meta:{tool:'EmbeddedLens',version:'0.1.0-mvp',example:'browser-import'},
      device:{name:$('p_device').value||'未知型号',core:$('p_core').value||'Cortex-M',svd:structure.svd,flash_base:$('p_flash').value,ram_base:$('p_ram').value},
      build:{rtos,rtos_linked:lk.linked,axf_sha:axfSha,map_sha:mapSha,kernel:facts.kernel},
      identity:{status:'no-sample',reason:'尚未采集板上数据（浏览器导入仅含权威定义与工程事实，实测需 ST-LINK 采样）'},
      structure,facts,offsets,symbols:mp.symbols,snapshots:[],
      concepts:CONCEPTS,terms:buildTerms(facts),honesty:HONESTY,
      import_report:{map_format:mp.format,symbol_count:Object.keys(mp.symbols).length,removed_count:mp.removed_sections.length,
        rtos_linked_reason:lk.reason,axf_provided:!!F.axf,header_provided:!!F.hdr,offsets_provided:!!F.off,flash_image:flashImage}
    };
    LENS=payload;renderAll();
    $('impexphtml').disabled=false;$('impexpjson').disabled=false;
    const rep=payload.import_report;
    status('✓ 已读懂你的工程，下面每个页面都更新好了。\n'
      +'· 地址清单：认出 '+rep.symbol_count+' 个符号，'+rtos+(lk.linked?' 内核已链接':' 内核未链接')+'\n'
      +'· 寄存器：'+perName+'.'+regName+'，'+reg.register.fields.length+' 个位'+(agree?'（与设备头核对一致）':'（设备头没提供或对不上，需复核）')+'\n'
      +'· 你的代码：任务 '+facts.tasks.length+' 个 · 延时 '+facts.delay_calls.length+' 处 · 点灯 '+facts.gpio_writes.length+' 处 · 引脚 '+Object.keys(facts.pins).length+' 个\n'
      +'· 固件指纹：'+(rep.axf_provided?'已提取，可核对身份':'没给程序文件，身份暂时无法核对')+'\n'
      +'· 结构偏移：'+(rep.offsets_provided?'已导入':'不可知（要用命令行 gdb 核定）')+'\n'
      +'芯片此刻的真实状态：不可知（要接 ST-LINK 采样）。缺的地方都老实标注，没有编造任何数。点页面上带虚线的词可看大白话解释。','ok');
    $('impwrap').classList.remove('on');
  }catch(e){status('✗ '+e.message,'err');}
});

/* ---- 导出 / 恢复 ---- */
$('impexphtml').addEventListener('click',()=>{exportPage('embedded-lens-imported.html');status('已导出单文件 HTML（含当前工程与实验记录，双击离线打开）。','ok');});
$('impexpjson').addEventListener('click',()=>{download('payload.json',JSON.stringify(LENS,null,1),'application/json');status('已导出 payload.json。','ok');});
$('f_json').addEventListener('change',async e=>{const f=e.target.files[0];if(!f)return;
  try{const p=await studyReadFile(f);
    p.concepts=p.concepts||CONCEPTS;p.honesty=p.honesty||HONESTY;p.terms=buildTerms(p.facts);
    const previous=LENS;LENS=p;
    try{renderAll();}catch(err){LENS=previous;renderAll();throw err;}
    $('impexphtml').disabled=false;$('impexpjson').disabled=false;
    status('✓ 已载入 payload.json 并渲染。','ok');$('impwrap').classList.remove('on');
  }catch(err){status('✗ 导入 payload 失败：'+err.message,'err');}});
function resetFiles(){IMP.files={};IMP.svdDoc=null;IMP.peripherals=[];
  ['map','axf','svd','hdr','mainc','mainh','cfg','off'].forEach(k=>{const c=$('c_'+k);if(c)c.hidden=true;});
  ['f_map','f_axf','f_svd','f_hdr','f_mainc','f_mainh','f_cfg','f_off','f_json'].forEach(id=>{const i=$(id);if(i)i.value='';});
  document.querySelectorAll('#impwrap .imp-pick').forEach(p=>{p.classList.remove('done');const s=p.querySelector('span');if(s)s.textContent='选择文件';});
  $('sel_per').innerHTML='<option value="">先载入说明书…</option>';$('sel_reg').innerHTML='<option value="">先选外设…</option>';}
$('impreset').addEventListener('click',()=>{LENS=JSON.parse(JSON.stringify(INITIAL));renderAll();
  $('impexphtml').disabled=true;$('impexpjson').disabled=true;resetFiles();
  status('已切换到内置示例。','ok');$('impwrap').classList.remove('on');});

/* ---- 开合 ---- */
$('impopen').addEventListener('click',()=>{closeProv();hideGl();$('glwrap').classList.remove('on');$('impwrap').classList.add('on');});
$('impclose').addEventListener('click',()=>$('impwrap').classList.remove('on'));
$('impwrap').addEventListener('click',e=>{if(e.target===$('impwrap'))$('impwrap').classList.remove('on');});
document.addEventListener('keydown',e=>{if(e.key==='Escape')$('impwrap').classList.remove('on');});
})();

/* ---- 一键读取：本机 bridge。静态页不能直接访问 ST-LINK，桥接只读采样 ---- */
(function(){
const READ_URL='http://127.0.0.1:8765';
const LOCAL_ORIGIN=(location.hostname==='127.0.0.1'||location.hostname==='localhost')?location.origin:null;
const BRIDGE_CANDIDATES=[...new Set([LOCAL_ORIGIN,READ_URL].filter(Boolean))];
let BRIDGE=BRIDGE_CANDIDATES[0];
const COPY_CMD='python tools\\elens_bridge.py';
let health=null,busy=false;
function readStatus(msg,cls){const el=$('readstatus');if(!el)return;el.textContent=msg;el.className='read-status'+(cls?' '+cls:'');}
async function bridgeFetch(base,path,opts,ms){
  const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),ms||2500);
  try{
    const res=await fetch(base+path,{cache:'no-store',...opts,signal:ctrl.signal,headers:{'Content-Type':'application/json',...((opts&&opts.headers)||{})}});
    const data=await res.json().catch(()=>({}));
    if(!res.ok)throw new Error(data.error||('HTTP '+res.status));
    return data;
  }finally{clearTimeout(timer);}
}
async function bridgeConnect(){
  readStatus('正在连接本机桥接…','busy');
  let found=null;
  for(const base of BRIDGE_CANDIDATES){
    try{const h=await bridgeFetch(base,'/health',{},3000);if(h&&h.app==='EmbeddedLens bridge'){found={base,h};break;}}catch(e){}
  }
  if(!found){
    health=null;$('readgo').disabled=true;$('readcmd').classList.add('on');
    readStatus('未检测到本机桥接。'+(location.protocol==='https:'?'线上页面若被浏览器拦截，请点「打开本机页面」。':'')+'\n请在本机运行下面的启动命令，然后点「重试连接」。','err');
    return;
  }
  BRIDGE=found.base;health=found.h;
  const ready=(health.examples||[]).filter(x=>x.ready);
  const sel=$('read-example'),want=sel.value||(LENS.meta&&LENS.meta.example)||health.default;
  sel.innerHTML=ready.length?ready.map(x=>`<option value="${esc(x.name)}">${esc(x.name)}</option>`).join(''):'<option value="">没有可用工程</option>';
  if(ready.some(x=>x.name===want))sel.value=want;
  else if(health.default&&ready.some(x=>x.name===health.default))sel.value=health.default;
  const toolOk=!!(health.tools&&health.tools.openocd_exists),scriptOk=!!(health.tools&&health.tools.scripts_exists);
  $('readgo').disabled=busy||!ready.length||!toolOk||!scriptOk;
  $('readcmd').classList.remove('on');
  if(!toolOk||!scriptOk)readStatus('桥接已连接，但工具不完整：'+(toolOk?'':'OpenOCD 未找到。')+(scriptOk?'':'OpenOCD scripts 未找到。')+'请检查安装路径或启动参数。','err');
  else readStatus(`本机桥接已连接 · ${ready.length} 个工程就绪。\n探针连接状态将在读取时检测；读取只读，不写内存、不烧录。`,'ok');
}
function openRead(){
  closeProv();hideGl();$('glwrap').classList.remove('on');
  $('readwrap').classList.add('on');
  bridgeConnect();
  setTimeout(()=>$('read-example').focus({preventScroll:true}),60);
}
document.addEventListener('click',e=>{
  const op=e.target.closest('#readopen,[data-readopen]');
  if(op){e.preventDefault();openRead();return;}
  if(e.target.closest('#readclose')){$('readwrap').classList.remove('on');return;}
  if(e.target===$('readwrap'))$('readwrap').classList.remove('on');
});
document.addEventListener('keydown',e=>{if(e.key==='Escape')$('readwrap').classList.remove('on');});
$('readretry').addEventListener('click',bridgeConnect);
$('readcopy').addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(COPY_CMD);readStatus('启动命令已复制。','ok');}
  catch(e){readStatus('复制失败，请手动执行：\n'+COPY_CMD,'err');}
});
$('readgo').addEventListener('click',async()=>{
  if(busy)return;
  const example=$('read-example').value;
  if(!example){readStatus('请先选择工程，并确认本机桥接已连接。','err');return;}
  const frames=Math.max(1,Math.min(20,parseInt($('read-frames').value,10)||5));
  const interval=Math.max(0,Math.min(10,parseFloat($('read-interval').value)||0));
  busy=true;$('readgo').disabled=true;$('readretry').disabled=true;
  readStatus(`正在读取 ${example}：${frames} 帧，请求间隔 ${interval} s。\n目标会短暂停核并立即恢复；不写内存、不烧录、不复位。请勿拔线。`,'busy');
  try{
    const timeout=Math.min(300000,(frames*(interval+4)+20)*1000);
    const r=await bridgeFetch(BRIDGE,'/sample',{method:'POST',body:JSON.stringify({example,frames,interval})},timeout);
    if(r.payload)LENS=r.payload;
    else{
      const got=Array.isArray(r.snapshots)?r.snapshots:[],ids=new Set((LENS.snapshots||[]).map(s=>s.id));
      for(const s of got)if(!ids.has(s.id)){LENS.snapshots.push(s);ids.add(s.id);}
      const verified=[...LENS.snapshots].reverse().find(s=>s.identity&&s.identity.status==='verified');
      const mismatch=[...LENS.snapshots].reverse().find(s=>s.identity&&s.identity.status==='mismatch');
      LENS.identity=verified?verified.identity:(mismatch?mismatch.identity:{status:'no-sample',reason:'尚未采集板上数据'});
    }
    refreshSnaps();renderAll();
    if(r.ok){
      const sum=r.summary||{};
      readStatus(`读取完成：${sum.valid??0} 个有效帧 / ${sum.frames??0} 帧。\n页面已更新，正在打开调度快照。`+(sum.exported===false?'\n本机页面文件重建失败，可仍用页面内「导出网页」。':''),'ok');
      $('readwrap').classList.remove('on');
      document.querySelector('.tab[data-v="sched"]').click();
    }else{
      const d=(r.summary&&r.summary.diagnostic)||{};
      readStatus(`未产出有效帧${d.stage?`（${d.stage}/${d.code}）`:''}：${d.message||r.error||'请查看采样诊断。'}\n失败帧已记录，页面不会编造数据。`,'err');
    }
  }catch(e){
    readStatus('读取失败：'+e.message+'\n请确认本机桥接在运行、ST-LINK 已连接且未被 Keil 独占。','err');
  }finally{
    busy=false;$('readgo').disabled=false;$('readretry').disabled=false;
  }
});
})();
</script></body></html>"""

VENDOR = Path(__file__).resolve().parent / "vendor"

def render(payload):
    js = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    libs = "\n".join(
        "<script>" + (VENDOR / f).read_text(encoding="utf-8").replace("</script", "<\\/script") + "</script>"
        for f in ("gsap.min.js", "ScrollToPlugin.min.js", "DrawSVGPlugin.min.js", "three.min.js")
        if (VENDOR / f).exists())
    return TEMPLATE.replace("__GSAP_LIBS__", libs).replace("__LENS_JSON__", js)

def export(payload, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(payload), encoding="utf-8")
    return out_path