# Kiểm chứng TV3 — Phase 1

Bản chạy là `main` local `9e9e0b5` cùng hai thay đổi test của TV3. `origin/main` được lưu tại `c6b22de`, hơn một commit chỉ cập nhật `docs/clarify.md`. Môi trường kiểm là PowerShell và Python 3.12.10 trên Windows.

```powershell
$env:PYTHONPATH = 'tests;.'
python -m unittest discover -s tests -v
python tools/check_team.py
```

Build theo `build_cmd` (`true`) và **53/53 test** đạt, gồm 11 test Gather, 9 test Quán và ca tích hợp mới. `git diff --check` đạt. Kiểm tra thực tế `tools/check_team.py` trả mã `1` vì roster có 3 người, đề yêu cầu 4–6. Bước này chỉ cảnh báo trong workflow hiện có. Kết quả build/test là local. Chưa xác minh được GitHub Actions vì CLI chưa đăng nhập và API công khai không kết nối được từ môi trường này.

## Tích hợp hai tiến trình

| Ca chạy | Kết quả thực tế |
|---|---|
| [Smoke mục G](../../../tests/test_smoke_p1.py#L201), seed `42` | `gather_end` ở tick 1 có `reason: docked`. Event và file kho cùng có `{"items":{"bong_sung":2,"ca_loc":1}}`. Quán nạp đúng `stock` ở tick 0. Cả hai tiến trình trả `0`. |
| [Bắt cá đến thu tiền](../../../tests/test_smoke_p1.py#L221), seed `42` | Gather bắt 1 cá lóc từ giỏ rỗng, ghi file kho khi hết giờ. Quán nạp file đó, khách gọi cá lóc nướng trui và quán tiêu đúng 1 cá lóc. Các event lần lượt là `customer_arrived`, `cook_started`, `dish_ready`, `dish_picked`, `served`, `paid`, `quan_end`. Kết ca với kho rỗng, thu 72 nghìn đồng, điểm 372. |
| Đích kho đã có sẵn, chạy Gather `--ticks 1` | Dòng cuối có `reason: tick_limit`. File kho giữ nguyên từng byte. |
| Chạy lặp cùng seed và đầu vào | Smoke Gather và test Quán có so sánh JSONL từng byte, cả hai đạt. |

## Kiểm lại Quán

| Tình huống chưa đạt ở `85e2796` | Kết quả trên bản tích hợp |
|---|---|
| Kho rỗng tại tick khách đầu tiên | Tick 120 phát `no_dish` với `{}`. |
| Kho có 2 bông súng tại tick khách đầu tiên | Tick 120 phát `customer_arrived`. Khách `C1` ở `T1` gọi `goi_bong_sung`, giữ đúng 2 bông súng. |
| Fixture giữ 1 cá lóc trong khi kho rỗng | Trả mã `2` trước khi tạo JSONL. |

## Live và HUD

- API live phục vụ trang Canvas cho cả hai chế độ. Gửi `catch` đến Gather tạo `fish_caught`, kết ca theo `time` và ghi file có 1 cá lóc. Quán dùng số liệu từ file đó, sinh khách giữ 1 cá lóc, nhận `interact` để bắt đầu nấu và trừ kho về rỗng. `GET /state` trả `error: null` tại các lần kiểm.
- Kiểm hàm vẽ bằng Node.js và Canvas giả lập. Gather hiện thời gian, `Oxy 5s`, Máu `♥♥♡`, `Giỏ 1/12`. Quán hiện tên món, kho khả dụng, tiền và uy tín. Ca có 2 bông súng bị giữ chỗ chỉ hiện 1 cá lóc khả dụng. Nhãn bếp rảnh, đang nấu, món đã chín và món trên tay đều qua kiểm tra.
- Lượt kiểm trực tiếp trên trình duyệt dừng vì công cụ không xác minh được URL Chrome. Kết quả API và hàm vẽ là các kiểm tra riêng. Chơi thử bằng phím và đọc HUD trực tiếp còn chờ xác nhận.

## Điều kiện còn mở

- TV1/PO xác nhận yêu cầu 4–6 với giảng viên cho nhóm 3 người. README cần bổ sung điều khiển và cách tính điểm theo DoD. Tài liệu hợp đồng hiện có kho mẫu. TV2 cần chốt mô tả schema và giao diện theo phân công.
- Chạy lại trên commit bàn giao và xác nhận GitHub Actions nếu nhóm dùng CI. Tag `phase-1` thuộc lượt bàn giao của nhóm.
