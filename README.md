# Payments Reconciliation & Finance Analytics System

A synthetic payments reconciliation and finance analytics project designed to simulate a fintech payment flow across the product ledger, payment gateway, bank settlement, and general ledger.

## Finance Dashboard

<img width="1335" height="276" alt="image" src="https://github.com/user-attachments/assets/d4f35cea-2e46-43e6-8cd4-9d1cb25cb6c1" />
 
A Metabase dashboard was created to monitor:

- Total Payment Volume (TPV)
- Settled Amount
- Reconciliation Exceptions
- Exception Rate

Current synthetic dataset metrics:

- **TPV:** AED 10.55M
- **Settled Amount:** AED 10.23M
- **Reconciliation Exceptions:** 700
- **Exception Rate:** 7.00%

The dashboard is intended to demonstrate how transaction-level reconciliation outputs can be converted into finance monitoring metrics.

## Project Objective

The objective is to build a finance-controlled reconciliation workflow that identifies transaction-level breaks, classifies exceptions, and provides management-level finance metrics.

The project simulates the following payment lifecycle:

**Customer Payment → Product Ledger → Payment Gateway → Bank Settlement → General Ledger → Reconciliation Engine → Finance Dashboard**

## Key Finance Questions

The system is designed to answer:

- Which transactions have fully reconciled?
- Which transactions are missing from the payment gateway?
- Which gateway transactions are duplicated?
- Which settlements are missing or still pending?
- Are settlement amounts consistent with gateway amounts and fees?
- Are gateway fees calculated correctly?
- Does the general ledger agree with settlement records?
- What is total payment volume (TPV)?
- How much value is settled, pending, or exposed to reconciliation issues?
- What is the overall reconciliation exception rate?

## Dataset

The project uses synthetic transaction data representing 10,000 payment transactions.

Four source systems are simulated:

| Source System | Fields |
|---|---|
| **Product Ledger** | Transaction ID, Customer ID, Transaction amount, Currency, Transaction timestamp, Status |
| **Payment Gateway** | Gateway transaction ID, Transaction ID, Gateway, Payment amount, Gateway fee, Status |
| **Bank Settlement** | Settlement ID, Transaction ID, Settlement date, Settlement amount, Settlement status |
| **General Ledger** | Journal ID, Transaction ID, Account, Debit, Credit, Posting date |

## Reconciliation Logic

Each product ledger transaction is evaluated against downstream payment records.

The reconciliation engine identifies:

- MATCHED
- MISSING_GATEWAY
- DUPLICATE
- MISSING_BANK_SETTLEMENT
- PENDING_SETTLEMENT
- FEE_MISMATCH
- AMOUNT_MISMATCH
- GL_MISMATCH

The reconciliation logic is implemented in both Python and SQL.

## Results

The synthetic dataset contains:

| Reconciliation Status | Transactions |
|---|---:|
| Matched | 9,300 |
| Duplicate | 100 |
| Missing Gateway | 100 |
| Missing Bank Settlement | 100 |
| Pending Settlement | 100 |
| Fee Mismatch | 100 |
| Amount Mismatch | 100 |
| GL Mismatch | 100 |
| **Total** | **10,000** |

## Key Finance Metrics

| Metric | Value |
|---|---:|
| TPV | AED 10,549,173.00 |
| Settled Amount | AED 10,232,298.35 |
| Pending Settlement Exposure | AED 103,383.00 |
| Missing Settlement Exposure | AED 109,125.00 |
| Gateway Fees | AED 104,957.15 |
| Exception Rate | 7.00% |
| Reconciliation Variance | AED 1,500.00 |

## Technology Stack

- Python
- Pandas
- PostgreSQL
- SQL
- Metabase
- Git / GitHub

## Project Structure

```text
PaymentsRecon_Project/
│
├── generate_data.py
├── test_connection.py
│
├── product_ledger.csv
├── payment_gateway.csv
├── bank_settlement.csv
├── general_ledger.csv
│
├── reconciliation.sql
├── finance_metrics.sql
├── README.md
└── .gitignore
```
