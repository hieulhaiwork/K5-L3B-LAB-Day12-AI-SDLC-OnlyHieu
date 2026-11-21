# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

## Phase 4

| # | Câu hỏi | Quyết định |
|---|---|---|
| P4-bench | Đếm nhịp trình duyệt hay số khung Canvas? | Đếm sau khi vẽ xong cảnh Gather thật ở 1280×720. Giữ seed 42, warmup 3 giây, đo 30 giây. Ghi riêng ba mốc hiệu năng theo TICKET-04. |
| P4-contrast | Làm thế nào để thấy cảnh báo khi không phân biệt được màu? | Dùng nhãn chữ và dấu `!`, hiện đồng thời nếu oxy thấp và thủy quái gần. Ngưỡng trình bày HUD dưới 25% theo TICKET-02. |
| P4-cli | Dùng trình thông dịch nào trong manifest? | Dùng `python3` theo môi trường sạch macOS/Linux. Khi chạy test trên Windows, dùng chính Python đã khởi động bộ test thay cho shim Microsoft Store. |
| P4-release | Bằng chứng thuộc bản nào? | Kiểm trên working tree dựa vào `f0a434f` và gói ZIP local. Hai tag hiện có trỏ đến `f0a434f`. Chờ nhóm kiểm lại commit bàn giao trước khi cập nhật tag và công bố Release. |

## Phase 3

| # | Câu hỏi | Quyết định |
|---|---|---|
| P3-kho | Có giữ kho đếm trong lượt chạy v1.2 không? | Mã thoát `2` nếu đưa kho đếm vào v1.2. Bộ đọc legacy dùng schema theo phiên bản cấu hình. Gather ghi nguyên tử qua file hoặc chuyển kho cá thể trong bộ nhớ. |
| P3-reserved | Xử lý fixture có đơn chỉ định ID xen với đơn tự giữ thế nào? | Kiểm và giữ các ID khai tường minh trước. Các đơn còn lại cấp theo `order_tick` rồi ID bàn, tránh lấy ID của đơn đã chỉ định. Khi hao tươi, lần lượt nhả và thử giữ lại từng đơn bị ảnh hưởng theo đúng ưu tiên. |

## Phase 2

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| P2-quán | 2026-11-21 | Quán có dừng bán một món khi đã vượt số suất trong kế hoạch ngày không? | Số suất chỉ tính nguyên liệu cần lấy. Khách được gọi bất kỳ món nào có trong kế hoạch nếu đủ kho khả dụng. Ca độc lập dùng cả sáu món. | TICKET-02 mục 2 |

## Phase 1

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 | PRD-0 mục D–F quy định sự kiện và trường của đơn, món trên bếp/tay thế nào? | `state` là `waiting` hoặc `eating`. `order_status` là `reserved`, `assigned`, `unfulfillable` hoặc `served`. Payload món có `order_id`, `dish_id`, `base_price`. Sự kiện dùng các trường ở mục E. | PRD-0 D–E |
| 2 | 2026-11-21 | Khi nào giữ, trừ kho và chốt boa? | Giữ nguyên liệu khi gọi món. Bắt đầu nấu thì trừ đúng phần giữ và chốt giá. Phục vụ thì chốt boa từ kiên nhẫn còn lại, làm tròn xuống. Khi thu tiền, boa dương cộng uy tín. Khách rời thì nhả phần giữ và bỏ món thuộc đơn. | PRD-0 F |
| 3 | 2026-11-21 | Khi một tick có khách rời, tương tác, khách đến hoặc đóng ca, xử lý theo thứ tự nào? | Giảm timer, xử lý bếp, di chuyển và tương tác, rồi xử lý khách theo ID bàn. Khách có thể nhận món ngay tick kiên nhẫn về 0 hoặc đóng ca. Đóng ca thu tiền khách còn ăn, cho khách còn chờ rời với `closing` và giữ nguyên uy tín. Khách mới chỉ đến khi ca còn giờ. | PRD-0 F |
|4|2026-11-21|Sau khi bắt thành công một đàn cá, đàn cá có biến mất khỏi bản đồ không?|Code tạm giả định đàn cá biến mất sau một lần bắt thành công.|---|
|5|2026-11-21|Nếu giỏ chỉ còn 1 chỗ nhưng sản lượng bắt cá là 3, có được nhận một phần không?|Code tạm giả định phải đủ chỗ cho toàn bộ sản lượng; nếu không thì phát hold_full.|---|
|6|2026-11-21|Khi bắt hụt hoặc giỏ đầy, có kích hoạt thời gian hồi chiêu không?|Code tạm chỉ kích hoạt cooldown khi bắt thành công.|---|
