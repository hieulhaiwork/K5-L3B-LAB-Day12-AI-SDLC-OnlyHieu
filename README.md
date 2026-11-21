# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

Game dùng **Python 3.12** và Chromium, Chrome hoặc Edge gần đây. Benchmark và kiểm trình duyệt cần thêm **Node.js 22+**. Có thể đặt `CHONOI_BROWSER` tới file thực thi nếu công cụ chưa tự tìm được trình duyệt.

```bash
git clone https://github.com/hieulhaiwork/K5-L3B-LAB-Day12-AI-SDLC-OnlyHieu.git
cd K5-L3B-LAB-Day12-AI-SDLC-OnlyHieu
python3 -m chonoi.live --mode day --port 0
```

Mở địa chỉ do terminal in ra và chọn **Chơi**. **WASD hoặc phím mũi tên** để di chuyển, **E** để tương tác, **Space** để bắt cá, **P** hoặc **Esc** để tạm dừng, **R** để chơi lại và **C** để đổi tương phản. Trong Shop, nhấn **1** hoặc **2** để mua nâng cấp bình oxy hoặc áo phao. **Đóng Shop** để sang ngày tiếp theo hoặc xem tổng kết. Điểm bằng `earned + 100 × floor(reputation)`.

## Kiểm thử và phát hành

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
python3 tools/package_release.py
```

Các lệnh trong manifest dùng `python3` trên macOS/Linux. Trên Windows dùng `python` và đặt `$env:PYTHONPATH='tests;.'` trong PowerShell.

Headless hỗ trợ `gather`, `quan` và `day`. Để chơi riêng Quán, chạy **python3 -m chonoi.live --mode quan --inventory docs/contracts/inventory.sample.json --port 0**. [Mẫu kho v1.2](docs/contracts/inventory.sample.json) · [Ma trận kiểm chứng](docs/verification/phase-4.md) · [Release notes](RELEASE_NOTES.md)

## Sáng tạo của nhóm

Cảnh sông và nhà bè dùng Pixel Art tự vẽ bằng Canvas. Sprite, sóng, bong bóng, ánh đèn và khói bếp chạy trên giao diện. [Bằng chứng trình duyệt và regression](docs/verification/phase-4.md)

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
