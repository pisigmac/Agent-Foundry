# Performance Monitoring Agent

An autonomous agent that monitors application performance metrics, detects anomalies, identifies bottlenecks, and generates optimization recommendations.

## Features

- **Metric Parsing**: CSV and free-text metric ingestion (latency, throughput, error rate, CPU, memory, cache hit, etc.)
- **Anomaly Detection**: Baseline deviation and threshold-based anomaly identification
- **Bottleneck Analysis**: CPU-bound, memory-bound, I/O-bound, network-bound, database-bound, cache miss detection
- **LLM-Powered Analysis**: Advanced bottleneck identification with confidence scoring
- **Optimization Recommendations**: Specific fixes with estimated impact
- **Multi-Service Support**: Track metrics across multiple services simultaneously

## Supported Metrics

Latency, throughput, error rate, CPU, memory, disk I/O, network, database, cache hit rate, queue depth

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run performance_monitoring_agent.py
```

## Architecture

1. Metric ingestion (CSV or free text parsing)
2. Baseline comparison and threshold evaluation
3. Anomaly detection with severity classification
4. LLM-powered bottleneck analysis with contributing factors
5. Optimization recommendation generation with impact estimation
6. Interactive dashboard with metrics, anomalies, and bottlenecks

## License

Apache-2.0
