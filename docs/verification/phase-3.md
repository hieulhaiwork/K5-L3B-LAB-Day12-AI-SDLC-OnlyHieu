# Ma trận kiểm chứng Phase 3

| Tiêu chí | Cách kiểm chứng | Kết quả local |
|---|---|---|
| AC-P3-01 — schema và file kho | Smoke hai tiến trình tại ranh giới độ tươi. So file với snapshot tick 0. Dùng kho đếm, ID trùng và fixture giữ hàng ươn để thử mã `2`. | Đạt |
| AC-P3-02 — độ tươi Gather, ID và LIFO | Kiểm ngưỡng 30, sắp sự kiện theo ID, dừng hao khi pause, rơi hàng khi bị chạm và ngất. | Đạt |
| AC-P3-03 — giữ chỗ và giá | Làm hai đơn mất hàng ở cùng tick. Kiểm đơn ưu tiên giữ lại trước khi tương tác, giá làm tròn xuống và giữ kho ươn. | Đạt |
| AC-P3-04 — vòng ngày | Đối chiếu ID và độ tươi khi chuyển sang Quán, kiểm kho dư khi mở Shop, tái tạo ID và kích hoạt nâng cấp khi sang ngày mới. Chạy thêm một ngày từ giỏ rỗng trên bản Gather tích hợp và đối chiếu giá, boa cùng tick đóng Shop. | Đạt |
| AC-P3-05 — HUD và regression | Kiểm API live, hàm vẽ ở 1280×720 và chạy lại toàn bộ test Phase 1–3. | Đạt theo API và hàm vẽ. Chưa đo FPS trên trình duyệt. |

[Bằng chứng Phase 3](../proof/phase-3/freshness.md) · [Test v1.2](../../tests/test_freshness_p3.py) · [Kế hoạch chuyển schema](../plan/phase-3.md)

Các kết quả này chạy trên nhánh `feat/quan`. Commit bàn giao trên `main` và tag `phase-3` đang chờ tích hợp.
