# Data Quality Validator

An autonomous agent that profiles datasets, validates schemas, detects anomalies, measures completeness, and scores overall data quality.

## Features

- **Statistical Profiling**: Null percentages, uniqueness, min/max/mean/std for every column
- **Heuristic Checks**: Missing values, duplicates, negative values, case inconsistencies
- **LLM-Powered Analysis**: Schema design review, outlier detection, business rule validation
- **Quality Scoring**: 6-dimension scoring (completeness, accuracy, consistency, validity, uniqueness, timeliness)
- **File Support**: CSV, Excel, JSON
- **Visual Reports**: Bar charts, data tables, severity indicators

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run data_quality_validator.py
```

## Architecture

1. Dataset ingestion and format detection
2. Per-column statistical profiling (pandas/numpy)
3. Heuristic issue detection (nulls, duplicates, negatives, case)
4. LLM-powered advanced analysis with schema review
5. 6-dimension quality score calculation
6. Interactive report generation with Streamlit

## License

Apache-2.0
