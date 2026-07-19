"""
DevOps Pipeline Monitor

An autonomous agent that monitors CI/CD pipelines, detects failures,
analyzes root causes, and suggests auto-remediation steps.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import streamlit as st
from agno.assistant import Assistant
from agno.models.openai import OpenAIChat


class PipelineStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    UNSTABLE = "unstable"
    ABORTED = "aborted"
    PENDING = "pending"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PipelineRun:
    pipeline_id: str
    run_id: str
    status: PipelineStatus
    duration_seconds: int
    stage_results: List[Dict]
    logs: str
    timestamp: str


@dataclass
class FailureAnalysis:
    stage: str
    error_type: str
    description: str
    root_cause: str
    severity: Severity
    remediation: str
    estimated_fix_time: str


class DevOpsPipelineMonitor:
    """
    Primary entry point for CI/CD pipeline monitoring and failure analysis.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="CI/CD pipeline monitoring, failure detection, and auto-remediation",
            instructions=[
                "Analyze pipeline logs to identify failure points and root causes",
                "Classify errors by type: build, test, deployment, infrastructure, dependency",
                "Suggest specific remediation steps with estimated fix times",
                "Identify flaky tests and unstable stages"
            ]
        )

    def parse_pipeline_logs(self, logs: str) -> List[Dict]:
        """
        Parse pipeline logs and extract stage results and errors.
        """
        stages = []

        # Pattern: stage headers
        stage_pattern = r"(?:Stage|STEP|stage)\s*['"]?([\w-]+)['"]?\s*(?:started|begin|running)?"
        stage_matches = re.finditer(stage_pattern, logs, re.IGNORECASE)

        for match in stage_matches:
            stages.append({
                "name": match.group(1),
                "status": "unknown",
                "errors": []
            })

        # Pattern: error messages
        error_pattern = r"(?:ERROR|FAIL|FAILED|Exception|Traceback)[^\n]*"
        error_matches = re.finditer(error_pattern, logs, re.IGNORECASE)

        for match in error_matches:
            error_text = match.group(0).strip()
            # Associate error with nearest stage
            if stages:
                stages[-1]["errors"].append(error_text)
                stages[-1]["status"] = "failed"

        # Pattern: success indicators
        success_pattern = r"(?:SUCCESS|passed|completed|done)\s*(?:successfully)?"
        if re.search(success_pattern, logs, re.IGNORECASE) and not stages:
            stages.append({"name": "pipeline", "status": "success", "errors": []})

        return stages

    def analyze_failure(self, stage: Dict, logs: str) -> FailureAnalysis:
        """
        Analyze a failed stage and determine root cause.
        """
        prompt = f"""
        Analyze this CI/CD pipeline failure:

        Stage: {stage['name']}
        Status: {stage['status']}
        Errors: {json.dumps(stage['errors'], indent=2)}

        Relevant log context:
        ```
        {logs[:2000]}
        ```

        Identify:
        1. Error type (build, test, deployment, infrastructure, dependency, configuration)
        2. Root cause description
        3. Severity (critical/high/medium/low)
        4. Specific remediation steps
        5. Estimated fix time

        Respond in JSON format:
        {{
            "error_type": "<type>",
            "description": "<description>",
            "root_cause": "<root cause>",
            "severity": "<severity>",
            "remediation": "<steps>",
            "estimated_fix_time": "<time estimate>"
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

            return FailureAnalysis(
                stage=stage["name"],
                error_type=data.get("error_type", "unknown"),
                description=data.get("description", ""),
                root_cause=data.get("root_cause", ""),
                severity=Severity(data.get("severity", "medium")),
                remediation=data.get("remediation", "Review logs for details"),
                estimated_fix_time=data.get("estimated_fix_time", "Unknown")
            )
        except (json.JSONDecodeError, ValueError):
            return FailureAnalysis(
                stage=stage["name"],
                error_type="parse_error",
                description="Could not analyze failure",
                root_cause="Insufficient log data",
                severity=Severity.MEDIUM,
                remediation="Review full pipeline logs manually",
                estimated_fix_time="Unknown"
            )

    def handle_request(self, logs: str, pipeline_name: Optional[str] = None) -> Dict:
        """
        Process pipeline logs and return monitoring results.
        """
        stages = self.parse_pipeline_logs(logs)

        failed_stages = [s for s in stages if s["status"] == "failed"]

        analyses = []
        for stage in failed_stages:
            analysis = self.analyze_failure(stage, logs)
            analyses.append({
                "stage": analysis.stage,
                "error_type": analysis.error_type,
                "description": analysis.description,
                "root_cause": analysis.root_cause,
                "severity": analysis.severity.value,
                "remediation": analysis.remediation,
                "estimated_fix_time": analysis.estimated_fix_time
            })

        # Determine overall status
        if any(a["severity"] == "critical" for a in analyses):
            overall_status = PipelineStatus.FAILED
        elif analyses:
            overall_status = PipelineStatus.UNSTABLE
        elif not stages:
            overall_status = PipelineStatus.PENDING
        else:
            overall_status = PipelineStatus.SUCCESS

        return {
            "pipeline_name": pipeline_name or "unknown",
            "overall_status": overall_status.value,
            "stages_analyzed": len(stages),
            "failures": len(failed_stages),
            "analyses": analyses,
            "flaky_stages": [s["name"] for s in stages if len(s.get("errors", [])) > 3]
        }


# Streamlit interface
st.title("DevOps Pipeline Monitor")
st.caption("Monitor CI/CD pipelines, detect failures, analyze root causes, and suggest auto-remediation")

api_key = st.text_input("OpenAI API Key", type="password")

pipeline_name = st.text_input("Pipeline Name", placeholder="e.g., production-deploy, api-tests")

logs = st.text_area("Pipeline Logs", 
    placeholder="Paste CI/CD logs from Jenkins, GitHub Actions, GitLab CI, CircleCI, etc.",
    height=400)

if api_key and logs:
    monitor = DevOpsPipelineMonitor(api_key)
    result = monitor.handle_request(logs, pipeline_name)

    # Status indicator
    status_color = {
        "success": "green",
        "failed": "red",
        "unstable": "orange",
        "aborted": "gray",
        "pending": "blue"
    }

    st.subheader(f"Pipeline Status: :{status_color.get(result['overall_status'], 'gray')}[{result['overall_status'].upper()}]")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Stages", result["stages_analyzed"])
    with col2:
        st.metric("Failures", result["failures"], delta_color="inverse")
    with col3:
        st.metric("Flaky Stages", len(result["flaky_stages"]))

    if result["analyses"]:
        st.subheader("Failure Analysis")

        for analysis in result["analyses"]:
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green"}

            with st.container():
                st.markdown(f"### Stage: {analysis['stage']}")
                st.caption(f"Error Type: {analysis['error_type']} | :{severity_color.get(analysis['severity'], 'gray')}[{analysis['severity'].upper()}]")

                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Description:**")
                    st.write(analysis['description'])
                with col2:
                    st.write("**Root Cause:**")
                    st.write(analysis['root_cause'])

                st.info(f"**Fix:** {analysis['remediation']}")
                st.caption(f"Estimated Fix Time: {analysis['estimated_fix_time']}")
                st.divider()

    if result["flaky_stages"]:
        st.warning(f"Flaky stages detected: {', '.join(result['flaky_stages'])}")
