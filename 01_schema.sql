-- PostgreSQL schema for normalized, outcome-resolved loan records.
-- Only import data you are permitted to use; avoid uploading borrower-level records publicly.
CREATE TABLE IF NOT EXISTS fact_loans (
    loan_id          TEXT PRIMARY KEY,
    issue_date       DATE NOT NULL,
    loan_amnt        NUMERIC(12,2) NOT NULL CHECK (loan_amnt > 0),
    annual_inc       NUMERIC(14,2) CHECK (annual_inc >= 0),
    dti              NUMERIC(6,2) CHECK (dti BETWEEN 0 AND 100),
    int_rate         NUMERIC(5,2) CHECK (int_rate BETWEEN 0 AND 100),
    term_months      SMALLINT CHECK (term_months IN (36, 60)),
    grade            CHAR(1) CHECK (grade IN ('A','B','C','D','E','F','G')),
    emp_length       TEXT,
    home_ownership   TEXT,
    purpose          TEXT,
    delinq_2yrs      INTEGER CHECK (delinq_2yrs >= 0),
    loan_status      TEXT NOT NULL CHECK (loan_status IN ('Fully Paid','Charged Off')),
    default_flag     SMALLINT NOT NULL CHECK (default_flag IN (0, 1)),
    CHECK ((loan_status = 'Charged Off' AND default_flag = 1) OR (loan_status = 'Fully Paid' AND default_flag = 0))
);
CREATE INDEX IF NOT EXISTS idx_fact_loans_issue_date ON fact_loans(issue_date);
CREATE INDEX IF NOT EXISTS idx_fact_loans_grade ON fact_loans(grade);
CREATE INDEX IF NOT EXISTS idx_fact_loans_term ON fact_loans(term_months);
