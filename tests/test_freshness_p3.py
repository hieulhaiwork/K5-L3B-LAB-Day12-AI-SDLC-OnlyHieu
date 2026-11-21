"""Biên độ tươi, giữ chỗ và bàn giao kho v1.2."""

import json
import os
import unittest
from decimal import Decimal
from fractions import Fraction

from chonoi.contract import load_contract
from chonoi.inputs import InputState
from chonoi.inventory import read_inventory
from chonoi.runner import Session
from helpers import Workdir, events, frames, individuals, read_jsonl, run_headless, snapshots, write_json


IDLE = InputState((0, 0), {}, set())
COOK = InputState((0, 0), {}, {"interact"})


class FreshnessPhase3(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def test_gather_spoils_once_in_id_order_and_freezes_while_paused(self):
        hold = [dict(individuals(["ca_linh"], fresh=30)[0], id="I10"),
                dict(individuals(["ca_loc"], fresh=30)[0], id="I2")]
        session = Session("gather", self.tuning, {"hold": hold, "random_fish": False, "monsters": []}, 1)
        pause = InputState((0, 0), {}, {"pause"})
        self.assertEqual([row["name"] for row in session.step(pause)], ["paused"])
        self.assertEqual(session.step(IDLE), [])
        frozen = session.snapshot()
        self.assertEqual((frozen["sim_tick"], frozen["state"], frozen["hold"][0]["fresh"]), (0, "paused", 30))
        rows = session.step(pause)
        self.assertEqual([(row["tick"], row["name"], row["data"]) for row in rows], [
            (3, "resumed", {}),
            (3, "spoiled", {"item_id": "I2", "kind": "ca_loc", "location": "hold"}),
            (3, "spoiled", {"item_id": "I10", "kind": "ca_linh", "location": "hold"}),
        ])
        self.assertEqual(session.snapshot()["hold"][0]["fresh"], 30 - Fraction(1, 120))
        self.assertEqual(session.step(IDLE), [])

    def test_reassigns_once_in_order_priority_before_interact(self):
        stock = [dict(item, fresh=fresh) for item, fresh in zip(individuals(["ca_loc"] * 3), [30, 30, 80])]
        scenario = {"stock": stock, "player": {"pos": [2, 8]}, "random_customers": False,
                    "customers": [self.order("C1", "T2", order_tick=8, reserved=["I1"]),
                                  self.order("C9", "T1", order_tick=5, reserved=["I2"])]}
        session = Session("quan", self.tuning, scenario, 1)
        spoiled1, spoiled2, cook = session.step(COOK)
        self.assertEqual([row["name"] for row in (spoiled1, spoiled2, cook)], ["spoiled", "spoiled", "cook_started"])
        self.assertEqual([row["data"]["item_id"] for row in (spoiled1, spoiled2)], ["I1", "I2"])
        self.assertEqual(cook["data"]["order_id"], "C9")
        self.assertEqual(cook["data"]["items"], [{"id": "I3", "kind": "ca_loc", "fresh": 80 - Fraction(1, 240)}])
        self.assertEqual(cook["data"]["base_price"], 47)
        self.assertEqual(session.snapshot()["customers"][0]["order_status"], "unfulfillable")
        self.assertEqual([item["id"] for item in session.snapshot()["stock"]], ["I1", "I2"])

    def test_explicit_reservations_and_freshest_id_tiebreak(self):
        stock = [{"id": ident, "kind": "ca_loc", "fresh": fresh}
                 for ident, fresh in (("I10", 90), ("I2", 90), ("I1", 85), ("I3", 95))]
        scenario = {"stock": stock, "customers": [self.order("C1", "T1"), self.order("C2", "T2", reserved=["I3"])]}
        session = Session("quan", self.tuning, scenario, 1)
        self.assertEqual([order["reserved"] for order in session.snapshot()["customers"]], [["I2"], ["I3"]])

    def test_monster_hit_and_faint_drop_whole_items_in_lifo_order(self):
        hold = [dict(item, id=ident) for item, ident in zip(individuals(["ca_loc"] * 4), ["I8", "I2", "I3", "I4"])]
        monster = {"id": "M4", "kind": "ca_sau", "pos": [20, 12], "waypoints": [[20, 12], [24, 12]]}
        scenario = {"hold": hold, "player": {"pos": [20, 12], "hp": 1}, "monsters": [monster], "random_fish": False}
        session = Session("gather", self.tuning, scenario, 1)
        hit, faint, end = session.step(IDLE)
        self.assertEqual([row["name"] for row in (hit, faint, end)], ["monster_hit", "faint", "gather_end"])
        self.assertEqual([item["id"] for item in hit["data"]["lost"]], ["I4", "I3"])
        self.assertEqual([item["id"] for item in faint["data"]["lost"]], ["I2", "I8"])
        self.assertEqual(hit["data"]["lost"][0]["fresh"], 100 - Fraction(1, 120))
        self.assertEqual(end["data"]["inventory"], {"items": []})

    def test_floor_is_applied_after_decay_without_rounding_freshness(self):
        for fresh, expected in ((Decimal("50.00416"), 29), (Decimal("50.00417"), 30)):
            with self.subTest(fresh=fresh):
                session = Session("quan", self.tuning, {"stock": individuals(["ca_loc"], fresh),
                    "player": {"pos": [2, 8]}, "customers": [self.order("C1", "T1")]}, 1)
                cooked, = session.step(COOK)
                self.assertEqual(cooked["data"]["base_price"], expected)

    def test_precise_file_handoff_and_legacy_version_selection(self):
        with Workdir() as work:
            scenario = write_json(work.path("morning.json"), {"gather": {"hold": individuals(["ca_linh"], fresh=30.00834),
                                                                         "monsters": [], "random_fish": False}})
            inputs = write_json(work.path("input.json"), frames({"tick": 0, "interact": True}))
            bag, morning, evening = (work.path(name) for name in ("bag.json", "morning.jsonl", "evening.jsonl"))
            self.assertEqual(run_headless("--mode", "gather", "--seed", "3", "--ticks", "1", "--out", morning,
                                          "--inputs", inputs, "--scenario", scenario, "--inventory-out", bag)[0], 0)
            self.assertEqual(run_headless("--mode", "quan", "--seed", "3", "--ticks", "0", "--out", evening,
                                          "--inventory", bag)[0], 0)
            with open(bag, encoding="utf-8") as f:
                saved = json.load(f, parse_float=Decimal)["items"]
            with open(evening, encoding="utf-8") as f:
                stocked = json.loads(next(f), parse_float=Decimal)["stock"]
            self.assertEqual(stocked, saved)
            self.assertGreater(saved[0]["fresh"], 30)
            self.assertEqual(len(events(read_jsonl(morning), "spoiled")), 0)
            old = write_json(work.path("old-counts.json"), {"items": {"ca_loc": 1}})
            self.assertEqual(read_inventory(old, contract_version="1.1"), {"ca_loc": 1})
            bad_out = work.path("bad.jsonl")
            self.assertEqual(run_headless("--mode", "quan", "--seed", "3", "--ticks", "0", "--out", bad_out,
                                          "--inventory", old)[0], 2)
            self.assertFalse(os.path.exists(bad_out))

    def test_rejects_duplicate_or_spoiled_reservations_before_output(self):
        with Workdir() as work:
            for stock, orders in (
                (individuals(["ca_loc"]), [self.order("C1", "T1", reserved=["I1"]), self.order("C2", "T2", reserved=["I1"])]),
                (individuals(["ca_loc"], fresh=29.999), [self.order("C1", "T1", reserved=["I1"])]),
                (individuals(["ca_loc"]) * 2, []),
            ):
                with self.subTest(stock=stock, orders=orders):
                    scenario = write_json(work.path("scenario.json"), {"quan": {"stock": stock, "customers": orders}})
                    out = work.path("out.jsonl")
                    code, _ = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--scenario", scenario, "--out", out)
                    self.assertEqual(code, 2)
                    self.assertFalse(os.path.exists(out))

    def test_rejects_invalid_fresh_numbers_in_file_and_scenario(self):
        with Workdir() as work:
            source, out = work.path("input.json"), work.path("out.jsonl")
            for fresh in ("-0.001", "100.001", "NaN", "1e1000", "1e99999999999999999999"):
                item = '{"id":"I1","kind":"ca_linh","fresh":' + fresh + "}"
                for mode, flag, content in (
                    ("gather", "--scenario", '{"gather":{"hold":[' + item + "]}}"),
                    ("quan", "--inventory", '{"items":[' + item + "]}"),
                ):
                    with self.subTest(fresh=fresh, flag=flag):
                        with open(source, "w", encoding="utf-8") as f:
                            f.write(content)
                        code, err = run_headless("--mode", mode, "--seed", "17", "--ticks", "0", "--out", out,
                                                 flag, source)
                        self.assertEqual(code, 2, err)
                        self.assertNotIn("Traceback", err)
                        self.assertFalse(os.path.exists(out))

    def test_day_handoff_keeps_freshness_and_reissues_fixture_ids_next_day(self):
        with Workdir() as work:
            scenario = write_json(work.path("scenario.json"), {"day": {"money": 200, "earned": 200,
                "day_plan": {"2": {"dishes": {"ca_loc_nuong_trui": 4}}}},
                "gather": {"time_left_ticks": 1, "random_fish": False, "monsters": [],
                           "hold": [{"id": "I7", "kind": "ca_loc", "fresh": 100}]},
                "quan": {"time_left_ticks": 2, "random_customers": False}})
            inputs = write_json(work.path("inputs.json"), frames({"tick": 3, "buy": "oxygen", "shop_done": True},
                                                               {"tick": 4, "shop_done": False},
                                                               {"tick": 7, "shop_done": True}))
            out = work.path("day.jsonl")
            code, err = run_headless("--mode", "day", "--days", "2", "--seed", "1", "--ticks", "12", "--out", out,
                                     "--scenario", scenario, "--inputs", inputs)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            self.assertEqual([row["name"] for row in rows[:3]], ["day_start", "day_plan", "phase_start"])
            snap = {s["tick"]: s for s in snapshots(rows)}
            self.assertEqual((snap[1]["phase"], snap[1]["phase_tick"]), ("quan", 0))
            self.assertEqual(snap[1]["stock"], events(rows, "gather_end")[0]["data"]["inventory"]["items"])
            self.assertAlmostEqual(snap[3]["stock"][0]["fresh"], 100 - 1 / 120 - 2 / 240)
            self.assertEqual((snap[4]["day"], snap[4]["hold"][0]["id"], snap[4]["hold"][0]["fresh"]), (2, "I8", 100))
            self.assertEqual(snap[4]["day_plan"]["ingredients"], {"ca_loc": 4})
            self.assertEqual((snap[4]["active_upgrades"], snap[4]["player"]["oxygen_max_ticks"]), ({"oxygen": 1}, 2700))
            self.assertEqual((rows[-1]["reason"], rows[-1]["days_completed"], rows[-1]["money"]), ("days_complete", 2, 0))

    def test_day_fixture_uses_active_gather_upgrade_limits(self):
        with Workdir() as work:
            player = {"hp": 4, "oxygen_ticks": 2400}
            fixture = {"day": {"upgrades": {"hp": 1, "oxygen": 1}}, "gather": {"player": player}}
            scenario = write_json(work.path("scenario.json"), fixture)
            out = work.path("day.jsonl")
            args = ("--mode", "day", "--seed", "1", "--ticks", "0", "--scenario", scenario, "--out", out)
            code, err = run_headless(*args)
            self.assertEqual(code, 0, err)
            saved = snapshots(read_jsonl(out))[0]["player"]
            self.assertEqual((saved["hp"], saved["hp_max"], saved["oxygen_ticks"], saved["oxygen_max_ticks"]),
                             (4, 4, 2400, 2700))
            os.remove(out)
            fixture["day"]["upgrades"] = {"hp": 1}
            write_json(scenario, fixture)
            code, _ = run_headless(*args)
            self.assertEqual(code, 2)
            self.assertFalse(os.path.exists(out))

    def test_day_from_empty_hold_to_revenue_with_default_map(self):
        with Workdir() as work:
            inputs = write_json(work.path("controls.json"), frames(
                {"tick": 0, "move": [1, 0]},
                {"tick": 630, "move": [0, 0], "interact": True},
                {"tick": 631, "move": [1, 0], "interact": False},
                {"tick": 871, "move": [0, 0], "interact": True},
                {"tick": 872, "move": [-1, 0], "interact": False},
                {"tick": 1742, "move": [0, 0], "interact": True},
                {"tick": 1743, "move": [-1, 0.5], "interact": False},
                {"tick": 1843, "move": [0, 0]},
                {"tick": 1863, "interact": True},
                {"tick": 1864, "interact": False},
                {"tick": 2103, "interact": True},
                {"tick": 2104, "move": [1, -6 / 7], "interact": False},
                {"tick": 2242, "move": [0, 0]},
                {"tick": 2243, "interact": True},
                {"tick": 12543, "shop_done": True},
            ))
            out = work.path("day.jsonl")
            code, err = run_headless("--mode", "day", "--days", "1", "--seed", "1", "--ticks", "13000",
                                     "--inputs", inputs, "--out", out)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            sampled = snapshots(rows)
            self.assertEqual(sampled[0]["hold"], [])
            self.assertEqual([row["data"]["node_id"] for row in events(rows, "gather")], ["N3", "N4"])
            handoff, = events(rows, "gather_end")
            opening = next(row for row in sampled if row["phase"] == "quan")
            self.assertEqual((handoff["tick"], opening["tick"], opening["phase_tick"]), (1743, 1743, 0))
            self.assertEqual(opening["stock"], handoff["data"]["inventory"]["items"])
            cooked, = events(rows, "cook_started")
            self.assertEqual((cooked["data"]["dish_id"], cooked["data"]["base_price"]), ("goi_bong_sung", 36))
            self.assertEqual([item["id"] for item in cooked["data"]["items"]], ["I1", "I2"])
            paid, = events(rows, "paid")
            self.assertEqual((paid["tick"], paid["data"]["tip"], paid["data"]["amount"]), (2844, 7, 43))
            self.assertEqual((rows[-1]["reason"], rows[-1]["ticks"], rows[-1]["money"]), ("days_complete", 12544, 43))

    @staticmethod
    def order(ident, table, **fields):
        return dict(id=ident, table_id=table, dish_id="ca_loc_nuong_trui", **fields)
