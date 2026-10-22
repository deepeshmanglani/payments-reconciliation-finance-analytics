import pandas as pd
import numpy as np

np.random.seed(42)


# -----------------------------
# 1. GENERATE TRANSACTIONS
# -----------------------------

NUM_TRANSACTIONS = 10000

transaction_ids = [
    f"TXN{i:05d}"
    for i in range(1, NUM_TRANSACTIONS + 1)
]

amounts = np.random.randint(
    100,
    2000,
    size=NUM_TRANSACTIONS
)


# -----------------------------
# 2. PRODUCT LEDGER
# -----------------------------

product_ledger = pd.DataFrame({
    "transaction_id": transaction_ids,
    "transaction_date": pd.date_range(
        "2026-10-01",
        periods=NUM_TRANSACTIONS,
        freq="min"
    ),
    "customer_id": [
        f"CUST{i:05d}"
        for i in range(1, NUM_TRANSACTIONS + 1)
    ],
    "amount": amounts,
    "currency": "AED",
    "status": "SUCCESS"
})


# -----------------------------
# 3. PAYMENT GATEWAY
# -----------------------------

payment_gateway = pd.DataFrame({
    "gateway_transaction_id": [
        f"GW{i:05d}"
        for i in range(1, NUM_TRANSACTIONS + 1)
    ],
    "transaction_id": transaction_ids,
    "gateway": "Gateway_A",
    "amount": amounts,
    "fee": amounts * 0.01,
    "status": "SUCCESS"
})


# -----------------------------
# 4. SELECT EXCEPTION TRANSACTIONS
# -----------------------------

exception_count = int(NUM_TRANSACTIONS * 0.01)

exception_transactions = np.random.choice(
    transaction_ids,
    size=exception_count * 7,
    replace=False
)

missing_gateway_ids = exception_transactions[
    0:exception_count
]

duplicate_gateway_ids = exception_transactions[
    exception_count:exception_count * 2
]

missing_settlement_ids = exception_transactions[
    exception_count * 2:exception_count * 3
]

pending_settlement_ids = exception_transactions[
    exception_count * 3:exception_count * 4
]

amount_mismatch_ids = exception_transactions[
    exception_count * 4:exception_count * 5
]

fee_mismatch_ids = exception_transactions[
    exception_count * 5:exception_count * 6
]

gl_mismatch_ids = exception_transactions[
    exception_count * 6:exception_count * 7
]


# -----------------------------
# 5. INJECT FEE MISMATCH
# -----------------------------

payment_gateway.loc[
    payment_gateway["transaction_id"].isin(fee_mismatch_ids),
    "fee"
] += 5


# -----------------------------
# 6. REMOVE MISSING GATEWAY
# -----------------------------

payment_gateway = payment_gateway[
    ~payment_gateway["transaction_id"].isin(
        missing_gateway_ids
    )
].copy()


# -----------------------------
# 7. INJECT DUPLICATE GATEWAY
# -----------------------------

duplicate_gateway = payment_gateway[
    payment_gateway["transaction_id"].isin(
        duplicate_gateway_ids
    )
].copy()

duplicate_gateway["gateway_transaction_id"] = (
    duplicate_gateway["gateway_transaction_id"]
    + "_DUP"
)

payment_gateway = pd.concat(
    [payment_gateway, duplicate_gateway],
    ignore_index=True
)


# -----------------------------
# 8. BANK SETTLEMENT
# -----------------------------

bank_settlement = pd.DataFrame({
    "settlement_id": [
        f"SET{i:05d}"
        for i in range(1, NUM_TRANSACTIONS + 1)
    ],
    "transaction_id": transaction_ids,
    "settlement_date": pd.date_range(
        "2026-10-02",
        periods=NUM_TRANSACTIONS,
        freq="min"
    ),
    "settlement_amount": amounts - (amounts * 0.01),
    "status": "SETTLED"
})


# -----------------------------
# 9. INJECT PENDING SETTLEMENT
# -----------------------------

bank_settlement.loc[
    bank_settlement["transaction_id"].isin(
        pending_settlement_ids
    ),
    "status"
] = "PENDING"


# -----------------------------
# 10. INJECT AMOUNT MISMATCH
# -----------------------------

bank_settlement.loc[
    bank_settlement["transaction_id"].isin(
        amount_mismatch_ids
    ),
    "settlement_amount"
] -= 10


# -----------------------------
# 11. REMOVE MISSING SETTLEMENT
# -----------------------------

bank_settlement = bank_settlement[
    ~bank_settlement["transaction_id"].isin(
        missing_settlement_ids
    )
].copy()


# -----------------------------
# 12. GENERAL LEDGER
# -----------------------------

general_ledger = pd.DataFrame({
    "journal_id": [
        f"J{i:05d}"
        for i in range(1, len(bank_settlement) * 2 + 1)
    ],
    "transaction_id": (
        list(bank_settlement["transaction_id"]) * 2
    ),
    "account": (
        ["Bank"] * len(bank_settlement)
        + ["Gateway Receivable"] * len(bank_settlement)
    ),
    "debit": (
        list(bank_settlement["settlement_amount"])
        + [0] * len(bank_settlement)
    ),
    "credit": (
        [0] * len(bank_settlement)
        + list(bank_settlement["settlement_amount"])
    ),
    "posting_date": (
        list(bank_settlement["settlement_date"]) * 2
    )
})


# -----------------------------
# 13. INJECT GL MISMATCH
# -----------------------------

general_ledger.loc[
    (
        general_ledger["transaction_id"].isin(
            gl_mismatch_ids
        )
    )
    &
    (
        general_ledger["account"] == "Bank"
    ),
    "debit"
] += 15


# -----------------------------
# 14. RECONCILIATION
# -----------------------------

# Count gateway records per transaction
gateway_counts = (
    payment_gateway
    .groupby("transaction_id")
    .size()
    .reset_index(name="gateway_record_count")
)


# Start with product ledger.
# This guarantees one expected row per product transaction.

reconciliation_check = product_ledger.merge(
    payment_gateway.drop_duplicates("transaction_id"),
    on="transaction_id",
    how="left",
    suffixes=("_product", "_gateway")
)


# Add bank settlement
reconciliation_check = reconciliation_check.merge(
    bank_settlement[
        [
            "transaction_id",
            "settlement_amount",
            "status"
        ]
    ],
    on="transaction_id",
    how="left",
    suffixes=("", "_bank")
)


# Add gateway record count
reconciliation_check = reconciliation_check.merge(
    gateway_counts,
    on="transaction_id",
    how="left"
)


# -----------------------------
# 15. EXPECTED GATEWAY FEE
# -----------------------------

reconciliation_check["expected_fee"] = (
    reconciliation_check["amount_gateway"] * 0.01
)


# -----------------------------
# 16. EXPECTED BANK AMOUNT
# -----------------------------

reconciliation_check["expected_bank_amount"] = (
    reconciliation_check["amount_gateway"]
    - reconciliation_check["fee"]
)


# -----------------------------
# 17. BANK VARIANCE
# -----------------------------

reconciliation_check["variance"] = (
    reconciliation_check["settlement_amount"]
    - reconciliation_check["expected_bank_amount"]
)


# -----------------------------
# 18. GL RECONCILIATION
# -----------------------------

gl_summary = (
    general_ledger
    .groupby(
        ["transaction_id", "account"]
    )["debit"]
    .sum()
    .reset_index()
)


# Keep only Bank debit entries
bank_gl = gl_summary[
    gl_summary["account"] == "Bank"
].rename(
    columns={
        "debit": "gl_bank_amount"
    }
)


# Add GL amount to reconciliation table
reconciliation_check = reconciliation_check.merge(
    bank_gl[
        [
            "transaction_id",
            "gl_bank_amount"
        ]
    ],
    on="transaction_id",
    how="left"
)


# GL variance
reconciliation_check["gl_variance"] = (
    reconciliation_check["gl_bank_amount"]
    - reconciliation_check["settlement_amount"]
)


# -----------------------------
# 19. CLASSIFY RECONCILIATION
# -----------------------------

reconciliation_check["reconciliation_status"] = np.select(
    [
        reconciliation_check["gateway_record_count"] > 1,

        reconciliation_check["gateway_transaction_id"].isna(),

        reconciliation_check["settlement_amount"].isna(),

        reconciliation_check["status"] == "PENDING",

        reconciliation_check["fee"] != reconciliation_check["expected_fee"],

        reconciliation_check["variance"] != 0,

        reconciliation_check["gl_variance"] != 0
    ],

    [
        "DUPLICATE",

        "MISSING_GATEWAY",

        "MISSING_BANK_SETTLEMENT",

        "PENDING_SETTLEMENT",

        "FEE_MISMATCH",

        "AMOUNT_MISMATCH",

        "GL_MISMATCH"
    ],

    default="MATCHED"
)


# -----------------------------
# 20. VALIDATION
# -----------------------------

print("\n--- DATASET SIZE ---")

print(
    "Product ledger:",
    len(product_ledger)
)

print(
    "Payment gateway:",
    len(payment_gateway)
)

print(
    "Bank settlement:",
    len(bank_settlement)
)

print(
    "General ledger:",
    len(general_ledger)
)

print(
    "Reconciliation rows:",
    len(reconciliation_check)
)


print("\n--- RECONCILIATION STATUS COUNTS ---")

print(
    reconciliation_check[
        "reconciliation_status"
    ].value_counts()
)


print("\n--- EXCEPTION COUNTS ---")

exception_statuses = [
    "DUPLICATE",
    "MISSING_GATEWAY",
    "MISSING_BANK_SETTLEMENT",
    "PENDING_SETTLEMENT",
    "FEE_MISMATCH",
    "AMOUNT_MISMATCH",
    "GL_MISMATCH"
]

print(
    reconciliation_check[
        reconciliation_check[
            "reconciliation_status"
        ].isin(exception_statuses)
    ][
        "reconciliation_status"
    ].value_counts()
)

# -----------------------------
# 21. EXPORT DATASETS TO CSV
# -----------------------------

product_ledger.to_csv(
    "product_ledger.csv",
    index=False
)

payment_gateway.to_csv(
    "payment_gateway.csv",
    index=False
)

bank_settlement.to_csv(
    "bank_settlement.csv",
    index=False
)

general_ledger.to_csv(
    "general_ledger.csv",
    index=False
)

print("\n--- CSV EXPORT COMPLETE ---")

print("product_ledger.csv")
print("payment_gateway.csv")
print("bank_settlement.csv")
print("general_ledger.csv")
