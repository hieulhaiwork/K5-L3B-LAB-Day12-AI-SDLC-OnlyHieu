# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Smoke Phase 2: `python3 -m chonoi.headless --mode day --days 1 --seed 42 --ticks 22200 --out out.jsonl`
- Chơi vòng ngày trên trình duyệt: `python3 -m chonoi.live --mode day` (WASD, E, Space, Esc/P). Vẫn hỗ trợ `--mode gather` và `--mode quan`.
- Kiểm thử lát quán Phase 2: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -p 'test_quan_p*.py' -v`
- Mở quán với kho mẫu: `python3 -m chonoi.live --mode quan --inventory docs/contracts/inventory.sample.json --port 0`

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- Khi chuyển `day` sang ca tối, truyền kho thực, kế hoạch ngày, `money`, `earned` và `reputation` vào `QuanSim`. Giữ `shift_earned` riêng cho mỗi ca.
- `DaySim` điều phối ca sáng, ca tối và Shop. `Session` quản lý pause và tick. Màn giới thiệu/kết quả thuộc live, không cộng tick gameplay headless.
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- [`phase-qa`](.agents/skills/phase-qa/SKILL.md): regression, kiểm bàn giao kho/vòng ngày và nối kết quả vào ma trận nghiệm thu.
