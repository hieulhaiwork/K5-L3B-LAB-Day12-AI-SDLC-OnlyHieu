# Phase 1 — Kiểm chứng phần quán

Chạy trên PowerShell từ thư mục gốc.

```powershell
$env:PYTHONPATH = 'tests;.'
python3 -m unittest discover -s tests -v
```

Kết quả 41/41 test qua, gồm 9 test phần quán trong [test_quan_p1.py](../../../tests/test_quan_p1.py). Test tích hợp công khai chạy hai tiến trình `gather` và `quan` với kho `{"items":{"bong_sung":2,"ca_loc":1}}` và đọc đúng `stock` ở tick 0.

Kiểm tra thêm API live trên cổng tạm. `GET /state` trả về khách `C1` ở bàn `T1`, đơn `reserved`, sự kiện `customer_arrived` với `order_id`, `table_id`, `dish_id` và `error: null`. Chạy hàm vẽ HUD bằng Node với Canvas giả lập để xác nhận tên món đọc được từ payload và kho hiển thị 1 cá lóc khả dụng khi tồn vật lý là 2, đã giữ 1.

| Kịch bản | Kết quả quan sát |
|---|---|
| Nạp kho có một cá lóc và chơi trọn ca headless hai lần với seed 1 | Hai JSONL giống từng byte. Khách giữ một cá lúc tick 120, bếp trừ kho tại tick 121, món chín và được lấy tại 481, phục vụ tại 621, khách trả tiền trước `quan_end` tại 1221. Giá 60, boa 12, thu 72, uy tín 3,2, điểm 372. |
| Hai bàn và một phần nguyên liệu trong test nội bộ | Bàn còn trống nhận `no_dish` với payload `{}` khi nguyên liệu đang được giữ. Khi khách bỏ đi, lượt đến tiếp theo dùng lại nguyên liệu đó. |
| Khách bỏ đi khi món đang nấu hoặc trên tay | Bếp hoặc tay được giải phóng, bàn trống, uy tín giảm trong giới hạn. |
| Bếp và bàn cùng khoảng cách, phục vụ ở tick kiên nhẫn về 0 | Bếp được chọn trước. Món chín có `ready_ticks: 0`. Phục vụ ở tick kiên nhẫn về 0 vẫn hợp lệ, boa bằng 0. |
| Phục vụ tại tick đóng ca | Ngay tick 1 có `served`, `paid` với `reason: closing`, rồi `quan_end`. Giá đã chốt 63, boa làm tròn xuống 12, tổng 75. |
| Khách còn chờ lúc đóng ca | Khách rời với `closing`, giải phóng phần giữ và giữ nguyên uy tín. Lượt khách mới cùng tick bị bỏ qua. |
| Nhiều đơn đến bếp và đơn `unfulfillable` | Chọn theo `order_tick` rồi ID bàn, liệt kê món nguyên liệu theo kind. Đơn `unfulfillable` vẫn chờ và bếp bỏ qua. |
| Fixture mâu thuẫn hoặc ngoài biên | CLI thoát mã `2` trước khi tạo JSONL cho fixture thiếu giá/boa khi đang ăn, món sai đơn, một đơn có hai món, timer sai, giữ quá tồn, trường lạ hoặc tọa độ bàn ngoài miền. |

Thay đổi ở starter gồm kiểm trường và tọa độ fixture trong `chonoi/scenario.py`, dùng hậu tố số ASCII theo PRD-0 D trong `chonoi/ids.py`, và đọc payload món cùng phần kho giữ chỗ trong `chonoi/web/index.html`. `QuanSim` kiểm tra mâu thuẫn sau khi đã có kho thực tế, kể cả kho nạp bằng `--inventory`. Các câu hỏi về PRD-0 đã được giải đáp trong [Clarify](../../clarify.md).
