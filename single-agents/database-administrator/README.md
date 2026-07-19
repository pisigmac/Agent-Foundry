# Database Administrator

An autonomous agent for SQL optimization, schema analysis, query tuning, index recommendations, and database health monitoring.

## Features

- **Query Analysis**: Cost estimation, bottleneck identification, execution time prediction
- **Index Recommendations**: Specific column combinations for optimal performance
- **Schema Review**: Normalization checks, missing keys, data type efficiency
- **Security Scanning**: Identify sensitive data exposure and injection risks
- **Multi-Dialect Support**: PostgreSQL, MySQL, SQLite, MSSQL, Oracle

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run database_administrator.py
```

## Architecture

1. SQL query ingestion and dialect detection
2. LLM-powered query analysis with cost estimation
3. Schema parsing and normalization validation
4. Index recommendation engine
5. Security risk assessment

## License

Apache-2.0
