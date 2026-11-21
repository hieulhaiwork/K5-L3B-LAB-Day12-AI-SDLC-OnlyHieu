# Một ngày ở chợ nổi v1.0.0

Út Sen lặn bắt cá và hái rau, phục vụ khách trên nhà bè rồi dùng tiền mua nâng cấp cho lần lặn sau. Bản v1.0.0 có vòng chơi năm ngày, kho theo từng cá thể và độ tươi ảnh hưởng đến nấu ăn, giá bán và tiền boa.

- Cảnh sông và nhà bè Pixel Art có sprite gốc và hiệu ứng nhẹ. Phím **C** đổi tương phản. Cả ba cảnh báo có chữ.
- Test Contract v1.3 giữ gameplay và JSONL v1.2, thêm lệnh benchmark Canvas và soak headless.
- Giải nén ZIP, vào thư mục vừa giải nén và chạy **python3 -m chonoi.live --mode day --port 0**. Mở URL in trong terminal. Cần Python 3.12 và Chromium, Chrome hoặc Edge. [README](README.md)
- Bản chơi dùng bàn phím. Benchmark cần thêm Node.js 22+. Gói này dùng chung cho các hệ điều hành có Python, Chrome và các công cụ cần thiết. [Kiểm chứng](docs/verification/phase-4.md)
