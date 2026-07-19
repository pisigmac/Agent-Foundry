"""
Content Moderation Agent

An autonomous agent that moderates user-generated content across platforms,
detects policy violations, classifies severity, and handles appeals with
explanation generation.
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
import pandas as pd


class ViolationType(Enum):
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    SPAM = "spam"
    SELF_HARM = "self_harm"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    COPYRIGHT = "copyright"
    IMPERSONATION = "impersonation"
    MANIPULATION = "manipulation"
    NONE = "none"


class Severity(Enum):
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"            # Remove within 1 hour
    MEDIUM = "medium"        # Remove within 24 hours
    LOW = "low"              # Flag for review
    NONE = "none"            # No action


class Action(Enum):
    REMOVE = "remove"
    HIDE = "hide"
    WARN = "warn"
    FLAG = "flag"
    ESCALATE = "escalate"
    APPROVE = "approve"
    SHADOWBAN = "shadowban"


@dataclass
class ModerationDecision:
    content_id: str
    violation_type: ViolationType
    severity: Severity
    action: Action
    confidence: float
    explanation: str
    policy_references: List[str]
    human_review_required: bool
    appeal_eligible: bool
    timestamp: str


@dataclass
class AppealReview:
    appeal_id: str
    original_decision: ModerationDecision
    appeal_reason: str
    reviewer_notes: Optional[str]
    overturned: bool
    new_decision: Optional[ModerationDecision]


class ContentModerationAgent:
    """
    Primary entry point for content moderation, policy enforcement, and appeal handling.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Content moderation, policy violation detection, severity classification, and appeal review",
            instructions=[
                "Analyze user-generated content for policy violations across multiple categories",
                "Classify severity based on potential harm, reach, and intent",
                "Determine appropriate action: remove, hide, warn, flag, escalate, approve, shadowban",
                "Generate clear explanations for moderation decisions and handle appeals with transparency"
            ]
        )

    def moderate_content(self, content_id: str, content_text: str, content_type: str = "text",
                        platform_policies: Optional[List[str]] = None) -> ModerationDecision:
        """
        Moderate a piece of content against platform policies.
        """
        policies_text = "\n".join(platform_policies) if platform_policies else "Standard community guidelines"

        prompt = f"""
        Moderate this {content_type} content against the platform policies:

        Content ID: {content_id}
        Content: "{content_text}"

        Platform Policies:
        {policies_text}

        Analyze for:
        1. Hate speech or discrimination
        2. Harassment or bullying
        3. Misinformation or disinformation
        4. Spam or commercial abuse
        5. Self-harm or suicide promotion
        6. Violence or graphic content
        7. Sexual content or nudity
        8. Copyright infringement
        9. Impersonation or identity fraud
        10. Manipulation or coordinated inauthentic behavior

        For each violation found, determine:
        - Severity: critical (immediate harm), high (significant harm), medium (moderate harm), low (minor issue), none
        - Action: remove, hide, warn, flag, escalate, approve, shadowban
        - Confidence: 0.0-1.0
        - Policy references: specific policy sections violated
        - Human review required: true/false
        - Appeal eligible: true/false

        If no violations, classify as NONE with APPROVE action.

        Respond in JSON format:
        {{
            "violation_type": "<type or none>",
            "severity": "<severity>",
            "action": "<action>",
            "confidence": <number>,
            "explanation": "<detailed explanation>",
            "policy_references": ["<policy1>", "<policy2>"],
            "human_review_required": <true/false>,
            "appeal_eligible": <true/false>
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

            return ModerationDecision(
                content_id=content_id,
                violation_type=ViolationType(data.get("violation_type", "none")),
                severity=Severity(data.get("severity", "none")),
                action=Action(data.get("action", "approve")),
                confidence=data.get("confidence", 0.5),
                explanation=data.get("explanation", ""),
                policy_references=data.get("policy_references", []),
                human_review_required=data.get("human_review_required", False),
                appeal_eligible=data.get("appeal_eligible", True),
                timestamp=datetime.now().isoformat()
            )
        except (json.JSONDecodeError, ValueError):
            return ModerationDecision(
                content_id=content_id,
                violation_type=ViolationType.NONE,
                severity=Severity.NONE,
                action=Action.APPROVE,
                confidence=0.5,
                explanation="Unable to analyze content. Flagged for human review.",
                policy_references=[],
                human_review_required=True,
                appeal_eligible=True,
                timestamp=datetime.now().isoformat()
            )

    def review_appeal(self, appeal_id: str, original_decision: ModerationDecision,
                     appeal_reason: str) -> AppealReview:
        """
        Review an appeal against a moderation decision.
        """
        prompt = f"""
        Review this content moderation appeal:

        Appeal ID: {appeal_id}
        Original Decision:
        - Violation: {original_decision.violation_type.value}
        - Severity: {original_decision.severity.value}
        - Action: {original_decision.action.value}
        - Explanation: {original_decision.explanation}
        - Confidence: {original_decision.confidence}

        Appeal Reason: "{appeal_reason}"

        Determine:
        1. Was the original decision correct? (true/false)
        2. If overturned, what should the new decision be?
        3. Reviewer notes explaining the decision
        4. Any policy clarifications needed

        Respond in JSON format:
        {{
            "overturned": <true/false>,
            "new_violation_type": "<type or none>",
            "new_severity": "<severity>",
            "new_action": "<action>",
            "new_explanation": "<explanation>",
            "reviewer_notes": "<notes>"
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

            overturned = data.get("overturned", False)

            new_decision = None
            if overturned:
                new_decision = ModerationDecision(
                    content_id=original_decision.content_id,
                    violation_type=ViolationType(data.get("new_violation_type", "none")),
                    severity=Severity(data.get("new_severity", "none")),
                    action=Action(data.get("new_action", "approve")),
                    confidence=0.7,
                    explanation=data.get("new_explanation", ""),
                    policy_references=original_decision.policy_references,
                    human_review_required=True,
                    appeal_eligible=False,
                    timestamp=datetime.now().isoformat()
                )

            return AppealReview(
                appeal_id=appeal_id,
                original_decision=original_decision,
                appeal_reason=appeal_reason,
                reviewer_notes=data.get("reviewer_notes", ""),
                overturned=overturned,
                new_decision=new_decision
            )
        except (json.JSONDecodeError, ValueError):
            return AppealReview(
                appeal_id=appeal_id,
                original_decision=original_decision,
                appeal_reason=appeal_reason,
                reviewer_notes="Unable to process appeal. Escalated to human review.",
                overturned=False,
                new_decision=None
            )

    def handle_request(self, content_id: str, content_text: str, content_type: str = "text",
                      platform_policies: Optional[List[str]] = None,
                      appeal_id: Optional[str] = None,
                      appeal_reason: Optional[str] = None,
                      original_decision: Optional[Dict] = None) -> Dict:
        """
        Process a moderation or appeal request.
        """
        if appeal_id and appeal_reason and original_decision:
            # Handle appeal
            orig = ModerationDecision(
                content_id=original_decision["content_id"],
                violation_type=ViolationType(original_decision["violation_type"]),
                severity=Severity(original_decision["severity"]),
                action=Action(original_decision["action"]),
                confidence=original_decision["confidence"],
                explanation=original_decision["explanation"],
                policy_references=original_decision["policy_references"],
                human_review_required=original_decision["human_review_required"],
                appeal_eligible=original_decision["appeal_eligible"],
                timestamp=original_decision["timestamp"]
            )

            review = self.review_appeal(appeal_id, orig, appeal_reason)

            return {
                "type": "appeal_review",
                "appeal_id": review.appeal_id,
                "overturned": review.overturned,
                "reviewer_notes": review.reviewer_notes,
                "new_decision": {
                    "violation_type": review.new_decision.violation_type.value if review.new_decision else None,
                    "severity": review.new_decision.severity.value if review.new_decision else None,
                    "action": review.new_decision.action.value if review.new_decision else None,
                    "explanation": review.new_decision.explanation if review.new_decision else None
                } if review.new_decision else None
            }
        else:
            # Moderate content
            decision = self.moderate_content(content_id, content_text, content_type, platform_policies)

            return {
                "type": "moderation",
                "content_id": decision.content_id,
                "violation_type": decision.violation_type.value,
                "severity": decision.severity.value,
                "action": decision.action.value,
                "confidence": decision.confidence,
                "explanation": decision.explanation,
                "policy_references": decision.policy_references,
                "human_review_required": decision.human_review_required,
                "appeal_eligible": decision.appeal_eligible,
                "timestamp": decision.timestamp
            }


# Streamlit interface
st.title("Content Moderation Agent")
st.caption("Moderate user-generated content, detect policy violations, classify severity, and handle appeals")

api_key = st.text_input("OpenAI API Key", type="password")

tab1, tab2 = st.tabs(["Content Moderation", "Appeal Review"])

with tab1:
    content_id = st.text_input("Content ID", placeholder="post-12345")
    content_type = st.selectbox("Content Type", ["text", "image", "video", "audio", "comment", "profile"])
    content_text = st.text_area("Content Text", placeholder="Paste the content to moderate...", height=150)

    platform_policies = st.text_area("Platform Policies (one per line, optional)", 
        placeholder="No hate speech\nNo harassment\nNo spam\nNo misinformation",
        height=100)

    policies = [p.strip() for p in platform_policies.split("\n") if p.strip()] if platform_policies else None

    if api_key and content_id and content_text:
        moderator = ContentModerationAgent(api_key)
        result = moderator.handle_request(content_id, content_text, content_type, policies)

        st.subheader("Moderation Decision")

        severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green", "none": "blue"}
        action_color = {"remove": "red", "hide": "orange", "warn": "yellow", "flag": "blue", "escalate": "purple", "approve": "green", "shadowban": "gray"}

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"Violation: **{result['violation_type'].replace('_', ' ').title()}**")
        with col2:
            st.markdown(f"Severity: :{severity_color.get(result['severity'], 'gray')}[{result['severity'].upper()}]")
        with col3:
            st.markdown(f"Action: :{action_color.get(result['action'], 'gray')}[{result['action'].upper()}]")

        st.metric("Confidence", f"{result['confidence']:.0%}")
        st.write(result["explanation"])

        if result["policy_references"]:
            st.caption(f"Policies: {', '.join(result['policy_references'])}")

        if result["human_review_required"]:
            st.warning("Human review required")

        if result["appeal_eligible"]:
            st.info("This decision can be appealed")

with tab2:
    appeal_id = st.text_input("Appeal ID", placeholder="appeal-67890")
    original_violation = st.selectbox("Original Violation", [v.value for v in ViolationType])
    original_severity = st.selectbox("Original Severity", [s.value for s in Severity])
    original_action = st.selectbox("Original Action", [a.value for a in Action])
    original_explanation = st.text_area("Original Explanation", placeholder="The original moderation explanation...")
    appeal_reason = st.text_area("Appeal Reason", placeholder="Why do you believe this decision was incorrect?")

    if api_key and appeal_id and appeal_reason and original_explanation:
        original_decision = {
            "content_id": "content-123",
            "violation_type": original_violation,
            "severity": original_severity,
            "action": original_action,
            "confidence": 0.8,
            "explanation": original_explanation,
            "policy_references": ["Policy 3.2"],
            "human_review_required": True,
            "appeal_eligible": True,
            "timestamp": datetime.now().isoformat()
        }

        moderator = ContentModerationAgent(api_key)
        result = moderator.handle_request(
            content_id="content-123",
            content_text="",
            appeal_id=appeal_id,
            appeal_reason=appeal_reason,
            original_decision=original_decision
        )

        st.subheader("Appeal Review")

        if result["overturned"]:
            st.success("Appeal approved — decision overturned")
            if result["new_decision"]:
                st.write(f"New action: {result['new_decision']['action']}")
                st.write(f"New explanation: {result['new_decision']['explanation']}")
        else:
            st.error("Appeal denied — original decision upheld")

        st.write(f"**Reviewer notes:** {result['reviewer_notes']}")
