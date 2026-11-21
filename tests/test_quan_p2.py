"""TICKET-02: quán độc lập và đầu nối với kế hoạch ngày."""

import json
import unittest

from helpers import Workdir, events, frames, individuals, item_counts, read_jsonl, run_headless, snapshots, write_json

from chonoi.contract import load_contract
from chonoi.day_plan import normalize_day_plan
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim


IDLE = InputState((0, 0), set(), set())
PRESS = InputState((0, 0), {"interact"}, {"interact"})
RIGHT = InputState((1, 0), set(), set())


class QuanPhase2(unittest.TestCase):
    def test_standard_restaurant_and_daily_ingredient_totals(self):
        contract = load_contract()
        tuning = contract["tuning"]
        self.assertEqual(contract["contract_version"], "1.3")
        self.assertEqual({s["id"]: s["pos"] for s in tuning["quan"]["stoves"]}, {"B1": [2, 8], "B2": [5, 8]})
        self.assertEqual({t["id"]: t["pos"] for t in tuning["quan"]["tables"]},
                         {"T1": [9, 2], "T2": [13, 2], "T3": [9, 6], "T4": [13, 6]})
        self.assertEqual(len(tuning["menu"]), 6)
        self.assertEqual(tuning["menu"]["canh_chua_ca_loc"],
                         {"recipe": {"ca_loc": 1, "bong_dien_dien": 1}, "cook_s": 8, "price": 90})
        self.assertEqual(tuning["menu"]["ca_keo_nuong"], {"recipe": {"ca_keo": 2}, "cook_s": 6, "price": 70})
        self.assertEqual(tuning["menu"]["lau_mam"], {
            "recipe": {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1}, "cook_s": 12, "price": 200,
        })
        self.assertEqual([p["day"] for p in tuning["day_plan"]], [1, 2, 3, 4, 5])
        self.assertEqual([sum(p["ingredients"].values()) for p in tuning["day_plan"]], [9, 10, 12, 9, 10])
        self.assertEqual(normalize_day_plan({"day": 5, "dishes": {"ca_keo_nuong": 2}}, tuning["menu"])["ingredients"],
                         {"ca_keo": 4})
        with self.assertRaises(BadInput):
            normalize_day_plan({"day": 5, "dishes": {"ca_keo_nuong": 2}, "ingredients": {"ca_keo": 3}}, tuning["menu"])

    def test_two_stoves_cook_separate_orders_in_parallel(self):
        tuning = load_contract()["tuning"]
        scenario = {"player": {"pos": [2, 8]}, "stock": individuals(["ca_keo"] * 4), "random_customers": False,
                    "customers": [{"id": f"C{i}", "table_id": f"T{i}", "dish_id": "ca_keo_nuong"} for i in (1, 2)]}
        sim = QuanSim(tuning, scenario, Streams(2), IdAllocator())
        (name, data), = sim.step(PRESS)
        self.assertEqual((name, data["stove_id"], data["order_id"], data["dish_id"], data["base_price"]),
                         ("cook_started", "B1", "C1", "ca_keo_nuong", 69))
        self.assertEqual(item_counts(data["items"]), {"ca_keo": 2})
        for _ in range(46):
            sim.step(RIGHT)
        self.assertEqual(sim.step(PRESS)[0][1]["stove_id"], "B2")
        snap = sim.snapshot()
        self.assertEqual([(s["state"], s["dish"]["order_id"]) for s in snap["stoves"]],
                         [("cooking", "C1"), ("cooking", "C2")])
        self.assertEqual(snap["stock"], [])

    def test_standalone_fills_four_tables_in_order_with_new_dish(self):
        with Workdir() as w:
            inventory = write_json(w.path("inventory.json"), {"items": individuals(["ca_keo"] * 8)})
            out = w.path("quan.jsonl")
            status, stderr = run_headless("--mode", "quan", "--seed", "1", "--inventory", inventory,
                                          "--ticks", "3720", "--out", out)
            self.assertEqual(status, 0, stderr)
            rows = read_jsonl(out)
            arrivals = events(rows, "customer_arrived")
            self.assertEqual([(a["tick"], a["data"]["table_id"], a["data"]["dish_id"]) for a in arrivals],
                             [(120 + 900 * i, f"T{i % 4 + 1}", "ca_keo_nuong") for i in range(5)])
            self.assertEqual(events(rows, "no_dish"), [])
            self.assertEqual([(r["tick"], r["name"]) for r in events(rows)[-2:]],
                             [(3720, "customer_left"), (3720, "customer_arrived")])

    def test_day_uses_plan_as_filter_not_serving_cap(self):
        tuning = load_contract()["tuning"]
        inventory = individuals(["ca_keo"] * 4 + ["ca_loc"] * 3)
        plan = {"day": 3, "dishes": {"ca_keo_nuong": 1}}
        eating = {"id": "C1", "table_id": "T1", "dish_id": "ca_keo_nuong", "state": "eating",
                  "order_status": "served", "eat_ticks_left": 1, "base_price": 70, "tip": 0}
        sim = QuanSim(tuning, {"customers": [eating]}, Streams(3), IdAllocator(), inventory, day_plan=plan)
        paid, = sim.step(IDLE)
        self.assertEqual((paid[0], sim.shift_earned), ("paid", 70))
        arrivals = []
        for _ in range(1919):
            arrivals.extend(sim.step(IDLE))
        self.assertEqual(arrivals, [
            ("customer_arrived", {"order_id": "C2", "table_id": "T1", "dish_id": "ca_keo_nuong"}),
            ("customer_arrived", {"order_id": "C3", "table_id": "T2", "dish_id": "ca_keo_nuong"}),
            ("no_dish", {}),
        ])
        with self.assertRaises(BadInput):
            customer = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}
            QuanSim(tuning, {"customers": [customer]}, Streams(3), IdAllocator(), inventory, day_plan=plan)

    def test_day_keeps_campaign_totals_separate_from_shift_earnings(self):
        tuning = load_contract()["tuning"]
        customer = {"id": "C1", "table_id": "T1", "dish_id": "lau_mam", "state": "eating",
                    "order_status": "served", "eat_ticks_left": 2, "base_price": 200, "tip": 40}
        scenario = {"customers": [customer], "time_left_ticks": 1}
        sim = QuanSim(tuning, scenario, Streams(3), IdAllocator(), [], day_plan=tuning["day_plan"][3],
                      money=50, earned=250, reputation=4.9)
        self.assertEqual(sim.shift_earned, 0)
        paid, end = sim.step(IDLE)
        self.assertEqual(paid[1]["reason"], "closing")
        self.assertEqual(end, ("quan_end", {"reason": "time", "money": 290, "earned": 490,
                                           "shift_earned": 240, "reputation": 5.0}))

    def test_two_process_inventory_handoff_includes_all_six_ingredients(self):
        with Workdir() as w:
            ingredients = {"ca_loc": 1, "ca_linh": 2, "ca_keo": 1, "bong_dien_dien": 1, "bong_sung": 2, "keo_neo": 1}
            hold = individuals(kind for kind, amount in ingredients.items() for _ in range(amount))
            dock = write_json(w.path("dock.json"), {"gather": {"hold": hold}})
            inputs = write_json(w.path("dock-inputs.json"), frames({"tick": 0, "interact": True}))
            inventory, gather_out, quan_out = (w.path(f) for f in ("stock.json", "gather.jsonl", "quan.jsonl"))
            code, err = run_headless("--mode", "gather", "--seed", "42", "--scenario", dock, "--inputs", inputs,
                                     "--ticks", "1", "--out", gather_out, "--inventory-out", inventory)
            self.assertEqual(code, 0, err)
            with open(inventory, encoding="utf-8") as f:
                saved = json.load(f)["items"]
            self.assertEqual(item_counts(saved), ingredients)
            code, err = run_headless("--mode", "quan", "--seed", "42", "--inventory", inventory,
                                     "--ticks", "0", "--out", quan_out)
            self.assertEqual(code, 0, err)
            self.assertEqual(snapshots(read_jsonl(quan_out))[0]["stock"], saved)
