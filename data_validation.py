import pandas as pd
import numpy as np

def _validate_common(df, required, label):
    errors = []
    if df.empty:
        errors.append(f"File {label} không có dữ liệu.")
        return errors
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append("Thiếu cột bắt buộc: " + ", ".join(missing))
        return errors
    if df["order_id"].isna().any() or df["order_id"].astype(str).str.strip().eq("").any():
        errors.append("Có mã đơn hàng bị trống.")
    return errors

def validate_orders(df: pd.DataFrame):
    errors = _validate_common(df, ["order_id", "order_amount"], "đơn hàng")
    if "order_amount" in df.columns:
        amount = pd.to_numeric(df["order_amount"], errors="coerce")
        if amount.isna().any():
            errors.append("Cột order_amount có giá trị không phải số hoặc bị trống.")
        elif not np.isfinite(amount).all():
            errors.append("Cột order_amount phải chứa số hữu hạn.")
        elif (amount < 0).any():
            errors.append("Cột order_amount không được âm.")
    return errors

def validate_payments(df: pd.DataFrame):
    errors = _validate_common(df, ["order_id", "payment_amount"], "thanh toán")
    if "payment_amount" in df.columns:
        amount = pd.to_numeric(df["payment_amount"], errors="coerce")
        if amount.isna().any():
            errors.append("Cột payment_amount có giá trị không phải số hoặc bị trống.")
        elif not np.isfinite(amount).all():
            errors.append("Cột payment_amount phải chứa số hữu hạn.")
        elif (amount < 0).any():
            errors.append("Cột payment_amount không được âm.")
    return errors
