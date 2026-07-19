"""
Accessibility Auditor

An autonomous agent that audits web pages and applications for WCAG compliance,
identifies accessibility issues, and provides remediation guidance with code fixes.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import streamlit as st
from agno.assistant import Assistant
from agno.models.openai import OpenAIChat


class WCAGLevel(Enum):
    A = "A"
    AA = "AA"
    AAA = "AAA"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AccessibilityIssue:
    guideline: str
    criterion: str
    level: WCAGLevel
    description: str
    element: Optional[str]
    impact: str
    severity: Severity
    remediation: str
    code_fix: Optional[str]
    automated_detectable: bool


class AccessibilityAuditor:
    """
    Primary entry point for WCAG compliance auditing and accessibility remediation.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Web accessibility auditing, WCAG compliance checking, and remediation guidance",
            instructions=[
                "Audit HTML/CSS/JS for WCAG 2.1 compliance at A, AA, and AAA levels",
                "Identify missing alt text, keyboard navigation issues, color contrast problems",
                "Detect missing ARIA labels, improper heading hierarchy, focus management issues",
                "Provide specific code fixes for each identified issue"
            ]
        )

    def audit_html(self, html_content: str) -> List[AccessibilityIssue]:
        """
        Audit HTML content for accessibility issues.
        """
        prompt = f"""
        Perform a WCAG 2.1 accessibility audit on this HTML:

        ```html
        {html_content[:5000]}
        ```

        Check for:
        1. Missing or empty alt attributes on images (1.1.1)
        2. Missing form labels (1.3.1, 3.3.2)
        3. Insufficient color contrast (1.4.3)
        4. Missing keyboard navigation (2.1.1, 2.1.2)
        5. Missing focus indicators (2.4.7)
        6. Improper heading hierarchy (1.3.1)
        7. Missing ARIA labels on interactive elements (4.1.2)
        8. Missing language attribute (3.1.1)
        9. Missing skip links (2.4.1)
        10. Form error identification (3.3.1)

        For each issue, provide:
        - Guideline number (e.g., 1.1.1)
        - Criterion description
        - WCAG level (A/AA/AAA)
        - Description of the issue
        - Affected HTML element
        - User impact
        - Severity (critical/high/medium/low)
        - Specific code fix
        - Whether it's automatically detectable

        Respond in JSON format:
        [
            {{
                "guideline": "<number>",
                "criterion": "<description>",
                "level": "<A/AA/AAA>",
                "description": "<issue description>",
                "element": "<element or null>",
                "impact": "<user impact>",
                "severity": "<severity>",
                "remediation": "<fix description>",
                "code_fix": "<code snippet or null>",
                "automated_detectable": <true/false>
            }}
        ]
        """

        response = self.assistant.run(prompt)
        content = response.content

        issues = []
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            for item in data:
                issues.append(AccessibilityIssue(
                    guideline=item.get("guideline", ""),
                    criterion=item.get("criterion", ""),
                    level=WCAGLevel(item.get("level", "A")),
                    description=item.get("description", ""),
                    element=item.get("element"),
                    impact=item.get("impact", ""),
                    severity=Severity(item.get("severity", "medium")),
                    remediation=item.get("remediation", ""),
                    code_fix=item.get("code_fix"),
                    automated_detectable=item.get("automated_detectable", True)
                ))
        except (json.JSONDecodeError, ValueError):
            pass

        return issues

    def audit_css(self, css_content: str) -> List[AccessibilityIssue]:
        """
        Audit CSS for accessibility issues.
        """
        prompt = f"""
        Audit this CSS for accessibility issues:

        ```css
        {css_content[:3000]}
        ```

        Check for:
        1. Color contrast ratios below 4.5:1 (1.4.3)
        2. Font sizes too small for readability (1.4.4)
        3. Animation without reduced-motion support (2.2.2)
        4. Content hidden with display:none (visible to screen readers?)
        5. Focus styles removed or insufficient (2.4.7)

        Respond in the same JSON format as HTML audit.
        """

        response = self.assistant.run(prompt)
        content = response.content

        issues = []
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            for item in data:
                issues.append(AccessibilityIssue(
                    guideline=item.get("guideline", ""),
                    criterion=item.get("criterion", ""),
                    level=WCAGLevel(item.get("level", "A")),
                    description=item.get("description", ""),
                    element=item.get("element"),
                    impact=item.get("impact", ""),
                    severity=Severity(item.get("severity", "medium")),
                    remediation=item.get("remediation", ""),
                    code_fix=item.get("code_fix"),
                    automated_detectable=item.get("automated_detectable", True)
                ))
        except (json.JSONDecodeError, ValueError):
            pass

        return issues

    def generate_report(self, issues: List[AccessibilityIssue]) -> Dict:
        """
        Generate a comprehensive accessibility report.
        """
        by_level = {"A": 0, "AA": 0, "AAA": 0}
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        auto_detectable = 0

        for issue in issues:
            by_level[issue.level.value] += 1
            by_severity[issue.severity.value] += 1
            if issue.automated_detectable:
                auto_detectable += 1

        return {
            "total_issues": len(issues),
            "by_level": by_level,
            "by_severity": by_severity,
            "auto_detectable": auto_detectable,
            "manual_review_needed": len(issues) - auto_detectable,
            "compliance_score": max(0, 100 - (by_severity["critical"] * 20 + by_severity["high"] * 10 + by_severity["medium"] * 5))
        }

    def handle_request(self, html_content: Optional[str] = None, css_content: Optional[str] = None,
                      url: Optional[str] = None) -> Dict:
        """
        Process an accessibility audit request.
        """
        all_issues = []

        if html_content:
            all_issues.extend(self.audit_html(html_content))

        if css_content:
            all_issues.extend(self.audit_css(css_content))

        report = self.generate_report(all_issues)

        return {
            "url": url or "inline",
            "total_issues": len(all_issues),
            "report": report,
            "issues": [{
                "guideline": i.guideline,
                "criterion": i.criterion,
                "level": i.level.value,
                "description": i.description,
                "element": i.element,
                "impact": i.impact,
                "severity": i.severity.value,
                "remediation": i.remediation,
                "code_fix": i.code_fix,
                "automated": i.automated_detectable
            } for i in all_issues]
        }


# Streamlit interface
st.title("Accessibility Auditor")
st.caption("Audit web pages for WCAG compliance, identify issues, and get remediation guidance with code fixes")

api_key = st.text_input("OpenAI API Key", type="password")

url = st.text_input("Page URL (Optional)", placeholder="https://example.com")

tab1, tab2 = st.tabs(["HTML Audit", "CSS Audit"])

with tab1:
    html_content = st.text_area("HTML Content", 
        placeholder="Paste HTML content to audit...",
        height=300)

    if api_key and html_content:
        auditor = AccessibilityAuditor(api_key)
        result = auditor.handle_request(html_content=html_content, url=url)

        st.subheader("Audit Results")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Issues", result["total_issues"])
        with col2:
            st.metric("Compliance Score", f"{result['report']['compliance_score']}%")
        with col3:
            st.metric("Auto-Detectable", result["report"]["auto_detectable"])

        if result["issues"]:
            st.subheader("Issues by Severity")

            for issue in result["issues"]:
                severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green"}

                with st.container():
                    st.markdown(f"**{issue['guideline']}** — {issue['criterion']} ({issue['level']})")
                    st.caption(f":{severity_color.get(issue['severity'], 'gray')}[{issue['severity'].upper()}] | {'Auto-detectable' if issue['automated'] else 'Manual review'}")
                    st.write(issue['description'])

                    if issue['element']:
                        st.caption(f"Element: `{issue['element']}`")

                    st.write(f"**Impact:** {issue['impact']}")
                    st.info(f"**Fix:** {issue['remediation']}")

                    if issue['code_fix']:
                        with st.expander("Code Fix"):
                            st.code(issue['code_fix'], language='html')

                    st.divider()

with tab2:
    css_content = st.text_area("CSS Content", 
        placeholder="Paste CSS content to audit...",
        height=300)

    if api_key and css_content:
        auditor = AccessibilityAuditor(api_key)
        result = auditor.handle_request(css_content=css_content, url=url)

        st.subheader("CSS Audit Results")
        st.metric("Issues Found", result["total_issues"])

        for issue in result["issues"]:
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green"}

            with st.container():
                st.markdown(f"**{issue['guideline']}** — {issue['criterion']}")
                st.caption(f":{severity_color.get(issue['severity'], 'gray')}[{issue['severity'].upper()}]")
                st.write(issue['description'])
                st.info(f"**Fix:** {issue['remediation']}")

                if issue['code_fix']:
                    with st.expander("Code Fix"):
                        st.code(issue['code_fix'], language='css')

                st.divider()
