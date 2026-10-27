# Order Reconciliation Dashboard

Ứng dụng Streamlit hỗ trợ đối soát đơn hàng và giao dịch thanh toán từ Excel/CSV.

## Bài toán cần giải quyết

Cửa hàng có một file đơn hàng và một file giao dịch thanh toán. Nhân viên phải kiểm tra thủ công xem đơn nào đã thanh toán, đơn nào thiếu tiền hoặc có giao dịch không khớp.

## Tính năng

- Tải lên file đơn hàng và file thanh toán.
- Kiểm tra các cột bắt buộc và dữ liệu không hợp lệ.
- Đối chiếu tổng thanh toán theo mã đơn hàng.
- Phân loại đơn khớp, chưa thanh toán, thanh toán thiếu/thừa, giao dịch không có đơn và dữ liệu nghi trùng.
- Dashboard KPI, biểu đồ, lọc kết quả và xuất báo cáo Excel.

## Cài đặt

Python 3.10+ được khuyến nghị.

Không cần chạy nếu máy đã cài đặt.

```Shell
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Chạy ứng dụng

```Shell
streamlit run app.py
```

Hoặc

```Shell
python -m streamlit run app.py
```

## Định dạng file

`orders.xlsx`:

| order_id | order_amount |
| -------- | -----------: |
| DH001    |       500000 |

`payments.xlsx`:

| order_id | payment_amount |
| -------- | -------------: |
| DH001    |         500000 |

Có thể dùng CSV thay Excel nếu giữ nguyên tên cột.

## Giới hạn

- Nếu mã đơn hàng bị nhập sai, ứng dụng có thể xem giao dịch đó là không có đơn hàng tương ứng.
- Chưa xử lý đầy đủ các trường hợp thanh toán phức tạp.
- Các dòng thanh toán có cùng mã đơn và số tiền được đánh dấu nghi trùng, không tự động loại bỏ.
- Công cụ chưa có chức năng tự động làm sạch và chuẩn hóa mọi định dạng dữ liệu.
- Đây là công cụ hỗ trợ rà soát, không thay thế hệ thống kế toán hoặc xác nhận giao dịch từ ngân hàng.
