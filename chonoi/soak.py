"""Phase 4: deterministic, real 10-day headless soak for Cho Noi.

Usage: python -m chonoi.soak --seed 7 --days 10 --out soak.json

Uses the existing Session/DaySim simulation, rather than synthesizing results.
One deterministic bot gathers two bong_sung per day, serves customers when
possible, and closes each Shop. No gameplay state is reset between days.
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
from .inputs import InputState
from .runner import Session


def _input(move=(0.0, 0.0), press=None):
    edges = {press} if press else set()
    return InputState(move, {press: True} if press else {}, edges)


def _navigate(position, destination, radius=1.0):
    """Return a direction and whether an interact edge can be sent."""
    dx = destination[0] - position[0]
    dy = destination[1] - position[1]
    distance = math.hypot(dx, dy)
    if distance <= radius:
        return (0.0, 0.0), True
    return (dx / distance, dy / distance), False


class DeterministicBot:
    """Drive the same simulation and input semantics used by headless mode."""

    def __init__(self):
        self.day = None
        self.gather_stage = 0

    def choose(self, day_sim):
        if self.day != day_sim.day:
            self.day = day_sim.day
            self.gather_stage = 0

        phase = day_sim.phase
        sim = day_sim.current if phase != "shop" else None

        if phase == "shop":
            return _input(press="shop_done")

        if phase == "gather":
            # Gather N3 and N4, then return to the dock. The bot stays
            # on the surface; default fish and monsters still run normally.
            if self.gather_stage < 2:
                node_id = ("N3", "N4")[self.gather_stage]
                node = next((n for n in sim.nodes if n["id"] == node_id), None)
                if node is None:
                    raise RuntimeError(f"missing default gather node {node_id}")
                move, reached = _navigate(sim.pos, node["pos"], radius=1.0)
                if reached and node["regrow_ticks"] == 0:
                    return _input(press="interact")
                return _input(move)

            move, reached = _navigate(sim.pos, sim.t["dock_pos"], radius=1.0)
            return _input(press="interact") if reached else _input(move)

        # Quan: take an order at a stove, collect it once cooked, and
        # serve it at the matching table. Idle when there is nothing to do.
        if sim.hand is not None:
            order_id = sim.hand["order_id"]
            customer = sim.customers.get(order_id)
            if customer is None:
                return _input()
            table = next((t for t in sim.tables if t["id"] == customer["table_id"]), None)
            if table is None:
                raise RuntimeError("customer table missing")
            move, reached = _navigate(sim.pos, table["pos"], radius=0.8)
            return _input(press="interact") if reached else _input(move)

        ready = next((s for s in sim.stoves if s["state"] == "ready"), None)
        if ready is not None:
            move, reached = _navigate(sim.pos, ready["pos"], radius=0.8)
            return _input(press="interact") if reached else _input(move)

        reserved = any(c["order_status"] == "reserved" for c in sim.customers.values())
        idle = next((s for s in sim.stoves if s["state"] == "idle"), None)
        if reserved and idle is not None:
            move, reached = _navigate(sim.pos, idle["pos"], radius=0.8)
            return _input(press="interact") if reached else _input(move)

        return _input()

    def observe(self, rows):
        """Advance gather targets only after a successful harvest event."""
        if self.gather_stage >= 2:
            return
        target_id = ("N3", "N4")[self.gather_stage]
        if any(row["name"] == "gather" and row["data"].get("node_id") == target_id
               for row in rows):
            self.gather_stage += 1


def _save_json(path, data):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".soak-", suffix=".tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(tmp, destination)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def run_soak(seed, days):
    tuning = load_contract()["tuning"]
    session = Session("day", tuning, {}, seed, days=days)
    bot = DeterministicBot()
    results = []
    visited = {}
    # Bound the run so a transition regression cannot loop forever.
    per_day = round((tuning["gather"]["duration_s"] +
                     tuning["quan"]["duration_s"]) * tuning["tick_hz"])
    per_day += tuning["shop"]["max_ticks"]
    limit = days * (per_day + 10)

    while not session.done and session.tick < limit:
        day = session.sim
        before_phase = day.phase
        before_day = day.day
        visited.setdefault(before_day, set()).add(before_phase)
        rows = session.step(bot.choose(day))
        bot.observe(rows)

        for row in rows:
            if row["name"] != "shop_end":
                continue
            day_number = row["day"]
            if visited.get(day_number) != {"gather", "quan", "shop"}:
                raise RuntimeError(f"day {day_number} skipped a game phase")
            state = session.end_row()
            results.append({
                "day": day_number,
                "earned": state["earned"],
                "reputation": state["reputation"],
                "score": state["score"],
            })

    if not session.done or session.sim.reason != "days_complete":
        raise RuntimeError(f"soak stopped at tick {session.tick} before days_complete")
    if session.sim.days_completed != days or len(results) != days:
        raise RuntimeError("soak completed-days/result count mismatch")
    return results, session.sim.days_completed


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deterministic 10-day Phase 4 soak")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.days < 1:
        parser.error("--days must be a positive integer")

    start = time.perf_counter()
    completed, results, crashes = 0, [], 0
    try:
        results, completed = run_soak(args.seed, args.days)
    except Exception as exc:
        crashes = 1
        print(f"Soak FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)

    payload = {
        "days": args.days,
        "days_completed": completed,
        "crashes": crashes,
        "results": results,
        "duration_s": round(time.perf_counter() - start, 6),
    }
    try:
        _save_json(args.out, payload)
    except OSError as exc:
        print(f"Cannot write soak result: {exc}", file=sys.stderr)
        return 1
    if crashes:
        return 1
    print(f"Soak PASS: {completed}/{args.days} days; {len(results)} shop closes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
