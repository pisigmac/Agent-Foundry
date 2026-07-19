"""
Log Anomaly Detector

An autonomous agent that analyzes application logs, detects anomalies,
identifies patterns, and performs incident triage with severity scoring.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter, defaultdict
from datetime import datetime

import streamlit as st
from agno.assistant import Assistant
from agno.models.openai import OpenAIChat


class AnomalyType(Enum):
    ERROR_SPIKE = "error_spike"
    LATENCY_SPIKE = "latency_spike"
    PATTERN_BREAK = "pattern_break"
    SECURITY_EVENT = "security_event"
    CAPACITY_ISSUE = "capacity_issue"
    UNKNOWN = "unknown"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class LogPattern:
    pattern: str
    count: int
    frequency: float
    is_anomaly: bool
    severity: Severity


@dataclass
class Anomaly:
    timestamp: str
    type: AnomalyType
    description: str
    affected_services: List[str]
    severity: Severity
    confidence: float
    recommended_action: str


class LogAnomalyDetector:
    """
    Primary entry point for log analysis, anomaly detection, and incident triage.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Log analysis, anomaly detection, and incident triage",
            instructions=[
                "Analyze application logs for error patterns, latency spikes, and anomalies",
                "Identify affected services and components from log context",
                "Classify anomalies by type and severity with confidence scores",
                "Recommend specific actions for each detected anomaly"
            ]
        )
        self.patterns: Dict[str, int] = defaultdict(int)
        self.baseline_established = False

    def extract_patterns(self, logs: str) -> List[LogPattern]:
        """
        Extract and count log patterns.
        """
        lines = logs.strip().split("\n")

        # Extract error patterns
        error_pattern = r"(?:ERROR|Exception|Traceback|Failed|failed)[^\n]*"
        errors = re.findall(error_pattern, logs, re.IGNORECASE)

        # Extract service names
        service_pattern = r"\[(\w+(?:[-_]\w+)*)\]|\b(service|app|api|worker|db)\s*[:=]?\s*(\w+)"
        services = re.findall(service_pattern, logs, re.IGNORECASE)
        service_names = [s[0] or s[2] for s in services if s[0] or s[2]]

        # Extract timestamps
        timestamp_pattern = r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)"
        timestamps = re.findall(timestamp_pattern, logs)

        # Count patterns
        patterns = []

        if errors:
            error_count = len(errors)
            patterns.append(LogPattern(
                pattern="ERROR/Exception",
                count=error_count,
                frequency=error_count / max(len(lines), 1),
                is_anomaly=error_count > 10,
                severity=Severity.CRITICAL if error_count > 50 else Severity.HIGH if error_count > 10 else Severity.MEDIUM
            ))

        if service_names:
            service_counter = Counter(service_names)
            for service, count in service_counter.most_common(5):
                patterns.append(LogPattern(
                    pattern=f"Service: {service}",
                    count=count,
                    frequency=count / max(len(lines), 1),
                    is_anomaly=False,
                    severity=Severity.INFO
                ))

        if timestamps:
            patterns.append(LogPattern(
                pattern="Timestamped logs",
                count=len(timestamps),
                frequency=len(timestamps) / max(len(lines), 1),
                is_anomaly=False,
                severity=Severity.INFO
            ))

        return patterns

    def detect_anomalies(self, logs: str, patterns: List[LogPattern]) -> List[Anomaly]:
        """
        Detect anomalies in logs using LLM analysis.
        """
        # Sample logs for analysis (first 3000 chars)
        log_sample = logs[:3000]

        prompt = f"""
        Analyze these application logs for anomalies:

        ```
        {log_sample}
        ```

        Detected patterns:
        {json.dumps([{"pattern": p.pattern, "count": p.count, "frequency": f"{p.frequency:.2%}"} for p in patterns], indent=2)}

        Identify:
        1. Error spikes or unusual error rates
        2. Latency or performance issues
        3. Security events (unauthorized access, injection attempts)
        4. Capacity issues (memory, CPU, disk)
        5. Pattern breaks (unusual sequences or missing expected logs)

        For each anomaly, provide:
        - Type: error_spike, latency_spike, pattern_break, security_event, capacity_issue
        - Description
        - Affected services
        - Severity: critical/high/medium/low
        - Confidence: 0.0-1.0
        - Recommended action

        Respond in JSON format:
        [
            {{
                "type": "<type>",
                "description": "<description>",
                "affected_services": ["<service1>", "<service2>"],
                "severity": "<severity>",
                "confidence": <number>,
                "recommended_action": "<action>"
            }}
        ]
        """

        response = self.assistant.run(prompt)
        content = response.content

        anomalies = []
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            for item in data:
                anomalies.append(Anomaly(
                    timestamp=datetime.now().isoformat(),
                    type=AnomalyType(item.get("type", "unknown")),
                    description=item.get("description", ""),
                    affected_services=item.get("affected_services", []),
                    severity=Severity(item.get("severity", "medium")),
                    confidence=item.get("confidence", 0.5),
                    recommended_action=item.get("recommended_action", "Investigate")
                ))
        except (json.JSONDecodeError, ValueError):
            pass

        return anomalies

    def handle_request(self, logs: str, service_name: Optional[str] = None) -> Dict:
        """
        Process logs and return anomaly detection results.
        """
        patterns = self.extract_patterns(logs)
        anomalies = self.detect_anomalies(logs, patterns)

        # Triage: group by severity
        critical = [a for a in anomalies if a.severity == Severity.CRITICAL]
        high = [a for a in anomalies if a.severity == Severity.HIGH]
        medium = [a for a in anomalies if a.severity == Severity.MEDIUM]

        return {
            "service": service_name or "unknown",
            "log_lines": len(logs.strip().split("\n")),
            "patterns_detected": len(patterns),
            "anomalies_found": len(anomalies),
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
            "patterns": [{
                "pattern": p.pattern,
                "count": p.count,
                "frequency": f"{p.frequency:.2%}",
                "anomaly": p.is_anomaly,
                "severity": p.severity.value
            } for p in patterns],
            "anomalies": [{
                "type": a.type.value,
                "description": a.description,
                "services": a.affected_services,
                "severity": a.severity.value,
                "confidence": f"{a.confidence:.0%}",
                "action": a.recommended_action
            } for a in anomalies]
        }


# Streamlit interface
st.title("Log Anomaly Detector")
st.caption("Analyze application logs, detect anomalies, identify patterns, and perform incident triage")

api_key = st.text_input("OpenAI API Key", type="password")

service_name = st.text_input("Service Name", placeholder="e.g., api-gateway, payment-service, user-service")

logs = st.text_area("Application Logs", 
    placeholder="Paste application logs here (supports JSON, plain text, syslog formats)...",
    height=400)

if api_key and logs:
    detector = LogAnomalyDetector(api_key)
    result = detector.handle_request(logs, service_name)

    st.subheader("Analysis Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Log Lines", result["log_lines"])
    with col2:
        st.metric("Anomalies", result["anomalies_found"], delta_color="inverse")
    with col3:
        st.metric("Critical", result["critical_count"], delta_color="inverse")
    with col4:
        st.metric("High", result["high_count"], delta_color="inverse")

    if result["patterns"]:
        st.subheader("Detected Patterns")

        pattern_data = []
        for p in result["patterns"]:
            pattern_data.append({
                "Pattern": p["pattern"],
                "Count": p["count"],
                "Frequency": p["frequency"],
                "Severity": p["severity"].upper()
            })

        st.dataframe(pattern_data, use_container_width=True)

    if result["anomalies"]:
        st.subheader("Anomalies")

        for anomaly in result["anomalies"]:
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green", "info": "blue"}

            with st.container():
                st.markdown(f"**{anomaly['type'].replace('_', ' ').title()}**")
                st.caption(f":{severity_color.get(anomaly['severity'], 'gray')}[{anomaly['severity'].upper()}] | Confidence: {anomaly['confidence']}")

                if anomaly['services']:
                    st.caption(f"Affected: {', '.join(anomaly['services'])}")

                st.write(anomaly['description'])
                st.info(f"Action: {anomaly['action']}")
                st.divider()
    else:
        st.success("No anomalies detected in the analyzed logs.")
