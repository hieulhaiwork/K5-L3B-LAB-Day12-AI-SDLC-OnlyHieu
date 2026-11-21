# Changelog
## v1.0.0

### Phase 4 — Phát hành, Test Contract v1.3

- Giao diện Pixel Art cho sông, khách và nhà bè, với chế độ tương phản cao và cảnh báo bằng chữ cho thủy quái, oxy và kiên nhẫn.
- Benchmark đo khung Canvas thật ở 1280×720. Soak chạy 10 ngày trong cùng tiến trình, thêm test lặp seed và giữ trạng thái qua ngày thứ sáu.
- Thêm gói ZIP nguồn, hướng dẫn chạy và ma trận nghiệm thu. Gameplay và JSONL giữ quy tắc v1.2. [Ma trận Phase 4](docs/verification/phase-4.md)

### Phase 3 — Mùa Nước Nổi, Test Contract v1.2

- **Breaking change.** `items` đổi từ map số lượng sang mảng `{id, kind, fresh}`. Kho rỗng dùng `{"items":[]}`. File kho đếm trả mã thoát `2` với v1.2.
- Chuyển fixture `gather.hold` và `quan.stock` thành mảng cá thể với ID duy nhất. Đổi `customers[].reserved` thành mảng ID trỏ đúng kho. Bỏ trường `reserved` để quán tự giữ theo công thức và độ tươi.
- Gather và Quán giảm độ tươi theo tick, phát `spoiled` đúng lần qua ngưỡng 30. Quán thử giữ lại khi hàng ươn, dùng giá theo độ tươi lúc nấu và tính boa từ giá đã chốt.
- `day` chuyển kho cá thể trực tiếp sang Quán rồi sang Shop. Pause dừng hao tươi. Cấp oxy và Máu mua trong Shop áp dụng từ ngày kế tiếp.
- Test hồi quy đổi kịch bản kho và kỳ vọng giá theo v1.2. Giữ kiểm tra tồn kho, thao tác, thời điểm thanh toán và kết ca. [Ma trận Phase 3](docs/verification/phase-3.md)

### Phase 2 — Vòng ngày, Test Contract v1.1

- Cập nhật số chuẩn, sáu nguyên liệu/món, Cá Sấu Năm Chèo, hai bếp và bốn bàn. Nối Gather, Quán, kết quả ngày, Shop và tổng kết năm ngày.
- Bổ sung kế hoạch D1–D5, pause, nâng cấp oxy và Máu có hiệu lực từ ngày sau. [Ma trận Phase 2](docs/verification/phase-2.md)

### Phase 1 — Hai ca độc lập, Test Contract v1.0

- Hoàn thành lặn, hái, bắt cá, bến và bàn giao kho giữa hai ca. Quán nhận đơn, giữ nguyên liệu, nấu, phục vụ và thanh toán. [Ma trận Phase 1](docs/verification/phase-1.md)
