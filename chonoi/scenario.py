"""Nạp và kiểm scenario (Contract D). Trả về dict của đúng khối theo mode.

Kiểm cú pháp và phạm vi dữ liệu. QuanSim kiểm mâu thuẫn đơn hàng khi đã nạp kho.
"""

import json
import math
from decimal import Decimal

from .day_plan import normalize_day_plan
from .errors import BadInput
from .freshness import validate_individuals
from .inventory import ingredient_kinds, validate_items

GATHER_KEYS = {"player", "hold", "nodes", "fish", "monsters", "random_fish", "time_left_ticks"}
GATHER_PLAYER_KEYS = {"pos", "vel", "heading_deg", "hp", "oxygen_ticks", "zero_oxy_ticks",
                      "invuln_ticks", "catch_cd_ticks"}
NODE_KINDS = ("bong_dien_dien", "bong_sung", "keo_neo")
FISH_KINDS = ("ca_linh", "ca_loc", "ca_keo")
QUAN_PLAYER_KEYS = {"pos", "vel"}
QUAN_KEYS = {"player", "stock", "hand", "stoves", "tables", "customers", "random_customers",
             "reputation", "time_left_ticks"}
QUAN_ENTITY_KEYS = {
    "stoves": {"id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks"},
    "tables": {"id", "pos"},
    "customers": {"id", "table_id", "dish_id", "order_tick", "state", "patience_ticks_left", "eat_ticks_left",
                  "order_status", "reserved", "base_price", "tip"},
}


def _check_ids(name, arr):
    if not isinstance(arr, list):
        raise BadInput(f"{name} phải là mảng")
    seen = set()
    for e in arr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise BadInput(f"{name}: mỗi phần tử cần id (chuỗi khác rỗng)")
        if e["id"] in seen:
            raise BadInput(f"{name}: id trùng {e['id']}")
        seen.add(e["id"])


def _float_vectors(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [_float_vectors(item) for item in value]
    return value


def _preserve_freshness(obj):
    return {key: value if key == "fresh" else _float_vectors(value) for key, value in obj.items()}


def load_scenario(path, mode: str, tuning: dict) -> dict:
    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f, parse_float=Decimal, object_hook=_preserve_freshness)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    allowed = {"gather", "quan", "day"} if mode == "day" else {mode}
    if not isinstance(data, dict) or set(data) - allowed:
        raise BadInput(f"scenario có khối không hợp lệ cho --mode {mode}")
    if mode == "day":
        day = _validate_day(data.get("day", {}), tuning)
        gather = data.get("gather", {})
        gather_tuning = dict(tuning["gather"])
        for key, level in day.get("upgrades", {}).items():
            if level:
                tier = tuning["shop"]["upgrades"][key][level - 1]
                field = "oxygen_max_s" if key == "oxygen" else "hp_max"
                gather_tuning[field] = tier[field]
        quan = data.get("quan", {})
        _validate_block("gather", gather, dict(tuning, gather=gather_tuning))
        _validate_block("quan", quan, tuning)
        if {"stock", "reputation"} & set(quan):
            raise BadInput("scenario day nhận kho và uy tín từ ca trước")
        return {"day": day, "gather": gather, "quan": quan}
    block = data.get(mode, {})
    _validate_block(mode, block, tuning)
    return block


def _validate_day(block, tuning):
    known = {"money", "earned", "reputation", "upgrades", "day_plan"}
    if not isinstance(block, dict) or set(block) - known:
        raise BadInput("khối day không hợp lệ")
    money, earned = block.get("money", 0), block.get("earned", 0)
    if (type(money) is not int or type(earned) is not int or not 0 <= money <= earned
            or (earned > 0 and not {"money", "earned"} <= set(block))):
        raise BadInput("day cần khai cả money và earned với 0 <= money <= earned")
    if "reputation" in block:
        value, q = block["reputation"], tuning["quan"]
        if not _num(value) or not q["reputation_min"] <= value <= q["reputation_max"]:
            raise BadInput("day.reputation ngoài miền")
    levels = block.get("upgrades", {})
    tiers = tuning["shop"]["upgrades"]
    if not isinstance(levels, dict) or any(key not in tiers or type(level) is not int or not 0 <= level <= len(tiers[key])
                                          for key, level in levels.items()):
        raise BadInput("day.upgrades có cấp không hợp lệ")
    raw_plans = block.get("day_plan", [])
    if isinstance(raw_plans, dict):
        entries = []
        allowed_days = {str(plan["day"]) for plan in tuning["day_plan"]}
        for day, entry in raw_plans.items():
            if day not in allowed_days or not isinstance(entry, dict):
                raise BadInput("day.day_plan cần khóa ngày từ 1 đến 5")
            if "day" in entry and entry["day"] != int(day):
                raise BadInput("day.day_plan có số ngày không khớp khóa")
            entries.append(dict(entry, day=int(day)))
        raw_plans = entries
    if not isinstance(raw_plans, list):
        raise BadInput("day.day_plan phải là mảng hoặc object theo ngày")
    plans = [normalize_day_plan(entry, tuning["menu"]) for entry in raw_plans]
    if len({entry["day"] for entry in plans}) != len(plans):
        raise BadInput("day.day_plan có Ngày bị trùng")
    return dict(block, day_plan=plans)


def _validate_block(mode, block, tuning):
    if not isinstance(block, dict):
        raise BadInput(f"khối {mode} phải là object")
    allowed = GATHER_KEYS if mode == "gather" else QUAN_KEYS
    extra = set(block) - allowed
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong {mode}: {sorted(extra)}")
    dur = round(tuning[mode]["duration_s"] * tuning["tick_hz"])
    if "time_left_ticks" in block:
        t = block["time_left_ticks"]
        if isinstance(t, bool) or not isinstance(t, int) or not (1 <= t <= dur):
            raise BadInput(f"time_left_ticks phải là số nguyên trong [1, {dur}]")
    if mode == "gather":
        _validate_gather(block, tuning)
    else:
        _validate_quan(block, tuning)


def _num(v):
    return type(v) is int or (type(v) is float and math.isfinite(v))


def _nonneg_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise BadInput(f"{name} phải là số nguyên không âm")


def _pos(name, pos, bounds, axes=("x", "d")):
    if not (isinstance(pos, list) and len(pos) == 2 and all(_num(c) for c in pos)):
        raise BadInput(f"{name} phải là [{axes[0]}, {axes[1]}]")
    for c, axis in zip(pos, axes):
        lo, hi = bounds[axis]
        if not (lo <= c <= hi):
            raise BadInput(f"{name} nằm ngoài vùng nước ({axis} ∈ [{lo}, {hi}])")


def _validate_gather(b, tuning):
    g = tuning["gather"]
    bounds = g["bounds"]
    for arr in ("nodes", "fish", "monsters"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "random_fish" in b and not isinstance(b["random_fish"], bool):
        raise BadInput("random_fish phải là boolean")
    if "hold" in b:
        h = b["hold"]
        kinds = ingredient_kinds(tuning)
        if "freshness" in tuning:
            validate_individuals(h, kinds)
        elif not isinstance(h, list) or any(not isinstance(k, str) or k not in kinds for k in h):
            raise BadInput("hold phải là mảng id nguyên liệu hợp lệ")
        if len(h) > g["hold_capacity"]:
            raise BadInput("hold vượt sức chứa")
    p = b.get("player", {})
    if not isinstance(p, dict):
        raise BadInput("player phải là object")
    extra = set(p) - GATHER_PLAYER_KEYS
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong gather.player: {sorted(extra)}")
    if "pos" in p:
        _pos("player.pos", p["pos"], bounds)
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, d]")
    if "heading_deg" in p and not _num(p["heading_deg"]):
        raise BadInput("player.heading_deg phải là số")
    for key in ("invuln_ticks", "catch_cd_ticks", "zero_oxy_ticks", "oxygen_ticks", "hp"):
        if key in p:
            _nonneg_int(f"player.{key}", p[key])
    omax = round(g["oxygen_max_s"] * tuning["tick_hz"])
    if "oxygen_ticks" in p and p["oxygen_ticks"] > omax:
        raise BadInput("player.oxygen_ticks vượt oxy tối đa")
    if "hp" in p and not (1 <= p["hp"] <= g["hp_max"]):
        raise BadInput("player.hp phải trong [1, hp_max]")
    if "zero_oxy_ticks" in p:
        pos = p.get("pos", g["start_pos"])
        oxy = p.get("oxygen_ticks", omax)
        if p["zero_oxy_ticks"] > 59:
            raise BadInput("player.zero_oxy_ticks phải trong [0, 59]")
        if p["zero_oxy_ticks"] > 0 and not (oxy == 0 and pos[1] > g["surface_depth"]):
            raise BadInput("player.zero_oxy_ticks > 0 chỉ khi oxy = 0 và đang dưới nước")
    for n in b.get("nodes", []):
        if n.get("kind") not in NODE_KINDS:
            raise BadInput(f"nodes.{n['id']}: kind phải là một trong {NODE_KINDS}")
        _pos(f"nodes.{n['id']}.pos", n.get("pos"), bounds)
        if n["pos"][1] != 0:
            raise BadInput(f"nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
        if "regrow_ticks" in n:
            _nonneg_int(f"nodes.{n['id']}.regrow_ticks", n["regrow_ticks"])
    for f in b.get("fish", []):
        if set(f) - {"id", "kind", "pos", "heading_deg", "age_ticks"}:
            raise BadInput(f"fish.{f['id']}: có trường không hợp lệ")
        if f.get("kind") not in FISH_KINDS:
            raise BadInput(f"fish.{f['id']}: kind phải là một trong {FISH_KINDS}")
        _pos(f"fish.{f['id']}.pos", f.get("pos"), bounds)
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"fish.{f['id']}: đàn cá phải ở dưới nước")
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"fish.{f['id']}.heading_deg phải là số")
        if "age_ticks" in f:
            _nonneg_int(f"fish.{f['id']}.age_ticks", f["age_ticks"])
    for monster in b.get("monsters", []):
        _validate_monster(monster, g)


def _validate_monster(monster, gather):
    name = f"monsters.{monster['id']}"
    keys = {"id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left", "recoil_dir"}
    kind = monster.get("kind")
    species = gather.get("monsters", {}).get("species", {})
    if set(monster) - keys or not isinstance(kind, str) or kind not in species:
        raise BadInput(f"{name}: loài hoặc trường không hợp lệ")
    bounds = dict(gather["bounds"], d=species[kind]["depths"])
    _pos(f"{name}.pos", monster.get("pos"), bounds)
    waypoints = monster.get("waypoints")
    if not isinstance(waypoints, list) or len(waypoints) != 2:
        raise BadInput(f"{name}.waypoints cần đúng hai điểm")
    for point in waypoints:
        _pos(f"{name}.waypoints", point, bounds)
    target = monster.get("target_idx", 1)
    if type(target) is not int or target not in (0, 1):
        raise BadInput(f"{name}.target_idx phải là 0 hoặc 1")
    state, ticks = monster.get("state", "patrol"), monster.get("state_ticks_left", 0)
    _nonneg_int(f"{name}.state_ticks_left", ticks)
    if state not in ("patrol", "chase", "recoil") or (state == "recoil") != (ticks > 0):
        raise BadInput(f"{name}: trạng thái hoặc timer không hợp lệ")
    direction = monster.get("recoil_dir")
    if state == "recoil":
        if (not isinstance(direction, list) or len(direction) != 2 or not all(_num(c) for c in direction)
                or not math.isclose(math.hypot(*direction), 1, abs_tol=1e-6)):
            raise BadInput(f"{name}.recoil_dir phải là vector đơn vị")
    elif direction is not None:
        raise BadInput(f"{name}.recoil_dir chỉ dùng khi recoil")


def _validate_quan(b, tuning):
    for name, allowed in QUAN_ENTITY_KEYS.items():
        if name in b:
            _check_ids(name, b[name])
            for entity in b[name]:
                extra = set(entity) - allowed
                if extra:
                    raise BadInput(f"{name}.{entity['id']}: trường lạ {sorted(extra)}")
    if "stock" in b:
        validator = validate_individuals if "freshness" in tuning else validate_items
        validator(b["stock"], ingredient_kinds(tuning))
    p = b.get("player", {})
    if not isinstance(p, dict) or set(p) - QUAN_PLAYER_KEYS:
        raise BadInput("quan.player chỉ có pos và vel")
    qb = tuning["quan"]["bounds"]
    if "pos" in p:
        _pos("player.pos", p["pos"], qb, axes=("x", "z"))
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, z]")
    for name in ("stoves", "tables"):
        known = {fixture["id"] for fixture in tuning["quan"][name]}
        for fixture in b.get(name, []):
            if fixture["id"] not in known:
                raise BadInput(f"{name}.{fixture['id']}: không có trong tuning")
            if "pos" in fixture:
                _pos(f"{name}.{fixture['id']}.pos", fixture["pos"], qb, axes=("x", "z"))
