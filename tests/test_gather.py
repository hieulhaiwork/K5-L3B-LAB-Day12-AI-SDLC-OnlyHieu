
"""Kiểm thử luật chơi Gather — Phase 1."""

import unittest

from chonoi.contract import load_contract
from chonoi.inputs import LiveInputs
from chonoi.runner import Session


class GatherRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tuning = load_contract()["tuning"]

    def make_session(self, scenario=None):
        return Session(
            "gather", self.tuning, scenario or {}, seed=1
        )

    @staticmethod
    def names(rows):
        return [row["name"] for row in rows]

    def test_oxygen_drops_and_empty_event_only_once(self):
        session = self.make_session({
            "player": {
                "pos": [20, 5],
                "oxygen_ticks": 2,
            },
            "random_fish": False,
        })
        inputs = LiveInputs()

        session.step(inputs.advance())
        self.assertEqual(session.sim.oxygen_ticks, 1)

        rows = session.step(inputs.advance())
        self.assertEqual(session.sim.oxygen_ticks, 0)
        self.assertIn("oxygen_empty", self.names(rows))

        rows = session.step(inputs.advance())
        self.assertNotIn("oxygen_empty", self.names(rows))

    def test_surface_refills_oxygen_and_resets_choke(self):
        session = self.make_session({
            "player": {
                "pos": [20, 0],
                "oxygen_ticks": 1,
            },
            "random_fish": False,
        })
        session.sim.zero_oxy_ticks = 3

        session.step(LiveInputs().advance())

        want = min(
            session.sim.oxygen_max,
            1 + self.tuning["gather"][
                "oxygen_refill_per_tick"
            ],
        )
        self.assertEqual(session.sim.oxygen_ticks, want)
        self.assertEqual(session.sim.zero_oxy_ticks, 0)

    def test_diving_and_surfacing_emit_events(self):
        session = self.make_session({
            "player": {"pos": [20, 0.5]},
            "random_fish": False,
        })
        inputs = LiveInputs()
        inputs.set(move=[0, 1])

        found = []
        for _ in range(15):
            found.extend(
                self.names(session.step(inputs.advance()))
            )
        self.assertIn("dive", found)

        inputs.set(move=[0, -1])
        for _ in range(35):
            found.extend(
                self.names(session.step(inputs.advance()))
            )
        self.assertIn("surface", found)

    def test_choke_faint_clears_hold_and_ends(self):
        interval = self.tuning["gather"][
            "choke_interval_ticks"
        ]
        session = self.make_session({
            "player": {
                "pos": [20, 5],
                "hp": 1,
                "oxygen_ticks": 0,
                "zero_oxy_ticks": interval - 1,
            },
            "hold": ["ca_loc"],
            "random_fish": False,
        })

        rows = session.step(LiveInputs().advance())

        self.assertEqual(
            self.names(rows)[-3:],
            ["choke", "faint", "gather_end"],
        )
        self.assertEqual(session.sim.reason, "fainted")
        self.assertEqual(session.sim.hp, 0)
        self.assertEqual(session.sim.hold, [])
        self.assertEqual(session.sim.inventory_items(), {})

    def test_harvest_nearest_node_with_id_tiebreak(self):
        session = self.make_session({
            "player": {"pos": [20, 0]},
            "nodes": [
                {
                    "id": "N10",
                    "kind": "bong_sung",
                    "pos": [21, 0],
                },
                {
                    "id": "N2",
                    "kind": "bong_dien_dien",
                    "pos": [19, 0],
                },
            ],
            "random_fish": False,
        })
        inputs = LiveInputs()
        inputs.set(interact=True)

        rows = session.step(inputs.advance())

        self.assertIn("gather", self.names(rows))
        self.assertEqual(
            session.sim.hold,
            ["bong_dien_dien"],
        )
        node = next(
            n for n in session.sim.nodes
            if n["id"] == "N2"
        )
        self.assertGreater(node["regrow_ticks"], 0)

    def test_regrowth_happens_before_interact(self):
        session = self.make_session({
            "player": {"pos": [20, 0]},
            "nodes": [{
                "id": "N1",
                "kind": "bong_sung",
                "pos": [20, 0],
                "regrow_ticks": 1,
            }],
            "random_fish": False,
        })
        inputs = LiveInputs()
        inputs.set(interact=True)

        rows = session.step(inputs.advance())

        self.assertEqual(
            self.names(rows),
            ["node_regrown", "gather"],
        )

    def test_full_hold_does_not_consume_node(self):
        cap = self.tuning["gather"]["hold_capacity"]
        session = self.make_session({
            "player": {"pos": [20, 0]},
            "nodes": [{
                "id": "N1",
                "kind": "bong_sung",
                "pos": [20, 0],
            }],
            "hold": ["ca_loc"] * cap,
            "random_fish": False,
        })
        inputs = LiveInputs()
        inputs.set(interact=True)

        rows = session.step(inputs.advance())

        self.assertIn("hold_full", self.names(rows))
        self.assertEqual(len(session.sim.hold), cap)
        self.assertEqual(
            session.sim.nodes[0]["regrow_ticks"], 0
        )

    def test_catch_fish_and_cooldown(self):
        session = self.make_session({
            "player": {"pos": [15, 5]},
            "nodes": [],
            "fish": [
                {
                    "id": "F1",
                    "kind": "ca_linh",
                    "pos": [15, 5],
                },
                {
                    "id": "F2",
                    "kind": "ca_linh",
                    "pos": [15, 5],
                },
            ],
        })
        inputs = LiveInputs()
        inputs.set(catch=True)

        rows = session.step(inputs.advance())

        self.assertIn("fish_caught", self.names(rows))
        self.assertEqual(
            session.sim.hold,
            ["ca_linh"] * self.tuning["gather"][
                "fish_yield"
            ]["ca_linh"],
        )
        self.assertEqual(len(session.sim.fish), 1)

        inputs.set(catch=False)
        session.step(inputs.advance())
        inputs.set(catch=True)
        rows = session.step(inputs.advance())

        self.assertNotIn("fish_caught", self.names(rows))

    def test_no_partial_catch_when_hold_is_almost_full(self):
        cap = self.tuning["gather"]["hold_capacity"]
        session = self.make_session({
            "player": {"pos": [15, 5]},
            "nodes": [],
            "hold": ["ca_loc"] * (cap - 1),
            "fish": [{
                "id": "F1",
                "kind": "ca_linh",
                "pos": [15, 5],
            }],
        })
        inputs = LiveInputs()
        inputs.set(catch=True)

        rows = session.step(inputs.advance())

        self.assertIn("hold_full", self.names(rows))
        self.assertEqual(len(session.sim.hold), cap - 1)
        self.assertEqual(len(session.sim.fish), 1)

    def test_dock_takes_priority_over_harvest(self):
        session = self.make_session({
            "nodes": [{
                "id": "N1",
                "kind": "bong_sung",
                "pos": [2, 0],
            }],
            "random_fish": False,
        })
        inputs = LiveInputs()
        inputs.set(interact=True)

        rows = session.step(inputs.advance())

        self.assertEqual(
            self.names(rows), ["gather_end"]
        )
        self.assertEqual(session.sim.reason, "docked")
        self.assertEqual(session.sim.hold, [])

    def test_time_limit_keeps_inventory(self):
        session = self.make_session({
            "player": {"pos": [50, 0]},
            "hold": ["ca_loc", "bong_sung"],
            "time_left_ticks": 1,
            "random_fish": False,
        })

        rows = session.step(LiveInputs().advance())

        self.assertIn("gather_end", self.names(rows))
        self.assertEqual(session.sim.reason, "time")
        self.assertEqual(
            session.sim.inventory_items(),
            {"bong_sung": 1, "ca_loc": 1},
        )


if __name__ == "__main__":
    unittest.main()
