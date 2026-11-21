# Ma trận truy vết Phase 2 — lát quán

Các kết quả dưới đây chạy local trên nhánh `feat/quan`.

| Yêu cầu TICKET-02 | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| Mục 1.3 — 2 bếp, 4 bàn, 6 món theo số chuẩn | Kiểm tọa độ, công thức, giá và giờ nấu. Cho hai bếp nấu đồng thời và xác nhận thứ tự nhận khách của bốn bàn. | [Test lát quán](../../tests/test_quan_p2.py) · [Bằng chứng quán](../proof/phase-2/quan.md) | Đạt |
| Mục 2 và 4.3–4.5 — kế hoạch D1–D5 và ca tối trong `day` | Tính lại nguyên liệu, kiểm khách gọi vượt số suất nếu đủ hàng và từ chối khách fixture gọi món ngoài kế hoạch. Kiểm số dư, tổng thu và uy tín qua đầu nối `QuanSim`. | [Bằng chứng quán](../proof/phase-2/quan.md) | Đạt ở cấp mô phỏng quán. Chờ kiểm thử qua CLI `day`. |
| Mục 2 — HUD ca tối | Kiểm `GET /state` và các nhãn, màu kiên nhẫn, tiến độ bếp và cỡ chữ khi vẽ tại 1280×720. | [Bằng chứng quán](../proof/phase-2/quan.md) | Đạt theo API và hàm vẽ. Chưa đo FPS trên trình duyệt. |
| Mục 5 — smoke hai tiến trình và regression P1 | Ghi kho từ ca sáng, đọc đúng sáu loại ở snapshot quán tick 0. Chạy toàn bộ test local. | [Smoke bàn giao kho](../proof/phase-2/integration.md) · [Regression](../proof/phase-2/quan.md) | Đạt trên nhánh quán |
| DoD toàn Phase 2 — vòng ngày, Shop, pause, `gather` Phase 2 và tag bàn giao | Chạy `day --days 1`, chạy nhiều Ngày kiểm cấp oxy/Máu và gắn tag vào commit đã kiểm chứng. | Chờ tích hợp các lát. | Chưa kiểm chứng |
