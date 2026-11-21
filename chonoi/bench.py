"""Phase 4: measure real Canvas-rendered frames in a Chromium browser.

Usage: python -m chonoi.bench --seed 42 --duration 30 --out bench.json

Requires Node.js 22+ and a local Chromium, Chrome or Edge installation.

Unlike an rAF callback counter, this instruments drawGather itself and only
counts frames after a real draw finishes. Headless Chromium still renders
Canvas; use --headed to observe the browser on a desktop.
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .contract import load_contract
from .live import LiveGame, LiveServer


# Count completed Canvas draws rather than animation callbacks.
INSTRUMENT_JS = r"""
({warmupMs, durationMs}) => {
  if (typeof drawGather !== 'function' || typeof snap === 'undefined') {
    throw new Error('The Gather Canvas renderer is unavailable');
  }
  if (window.__phase4Bench) {
    throw new Error('A benchmark is already installed');
  }
  window.__phase4Bench = {
    first: null,
    firstEpoch: null,
    measuringStart: null,
    measuringEnd: null,
    previous: null,
    samples: [],
    done: false
  };
  const oldDrawGather = drawGather;
  drawGather = function(w, h) {
    // A real render of the game scene must have completed before counting it.
    const output = oldDrawGather.apply(this, arguments);
    if (home || restarting || offline) return output;
    const now = performance.now();
    const b = window.__phase4Bench;
    if (b.first === null) {
      b.first = now;
      b.firstEpoch = performance.timeOrigin + now;
    }
    if (b.done) return output;
    if (now - b.first < warmupMs) return output;
    if (b.measuringStart === null) {
      b.measuringStart = now;
      b.previous = now;
      return output;
    }
    const delta = now - b.previous;
    if (delta > 0) b.samples.push(delta);
    b.previous = now;
    if (now - b.measuringStart >= durationMs) {
      b.measuringEnd = now;
      b.done = true;
    }
    return output;
  };
}
"""


def _save_json(path, data):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".bench-", suffix=".tmp", dir=dest.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, dest)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _metrics(raw, load_ms):
    intervals_ms = raw["samples"]
    count = len(intervals_ms)
    if count < 2 or raw["measuringEnd"] is None:
        raise RuntimeError("No measurable Canvas frames were recorded")
    elapsed = (raw["measuringEnd"] - raw["measuringStart"]) / 1000.0
    if elapsed <= 0 or not math.isfinite(elapsed):
        raise RuntimeError("Invalid measured render duration")
    worst_count = max(1, math.ceil(0.01 * count))
    worst = sorted(intervals_ms, reverse=True)[:worst_count]
    low = worst_count * 1000.0 / sum(worst)
    return {
        "avg_fps": round(count / elapsed, 3),
        "p1_low_fps": round(low, 3),
        "frames": count,
        "measured_s": round(elapsed, 3),
        "load_ms": round(load_ms, 3),
    }


def chromium_path():
    override = os.environ.get("CHONOI_BROWSER")
    if override:
        return override
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "microsoft-edge"):
        if installed := shutil.which(name):
            return installed
    candidates = [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                  Path("/Applications/Chromium.app/Contents/MacOS/Chromium")]
    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        if root := os.environ.get(variable):
            candidates.extend([Path(root, "Google/Chrome/Application/chrome.exe"),
                               Path(root, "Microsoft/Edge/Application/msedge.exe")])
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError("Không tìm thấy Chromium, Chrome hoặc Edge. Đặt CHONOI_BROWSER tới file thực thi.")


def run_benchmark(seed, duration, headed=False):
    launched_at = time.time_ns() / 1_000_000
    executable = chromium_path()
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Benchmark cần Node.js 22+")
    driver = Path(__file__).resolve().parents[1] / "tools" / "chromium.cjs"
    source = "(" + INSTRUMENT_JS + ")(" + json.dumps({"warmupMs": 3000, "durationMs": duration * 1000}) + ")"
    tuning = load_contract()["tuning"]
    # Gather defaults: player stays docked, freshness enabled, fish and
    # Năm Chèo monsters run, default effects remain on.
    game = LiveGame("gather", tuning, {}, seed)
    server = LiveServer(game, host="127.0.0.1", port=0)
    server.start()
    try:
        result = subprocess.run(
            [node, str(driver), executable, server.url, source, "headed" if headed else "headless"],
            capture_output=True, text=True, encoding="utf-8", timeout=duration + 35,
            env=dict(os.environ, CHONOI_BENCH_TIMEOUT=str(int((duration + 18) * 1000))),
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Không đo được scene trong Chromium")
        raw = json.loads(result.stdout)
        return _metrics(raw, raw["firstEpoch"] - launched_at)
    finally:
        server.stop()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Canvas-render benchmark for Phase 4")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--duration", required=True, type=float, help="Seconds after 3s warmup")
    parser.add_argument("--out", required=True)
    parser.add_argument("--headed", action="store_true", help="Show Chromium instead of headless rendering")
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration) or args.duration <= 0:
        parser.error("--duration must be a positive finite number")
    try:
        result = run_benchmark(args.seed, args.duration, headed=args.headed)
        _save_json(args.out, result)
    except Exception as exc:
        print(f"Benchmark FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(
        f"Benchmark complete: {result['avg_fps']} avg FPS, "
        f"{result['p1_low_fps']} 1% low FPS, "
        f"{result['frames']} rendered frames"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
