# Raw source data (not tracked)

This folder is intentionally git-ignored. Do not commit large source files or individual borrower data.

For the LendingClub variant, obtain a copy of the historical accepted-loan export only from a source where you have checked the current terms and permissions. One commonly referenced historical mirror is the [Lending Club Loan Data CSV dataset on Kaggle](https://www.kaggle.com/datasets/adarshsng/lending-club-loan-data-csv); this project does not redistribute it and does not make a claim about the current availability or licence of that mirror.

Place the CSV at `data/raw/accepted_2007_to_2018Q4.csv` and run `src/prepare_lendingclub.py`. The importer needs these columns: `id`, `issue_d`, `loan_amnt`, `annual_inc`, `dti`, `int_rate`, `term`, `grade`, `emp_length`, `home_ownership`, `purpose`, `delinq_2yrs`, `loan_status`. If a newer or alternate export uses a different schema, map fields only after checking its own data dictionary.
