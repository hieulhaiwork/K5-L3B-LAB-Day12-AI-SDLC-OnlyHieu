"""Buổi sáng — Lặn & Hái (`gather`). KHUNG: bơi, chặn mép, đồng hồ, cập bến, xuất kho.

Mặt cắt dòng sông nhìn NGANG: vị trí `[x, d]` (x sang phải, `d` độ sâu hướng xuống, d = 0 là mặt nước).
`move = [x, d]`: thành phần thứ hai DƯƠNG = bơi xuống. Hướng mặt là góc từ +x, dương = xuống.

Đã làm sẵn để smoke test chạy được: bơi + tăng/giảm tốc, chặn mép (d không âm), đồng hồ và hết giờ,
cập bến (`interact` trong vùng bến -> `gather_end` reason `docked`), xuất kho, snapshot đầy đủ trường gather.

Nhóm viết tiếp (đúng thứ tự một bước trong PRD mục 13.8, "Gather"):
  TODO(nhóm, lát 1): bơi + oxy + biên + giỏ
      - oxy: dưới nước (d > surface_depth) trừ 1 tick/tick, mặt nước hồi oxygen_refill_per_tick, kẹp [0, max]
      - ngạt: oxy = 0 và đang dưới nước -> đếm zero_oxy_ticks, đủ choke_interval_ticks thì -1 Máu (choke)
      - Máu về 0 -> ngất (faint, gather_end reason `fainted`, mất toàn bộ giỏ, kho rỗng)
      - sự kiện dive / surface / oxygen_empty / choke / faint
      - giỏ: thứ tự nhặt (LIFO), sức chứa hold_capacity
  TODO(nhóm, lát 2): hái + bắt cá + cập bến + kho
      - hái nút ở mặt nước (gather, hold_full), nút mọc lại (node_regrown đã có phần đếm ngược)
      - bắt đàn cá bằng `catch` (fish_caught, hold_full, hồi chiêu catch_cd_ticks, chỉ khi dưới nước)
      - cập bến xét TRƯỚC hái (đã có); ghi kho đúng một lần do runner lo
Các tính năng của phase sau chưa nằm trong khung này.
"""

import math

from ..errors import BadInput
from ..freshness import decay, exact, snapshot_items, validate_individuals
from ..ids import id_key, sort_by_id
from ..inventory import hold_to_items, ingredient_kinds
from .ramp import ramp_velocity

# TICK = 60.0
AXES = ("x", "d")

def _towards(source, target):
    dx = target[0] - source[0]
    dy = target[1] - source[1]
    distance = math.hypot(dx, dy)

    if distance == 0:
        return (0.0, 0.0), 0.0

    return (dx / distance, dy / distance), distance

class GatherSim:
    mode = "gather"
    phase = "gather"

    def __init__(
            self, tuning, scenario, streams, ids,
            day=1, active_upgrades=None,
    ):
        self.t = tuning["gather"]
        self.hz = tuning["tick_hz"]
        self.rng = streams
        self.ids = ids
        self.day = day
        self.phase_tick = 0
        self.active_upgrades = dict(active_upgrades or {})
        self.mconfig = self.t.get("monsters", {})
        self.random_fish = scenario.get("random_fish", True)

        player = scenario.get("player", {})
        self.pos = list(map(
            float, player.get("pos", self.t["start_pos"])
        ))
        self.vel = list(map(
            float, player.get("vel", [0, 0])
        ))
        self._tgt = None
        self._ramp_left = 0
        self.heading = float(player.get(
            "heading_deg", self.t["start_heading_deg"]
        ))

        oxygen_s = self._upgrade_value(
            tuning, "oxygen", "oxygen_max_s",
            self.t["oxygen_max_s"],
        )
        self.oxygen_max = round(oxygen_s * self.hz)
        self.hp_max = self._upgrade_value(
            tuning, "hp", "hp_max", self.t["hp_max"]
        )

        self.oxygen_ticks = player.get(
            "oxygen_ticks", self.oxygen_max
        )
        self.hp = player.get("hp", self.hp_max)
        if not 0 <= self.oxygen_ticks <= self.oxygen_max:
            raise BadInput("player.oxygen_ticks vượt oxy tối đa đang áp dụng")
        if not 1 <= self.hp <= self.hp_max:
            raise BadInput("player.hp vượt giới hạn Máu đang áp dụng")
        self.zero_oxy_ticks = player.get(
            "zero_oxy_ticks", 0
        )
        self.invuln_ticks = player.get(
            "invuln_ticks", 0
        )
        self.catch_cd_ticks = player.get(
            "catch_cd_ticks", 0
        )

        self.freshness = tuning.get("freshness")
        self.hold = list(scenario.get("hold", []))
        if self.freshness:
            self.hold = validate_individuals(self.hold, ingredient_kinds(tuning))
            self.hold_decay = exact(self.freshness["gather_decay_per_s"]) / self.hz
            for item in self.hold:
                self.ids.reserve(item["id"])
        self.time_left_ticks = scenario.get(
            "time_left_ticks",
            round(self.t["duration_s"] * self.hz),
        )
        
        # nút và đàn cá: scenario THAY THẾ danh sách mặc định; random_fish=false tắt cá mặc định
        node_data = scenario.get("nodes", self.t["nodes"])
        self.nodes = [
            {
                "id": n["id"],
                "kind": n["kind"],
                "pos": list(map(float, n["pos"])),
                "regrow_ticks": n.get("regrow_ticks", 0),
            }
            for n in node_data
        ]

        # random_fish=false: fixture fish remain stationary.
        initial_fish = self.t["fish_initial"]
        default_fish = initial_fish if self.random_fish and isinstance(initial_fish, list) else []
        fish_data = scenario.get("fish", default_fish)
        if isinstance(initial_fish, int) and self.random_fish and "fish" not in scenario:
            fish_data = []
        self.fish = [
            {
                "id": f["id"],
                "kind": f["kind"],
                "pos": list(map(float, f["pos"])),
                "heading_deg": float(
                    f.get("heading_deg", 0)
                ),
                "age_ticks": f.get("age_ticks", 0),
            }
            for f in fish_data
        ]

        # Standalone gather uses Day 1 monsters.
        monster_data = scenario.get(
            "monsters",
            [
                m for m in self.mconfig.get("spawns", [])
                if m.get("from_day", 1) <= day
            ],
        )
        self.monsters = []
        for m in monster_data:
            self.monsters.append({
                "id": m["id"],
                "kind": m["kind"],
                "pos": list(map(float, m["pos"])),
                "waypoints": [
                    list(map(float, w))
                    for w in m["waypoints"]
                ],
                "target_idx": m.get("target_idx", 1),
                "state": m.get("state", "patrol"),
                "state_ticks_left": m.get(
                    "state_ticks_left", 0
                ),
                "recoil_dir": (
                    list(m["recoil_dir"])
                    if m.get("recoil_dir") is not None
                    else None
                ),
            })
        
        for collection in (
            self.nodes, self.fish, self.monsters
        ):
            for entity in collection:
                self.ids.reserve(entity["id"])
        for item in self.hold:
            self.ids.reserve(item["id"])
        if self.random_fish and "fish" not in scenario and type(initial_fish) is int:
            for _ in range(initial_fish):
                if self._spawn_school("fish_initial") is None:
                    break
        
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"][
            "reputation_initial"
        ]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def _upgrade_value(
        self, tuning, name, field, default
    ):
        level = self.active_upgrades.get(name, 0)
        if not level:
            return default

        options = tuning["shop"]["upgrades"][name]
        return next(
            option[field]
            for option in options
            if option["level"] == level
        )
    
    def inventory_items(self) -> list:
        """Danh sách cá thể dùng khi bàn giao kho."""
        if self.freshness:
            return snapshot_items(sort_by_id(self.hold))
        return hold_to_items(self.hold)

    def _add_to_hold(self, kind, amount):
        if self.freshness:
            initial = exact(self.freshness["initial"])
            self.hold.extend({"id": self.ids.new("I"), "kind": kind, "fresh": initial} for _ in range(amount))
        else:
            self.hold.extend([kind] * amount)

    def snapshot(self):
        return {
            "player": {
                "pos": self.pos.copy(),
                "vel": self.vel.copy(),
                "heading_deg": self.heading,
                "oxygen_ticks": self.oxygen_ticks,
                "oxygen_max_ticks": self.oxygen_max,
                "hp": self.hp,
                "hp_max": self.hp_max,
                "zero_oxy_ticks": self.zero_oxy_ticks,
                "invuln_ticks": self.invuln_ticks,
                "catch_cd_ticks": self.catch_cd_ticks,
                "at_surface": self._at_surface(),
            },
            "hold": snapshot_items(self.hold) if self.freshness else list(self.hold),
            "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [
                {
                    "id": n["id"],
                    "pos": n["pos"].copy(),
                    "kind": n["kind"],
                    "ready": n["regrow_ticks"] == 0,
                    "regrow_ticks": n["regrow_ticks"],
                }
                for n in sort_by_id(self.nodes)
            ],
            "fish": [
                {
                    "id": f["id"],
                    "pos": f["pos"].copy(),
                    "kind": f["kind"],
                    "heading_deg": f["heading_deg"],
                    "age_ticks": f["age_ticks"],
                }
                for f in sort_by_id(self.fish)
            ],
            "monsters": [
                {
                    "id": m["id"],
                    "kind": m["kind"],
                    "pos": m["pos"].copy(),
                    "waypoints": [
                        v.copy() for v in m["waypoints"]
                    ],
                    "target_idx": m["target_idx"],
                    "state": m["state"],
                    "state_ticks_left": m[
                        "state_ticks_left"
                    ],
                    "recoil_dir": m["recoil_dir"],
                }
                for m in sort_by_id(self.monsters)
            ],
        }

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        if self.done:
            return []
        
        events = []
        self.phase_tick += 1

        # 1. đồng hồ và hàng có sẵn: giảm bộ đếm, nút mọc lại
        self.time_left_ticks = max(
            0, self.time_left_ticks - 1
        )
        self.catch_cd_ticks = max(
            0, self.catch_cd_ticks - 1
        )
        self.invuln_ticks = max(
            0, self.invuln_ticks - 1
        )

        for node in sort_by_id(self.nodes):
            if node["regrow_ticks"] > 0:
                node["regrow_ticks"] -= 1
                if node["regrow_ticks"] == 0:
                    events.append((
                        "node_regrown",
                        {"node_id": node["id"]},
                    ))
        
        if self.freshness:
            decay(self.hold, self.hold_decay, self.freshness["spoiled_below"], "hold", events)

        # 2. Player movement and oxygen.
        was_surface = self._at_surface()
        self._move(inp)
        at_surface = self._at_surface()

        if was_surface and not at_surface:
             events.append((
                "dive", {"pos": self.pos.copy()}
            ))
        elif not was_surface and at_surface:
            events.append((
                "surface", {"pos": self.pos.copy()}
            ))

        if at_surface:
            self.oxygen_ticks = min(
                self.oxygen_max,
                self.oxygen_ticks
                + self.t["oxygen_refill_per_tick"],
            )
            self.zero_oxy_ticks = 0
        else:
            before = self.oxygen_ticks
            self.oxygen_ticks = max(0, before - 1)

            if before > 0 and self.oxygen_ticks == 0:
                events.append((
                    "oxygen_empty",
                    {"oxygen_ticks": 0},
                ))

            if self.oxygen_ticks == 0:
                self.zero_oxy_ticks += 1

                if self.zero_oxy_ticks >= self.t[
                    "choke_interval_ticks"
                ]:
                    self.zero_oxy_ticks = 0
                    self.hp = max(0, self.hp - 1)
                    events.append((
                        "choke", {"hp": self.hp}
                    ))

                    if self.hp == 0:
                        self._faint(events)
                        return events
            else:
                self.zero_oxy_ticks = 0

        # 3. Monsters move and may hit.
        if self._step_monsters(events):
            return events

        # 4. Dock first, then harvest.
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events

            if at_surface:
                node = self._nearest([
                    n for n in self.nodes
                    if n["regrow_ticks"] == 0
                    and math.dist(
                        self.pos, n["pos"]
                    ) <= self.t["interact_radius"]
                ])

                if node is not None:
                    amount = int(self.t["node_yield"])

                    if not self._has_space(amount):
                        events.append((
                            "hold_full",
                            {
                                "action": "gather",
                                "node_id": node["id"],
                                "required": amount,
                                "free": self.t["hold_capacity"] - len(self.hold),
                            },
                        ))
                    else:
                        self._add_to_hold(node["kind"], amount)
                        node["regrow_ticks"] = round(
                            self.t["regrow_s"] * self.hz
                        )
                        events.append((
                            "gather",
                            {
                                "node_id": node["id"],
                                "kind": node["kind"],
                                "amount": amount,
                            },
                        ))

        # 5. Catch uses fish positions BEFORE swimming.
        if (
            inp.pressed("catch")
            and not at_surface
            and self.catch_cd_ticks == 0
        ):
            fish = self._nearest([
                f for f in self.fish
                if math.dist(
                    self.pos, f["pos"]
                ) <= self.t["catch_radius"]
            ])

            if fish is not None:
                amount = self.t[
                    "fish_yield"
                ][fish["kind"]]

                if not self._has_space(amount):
                    events.append((
                        "hold_full",
                        {
                            "action": "catch",
                            "fish_id": fish["id"],
                            "required": amount,
                            "free": self.t["hold_capacity"] - len(self.hold),
                        },
                    ))
                else:
                    self._add_to_hold(fish["kind"], amount)
                    self.fish.remove(fish)
                    self.catch_cd_ticks = round(
                        self.t[
                            "catch_cooldown_s"
                        ] * self.hz
                    )
                    events.append((
                        "fish_caught",
                        {
                            "fish_id": fish["id"],
                            "kind": fish["kind"],
                            "yield": amount,
                        },
                    ))
            
        # 6. On the final tick, no fish movement/spawning.
        if self.time_left_ticks == 0:
            self._finish("time", events)
            return events

        self._step_fish(events)
        return events

    # --- tiện ích ---------------------------------------------------------------
    def _faint(self, events, cause=None):
        lost = [
            self.hold.pop()
            for _ in range(len(self.hold))
        ]
        data = {"hp": 0, "lost": lost}

        if self.freshness or cause == "monster":
            data["cause"] = cause or "choke"

        events.append(("faint", data))
        self._finish("fainted", events)

    def _step_monsters(self, events):
        eligible = []

        for monster in sort_by_id(self.monsters):
            cfg = self.mconfig[
                "species"
            ][monster["kind"]]

            # Recoil/stun: no hit during these steps.
            if monster["state"] in (
                "recoil", "stunned"
            ):
                if monster["state"] == "recoil":
                    displacement = (
                        cfg["recoil_dist"]
                        / cfg["recoil_ticks"]
                    )
                    direction = (
                        monster["recoil_dir"]
                        or [1.0, 0.0]
                    )
                    self._move_monster(
                        monster,
                        direction,
                        displacement,
                        cfg["depths"],
                    )

                monster["state_ticks_left"] -= 1

                if monster["state_ticks_left"] <= 0:
                    monster["state"] = "patrol"
                    monster["state_ticks_left"] = 0
                    monster["recoil_dir"] = None
                continue

            distance = math.dist(
                monster["pos"], self.pos
            )
            detection_depth = cfg["depths"][0]

            if monster["state"] == "chase":
                if (
                    self.pos[1] < detection_depth
                    or distance > cfg["exit_radius"]
                ):
                    monster["state"] = "patrol"

            elif (
                self.pos[1] >= detection_depth
                and distance <= cfg["detect_radius"]
            ):
                monster["state"] = "chase"

            if monster["state"] == "chase":
                direction, distance = _towards(
                    monster["pos"], self.pos
                )
                step = min(
                    distance,
                    cfg["chase_speed"] / self.hz,
                )
                self._move_monster(
                    monster,
                    direction,
                    step,
                    cfg["depths"],
                )
            else:
                target = monster[
                    "waypoints"
                ][monster["target_idx"]]
                direction, distance = _towards(
                    monster["pos"], target
                )
                step = min(
                    distance,
                    cfg["patrol_speed"] / self.hz,
                )
                self._move_monster(
                    monster,
                    direction,
                    step,
                    cfg["depths"],
                )

                if distance <= (
                    cfg["patrol_speed"] / self.hz
                ):
                    monster["target_idx"] = (
                        1 - monster["target_idx"]
                    )

            if (
                self.pos[1] >= detection_depth
                and math.dist(
                    monster["pos"], self.pos
                ) <= cfg["hit_radius"]
            ):
                eligible.append(monster)

        if self.invuln_ticks or not eligible:
            return False

        attacker = self._nearest(eligible)

        loss_count = math.floor(
            len(self.hold)
            * self.mconfig["loss_ratio"]
        )
        lost = [
            self.hold.pop()
            for _ in range(loss_count)
        ]

        self.hp = max(0, self.hp - 1)
        events.append((
            "monster_hit",
            {
                "monster_id": attacker["id"],
                "hp": self.hp,
                "lost": lost,
                "pos": self.pos.copy(),
            },
        ))

        direction, distance = _towards(
            self.pos, attacker["pos"]
        )
        attacker["recoil_dir"] = (
            list(direction)
            if distance else [1.0, 0.0]
        )
        attacker["state"] = "recoil"
        attacker["state_ticks_left"] = (
            self.mconfig["species"][
                attacker["kind"]
            ]["recoil_ticks"]
        )
        self.invuln_ticks = self.mconfig[
            "invuln_ticks"
        ]

        if self.hp == 0:
            self._faint(
                events, cause="monster"
            )
            return True

        return False

    def _move_monster(
        self, monster, direction, step, depths
    ):
        monster["pos"][0] = min(
            self.t["bounds"]["x"][1],
            max(
                self.t["bounds"]["x"][0],
                monster["pos"][0]
                + direction[0] * step,
            ),
        )
        monster["pos"][1] = min(
            depths[1],
            max(
                depths[0],
                monster["pos"][1]
                + direction[1] * step,
            ),
        )

    @staticmethod
    def _reflect(value, velocity, lo, hi):
        value += velocity

        while value < lo or value > hi:
            if value < lo:
                value = 2 * lo - value
            else:
                value = 2 * hi - value
            velocity = -velocity

        return value, velocity

    def _step_fish(self, events):
        if (
            not self.random_fish
            or "fish_speed" not in self.t
        ):
            return

        turning = self.rng.get("fish_turn")
        step = self.t["fish_speed"] / self.hz

        for fish in sort_by_id(self.fish):
            fish["age_ticks"] += 1

            if fish["age_ticks"] % self.t[
                "fish_turn_ticks"
            ] == 0:
                fish["heading_deg"] = (
                    turning.uniform(0, 360)
                )

            radians = math.radians(
                fish["heading_deg"]
            )
            vx = step * math.cos(radians)
            vy = step * math.sin(radians)

            x_lo, x_hi = self.t["fish_x"]
            d_lo, d_hi = self.t[
                "fish_depths"
            ][fish["kind"]]

            fish["pos"][0], vx = self._reflect(
                fish["pos"][0],
                vx,
                x_lo,
                x_hi,
            )
            fish["pos"][1], vy = self._reflect(
                fish["pos"][1],
                vy,
                d_lo,
                d_hi,
            )
            fish["heading_deg"] = (
                math.degrees(
                    math.atan2(vy, vx)
                ) % 360
            )

        if self.phase_tick % self.t[
            "fish_spawn_ticks"
        ]:
            return

        if len(self.fish) >= self.t[
            "fish_max"
        ]:
            return

        new = self._spawn_school()
        if new:
            events.append(("fish_spawned", {"id": new["id"], "kind": new["kind"], "pos": new["pos"].copy()}))

    def _spawn_school(self, stream="fish_spawn"):
        # Eligible species and geometric spawn locations.
        locations = {}

        for kind in sorted(
            self.t["fish_weights"]
        ):
            locations[kind] = [
                [float(x), float(depth)]
                for x in self.t["fish_spawn_x"]
                for depth in self.t[
                    "fish_spawn_depths"
                ][kind]
                if all(
                    math.dist(
                        [x, depth], fish["pos"]
                    ) > self.t[
                        "fish_spawn_clearance"
                    ]
                    for fish in self.fish
                )
            ]

        eligible = [
            kind for kind, positions
            in locations.items()
            if positions
        ]
        if not eligible:
            return

        spawner = self.rng.get(stream)
        kind = spawner.choices(
            eligible,
            weights=[
                self.t["fish_weights"][k]
                for k in eligible
            ],
            k=1,
        )[0]
        pos = spawner.choice(locations[kind])

        new = {
            "id": self.ids.new("F"),
            "kind": kind,
            "pos": pos,
            "heading_deg": spawner.uniform(
                0, 360
            ),
            "age_ticks": 0,
        }

        self.fish.append(new)
        return new

    def _nearest(self, entities):
        if not entities:
            return None

        return min(
            entities,
            key=lambda e: (
                math.dist(
                    self.pos, e["pos"]
                ),
                id_key(e["id"]),
            ),
        )

    def _has_space(self, amount):
        return (
            len(self.hold) + amount
            <= self.t["hold_capacity"]
        )

    def _at_surface(self):
        return self.pos[1] <= self.t[
            "surface_depth"
        ]

    def _in_dock(self):
        return math.dist(
            self.pos, self.t["dock_pos"]
        ) <= self.t["dock_radius"]

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append((
            "gather_end",
            {
                "reason": reason,
                "inventory": {
                    "items": self.inventory_items(),
                },
            },
        ))

    def _move(self, inp):
        speed = self.t["swim_speed"]
        mx, md = inp.move

        self.vel = ramp_velocity(
            self,
            (mx * speed, md * speed),
            self.t["ramp_max_ticks"],
        )

        if (mx, md) != (0, 0):
            self.heading = (
                math.degrees(
                    math.atan2(md, mx)
                ) % 360
            )

        for i, axis in enumerate(AXES):
            self.pos[i] += (
                self.vel[i] / self.hz
            )
            lo, hi = self.t[
                "bounds"
            ][axis]

            if self.pos[i] <= lo:
                self.pos[i] = lo
                self.vel[i] = max(
                    0.0, self.vel[i]
                )
            elif self.pos[i] >= hi:
                self.pos[i] = hi
                self.vel[i] = min(
                    0.0, self.vel[i]
                )

