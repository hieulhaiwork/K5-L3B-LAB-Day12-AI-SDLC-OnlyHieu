"""Phase 4: measure real Canvas-rendered frames in a Chromium browser.

Usage: python -m chonoi.bench --seed 42 --duration 30 --out bench.json

Install once: python -m pip install playwright
              python -m playwright install chromium

Unlike an rAF callback counter, this instruments drawGather itself and only
counts frames after a real draw finishes. Headless Chromium still renders
Canvas; use --headed to observe the browser on a desktop.
"""

import argparse
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

from .contract import load_contract
from .live import LiveGame, LiveServer


# App JS draws only for new /state snapshots, even though rAF fires more often.
# Hook drawGather (not rAF) to count completed Canvas draws.
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
    const now = performance.now();
    const b = window.__phase4Bench;
    if (b.first === null) b.first = now;
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


def run_benchmark(seed, duration, headed=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright missing: pip install playwright && playwright install chromium"
        ) from exc

    launched_at = time.perf_counter()
    tuning = load_contract()["tuning"]
    # Gather defaults: player stays docked, freshness enabled, fish and
    # Năm Chèo monsters run, default effects remain on.
    game = LiveGame("gather", tuning, {}, seed)
    server = LiveServer(game, host="127.0.0.1", port=0)
    server.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not headed)
            try:
                page = browser.new_page(
                    viewport={"width": 1280, "height": 720},
                    device_scale_factor=1,
                )
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                page.goto(server.url, wait_until="domcontentloaded", timeout=30000)
                page.locator('[data-action="start"]').click(timeout=15000)
                page.wait_for_function(
                    "typeof snap !== 'undefined' && snap && snap.phase === 'gather' "
                    "&& !home && !restarting && !offline",
                    timeout=15000,
                )
                # Force one ordinary frame after instrumentation. Subsequent
                # frames come solely from the game's normal Canvas render loop.
                page.evaluate(INSTRUMENT_JS, {
                    "warmupMs": 3000,
                    "durationMs": duration * 1000,
                })
                page.evaluate("() => { lastDraw = null; }")
                page.wait_for_function(
                    "window.__phase4Bench && window.__phase4Bench.first !== null",
                    timeout=10000,
                )
                load_ms = (time.perf_counter() - launched_at) * 1000.0
                page.wait_for_function(
                    "window.__phase4Bench && window.__phase4Bench.done",
                    timeout=max(45000, int((duration + 15) * 1000)),
                )
                raw = page.evaluate("() => window.__phase4Bench")
                if errors:
                    raise RuntimeError(f"Browser JavaScript error: {errors[0]}")
                return _metrics(raw, load_ms)
            finally:
                browser.close()
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
