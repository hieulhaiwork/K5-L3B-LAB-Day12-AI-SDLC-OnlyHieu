# Kế hoạch Phase 4 — Phát hành v1.0.0

**2:30–3:00.** Chốt Test Contract v1.3, hồi quy Phase 1–3, benchmark Canvas, soak 10 ngày, bản đóng gói và bằng chứng demo. Kế hoạch tổng hợp theo TICKET-04 và [phân công nhóm](../../TEAM.md).

| Đầu việc | Phụ trách | Phụ thuộc và cách nghiệm thu |
|---|---|---|
| Rà manifest và hai lệnh `bench_cmd`, `soak_cmd`. Đối chiếu dữ liệu gameplay với bản v1.2. | hieulhaiwork, phối hợp Honggam1109 | Đo cảnh Gather seed 42 ở 1280×720, làm nóng 3 giây và đo 30 giây. Soak seed 7 đạt 10/10 ngày, 0 crash và lặp kết quả bỏ thời gian thực. [Benchmark](../proof/phase-4/bench.json) · [Soak](../proof/phase-4/soak.json) |
| Rà hồi quy Quán và hành động đã chốt ở retro Phase 2. | ThinkLee04, phối hợp cả nhóm | Kiểm ca khách rời và khách tới cùng tick, giữ chỗ, giá theo độ tươi và thanh toán cuối ca trên bản tích hợp. [Retro](../retro.md) |
| Kiểm UI, tương phản cao, hồi quy và ma trận nghiệm thu. | Honggam1109 | Trên trình duyệt thật, thử đủ ba cảnh báo và chơi từ Gather đến đóng Shop. Lưu ảnh và kết quả. [Bằng chứng](../proof/phase-4/run.md) |
| Đóng gói, kiểm khởi chạy và chuẩn bị phát hành. | Honggam1109, phối hợp hieulhaiwork | Thử từ nguồn sạch theo README tối đa 3 lệnh trên Linux hoặc macOS. Rà ZIP, CHANGELOG, credits, license và release notes. Chốt bằng chứng trên commit dùng để bàn giao. [Release notes](../../RELEASE_NOTES.md) |
| Hoàn tất retro và xác nhận phản tư cá nhân. | Cả nhóm | Mỗi người ghi phần đóng góp, hỗ trợ, lỗi AI và bài học trong tối đa 200 từ, kèm commit hoặc bằng chứng. |

**Mốc theo đề.** Phút 0–15 song song đo hiệu năng, rà UI, chạy test và đóng gói. Phút 15–25 làm retro và phản tư, standup ở phút 20. Phút 25–30 kiểm lại artifact và commit. `phase-4` và GitHub Release `v1.0.0` dùng cùng commit bàn giao trên main.

**Trạng thái bàn giao.** Bản local đã có ZIP kiểm trên Ubuntu, 88 test đạt và bằng chứng Chromium. Kiểm macOS, GitHub Actions, xác nhận phản tư và công bố bản gắn tag còn chờ nhóm. Demo một ngày trọn vòng, mở kết quả test, ma trận và bằng chứng đóng góp. [Ma trận Phase 4](../verification/phase-4.md) · [Standup](../standup.md)
