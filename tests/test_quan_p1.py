"""Regression tests cho vòng đời đơn quán Phase 1."""

import os
import unittest

from helpers import Workdir, events, frames, individuals, item_counts, read_jsonl, run_headless, snapshots, write_json

from chonoi.contract import load_contract
from chonoi.inputs import InputState
from chonoi.runner import Session


DISH = "ca_loc_nuong_trui"
SOUP = "lau_ca_linh_dien_dien"
IDLE = InputState((0, 0), set(), set())
PRESS = InputState((0, 0), {"interact"}, {"interact"})


def order(customer_id="C1", table_id="T1", **fields):
    return dict({"id": customer_id, "table_id": table_id, "dish_id": DISH}, **fields)


def meal(order_id="C1", base_price=60):
    return {"order_id": order_id, "dish_id": DISH, "base_price": base_price}


class QuanPhase1(unittest.TestCase):
    def test_headless_shift_from_inventory_to_payment_is_deterministic(self):
        with Workdir() as w:
            inventory = write_json(w.path("inventory.json"), {"items": individuals(["ca_loc"])})
            scenario = write_json(w.path("scenario.json"), {"quan": {"player": {"pos": [2, 8]},
                                                                     "time_left_ticks": 1221}})
            inputs = write_json(w.path("inputs.json"), frames(
                {"tick": 120, "interact": True},
                {"tick": 121, "interact": False},
                {"tick": 480, "interact": True},
                {"tick": 481, "interact": False, "move": [1, -6 / 7]},
                {"tick": 619, "move": [0, 0]},
                {"tick": 620, "interact": True},
            ))
            outputs = [w.path("first.jsonl"), w.path("second.jsonl")]
            for out in outputs:
                code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "1300", "--out", out,
                                         "--inventory", inventory, "--scenario", scenario, "--inputs", inputs)
                self.assertEqual(code, 0, err)
            with open(outputs[0], "rb") as first, open(outputs[1], "rb") as second:
                self.assertEqual(first.read(), second.read())
            rows = read_jsonl(outputs[0])
            self.assertEqual([(r["tick"], r["name"]) for r in events(rows)], [
                (120, "customer_arrived"), (121, "cook_started"), (481, "dish_ready"), (481, "dish_picked"),
                (621, "served"), (1020, "no_dish"), (1221, "paid"), (1221, "quan_end"),
            ])
            order_fields = {"order_id": "C1", "table_id": "T1", "dish_id": DISH}
            stove_fields = {"stove_id": "B1", "order_id": "C1", "dish_id": DISH}
            self.assertEqual([r["data"] for r in events(rows)], [
                order_fields,
                dict(stove_fields, items=individuals(["ca_loc"], fresh=100 - 121 / 240), base_price=59),
                stove_fields,
                stove_fields,
                dict(order_fields, patience_ticks_left=3099, base_price=59, tip=11),
                {},  # Bàn trống thứ hai của preset P2 xét lượt khách khi T1 vẫn đang có khách.
                {"order_id": "C1", "table_id": "T1", "base_price": 59, "tip": 11,
                 "amount": 70, "reason": "finished_eating"},
                {"reason": "time", "money": 70, "earned": 70, "shift_earned": 70, "reputation": 3.2},
            ])
            snaps = {r["tick"]: r for r in snapshots(rows)}
            self.assertEqual(snaps[120]["customers"][0]["reserved"], ["I1"])
            self.assertEqual(snaps[120]["customers"][0]["order_tick"], 120)
            self.assertEqual(snaps[120]["stock"], individuals(["ca_loc"], fresh=99.5))
            self.assertEqual(snaps[130]["stock"], [])
            self.assertEqual(snaps[130]["stoves"][0]["dish"], meal(base_price=59))
            self.assertEqual(snaps[130]["customers"][0]["order_status"], "assigned")
            self.assertEqual(snaps[130]["customers"][0]["state"], "waiting")
            self.assertEqual(snaps[490]["hand"], meal(base_price=59))
            self.assertEqual(snaps[1220]["money"], 0)
            self.assertEqual(snaps[1221]["customers"], [])
            self.assertEqual(snaps[1221]["tables"][0]["customer_id"], None)
            self.assertEqual((rows[-1]["money"], rows[-1]["reputation"], rows[-1]["score"]), (70, 3.2, 370))

    def test_reserved_stock_is_reused_after_waiting_customer_leaves(self):
        tuning = load_contract()["tuning"]
        tuning["quan"].update(first_customer_tick=1, customer_interval_s=0.1)
        scenario = {"stock": individuals(["ca_loc"]), "customers": [order("C9", patience_ticks_left=7)]}
        session = Session("quan", tuning, scenario, seed=1)
        self.assertEqual([(r["name"], r["data"]) for r in session.step(IDLE)], [("no_dish", {})])
        for _ in range(5):
            self.assertEqual(session.step(IDLE), [])
        left, arrived = session.step(IDLE)
        self.assertEqual(left["name"], "customer_left")
        self.assertEqual(left["data"], {"order_id": "C9", "table_id": "T1", "reason": "patience", "reputation": 2.5})
        self.assertEqual(arrived["name"], "customer_arrived")
        customer = session.snapshot()["customers"][0]
        self.assertEqual((customer["id"], customer["table_id"], customer["reserved"]), ("C10", "T1", ["I1"]))
        self.assertEqual(session.snapshot()["reputation"], 2.5)

    def test_departing_assigned_customer_frees_stove_or_hand(self):
        tuning = load_contract()["tuning"]
        for carrier in ({"stoves": [{"id": "B1", "state": "cooking", "dish": meal(), "cook_ticks_left": 3}]},
                        {"hand": meal()}):
            with self.subTest(carrier=carrier):
                scenario = dict(carrier, customers=[order(order_status="assigned", patience_ticks_left=1)],
                                random_customers=False, reputation=0.1)
                session = Session("quan", tuning, scenario, seed=1)
                rows = session.step(IDLE)
                self.assertEqual([row["name"] for row in rows], ["customer_left"])
                snap = session.snapshot()
                self.assertEqual(snap["stoves"][0]["state"], "idle")
                self.assertIsNone(snap["hand"])
                self.assertEqual(snap["customers"], [])
                self.assertEqual(snap["stock"], [])
                self.assertEqual(snap["reputation"], 0)

    def test_stove_wins_interaction_tie_and_late_service_has_no_tip(self):
        tuning = load_contract()["tuning"]
        scenario = {"player": {"pos": [9, 2]}, "stoves": [{"id": "B1", "pos": [9, 2], "state": "cooking",
                                                          "dish": meal(), "cook_ticks_left": 1}],
                    "customers": [order(order_status="assigned", patience_ticks_left=20)], "random_customers": False}
        session = Session("quan", tuning, scenario, seed=1)
        self.assertEqual([r["name"] for r in session.step(IDLE)], ["dish_ready"])
        self.assertEqual(session.snapshot()["stoves"][0]["ready_ticks"], 0)
        self.assertEqual(session.step(IDLE), [])
        self.assertEqual(session.snapshot()["stoves"][0]["ready_ticks"], 1)
        self.assertEqual([r["name"] for r in session.step(PRESS)], ["dish_picked"])
        self.assertEqual(session.step(PRESS), [])

        scenario = {"player": {"pos": [9, 2]}, "hand": meal(), "random_customers": False,
                    "customers": [order(order_status="assigned", patience_ticks_left=1)]}
        session = Session("quan", tuning, scenario, seed=1)
        served, = session.step(PRESS)
        self.assertEqual((served["name"], served["data"]["patience_ticks_left"], served["data"]["tip"]),
                         ("served", 0, 0))
        for _ in range(round(tuning["quan"]["eat_s"] * tuning["tick_hz"])):
            last = session.step(IDLE)
        self.assertEqual(last[0]["name"], "paid")
        self.assertEqual((session.snapshot()["money"], session.snapshot()["reputation"]), (60, 3.0))

    def test_final_tick_service_uses_locked_price_and_pays_on_closing(self):
        with Workdir() as w:
            fixture = write_json(w.path("scenario.json"), {"quan": {
                "player": {"pos": [9, 2], "vel": [0, 0]}, "hand": meal(base_price=63), "time_left_ticks": 1,
                "customers": [order(order_status="assigned", patience_ticks_left=1801)],
            }})
            inputs = write_json(w.path("inputs.json"), frames({"tick": 0, "interact": True}))
            out = w.path("out.jsonl")
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "1", "--out", out,
                                     "--scenario", fixture, "--inputs", inputs)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            self.assertEqual(snapshots(rows)[0]["player"], {"pos": [9, 2], "vel": [0, 0]})
            self.assertEqual(snapshots(rows)[0]["hand"], meal(base_price=63))
            served, paid, end = events(rows)
            self.assertEqual([event["tick"] for event in (served, paid, end)], [1, 1, 1])
            self.assertEqual(served["data"], {"order_id": "C1", "table_id": "T1", "dish_id": DISH,
                                              "patience_ticks_left": 1800, "base_price": 63, "tip": 12})
            self.assertEqual(paid["data"], {"order_id": "C1", "table_id": "T1", "base_price": 63,
                                            "tip": 12, "amount": 75, "reason": "closing"})
            self.assertEqual((end["name"], rows[-1]["reason"], rows[-1]["score"]), ("quan_end", "time", 375))

    def test_closing_releases_waiting_orders_and_skips_scheduled_arrival(self):
        tuning = load_contract()["tuning"]
        tuning["quan"].update(first_customer_tick=1)
        scenario = {"time_left_ticks": 1, "stock": individuals(["ca_loc"]), "customers": [order(patience_ticks_left=1)]}
        session = Session("quan", tuning, scenario, seed=1)
        left, end = session.step(IDLE)
        self.assertEqual(left["name"], "customer_left")
        self.assertEqual(left["data"], {"order_id": "C1", "table_id": "T1", "reason": "closing", "reputation": 3.0})
        self.assertEqual(end["name"], "quan_end")
        self.assertEqual(session.snapshot()["customers"], [])
        self.assertEqual(item_counts(session.snapshot()["stock"]), {"ca_loc": 1})

    def test_stove_uses_order_tick_then_table_id_and_lists_items_sorted(self):
        tuning = load_contract()["tuning"]
        scenario = {"player": {"pos": [2, 8]}, "stock": individuals(["ca_loc"] * 2 + ["ca_linh"] * 3 + ["bong_dien_dien"]),
                    "customers": [order("C1", "T1", order_tick=10), order("C2", "T4", order_tick=2),
                                  order("C9", "T2", order_tick=2, dish_id=SOUP)]}
        session = Session("quan", tuning, scenario, seed=1)
        cooked, = session.step(PRESS)
        self.assertEqual(cooked["name"], "cook_started")
        data = cooked["data"]
        self.assertEqual((data["order_id"], data["stove_id"], data["dish_id"], data["base_price"]),
                         ("C9", "B1", SOUP, 119))
        self.assertEqual([item["id"] for item in data["items"]], ["I6", "I3", "I4", "I5"])
        self.assertEqual(item_counts(session.snapshot()["stock"]), {"ca_loc": 2})

    def test_unfulfillable_order_is_skipped_at_idle_stove(self):
        tuning = load_contract()["tuning"]
        scenario = {"player": {"pos": [2, 8]}, "stock": individuals(["ca_loc"]), "random_customers": False,
                    "customers": [order(order_status="unfulfillable", patience_ticks_left=2)]}
        session = Session("quan", tuning, scenario, seed=1)
        self.assertEqual(session.step(PRESS), [])
        self.assertEqual(session.snapshot()["customers"][0]["reserved"], [])
        self.assertEqual(item_counts(session.snapshot()["stock"]), {"ca_loc": 1})
        self.assertEqual(session.step(IDLE)[0]["name"], "customer_left")

    def test_contradictory_fixtures_exit_2_before_writing(self):
        bad_scenarios = (
            {"customers": [order()]},
            {"customers": [order(order_status="assigned")]},
            {"customers": [order(state="eating", order_status="served", eat_ticks_left=3, base_price=60)]},
            {"customers": [order(order_status="assigned")], "hand": meal(),
             "stoves": [{"id": "B1", "state": "ready", "dish": meal()}]},
            {"customers": [order(order_status="assigned")],
             "stoves": [{"id": "B1", "state": "cooking", "dish": meal(), "cook_ticks_left": 0}]},
            {"customers": [order(order_status="assigned")], "hand": dict(meal(), dish_id=SOUP)},
            {"customers": [order(order_status="assigned", base_price=61)], "hand": meal()},
            {"customers": [order(order_status="unfulfillable", reserved=["I1"])], "stock": individuals(["ca_loc"])},
            {"tables": [{"id": "T1", "pos": [99, 0]}]},
            {"customers": [order(order_status="unfulfillable", unknown=True)]},
            {"player": {"vel": [float("nan"), 0]}},
        )
        with Workdir() as w:
            for scenario in bad_scenarios:
                with self.subTest(scenario=scenario):
                    fixture = write_json(w.path("scenario.json"), {"quan": scenario})
                    out = w.path("out.jsonl")
                    code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--out", out,
                                             "--scenario", fixture)
                    self.assertEqual(code, 2, err)
                    self.assertFalse(os.path.exists(out))
