"""Tính và kiểm mục tiêu thu gom của một Ngày từ công thức thực đơn."""

from collections import Counter

from .errors import BadInput


def normalize_day_plan(entry, menu):
    if (not isinstance(entry, dict) or set(entry) - {"day", "dishes", "ingredients"}
            or type(entry.get("day")) is not int or not 1 <= entry["day"] <= 5):
        raise BadInput("day_plan: mỗi mục cần day nguyên từ 1 đến 5")
    dishes = entry.get("dishes")
    if not isinstance(dishes, dict) or not dishes:
        raise BadInput("day_plan.dishes phải là object có ít nhất một món")

    ingredients = Counter()
    for dish_id, servings in dishes.items():
        if dish_id not in menu or type(servings) is not int or servings <= 0:
            raise BadInput(f"day_plan.dishes: món hoặc số suất không hợp lệ ({dish_id!r})")
        for kind, amount in menu[dish_id]["recipe"].items():
            ingredients[kind] += amount * servings

    if "ingredients" in entry:
        declared = entry["ingredients"]
        if (not isinstance(declared, dict)
                or any(type(amount) is not int or amount <= 0 for amount in declared.values())
                or declared != dict(ingredients)):
            raise BadInput("day_plan.ingredients không khớp công thức và số suất")
    return {"day": entry["day"], "dishes": dict(sorted(dishes.items())),
            "ingredients": dict(sorted(ingredients.items()))}
