-- Basic quality checks after loading fact_loans.
SELECT COUNT(*) AS row_count, COUNT(DISTINCT loan_id) AS distinct_loan_ids,
       COUNT(*) - COUNT(DISTINCT loan_id) AS duplicate_id_rows,
       COUNT(*) FILTER (WHERE issue_date IS NULL) AS missing_dates,
       COUNT(*) FILTER (WHERE loan_amnt <= 0) AS invalid_loan_amounts,
       COUNT(*) FILTER (WHERE dti < 0 OR dti > 100) AS out_of_range_dti,
       COUNT(*) FILTER (WHERE default_flag NOT IN (0,1)) AS invalid_targets
FROM fact_loans;

-- Verify target/status mapping has no inconsistencies.
SELECT loan_status, default_flag, COUNT(*) AS row_count
FROM fact_loans GROUP BY loan_status, default_flag ORDER BY loan_status, default_flag;
