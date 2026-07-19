# Cost Optimizer

An autonomous agent that analyzes cloud resource usage, identifies waste, recommends right-sizing, and projects savings from optimization.

## Features

- **Resource Parsing**: Reads CSV billing data with resource IDs, service types, costs, regions, utilization
- **Heuristic Analysis**: Low utilization detection, idle resource identification, uptime analysis
- **LLM-Powered Analysis**: Advanced pattern recognition across resource types
- **Optimization Types**: Right-size, shutdown, reserve, spot, tier, archive, compress
- **Savings Projection**: Monthly and annual savings with implementation effort estimates
- **Risk Assessment**: Low/medium/high risk classification for each recommendation

## Supported Cloud Providers

AWS, Azure, GCP, and any provider with CSV billing export

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run cost_optimizer.py
```

## Architecture

1. CSV billing data ingestion and parsing
2. Resource classification by type (compute, storage, network, database, etc.)
3. Heuristic optimization detection (utilization thresholds, uptime patterns)
4. LLM-powered cross-resource analysis and advanced pattern detection
5. Savings calculation with effort and risk scoring
6. Interactive recommendation dashboard

## License

Apache-2.0
