# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 | PRD-0 mục D–F quy định sự kiện và trường của đơn, món trên bếp/tay thế nào? | `state` là `waiting` hoặc `eating`. `order_status` là `reserved`, `assigned`, `unfulfillable` hoặc `served`. Payload món có `order_id`, `dish_id`, `base_price`. Sự kiện dùng các trường ở mục E. | PRD-0 D–E |
| 2 | 2026-11-21 | Khi nào giữ, trừ kho và chốt boa? | Giữ nguyên liệu khi gọi món. Bắt đầu nấu thì trừ đúng phần giữ và chốt giá. Phục vụ thì chốt boa từ kiên nhẫn còn lại, làm tròn xuống. Khi thu tiền, boa dương cộng uy tín. Khách rời thì nhả phần giữ và bỏ món thuộc đơn. | PRD-0 F |
| 3 | 2026-11-21 | Khi một tick có khách rời, tương tác, khách đến hoặc đóng ca, xử lý theo thứ tự nào? | Giảm timer, xử lý bếp, di chuyển và tương tác, rồi xử lý khách theo ID bàn. Khách có thể nhận món ngay tick kiên nhẫn về 0 hoặc đóng ca. Đóng ca thu tiền khách còn ăn, cho khách còn chờ rời với `closing` và giữ nguyên uy tín. Khách mới chỉ đến khi ca còn giờ. | PRD-0 F |
|4|2026-11-21|Sau khi bắt thành công một đàn cá, đàn cá có biến mất khỏi bản đồ không?|Code tạm giả định đàn cá biến mất sau một lần bắt thành công.|---|
|5|2026-11-21|Nếu giỏ chỉ còn 1 chỗ nhưng sản lượng bắt cá là 3, có được nhận một phần không?|Code tạm giả định phải đủ chỗ cho toàn bộ sản lượng; nếu không thì phát hold_full.|---|
|6|2026-11-21|Khi bắt hụt hoặc giỏ đầy, có kích hoạt thời gian hồi chiêu không?|Code tạm chỉ kích hoạt cooldown khi bắt thành công.|---|
