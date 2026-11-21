# Kế hoạch Phase 1 (≤ 1 trang)

**0:00–1:00.** Chơi được Lặn & Hái và Mở Quán, bàn giao kho qua file, có smoke headless và HUD theo PRD-0/Test Contract v1.0. Kế hoạch tổng hợp theo đề và [phân công nhóm](../../TEAM.md).

| Đầu việc | Phụ trách | Phụ thuộc và cách nghiệm thu |
|---|---|---|
| Chốt tuning, schema kho đếm và ví dụ kho. Ghi điểm mơ hồ, phân vai và thống nhất trạng thái/lệnh UI. | hieulhaiwork, phối hợp cả nhóm | Chốt sớm để Gather xuất và Quán nạp theo cùng quy ước. [Hợp đồng kho](../contracts/README.md) · [Làm rõ](../clarify.md) |
| Bơi, giới hạn vùng nước, oxy, ngạt và giỏ. Hái, bắt cá và cập bến. | hieulhaiwork | Kiểm giới hạn giỏ, ngất và ghi kho khi kết ca. Xuất file thật trước phút 25 theo mốc gợi ý. [Test Gather](../../tests/test_gather.py) |
| Khách, giữ chỗ và kiên nhẫn. Nấu, bưng, giao món và thu tiền. | ThinkLee04 | Bắt đầu với kho mẫu. Đổi sang file Gather xuất khi smoke hai tiến trình, so kho với snapshot Quán tick 0. [Bằng chứng Quán](../proof/phase-1/quan.md) |
| Kiểm HUD, CLI, truyền kho, chạy test và lập ma trận. | Honggam1109 | Có thể chuẩn bị fixture và test từ hợp đồng kho. Kiểm cuối chờ cả hai mode chạy được, gồm một ca bắt cá đến thu tiền. [Bằng chứng tích hợp](../proof/phase-1/qa-baseline.md) |

**Mốc theo đề.** Phút 0–15 chia vai và chốt hợp đồng. Phút 15–45 triển khai, standup phút 20. Phút 45–55 kiểm smoke và chơi thử trên main. Phút 55–60 dự phòng và bàn giao `phase-1`.

**Rủi ro và bàn giao.** Kiểm cả file kho thật lẫn fixture để phát hiện lệch schema. Xác nhận với giảng viên về số thành viên. README cần hướng dẫn chạy trong tối đa 3 lệnh trên macOS/Linux cùng lệnh test, điều khiển và cách tính điểm. Ma trận cần dẫn bằng chứng chạy trên commit bàn giao. [Ma trận Phase 1](../verification/phase-1.md)
