# Payments Reconciliation & Finance Analytics System

A synthetic payments reconciliation and finance analytics project designed to simulate a fintech payment flow across the product ledger, payment gateway, bank settlement, and general ledger.

## Project Objective

The objective is to build a finance-controlled reconciliation workflow that identifies transaction-level breaks, classifies exceptions, and provides management-level finance metrics.

The project simulates a payment lifecycle:

Customer Payment
→ Product Ledger
→ Payment Gateway
→ Bank Settlement
→ General Ledger
→ Reconciliation Engine
→ Finance Dashboard

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

1. **Product Ledger**
   - Transaction ID
   - Customer ID
   - Transaction amount
   - Currency
   - Transaction timestamp
   - Status

2. **Payment Gateway**
   - Gateway transaction ID
   - Transaction ID
   - Gateway
   - Payment amount
   - Gateway fee
   - Status

3. **Bank Settlement**
   - Settlement ID
   - Transaction ID
   - Settlement date
   - Settlement amount
   - Settlement status

4. **General Ledger**
   - Journal ID
   - Transaction ID
   - Account
   - Debit
   - Credit
   - Posting date

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

## Finance Dashboard

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

## Technology Stack

- Python
- Pandas
- PostgreSQL
- SQL
- Metabase
- Git / GitHub

## Project Structure

```text
Ziina_Project/
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