# Phase 3 — tác động và thứ tự tích hợp

**1:55–2:30.** Chuyển sang kho cá thể v1.2, đọc đúng độ tươi và giữ được hồi quy của các phase trước. Bảng dưới ghi nhận tác động kỹ thuật và người tổng hợp. Phân công thực hiện theo [vai trò nhóm](../../TEAM.md).

| Lát | File chính | Kiểm chứng | Người ghi nhận |
|---|---|---|---|
| Schema và bộ đọc | `inventory.py`, `freshness.py`, `scenario.py`, `contract.py`, `jsonl.py`, `game.contract.json` | AC-P3-01 | ThinkLee04 |
| Gather | `sim/gather.py` | AC-P3-02 | ThinkLee04 |
| Quán | `sim/quan.py` | AC-P3-03 | ThinkLee04 |
| Vòng ngày và UI | `runner.py`, `inputs.py`, `headless.py`, `live.py`, `web/index.html` | AC-P3-04, AC-P3-05 | ThinkLee04 |

Chốt schema và cách biểu diễn độ tươi trước. Nối Gather và Quán với cùng bộ kiểm cá thể, sau đó nối bàn giao trong `day` và cập nhật HUD. Bật manifest v1.2 trên cùng tập thay đổi sau khi smoke đi qua cả hai đầu. Giữ test chuyển pha, sự kiện và tính tất định của Phase 1–2. Chuyển các fixture còn dùng kho đếm và cập nhật kỳ vọng giá theo độ tươi.

| Đầu việc | Phụ trách | Phụ thuộc và cách nghiệm thu |
|---|---|---|
| Cấp ID khi thu thập, hao độ tươi và rơi hàng theo LIFO. Ghi quyết định đổi schema. | hieulhaiwork | Dùng bộ kiểm kho cá thể đã chốt. Kiểm hàng vừa qua ngưỡng 30, kho rỗng khi ngất và file giữ nguyên khi chưa kết ca. |
| Giữ chỗ theo ID, thử giữ lại khi hàng vừa ươn và chốt giá lúc bắt đầu nấu. | ThinkLee04 | Dùng fixture cá thể song song với Gather. Kiểm thứ tự giữ chỗ, giá làm tròn xuống và boa theo giá đã chốt. |
| Nối cả hai đường bàn giao, HUD và hồi quy. | Honggam1109 | Chờ Gather xuất và Quán đọc cùng schema. So file với snapshot Quán tick 0, kiểm ID và độ tươi qua `day`, rồi lưu kết quả. [Bằng chứng Phase 3](../proof/phase-3/freshness.md) |

**Mốc theo đề.** Phút 0–7 chốt tác động và thứ tự tích hợp. Phút 7–25 triển khai song song, smoke kho và standup ở phút 20. Phút 25–32 bật v1.2 trên bản tích hợp, chạy hồi quy và chốt bằng chứng. Phút 32–35 dự phòng và bàn giao `phase-3`.

**Rủi ro và bàn giao.** Kho đếm trả mã 2 khi chạy v1.2. So ngưỡng 30 và chốt giá trước khi làm tròn dữ liệu hiển thị. Ghi breaking change và cách sửa fixture trong [CHANGELOG](../../CHANGELOG.md). [Ma trận Phase 3](../verification/phase-3.md)
