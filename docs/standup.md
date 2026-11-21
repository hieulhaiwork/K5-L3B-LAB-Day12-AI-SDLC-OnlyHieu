# Standup giữa phase (mỗi người một dòng, 2–3 phút)

| Phase | Người | Đã xong | Sắp làm | Vướng gì |
|---|---|---|---|---|
| 2 | ThinkLee04 | Đã triển khai 2 bếp, 4 bàn, 6 món, lọc món theo kế hoạch D1–D5 và HUD quán. Smoke hai tiến trình đọc đúng cả 6 nguyên liệu, bộ test local qua 59/59. | Phối hợp nối `QuanSim` vào vòng `day`, chạy smoke một ngày rồi nhiều ngày trên commit bàn giao. | Nhánh quán đang dùng mô phỏng `gather` Phase 1. Bộ điều phối `day`, Shop và pause đang chờ tích hợp. |
| 3 | ThinkLee04 | Gộp vòng ngày và UI từ `main` với kho cá thể v1.2. Kiểm lại bàn giao, pause, Shop và ca từ giỏ rỗng thu 43k. Bộ test local qua 73/73. | Bàn giao cho Integrator để đưa vào `main` và gắn tag. | Bằng chứng hiện chạy trên bản gộp cho `feat/quan`. |
