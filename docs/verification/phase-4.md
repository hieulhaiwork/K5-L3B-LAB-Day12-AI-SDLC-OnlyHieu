# Ma trận kiểm chứng Phase 4

TICKET-04, Test Contract v1.3. Kết quả dưới đây thuộc working tree dựa trên `f0a434f`. Hai tag local `phase-4` và `v1.0.0` hiện trỏ tới `f0a434f`. Bằng chứng cần chạy lại trên commit bàn giao.

| AC | Cách kiểm và bằng chứng | Kết quả |
|---|---|---|
| AC-P4-01 — benchmark có render | Gọi `bench_cmd` với seed 42. Đo khung Canvas tại 1280×720, làm nóng 3 giây, đo 30 giây. Kiểm công thức 1% low và đủ năm trường. [JSON](../proof/phase-4/bench.json) · [Cách chạy](../proof/phase-4/run.md) | Đạt. 60,002 FPS trung bình, 44,393 FPS mức 1% thấp, tải 1,083 s. |
| AC-P4-02 — cảnh báo và tương phản | Dùng nút menu và phím C trong Chromium. Thử thủy quái và oxy thấp đồng thời, sau đó khách sắp giận. [Gather tương phản cao](../proof/phase-4/gather-contrast.png) · [Quán tương phản cao](../proof/phase-4/quan-contrast.png) | Đạt trên Chromium. |
| AC-P4-03 — chơi trọn ngày và hồi quy | Điều khiển thật qua trình duyệt, pause và chơi tiếp. Bắt cá, đối chiếu ID và độ tươi khi nhập Quán, nấu, phục vụ, thu 58k, mua oxy và đóng Shop. Chạy regression CLI P1–P3 và các ca P4. [Lượt chạy](../proof/phase-4/run.md) · [Shop](../proof/phase-4/shop.png) | Đạt local. 88 test đạt trên Windows và Ubuntu. Ba ca JSONL trùng từng byte với bản gốc. |
| AC-P4-04 — soak và trạng thái qua ngày | Gọi `soak_cmd` seed 7 hai lần và so mọi trường gameplay. Kiểm D1–D5 lặp lại ở ngày 6–10, ID và trạng thái xuyên ngày. [JSON](../proof/phase-4/soak.json) · [Test](../../tests/test_phase4.py) | Đạt 10/10, 0 crash, dữ liệu giống nhau khi bỏ thời gian. |
| AC-P4-05 — khởi chạy và đóng gói | Tạo ZIP bằng `python3 tools/package_release.py` rồi thử lệnh README từ thư mục vừa giải nén. Rà changelog, release notes và nguồn tài sản. [Cách chạy](../../README.md#bắt-đầu-nhanh) · [Bằng chứng](../proof/phase-4/run.md) | Đạt trên Ubuntu với ZIP sạch. Kiểm clone từ commit bàn giao và kiểm trên macOS chờ lượt CI sau khi nhóm đưa bản cuối lên. |
| AC-P4-06 — harness, tài liệu và retro | Hai skill, nhật ký AI, ghi làm rõ, rà hành động ở P2 và đối chiếu đóng góp từng thành viên với Git. [AGENTS](../../AGENTS.md) · [Retro](../retro.md) | Tài liệu local đầy đủ, bản nháp phản tư chờ thành viên xác nhận. Nhóm có 3 người, README yêu cầu 4–6. |
| AC-P4-07 — bàn giao và demo | Bản chơi, ma trận và bằng chứng dùng cho demo. Tag `phase-4` và Release `v1.0.0` phải cùng trỏ vào commit bàn giao trên main. [Release notes](../../RELEASE_NOTES.md) | Sẵn sàng demo local. Còn kiểm trên commit bàn giao và công bố Release do nhóm thực hiện. |

Local hiện chỉ có hai tag `phase-4` và `v1.0.0` ở bản gốc. Tình trạng tag các checkpoint trước và thời hạn nộp cần nhóm xác minh khi bàn giao.

[Phase 1](phase-1.md) · [Phase 2](phase-2.md) · [Phase 3](phase-3.md)
