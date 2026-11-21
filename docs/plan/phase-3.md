# Phase 3 — tác động và thứ tự tích hợp

| Lát | File chính | Kiểm chứng | Người ghi nhận |
|---|---|---|---|
| Schema và bộ đọc | `inventory.py`, `freshness.py`, `scenario.py`, `contract.py`, `jsonl.py`, `game.contract.json` | AC-P3-01 | ThinkLee04 |
| Gather | `sim/gather.py` | AC-P3-02 | ThinkLee04 |
| Quán | `sim/quan.py` | AC-P3-03 | ThinkLee04 |
| Vòng ngày và UI | `runner.py`, `inputs.py`, `headless.py`, `live.py`, `web/index.html` | AC-P3-04, AC-P3-05 | ThinkLee04 |

Chốt schema và cách biểu diễn độ tươi trước. Nối Gather và Quán với cùng bộ kiểm cá thể, sau đó nối bàn giao trong `day` và cập nhật HUD. Bật manifest v1.2 trên cùng tập thay đổi sau khi smoke đi qua cả hai đầu. Giữ test chuyển pha, sự kiện và tính tất định của Phase 1–2. Chuyển các fixture còn dùng kho đếm và cập nhật kỳ vọng giá theo độ tươi.
