"""
Incident Response Coordinator

An autonomous agent that triages on-call incidents, executes runbooks,
manages escalation chains, and coordinates cross-team response efforts.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

import streamlit as st
from agno.assistant import Assistant
from agno.models.openai import OpenAIChat


class IncidentSeverity(Enum):
    SEV1 = "sev1"  # Critical - immediate response
    SEV2 = "sev2"  # High - < 30 min response
    SEV3 = "sev3"  # Medium - < 2 hour response
    SEV4 = "sev4"  # Low - next business day


class IncidentStatus(Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EscalationLevel(Enum):
    L1 = "l1"  # On-call engineer
    L2 = "l2"  # Team lead
    L3 = "l3"  # Engineering manager
    L4 = "l4"  # Director/VP
    L5 = "l5"  # Executive


@dataclass
class Incident:
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    affected_services: List[str]
    detected_at: str
    acknowledged_at: Optional[str]
    resolved_at: Optional[str]
    assigned_to: Optional[str]
    runbook_executed: Optional[str]
    escalation_level: EscalationLevel
    updates: List[Dict]


@dataclass
class RunbookStep:
    step_number: int
    instruction: str
    expected_outcome: str
    automated: bool
    command: Optional[str]
    verification: Optional[str]


@dataclass
class EscalationRule:
    level: EscalationLevel
    trigger_condition: str
    notify_channels: List[str]
    response_time_minutes: int


class IncidentResponseCoordinator:
    """
    Primary entry point for incident triage, runbook execution, and escalation management.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Incident triage, runbook execution, escalation management, and cross-team coordination",
            instructions=[
                "Triage incoming incidents based on severity, affected services, and business impact",
                "Generate and execute appropriate runbooks for each incident type",
                "Manage escalation chains with time-based triggers",
                "Coordinate communication across response teams and stakeholders"
            ]
        )
        self.incidents: List[Incident] = []
        self.runbooks: Dict[str, List[RunbookStep]] = {}
        self.escalation_rules: List[EscalationRule] = []
        self._init_default_runbooks()
        self._init_default_escalation_rules()

    def _init_default_runbooks(self):
        """
        Initialize default runbooks for common incident types.
        """
        self.runbooks["database_connection_timeout"] = [
            RunbookStep(1, "Check database connection pool status", "Pool utilization < 80%", True, "check_db_pool", "Pool status healthy"),
            RunbookStep(2, "Verify database server CPU and memory", "CPU < 80%, Memory < 90%", True, "check_db_metrics", "Metrics within thresholds"),
            RunbookStep(3, "Check for long-running queries", "No queries > 60s", True, "check_long_queries", "No blocking queries"),
            RunbookStep(4, "Restart connection pool if necessary", "Connections reset successfully", False, None, "Pool restarted"),
            RunbookStep(5, "Escalate to DBA team if unresolved", "DBA team notified", False, None, "Escalation sent"),
        ]

        self.runbooks["high_error_rate"] = [
            RunbookStep(1, "Check error logs for patterns", "Top 5 errors identified", True, "analyze_error_logs", "Error patterns identified"),
            RunbookStep(2, "Verify recent deployments", "No failed deployments in last 4 hours", True, "check_deployments", "Deployment status confirmed"),
            RunbookStep(3, "Check upstream service health", "All dependencies healthy", True, "check_dependencies", "Dependencies healthy"),
            RunbookStep(4, "Consider rollback if deployment-related", "Rollback executed or not needed", False, None, "Rollback decision made"),
            RunbookStep(5, "Scale up if capacity-related", "Auto-scaling triggered or not needed", False, None, "Scaling decision made"),
        ]

        self.runbooks["memory_leak"] = [
            RunbookStep(1, "Check memory usage trends", "Memory growth pattern identified", True, "check_memory_trend", "Trend confirmed"),
            RunbookStep(2, "Identify top memory consumers", "Top 5 processes identified", True, "check_top_processes", "Processes identified"),
            RunbookStep(3, "Check for known memory leak patterns", "Pattern match found or not", True, "check_leak_patterns", "Pattern analysis complete"),
            RunbookStep(4, "Restart affected service", "Service restarted successfully", False, None, "Service restarted"),
            RunbookStep(5, "Schedule heap dump analysis", "Heap dump scheduled", False, None, "Analysis scheduled"),
        ]

    def _init_default_escalation_rules(self):
        """
        Initialize default escalation rules.
        """
        self.escalation_rules = [
            EscalationRule(EscalationLevel.L1, "Incident created", ["slack", "pagerduty"], 5),
            EscalationRule(EscalationLevel.L2, "Not acknowledged in 5 minutes", ["slack", "pagerduty", "email"], 15),
            EscalationRule(EscalationLevel.L3, "Not resolved in 30 minutes (SEV1) or 2 hours (SEV2)", ["slack", "pagerduty", "email", "sms"], 30),
            EscalationRule(EscalationLevel.L4, "Not resolved in 1 hour (SEV1) or 4 hours (SEV2)", ["slack", "pagerduty", "email", "sms", "phone"], 60),
            EscalationRule(EscalationLevel.L5, "Business-critical service down > 2 hours", ["slack", "pagerduty", "email", "sms", "phone"], 120),
        ]

    def triage_incident(self, title: str, description: str, affected_services: List[str]) -> Incident:
        """
        Triage a new incident and determine severity.
        """
        prompt = f"""
        Triage this incident:

        Title: {title}
        Description: {description}
        Affected Services: {', '.join(affected_services)}

        Determine:
        1. Severity (sev1/sev2/sev3/sev4) based on business impact
        2. Most appropriate runbook type
        3. Initial response team
        4. Estimated time to resolution

        Severity guidelines:
        - SEV1: Complete service outage, data loss, security breach, revenue impact > $100K/hour
        - SEV2: Major functionality degraded, partial outage, revenue impact $10K-$100K/hour
        - SEV3: Minor functionality issues, workarounds available, revenue impact < $10K/hour
        - SEV4: Cosmetic issues, documentation problems, no revenue impact

        Respond in JSON format:
        {{
            "severity": "<sev1/sev2/sev3/sev4>",
            "runbook_type": "<type>",
            "response_team": "<team>",
            "estimated_resolution": "<time estimate>"
        }}
        """

        response = self.assistant.run(prompt)
        content = response.content

        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            severity = IncidentSeverity(data.get("severity", "sev3"))
        except (json.JSONDecodeError, ValueError):
            severity = IncidentSeverity.SEV3

        incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            affected_services=affected_services,
            detected_at=datetime.now().isoformat(),
            acknowledged_at=None,
            resolved_at=None,
            assigned_to=None,
            runbook_executed=None,
            escalation_level=EscalationLevel.L1,
            updates=[]
        )

        self.incidents.append(incident)
        return incident

    def generate_runbook(self, incident: Incident) -> List[RunbookStep]:
        """
        Generate a runbook for an incident.
        """
        # Check if we have a matching runbook
        for runbook_type, steps in self.runbooks.items():
            if runbook_type.lower() in incident.title.lower() or runbook_type.lower() in incident.description.lower():
                return steps

        # Generate custom runbook via LLM
        prompt = f"""
        Generate an incident response runbook for:

        Title: {incident.title}
        Description: {incident.description}
        Affected Services: {', '.join(incident.affected_services)}
        Severity: {incident.severity.value}

        Create 5-7 steps that include:
        - Diagnostic steps (automated where possible)
        - Mitigation steps
        - Verification steps
        - Escalation triggers

        Respond in JSON format:
        [
            {{
                "step_number": <number>,
                "instruction": "<instruction>",
                "expected_outcome": "<outcome>",
                "automated": <true/false>,
                "command": "<command or null>",
                "verification": "<verification or null>"
            }}
        ]
        """

        response = self.assistant.run(prompt)
        content = response.content

        steps = []
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            for item in data:
                steps.append(RunbookStep(
                    step_number=item.get("step_number", 0),
                    instruction=item.get("instruction", ""),
                    expected_outcome=item.get("expected_outcome", ""),
                    automated=item.get("automated", False),
                    command=item.get("command"),
                    verification=item.get("verification")
                ))
        except (json.JSONDecodeError, ValueError):
            steps = [
                RunbookStep(1, "Investigate incident details", "Details understood", False, None, None),
                RunbookStep(2, "Check affected service health", "Service status confirmed", True, "check_health", "Status healthy or degraded"),
                RunbookStep(3, "Identify root cause", "Root cause identified", False, None, None),
                RunbookStep(4, "Apply mitigation", "Issue mitigated", False, None, None),
                RunbookStep(5, "Verify resolution", "Service restored", True, "verify_service", "Service healthy"),
            ]

        return steps

    def check_escalation(self, incident: Incident) -> Optional[EscalationRule]:
        """
        Check if an incident needs escalation.
        """
        detected = datetime.fromisoformat(incident.detected_at)
        elapsed_minutes = (datetime.now() - detected).total_seconds() / 60

        for rule in self.escalation_rules:
            if rule.level.value > incident.escalation_level.value:
                if elapsed_minutes >= rule.response_time_minutes:
                    # Check if severity matches
                    if incident.severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2]:
                        return rule
                    elif incident.severity == IncidentSeverity.SEV3 and rule.level.value <= EscalationLevel.L3.value:
                        return rule

        return None

    def handle_request(self, title: str, description: str, affected_services: List[str]) -> Dict:
        """
        Process an incident and return triage results.
        """
        incident = self.triage_incident(title, description, affected_services)
        runbook = self.generate_runbook(incident)
        escalation = self.check_escalation(incident)

        return {
            "incident_id": incident.incident_id,
            "severity": incident.severity.value,
            "status": incident.status.value,
            "affected_services": incident.affected_services,
            "detected_at": incident.detected_at,
            "escalation_level": incident.escalation_level.value,
            "runbook": [{
                "step": s.step_number,
                "instruction": s.instruction,
                "expected": s.expected_outcome,
                "automated": s.automated,
                "command": s.command,
                "verification": s.verification
            } for s in runbook],
            "escalation_needed": escalation is not None,
            "escalation_details": {
                "level": escalation.level.value,
                "channels": escalation.notify_channels,
                "response_time": escalation.response_time_minutes
            } if escalation else None
        }


# Streamlit interface
st.title("Incident Response Coordinator")
st.caption("Triage on-call incidents, execute runbooks, manage escalation chains, and coordinate response efforts")

api_key = st.text_input("OpenAI API Key", type="password")

st.markdown("### Create New Incident")

title = st.text_input("Incident Title", placeholder="e.g., Database connection timeout in production")

description = st.text_area("Description", 
    placeholder="Describe the incident symptoms, error messages, and user impact...",
    height=100)

affected_services = st.multiselect(
    "Affected Services",
    ["API Gateway", "Authentication", "Database", "Payment Processing", "Notification Service", 
     "Search", "CDN", "Cache", "Message Queue", "File Storage"],
    default=["API Gateway"]
)

if api_key and title and description:
    coordinator = IncidentResponseCoordinator(api_key)
    result = coordinator.handle_request(title, description, affected_services)

    st.subheader("Incident Triage Results")

    severity_color = {
        "sev1": "red",
        "sev2": "orange",
        "sev3": "yellow",
        "sev4": "green"
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Incident ID", result["incident_id"])
    with col2:
        st.markdown(f"Severity: :{severity_color.get(result['severity'], 'gray')}[{result['severity'].upper()}]")
    with col3:
        st.metric("Status", result["status"].upper())

    st.caption(f"Affected: {', '.join(result['affected_services'])}")
    st.caption(f"Detected: {result['detected_at']}")

    if result["escalation_needed"]:
        escalation = result["escalation_details"]
        st.error(f"Escalation Required: {escalation['level'].upper()} | Channels: {', '.join(escalation['channels'])} | Response Time: {escalation['response_time']} min")
    else:
        st.success("No escalation needed at this time")

    st.subheader("Runbook")

    for step in result["runbook"]:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**Step {step['step']}**")
                if step['automated']:
                    st.caption("🤖 Automated")
                else:
                    st.caption("👤 Manual")
            with col2:
                st.write(step['instruction'])
                st.caption(f"Expected: {step['expected']}")
                if step['command']:
                    st.code(step['command'], language='bash')
                if step['verification']:
                    st.caption(f"Verification: {step['verification']}")
            st.divider()
