# Lượt kiểm Phase 4

Working tree dựa trên `f0a434f`. Windows, Python 3.12.10, Node.js 22.23.2, Chromium 157. Kết quả dùng để đối chiếu [AC Phase 4](../../verification/phase-4.md).

| Lệnh | Kết quả |
|---|---|
| `python -m unittest discover -s tests -q` với `PYTHONPATH=tests;.` | 88 test đạt. Giữ nguyên kỳ vọng các test cũ. |
| `python -m tests.test_phase4 --browser docs/proof/phase-4` | Điều khiển qua Chromium thật. Tạm dừng đứng tick, chơi tiếp, bắt cá I1, nhập kho giữ I1, nấu và giao ở T1, thu 58k, mua bình oxy cấp 1, đóng Shop và thấy tổng kết. Cả ba cảnh báo thấy ở tương phản cao. Bố cục 390×844 không cuộn ngang, không có lỗi JavaScript. Fixture giảm thời gian ca và đặt trước khách để kiểm nhanh, dùng mô phỏng thật. |
| `python -m chonoi.bench --seed 42 --duration 30 --out docs/proof/phase-4/bench.json` | 1.801 khung đã vẽ trong 30,016 giây sau 3 giây làm nóng. 60,002 FPS trung bình, 44,393 FPS mức 1% thấp, tải 1.082,622 ms. [Dữ liệu benchmark](bench.json) |
| `python -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json` | 10/10 lượt đóng Shop, 0 crash. Lượt 10 đạt tổng thu 258k, uy tín 4,2, điểm 658. Test gọi lệnh khai trong manifest hai lần và đối chiếu dữ liệu bỏ `duration_s`. [Dữ liệu soak](soak.json) |
| So với `git archive f0a434f` | Chạy cùng seed 42. Gather (1.200 tick, 125 dòng), Quán (1.200 tick và kho mẫu, 124 dòng) và day (5 Ngày, 11.222 dòng) cho JSONL giống từng byte. Manifest chỉ đổi bốn lệnh gọi sang `python3`. |
| ZIP sạch trên Ubuntu WSL, Python 3.12.3 | Giải nén vào thư mục tạm. `run_cmd` mở được Canvas, `/pixel.js` và `/state` qua localhost. `headless_cmd --mode day --days 1 --seed 42 --ticks 22200` ghi 2.246 dòng, kết thúc `days_complete` trong 1,777 giây. Chạy toàn bộ 88 test trực tiếp trong thư mục giải nén, đều đạt. |

[Menu](menu.png) · [Thủy quái và oxy](gather-contrast.png) · [Khách sắp giận](quan-contrast.png) · [Quán đang nấu](quan.png) · [Mua oxy trong Shop](shop.png)

Các file `bench.json` và `soak.json` tại gốc là phép đo lưu từ trước Phase 4 này. Dùng bản trong thư mục này để đối chiếu.

Khung live phục vụ thêm module đồ họa và xử lý ngắt kết nối khi trình duyệt đóng. Gameplay và xác thực đầu vào tiếp tục đi qua mô phỏng hiện có.
