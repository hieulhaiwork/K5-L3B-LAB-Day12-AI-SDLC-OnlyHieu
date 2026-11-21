# Hợp đồng tích hợp (nên chốt sớm; hình thức do nhóm chọn)

## Kho v1.2

File có duy nhất khóa `items`, chứa mảng `{id, kind, fresh}`. Xem [file mẫu](inventory.sample.json). Gather cấp ID bằng allocator chung và ghi file sau `gather_end`. Quán nhận nguyên trạng các cá thể tại tick chuyển pha, gồm cả hàng ươn. `reserved` trỏ vào các ID đang có trong kho. Chế độ `day` truyền mảng trong bộ nhớ. Shop giữ kho dư đến khi kết thúc ngày.

## Quy ước kickoff Phase 1

Điền trong 15 phút kickoff (hoặc thay bằng một mục trong README / một bảng trên giấy, miễn cả nhóm cùng thống nhất):
1. **Schema file kho** — khớp mục G của PRD-0 (kho ghi khi `gather_end`) + một file kho mẫu hợp lệ: `inventory.sample.json`.
2. **Giao diện giữa `sim/*` và `client/ui`** — trạng thái nào UI được đọc, lệnh nào UI gửi vào.
3. **Danh sách sự kiện** — tên, `data`, ai phát, ai nghe (gather: `gather`, `node_regrown`, `hold_full`, `fish_caught`, `gather_end`...; quan: theo mục E của PRD-0).

Khi đổi hợp đồng sau này: báo cả nhóm và ghi lại lý do (ADR hoặc ghi chú, tùy chọn).
