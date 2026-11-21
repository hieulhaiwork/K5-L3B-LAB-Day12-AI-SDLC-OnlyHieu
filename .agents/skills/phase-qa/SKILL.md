---
name: phase-qa
description: Kiểm thử và lập bằng chứng nghiệm thu theo PRD hoặc Test Contract của bài lab Quán Ăn Chợ Nổi. Dùng khi chạy regression, kiểm CLI headless, bàn giao kho, vòng ngày hoặc review ma trận AC.
---

# Kiểm thử checkpoint

1. Đọc đề phase đang làm trong thư mục debaitungphase và xem manifest game.contract.json. Đối chiếu luật mới với test cũ trước khi sửa kỳ vọng. Ghi lý do thay đổi theo đúng mục của đề.
2. Chạy ca nhỏ qua headless_cmd bằng seed và fixture cố định. Với ca truyền kho, so nội dung gather_end, file kho và stock của Quán ở tick 0. Với vòng day, kiểm event chuyển pha mang pha cũ/mới đúng chỗ, snapshot pha mới tại phase_tick 0 và ngày chỉ hoàn thành khi đóng Shop.
3. Tách tick ngoài khỏi sim_tick để kiểm pause. Giữ phím qua chuyển pha và qua pause để kiểm cạnh lên. Kiểm mua tại tick cuối Shop, cấp mới chỉ áp dụng từ Ngày sau, cùng fixture cho JSONL giống từng byte.
4. Chạy toàn bộ test bằng lệnh trong AGENTS.md. Lưu kết quả thực trong docs/proof của phase và nối yêu cầu → bằng chứng → đạt/chưa đạt trong docs/verification. Ghi rõ phạm vi chạy local, mô phỏng UI hoặc trình duyệt thực.
