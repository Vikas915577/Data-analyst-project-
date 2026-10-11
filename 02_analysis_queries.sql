-- Run after loading normalized, outcome-resolved data into fact_loans.
-- 1. Portfolio headline KPIs
SELECT COUNT(*) AS loans,
       SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct,
       ROUND(AVG(loan_amnt), 2) AS avg_loan_amount,
       ROUND(AVG(annual_inc), 2) AS avg_annual_income,
       ROUND(AVG(dti), 2) AS avg_dti_pct,
       ROUND(AVG(int_rate), 2) AS avg_interest_rate_pct,
       ROUND(SUM(loan_amnt) FILTER (WHERE default_flag = 1), 2) AS defaulted_original_amount
FROM fact_loans;

-- 2. Loan-grade risk: keep denominators visible and sort by grade's natural order.
SELECT grade, COUNT(*) AS loans, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct,
       ROUND(AVG(loan_amnt), 2) AS avg_loan_amount
FROM fact_loans
GROUP BY grade
ORDER BY grade;

-- 3. Income-band risk segmentation
SELECT CASE WHEN annual_inc < 25000 THEN '<$25k'
            WHEN annual_inc < 50000 THEN '$25k–$50k'
            WHEN annual_inc < 75000 THEN '$50k–$75k'
            WHEN annual_inc < 100000 THEN '$75k–$100k'
            WHEN annual_inc IS NULL THEN 'Unknown'
            ELSE '$100k+' END AS income_band,
       COUNT(*) AS loans, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct
FROM fact_loans
GROUP BY 1 ORDER BY MIN(annual_inc) NULLS LAST;

-- 4. Term-length comparison
SELECT term_months, COUNT(*) AS loans, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct,
       ROUND(AVG(loan_amnt), 2) AS avg_loan_amount
FROM fact_loans
GROUP BY term_months ORDER BY term_months;

-- 5. DTI bands and the resume-relevant D/E + DTI >25% segment to recompute on verified data.
SELECT CASE WHEN dti < 10 THEN '<10' WHEN dti < 20 THEN '10–<20'
            WHEN dti < 25 THEN '20–<25' WHEN dti < 35 THEN '25–<35'
            WHEN dti IS NULL THEN 'Unknown' ELSE '35+' END AS dti_band,
       COUNT(*) AS loans, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct
FROM fact_loans GROUP BY 1 ORDER BY 1;

SELECT 'Grades D/E and DTI >25%' AS segment, COUNT(*) AS loans,
       SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS default_rate_pct
FROM fact_loans WHERE grade IN ('D','E') AND dti > 25;

-- 6. Origination vintage trend. Compare fully resolved outcomes, not in-flight loans.
SELECT DATE_TRUNC('year', issue_date)::date AS issue_year,
       COUNT(*) AS resolved_loans, SUM(default_flag) AS defaults,
       ROUND(100.0 * AVG(default_flag::numeric), 2) AS observed_default_rate_pct
FROM fact_loans GROUP BY 1 ORDER BY 1;
