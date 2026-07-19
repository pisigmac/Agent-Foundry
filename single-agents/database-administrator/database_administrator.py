"""
Database Administrator Agent

An autonomous agent for SQL optimization, schema analysis, query tuning,
index recommendations, and database health monitoring.
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


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QueryAnalysis:
    query: str
    estimated_cost: int
    index_suggestions: List[str]
    optimization_tips: List[str]
    severity: Severity
    execution_time_ms: Optional[int] = None


@dataclass
class SchemaIssue:
    table: str
    column: str
    issue_type: str
    description: str
    recommendation: str
    severity: Severity


class DatabaseAdministrator:
    """
    Primary entry point for database administration and query optimization.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Database administration, SQL optimization, and schema analysis",
            instructions=[
                "Analyze SQL queries for performance bottlenecks and optimization opportunities",
                "Review database schemas for normalization issues and missing indexes",
                "Suggest query rewrites and index strategies",
                "Identify security risks in query patterns and schema design"
            ]
        )

    def analyze_query(self, query: str, dialect: str = "postgresql") -> QueryAnalysis:
        """
        Analyze a SQL query for performance and optimization.
        """
        prompt = f"""
        Analyze this {dialect} SQL query for performance optimization:

        ```sql
        {query}
        ```

        Provide:
        1. Estimated cost (1-1000 scale)
        2. Index suggestions (specific column combinations)
        3. Query rewrite suggestions
        4. Potential bottlenecks
        5. Severity: critical/high/medium/low/info

        Respond in JSON format:
        {{
            "estimated_cost": <number>,
            "index_suggestions": ["<suggestion1>", "<suggestion2>"],
            "optimization_tips": ["<tip1>", "<tip2>"],
            "severity": "<severity>",
            "execution_time_ms": <number or null>
        }}
        """

        response = self.assistant.run(prompt)
        content = response.content

        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            return QueryAnalysis(
                query=query,
                estimated_cost=data.get("estimated_cost", 500),
                index_suggestions=data.get("index_suggestions", []),
                optimization_tips=data.get("optimization_tips", []),
                severity=Severity(data.get("severity", "medium")),
                execution_time_ms=data.get("execution_time_ms")
            )
        except (json.JSONDecodeError, ValueError):
            return QueryAnalysis(
                query=query,
                estimated_cost=500,
                index_suggestions=["Consider adding an index on frequently filtered columns"],
                optimization_tips=["Review query execution plan"],
                severity=Severity.MEDIUM
            )

    def analyze_schema(self, schema_text: str) -> List[SchemaIssue]:
        """
        Analyze a database schema for issues and improvements.
        """
        prompt = f"""
        Analyze this database schema for issues:

        ```sql
        {schema_text}
        ```

        Identify:
        1. Missing primary keys or foreign keys
        2. Columns without appropriate indexes
        3. Normalization issues (1NF, 2NF, 3NF violations)
        4. Data type mismatches or inefficiencies
        5. Security concerns (sensitive data without encryption)

        Respond in JSON format:
        [
            {{
                "table": "<table_name>",
                "column": "<column_name>",
                "issue_type": "<type>",
                "description": "<description>",
                "recommendation": "<recommendation>",
                "severity": "<severity>"
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
                issues.append(SchemaIssue(
                    table=item.get("table", "unknown"),
                    column=item.get("column", "unknown"),
                    issue_type=item.get("issue_type", "general"),
                    description=item.get("description", ""),
                    recommendation=item.get("recommendation", ""),
                    severity=Severity(item.get("severity", "medium"))
                ))
        except (json.JSONDecodeError, ValueError):
            issues.append(SchemaIssue(
                table="unknown",
                column="unknown",
                issue_type="parse_error",
                description="Could not parse schema analysis",
                recommendation="Please provide a clearer schema definition",
                severity=Severity.LOW
            ))

        return issues

    def handle_request(self, query: str, schema_text: Optional[str] = None, dialect: str = "postgresql") -> Dict:
        """
        Process a database administration request.
        """
        results = {
            "query": query,
            "dialect": dialect,
            "query_analysis": None,
            "schema_issues": []
        }

        # Analyze query if it looks like SQL
        if any(keyword in query.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER"]):
            results["query_analysis"] = self.analyze_query(query, dialect)

        # Analyze schema if provided
        if schema_text:
            results["schema_issues"] = self.analyze_schema(schema_text)

        return results


# Streamlit interface
st.title("Database Administrator")
st.caption("SQL optimization, schema analysis, query tuning, and index recommendations")

api_key = st.text_input("OpenAI API Key", type="password")

dialect = st.selectbox(
    "Database Dialect",
    ["postgresql", "mysql", "sqlite", "mssql", "oracle"]
)

query = st.text_area("SQL Query or Question", 
    placeholder="Paste a SQL query to analyze, or ask a database administration question...",
    height=150)

schema_text = st.text_area("Schema Definition (Optional)", 
    placeholder="Paste CREATE TABLE statements to analyze schema issues...",
    height=200)

if api_key and query:
    dba = DatabaseAdministrator(api_key)
    result = dba.handle_request(query, schema_text if schema_text else None, dialect)

    if result["query_analysis"]:
        analysis = result["query_analysis"]

        st.subheader("Query Analysis")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimated Cost", analysis.estimated_cost)
        with col2:
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green", "info": "blue"}
            st.markdown(f"Severity: :{severity_color.get(analysis.severity.value, 'gray')}[{analysis.severity.value.upper()}]")
        with col3:
            if analysis.execution_time_ms:
                st.metric("Est. Time", f"{analysis.execution_time_ms}ms")

        if analysis.index_suggestions:
            st.subheader("Index Suggestions")
            for suggestion in analysis.index_suggestions:
                st.markdown(f"- {suggestion}")

        if analysis.optimization_tips:
            st.subheader("Optimization Tips")
            for tip in analysis.optimization_tips:
                st.markdown(f"- {tip}")

    if result["schema_issues"]:
        st.subheader(f"Schema Issues ({len(result['schema_issues'])})")

        for issue in result["schema_issues"]:
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green", "info": "blue"}
            with st.container():
                st.markdown(f"**{issue.table}.{issue.column}** — :{severity_color.get(issue.severity.value, 'gray')}[{issue.severity.value.upper()}]")
                st.caption(f"Type: {issue.issue_type}")
                st.write(issue.description)
                st.info(f"Recommendation: {issue.recommendation}")
                st.divider()
