# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Quán — khách đến, gọi món, giữ nguyên liệu, bỏ đi | Chạy lịch khách trên hai bàn với một phần nguyên liệu, rồi kiểm tra kho và uy tín khi khách rời. | [Quán Phase 1](../proof/phase-1/quan.md) | Đạt theo test hiện có |
| Quán — nấu, lấy món, phục vụ, thanh toán, kết ca | So sánh JSONL của hai lần chạy. Kiểm tra thứ tự đơn, payload sự kiện, phục vụ lúc kiên nhẫn về 0 và thu tiền khi đóng ca. | [Quán Phase 1](../proof/phase-1/quan.md) | Đạt theo test hiện có |
| Quán — từ chối đầu vào mâu thuẫn | Chạy fixture thiếu trường, giữ quá kho, gán món trùng hoặc có bàn ngoài biên. | [Quán Phase 1](../proof/phase-1/quan.md) | Đạt theo test hiện có |
| Quán — HUD kho khả dụng và tên món | Đọc snapshot từ API live và chạy hàm vẽ với ca có nguyên liệu đã giữ chỗ. | [Quán Phase 1](../proof/phase-1/quan.md) | Đạt theo kiểm tra API và hàm vẽ |

## Đánh giá ngắn
- Phần quán đã đối chiếu PRD-0 mục D–F và qua kiểm thử trên nhánh `feat/quan`. Smoke hai tiến trình lấy kho từ `gather` để khởi tạo `quan` cũng đã qua.
- Điều cần chỉnh cho phase sau:
