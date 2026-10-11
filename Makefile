.PHONY: setup test validate analyze dashboard report preview

setup:
	python -m pip install -r requirements.txt

test:
	pytest -q

validate:
	python -m src.validate_data --input data/sample/synthetic_loans.csv --output outputs/data_quality.json

analyze:
	python -m src.analyze --input data/sample/synthetic_loans.csv --output outputs/analysis

dashboard:
	streamlit run streamlit_app.py

report:
	python -m src.create_demo_report

preview:
	python -m src.create_preview
