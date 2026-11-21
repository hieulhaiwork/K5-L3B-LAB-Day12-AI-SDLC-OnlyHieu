"""Điều phối các ca và nâng cấp trong vòng ngày."""

from ..day_plan import normalize_day_plan
from ..ids import IdAllocator
from ..rng import Streams
from .gather import GatherSim
from .quan import QuanSim


def build_gather(tuning, scenario, streams, ids, **kwargs):
    """Chuyển số đàn trong manifest v1.1 thành fixture cho GatherSim."""
    gather = tuning["gather"]
    if "fish" not in scenario and scenario.get("random_fish", True):
        rng = streams.get("fish_initial")
        weights = gather["fish_weights"]
        positions = {kind: [(x, d) for x in gather["fish_spawn_x"] for d in gather["fish_spawn_depths"][kind]]
                     for kind in sorted(weights)}
        fish = []
        for _ in range(gather["fish_initial"]):
            eligible = [kind for kind, points in positions.items() if points]
            kind = rng.choices(eligible, weights=[weights[k] for k in eligible], k=1)[0]
            pos = rng.choice(positions[kind])
            fish.append({"id": ids.new("F"), "kind": kind, "pos": pos, "heading_deg": rng.uniform(0, 360)})
            for points in positions.values():
                if pos in points:
                    points.remove(pos)
        scenario = dict(scenario, fish=fish)
    return GatherSim(tuning, scenario, streams, ids, **kwargs)


class DaySim:
    mode = "day"

    def __init__(self, tuning, scenario, seed, days):
        self.tuning, self.scenario, self.days = tuning, scenario, days
        self.streams = Streams(seed)
        self.ids = IdAllocator()
        start = scenario.get("day", {})
        self.plans = {entry["day"]: normalize_day_plan(entry, tuning["menu"]) for entry in tuning["day_plan"]}
        self.plans.update({entry["day"]: entry for entry in start.get("day_plan", [])})
        self.money = start.get("money", 0)
        self.earned = start.get("earned", 0)
        self.reputation = start.get("reputation", tuning["quan"]["reputation_initial"])
        self.upgrades = dict(start.get("upgrades", {}))
        self.day = 1
        self.days_completed = 0
        self.done, self.reason = False, None
        self._start_day()

    @property
    def time_left_ticks(self):
        return self.shop_ticks if self.phase == "shop" else self.current.time_left_ticks

    def _start_day(self):
        self.phase = "gather"
        self.active_upgrades = self.upgrades.copy()
        self.plan = self.plans[self.day]
        self.stock = {}
        self.current = build_gather(self.tuning, self.scenario.get("gather", {}), self.streams, self.ids,
                                    day=self.day, active_upgrades=self.active_upgrades)

    def _event(self, name, data):
        return self.phase, self.day, name, data

    def initial_events(self):
        return [self._event("day_start", {}),
                self._event("day_plan", {key: self.plan[key] for key in ("dishes", "ingredients")}),
                self._event("phase_start", {})]

    def snapshot(self):
        detail = {"stock": self.stock.copy()} if self.phase == "shop" else self.current.snapshot()
        return dict(detail, day=self.day, day_plan=self.plan, upgrades=self.upgrades.copy(),
                    active_upgrades=self.active_upgrades.copy())

    def _buy(self, action):
        options = self.tuning["shop"]["upgrades"].get(action)
        level = self.upgrades.get(action, 0)
        if options is None:
            return self._event("buy_failed", {"action": action, "reason": "unknown"})
        if level >= len(options):
            return self._event("buy_failed", {"action": action, "reason": "max_level"})
        option = options[level]
        if self.money < option["price"]:
            return self._event("buy_failed", {"action": action, "reason": "funds"})
        self.money -= option["price"]
        self.upgrades[action] = option["level"]
        return self._event("bought", {"upgrade": action, "level": option["level"],
                                      "price": option["price"], "money": self.money})

    def _shop_step(self, inp):
        self.shop_ticks -= 1
        events = [self._buy(inp.buy)] if inp.buy else []
        close = inp.pressed("shop_done")
        if not close and self.shop_ticks:
            return events
        events.append(self._event("shop_end", {"reason": "done" if close else "time"}))
        self.stock = {}
        self.days_completed += 1
        if self.days_completed == self.days:
            self.done, self.reason = True, "days_complete"
        else:
            self.day += 1
            self._start_day()
            events.extend(self.initial_events())
        return events

    def step(self, inp):
        if self.phase == "shop":
            return self._shop_step(inp)
        events = [self._event(name, data) for name, data in self.current.step(inp)]
        if self.phase == "quan":
            self.money, self.earned, self.reputation = self.current.money, self.current.earned, self.current.reputation
        if not self.current.done:
            return events
        if self.phase == "gather":
            self.stock = self.current.inventory_items()
            self.current = QuanSim(self.tuning, self.scenario.get("quan", {}), self.streams, self.ids,
                                   self.stock, day_plan=self.plan, money=self.money,
                                   earned=self.earned, reputation=self.reputation)
            self.phase = "quan"
        else:
            self.stock = self.current.snapshot()["stock"]
            self.phase = "shop"
            self.shop_ticks = self.tuning["shop"]["max_ticks"]
        return [*events, self._event("phase_start", {})]
