# Data dictionary

All fields in the bundled CSV are synthetic.

| Field | Type | Meaning |
|---|---|---|
| `loan_id` | string | Synthetic unique row/loan identifier |
| `issue_date` | date | Simulated issue date; YYYY-MM-DD |
| `loan_amnt` | numeric USD | Simulated principal amount |
| `annual_inc` | numeric USD | Simulated annual income |
| `dti` | numeric percent | Simulated debt-to-income ratio |
| `int_rate` | numeric percent | Simulated interest rate |
| `term_months` | integer | Simulated term: 36 or 60 months |
| `grade` | category | Simulated grade A-G |
| `emp_length` | category | Simulated employment tenure band |
| `home_ownership` | category | Simulated housing category |
| `purpose` | category | Simulated loan purpose |
| `delinq_2yrs` | integer | Simulated delinquencies in prior 2 years |
| `default_flag` | binary | Simulated outcome: 1=default, 0=non-default |

For real data, document source, extraction date, status mapping, unit, missing-value semantics, and any transformations before comparing results.
