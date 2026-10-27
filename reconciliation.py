import pandas as pd
import numpy as np

AMOUNT_TOLERANCE = 1e-9

def reconcile(orders: pd.DataFrame, payments: pd.DataFrame) -> pd.DataFrame:
    """Đối soát tổng thanh toán theo mã đơn; giao dịch trùng được đánh dấu để kiểm tra."""
    orders = orders.copy()
    payments = payments.copy()
    orders["order_id"] = orders["order_id"].astype(str).str.strip()
    payments["order_id"] = payments["order_id"].astype(str).str.strip()
    orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="raise")
    payments["payment_amount"] = pd.to_numeric(payments["payment_amount"], errors="raise")

    duplicate_order_ids = set(orders.loc[orders["order_id"].duplicated(keep=False), "order_id"])
    duplicate_payment_rows = payments.duplicated(
        subset=["order_id", "payment_amount"], keep=False
    )
    duplicate_payment_ids = set(payments.loc[duplicate_payment_rows, "order_id"])

    payment_totals = payments.groupby("order_id", as_index=False).agg(
        paid_amount=("payment_amount", "sum"),
        payment_count=("payment_amount", "size"),
    )
    result = orders.merge(payment_totals, on="order_id", how="outer", indicator=True)
    result["order_amount"] = result["order_amount"].fillna(0)
    result["paid_amount"] = result["paid_amount"].fillna(0)
    result["payment_count"] = result["payment_count"].fillna(0).astype(int)
    result["difference"] = result["paid_amount"] - result["order_amount"]

    def classify(row):
        oid = str(row["order_id"])
        if row["_merge"] == "right_only":
            return "Không có đơn hàng"
        if oid in duplicate_order_ids:
            return "Mã đơn bị trùng"
        if oid in duplicate_payment_ids:
            return "Giao dịch có khả năng trùng"
        if row["payment_count"] == 0:
            return "Chưa thanh toán"
        if np.isclose(row["difference"], 0, atol=AMOUNT_TOLERANCE, rtol=0):
            return "Khớp"
        if row["difference"] < 0:
            return "Thanh toán thiếu"
        if row["difference"] > 0:
            return "Thanh toán thừa"
        return "Khớp"

    result["status"] = result.apply(classify, axis=1)
    result = result.rename(columns={"order_amount": "order_amount", "paid_amount": "paid_amount"})
    result = result[[
        "order_id", "order_amount", "paid_amount", "difference", "payment_count", "status"
    ]]
    result = result.sort_values(["status", "order_id"]).reset_index(drop=True)
    return result
