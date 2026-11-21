# Phase 2 — kiểm chứng lát quán

Chạy trên PowerShell trong thư mục gốc. Nếu `python` đang trỏ vào virtualenv hỏng, đưa thư mục Python đang chạy được lên đầu `PATH` của phiên hiện tại để cả tiến trình con trong smoke dùng đúng runtime.

```powershell
$quanPythonDir = Split-Path -Parent (python3 -c 'import sys; print(sys.executable)')
$env:PATH = "$quanPythonDir;$env:PATH"
$env:PYTHONPATH = 'tests;.'
python -m unittest discover -s tests -v
```

Kết quả **59/59 test qua**. Sáu test mới trong [test_quan_p2.py](../../../tests/test_quan_p2.py) kiểm các trường hợp sau.

| Kiểm chứng | Kết quả quan sát |
|---|---|
| Hai bếp và bốn bàn | B1 nấu đơn C1 trong khi B2 nấu C2. Lịch mặc định đưa khách tới T1–T4 ở tick 120, 1020, 1920 và 2820. T1 rảnh rồi nhận khách mới ở tick 3720. |
| Sáu món, kế hoạch D1–D5 | Công thức và giá ba món mới đúng preset. Tổng ô theo kế hoạch lần lượt là 9, 10, 12, 9, 10. Từ chối `ingredients` khai sai công thức. |
| Kế hoạch khi mở ca tối | Sau khi đã thu tiền một suất cá kèo nướng, hai khách tiếp theo vẫn gọi được món dù kế hoạch chỉ có một suất. Khi nguyên liệu khả dụng hết, phát `no_dish` dù kho còn cá lóc ngoài kế hoạch. |
| Bàn giao tiền, tổng thu và uy tín | Vào ca với tiền 50, tổng thu 250, uy tín 4,9. Thu 240 khi đóng ca, tiền cuối ca 290, tổng thu 490, tiền ca 240, uy tín kẹp ở 5. |
| Smoke hai tiến trình | Cả sáu mã nguyên liệu trùng giữa file kho và snapshot quán tick 0. [Chi tiết](integration.md) |
| API live và HUD | `GET /` và `/state` chạy được, API trả 2 bếp, 4 bàn, 6 món và tiền ca 84 trong fixture. Hàm vẽ tại 1280×720 dùng 18 px cho các nhãn quán, hiển thị kho đã trừ phần giữ, món trên tay, tiến độ bếp và đổi màu kiên nhẫn dưới 25%. |

Regression Phase 1 giữ kiểm tra thứ tự và payload cũ. Hai kịch bản quán một nguyên liệu, gồm ca QA bắt cá đến thanh toán, có thêm `no_dish` ở tick 1020 vì preset có thêm bàn trống trong lúc khách T1 đang ăn. Hai test thứ tự dùng bàn T2–T4 có sẵn trong preset mới.

## Bàn giao cho lát vòng ngày

Khi nhận `gather_end`, lấy `items` từ `inventory.items` trong sự kiện hoặc gọi `GatherSim.inventory_items()`. Dựng `QuanSim(tuning, quan_fixture, streams, ids, inventory=items, day_plan=plan, money=money, earned=earned, reputation=reputation)`. `plan` là mục `{day, dishes, ingredients}`. Dùng `normalize_day_plan` để tính và kiểm nguyên liệu của kế hoạch tùy chỉnh. Quán kiểm lại món của khách và phần giữ với kho thực ngay khi dựng. Khi `quan_end`, dùng `sim.stock` của quán cho kho dư Shop. Tiền, tổng thu và uy tín có trên `sim` và `quan_end`, còn `shift_earned` bắt đầu từ 0 ở đầu mỗi ca.

`game.contract.json` cập nhật `quan`, `menu` và `day_plan`. `inventory.py`, `scenario.py`, `headless.py` và `live.py` dùng danh sách nguyên liệu từ thực đơn, giữ nguyên schema `{"items":{...}}`. `live.py` gửi tiền ca và thời gian nấu cho HUD qua API màn hình. `contract.py` kiểm công thức và kế hoạch khai trong manifest. `gather` Phase 2, CLI `day`, Shop và pause cần được tích hợp trước khi nghiệm thu toàn phase.
