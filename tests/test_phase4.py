"""Kiểm hợp đồng Phase 4; chạy trình duyệt bằng riêng mục browser_main."""

import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path

from chonoi.bench import _metrics, chromium_path
from chonoi.contract import load_contract
from chonoi.inputs import InputState
from chonoi.live import LiveGame, LiveServer
from chonoi.runner import Session
from chonoi.scenario import load_scenario
from tests.helpers import contract_command

ROOT = Path(__file__).resolve().parents[1]


class PhaseFour(unittest.TestCase):
    def test_render_metrics_use_slowest_ceil_one_percent(self):
        intervals = [16] * 99 + [40, 60]
        result = _metrics({"samples": intervals, "measuringStart": 3000,
                           "measuringEnd": 3000 + sum(intervals)}, 901.2346)
        self.assertEqual(result, {"avg_fps": 59.976, "p1_low_fps": 20.0, "frames": 101,
                                  "measured_s": 1.684, "load_ms": 901.235})

    def test_soak_manifest_runs_ten_deterministic_days(self):
        contract = load_contract()
        self.assertEqual(contract["contract_version"], "1.3")
        self.assertTrue(contract["bench_cmd"])
        cmd = contract_command("soak_cmd")
        reports = []
        with tempfile.TemporaryDirectory() as directory:
            for attempt in range(2):
                out = Path(directory, f"soak-{attempt}.json")
                result = subprocess.run([*cmd, "--seed", "7", "--days", "10", "--out", str(out)],
                                        cwd=ROOT, capture_output=True, text=True, timeout=45)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(out.read_text(encoding="utf-8"))
                self.assertEqual(set(payload), {"days", "days_completed", "crashes", "results", "duration_s"})
                self.assertGreater(payload.pop("duration_s"), 0)
                self.assertEqual((payload["days"], payload["days_completed"], payload["crashes"]), (10, 10, 0))
                self.assertEqual([day["day"] for day in payload["results"]], list(range(1, 11)))
                for day in payload["results"]:
                    self.assertEqual(set(day), {"day", "earned", "reputation", "score"})
                    self.assertEqual(day["score"], day["earned"] + 100 * int(day["reputation"]))
                reports.append(payload)
        self.assertEqual(*reports)

    def test_day_six_repeats_plan_and_preserves_campaign(self):
        tuning = load_contract()["tuning"]
        scenario = {"day": {"money": 200, "earned": 300, "reputation": 4},
                    "gather": {"hold": [{"id": "I9", "kind": "ca_loc", "fresh": 100}],
                               "time_left_ticks": 1},
                    "quan": {"time_left_ticks": 1}}
        session = Session("day", tuning, scenario, 7, days=10)
        plans, item_ids = [], []
        idle = InputState((0, 0), {}, set())
        for day in range(1, 11):
            state = session.snapshot()
            self.assertEqual(state["phase"], "gather")
            self.assertEqual(state["day"], day)
            self.assertEqual((state["money"], state["earned"], state["reputation"]),
                             (200 if day == 1 else 0, 300, 4))
            self.assertEqual(state["active_upgrades"].get("oxygen", 0), 0 if day == 1 else 1)
            plans.append(state["day_plan"])
            item_ids.append(state["hold"][0]["id"])
            session.step(idle)
            state = session.snapshot()
            self.assertEqual(state["phase"], "quan")
            self.assertEqual(state["stock"][0]["id"], item_ids[-1])
            session.step(idle)
            self.assertEqual(session.snapshot()["phase"], "shop")
            session.step(InputState((0, 0), {"shop_done": True}, {"shop_done"},
                                    buy="oxygen" if day == 1 else None))
        self.assertEqual(plans[:5], plans[5:])
        self.assertEqual(item_ids, [f"I{n}" for n in range(9, 19)])
        self.assertTrue(session.done)
        self.assertEqual(session.sim.days_completed, 10)


def browser_main(destination):
    """Start isolated real game servers for reproducible browser acceptance."""
    tuning = load_contract()["tuning"]
    danger = {"gather": {"player": {"pos": [53, 24], "oxygen_ticks": 420}}}
    demo = {
        "day": {"money": 200, "earned": 200},
        "gather": {"player": {"pos": [7, 10]}, "monsters": [], "random_fish": False,
                   "fish": [{"id": "F1", "kind": "ca_loc", "pos": [7, 9]}]},
        "quan": {"player": {"pos": [2, 8]}, "time_left_ticks": 960, "random_customers": False,
                 "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                "patience_ticks_left": 850}]},
    }
    with ExitStack() as stack, tempfile.TemporaryDirectory() as directory:
        urls = []
        for mode, data in (("gather", danger), ("day", demo)):
            fixture = Path(directory, f"{mode}.json")
            fixture.write_text(json.dumps(data), encoding="utf-8")
            game = LiveGame(mode, tuning, load_scenario(fixture, mode, tuning), 42, days=1)
            server = LiveServer(game, port=0)
            server.start()
            stack.callback(server.stop)
            urls.append(server.url)
        subprocess.run(["node", str(ROOT / "tests/browser_phase4.cjs"), chromium_path(),
                        *urls, str(Path(destination).resolve())], cwd=ROOT, check=True, timeout=60)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--browser":
        browser_main(sys.argv[2])
    else:
        unittest.main()
