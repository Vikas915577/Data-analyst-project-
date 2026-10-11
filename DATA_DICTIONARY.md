# Data dictionary

The dashboard and normalized analysis pipeline expect one row per outcome-resolved loan.

| Field | Type | Meaning | Allowed / notes |
|---|---|---|---|
| `loan_id` | string | Unique loan identifier | Never use as a model feature |
| `issue_date` | date | Origination/issue date | Used for chronological split and trend charts, not as a predictor |
| `loan_amnt` | numeric | Original loan amount | Must be greater than 0 |
| `annual_inc` | numeric | Borrower annual income at origination | Currency in source dataset; nullable values are imputed in model pipeline |
| `dti` | numeric | Debt-to-income ratio, percentage points | Usually 0–100 in the source; `25` means 25% |
| `int_rate` | numeric | Interest rate, percentage points | `13.5` means 13.5%; dashboard renders the number as a percentage |
| `term_months` | integer | Loan term in months | Common historical LendingClub terms are 36 or 60 |
| `grade` | category | Loan risk grade assigned in source | A–G for historical LendingClub schema |
| `emp_length` | category | Employment length bucket | Source-defined category |
| `home_ownership` | category | Housing status | Source-defined category |
| `purpose` | category | Loan purpose | Source-defined category |
| `delinq_2yrs` | integer | Delinquencies over prior two years | Must not be confused with post-origination performance fields |
| `loan_status` | category | Final outcome status | Preparation script retains only `Fully Paid` / `Charged Off` |
| `default_flag` | binary | Analysis target | 1 = Charged Off; 0 = Fully Paid in included LendingClub preparation logic |
| `income_band` | derived | Income segment | `<$25k`, `$25k–$50k`, `$50k–$75k`, `$75k–$100k`, `$100k+`, Unknown |
| `dti_band` | derived | DTI segment | `<10`, `10–<20`, `20–<25`, `25–<35`, `35+`, Unknown |

**Units matter:** `dti` and `int_rate` are stored in percentage points, not decimal fractions. In Power BI percent measures divide the average by 100 before applying percentage formatting.

The bundled demo uses synthetic records and these same fields. See `data/sample/DATA_NOTICE.md`.
