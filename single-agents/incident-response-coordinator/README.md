# Incident Response Coordinator

An autonomous agent that triages on-call incidents, executes runbooks, manages escalation chains, and coordinates cross-team response efforts.

## Features

- **Incident Triage**: AI-powered severity classification (SEV1-SEV4) based on business impact
- **Runbook Generation**: Automatic runbook creation for known and unknown incident types
- **Escalation Management**: Time-based escalation rules with multi-channel notifications
- **Service Impact Analysis**: Track affected services and dependencies
- **Response Coordination**: Structured step-by-step incident response workflow

## Severity Levels

- **SEV1**: Complete outage, data loss, security breach, >$100K/hour impact
- **SEV2**: Major degradation, partial outage, $10K-$100K/hour impact
- **SEV3**: Minor issues, workarounds available, <$10K/hour impact
- **SEV4**: Cosmetic issues, no revenue impact

## Escalation Chain

- **L1**: On-call engineer (5 min response)
- **L2**: Team lead (15 min if unacknowledged)
- **L3**: Engineering manager (30 min for SEV1/2)
- **L4**: Director/VP (1 hour for SEV1/2)
- **L5**: Executive (2 hours for business-critical)

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run incident_response_coordinator.py
```

## Architecture

1. Incident creation with title, description, and affected services
2. LLM-powered severity triage and business impact assessment
3. Runbook matching or LLM-generated custom runbook
4. Escalation rule evaluation with time-based triggers
5. Step-by-step response workflow with automated/manual step classification
6. Real-time status tracking and team coordination

## License

Apache-2.0
