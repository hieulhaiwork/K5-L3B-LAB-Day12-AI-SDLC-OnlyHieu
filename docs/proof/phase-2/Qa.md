# Bằng chứng Honggam1109

Kiểm tại working tree dựa trên `main` `6b09191`, Python 3.12 trên Windows. Kết quả là lần chạy trước khi bàn giao tag.

```powershell
$env:PYTHONPATH = 'tests;.'
python -m unittest discover -s tests -q
python -m chonoi.headless --mode day --days 1 --seed 42 --ticks 22200 --out day.jsonl
python -m chonoi.headless --mode day --days 5 --seed 42 --ticks 111000 --out days.jsonl
```

| Ca kiểm | Kết quả local |
|---|---|
| Regression toàn repo | 63/63 test đạt, gồm smoke kho sáu nguyên liệu. |
| Một Ngày không thao tác | Kết ca sáng tại 10.800, ca tối tại 21.600 và Shop tại 22.200 tick. `reason=days_complete`, `days_completed=1`. Khoảng 0,73 giây. |
| Năm Ngày, seed 42 | Mục tiêu nguyên liệu có tổng 9, 10, 12, 9, 10 theo thứ tự. Kết ở tick 111.000 với `days_completed=5`. Khoảng 2,57 giây. |
| Hai Ngày với fixture 200k | Kho chuyển đúng, Shop đứng đồng hồ khi pause. Mua oxy đúng giá ở Ngày 1, chỉ tăng oxy tối đa lên 2.700 tick từ Ngày 2. Hai JSONL giống nhau từng byte. |
| Shop và đầu vào lỗi | Thiếu tiền và lệnh lạ có `buy_failed`. Mua ở tick cuối trước `shop_end(done)`. `--days` sai và `quan.stock` trong `day` trả mã 2 trước khi tạo output. |
| UI + API live | JavaScript chạy với DOM/Canvas giả lập và HTTP thật. Qua menu, hai màn giới thiệu, kết quả, Shop, pause, mua oxy rồi sang Ngày 2. FPS và trình bày trên trình duyệt thực còn cần kiểm. |

Điều chỉnh regression P1 theo TICKET-02 §1.1, §4.1. Số đàn mặc định đổi từ 6 sang 8 và `day` được hỗ trợ. Test vẫn kiểm vị trí đàn không trùng, mode cũ trả mã lỗi và luồng Gather → Quán. Kỳ vọng mới cho `day` nằm trong [test_day_p2.py](../../../tests/test_day_p2.py).
