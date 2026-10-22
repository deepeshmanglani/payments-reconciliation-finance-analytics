
CREATE OR REPLACE VIEW reconciliation_results AS

WITH gateway_summary AS (
    SELECT
        transaction_id,
        COUNT(*) AS gateway_record_count,
        MAX(amount) AS gateway_amount,
        MAX(fee) AS gateway_fee
    FROM payment_gateway
    GROUP BY transaction_id
),

bank_summary AS (
    SELECT
        transaction_id,
        MAX(settlement_amount) AS settlement_amount,
        MAX(status) AS settlement_status
    FROM bank_settlement
    GROUP BY transaction_id
),

gl_summary AS (
    SELECT
        transaction_id,
        SUM(
            CASE
                WHEN account = 'Bank' THEN debit
                ELSE 0
            END
        ) AS gl_bank_amount
    FROM general_ledger
    GROUP BY transaction_id
)

SELECT
    p.transaction_id,
    p.transaction_date,
    p.customer_id,
    p.amount AS product_amount,
    p.currency,

    g.gateway_amount,
    g.gateway_fee,
    g.gateway_record_count,

    b.settlement_amount,
    b.settlement_status,

    gl.gl_bank_amount,

    ROUND(
        COALESCE(
            g.gateway_amount - g.gateway_fee,
            0
        ),
        2
    ) AS expected_bank_amount,

    ROUND(
        COALESCE(
            b.settlement_amount
            - (g.gateway_amount - g.gateway_fee),
            0
        ),
        2
    ) AS settlement_variance,

    ROUND(
        COALESCE(
            gl.gl_bank_amount - b.settlement_amount,
            0
        ),
        2
    ) AS gl_variance,

    CASE
        WHEN g.gateway_record_count > 1
            THEN 'DUPLICATE'

        WHEN g.transaction_id IS NULL
            THEN 'MISSING_GATEWAY'

        WHEN b.transaction_id IS NULL
            THEN 'MISSING_BANK_SETTLEMENT'

        WHEN b.settlement_status = 'PENDING'
            THEN 'PENDING_SETTLEMENT'

        WHEN g.gateway_fee <>
             ROUND(g.gateway_amount * 0.01, 2)
            THEN 'FEE_MISMATCH'

        WHEN b.settlement_amount <>
             ROUND(g.gateway_amount - g.gateway_fee, 2)
            THEN 'AMOUNT_MISMATCH'

        WHEN gl.gl_bank_amount <>
             b.settlement_amount
            THEN 'GL_MISMATCH'

        ELSE 'MATCHED'
    END AS reconciliation_status

FROM product_ledger p

LEFT JOIN gateway_summary g
    ON p.transaction_id = g.transaction_id

LEFT JOIN bank_summary b
    ON p.transaction_id = b.transaction_id

LEFT JOIN gl_summary gl
    ON p.transaction_id = gl.transaction_id;
