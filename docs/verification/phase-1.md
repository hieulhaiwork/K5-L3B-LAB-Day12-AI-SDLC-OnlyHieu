# Ma trận truy vết Phase 1

TV3 kiểm trên `main` local `9e9e0b5` cùng các thay đổi kiểm thử bên dưới. Chạy lại bộ test trên commit bàn giao trước khi gắn `phase-1`.

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Headless v1.0 — CLI, JSONL, seed và đầu vào sai (mục B–E) | Chạy smoke công khai cho hai mode, snapshot/event/end, so đầu ra lặp và kiểm mã lỗi. | [Kết quả TV3](../proof/phase-1/qa-baseline.md) | Đạt các ca đã chạy. |
| Gather — di chuyển, oxy, ngạt, hái/bắt và sức chứa (mục F) | Chạy 11 test Gather và các ca di chuyển của smoke công khai. | [Kết quả TV3](../proof/phase-1/qa-baseline.md) | Đạt các ca đã chạy. |
| Gather → Quán — xuất/nạp kho (mục G) | Chạy smoke hai tiến trình với giỏ mẫu. Kiểm `tick_limit` giữ file kho cũ. | [Kết quả TV3](../proof/phase-1/qa-baseline.md#tích-hợp-hai-tiến-trình) | Đạt. `gather_end`, file kho và `quan.stock` tại tick 0 khớp nhau. |
| Gather → Quán — bắt cá, nấu, bưng, phục vụ và nhận tiền (mục F–G) | Bắt một cá lóc từ giỏ rỗng. Quán nạp file Gather vừa ghi, nấu và bán đúng món. | [Test tích hợp và kết quả](../proof/phase-1/qa-baseline.md#tích-hợp-hai-tiến-trình) | Đạt. Thu 72 nghìn đồng, điểm 372 theo preset. |
| Quán — khách đến, gọi món, giữ nguyên liệu, bỏ đi | Chạy lịch khách trên hai bàn với một phần nguyên liệu, rồi kiểm tra kho và uy tín khi khách rời. | [Quán Phase 1](../proof/phase-1/quan.md) | Đạt theo test hiện có |
| Quán — nấu, lấy món, phục vụ, thanh toán, kết ca | So sánh JSONL của hai lần chạy. Kiểm tra thứ tự đơn, payload sự kiện, phục vụ lúc kiên nhẫn về 0 và thu tiền khi đóng ca. | [Quán Phase 1](../proof/phase-1/quan.md) | Đạt theo test hiện có |
| Quán — từ chối đầu vào mâu thuẫn | Chạy fixture thiếu trường, giữ quá kho, gán món trùng hoặc có bàn ngoài biên. | [Quán Phase 1](../proof/phase-1/quan.md) | Đạt theo test hiện có |
| Quán — chạy lại ba lỗi trước tích hợp | Chạy tới tick 120 với kho rỗng và kho chỉ đủ nấu gỏi. Thử fixture giữ cá vượt tồn. | [Kết quả chạy lại](../proof/phase-1/qa-baseline.md#kiểm-lại-quán) | Đạt. Có `no_dish`, `customer_arrived` đúng tick và mã `2` trước khi ghi JSONL. |
| HUD hai buổi (mục 2, 7) | Chạy thao tác qua API live và kiểm hàm vẽ với snapshot đại diện. | [Live và HUD](../proof/phase-1/qa-baseline.md#live-và-hud) | Đạt phần API và các nhãn đã kiểm. Chơi thử trực tiếp trên trình duyệt còn mở. |
| CI và danh sách nhóm | Chạy lệnh build, bộ test và `tools/check_team.py` riêng. | [Kết quả TV3](../proof/phase-1/qa-baseline.md) | Build và test local đạt. Checker trả mã `1` vì nhóm 3 người. Trạng thái GitHub Actions chưa xác minh. |
| Điều kiện bàn giao (mục 7) | Đối chiếu README, tài liệu hợp đồng và mốc `phase-1`. | [Điều kiện còn mở](../proof/phase-1/qa-baseline.md#điều-kiện-còn-mở) | Còn mục cần chủ file xử lý. Commit và tag bàn giao chờ nhóm thực hiện. |

## Đánh giá ngắn

- Bản tích hợp qua 53 test local. Ca đầu cuối xác nhận nguyên liệu bắt ở Gather là nguyên liệu Quán dùng để thu tiền.
- Kiểm lại trên commit bàn giao và hoàn tất các mục còn mở trong bằng chứng TV3.
