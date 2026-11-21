"""Kho cá thể v1.2 và phép tính độ tươi trước khi định dạng JSON."""

from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction

from .errors import BadInput
from .ids import sort_by_id


def validate_individuals(items, kinds):
    if not isinstance(items, list):
        raise BadInput("kho v1.2 phải là mảng cá thể")
    validated = []
    seen = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "kind", "fresh"}:
            raise BadInput("mỗi cá thể phải có đúng id, kind và fresh")
        ident, kind, fresh = item["id"], item["kind"], item["fresh"]
        if not isinstance(ident, str) or not ident or ident in seen:
            raise BadInput("id cá thể phải là chuỗi duy nhất, khác rỗng")
        if not isinstance(kind, str) or kind not in kinds:
            raise BadInput(f"nguyên liệu lạ: {kind!r}")
        if type(fresh) not in (int, float, Decimal, Fraction):
            raise BadInput("fresh phải là số hữu hạn trong [0, 100]")
        try:
            fresh = exact(fresh)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            raise BadInput("fresh phải là số hữu hạn trong [0, 100]") from exc
        if not 0 <= fresh <= 100:
            raise BadInput("fresh phải trong [0, 100]")
        seen.add(ident)
        validated.append({"id": ident, "kind": kind, "fresh": fresh})
    return validated


def exact(value):
    return Fraction(str(value)) if isinstance(value, float) else Fraction(value)


def snapshot_items(items):
    return [dict(item) for item in items]


def fresh_decimal(value):
    # Dùng đủ chữ số để hai giá trị gần ngưỡng vẫn ở đúng phía khi đọc lại.
    numerator, denominator = Decimal(value.numerator), Decimal(value.denominator)
    with localcontext() as context:
        context.prec = max(40, numerator.adjusted() + denominator.adjusted() + 6)
        context.rounding = ROUND_CEILING
        return numerator / denominator


def decay(items, amount, threshold, location, events):
    spoiled = set()
    for item in items:
        before = item["fresh"]
        if before == 0:
            continue
        item["fresh"] = max(Fraction(0), before - amount)
        if before >= threshold > item["fresh"]:
            spoiled.add(item["id"])
    if spoiled:
        for item in sort_by_id(item for item in items if item["id"] in spoiled):
            events.append(("spoiled", {"item_id": item["id"], "kind": item["kind"], "location": location}))
    return spoiled
