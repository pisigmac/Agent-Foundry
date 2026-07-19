# DevOps Pipeline Monitor

An autonomous agent that monitors CI/CD pipelines, detects failures, analyzes root causes, and suggests auto-remediation steps.

## Features

- **Log Parsing**: Extracts stage results and error messages from CI/CD logs
- **Failure Classification**: Categorizes errors by type (build, test, deployment, infrastructure, dependency)
- **Root Cause Analysis**: LLM-powered identification of underlying issues
- **Remediation Guidance**: Specific fix steps with estimated completion times
- **Flaky Test Detection**: Identifies stages with inconsistent results

## Supported Platforms

- Jenkins, GitHub Actions, GitLab CI, CircleCI, Azure DevOps, Travis CI

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run devops_pipeline_monitor.py
```

## Architecture

1. Pipeline log ingestion and stage extraction
2. Error pattern matching and classification
3. LLM-powered root cause analysis with log context
4. Remediation recommendation generation
5. Flaky stage detection and alerting

## License

Apache-2.0
