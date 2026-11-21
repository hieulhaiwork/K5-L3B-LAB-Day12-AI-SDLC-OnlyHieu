# TEAM

**Tên nhóm:** OnlyHieu  **Số người:** 3  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
|Lê Hiền Hiếu |hieulhaiwork | `sim/gather` |Team Lead / PO |sim/quan |
|Đinh Lê Thịnh| ThinkLee04 | `sim/quan` |Developer / AI Harness |sim/gather |
|Trần Thị Hồng Gấm| Honggam1109 | `client/ui`, `qa` |Integrator / QA Lead / Scrum / Release |Kiểm thử và tích hợp hai module |


**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.
- PO (Hiếu): Đầu mối làm rõ yêu cầu với giảng viên, quản lý docs/clarify.md, phân tích yêu cầu từng phase.
- Integrator (TV3): Quản lý docs/contracts/, tích hợp code, kiểm tra trước khi gắn tag.
- QA Lead (TV3): Phụ trách kiểm thử, CI và docs/verification/.
- Scrum/Release (TV3): Theo dõi tiến độ, quản lý các checkpoint, tag và GitHub Release.
- AI Harness (TV2, phối hợp TV3): Phát triển tối thiểu 2 AI skills/hooks/commands, cập nhật AGENTS.md.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: Group Zalo
- Khi bất đồng về thiết kế: Thảo luận tối đa 2 phút, ưu tiên phương án đáp ứng PRD và Test Contract; nếu chưa thống nhất, Integrator quyết định kỹ thuật và ghi lý do.
- Khi ai đó trễ hoặc vướng quá 10 phút: Thông báo ngay trong nhóm, nêu rõ vấn đề và phần việc chưa hoàn thành; người dự phòng hỗ trợ hoặc nhận bàn giao.
- Giờ standup giữa phase: Kiểm tra tiến độ ngắn trước mỗi checkpoint, báo cáo phần đã xong, phần còn thiếu và các blocker.
- Cách đọc code của nhau (tùy chọn): Mỗi thành viên kiểm tra phần code liên quan của người khác trước khi tích hợp; ưu tiên review logic, Test Contract và các test bị ảnh hưởng.
- Cách làm việc với Git: Mỗi người commit bằng tài khoản GitHub cá nhân, tối thiểu 3 commit có nội dung; chạy test trước khi tích hợp. Integrator chịu trách nhiệm gắn tag phase-1 đến phase-4 và tạo Release v1.0.0.

## Phase 4

- Bản tích hợp local gom lượt rà luật, UI, đóng gói, QA và bằng chứng theo yêu cầu bàn giao cuối. [Ma trận](docs/verification/phase-4.md)
- PO rà các điểm làm rõ, thành viên xác nhận phản tư cá nhân, Integrator phát hành từ commit bàn giao đã chạy lại test. [Retro và bằng chứng đóng góp](docs/retro.md)
