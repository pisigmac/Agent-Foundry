"""
Code Review Assistant

An autonomous agent that reviews pull requests, detects issues,
suggests improvements, and generates review comments.
"""

import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

import streamlit as st
from agno.assistant import Assistant
from agno.models.openai import OpenAIChat
from agno.tools.github import GithubTools

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ReviewComment:
    file_path: str
    line_number: int
    severity: Severity
    message: str
    suggestion: Optional[str] = None
    category: str = "general"

class CodeReviewAssistant:
    """
    Primary entry point for automated code review processing.
    """

    def __init__(self, api_key: str, github_token: str):
        self.api_key = api_key
        self.github_token = github_token
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            tools=[GithubTools(access_token=github_token)],
            description="Automated code review and quality analysis",
            instructions=[
                "Analyze code for bugs, security issues, and style violations",
                "Suggest specific improvements with code examples",
                "Rate severity of each issue found",
                "Focus on maintainability and performance"
            ]
        )

    def analyze_diff(self, diff_text: str) -> List[ReviewComment]:
        """
        Parse a git diff and extract changed lines for review.
        """
        comments = []
        current_file = None
        line_number = 0

        for line in diff_text.split("\n"):
            if line.startswith("diff --git"):
                match = re.search(r"b/(.+)$", line)
                if match:
                    current_file = match.group(1)
            elif line.startswith("@@"):
                match = re.search(r"@@ -\d+,?\d* \+(\d+)", line)
                if match:
                    line_number = int(match.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                if current_file and line_number > 0:
                    comments.append(ReviewComment(
                        file_path=current_file,
                        line_number=line_number,
                        severity=Severity.INFO,
                        message="Changed line detected",
                        category="diff"
                    ))
                line_number += 1

        return comments

    def handle_request(self, code: str, language: str = "python") -> Dict:
        """
        Process code and return structured review results.
        """
        prompt = f"""
        Review the following {language} code. Identify:
        1. Bugs and logical errors
        2. Security vulnerabilities
        3. Performance issues
        4. Style violations
        5. Missing documentation

        For each issue, provide:
        - Severity (critical/high/medium/low/info)
        - Line number (if applicable)
        - Description
        - Suggested fix

        Code:
        ```{language}
        {code}
        ```
        """

        response = self.assistant.run(prompt)

        return {
            "raw_review": response.content,
            "language": language,
            "issue_count": len(re.findall(r"Severity:", response.content)),
            "has_critical": "critical" in response.content.lower()
        }

# Streamlit interface
st.title("Code Review Assistant")
st.caption("Automated code review with severity scoring and fix suggestions")

api_key = st.text_input("OpenAI API Key", type="password")
github_token = st.text_input("GitHub Token (optional)", type="password")

language = st.selectbox(
    "Language",
    ["python", "javascript", "typescript", "java", "go", "rust", "cpp"]
)

code = st.text_area("Code to Review", height=300)

if api_key and code:
    reviewer = CodeReviewAssistant(api_key, github_token or "")
    result = reviewer.handle_request(code, language)

    st.subheader("Review Results")
    st.write(result["raw_review"])

    if result["has_critical"]:
        st.error("Critical issues found! Please address before merging.")

    st.metric("Issues Found", result["issue_count"])
