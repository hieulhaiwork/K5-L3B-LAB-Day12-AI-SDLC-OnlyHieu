"""Đọc kho theo phiên bản contract và ghi qua file tạm cùng thư mục."""

import json
import os
import tempfile
from decimal import Decimal

from .errors import BadInput
from .freshness import validate_individuals
from .ids import sort_by_id
from .jsonl import dumps

KINDS_P1 = (
    "ca_loc",
    "ca_linh",
    "ca_keo",
    "bong_dien_dien",
    "bong_sung",
    "keo_neo",
)


def ingredient_kinds(tuning):
    return {kind for dish in tuning["menu"].values() for kind in dish["recipe"]}


def validate_items(items, kinds=KINDS_P1):
    if not isinstance(items, dict):
        raise BadInput("items phải là object")
    out = {}
    for k, v in items.items():
        if k not in kinds:
            raise BadInput(f"nguyên liệu lạ: {k}")
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"số lượng không hợp lệ cho {k}: {v!r}")
        if v > 0:
            out[k] = v
    return out


def read_inventory(path: str, kinds=KINDS_P1, contract_version="1.1"):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f, parse_float=Decimal)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    validator = validate_individuals if contract_version == "1.2" else validate_items
    return validator(data["items"], kinds)


def hold_to_items(hold: list) -> dict:
    """Khoang (mảng id theo thứ tự nhặt) -> object đếm, sắp theo id nguyên liệu."""
    counts = {}
    for k in hold:
        counts[k] = counts.get(k, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def write_inventory(path: str, items):
    if isinstance(items, list):
        items = sort_by_id(items)
    else:
        items = {k: items[k] for k in sorted(items) if items[k] > 0}
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps({"items": items}) + "\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
