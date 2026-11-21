# Retro nhóm

## Phase 2 (nhanh)
- Kiểm thử quán độc lập và đầu nối ca tối song song. Smoke hai tiến trình xác nhận cả sáu nguyên liệu qua đúng schema kho.
- Lượt khách thứ năm trùng tick T1 hết kiên nhẫn. Việc đối chiếu thứ tự dọn bàn trước khi xét lịch giúp sửa kỳ vọng test.
- Sang Phase 3, ThinkLee04 giữ test sự kiện trùng tick và chạy lại bộ quán khi tích hợp vòng `day`.

## Phase 4 (cuối)

- **Hành động Phase 2 đã kiểm lại.** Test khách rời rồi tới ở cùng tick còn trong `tests/test_quan_p2.py` và vẫn đạt sau Phase 3–4.
- **Điều tốt.** Các ca giá, độ tươi và bàn giao kho tách riêng khỏi kiểm UI. Chạy lại regression xác nhận chúng còn hiệu lực khi thay đồ họa.
- **Điều cần sửa.** DOM giả lập từng bỏ sót cả tốc độ cảnh thực và thao tác qua hộp thoại. Lần đầu đổi công cụ đo bằng Chromium thật vẫn ghi khoảng 34 FPS. Kiểm tra callback cho thấy Canvas cũ chỉ vẽ khi nhận snapshot. Bản cuối vẽ theo nhịp màn hình, đếm lần vẽ xong và thử một ngày trên Chromium.
- **Đóng góp tới `f0a434f`.** Đếm commit không merge theo tài khoản trong `TEAM.md`. Hiếu 10, Thịnh 5, Gấm 3. Ví dụ Hiếu `9f1542c` và `cbe2c7f`, Thịnh `4c01bff` và `eb9477c`, Gấm `10574cc` và `49529e3`. Lịch sử không đủ căn cứ tổng hợp số buổi review hay token theo người.
- **Việc tiếp theo.** Tích hợp kiểm chơi Chromium vào CI trước khi bàn giao. Ba người xác nhận bản phản tư và Integrator đo lại trên commit dùng để phát hành. [Kiểm chứng Phase 4](verification/phase-4.md)
