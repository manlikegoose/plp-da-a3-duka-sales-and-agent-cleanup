"""Reusable cleaning pipeline for the mobile-money agent transaction extract."""
import numpy as np
import pandas as pd

def clean_agent_data(txns, agents):
    """Clean transactions, merge agents, and return (clean_df, log).

    Removes duplicate txn_id rows; standardises txn_type and txn_date;
    converts amount to numeric, median-imputes unavailable values and flags
    them; flags but retains IQR outliers; and left-merges the agent register.
    Unknown agents are retained with county='Unknown'. The log records rules,
    affected-row counts and decisions for auditability.
    """
    clean = txns.copy()
    log = []
    def record(rule, rows, detail):
        log.append({"rule": rule, "rows_affected": int(rows), "detail": detail})

    before = len(clean)
    dup = clean.duplicated("txn_id", keep="first")
    clean = clean.loc[~dup].copy()
    record("Uniqueness: duplicate txn_id", dup.sum(),
           f"Removed {int(dup.sum())} duplicate rows; retained first occurrence.")

    normalized = clean["txn_type"].astype("string").str.strip().str.lower()
    mapped = normalized.map({"deposit":"Deposit", "withdrawal":"Withdrawal"})
    bad_type = mapped.isna()
    clean["txn_type"] = mapped
    record("Consistency: txn_type", bad_type.sum(),
           "Trimmed whitespace and normalised case to Deposit/Withdrawal.")

    date_text = clean["txn_date"].astype("string").str.strip().str.replace("/", "-", regex=False)
    parsed = pd.to_datetime(date_text, format="%Y-%m-%d", errors="coerce")
    bad_date = parsed.isna()
    clean["txn_date"] = parsed
    record("Validity: txn_date", bad_date.sum(),
           "Normalised slash separators and parsed ISO dates; invalid dates remain missing.")

    numeric = pd.to_numeric(clean["amount"], errors="coerce")
    missing_amount = numeric.isna()
    clean["amount_imputed"] = missing_amount
    median_amount = numeric.median()
    clean["amount"] = numeric.fillna(median_amount)
    record("Completeness/validity: amount", missing_amount.sum(),
           "Missing and N/A values median-imputed; amount_imputed preserves provenance.")

    q1, q3 = clean["amount"].quantile([0.25, 0.75])
    iqr = q3-q1
    lower, upper = q1-1.5*iqr, q3+1.5*iqr
    clean["is_outlier"] = (clean["amount"] < lower) | (clean["amount"] > upper)
    record("Accuracy: IQR amount outliers", clean["is_outlier"].sum(),
           f"Flagged values outside [{lower:.2f}, {upper:.2f}] and retained for review.")

    register = agents[["agent_id","county"]].drop_duplicates("agent_id")
    clean = clean.merge(register, on="agent_id", how="left", validate="many_to_one", indicator=True)
    unknown = clean["_merge"].eq("left_only")
    clean["county"] = clean["county"].fillna("Unknown")
    record("Integrity: unknown agent_id", unknown.sum(),
           "Left join preserves unmatched transactions; county set to Unknown.")
    clean = clean.drop(columns="_merge")
    clean["txn_date"] = clean["txn_date"].dt.strftime("%Y-%m-%d")
    clean = clean[["txn_id","agent_id","txn_type","amount","txn_date",
                   "amount_imputed","is_outlier","county"]]
    clean["amount"] = clean["amount"].astype(float)
    record("Pipeline", 0, f"Input rows={before}; output rows={len(clean)}.")
    return clean, pd.DataFrame(log)
