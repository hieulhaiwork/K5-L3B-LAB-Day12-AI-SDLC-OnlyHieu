
"""Gather Phase 3: item identity and freshness."""

import json
import unittest

from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim


IDLE = InputState((0, 0), {}, set())
INTERACT = InputState(
    (0, 0), {"interact": True}, {"interact"}
)
CATCH = InputState(
    (0, 0), {"catch": True}, {"catch"}
)


def item(number, kind="ca_linh", fresh=100):
    return {
        "id": f"I{number}",
        "kind": kind,
        "fresh": fresh,
    }


class GatherPhase3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(
            "game.contract.json", encoding="utf-8"
        ) as file:
            contract = json.load(file)

        cls.tuning = contract["tuning"]
        assert "freshness" in cls.tuning

    def make_sim(self, scenario=None):
        return GatherSim(
            self.tuning,
            scenario or {
                "random_fish": False,
                "monsters": [],
            },
            Streams(42),
            IdAllocator(),
        )

    def test_fresh_30_spoils_on_first_tick(self):
        sim = self.make_sim({
            "hold": [item(1, fresh=30)],
            "random_fish": False,
            "monsters": [],
        })

        events = sim.step(IDLE)

        self.assertEqual(events, [
            ("spoiled", {
                "item_id": "I1",
                "kind": "ca_linh",
                "location": "hold",
            })
        ])
        self.assertLess(sim.hold[0]["fresh"], 30)

        # Spoiled is emitted exactly once.
        events = sim.step(IDLE)
        self.assertNotIn(
            "spoiled", [name for name, _ in events]
        )

    def test_exact_threshold_at_tick_8400(self):
        sim = self.make_sim({
            "hold": [item(1, fresh=100)],
            "random_fish": False,
            "monsters": [],
        })

        for _ in range(8400):
            sim.step(IDLE)

        self.assertEqual(sim.hold[0]["fresh"], 30.0)

        events = sim.step(IDLE)
        self.assertEqual(
            [name for name, _ in events],
            ["spoiled"],
        )

    def test_multiple_spoiled_events_sorted_by_id(self):
        sim = self.make_sim({
            "hold": [
                item(10, fresh=30),
                item(2, fresh=30),
            ],
            "random_fish": False,
            "monsters": [],
        })

        events = sim.step(IDLE)
        self.assertEqual(
            [data["item_id"] for name, data in events
             if name == "spoiled"],
            ["I2", "I10"],
        )

    def test_new_harvest_starts_at_100(self):
        sim = self.make_sim({
            "player": {"pos": [12, 0]},
            "random_fish": False,
            "monsters": [],
        })

        events = sim.step(INTERACT)

        self.assertIn(
            "gather", [name for name, _ in events]
        )
        self.assertEqual(
            sim.hold,
            [item(1, "bong_dien_dien", 100)],
        )

        sim.step(IDLE)
        self.assertAlmostEqual(
            sim.hold[0]["fresh"],
            100 - 0.5 / 60,
        )

    def test_catch_creates_three_unique_items(self):
        sim = self.make_sim({
            "player": {"pos": [15, 5]},
            "random_fish": False,
            "monsters": [],
            "fish": [{
                "id": "F1",
                "kind": "ca_linh",
                "pos": [15, 5],
                "heading_deg": 0,
            }],
        })

        events = sim.step(CATCH)

        self.assertIn(
            "fish_caught",
            [name for name, _ in events],
        )
        self.assertEqual(
            [x["id"] for x in sim.hold],
            ["I1", "I2", "I3"],
        )
        self.assertTrue(
            all(x["fresh"] == 100 for x in sim.hold)
        )

    def test_fixture_id_is_not_reused(self):
        sim = self.make_sim({
            "player": {"pos": [12, 0]},
            "hold": [item(7, "ca_loc", 60)],
            "random_fish": False,
            "monsters": [],
        })

        sim.step(INTERACT)

        self.assertEqual(
            [x["id"] for x in sim.hold],
            ["I7", "I8"],
        )

    def test_monster_loss_preserves_lifo(self):
        sim = self.make_sim({
            "player": {
                "pos": [60, 24],
                "hp": 3,
            },
            "hold": [
                item(1),
                item(2),
                item(3),
                item(4),
                item(5),
            ],
            "random_fish": False,
        })

        events = sim.step(IDLE)
        hits = [
            data for name, data in events
            if name == "monster_hit"
        ]

        self.assertEqual(len(hits), 1)
        self.assertEqual(
            [x["id"] for x in hits[0]["lost"]],
            ["I5", "I4"],
        )
        self.assertEqual(
            [x["id"] for x in sim.hold],
            ["I1", "I2", "I3"],
        )

    def test_faint_exports_empty_inventory(self):
        sim = self.make_sim({
            "player": {
                "pos": [60, 24],
                "hp": 1,
            },
            "hold": [item(1), item(2)],
            "random_fish": False,
        })

        events = sim.step(IDLE)

        self.assertEqual(
            [name for name, _ in events],
            ["monster_hit", "faint", "gather_end"],
        )

        self.assertEqual(sim.hold, [])
        self.assertEqual(sim.inventory_items(), [])
        self.assertEqual(
            events[-1][1]["inventory"],
            {"items": []},
        )

    def test_dock_preserves_ids_and_freshness(self):
        sim = self.make_sim({
            "hold": [item(3, "ca_loc", 100)],
            "random_fish": False,
            "monsters": [],
        })

        events = sim.step(INTERACT)
        end = [
            data for name, data in events
            if name == "gather_end"
        ][0]

        exported = end["inventory"]["items"]
        self.assertEqual(exported[0]["id"], "I3")
        self.assertEqual(exported[0]["kind"], "ca_loc")
        self.assertAlmostEqual(
            exported[0]["fresh"],
            100 - 0.5 / 60,
        )

    def test_spoiled_item_stays_in_hold(self):
        sim = self.make_sim({
            "hold": [item(1, fresh=0)],
            "random_fish": False,
            "monsters": [],
        })

        sim.step(IDLE)

        self.assertEqual(len(sim.hold), 1)
        self.assertEqual(sim.hold_count if hasattr(
            sim, "hold_count"
        ) else len(sim.hold), 1)
        self.assertEqual(sim.hold[0]["fresh"], 0)


if __name__ == "__main__":
    unittest.main()
