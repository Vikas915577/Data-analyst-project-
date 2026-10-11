-- PostgreSQL-compatible demo schema. Import only data you are permitted to use.
CREATE TABLE IF NOT EXISTS loan_applications (
  loan_id TEXT PRIMARY KEY,
  issue_date DATE NOT NULL,
  loan_amnt NUMERIC(12,2) CHECK (loan_amnt > 0),
  annual_inc NUMERIC(12,2) CHECK (annual_inc >= 0),
  dti NUMERIC(6,2) CHECK (dti >= 0),
  int_rate NUMERIC(5,2) CHECK (int_rate >= 0),
  term_months INTEGER CHECK (term_months IN (36, 60)),
  grade CHAR(1),
  emp_length TEXT,
  home_ownership TEXT,
  purpose TEXT,
  delinq_2yrs INTEGER CHECK (delinq_2yrs >= 0),
  default_flag SMALLINT CHECK (default_flag IN (0, 1))
);
CREATE INDEX IF NOT EXISTS idx_loan_issue_date ON loan_applications(issue_date);
CREATE INDEX IF NOT EXISTS idx_loan_grade ON loan_applications(grade);
