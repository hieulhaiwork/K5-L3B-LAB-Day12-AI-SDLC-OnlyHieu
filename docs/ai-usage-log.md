# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| 1 | TV3 | Codex | Kiểm CLI và truyền kho, kiểm HUD và API live, bổ sung test bắt cá đến thanh toán, tách test roster mẫu khỏi `TEAM.md` và cập nhật bằng chứng. | Không đo | Ba ca Quán lỗi ở bản ban đầu đều đạt trên bản tích hợp. Phần kiểm trực tiếp trong trình duyệt bị dừng ở bước chọn Chrome. |
| 1 | ThinkLee04 | Codex | Triển khai quán, thêm test headless và đối chiếu PRD-0 khi có đặc tả. | Không đo được | Bản đầu xử lý khách rời trước tương tác và dùng payload khác PRD-0. Đã sửa khi đối chiếu mục D–F và kiểm tra tick kiên nhẫn về 0, tick đóng ca. |
| 2 | ThinkLee04 | Codex | Cập nhật 2 bếp, 4 bàn, 6 món, kế hoạch D1–D5 và HUD. Viết test cho định dạng kho và đầu nối ca tối. | Không đo được | Dự kiến ban đầu bỏ lượt khách tại tick 3720. Đối chiếu lịch `120 + 900 × 4` với `120 + 3600` cho thấy T1 vừa hết kiên nhẫn, nên phải tổ chức lượt khách sau khi dọn bàn. |
| 2 | TV3 | Codex | Tích hợp vòng ngày, Shop và pause. Nối UI với API live, viết skill QA, test hồi quy và cập nhật bằng chứng. | Không đo được | Smoke P1 vẫn đòi 6 đàn và từ chối mode `day`. Đối chiếu TICKET-02 và thay bằng kiểm số đàn từ preset v1.1 cùng test CLI `day`. |
