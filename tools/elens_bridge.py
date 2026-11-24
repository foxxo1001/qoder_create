"""EmbeddedLens 本机桥接：托管导出页 + 一键只读采样。

静态网页不能直接访问 ST-LINK。本桥接只监听 127.0.0.1，调用现有
OpenOCD halt-read-resume 采样器；不写内存、不烧录、不复位。
"""
import argparse, importlib.util, json, re, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CLI_PATH = ROOT / "elens.py"
DEFAULT_PAGE = ROOT.parent / "dist" / "embedded-lens.html"
REQUIRED = ("symbols.json", "offsets.json", "structure.json", "facts.json",
            "firmware_pack.json", "profile.json")
EXAMPLE_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
SAMPLE_LOCK = threading.Lock()

def _load_cli():
    spec = importlib.util.spec_from_file_location("elens_cli", CLI_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cli = _load_cli()
from elens import sample as sampler, frames as frame_builder, export as exporter, rtos as rtos_mod


def _origin_ok(origin):
    if not origin or origin == "null":
        return True
    try:
        u = urlparse(origin)
    except ValueError:
        return False
    if u.scheme in ("http", "https") and u.hostname in ("127.0.0.1", "localhost"):
        return True
    return u.scheme == "https" and u.hostname == "embedded-lens.pages.dev"


def _cors(handler):
    origin = handler.headers.get("Origin")
    if origin and _origin_ok(origin):
        handler.send_header("Access-Control-Allow-Origin", origin)
        handler.send_header("Vary", "Origin")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


def _json(handler, status, obj):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    _cors(handler)
    handler.end_headers()
    handler.wfile.write(body)


def _examples(root):
    out = []
    if not root.is_dir():
        return out
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        missing = [f for f in REQUIRED if not (d / f).exists()]
        out.append({"name": d.name, "ready": not missing, "missing": missing})
    return out


def _run_sample(examples_dir, page_path, example, frames_n, interval_s):
    ex = examples_dir / example
    if not ex.is_dir() or not EXAMPLE_RE.fullmatch(example):
        return {"ok": False, "error": "工程名无效或目录不存在", "snapshots": []}
    try:
        artifacts = cli.load_artifacts(ex)
    except Exception as e:
        return {"ok": False, "error": f"工程产物不完整：{e}", "snapshots": []}
    adapter = rtos_mod.detect_adapter(artifacts["symbols"]["symbols"])
    if adapter is None:
        return {"ok": False, "error": "未检测到受支持的 RTOS 内核符号", "snapshots": []}
    prof = dict(artifacts.get("profile") or cli.EXAMPLE_CFG["profile"])
    svd_base = int(artifacts["structure"]["peripheral"]["base_address"], 16)
    if prof.get("gpio_base") != svd_base:
        prof["gpio_base"] = svd_base
    odr = artifacts["structure"]["register"]["offset"]
    try:
        shots = sampler.sample_session(
            prof, artifacts["pack"], artifacts["symbols"]["symbols"], artifacts["offsets"], adapter,
            ex / "sample_run", str(cli.OPENOCD), str(cli.OCD_SCRIPTS),
            odr_offset=odr, frames=frames_n, interval_s=interval_s)
    except Exception as e:
        return {"ok": False, "error": f"采样器异常：{e}", "snapshots": []}
    history = cli.load_snapshots(ex)
    history.extend(shots)
    (ex / "snapshots.json").write_text(json.dumps(history, ensure_ascii=False, indent=1), encoding="utf-8")
    export_error = None
    payload = None
    try:
        payload = frame_builder.build_payload(example, artifacts, history, prof, adapter.name)
        exporter.export(payload, page_path)
    except Exception as e:
        export_error = str(e)
    valid = sum(1 for s in shots if s.get("valid"))
    diagnostic = next((s.get("diagnostic") for s in shots
                       if (s.get("diagnostic") or {}).get("code") not in (None, "ok")), None)
    return {"ok": valid > 0, "snapshots": shots, "payload": payload,
            "summary": {"example": example, "frames": len(shots), "valid": valid,
                        "session": (shots[0].get("session") or {}) if shots else {},
                        "identity": (shots[-1].get("identity") or {}).get("status") if shots else None,
                        "diagnostic": diagnostic, "exported": export_error is None,
                        "export_error": export_error}}


class Handler(BaseHTTPRequestHandler):
    server_version = "EmbeddedLensBridge/1.0"

    def _origin_allowed(self):
        origin = self.headers.get("Origin")
        if origin and not _origin_ok(origin):
            _json(self, 403, {"ok": False, "error": "Origin 不在本机桥接允许列表"})
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Content-Length", "0")
        _cors(self)
        self.end_headers()

    def do_GET(self):
        if not self._origin_allowed():
            return
        path = urlparse(self.path).path
        if path in ("/", "/embedded-lens.html"):
            page = self.server.page_path
            if not page.exists():
                _json(self, 503, {"ok": False, "error": f"页面不存在：{page}"})
                return
            data = page.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            _cors(self)
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/health":
            examples = _examples(self.server.examples_dir)
            ready = [x["name"] for x in examples if x["ready"]]
            default = cli.EXAMPLE_CFG["name"] if cli.EXAMPLE_CFG["name"] in ready else (ready[0] if ready else None)
            _json(self, 200, {
                "ok": True, "app": "EmbeddedLens bridge", "version": 1,
                "examples": examples, "default": default,
                "tools": {"openocd": str(cli.OPENOCD), "openocd_exists": cli.OPENOCD.exists(),
                          "scripts": str(cli.OCD_SCRIPTS), "scripts_exists": cli.OCD_SCRIPTS.exists()},
                "page": {"path": str(self.server.page_path), "exists": self.server.page_path.exists()},
                "note": "探针连接状态在读取时检测；采样只读，不写内存/不烧录/不复位。"})
            return
        _json(self, 404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if not self._origin_allowed():
            return
        if urlparse(self.path).path != "/sample":
            _json(self, 404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > 4096:
            _json(self, 400, {"ok": False, "error": "请求体为空或过大"})
            return
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            _json(self, 400, {"ok": False, "error": "JSON 无效"})
            return
        example = str(body.get("example") or "")
        if not EXAMPLE_RE.fullmatch(example):
            _json(self, 400, {"ok": False, "error": "工程名无效"})
            return
        try:
            frames_n = max(1, min(20, int(body.get("frames", 5))))
        except (TypeError, ValueError):
            frames_n = 5
        try:
            interval_s = max(0.0, min(10.0, float(body.get("interval", 1.0))))
        except (TypeError, ValueError):
            interval_s = 1.0
        if not SAMPLE_LOCK.acquire(blocking=False):
            _json(self, 409, {"ok": False, "error": "已有一次采样在进行，请稍后再试"})
            return
        try:
            result = _run_sample(self.server.examples_dir, self.server.page_path,
                                 example, frames_n, interval_s)
            _json(self, 200, result)
        except Exception as e:
            _json(self, 500, {"ok": False, "error": f"桥接异常：{e}", "snapshots": []})
        finally:
            SAMPLE_LOCK.release()


def main():
    p = argparse.ArgumentParser(prog="elens_bridge")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--page", default=str(DEFAULT_PAGE))
    p.add_argument("--examples-dir", default=str(cli.EXAMPLES))
    args = p.parse_args()
    page = Path(args.page).resolve()
    examples = Path(args.examples_dir).resolve()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    srv.daemon_threads = True
    srv.page_path = page
    srv.examples_dir = examples
    print(f"EmbeddedLens bridge: http://127.0.0.1:{args.port}/")
    print(f"  page     : {page}{'' if page.exists() else '  [缺失，请先 python elens.py export]'}")
    print(f"  examples : {examples}")
    print("  在页面点「一键读取」。仅本机访问；Ctrl+C 停止。")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()