"""Buổi tối — Mở Quán (Phase 1)."""

import math
from decimal import Decimal

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from ..inventory import validate_items
from .ramp import ramp_velocity


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.ids = ids
        self.orders_rng = streams.get("customer_order")
        self.tick_hz = tuning["tick_hz"]
        self.tick = 0
        self.customer_interval = self._ticks(t["customer_interval_s"])
        self.patience_max = self._ticks(t["patience_s"])
        self.tip_min_patience = math.ceil(self.patience_max * Decimal(str(t["tip_min_patience_ratio"])))
        self.eat_duration = self._ticks(t["eat_s"])
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = validate_items(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = None
        self.time_left_ticks = scenario.get("time_left_ticks", self._ticks(t["duration_s"]))
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.random_customers = scenario.get("random_customers", True)
        if not isinstance(self.random_customers, bool):
            raise BadInput("quan.random_customers phải là boolean")
        if (isinstance(self.reputation, bool) or not isinstance(self.reputation, (int, float))
                or not t["reputation_min"] <= self.reputation <= t["reputation_max"]):
            raise BadInput("quan.reputation nằm ngoài giới hạn uy tín")
        self.stoves = self._merge(t["stoves"], scenario.get("stoves", []))
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.customers = {}
        self._load_customers(scenario.get("customers", []))
        self._load_dishes(scenario.get("hand"))
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    def _ticks(self, seconds):
        return max(1, round(seconds * self.tick_hz))

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    @staticmethod
    def _nonnegative_int(value, field):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise BadInput(f"{field} phải là số nguyên không âm")
        return value

    def _load_customers(self, customers):
        for source in customers:
            customer = dict(source)
            dish = customer.get("dish_id")
            state = customer.get("state", "waiting")
            status = customer.get("order_status", "reserved")
            if not isinstance(dish, str) or dish not in self.menu or state not in ("waiting", "eating"):
                raise BadInput(f"customers.{customer['id']}: món hoặc trạng thái không hợp lệ")
            if status not in ("reserved", "assigned", "unfulfillable", "served") or (state == "eating") != (status == "served"):
                raise BadInput(f"customers.{customer['id']}: order_status không khớp trạng thái")
            customer.update(state=state, order_status=status)
            for field, default in (("order_tick", 0), ("patience_ticks_left", self.patience_max), ("eat_ticks_left", 0)):
                customer[field] = self._nonnegative_int(customer.get(field, default), field)
            if (customer["eat_ticks_left"] > 0) != (state == "eating"):
                raise BadInput(f"customers.{customer['id']}: bộ đếm ăn không khớp trạng thái")
            base_price, tip = customer.get("base_price"), customer.get("tip")
            if state == "eating" or base_price is not None:
                if self._nonnegative_int(base_price, "base_price") == 0:
                    raise BadInput("base_price phải lớn hơn 0")
            if state == "eating" or tip is not None:
                self._nonnegative_int(tip, "tip")
            customer.update(base_price=base_price, tip=tip)
            self.customers[customer["id"]] = customer
            self.ids.reserve(customer["id"])

        available = self.stock.copy()
        for customer in sorted(self.customers.values(), key=self._order_priority):
            recipe = self.menu[customer["dish_id"]]["recipe"] if customer["order_status"] == "reserved" else {}
            if "reserved" in customer and validate_items(customer["reserved"]) != recipe:
                raise BadInput(f"customers.{customer['id']}: giữ chỗ không khớp trạng thái và công thức")
            for kind, amount in recipe.items():
                if available.get(kind, 0) < amount:
                    raise BadInput("khách giữ chỗ nhiều nguyên liệu hơn trong kho")
                available[kind] -= amount
            customer["reserved"] = dict(recipe)

    def _load_dishes(self, hand):
        assigned = {c["id"] for c in self.customers.values() if c["order_status"] == "assigned"}
        for stove in self.stoves:
            state = stove.get("state", "idle")
            dish = stove.get("dish")
            cook = self._nonnegative_int(stove.get("cook_ticks_left", 0), "cook_ticks_left")
            ready = self._nonnegative_int(stove.get("ready_ticks", 0), "ready_ticks")
            if state not in ("idle", "cooking", "ready") or (cook > 0) != (state == "cooking") or (ready and state != "ready"):
                raise BadInput(f"stoves.{stove['id']}: trạng thái hoặc bộ đếm không hợp lệ")
            if state == "idle" and dish is not None:
                raise BadInput(f"stoves.{stove['id']}: bếp rảnh phải trống")
            if state in ("cooking", "ready"):
                dish = self._claim_dish(assigned, dish)
            stove.update(state=state, dish=dish, cook_ticks_left=cook, ready_ticks=ready)

        if hand is not None:
            self.hand = self._claim_dish(assigned, hand)
        if assigned:
            raise BadInput("đơn assigned phải có đúng một món trên bếp hoặc trên tay")

    def _claim_dish(self, assigned, dish):
        if not isinstance(dish, dict) or set(dish) != {"order_id", "dish_id", "base_price"}:
            raise BadInput("payload món phải có đúng order_id, dish_id và base_price")
        order_id = dish["order_id"]
        if not isinstance(order_id, str) or order_id not in assigned:
            raise BadInput("món trên bếp/tay phải khớp với đúng một đơn assigned")
        customer = self.customers[order_id]
        base_price = self._nonnegative_int(dish["base_price"], "dish.base_price")
        if (base_price == 0 or dish["dish_id"] != customer["dish_id"]
                or customer["base_price"] not in (None, base_price)):
            raise BadInput("món hoặc giá đã chốt không khớp đơn assigned")
        customer["base_price"] = base_price
        assigned.remove(order_id)
        return {"order_id": order_id, "dish_id": dish["dish_id"], "base_price": base_price}

    @staticmethod
    def _order_priority(customer):
        return (customer["order_tick"], id_key(customer["table_id"]))

    def _available_stock(self):
        available = self.stock.copy()
        for customer in self.customers.values():
            for kind, amount in customer["reserved"].items():
                available[kind] = available.get(kind, 0) - amount
        return available

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers.values()}
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s[k] for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers.values()),
        }

    def step(self, inp):
        events = []
        self.tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self._advance_stoves(events)
        self._tick_customers()
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        closing = self.time_left_ticks == 0
        self._settle_tables(closing, events)
        if closing:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        else:
            first = self.t["first_customer_tick"]
            if self.random_customers and self.tick >= first and (self.tick - first) % self.customer_interval == 0:
                self._seat_customer(events)
        return events

    @staticmethod
    def _order_data(customer):
        return {"order_id": customer["id"], "table_id": customer["table_id"], "dish_id": customer["dish_id"]}

    @staticmethod
    def _stove_event_data(stove):
        return {"stove_id": stove["id"], "order_id": stove["dish"]["order_id"], "dish_id": stove["dish"]["dish_id"]}

    def _seat_customer(self, events):
        occupied = {c["table_id"] for c in self.customers.values()}
        table = next((table for table in self.tables if table["id"] not in occupied), None)
        if table is None:
            return
        available = self._available_stock()
        dishes = [dish_id for dish_id in sorted(self.menu)
                  if all(available.get(kind, 0) >= amount
                         for kind, amount in self.menu[dish_id]["recipe"].items())]
        if not dishes:
            events.append(("no_dish", {}))
            return
        dish = self.orders_rng.choice(dishes)
        customer = {"id": self.ids.new("C"), "table_id": table["id"], "dish_id": dish, "order_tick": self.tick,
                    "state": "waiting", "patience_ticks_left": self.patience_max, "eat_ticks_left": 0,
                    "order_status": "reserved", "reserved": dict(self.menu[dish]["recipe"]),
                    "base_price": None, "tip": None}
        self.customers[customer["id"]] = customer
        events.append(("customer_arrived", self._order_data(customer)))

    def _advance_stoves(self, events):
        for stove in self.stoves:
            if stove["state"] == "ready":
                stove["ready_ticks"] += 1
            elif stove["state"] == "cooking":
                stove["cook_ticks_left"] = max(0, stove["cook_ticks_left"] - 1)
                if stove["cook_ticks_left"] == 0:
                    stove["state"] = "ready"
                    events.append(("dish_ready", self._stove_event_data(stove)))

    def _tick_customers(self):
        for customer in self.customers.values():
            timer = "eat_ticks_left" if customer["state"] == "eating" else "patience_ticks_left"
            customer[timer] = max(0, customer[timer] - 1)

    def _settle_tables(self, closing, events):
        for customer in sort_by_id(self.customers.values(), key=lambda c: c["table_id"]):
            if customer["state"] == "eating":
                if customer["eat_ticks_left"] == 0:
                    self._pay(customer, "finished_eating", events)
                elif closing:
                    self._pay(customer, "closing", events)
            elif closing or customer["patience_ticks_left"] == 0:
                self._leave(customer, "closing" if closing else "patience", events)

    def _change_reputation(self, delta):
        value = float(Decimal(str(self.reputation)) + Decimal(str(delta)))
        self.reputation = min(self.t["reputation_max"], max(self.t["reputation_min"], value))

    def _pay(self, customer, reason, events):
        price, tip = customer["base_price"], customer["tip"]
        total = price + tip
        self.money += total
        self.earned += total
        self.shift_earned += total
        if tip:
            self._change_reputation(self.t["tip_reputation"])
        del self.customers[customer["id"]]
        events.append(("paid", {"order_id": customer["id"], "table_id": customer["table_id"],
                                "base_price": price, "tip": tip, "amount": total, "reason": reason}))

    @staticmethod
    def _clear_stove(stove):
        stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)

    def _leave(self, customer, reason, events):
        customer_id = customer["id"]
        for stove in self.stoves:
            if stove["dish"] is not None and stove["dish"]["order_id"] == customer_id:
                self._clear_stove(stove)
        if self.hand is not None and self.hand["order_id"] == customer_id:
            self.hand = None
        del self.customers[customer_id]
        if reason == "patience":
            self._change_reputation(self.t["left_reputation_delta"])
        events.append(("customer_left", {"order_id": customer_id, "table_id": customer["table_id"],
                                         "reason": reason, "reputation": self.reputation}))

    def _interact(self, events):
        targets = []
        for priority, fixtures in enumerate((self.stoves, self.tables)):
            for fixture in fixtures:
                distance = math.dist(self.pos, fixture["pos"])
                if distance <= self.t["interact_radius"]:
                    targets.append((distance, priority, id_key(fixture["id"]), fixture))
        if not targets:
            return
        _, priority, _, fixture = min(targets, key=lambda target: target[:3])
        if priority == 0:
            self._use_stove(fixture, events)
        else:
            self._serve(fixture, events)

    def _use_stove(self, stove, events):
        if stove["state"] == "idle":
            waiting = (c for c in self.customers.values() if c["order_status"] == "reserved")
            customer = min(waiting, key=self._order_priority, default=None)
            if customer is None:
                return
            items = []
            for kind, amount in sorted(customer["reserved"].items()):
                self.stock[kind] -= amount
                items.extend([kind] * amount)
            dish_id = customer["dish_id"]
            price = self.menu[dish_id]["price"]
            dish = {"order_id": customer["id"], "dish_id": dish_id, "base_price": price}
            customer.update(order_status="assigned", reserved={}, base_price=price)
            stove.update(state="cooking", dish=dish, cook_ticks_left=self._ticks(self.menu[dish_id]["cook_s"]))
            events.append(("cook_started", dict(self._stove_event_data(stove), items=items, base_price=price)))
        elif stove["state"] == "ready" and self.hand is None and self.t["carry_limit"] > 0:
            self.hand = stove["dish"]
            events.append(("dish_picked", self._stove_event_data(stove)))
            self._clear_stove(stove)

    def _serve(self, table, events):
        if self.hand is None:
            return
        customer = self.customers[self.hand["order_id"]]
        if customer["table_id"] != table["id"]:
            return
        price = self.hand["base_price"]
        tip = 0
        if customer["patience_ticks_left"] >= self.tip_min_patience:
            tip = int(price * Decimal(str(self.t["tip_rate"])))
        customer.update(state="eating", order_status="served", eat_ticks_left=self.eat_duration, base_price=price, tip=tip)
        self.hand = None
        events.append(("served", dict(self._order_data(customer), patience_ticks_left=customer["patience_ticks_left"],
                                      base_price=price, tip=tip)))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / self.tick_hz
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
