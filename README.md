# Duka Sales Exploration and Agent Data Cleanup

This repository contains two reproducible analytics engagements using Python, pandas and NumPy.

## Engagement 1 — Duka Electronics

The sales notebook explores 1,000 generated orders dated 1 January–29 June 2026. It inspects the source, derives revenue and calendar columns, compares branch and product performance, evaluates weekend trading and monthly revenue, filters Premium online orders in Nairobi and Mombasa, and reconciles branch/channel totals with the Excel workbook.

### Duka Executive Summary

- Duka Electronics recorded 1,000 orders from 1 January to 29 June 2026, generating KES 71,792,500 in revenue.
- Nairobi led branch revenue with KES 26,106,100, ahead of Mombasa at KES 14,003,700.
- Laptop generated the highest product revenue at KES 41,535,000, while Tablet led unit sales with 691 units.
- Weekend orders totalled 277 versus 723 weekday orders, with respective revenues of KES 19,936,300 and KES 51,856,200.
- April was the strongest month at KES 13,518,300, while June was weakest at KES 10,903,400, a 24.0% difference relative to the weaker month.

## Engagement 2 — Mobile-money agent network

The agent notebook audits transaction data across uniqueness, consistency, validity, completeness, accuracy and integrity. It imports a reusable cleaning function, preserves unknown agents through a left join, records a cleaning log and produces county and weekly summaries.

**Agent row counts:** 612 source rows → 12 duplicate rows removed → 600 cleaned transaction rows. The cleaned output contains 600 unique IDs and 7 transactions with unknown agent references.


## Regenerate data

From the repository root:

```bash
python -m pip install -r requirements.txt
python generate_data.py
```

This writes `duka_sales.csv`, `agents.csv` and `agent_transactions.csv` into the working directory using fixed seeds.

## Run the notebooks

Run `python generate_data.py` first, then launch Jupyter:

```bash
jupyter notebook
```

Open both notebooks and run every cell from top to bottom. They read raw CSVs from the repository root and write required output files under `outputs/`.

For non-interactive execution:

```bash
jupyter nbconvert --to notebook --execute --inplace duka_sales_exploration.ipynb
jupyter nbconvert --to notebook --execute --inplace agent_cleanup.ipynb
```

## Cleaning decisions

- Duplicate `txn_id`: retain first occurrence and remove later duplicates.
- Transaction types: trim whitespace and normalise case to `Deposit` and `Withdrawal`.
- Dates: standardise slash separators and export as ISO `YYYY-MM-DD`.
- Amounts: coerce invalid/missing values to missing, median-impute and mark `amount_imputed`.
- Outliers: flag using 1.5×IQR and retain for investigation (`is_outlier`).
- Unknown agents: left join and label unmatched county as `Unknown`.

KES 250,000 values are not automatically discarded. Verify against source evidence and business limits before any correction or reversal.

## Privacy

Customer phone numbers would be personal data. They should not be committed to a public repository or included in analysis outputs. Use role-based access, masking or pseudonymisation, encryption, purpose limitation, retention controls and a lawful basis for processing under the Kenya Data Protection Act 2019.
