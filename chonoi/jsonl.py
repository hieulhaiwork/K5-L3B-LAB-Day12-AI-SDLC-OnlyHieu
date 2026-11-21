"""Ghi JSONL tất định: làm tròn 3 chữ số khi XUẤT (tính toán dùng giá trị chính xác)."""

import json
from decimal import Decimal
from fractions import Fraction

from .freshness import fresh_decimal


def _encode(v):
    if isinstance(v, Fraction):
        return str(fresh_decimal(v))
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, float):
        r = round(v, 3)
        v = 0.0 if r == 0 else r
    if isinstance(v, dict):
        return "{" + ",".join(_encode(k) + ":" + _encode(x) for k, x in v.items()) + "}"
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(_encode(x) for x in v) + "]"
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def dumps(obj) -> str:
    return _encode(obj)


class JsonlWriter:
    def __init__(self, path: str):
        self._f = open(path, "w", encoding="utf-8", newline="\n")

    def write(self, obj):
        self._f.write(dumps(obj) + "\n")

    def close(self):
        self._f.close()
