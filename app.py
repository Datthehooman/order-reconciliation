import streamlit as st
import pandas as pd
import plotly.express as px
from reconciliation import reconcile
from data_validation import validate_orders, validate_payments
from report_export import build_excel_report

st.set_page_config(page_title="Order Reconciliation", page_icon="📊", layout="wide")
st.title("Order Reconciliation Dashboard",)
st.caption("Đối soát đơn hàng và thanh toán từ Excel/CSV")

with st.sidebar:
    st.header("1. Tải dữ liệu")
    orders_file = st.file_uploader("File đơn hàng", type=["xlsx", "csv"], key="orders")
    payments_file = st.file_uploader("File thanh toán", type=["xlsx", "csv"], key="payments")
    st.markdown("---")
    st.markdown("**Cột bắt buộc**")
    st.code("Đơn hàng: order_id, order_amount\nThanh toán: order_id, payment_amount")
    st.caption("Có thể dùng file mẫu trong thư mục sample_data/.")

def read_table(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)

def money(value):
    return f"{value:,.0f} đ"

if not orders_file or not payments_file:
    st.info("Tải lên cả file đơn hàng và file thanh toán để bắt đầu.")
    st.subheader("Mô tả kết quả")
    st.write("Ứng dụng sẽ phân loại đơn khớp, thiếu thanh toán, thừa thanh toán, chưa thanh toán và giao dịch không có đơn tương ứng.")
    st.stop()

try:
    orders = read_table(orders_file)
    payments = read_table(payments_file)
    order_errors = validate_orders(orders)
    payment_errors = validate_payments(payments)
    errors = [f"Đơn hàng: {e}" for e in order_errors] + [f"Thanh toán: {e}" for e in payment_errors]
    if errors:
        st.error("Dữ liệu chưa hợp lệ. Hãy sửa các lỗi sau rồi tải lại file:")
        for error in errors:
            st.write(f"- {error}")
        st.stop()

    result = reconcile(orders, payments)
except Exception as exc:
    st.error(f"Không thể đọc hoặc xử lý file: {exc}")
    st.stop()

total_orders = len(result)
matched = int((result["status"] == "Khớp").sum())
exceptions = total_orders - matched
unmatched_payments = int((result["status"] == "Không có đơn hàng").sum())
difference = result.loc[result["status"] != "Khớp", "difference"].abs().sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Số đơn hàng", f"{total_orders:,}")
c2.metric("Đơn khớp", f"{matched:,}")
c3.metric("Đơn có sai lệch", f"{exceptions:,}")
c4.metric("Tổng chênh lệch tuyệt đối", money(float(difference)))

st.markdown("### Phân loại kết quả")
status_counts = result["status"].value_counts().rename_axis("Trạng thái").reset_index(name="Số lượng")
left, right = st.columns([1, 2])
with left:
    st.dataframe(status_counts, use_container_width=True, hide_index=True)
with right:
    fig = px.pie(status_counts, names="Trạng thái", values="Số lượng", hole=0.55)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Chi tiết đối soát")
statuses = ["Tất cả"] + sorted(result["status"].dropna().unique().tolist())
selected_status = st.selectbox("Lọc theo trạng thái", statuses)
search = st.text_input("Tìm mã đơn hàng", placeholder="Ví dụ: DH001")
filtered = result.copy()
if selected_status != "Tất cả":
    filtered = filtered[filtered["status"] == selected_status]
if search.strip():
    filtered = filtered[
        filtered["order_id"].astype(str).str.contains(
            search.strip(), case=False, na=False, regex=False
        )
    ]
st.dataframe(filtered, use_container_width=True, hide_index=True)

report_bytes = build_excel_report(result, status_counts)
st.download_button(
    "Tải báo cáo Excel",
    data=report_bytes,
    file_name="bao_cao_doi_soat.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
st.caption("Lưu ý: Đây là công cụ hỗ trợ đối soát. Hãy kiểm tra các giao dịch bị đánh dấu trước khi điều chỉnh sổ sách.")
