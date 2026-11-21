# Changelog
## Unreleased

### Phase 3 — Mùa Nước Nổi, Test Contract v1.2

- **Breaking change.** `items` đổi từ map số lượng sang mảng `{id, kind, fresh}`. Kho rỗng dùng `{"items":[]}`. File kho đếm trả mã thoát `2` với v1.2.
- Chuyển fixture `gather.hold` và `quan.stock` thành mảng cá thể với ID duy nhất. Đổi `customers[].reserved` thành mảng ID trỏ đúng kho. Bỏ trường `reserved` để quán tự giữ theo công thức và độ tươi.
- Gather và Quán giảm độ tươi theo tick, phát `spoiled` đúng lần qua ngưỡng 30. Quán thử giữ lại khi hàng ươn, dùng giá theo độ tươi lúc nấu và tính boa từ giá đã chốt.
- `day` chuyển kho cá thể trực tiếp sang Quán rồi sang Shop. Pause dừng hao tươi. Cấp oxy và Máu mua trong Shop áp dụng từ ngày kế tiếp.
- Test hồi quy đổi kịch bản kho và kỳ vọng giá theo v1.2. Giữ kiểm tra tồn kho, thao tác, thời điểm thanh toán và kết ca. [Ma trận Phase 3](docs/verification/phase-3.md)
