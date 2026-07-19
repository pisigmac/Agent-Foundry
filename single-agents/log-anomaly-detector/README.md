# Log Anomaly Detector

An autonomous agent that analyzes application logs, detects anomalies, identifies patterns, and performs incident triage with severity scoring.

## Features

- **Pattern Extraction**: Identifies error patterns, service names, and timestamps from logs
- **Anomaly Detection**: LLM-powered detection of error spikes, latency issues, security events
- **Incident Triage**: Automatic severity classification and affected service identification
- **Action Recommendations**: Specific remediation steps for each detected anomaly
- **Multi-Format Support**: JSON, plain text, syslog, and structured log formats

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run log_anomaly_detector.py
```

## Architecture

1. Log ingestion and format detection
2. Regex-based pattern extraction (errors, services, timestamps)
3. Baseline pattern frequency analysis
4. LLM-powered anomaly detection with confidence scoring
5. Incident triage and action recommendation

## License

Apache-2.0
