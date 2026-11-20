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
.wrap{max-width:1040px;margin:0 auto;padding:0 22px 80px;position:relative}
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
.masthead{display:grid;grid-template-columns:1fr auto;gap:26px;align-items:end;padding:34px 0 20px;border-bottom:2px solid var(--ink)}
.mark{width:44px;height:44px;color:var(--accent);margin-bottom:12px}
.mark svg{width:44px;height:44px;stroke:currentColor;fill:none;stroke-width:1.3;stroke-linecap:round}
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
h1{font-family:var(--serif);font-size:37px;font-weight:700;letter-spacing:-.015em;line-height:1.05;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
h1 .zh{font-family:var(--serif);font-size:16px;font-weight:400;color:var(--muted);letter-spacing:.06em}
.sub{color:var(--muted);font-size:13px;margin-top:9px;max-width:58ch}
.spec{font-family:var(--mono);font-size:11px;min-width:230px;border-left:1px solid var(--line);padding-left:20px}
.spec .row{display:flex;justify-content:space-between;gap:16px;padding:4px 0;border-bottom:1px dotted var(--line)}
.spec .row:last-child{border-bottom:none}
.spec .k{color:var(--faint);letter-spacing:.08em}
.spec .val{color:var(--ink);text-align:right}
.rule{height:1px;background:var(--ink);opacity:.28;margin:3px 0 22px}

/* badges */
.badges{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}
.tag{font-family:var(--mono);font-size:11px;border:1px solid var(--line);border-radius:var(--r);padding:4px 10px;background:var(--surface);color:var(--ink-2);display:inline-flex;align-items:center;gap:7px}
.tag::before{content:"";width:6px;height:6px;background:var(--faint);flex:0 0 auto}
.tag.ok{border-color:#bcd3ba;color:var(--ok);background:var(--ok-soft)} .tag.ok::before{background:var(--ok)}
.tag.warn{border-color:#e0cfa8;color:var(--warn);background:var(--warn-soft)} .tag.warn::before{background:var(--warn)}
.tag.bad{border-color:#e0bdb8;color:var(--bad);background:var(--bad-soft)} .tag.bad::before{background:var(--bad)}
.tag.acc{border-color:var(--accent-tint);color:var(--accent);background:var(--accent-soft)} .tag.acc::before{background:var(--accent)}

/* ruled sections */
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:24px;margin-bottom:18px;position:relative}
h2{font-family:var(--serif);font-size:20px;font-weight:700;margin-bottom:15px;padding-bottom:11px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:11px;letter-spacing:-.01em;flex-wrap:wrap}
h2 .n{font-family:var(--mono);font-size:10.5px;font-weight:600;background:transparent;color:var(--accent);border:1px solid var(--accent-tint);border-radius:var(--r);padding:3px 7px;letter-spacing:.05em}
.seal{width:26px;height:26px;border-radius:var(--r);display:inline-grid;place-items:center;flex:0 0 auto;border:1px solid var(--line)}
.seal svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.seal.ok{background:var(--ok-soft);color:var(--ok);border-color:#bcd3ba}
.seal.warn{background:var(--warn-soft);color:var(--warn);border-color:#e0cfa8}
.seal.bad{background:var(--bad-soft);color:var(--bad);border-color:#e0bdb8}
.fp{font-family:var(--mono);font-size:11px;background:var(--surface-2);border:1px solid var(--line-2);border-radius:var(--r);padding:3px 9px;color:var(--ink-2);display:inline-block;margin:3px 6px 0 0}

/* index nav */
.tabs{display:flex;gap:0;flex-wrap:wrap;margin-bottom:22px;position:sticky;top:0;z-index:30;background:var(--paper);border-bottom:1px solid var(--line);padding:0}
.tab{border:none;border-bottom:2px solid transparent;background:none;border-radius:0;padding:13px 20px 11px;cursor:pointer;font-size:13.5px;font-weight:600;color:var(--muted);display:inline-flex;align-items:center;gap:9px;transition:color .2s,border-color .2s;user-select:none}
.tab .num{font-family:var(--mono);font-size:10.5px;color:var(--faint);letter-spacing:.05em}
.tab:hover{color:var(--ink)}
.tab.on{color:var(--accent);border-bottom-color:transparent}
.tab.on .num{color:var(--accent)}
.tab-ink{position:absolute;left:0;top:0;height:2px;background:var(--accent);border-radius:2px 2px 0 0;pointer-events:none;will-change:transform,width}
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
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}

/* empty + notes */
.empty{border:1px dashed var(--line);border-radius:var(--r);padding:34px 26px;text-align:center;color:var(--muted);background:var(--surface-2)}
.empty b{color:var(--warn);font-size:15px;font-family:var(--serif)}
.snote{border:1px solid var(--line);border-left:3px solid var(--accent);background:var(--surface-2);border-radius:var(--r);padding:12px 15px;margin:11px 0;font-size:12.8px;color:var(--ink-2)}
.snote b{color:var(--accent)}

/* register map */
.bits{display:grid;grid-template-columns:repeat(8,1fr);gap:5px;margin:15px 0}
.bit{border:1px solid var(--line);border-radius:var(--r);padding:9px 4px 8px;text-align:center;font-family:var(--mono);font-size:11px;cursor:pointer;background:var(--surface);transition:all .18s var(--ease);position:relative}
.bit:hover{border-color:var(--accent);transform:translateY(-2px)}
.bit .bn{font-size:9px;color:var(--faint);display:block;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bit .bv{font-size:17px;font-weight:700;color:var(--faint);line-height:1}
.bit.hi{border-color:var(--accent-tint);background:var(--accent-soft)}
.bit.hi::after{content:"";position:absolute;top:4px;right:4px;width:5px;height:5px;background:var(--accent)}
.bit.set{border-color:var(--accent);background:var(--accent-soft)}
.bit.set .bv{color:var(--accent)}

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
.term-deep{padding:19px 20px}
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
#impwrap,#glwrap{position:fixed;inset:0;z-index:60;display:none;align-items:flex-start;justify-content:center;padding:38px 16px;background:rgba(27,30,33,.34);overflow-y:auto}
#impwrap.on,#glwrap.on{display:flex}
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
.imp-field input[type=text]:focus,.imp-field select:focus{outline:2px solid var(--accent);outline-offset:1px}
.imp-mini{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.imp-mini .imp-pick{padding:6px 11px;font-size:11.5px}
.imp-actions{display:flex;gap:9px;flex-wrap:wrap;align-items:center;margin-top:22px;padding-top:18px;border-top:1px solid var(--line)}
.btn.big{padding:11px 22px;font-size:14px}
#impstatus{font-size:12.8px;margin-top:14px;white-space:pre-wrap;word-break:break-word;color:var(--ink-2);line-height:1.7;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px}
#impstatus:empty{display:none}
#impstatus.err{color:var(--bad);border-color:#e0bdb8;background:var(--bad-soft)}
#impstatus.ok{border-left:3px solid var(--ok)}
/* glossary dictionary */
.gl-search{width:100%;font-family:var(--sans);font-size:13px;border:1px solid var(--line);border-radius:var(--r);padding:9px 12px;background:var(--surface-2);color:var(--ink);margin:14px 0 4px}
.gl-search:focus{outline:2px solid var(--accent);outline-offset:1px}
.gl-cat{font-family:var(--mono);font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--accent);margin:16px 0 6px;border-bottom:1px dotted var(--line);padding-bottom:5px}
.gl-item{padding:9px 0;border-bottom:1px solid var(--line-2)}
.gl-item:last-child{border-bottom:none}
.gl-item .t{font-family:var(--mono);font-size:12.5px;font-weight:700;color:var(--ink);display:block;margin-bottom:3px}
.gl-item .p{font-size:12.8px;color:var(--ink-2);line-height:1.6}
.gl-empty{color:var(--muted);font-size:13px;padding:20px 0;text-align:center}
.mast-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}
@media(max-width:760px){
.imp-grid{grid-template-columns:1fr}
.imppanel,.glpanel{padding:22px 18px}
.imp-row{flex-wrap:wrap}
.imp-rowfile{flex-direction:row;align-items:center;width:100%;min-width:0;margin-top:9px;padding-left:41px}
.imp-chip{max-width:46vw}
#glpop{max-width:calc(100vw - 24px)}
.wrap{padding:0 15px 60px}
.masthead{grid-template-columns:1fr;gap:16px;padding:24px 0 16px}
.spec{border-left:none;padding-left:0;border-top:1px solid var(--line);padding-top:12px;min-width:0}
h1{font-size:29px}
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
#ldgrid{position:absolute;inset:0;pointer-events:none;opacity:.5;background-image:linear-gradient(var(--line-2) 1px,transparent 1px),linear-gradient(90deg,var(--line-2) 1px,transparent 1px);background-size:56px 56px;-webkit-mask-image:radial-gradient(120% 100% at 62% 38%,#000 45%,transparent 100%);mask-image:radial-gradient(120% 100% at 62% 38%,#000 45%,transparent 100%)}
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
.ld-stage{grid-row:1;grid-column:2;position:relative;margin:8px 8px 8px 0;display:grid;place-items:center;perspective:900px}
#ldgl{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab;touch-action:none}
#ldgl:active{cursor:grabbing}
.ld-zoom{position:absolute;right:12px;bottom:44px;display:flex;gap:6px;z-index:3}
.ld-zoom button{font-family:var(--mono);font-size:11px;line-height:1;color:var(--muted);background:var(--surface);border:1px solid var(--line);border-radius:2px;min-width:24px;height:24px;padding:0 6px;cursor:pointer}
.ld-zoom button:hover{color:var(--accent);border-color:var(--accent)}
.ld-stage.gl-ok .ld-scope{display:none}
.ld-q{position:absolute;left:66%;top:22%;font-family:var(--mono);font-size:12px;color:var(--faint);display:none;pointer-events:none;animation:ldq 7s ease-in-out infinite}
.ld-stage.gl-ok .ld-q{display:block}
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
.ld-tag{position:absolute;display:inline-flex;align-items:center;gap:7px;font-family:var(--mono);font-size:8.5px;letter-spacing:.18em;color:var(--muted);padding:4px 8px;border:1px solid var(--line);border-radius:2px;background:rgba(250,248,242,.88);z-index:2}
.ld-tag i{width:4px;height:4px;border-radius:50%;background:var(--accent);flex:0 0 auto}
.ld-tag.t1{right:11%;top:15%}
.ld-tag.t2{left:9%;top:29%}
.ld-tag.t3{right:8%;bottom:27%}
.ld-tag.t4{left:11%;bottom:15%}
.ld-wave{position:absolute;left:30px;right:30px;bottom:48px;height:30px;width:auto;z-index:2;opacity:.42;pointer-events:none}
.ld-wave polyline{fill:none;stroke:var(--accent);stroke-width:1.1;stroke-dasharray:6 5;animation:ldwave 3.4s linear infinite}
@keyframes ldwave{to{stroke-dashoffset:-44}}
.ld-stage-foot{position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:space-between;gap:10px;padding:9px 14px;border-top:1px solid var(--line);font-family:var(--mono);font-size:8.5px;letter-spacing:.14em;color:var(--faint);z-index:2}
.ld-trace{position:absolute;left:50%;bottom:96px;transform:translateX(-50%);display:flex;align-items:center;gap:12px;padding:8px 13px 9px;border:1px solid var(--accent-tint);background:var(--surface);border-radius:2px;font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;color:var(--accent);opacity:0;pointer-events:none;z-index:3;overflow:hidden;box-shadow:0 6px 20px rgba(27,30,33,.1)}
.ld-trace i{width:23px;height:1px;background:var(--accent-tint)}
.ld-scanbar{position:absolute;left:0;bottom:0;height:2px;width:16%;background:var(--accent);opacity:.9}
.ld-eggtoast{position:absolute;left:50%;top:14px;transform:translateX(-50%);font-family:var(--mono);font-size:9px;letter-spacing:.12em;color:#fff;background:var(--accent);padding:5px 11px;border-radius:2px;opacity:0;pointer-events:none;z-index:4;white-space:nowrap}
.ld-stage.egg-on .ld-q{animation:none;opacity:.1}
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
#landing{grid-template-columns:1fr}
.ld-main{padding:clamp(22px,6vw,40px);max-width:none}
.ld-stage{position:absolute;right:-22%;bottom:2%;width:88vw;height:88vw;margin:0;opacity:.3;pointer-events:none;z-index:0}
.ld-tag,.ld-trace,.ld-eggtoast,.ld-wave,.ld-stage-foot,.ld-ruler,.ld-stage-tag,.ld-zoom{display:none}
.ld-sweep{display:none}
.ld-title{font-size:clamp(46px,13vw,72px)}
.ld-meta{gap:14px}
.ld-meta span{min-width:104px}
.ld-marquee{padding:10px 0}
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
  </div>
  <div class="ld-stage" id="ldstage" aria-hidden="true">
    <span class="ld-stage-tag tl">INSTRUMENT No.01</span>
    <span class="ld-stage-tag tr">FIELD UNIT · STANDBY</span>
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
    <span class="ld-tag t1"><i></i>TICK</span>
    <span class="ld-tag t2"><i></i>READY</span>
    <span class="ld-tag t3"><i></i>DELAYED</span>
    <span class="ld-tag t4"><i></i>ODR</span>
    <svg class="ld-wave" viewBox="0 0 420 48" preserveAspectRatio="none" aria-hidden="true"><polyline points="0,34 12,34 14,18 18,18 20,34 42,34 46,26 50,26 52,34 78,34 80,10 84,10 86,34 104,34 108,30 112,30 114,34 150,34 152,22 156,22 158,34 186,34 190,38 194,38 196,34 230,34 232,14 236,14 238,34 260,34 264,28 268,28 270,34 300,34 302,20 306,20 308,34 336,34 340,32 344,32 346,34 380,34 382,12 386,12 388,34 420,34"/></svg>
    <div class="ld-stage-foot"><span>SWD · 2-WIRE</span><span>DRAG ROTATE · WHEEL ZOOM</span><span>HALT → READ → RESUME</span></div>
    <div class="ld-trace" id="ldtrace"><span>HALT</span><i></i><span>READ</span><i></i><span>RESUME</span><div class="ld-scanbar" id="ldscan"></div></div>
    <div class="ld-eggtoast" id="ldeggtoast">彩蛋 · 停核采样演练（示意）</div>
  </div>
  <div class="ld-probe" id="ldprobe" aria-hidden="true"></div>
  <div class="ld-marquee" aria-hidden="true"><div class="ld-marq" id="ldmarq"><span>SWD · SNAPSHOT · TICK · READY · DELAYED · PROVENANCE · NO FABRICATION · </span><span>SWD · SNAPSHOT · TICK · READY · DELAYED · PROVENANCE · NO FABRICATION · </span></div></div>
</div>
<div id="ldiris" aria-hidden="true"></div>
<button id="ldhome" aria-label="返回介绍页"><svg class="ic" viewBox="0 0 24 24"><path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/></svg>介绍页</button>
<div class="wrap">
<header class="masthead">
  <div class="brand">
    <div class="mark" aria-hidden="true"><svg viewBox="0 0 44 44"><circle cx="22" cy="22" r="15"/><circle cx="22" cy="22" r="5.5"/><path d="M22 2v8M22 34v8M2 22h8M34 22h8"/><path d="M11.4 11.4l3 3M29.6 29.6l3 3M32.6 11.4l-3 3M14.4 29.6l-3 3"/></svg></div>
    <div class="kicker">Field Instrument · SWD Probe · Honest Provenance</div>
    <h1>EmbeddedLens <span class="zh">嵌入式透视镜</span></h1>
    <div class="sub">把芯片里真实运行的状态，画成初学者看得懂的图。不改你的固件、不加代码、不用串口——接上调试器读一拍即可。</div>
    <div class="mast-actions">
      <button class="btn" id="impopen"><svg class="ic" viewBox="0 0 24 24"><path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>导入我的工程</button>
      <button class="btn sec" id="glopen"><svg class="ic" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>名词小词典</button>
    </div>
  </div>
  <div class="spec" id="spec"></div>
</header>
<div class="rule"></div>
<div class="badges" id="topbadges"></div>
<div class="card" id="identitycard"></div>
<nav class="tabs" id="tabs" aria-label="视图切换"></nav>
<div class="view on" id="view-sched"></div>
<div class="view" id="view-reg"></div>
<div class="view" id="view-term"></div>
<div class="view" id="view-plat"></div>
<div class="view" id="view-replay"></div>
<div class="card"><div class="note" id="contract"></div>
<div class="note" style="margin:10px 0 8px">每个数字都标了「它从哪来」。点下面带虚线的词，看大白话解释：</div>
<div class="legend"><span><b class="v m">实测值<i class="bdg">实测</i></b> <span class="gl" data-gl="实测值" tabindex="0" role="button">真的从芯片读出来的数</span></span>
<span><b class="v a">权威定义<i class="bdg">权威</i></b> <span class="gl" data-gl="权威定义" tabindex="0" role="button">厂商说明书/编译信息的标准答案</span></span>
<span><b class="v d">推导值<i class="bdg">推导</i></b> <span class="gl" data-gl="推导值" tabindex="0" role="button">实测+定义算出来，附公式</span></span>
<span><b class="v u">不可知<i class="bdg">不可知</i></b> <span class="gl" data-gl="不可知" tabindex="0" role="button">证据不够，老实说不知道</span></span></div></div>
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
const IC={sched:'<path d="M3 12h4l3 8 4-16 3 8h4"/>',reg:'<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/>',term:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',plat:'<path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>',replay:'<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',prev:'<path d="M15 18l-6-6 6-6"/>',next:'<path d="M9 18l6-6-6-6"/>',reset:'<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',play:'<path d="M6 4l14 8-14 8V4z"/>',stop:'<rect x="6" y="6" width="12" height="12" rx="1.5"/>',check:'<path d="M20 6 9 17l-5-5"/>',alert:'<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',shield:'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4M12 16h.01"/>',arrow:'<path d="M5 12h14M13 6l6 6-6 6"/>'};
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
document.addEventListener('click',e=>{
  const t=e.target.closest('.v'); if(!t||!t.dataset.prov)return;
  const v=JSON.parse(t.dataset.prov); const st=STATE[v.state]||['?','u'];
  let h=`<div class="row"><b>态</b><span>${st[0]}值</span></div>`;
  for(const[k,val]of Object.entries(v.prov||{})) h+=`<div class="row"><b>${esc(k)}</b><span class="mono">${esc(typeof val==='object'?JSON.stringify(val):val)}</span></div>`;
  document.getElementById('provbody').innerHTML=h;
  openProv();
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
function refreshSnaps(){snaps=LENS.snapshots.filter(s=>s.status==='ok');validSnaps=snaps.filter(s=>s.valid&&s.decoded);}
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
  $('topbadges').innerHTML=
    `<span class="tag ${b.rtos_linked?'ok':'bad'}">${g('RTOS')} ${b.rtos_linked?'已链接':'未链接'}</span>`+
    `<span class="tag acc">${g('停核采样','停核离散采样')}</span>`+
    `<span class="tag">${g('离散快照','快照')} ${validSnaps.length} 有效 / ${LENS.snapshots.length} 采集</span>`;
  const id=LENS.identity;
  const cls=id.status==='verified'?'ok':(id.status==='mismatch'?'bad':'warn');
  const sealIc={verified:'check',mismatch:'alert',unverified:'shield','no-sample':'shield'}[id.status]||'shield';
  const txt={verified:'固件身份已核验',mismatch:'固件身份不匹配',unverified:'身份未核验','no-sample':'尚未采样'}[id.status]||id.status;
  $('identitycard').innerHTML=`<h2><span class="n">§6.3</span>${g('固件身份核验')} <span class="seal ${cls}">${ic(sealIc)}</span><span class="tag ${cls}">${txt}</span></h2>
    <div class="plain"><span class="ptag">大白话</span><span>确认「芯片里烧的程序」和「你这次编译的程序」是不是同一个。只有对得上，工具才敢解释内核状态；对不上就只给原始读数，避免张冠李戴。</span></div>
    <div class="note">${esc(id.reason||'')}${id.range?` · 比对范围 ${esc(id.range)}`:''}</div>
    <div style="margin-top:9px"><span class="fp">${g('AXF')} sha256 ${b.axf_sha?esc(b.axf_sha.slice(0,20))+'…':'未提供'}</span><span class="fp">${g('map 文件','map')} sha256 ${b.map_sha?esc(b.map_sha.slice(0,20))+'…':'未提供'}</span></div>
    ${id.status!=='verified'?'<div class="snote" style="margin-top:11px">身份未通过核验时，界面只展示原始读数与权威定义，停止解释 RTOS 对象。</div>':''}`;
  $('contract').textContent=LENS.honesty.contract;
}

/* ---- Tab 切换 ---- */
const TABS=[['sched','调度快照'],['reg','寄存器位段'],['term','术语溯源'],['plat','平台对照'],['replay','回放/导出']];
$('tabs').innerHTML=TABS.map((t,i)=>`<div class="tab${i===0?' on':''}" data-v="${t[0]}" role="tab" tabindex="0" aria-selected="${i===0}"><span class="num">0${i+1}</span><span>${t[1]}</span></div>`).join('');
function selTab(t){document.querySelectorAll('.tab').forEach(x=>{const on=x===t;x.classList.toggle('on',on);x.setAttribute('aria-selected',on);});
  const view=$('view-'+t.dataset.v);
  document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v===view));
  if(window.__onTabShown)window.__onTabShown(view,t);
  history.replaceState(null,'','#'+t.dataset.v);}
$('tabs').addEventListener('click',e=>{const t=e.target.closest('.tab');if(t)selTab(t);});
$('tabs').addEventListener('keydown',e=>{const t=e.target.closest('.tab');if(!t)return;
  if(e.key==='Enter'||e.key===' '){e.preventDefault();selTab(t);}
  else if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();const all=[...document.querySelectorAll('.tab')];const i=all.indexOf(t);const n=all[(i+(e.key==='ArrowRight'?1:all.length-1))%all.length];n.focus();selTab(n);}});

/* ---- V1 调度快照 ---- */
function taskBlock(e,cls){const t=e.tcb||{};return{k:(t.addr||e.item.addr),cls:cls,task:(t.name||''),l:`${t.name||'?'} p${t.priority??'?'}`,lt:`${t.name||'?'} · 到期 ${e.wake_tick??''}`};}
function renderSched(){
  const root=$('view-sched');
  if(!validSnaps.length){
    root.innerHTML=`<div class="card"><h2><span class="n">V1</span>调度快照</h2>
      <div class="empty"><b>未采集到身份已核验的板上数据</b><br><br>
      结构定义（SVD/DWARF）与工程事实（源码/配置）已就绪并可查看；<br>
      实测调度状态需连接 ST-LINK 运行 <span class="mono">elens sample</span>，或导入 Keil 手工采集。<br><br>
      <span class="note">真实数据契约：不编造任何数值。当前任务 / tick / 到期 tick 均标为不可知。</span></div></div>`;
    const ls=LENS.snapshots[LENS.snapshots.length-1];
    const raw=[...((ls&&ls.notes)||[]), ...((ls&&ls.identity&&ls.identity.reason)?[ls.identity.reason]:[])];
    const msgs=[...new Set(raw)];
    if(msgs.length){
      const head=msgs.map(m=>m.split('：')[0].split('\n')[0]).join('；');
      const full=msgs.join('\n\n');
      root.insertAdjacentHTML('beforeend',`<div class="snote"><b>最近一次采样未产出可用帧</b><div style="margin-top:5px">${esc(head)}</div>
        <details style="margin-top:7px"><summary class="note" style="cursor:pointer;color:var(--accent-700)">展开完整探针日志</summary>
        <div class="mono note" style="margin-top:7px;white-space:pre-wrap;word-break:break-word">${esc(full)}</div></details></div>`);
    }
    return;
  }
  root.innerHTML=`<div class="card"><h2><span class="n">V1</span>${g('调度','调度快照')} <span class="note">${g('停核采样','停核快照')} · ${g('离散快照')}</span></h2>
    <div class="plain"><span class="ptag">大白话</span><span>把芯片「暂停一瞬间」拍下的快照画出来：左边是<b>准备好能跑</b>的任务，右边是<b>正在延时睡觉</b>的任务。点任务块可跳回源码。没接调试器时，这里诚实显示「不可知」。</span></div>
    <div class="demo-head"><div class="note" id="sdesc"></div>
      <div class="btns"><span class="idx" id="sidx"></span>
      <button class="btn sec" id="sprev">${ic('prev')}上一帧</button><button class="btn" id="snext">下一帧${ic('next')}</button><button class="btn sec" id="sreset">${ic('reset')}重置</button></div></div>
    <div id="snotes"></div>
    <div id="scur" class="card" style="background:var(--accent-soft)"></div>
    <div class="grid2">
      <div><div class="note mono">优先级 1 ${g('就绪链表')} <span id="raddr"></span></div>
        <div class="heapbar" id="rbar"></div><div id="rlbl" style="display:flex"></div><div class="cap" id="rcap"></div></div>
      <div><div class="note mono">当前${g('延时链表')} <span id="daddr"></span></div>
        <div class="heapbar" id="dbar"></div><div id="dlbl" style="display:flex"></div><div class="cap" id="dcap"></div></div>
    </div>
    <div class="note" style="margin-top:10px">语义边界 (§6.2)：${g('到期 tick','延时到期')} = 具备重新就绪条件 ≠ 实际开始执行 ≠ GPIO 动作发生。当前运行任务可同时位于${g('就绪链表')} → 标「当前选中」。</div>
    <div class="note mono" style="margin-top:8px">采样时间轴（标出间隔与可能漏采）</div><div class="tl" id="stl"></div>
    <div id="sraw" style="margin-top:10px"></div></div>`;
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
    $('stl').innerHTML=validSnaps.map((x,j)=>{
      const gap=j>0?`<div class="gap" title="离散快照之间可能漏采">⇢漏?</div>`:'';
      return gap+`<div class="pt" style="height:${20+ (x.decoded.scalars.xTickCount?x.decoded.scalars.xTickCount.value%26:0)}px;opacity:${j===i?1:.5}" title="${esc(x.host_time)}"></div>`;}).join('');
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
function renderReg(){
  const r=LENS.structure.register,per=LENS.structure.peripheral;
  const latest=validSnaps[validSnaps.length-1]||snaps[snaps.length-1];
  const odr=latest?latest.gpio_odr:null;
  const pins=LENS.facts.pins;const pinBits={};
  for(const[k,p]of Object.entries(pins))if(p.confirmed_from_source&&p.port===per.name)pinBits[p.bit]=k;
  let bits='';
  const n=r.size_bits>16?16:r.size_bits;
  for(let b=0;b<n;b++){
    const f=r.fields.find(x=>x.bit_offset===b);
    const set=odr&&odr.state==='measured'?((odr.value>>b)&1):null;
    const hi=pinBits[b]!==undefined;
    bits+=`<div class="bit${hi?' hi':''}${set?' set':''}" title="${esc(f?f.description:'')}">
      <span class="bn">${esc(f?f.name:'b'+b)}${hi?' · '+pinBits[b]:''}</span>
      <span class="bv">${set===null?'?':set}</span></div>`;
  }
  let pintab='';for(const[k,p]of Object.entries(pins))pintab+=`<tr><td>${k}</td><td class="m">${esc(p.port)} · bit ${p.bit}</td><td>${p.confirmed_from_source?'<span class="tag ok">源码已确认</span>':'未确认'}</td><td class="m note">${esc(p.file)}:${p.Pin?p.Pin.line:''}</td></tr>`;
  $('view-reg').innerHTML=`<div class="card"><h2><span class="n">V2</span>${esc(per.name)} ${esc(r.name)} ${g('位段')}</h2>
    <div class="plain"><span class="ptag">大白话</span><span>把控制引脚的「开关格子」（${g('寄存器')}）一位一位画出来。这里看的是 ${g('ODR')}：某位是 1，对应引脚就输出高电平（灯亮不亮取决于硬件接法，这里只能保证电平）。高亮的位是源码里确认接了灯的引脚。没采样时每位标「?」，不瞎猜。</span></div>
    <div class="note">地址 ${val({state:'authoritative',value:r.address,prov:{file:LENS.structure.svd.file,version:LENS.structure.svd.version,offset:r.offset}})} · ${esc(r.description)} · 定义来自 ${esc(r.defined_in)}${per.derivedFrom?` (${g('derivedFrom')} ${esc(per.derivedFrom)})`:''}</div>
    <div style="margin:10px 0">${g('实测值','实测值：')}${odr?val(odr,true):'<span class="v u">不可知<i class="bdg">不可知</i></span>'} <span class="note">未采样时各位标 ?，不编造</span></div>
    <div class="bits">${bits}</div>
    <div class="note">高亮位 = 引脚映射经源码确认后才关联到板上灯（${Object.keys(pinBits).map(b=>'bit'+b+'→'+pinBits[b]).join(', ')||'无'}）。GPIO_PIN_SET 是置位操作，置哪一位由 pin 参数决定。</div>
    <h2 style="margin-top:16px"><span class="n">${g('GPIO','引脚')}</span>映射（权威：设备头 + 源码）</h2>
    <table><tr><th>符号</th><th>端口/位</th><th>确认</th><th>来源</th></tr>${pintab}</table>
    <div class="note mono" style="margin-top:8px">${g('GPIO_TypeDef')} 布局来自 ${esc(LENS.structure.header.file)} · SVD/头文件一致性：${LENS.structure.cross_check&&LENS.structure.cross_check.svd_header_agree?'✓':'需复核'}</div></div>`;
}

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
    <div class="srcrow">${srcs}</div>
    <p class="tlead">这行代码让任务睡 <b>${ticks} 个节拍</b>，不是 ${ticks} 毫秒。本工程心跳 <b>${hz} Hz</b>，名义上是 <b>${secFmt(sec)} 秒</b>；而且它只决定「最早什么时候能再跑」，不保证准时执行。</p>
    <div class="tq">
      <div><span class="k">① 传了什么</span><span class="big">${val(t.passed)}<em>tick</em></span><span class="n">节拍数。代码里看不出实际时长——单位换算由 ② 决定。</span></div>
      <div><span class="k">② 谁决定效果</span><span class="big">${val(t.decider)}<em>Hz</em></span><span class="n">${g('configTICK_RATE_HZ')}（${esc(cfgLoc)}）→ 1 tick = ${dval(msFmt(period)+' ms',`1 s ÷ ${hz} = ${msFmt(period)} ms`,{hz:hz})}。</span></div>
      <div><span class="k">③ 等于多久</span><span class="big">${val(t.derived)}<em>s</em></span><span class="n">${esc(t.derived.prov&&t.derived.prov.formula||'')}；按心跳边界唤醒，实际落在 ${dval(msFmt(lo)+'–'+msFmt(hi)+' ms',`(${ticks}−1) × ${msFmt(period)} ms ～ ${ticks} × ${msFmt(period)} ms；不含调度延迟`,{ticks:ticks,period_ms:msFmt(period)})}。</span></div>
    </div>
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
    </div></details>
  </div>`;
}

function gpioTermCard(t){
  const w=t.writes&&t.writes[0]?t.writes[0]:{};
  const key=String(w.pin_macro||'').replace(/_Pin$/,'');
  const pin=(LENS.facts&&LENS.facts.pins&&LENS.facts.pins[key])||null;
  const port=pin&&pin.port?pin.port:null;
  const bit=pin&&pin.bit!=null?pin.bit:null;
  const regName=(LENS.structure&&LENS.structure.register&&LENS.structure.register.name)||'ODR';
  const last=validSnaps[validSnaps.length-1];
  const odr=last&&last.gpio_odr&&last.gpio_odr.state==='measured'?last.gpio_odr:null;
  const bitVal=(odr&&bit!=null)?((odr.value>>bit)&1):null;
  const srcs=t.writes.map(x=>`<span class="src" data-jump="reg">${esc(fileBase(x.file))}:${x.line} HAL_GPIO_WritePin(...,${esc(x.pin_macro)},${esc(x.state)})</span>`).join('');
  const isSet=w.state==='GPIO_PIN_SET',isReset=w.state==='GPIO_PIN_RESET';
  const hs=(LENS.facts&&LENS.facts.hal_gpio_pin_state&&LENS.facts.hal_gpio_pin_state[w.state])||null;
  const stateProv=hs?{file:hs.file,line:hs.line,def_value:hs.value}:{file:w.file,line:w.line};
  const stateV=isSet?val({state:'authoritative',value:'GPIO_PIN_SET',prov:stateProv})
    :isReset?val({state:'authoritative',value:'GPIO_PIN_RESET',prov:stateProv})
    :uval('未识别第 3 个参数');
  const sem=isSet?`置位：把这一位写成 1（高电平），不是翻转${hs?'（HAL 定义值为 '+hs.value+'）':''}。`
    :isReset?`复位：把这一位写成 0（低电平），不是翻转${hs?'（HAL 定义值为 '+hs.value+'）':''}。`
    :'按 HAL 定义的写入状态处理。';
  const pinV=(port&&bit!=null)
    ?val({state:'authoritative',value:`${port} · bit ${bit}`,prov:{file:pin.file,line:pin.Pin?pin.Pin.line:null,macro:w.pin_macro}})
    :uval('main.h 未确认这组 Pin / GPIO_Port 宏');
  const odrV=bit==null?uval('引脚位未知，无法定位 '+regName+' 的位')
    :(bitVal==null?uval('尚未采样；接调试器读 '+regName+' 对应位，或导入 Keil 手工采集')
      :val({state:'measured',value:bitVal,prov:(odr.prov||{})}));
  const states=[...new Set((((LENS.facts&&LENS.facts.gpio_writes)||[]).filter(x=>x.pin_macro===w.pin_macro)).map(x=>x.state))];
  const onlyOne=states.length===1;
  return `<div class="term term-deep">
    <div class="thead"><h3>${esc(t.title)}</h3><span class="tag acc">${t.writes.length} 处写入 · ${onlyOne?'同一电平':'电平有变化'}</span></div>
    <div class="srcrow">${srcs}</div>
    <p class="tlead">同一个函数里 ${t.writes.length} 处调用，传的是同一个引脚、同一个状态：<b>${esc(w.pin_macro)} · ${esc(w.state)}</b>；已提取的写入里没有相反电平，所以这个引脚的电平不会切换。若它接着灯，灯的状态也不会跟着变——但任务是否还在调度，不能靠看灯，要靠 V1 采样。</p>
    <div class="tq">
      <div><span class="k">① 写了什么</span><span class="big">${stateV}</span><span class="n">${sem}</span></div>
      <div><span class="k">② 写到哪里</span><span class="big">${pinV}</span><span class="n">引脚映射来自源码宏，不是猜的；未确认就标不可知。</span></div>
      <div><span class="k">③ 输出会变吗</span><span class="big">${dval('不变',`${t.writes.length} 处调用都写 ${w.state}，没有相反电平，输出不会切换`,{sites:t.writes.length,state:w.state})}</span><span class="n">实际电平：${odrV}（${g(regName==='ODR'?'ODR':regName)} 对应位，采样后可见）。</span></div>
    </div>
    <div class="tsec"><div class="hd">内核与硬件之间发生了什么</div>
      <ol class="flow">
        <li><code>HAL_GPIO_WritePin(port, pin, state)</code> 的第 3 个参数是目标电平：${sem}</li>
        <li>这个函数里已提取的写入（${t.writes.length} 处）传的都是 ${esc(w.state)}——执行到哪一处，写下去的值都一样。</li>
        <li>已提取的 GPIO 写入里，这个引脚${onlyOne?`只出现 ${esc(w.state)}，没有相反电平`:`出现过 ${states.map(esc).join(' / ')}`}。</li>
        <li>没有相反电平，引脚电平和灯的状态就不会切换——这就是「灯不闪」的源码侧解释；调度是否在跑是另一回事。</li>
      </ol>
    </div>
    <div class="tsec"><div class="hd">图上怎么验证（三向联动）</div>
      <div class="note">V2 寄存器位段里，${bit!=null?`<b>bit ${bit}</b>`:'对应位'} 高亮；采样后该位应与写入状态一致（SET→1，RESET→0）。未采样时每位标「?」，不编造。最后一个有效帧实测：${odrV}。</div>
      <div style="margin-top:6px"><span class="chip" data-jump="reg">${ic('arrow',14)}跳到寄存器位段</span></div>
    </div>
    <div class="tsec"><div class="hd">想让它变化，改哪里</div>
      <div class="note">把其中一处改成<b>相反</b>电平（如 <code>GPIO_PIN_RESET</code>，或改用 Toggle 函数），引脚才会出现切换；节奏仍由旁边的 vTaskDelay 决定。只改一处、其他处仍写同一电平，切换的间隔就由两次调用之间的代码决定。</div>
    </div>
    <details class="tadv"><summary>边界与陷阱（数据诚实契约 §6.2）</summary><div class="body">
      <b>源码只能证明「写了哪个端口、哪一位、什么电平」。</b>高电平到底点亮还是熄灭，取决于硬件接法（共阴/共阳、是否反相），本页不猜。<br>
      <b>亮灯 ≠ 调度。</b>GPIO 动作发生在任务执行之后；灯的状态不能证明任务在跑、也不能证明它准时醒。<br>
      <b>数据出处。</b>${esc(t.note||'')} 引脚宏若被重定义或板子改线，需重新核对映射。
    </div></details>
  </div>`;
}

function renderTerm(){
  const terms=LENS.terms||[];
  let h=`<div class="card"><h2><span class="n">V3</span>术语卡 + 三向联动</h2>
    <div class="plain"><span class="ptag">大白话</span><span>这不是名词表，而是把每处关键调用按固定顺序讲透：<b>传了什么单位</b> → <b>哪个工程事实决定效果</b> → <b>换算成多少</b> → <b>内核里发生了什么</b> → <b>图上在哪一格验证、哪里必须标「不可知」</b>。数字都带四态标记，点虚线下划线可看名词解释。</span></div>`;
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
  h+=`</div>`;
  $('view-term').innerHTML=h;
}
function termClick(e){
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
  $('view-plat').innerHTML=`<div class="card"><h2><span class="n">§13</span>跨平台概念对照</h2>
    <div class="plain"><span class="ptag">大白话</span><span>同一个概念（比如「延时」「建任务」），在不同系统里写法不同，这张表帮你对照。目前只有 ${g('FreeRTOS')} 能读真实数据，其余先给写法对照，不假装支持。</span></div>
    <div class="note">同一概念的多平台写法。MVP 仅 FreeRTOS 提供真实数据解析${g('适配器')}；其余为概念对照卡（concept-only），导入对应真实构建后方可解析，不假装支持。</div>
    <div style="overflow-x:auto"><table class="cmp"><tr><th>概念</th>${cols.map(k=>`<th>${heads[k]}</th>`).join('')}</tr>${rows}</table></div></div>`;
}

/* ---- V4 回放/导出 ---- */
function renderReplay(){
  $('view-replay').innerHTML=`<div class="card"><h2><span class="n">V4</span>离线回放与导出</h2>
    <div class="plain"><span class="ptag">大白话</span><span>这个网页本身就是导出成果：一个文件、不依赖网络，双击就能离线看。下面可调「回放速度」，把多张${g('离散快照','快照')}按间隔自动播放。注意：只能改回放/采样间隔，不会去改芯片里的真实参数。</span></div>
    <div class="note">本文件即导出产物：单文件 HTML、零外部依赖，数据与来源内嵌同一文件，双击即可离线回放并${g('溯源')}。</div>
    <div style="margin:14px 0">回放间隔（仅回放设置，真实数据模式下不得修改目标参数）：<br>
      <input type="range" id="rint" min="200" max="3000" step="100" value="1000" style="width:min(320px,100%);margin-top:9px"> <span class="chip" id="rintv">1000 ms</span></div>
    <div class="btns"><button class="btn" id="rplay">${ic('play')}自动回放</button><button class="btn sec" id="rstop">${ic('stop')}停止</button>
      <span class="note">有效快照 ${validSnaps.length} 帧</span></div>
    <div class="note mono" style="margin-top:12px">内嵌数据：device/build/identity/structure/facts/offsets/symbols/snapshots/concepts/terms · 每个数字带四态溯源</div>
    <div class="note" style="margin-top:6px">「改参」仅指采样间隔与回放设置；写内存/改固件/烧录/复位/单步均为非目标。</div></div>`;
  $('rint').oninput=e=>$('rintv').textContent=e.target.value+' ms';
  $('rplay').onclick=()=>{if(!validSnaps.length)return;const tab=document.querySelector('.tab[data-v="sched"]');tab.click();
    let i=0;const nextBtn=$('snext');clearInterval(replayTimer);
    replayTimer=setInterval(()=>{nextBtn.click();i++;if(i>=validSnaps.length){clearInterval(replayTimer);replayTimer=null;}},+$('rint').value);};
  $('rstop').onclick=()=>{clearInterval(replayTimer);replayTimer=null;};
}

let replayTimer=null;
function renderAll(){if(replayTimer){clearInterval(replayTimer);replayTimer=null;}refreshSnaps();renderTop();renderSched();renderReg();renderTerm();renderPlat();renderReplay();
  const on=document.querySelector('.tab.on');if(on&&window.__enterView)window.__enterView($('view-'+on.dataset.v));}
$('view-term').addEventListener('click',termClick);
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
  gsap.from('.kicker, .brand h1, .sub, .mast-actions, .spec',{opacity:0,y:d(9),duration:d(.55),stagger:d(.05),ease:EASE,clearProps:'opacity,transform',overwrite:'auto'});
  const on=document.querySelector('.tab.on');
  if(on)enterView($('view-'+on.dataset.v));
}
window.__appIntro=playAppIntro;

/* Tab 滑动指示条 */
const tabsEl=$('tabs');
const ink=document.createElement('span');ink.className='tab-ink';ink.setAttribute('aria-hidden','true');tabsEl.appendChild(ink);
function moveInk(tab,animate){
  if(!tab)return;
  const o={x:tab.offsetLeft,y:tab.offsetTop+tab.offsetHeight-2,width:tab.offsetWidth};
  if(animate&&!RM.matches)gsap.to(ink,{...o,duration:.36,ease:'power3.out',overwrite:'auto'});
  else gsap.set(ink,o);
}
let rz;addEventListener('resize',()=>{clearTimeout(rz);rz=setTimeout(()=>moveInk(document.querySelector('.tab.on'),false),120);});

/* 视图入场：卡片分层浮现（V2 位格、V3 术语卡再细分） */
function enterView(view){
  if(!view)return;
  const cards=[...view.querySelectorAll(':scope > .card')];
  if(!cards.length)return;
  gsap.fromTo(cards,{opacity:0,y:d(12)},{opacity:1,y:0,duration:d(.5),stagger:d(.07),ease:EASE,overwrite:'auto',clearProps:'transform,opacity'});
  if(view.id==='view-reg')gsap.fromTo(view.querySelectorAll('.bit'),{opacity:0,scale:.95},{opacity:1,scale:1,duration:d(.32),stagger:d(.008),ease:'power2.out',delay:d(.06),overwrite:'auto',clearProps:'transform,opacity'});
  if(view.id==='view-term')gsap.fromTo(view.querySelectorAll('.term'),{opacity:0,y:d(10)},{opacity:1,y:0,duration:d(.42),stagger:d(.08),delay:d(.06),ease:EASE,overwrite:'auto',clearProps:'transform,opacity'});
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
  renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.06;
  const scene=new T.Scene();
  const camera=new T.PerspectiveCamera(32,1,1,2200);

  function makeEnv(){
    const faces=[];
    for(let i=0;i<6;i++){
      const c=document.createElement('canvas');c.width=c.height=64;
      const x=c.getContext('2d'),g=x.createLinearGradient(0,0,0,64);
      g.addColorStop(0,'#eee7d8');g.addColorStop(.55,'#aeb9c6');g.addColorStop(1,'#33404d');
      x.fillStyle=g;x.fillRect(0,0,64,64);
      if(i===0||i===2){x.fillStyle='rgba(255,255,255,.95)';x.fillRect(18,6,28,20);}
      faces.push(c);
    }
    const cube=new T.CubeTexture(faces);cube.needsUpdate=true;
    const pm=new T.PMREMGenerator(renderer);
    const env=pm.fromCubemap(cube).texture;pm.dispose();return env;
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
  scene.add(new T.HemisphereLight(0xf7f2e7,0x2c3d50,0.4));
  const key=new T.DirectionalLight(0xffffff,0.95);key.position.set(150,250,140);key.castShadow=true;
  key.shadow.mapSize.set(1024,1024);
  key.shadow.camera.left=-200;key.shadow.camera.right=200;key.shadow.camera.top=200;key.shadow.camera.bottom=-200;
  key.shadow.camera.near=1;key.shadow.camera.far=800;key.shadow.bias=-0.0006;scene.add(key);
  const rim=new T.DirectionalLight(0x9cc4e8,0.35);rim.position.set(-170,130,-120);scene.add(rim);
  const fill=new T.DirectionalLight(0xffffff,0.15);fill.position.set(-60,70,220);scene.add(fill);

  const ground=new T.Mesh(new T.CircleGeometry(320,72),new T.ShadowMaterial({opacity:.16}));
  ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;scene.add(ground);
  const grid=new T.GridHelper(540,36,0x14406b,0xcfc9b8);
  grid.material.transparent=true;grid.material.opacity=.28;grid.position.y=-.2;scene.add(grid);

  const board=new T.Group();scene.add(board);
  function box(w,h,d,mat,x,y,z){const m=new T.Mesh(new T.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);m.castShadow=true;board.add(m);return m;}
  function cyl(rt,rb,h,mat,x,y,z,seg){const m=new T.Mesh(new T.CylinderGeometry(rt,rb,h,seg||22),mat);m.position.set(x,y,z);m.castShadow=true;board.add(m);return m;}
  const pcbMat=new T.MeshPhysicalMaterial({color:col(0x0f3a58),roughness:.6,metalness:.12,clearcoat:.2,clearcoatRoughness:.55,roughnessMap:rough,bumpMap:rough,bumpScale:.02,envMapIntensity:.25});
  box(300,3.2,160,pcbMat,0,1.6,0).receiveShadow=true;
  const chipMat=new T.MeshStandardMaterial({color:col(0x171d24),roughness:.8,metalness:.06,envMapIntensity:.2});
  const goldMat=new T.MeshStandardMaterial({color:col(0xd8b25a),metalness:1,roughness:.26,envMapIntensity:.9});
  const tinMat=new T.MeshStandardMaterial({color:col(0xd6dde3),metalness:1,roughness:.22,envMapIntensity:.9});
  const blackMat=new T.MeshStandardMaterial({color:col(0x14181c),roughness:.8,metalness:.05,envMapIntensity:.2});
  const canMat=new T.MeshStandardMaterial({color:col(0xcfd6dc),metalness:1,roughness:.32,envMapIntensity:1});
  const whiteMat=new T.MeshStandardMaterial({color:col(0xe6e2d8),roughness:.6,metalness:.05});
  const potMat=new T.MeshStandardMaterial({color:col(0x1c4f8a),roughness:.5,metalness:.2});
  const traceMat=new T.MeshBasicMaterial({color:col(0x2f6c99)});
  const silkMat=new T.MeshBasicMaterial({color:col(0x9db9cf)});

  /* 主控：LQFP-64，占板比例按实物缩小 */
  const bodyMat=chipMat;
  const sh=new T.Shape(),s=28,r=4;
  sh.moveTo(-s+r,-s);sh.lineTo(s-r,-s);sh.quadraticCurveTo(s,-s,s,-s+r);
  sh.lineTo(s,s-r);sh.quadraticCurveTo(s,s,s-r,s);sh.lineTo(-s+r,s);
  sh.quadraticCurveTo(-s,s,-s,s-r);sh.lineTo(-s,-s+r);sh.quadraticCurveTo(-s,-s,-s+r,-s);
  const body=new T.Mesh(new T.ExtrudeGeometry(sh,{depth:9,bevelEnabled:true,bevelThickness:1.1,bevelSize:1.1,bevelSegments:3,steps:1,curveSegments:8}),bodyMat);
  body.rotation.x=-Math.PI/2;body.position.set(-10,3.6,-4);body.castShadow=true;body.receiveShadow=true;board.add(body);

  const leadG=new T.BoxGeometry(1.3,1,10),bendG=new T.BoxGeometry(1.3,2.2,1.3);
  for(let side=0;side<4;side++){
    const g=new T.Group();g.rotation.y=side*Math.PI/2;g.position.set(-10,0,-4);board.add(g);
    for(let i=0;i<16;i++){
      const off=-28+3.5*(i+.5);
      const lead=new T.Mesh(leadG,tinMat);lead.position.set(off,3.8,28+5);lead.castShadow=true;g.add(lead);
      const bend=new T.Mesh(bendG,tinMat);bend.position.set(off,3.5,28.2);g.add(bend);
    }
  }

  function topTexture(){
    const c=document.createElement('canvas');c.width=c.height=1024;
    const x=c.getContext('2d');
    x.strokeStyle='rgba(198,224,248,.94)';x.lineWidth=5;
    x.beginPath();x.arc(512,262,86,0,Math.PI*2);x.stroke();
    x.beginPath();x.arc(512,262,34,0,Math.PI*2);x.stroke();
    x.lineWidth=4;x.beginPath();x.moveTo(512,146);x.lineTo(512,378);x.moveTo(396,262);x.lineTo(628,262);x.stroke();
    x.fillStyle='rgba(216,235,252,.96)';x.textAlign='center';
    x.font='600 60px "Segoe UI",Arial,sans-serif';x.fillText('STM32F103RCT6',512,506);
    x.font='500 46px "Segoe UI",Arial,sans-serif';x.fillText('ARM',512,592);
    x.fillStyle='rgba(176,205,232,.75)';x.font='400 34px Consolas,monospace';
    x.fillText('LQFP-64 · CORTEX-M3',512,672);
    const t=new T.CanvasTexture(c);t.anisotropy=4;t.encoding=T.sRGBEncoding;return t;
  }
  const top=new T.Mesh(new T.PlaneGeometry(56,56),new T.MeshBasicMaterial({map:topTexture(),transparent:true,depthWrite:false}));
  top.rotation.x=-Math.PI/2;top.position.set(-10,14.05,-4);board.add(top);

  /* 两侧 2×24 排针 */
  [-72,72].forEach(z=>{
    box(272,3,5,blackMat,0,4.7,z);
    for(let i=0;i<24;i++)box(1.8,6,1.8,goldMat,-134.5+i*11.7,9,z);
  });
  /* Micro-USB + CH340 串口桥（SSOP-16） */
  box(15,7,12,canMat,-141,6,0);
  box(.8,4.6,8,blackMat,-149,6,0);
  [-3,-1,1,3].forEach(z=>box(.8,.9,1.4,goldMat,-148.4,6,z));
  box(10,2.2,6,blackMat,-104,4.3,18);
  for(let i=0;i<8;i++){
    const x=-104-7.7+i*2.2;
    [13,23].forEach(z=>box(1,.8,4,tinMat,x,3.6,z));
  }
  /* 双晶振：8 MHz 大罐 + 32.768 kHz 小罐 */
  box(20,7,10,canMat,-56,5.7,-30);
  box(8,3,4,canMat,-56,4.7,-16);
  /* LDO + 两颗电解电容（黑壳银顶 + 负极白条） */
  box(11,3.2,7,blackMat,-66,4.8,34);
  box(6,1.6,4,canMat,-66,4.2,39);
  [[-112,48],[-94,48]].forEach(q=>{
    cyl(4.5,4.5,9,blackMat,q[0],7.7,q[1]);
    cyl(4.5,4.5,.6,canMat,q[0],12.4,q[1]);
    box(1,6,.5,silkMat,q[0]+4.2,7.7,q[1]);
  });
  /* 电源拨动开关 */
  box(10,3,6,blackMat,-134,4.7,48);
  box(3,2,2,canMat,-134,6.7,48);
  /* 复位键 / BOOT0 跳线 / 用户按键 KEY1 KEY2 */
  box(9,3,9,blackMat,-42,4.7,48);
  cyl(2.2,2.2,1.6,canMat,-42,6.6,48);
  box(12,3,8,blackMat,-42,4.7,-48);
  [-46,-38].forEach(x=>[-51,-45].forEach(z=>box(1.8,5,1.8,goldMat,x,8,z)));
  [[36,-50],[62,-50]].forEach(q=>{
    box(8,3,8,blackMat,q[0],4.7,q[1]);
    box(2,1.6,2,canMat,q[0],6.9,q[1]);
  });
  /* 蜂鸣器（顶开孔） */
  cyl(7,7,7,blackMat,36,6.7,50);
  cyl(2,2,.4,new T.MeshStandardMaterial({color:col(0x05070a),roughness:.9}),36,10.3,50);
  /* 蓝白电位器 + 金属螺丝 */
  box(9,6,9,potMat,62,6.2,50);
  cyl(2,2,1,canMat,62,9.7,50);
  box(2.6,.4,.6,blackMat,62,10.3,50);
  /* microSD 卡槽（含半插卡） */
  box(20,3.5,17,canMat,52,5,14);
  box(.8,2.4,13,blackMat,62.4,5,14);
  box(8,.8,12,blackMat,67,5,14);
  /* EEPROM SOIC-8 */
  box(6,2,5,blackMat,36,4.2,-26);
  for(let i=0;i<4;i++){
    const x=36-3+i*2;
    [-29.5,-22.5].forEach(z=>box(.8,.7,2.4,tinMat,x,3.6,z));
  }
  /* JST 电池座 */
  box(12,6,9,whiteMat,-134,6.2,-42);
  [-137,-131].forEach(x=>box(1.6,4,1.6,goldMat,x,9.5,-42));
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
  /* MCU 四边去耦电容 */
  [-32,-22,-12,-2].forEach(x=>{cap(x,-42);cap(x,34);});
  [-18,-8,2].forEach(z=>{cap(-48,z);cap(28,z);});
  /* 晶振负载电容 */
  cap(-44,-38);cap(-44,-26);cap(-66,-24);cap(-66,-12);
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
  res(-124,-24);res(-124,-12);
  /* 电位器与 SD 上拉、排阻 */
  res(50,36);cap(74,36);res(36,28);
  [8,20,32].forEach(x=>res(x,-42));
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
  /* 固定孔 */
  [[-142,-68],[142,-68],[-142,68],[142,68]].forEach(q=>{
    cyl(3.2,3.2,1.6,canMat,q[0],3.6,q[1]);
    cyl(1.5,1.5,1.8,blackMat,q[0],3.9,q[1]);
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
  const oled=new T.Mesh(new T.PlaneGeometry(58,26),new T.MeshBasicMaterial({map:oledTexture(),transparent:false}));
  oled.rotation.x=-Math.PI/2;oled.position.set(-100,5.75,-38);board.add(oled);
  /* 丝印位号与名称 */
  function pcbTexture(){
    const c=document.createElement('canvas');c.width=1536;c.height=816;
    const x=c.getContext('2d');
    function label(txt,wx,wz,size,col){x.fillStyle=col||'rgba(214,232,248,.85)';x.font='500 '+size+'px Consolas,monospace';x.textAlign='center';
      x.fillText(txt,(wx+150)/300*1536,816*(.5+wz/160));}
    label('U1',-46,12,24);
    label('Y1',-56,-44,20);label('Y2',-56,-6,20);
    label('U2',-104,30,20);label('U3',-66,54,20);
    label('OLED',-100,-16,22);
    label('SD',52,28,20);
    label('BUZ',24,50,20);
    label('KEY1',26,-50,18);label('KEY2',52,-50,18);
    label('RST',-42,34,20);label('BOOT0',-42,-38,20);
    label('SWD',134,-44,22);
    label('PC3',104,-18,20);label('PC1',104,6,20);
    label('PWR',104,-46,20);label('TX',104,10,18);
    label('J1',-134,-56,20);label('VBAT',-116,-56,18);
    label('PROTO',104,66,18);
    label('C1',-32,-48,16);label('C5',-32,42,16);label('C9',-56,-18,16);label('C12',36,-18,16);
    label('C15',-44,-46,16);label('C17',-74,-24,16);
    label('C19',-80,16,16);label('C20',-80,54,16);label('C21',-54,20,16);label('C22',-54,54,16);
    label('L1',-96,36,16);label('FB1',-110,42,16);label('D1',-124,42,16);
    label('Q1',24,44,16);label('Q2',88,20,16);
    label('R1',-124,14,16);label('R3',-118,-22,16);label('R4',-30,56,16);label('R5',84,-56,16);
    label('R9',-124,-32,16);label('R11',50,28,16);label('R12',36,20,16);label('R13',8,-34,16);
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

  const ringGroup=new T.Group();ringGroup.position.set(-10,24,-4);scene.add(ringGroup);
  const ring=new T.Mesh(new T.TorusGeometry(48,.45,8,120),
    new T.MeshBasicMaterial({color:0x14406b,transparent:true,opacity:.45}));
  ring.rotation.x=-Math.PI/2+.26;ringGroup.add(ring);

  const state={yaw:.72,pitch:.95,radius:420,zoom:1,lookX:0,lookY:0,auto:true,freeze:false,dragging:false,pinching:false};
  function fit(){
    const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;
    renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
    const tan=Math.tan(16*Math.PI/180),half=184;
    state.radius=Math.max(half/tan,half/(tan*camera.aspect));
  }
  fit();
  if(window.ResizeObserver)new ResizeObserver(fit).observe(host);

  const ray=new T.Raycaster(),pt=new T.Vector2();
  let downX=0,downY=0,lastX=0,lastY=0,idle=null,targetZoom=1;
  function castAt(e){
    const b=canvas.getBoundingClientRect();
    pt.x=((e.clientX-b.left)/b.width)*2-1;pt.y=-((e.clientY-b.top)/b.height)*2+1;
    ray.setFromCamera(pt,camera);
    return ray.intersectObject(body,false).length>0;
  }
  function zoomTo(z){
    targetZoom=Math.max(.55,Math.min(2.3,z));
    if(G&&!RM2.matches)G.to(state,{zoom:targetZoom,duration:.32,ease:'power2.out',overwrite:'auto'});
    else state.zoom=targetZoom;
  }
  function resetView(){
    targetZoom=1;
    if(G&&!RM2.matches)G.to(state,{yaw:.72,pitch:.95,zoom:1,duration:.6,ease:'power3.inOut',overwrite:'auto'});
    else{state.yaw=.72;state.pitch=.95;state.zoom=1;}
  }
  const pts=new Map();let pinchDist=0;
  function twoDist(){const a=[...pts.values()];return a.length<2?0:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);}
  canvas.addEventListener('pointerdown',e=>{
    pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(canvas.setPointerCapture)canvas.setPointerCapture(e.pointerId);
    if(pts.size===2){state.pinching=true;state.dragging=false;state.auto=false;pinchDist=twoDist();clearTimeout(idle);}
    else if(pts.size===1){
      state.dragging=true;state.auto=false;clearTimeout(idle);
      downX=lastX=e.clientX;downY=lastY=e.clientY;
    }
  });
  canvas.addEventListener('pointermove',e=>{
    if(pts.has(e.pointerId))pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(state.pinching){
      if(pts.size>=2){const d=twoDist();if(d>0&&pinchDist>0)zoomTo(targetZoom*(pinchDist/d));pinchDist=d;}
      return;
    }
    if(state.dragging){
      state.yaw-=(e.clientX-lastX)*.006;
      state.pitch=Math.max(.45,Math.min(1.38,state.pitch-(e.clientY-lastY)*.005));
      lastX=e.clientX;lastY=e.clientY;
    }else{
      const hov=castAt(e);
      canvas.style.cursor=hov?'pointer':'grab';
      bodyMat.emissive.setHex(hov?0x122436:0x000000);
    }
  });
  function endDrag(e){
    pts.delete(e.pointerId);
    if(state.pinching){if(pts.size<2){state.pinching=false;idle=setTimeout(()=>{state.auto=true;},2600);}return;}
    if(!state.dragging)return;
    state.dragging=false;
    idle=setTimeout(()=>{state.auto=true;},2600);
    if(Math.hypot(e.clientX-downX,e.clientY-downY)<6&&castAt(e))registerEggClick();
  }
  canvas.addEventListener('pointerup',endDrag);
  canvas.addEventListener('pointercancel',endDrag);
  canvas.addEventListener('pointerleave',()=>{bodyMat.emissive.setHex(0x000000);canvas.style.cursor='grab';});
  canvas.addEventListener('wheel',e=>{e.preventDefault();zoomTo(targetZoom*Math.exp(e.deltaY*.0011));},{passive:false});
  canvas.addEventListener('dblclick',e=>{e.preventDefault();resetView();});
  const zin=$('ldzin'),zout=$('ldzout'),zreset=$('ldzreset');
  if(zin)zin.addEventListener('click',()=>zoomTo(targetZoom/1.22));
  if(zout)zout.addEventListener('click',()=>zoomTo(targetZoom*1.22));
  if(zreset)zreset.addEventListener('click',resetView);

  let prev=0;
  renderer.setAnimationLoop(t=>{
    if(document.hidden||host.offsetParent===null)return;
    const dt=prev?Math.min(.06,(t-prev)/1000):0;prev=t;
    if(state.auto&&!state.dragging&&!state.freeze)state.yaw+=dt*.11;
    const yaw=state.yaw+state.lookX*.22,pitch=state.pitch+state.lookY*.07;
    const sp=Math.sin(pitch),rad=state.radius*state.zoom;
    camera.position.set(rad*sp*Math.sin(yaw),rad*Math.cos(pitch)+12,rad*sp*Math.cos(yaw));
    camera.lookAt(0,12,0);
    if(!state.freeze){board.position.y=Math.sin(t/1600)*1.6;board.rotation.z=Math.sin(t/2400)*.012;ringGroup.rotation.y+=dt*.5;}
    led.material.emissiveIntensity=state.freeze?.7+Math.sin(t/90)*.6:.7+Math.sin(t/700)*.35;
    renderer.render(scene,camera);
  });
  host.classList.add('gl-ok');
  return {state:state,setLook(nx,ny){state.lookX=nx;state.lookY=ny;}};
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
document.addEventListener('keydown',e=>{if(!landing.hidden&&e.key==='Enter'){e.preventDefault();enterApp();}});

function showLanding(){
  if(!landing.hidden)return;
  landing.hidden=false;document.body.classList.add('landing-on');setAppHidden(true);window.scrollTo(0,0);
  if(eggOn)eggOff(false);
  if(G){G.set(['.ld-main','.ld-stage','.ld-marquee'],{opacity:1,y:0});G.set(enterBtn,{x:0,y:0});
    const ring=document.querySelector('.ld-cta-ring');if(ring)G.set(ring,{opacity:0,scale:1});}
  landingIn();
  enterBtn.focus({preventScroll:true});
}
home.addEventListener('click',showLanding);

/* ---- 彩蛋：连点中央芯片 3 次，或键入 swd ---- */
const stage=$('ldstage'),hit=$('ldhit'),trace=$('ldtrace'),scan=$('ldscan'),toast=$('ldeggtoast'),secret=$('ldsecret');
let eggOn=false,eggTl=null,clicks=[];
function eggOff(){
  eggOn=false;
  if(eggTl){eggTl.kill();eggTl=null;}
  if(G){G.set([trace,toast],{opacity:0,clearProps:'transform'});if(secret)G.set(secret,{opacity:1});}
  else{trace.style.opacity=0;toast.style.opacity=0;}
  ambient.forEach(t=>t.resume());if(marqTween)marqTween.resume();
  stage.classList.remove('egg-on');
  if(gl)gl.state.freeze=false;
}
function eggPlay(){
  if(eggOn||landing.hidden)return;eggOn=true;
  stage.classList.add('egg-on');
  if(gl)gl.state.freeze=true;
  if(!G||RM2.matches){
    if(G)G.set([trace,toast],{opacity:1});else{trace.style.opacity=1;toast.style.opacity=1;}
    setTimeout(()=>{if(G)G.set([trace,toast],{opacity:0});else{trace.style.opacity=0;toast.style.opacity=0;}stage.classList.remove('egg-on');eggOn=false;},2600);return;}
  ambient.forEach(t=>t.pause());if(marqTween)marqTween.pause();
  const beats=[...trace.querySelectorAll('span')];
  G.set([trace,toast],{opacity:1});
  if(secret)G.to(secret,{opacity:0,duration:.2,overwrite:'auto'});
  eggTl=G.timeline({onComplete:()=>{
    eggTl=null;
    const done=()=>eggOff();
    if(RM2.matches)done();
    else G.to([trace,toast],{opacity:0,duration:.45,ease:'power2.out',onComplete:done,overwrite:'auto'});
  }});
  eggTl.fromTo(beats,{opacity:0,y:6},{opacity:1,y:0,duration:.24,stagger:.5,ease:'power2.out'},0)
    .fromTo(toast,{opacity:0,y:-6},{opacity:1,y:0,duration:.35,ease:'power2.out'},0)
    .fromTo(scan,{xPercent:0},{xPercent:520,duration:.62,ease:'power1.inOut',repeat:2,repeatDelay:.3},.15)
    .fromTo('#ldticks line.mj',{opacity:.3},{opacity:1,duration:.16,stagger:{each:.015,from:'random'},yoyo:true,repeat:1},.1)
    .fromTo('.ld-core',{scale:1,opacity:1},{scale:5,opacity:0,duration:.7,ease:'power2.out',svgOrigin:'280 280'},.1)
    .to({},{duration:1.5});
}
function registerEggClick(){
  const now=Date.now();clicks=clicks.filter(t=>now-t<1500);clicks.push(now);
  if(clicks.length>=3){clicks=[];eggPlay();}
}
if(hit)hit.addEventListener('click',registerEggClick);
let kbBuf='';
document.addEventListener('keydown',e=>{
  if(landing.hidden||e.metaKey||e.ctrlKey||e.altKey)return;
  if(e.key&&e.key.length===1){kbBuf=(kbBuf+e.key.toLowerCase()).slice(-6);
    if(kbBuf.endsWith('swd')){kbBuf='';eggPlay();}}
});

const deep=['sched','reg','term','plat','replay'].some(v=>location.hash==='#'+v);
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
  for(const d of facts.delay_calls){if(!tick)continue;const sec=d.ticks/tick;const secStr=String(+sec.toFixed(6));
    terms.push({kind:'delay',title:'vTaskDelay('+d.ticks+')',source:{file:d.file,line:d.line,fn:d.in_fn},
      passed:authoritative(d.ticks,d.file,null,d.line),decider:authoritative(tick,cfg.file,null,cfg.line),
      derived:derived(Math.round(sec*1e4)/1e4,d.ticks+' tick ÷ '+tick+' Hz ≈ '+secStr+' s',{ticks:d.ticks,hz:tick}),
      visible:'延时链表中的实测到期 tick（采样后可见）',links:{config:'configTICK_RATE_HZ',graph:'delayed'}});}
  const groups={};
  for(const w of facts.gpio_writes){const k=w.in_fn+'|'+w.pin_macro;(groups[k]=groups[k]||[]).push(w);}
  for(const k in groups){const ws=groups[k];const states=new Set(ws.map(w=>w.state));
    if(ws.length>=2&&states.size===1){const st=[...states][0];const fn=ws[0].in_fn,pin=ws[0].pin_macro;
      const sem=st==='GPIO_PIN_SET'?'置位操作（写 1）':st==='GPIO_PIN_RESET'?'复位操作（写 0）':'按 HAL 定义的写入';
      terms.push({kind:'gpio_dual',title:fn+': '+ws.length+' 处写入都是 '+st,
        writes:ws.map(w=>({file:w.file,line:w.line,state:w.state,pin_macro:w.pin_macro})),
        note:st+' 表示'+sem+'，置哪一位由 pin 参数决定（'+pin+'），不可混淆。同函数内所有写入状态相同 → 引脚电平不会切换。',
        links:{graph:'register'}});}}
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
function download(name,text,type){const blob=new Blob([text],{type:type+';charset=utf-8'});const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}
$('impexphtml').addEventListener('click',()=>{
  const clone=document.documentElement.cloneNode(true);
  ['#impwrap','#prov','#scrim'].forEach(s=>{const el=clone.querySelector(s);if(el)el.classList.remove('on');});
  let html='<!DOCTYPE html>\n'+clone.outerHTML;
  const json=JSON.stringify(LENS).replace(/</g,'\\u003c');
  html=html.replace(/let LENS = [^\n]*;\nconst STATE=/,'let LENS = '+json+';\nconst STATE=');
  download('embedded-lens-imported.html',html,'text/html');
  status('已导出单文件 HTML（内嵌当前导入数据，双击离线打开）。','ok');
});
$('impexpjson').addEventListener('click',()=>{download('payload.json',JSON.stringify(LENS,null,1),'application/json');status('已导出 payload.json。','ok');});
$('f_json').addEventListener('change',async e=>{const f=e.target.files[0];if(!f)return;
  try{const p=JSON.parse(await f.text());
    if(!p.device||!p.build||!p.structure)throw new Error('不是有效的 EmbeddedLens payload');
    p.concepts=p.concepts||CONCEPTS;p.honesty=p.honesty||HONESTY;p.snapshots=p.snapshots||[];p.terms=p.terms||[];
    LENS=p;renderAll();$('impexphtml').disabled=false;$('impexpjson').disabled=false;
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