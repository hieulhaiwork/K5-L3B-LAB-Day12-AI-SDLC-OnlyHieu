# Phase 3 — bằng chứng kho cá thể

```powershell
$repoPython = Split-Path -Parent (python3 -c 'import sys; print(sys.executable)')
$env:PATH = "$repoPython;$env:PATH"
$env:PYTHONPATH = 'tests;.'
python -m unittest discover -s tests
```

Kết quả **73/73 test qua** trên bản gộp khi rebase lên `main` tại `2f95253`, gồm mười test v1.2 trong [test_freshness_p3.py](../../../tests/test_freshness_p3.py) và bốn test vòng ngày từ `main` đã chuyển sang fixture cá thể.

- **Từ file.** Gather cập bến ở tick 1 với mức tươi đầu kỳ `30.00834`. File và snapshot Quán tick 0 chứa cùng ID, loại và số độ tươi nằm trên 30. Bản v1.2 trả mã `2` cho file đếm trước khi tạo đầu ra.
- **Ngưỡng và LIFO.** Cá thể đúng 30 phát `spoiled` ở bước hoạt động đầu tiên. Cùng tick phát theo ID. Cá sấu gây hit rồi ngất, bỏ lần lượt `I4`, `I3` rồi `I2`, `I8`, đóng Gather với `items: []`.
- **Giữ lại và giá.** Hai cá thể qua ngưỡng ở cùng tick. Đơn cũ được giữ lại trước và nấu bằng `I3`, đơn sau thành `unfulfillable`. Giá ở biên được làm tròn từ giá trị trước khi định dạng.
- **Trong day.** Quán nhận kho có `I7` tại `phase_tick: 0`. Ngày 2 cấp `I8` với độ tươi ban đầu và áp dụng bình oxy cấp 1. Chạy hai lượt `python3 -m chonoi.headless --mode day --days 1 --seed 17 --ticks 22200 --out day.jsonl` với hai đường dẫn đầu ra cho JSONL giống từng byte, kết thúc `days_complete` ở tick 22.200. Thời gian local lần lượt 2,00 s và 1,93 s.
- **Live.** `GET /` trả HTTP 200. Bấm tương tác qua API tại bến chuyển từ Gather sang Quán với ID `I1`. Hàm vẽ kiểm ở 1280×720 cho thấy nhãn `Ươn`, độ tươi, kho khả dụng sau khi loại phần đã giữ và Shop. Sau khi tích hợp `6b09191`, mỗi Cá Sấu được vẽ đúng một lần, với màu riêng cho `chase` và `recoil`.
- **Tích hợp bản Gather của nhóm.** Chạy một ngày seed `1` từ bản đồ mặc định, giỏ rỗng. Hái N3 và N4, cập bến tại tick 1743, chuyển nguyên hai cá thể bông súng sang Quán cùng tick. Gỏi bông súng chốt giá 36k, boa 7k, thu 43k tại tick 2844. Đóng Shop bằng phím tại tick 12544 và nhận `days_complete`. Fixture bắt đầu với bình oxy và Máu cấp 1 nhận đúng giới hạn 2700 tick oxy và 4 Máu.
- **Kiểm tra khi rebase.** Hai lượt headless seed `17` với cùng fixture tạo JSONL giống từng byte. Giữ E qua cập bến và pause giữ `sim_tick` cùng độ tươi trong thời gian pause. Chỉ lần nhấn E mới bắt đầu nấu tại tick 7. API live giữ màn mở quán và Shop, đồng thời bàn giao cá thể vừa ươn tại `phase_tick: 0`. Chạy các hàm dựng HTML bằng Node để xác nhận màn mở quán, HUD và Shop hiển thị độ tươi, đồng thời loại nguyên liệu đã giữ và hàng ươn khỏi kho khả dụng.

Regression Phase 1–2 giữ lại kiểm tra gameplay và đổi fixture sang mảng cá thể. Ca cá lóc nấu sau khi đã hao tươi thu 59k tiền món và 11k boa. Test cấm `day` đã chuyển sang kiểm mode cũ `river`, vì `day` nay có CLI riêng.

## Kiểm chứng TV3 trên main sau tích hợp

Chạy trên `main` tại `ab3e92a` cùng thay đổi local của TV3, Windows và Python 3.12. Chạy `$env:PYTHONPATH = 'tests;.'` rồi `python -m unittest discover -s tests -q`: **85/85 test đạt**.

- `--scenario` và `--inventory` trả mã `2` trước khi tạo JSONL với độ tươi âm, lớn hơn 100, không hữu hạn hoặc có số mũ mà bộ đọc không biểu diễn được. Trước khi sửa, trường hợp số mũ vượt miền làm cả hai đường đọc thoát mã `1` với traceback. [Test CLI](../../../tests/test_freshness_p3.py)
- API live chuyển `I1` và `I2` sang Quán ở `phase_tick: 0`, stock khớp `gather_end`. `I1` dưới 30 theo số chính xác dù chuyển sang số JavaScript thành 30. API vẫn đánh dấu `I1` trong `spoiled_ids`. Kiểm với JavaScript, DOM/Canvas giả lập và HTTP thật xác nhận HUD hiển thị `Ươn`, loại `I1` khỏi kho khả dụng và hiển thị hàng ươn trong Shop. [Test live](../../../tests/test_live.py)
- Hai lượt `python -m chonoi.headless --mode day --days 1 --seed 17 --ticks 22200 --out day.jsonl` dùng hai đường dẫn đầu ra tạm khác nhau. JSONL giống từng byte, kết thúc `days_complete` ở tick 22.200 trong khoảng 2,58 và 2,19 giây trên máy local.
