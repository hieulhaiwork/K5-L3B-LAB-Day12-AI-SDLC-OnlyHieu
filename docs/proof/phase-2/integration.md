# Phase 2 — smoke bàn giao kho từ gather sang quán

Dựng hai fixture JSON với seed 42.

```json
{"gather":{"hold":["ca_loc","ca_linh","ca_linh","ca_keo","bong_dien_dien","bong_sung","bong_sung","keo_neo"]}}
```

```json
{"frames":[{"tick":0,"interact":true}]}
```

Lưu hai fixture thành `dock.json` và `dock-inputs.json`, rồi chạy hai tiến trình từ thư mục gốc.

```bash
python3 -m chonoi.headless --mode gather --seed 42 --scenario dock.json --inputs dock-inputs.json --ticks 1 --out gather.jsonl --inventory-out stock.json
python3 -m chonoi.headless --mode quan --seed 42 --inventory stock.json --ticks 0 --out quan.jsonl
```

Kết quả thực tế trên nhánh `feat/quan`. Hai tiến trình đều trả mã `0`. `gather_end` tại tick 1 trả `reason: docked` và `inventory` trùng nội dung `stock.json`.

```json
{"items":{"bong_dien_dien":1,"bong_sung":2,"ca_keo":1,"ca_linh":2,"ca_loc":1,"keo_neo":1}}
```

Snapshot quán tại tick 0 có `stock` đúng bằng `items` ở trên. Kịch bản lặp lại được bằng `test_two_process_inventory_handoff_includes_all_six_ingredients` trong [test_quan_p2.py](../../../tests/test_quan_p2.py).
