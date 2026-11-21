"""Smoke hộp đen cho vòng ngày và kiểm tích hợp màn live."""

import json
import os
import unittest
from pathlib import Path

from helpers import Workdir, events, frames, individuals, item_counts, read_jsonl, run_headless, snapshots, write_json
from chonoi.contract import load_contract
from chonoi.live import LiveGame


class DayPhase2(unittest.TestCase):
    def test_roundtrip_shop_pause_and_deferred_upgrade_are_deterministic(self):
        with Workdir() as w:
            scenario = write_json(w.path("day.json"), {
                "day": {"money": 200, "earned": 200},
                "gather": {"hold": individuals(["ca_loc", "bong_sung", "bong_sung"]), "time_left_ticks": 1, "random_fish": False},
                "quan": {"time_left_ticks": 1},
            })
            inputs = write_json(w.path("inputs.json"), frames(
                {"tick": 2, "pause": True, "buy": "hp"},
                {"tick": 3, "pause": False, "shop_done": True},
                {"tick": 4, "pause": True, "buy": "oxygen"},
                {"tick": 5, "pause": False, "shop_done": False},
                {"tick": 6, "shop_done": True},
                {"tick": 7, "shop_done": False},
                {"tick": 9, "shop_done": True},
            ))
            files = [w.path(f"out{i}.jsonl") for i in (1, 2)]
            for out in files:
                code, err = run_headless("--mode", "day", "--days", "2", "--seed", "42", "--ticks", "20",
                                         "--scenario", scenario, "--inputs", inputs, "--snapshot-every", "1", "--out", out)
                self.assertEqual(code, 0, err)
            self.assertEqual(Path(files[0]).read_bytes(), Path(files[1]).read_bytes())
            rows = read_jsonl(files[0])
            self.assertEqual([r["name"] for r in rows[:3]], ["day_start", "day_plan", "phase_start"])
            snap = {r["tick"]: r for r in snapshots(rows)}
            self.assertEqual((snap[1]["phase"], snap[1]["phase_tick"], item_counts(snap[1]["stock"])),
                             ("quan", 0, {"bong_sung": 2, "ca_loc": 1}))
            self.assertEqual(snap[1]["stock"], events(rows, "gather_end")[0]["data"]["inventory"]["items"])
            self.assertEqual((snap[2]["phase"], snap[2]["phase_tick"]), ("shop", 0))
            self.assertEqual((snap[3]["state"], snap[3]["sim_tick"], snap[4]["time_left_ticks"]),
                             ("paused", 2, snap[2]["time_left_ticks"]))
            self.assertEqual([r["name"] for r in events(rows) if r["tick"] == 5], ["resumed", "bought"])
            self.assertEqual((snap[5]["money"], snap[5]["earned"], snap[5]["upgrades"], snap[5]["active_upgrades"]),
                             (0, 200, {"oxygen": 1}, {}))
            self.assertEqual((snap[7]["day"], snap[7]["phase_tick"], snap[7]["player"]["oxygen_ticks"]), (2, 0, 2700))
            self.assertEqual(snap[7]["active_upgrades"], {"oxygen": 1})
            self.assertEqual((rows[-1]["reason"], rows[-1]["days_completed"], rows[-1]["sim_tick"]),
                             ("days_complete", 2, 8))

    def test_shop_buy_at_last_tick_precedes_done(self):
        with Workdir() as w:
            scenario = write_json(w.path("day.json"), {
                "day": {"money": 249, "earned": 249},
                "gather": {"time_left_ticks": 1, "random_fish": False},
                "quan": {"time_left_ticks": 1},
            })
            inputs = write_json(w.path("inputs.json"), frames(
                {"tick": 2, "buy": "hp"}, {"tick": 3, "buy": "other"},
                {"tick": 601, "buy": "oxygen", "shop_done": True},
            ))
            out = w.path("out.jsonl")
            code, err = run_headless("--mode", "day", "--seed", "1", "--ticks", "603",
                                     "--scenario", scenario, "--inputs", inputs, "--out", out)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            self.assertEqual([r["data"]["reason"] for r in events(rows, "buy_failed")], ["funds", "unknown"])
            self.assertEqual([(r["name"], r["tick"]) for r in events(rows)[-2:]], [("bought", 602), ("shop_end", 602)])
            self.assertEqual((events(rows, "shop_end")[0]["data"]["reason"], rows[-1]["money"]), ("done", 49))

    def test_invalid_day_arguments_and_scenarios_fail_before_output(self):
        with Workdir() as w:
            out = w.path("out.jsonl")
            scenario = write_json(w.path("invalid.json"), {"quan": {"stock": []}})
            for args in (("--mode", "day", "--days", "0"), ("--mode", "gather", "--days", "1"),
                         ("--mode", "day", "--scenario", scenario)):
                with self.subTest(args=args):
                    self.assertEqual(run_headless(*args, "--seed", "1", "--ticks", "0", "--out", out)[0], 2)
                    self.assertFalse(os.path.exists(out))

    def test_live_presentation_waits_before_advancing_quan_and_shop(self):
        tuning = load_contract()["tuning"]
        fixture = {"gather": {"time_left_ticks": 1, "hold": individuals(["ca_loc"], fresh=30)},
                   "quan": {"time_left_ticks": 1}}
        game = LiveGame("day", tuning, fixture, 1)

        def state():
            return json.loads(game.state_json())

        def interact():
            game.set_input({"interact": True})
            game.set_input({"interact": False})
            game._tick_once()

        game._tick_once()
        self.assertFalse(state()["ui"]["started"])
        game.restart()
        self.assertEqual(state()["ui"]["screen"], "day_intro")
        interact()
        game._tick_once()
        evening = state()
        self.assertEqual((evening["ui"]["screen"], evening["phase_tick"]), ("evening_intro", 0))
        handoff, = [event for event in evening["events"] if event["name"] == "gather_end"]
        self.assertEqual(evening["stock"], handoff["data"]["inventory"]["items"])
        self.assertEqual(evening["meta"]["spoiled_ids"], ["I1"])
        game._tick_once()
        self.assertEqual(state()["phase_tick"], 0)
        interact()
        game._tick_once()
        self.assertEqual((state()["ui"]["screen"], state()["time_left_ticks"]), ("day_result", 600))
        self.assertEqual(state()["ui"]["result"]["shift_earned"], 0)
        interact()
        game.set_input({"pause": True})
        game._tick_once()
        self.assertEqual((state()["state"], state()["time_left_ticks"]), ("paused", 600))
        self.assertEqual(state()["stock"][0]["id"], "I1")
