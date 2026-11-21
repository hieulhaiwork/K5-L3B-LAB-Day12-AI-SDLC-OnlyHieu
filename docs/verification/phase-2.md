# Ma trận truy vết Phase 2

Kết quả lát Quán lấy từ bằng chứng của TV2. TV3 chạy lại trên working tree dựa trên `main` tại `6b09191`.

| Yêu cầu TICKET-02 | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| Mục 1.3 — 2 bếp, 4 bàn, 6 món theo số chuẩn | Kiểm tọa độ, công thức, giá và giờ nấu. Cho hai bếp nấu đồng thời và xác nhận thứ tự nhận khách của bốn bàn. | [Test lát quán](../../tests/test_quan_p2.py) · [Bằng chứng quán](../proof/phase-2/quan.md) | Đạt |
| Mục 2 và 4.3–4.5 — kế hoạch D1–D5 và ca tối trong `day` | Kiểm gọi món theo kế hoạch, vòng 1 và 5 ngày, số dư giữ qua các pha và thứ tự event. | [Bằng chứng Quán](../proof/phase-2/quan.md) · [Smoke `day`](../proof/phase-2/tv3.md) | Đạt các ca đã chạy. |
| Mục 2 — HUD ca tối | Kiểm `GET /state` và các nhãn, màu kiên nhẫn, tiến độ bếp và cỡ chữ khi vẽ tại 1280×720. | [Bằng chứng quán](../proof/phase-2/quan.md) | Đạt theo API và hàm vẽ. Chưa đo FPS trên trình duyệt. |
| Mục 2 và 4.2–4.5 — Shop và pause | Kiểm giữ tick khi pause, giữ phím qua pha, mua đủ đúng giá và tại tick cuối, áp cấp từ ngày sau. | [Test vòng ngày](../../tests/test_day_p2.py) · [Kết quả TV3](../proof/phase-2/tv3.md) | Đạt các ca đã chạy. |
| Mục 2 — UI vòng ngày | Qua API live: menu, thực đơn, nhập kho, kết quả, Shop, pause và sang ngày sau. | [Kết quả TV3](../proof/phase-2/tv3.md) | Đạt kiểm tra bằng JavaScript với DOM/Canvas giả lập và HTTP thật. Chưa đo FPS thực. |
| Mục 5 — smoke kho và regression P1 | Đọc đúng sáu loại tại snapshot Quán tick 0. Chạy toàn bộ test trên preset v1.1. | [Smoke bàn giao kho](../proof/phase-2/integration.md) · [Kết quả TV3](../proof/phase-2/tv3.md) | Đạt local. |
| Checkpoint 2 — AI Harness và tag | Rà skill QA, nhật ký AI và lệnh chạy. | [phase-qa](../../.agents/skills/phase-qa/SKILL.md) · [AGENTS](../../AGENTS.md) | Đã có skill QA của TV3. Cần skill phát triển luật của TV2 và tag của nhóm. |

Phase 4 đã bổ sung [skill đổi luật](../../.agents/skills/contract-change/SKILL.md) và kiểm menu, HUD, pause, toàn bộ vòng ngày và Shop trên Chromium. [Bằng chứng](../proof/phase-4/run.md)
