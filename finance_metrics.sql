
CREATE OR REPLACE VIEW finance_metrics AS
SELECT
    ROUND(SUM(product_amount), 2) AS tpv,

    ROUND(
        SUM(
            CASE
                WHEN settlement_status = 'SETTLED'
                THEN settlement_amount
                ELSE 0
            END
        ), 2
    ) AS settled_amount,

    ROUND(
        SUM(
            CASE
                WHEN reconciliation_status = 'PENDING_SETTLEMENT'
                THEN product_amount
                ELSE 0
            END
        ), 2
    ) AS pending_settlement_exposure,

    ROUND(
        SUM(
            CASE
                WHEN reconciliation_status = 'MISSING_BANK_SETTLEMENT'
                THEN product_amount
                ELSE 0
            END
        ), 2
    ) AS missing_settlement_exposure,

    ROUND(
        SUM(COALESCE(gateway_fee, 0)), 2
    ) AS gateway_fees,

    COUNT(*) AS total_transactions,

    SUM(
        CASE
            WHEN reconciliation_status <> 'MATCHED'
            THEN 1
            ELSE 0
        END
    ) AS exception_count,

    ROUND(
        1.0 *
        SUM(
            CASE
                WHEN reconciliation_status <> 'MATCHED'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        4
    ) AS exception_rate,

    ROUND(
        SUM(
            CASE
                WHEN reconciliation_status IN (
                    'AMOUNT_MISMATCH',
                    'FEE_MISMATCH',
                    'GL_MISMATCH'
                )
                THEN ABS(COALESCE(settlement_variance, 0))
                ELSE 0
            END
        ), 2
    ) AS reconciliation_variance

FROM reconciliation_results;
