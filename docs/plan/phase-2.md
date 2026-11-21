# Kế hoạch Phase 2 — Vòng ngày và AI Harness

**1:00–1:55.** Áp tuning chuẩn v1.1, chơi trọn Gather → Quán → Shop và kiểm hồi quy Phase 1. Kế hoạch tổng hợp theo TICKET-02 và [phân công nhóm](../../TEAM.md).

| Đầu việc | Phụ trách | Phụ thuộc và cách nghiệm thu |
|---|---|---|
| Cập nhật Gather theo số chuẩn, cá bơi và sinh, thêm nguyên liệu, Cá Sấu Năm Chèo, Máu và ngất. | hieulhaiwork | Đọc tuning theo v1.1. So file kho với Quán bằng fixture đủ sáu nguyên liệu. [Smoke kho](../proof/phase-2/integration.md) |
| Cập nhật 2 bếp, 4 bàn, 6 món, lọc món theo kế hoạch D1–D5. Viết skill hỗ trợ phát triển luật. | ThinkLee04 | Làm độc lập với kho mẫu. Khi tích hợp, dùng kế hoạch và kho khả dụng do vòng ngày truyền. [Bằng chứng Quán](../proof/phase-2/quan.md) |
| Nối hai ca và Shop, cập nhật menu, pause, HUD và kết quả. Viết skill QA. | Honggam1109 | Dùng fixture cố định để làm sớm. Kiểm bản cuối sau khi hai ca cập nhật, gồm pause giữ nguyên timer, mua đúng giá và cấp mới có hiệu lực từ ngày sau. [Bằng chứng vòng ngày](../proof/phase-2/Qa.md) |
| Rà hồi quy, chốt ma trận và ghi lý do nếu kỳ vọng cũ đổi theo đề. | Honggam1109, phối hợp cả nhóm | Chạy smoke 1 và 5 ngày, kiểm ngày chỉ hoàn thành khi Shop đóng. Rà tối thiểu 2 skill/hook/command, cập nhật `AGENTS.md` và nhật ký AI. [Ma trận Phase 2](../verification/phase-2.md) |

**Mốc theo đề.** Phút 0–5 chốt phần thay đổi, 5–20 làm song song. Phút 20 smoke kho hai tiến trình và standup. Phút 20–35 chốt `day`, 35–45 chạy hồi quy và lưu bằng chứng, 45–50 retro, 50–55 dự phòng và bàn giao `phase-2`.

**Rủi ro và bàn giao.** Giữ một nguồn tuning, so sự kiện tại ranh giới chuyển pha và thử giữ phím qua pause. Trên commit bàn giao, lưu kết quả smoke, cập nhật [Retro](../retro.md), [Làm rõ](../clarify.md) và [Nhật ký AI](../ai-usage-log.md).
