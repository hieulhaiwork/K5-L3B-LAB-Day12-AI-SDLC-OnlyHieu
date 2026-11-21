---
name: contract-change
description: Triển khai hoặc review thay đổi luật Gather, Quán, vòng ngày và kho của lab theo PRD, Test Contract và tuning. Dùng khi đổi dữ liệu, schema, event hoặc thứ tự xử lý tick.
---

# Thay đổi luật chơi

1. Đọc đề đúng phase, phần [THAY THẾ] nếu có, manifest `game.contract.json` và hợp đồng trong `docs/contracts/`. Ghi quyết định về điểm mơ hồ vào `docs/clarify.md`.
2. Xác định đầu vào, thứ tự trong tick, trạng thái và sự kiện cần đổi. So sánh với luật cũ để giữ nguyên ca không bị tác động. Báo đầu nối Gather, Quán và UI trước khi đổi hợp đồng dùng chung.
3. Dùng tuning và dữ liệu, cấp ID và PRNG theo `AGENTS.md`. Giữ phần hiển thị ở lớp live và dùng `Session` cho mô phỏng.
4. Qua `headless_cmd`, kiểm đúng điểm đổi luật và hai phía ranh giới bằng seed và fixture cố định. Nếu đổi test cũ, chỉ rõ điều khoản thay thế và kỳ vọng cũ/mới. Dùng `phase-qa` để chạy lại các phase và ghi bằng chứng.
