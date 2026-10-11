-- Run after loading data into loan_applications. Rates use eligible rows with known binary outcomes.
-- 1. Portfolio overview
SELECT COUNT(*) AS loans, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct,
       ROUND(AVG(loan_amnt), 2) AS avg_loan_amount
FROM loan_applications WHERE default_flag IN (0,1);

-- 2. Default rate by grade (show denominators)
SELECT grade, COUNT(*) AS loan_count, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct
FROM loan_applications WHERE default_flag IN (0,1)
GROUP BY grade ORDER BY default_rate_pct DESC;

-- 3. DTI bands
SELECT CASE WHEN dti < 10 THEN '<10' WHEN dti < 20 THEN '10-<20'
            WHEN dti < 30 THEN '20-<30' ELSE '30+' END AS dti_band,
       COUNT(*) AS loan_count, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct
FROM loan_applications WHERE default_flag IN (0,1) AND dti IS NOT NULL
GROUP BY 1 ORDER BY 1;

-- 4. Default rate by term and purpose
SELECT term_months, purpose, COUNT(*) AS loan_count,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct
FROM loan_applications WHERE default_flag IN (0,1)
GROUP BY term_months, purpose HAVING COUNT(*) >= 20
ORDER BY default_rate_pct DESC;

-- 5. Data quality: duplicate IDs, missing targets, out-of-range fields
SELECT COUNT(*) - COUNT(DISTINCT loan_id) AS duplicate_id_rows,
       COUNT(*) FILTER (WHERE default_flag IS NULL) AS missing_target_rows,
       COUNT(*) FILTER (WHERE loan_amnt <= 0) AS invalid_amount_rows,
       COUNT(*) FILTER (WHERE dti < 0 OR dti > 100) AS suspicious_dti_rows
FROM loan_applications;
