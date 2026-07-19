"""
Data Quality Validator

An autonomous agent that profiles datasets, validates schemas, detects
anomalies, measures completeness, and scores overall data quality.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import streamlit as st
from agno.assistant import Assistant
from agno.models.openai import OpenAIChat
import pandas as pd
import numpy as np


class QualityDimension(Enum):
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class QualityIssue:
    column: str
    dimension: QualityDimension
    description: str
    affected_rows: int
    severity: Severity
    recommendation: str
    example_values: List[str]


@dataclass
class ColumnProfile:
    name: str
    data_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    min_value: Optional[Any]
    max_value: Optional[Any]
    mean_value: Optional[float]
    std_value: Optional[float]
    sample_values: List[Any]


class DataQualityValidator:
    """
    Primary entry point for data profiling, quality validation, and anomaly detection.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Data quality profiling, schema validation, anomaly detection, and quality scoring",
            instructions=[
                "Profile datasets for completeness, accuracy, consistency, validity, uniqueness, and timeliness",
                "Detect schema violations, data type mismatches, and format inconsistencies",
                "Identify outliers, duplicates, and missing value patterns",
                "Provide specific recommendations for data cleaning and enrichment"
            ]
        )

    def profile_column(self, series: pd.Series) -> ColumnProfile:
        """
        Generate a statistical profile for a single column.
        """
        null_count = series.isnull().sum()
        total_count = len(series)

        profile = ColumnProfile(
            name=series.name,
            data_type=str(series.dtype),
            null_count=int(null_count),
            null_percentage=round(null_count / total_count * 100, 2) if total_count > 0 else 0,
            unique_count=series.nunique(),
            unique_percentage=round(series.nunique() / total_count * 100, 2) if total_count > 0 else 0,
            min_value=series.min() if pd.api.types.is_numeric_dtype(series) else None,
            max_value=series.max() if pd.api.types.is_numeric_dtype(series) else None,
            mean_value=round(series.mean(), 2) if pd.api.types.is_numeric_dtype(series) else None,
            std_value=round(series.std(), 2) if pd.api.types.is_numeric_dtype(series) else None,
            sample_values=series.dropna().head(5).tolist()
        )

        return profile

    def detect_issues(self, df: pd.DataFrame) -> List[QualityIssue]:
        """
        Detect data quality issues in a DataFrame.
        """
        issues = []

        for col in df.columns:
            series = df[col]
            null_count = series.isnull().sum()
            total_count = len(series)

            # Completeness check
            if null_count > 0:
                null_pct = null_count / total_count
                severity = Severity.CRITICAL if null_pct > 0.5 else Severity.HIGH if null_pct > 0.2 else Severity.MEDIUM if null_pct > 0.05 else Severity.LOW
                issues.append(QualityIssue(
                    column=col,
                    dimension=QualityDimension.COMPLETENESS,
                    description=f"{null_count} null values ({null_pct:.1%} of column)",
                    affected_rows=int(null_count),
                    severity=severity,
                    recommendation="Impute missing values or investigate data collection process",
                    example_values=[str(v) for v in series[series.isnull()].index[:3].tolist()]
                ))

            # Uniqueness check for potential ID columns
            if col.lower() in ['id', 'uuid', 'key', 'identifier', 'code']:
                dup_count = series.duplicated().sum()
                if dup_count > 0:
                    issues.append(QualityIssue(
                        column=col,
                        dimension=QualityDimension.UNIQUENESS,
                        description=f"{dup_count} duplicate values in potential identifier column",
                        affected_rows=int(dup_count),
                        severity=Severity.HIGH,
                        recommendation="Remove duplicates or redesign identifier strategy",
                        example_values=[str(v) for v in series[series.duplicated()].head(3).tolist()]
                    ))

            # Consistency check for categorical columns
            if series.dtype == 'object':
                # Check for mixed case inconsistencies
                if series.dropna().astype(str).str.islower().any() and series.dropna().astype(str).str.isupper().any():
                    issues.append(QualityIssue(
                        column=col,
                        dimension=QualityDimension.CONSISTENCY,
                        description="Mixed case values detected (e.g., 'USA' and 'usa')",
                        affected_rows=int(series.dropna().astype(str).str.islower().sum()),
                        severity=Severity.MEDIUM,
                        recommendation="Standardize to consistent case (lower or upper)",
                        example_values=series.dropna().unique()[:3].tolist()
                    ))

            # Validity check for numeric columns
            if pd.api.types.is_numeric_dtype(series):
                # Check for negative values in columns that should be positive
                if col.lower() in ['age', 'price', 'quantity', 'count', 'amount', 'salary']:
                    neg_count = (series < 0).sum()
                    if neg_count > 0:
                        issues.append(QualityIssue(
                            column=col,
                            dimension=QualityDimension.VALIDITY,
                            description=f"{neg_count} negative values in column that should be non-negative",
                            affected_rows=int(neg_count),
                            severity=Severity.HIGH,
                            recommendation="Investigate negative values or apply data validation rules",
                            example_values=[str(v) for v in series[series < 0].head(3).tolist()]
                        ))

        return issues

    def llm_analysis(self, df: pd.DataFrame, profiles: List[ColumnProfile]) -> List[QualityIssue]:
        """
        Use LLM for advanced quality analysis.
        """
        # Create summary for LLM
        summary = {
            "shape": df.shape,
            "columns": [{
                "name": p.name,
                "type": p.data_type,
                "null_pct": p.null_percentage,
                "unique_pct": p.unique_percentage,
                "sample": [str(v) for v in p.sample_values[:3]]
            } for p in profiles]
        }

        prompt = f"""
        Analyze this dataset for data quality issues:

        Dataset Summary:
        {json.dumps(summary, indent=2)}

        Sample data (first 5 rows):
        {df.head().to_json(orient='records', indent=2)}

        Identify:
        1. Schema design issues (wrong data types, missing constraints)
        2. Data distribution anomalies (outliers, skewed distributions)
        3. Relationship issues (orphaned records, referential integrity)
        4. Business rule violations
        5. Temporal issues (future dates, invalid date ranges)

        For each issue, provide:
        - Column name
        - Dimension: completeness, accuracy, consistency, validity, uniqueness, timeliness
        - Description
        - Severity: critical/high/medium/low
        - Recommendation
        - Example values

        Respond in JSON format matching the QualityIssue structure.
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
                issues.append(QualityIssue(
                    column=item.get("column", "unknown"),
                    dimension=QualityDimension(item.get("dimension", "completeness")),
                    description=item.get("description", ""),
                    affected_rows=item.get("affected_rows", 0),
                    severity=Severity(item.get("severity", "medium")),
                    recommendation=item.get("recommendation", ""),
                    example_values=item.get("example_values", [])
                ))
        except (json.JSONDecodeError, ValueError):
            pass

        return issues

    def calculate_quality_score(self, issues: List[QualityIssue], total_rows: int) -> Dict:
        """
        Calculate overall data quality score.
        """
        dimension_scores = {d.value: 100.0 for d in QualityDimension}

        for issue in issues:
            penalty = {
                Severity.CRITICAL: 20,
                Severity.HIGH: 10,
                Severity.MEDIUM: 5,
                Severity.LOW: 2
            }.get(issue.severity, 0)

            dimension_scores[issue.dimension.value] -= penalty

        dimension_scores = {k: max(0, v) for k, v in dimension_scores.items()}
        overall = sum(dimension_scores.values()) / len(dimension_scores)

        return {
            "overall_score": round(overall, 1),
            "dimension_scores": {k: round(v, 1) for k, v in dimension_scores.items()},
            "total_issues": len(issues),
            "critical_issues": sum(1 for i in issues if i.severity == Severity.CRITICAL),
            "high_issues": sum(1 for i in issues if i.severity == Severity.HIGH)
        }

    def handle_request(self, df: pd.DataFrame) -> Dict:
        """
        Process a dataset and return quality analysis results.
        """
        # Profile all columns
        profiles = [self.profile_column(df[col]) for col in df.columns]

        # Detect issues
        heuristic_issues = self.detect_issues(df)
        llm_issues = self.llm_analysis(df, profiles)

        all_issues = heuristic_issues + llm_issues

        # Calculate score
        score = self.calculate_quality_score(all_issues, len(df))

        return {
            "dataset_shape": df.shape,
            "profiles": [{
                "name": p.name,
                "type": p.data_type,
                "null_pct": p.null_percentage,
                "unique_pct": p.unique_percentage,
                "min": p.min_value,
                "max": p.max_value,
                "mean": p.mean_value,
                "std": p.std_value,
                "samples": [str(v) for v in p.sample_values]
            } for p in profiles],
            "quality_score": score,
            "issues": [{
                "column": i.column,
                "dimension": i.dimension.value,
                "description": i.description,
                "affected_rows": i.affected_rows,
                "severity": i.severity.value,
                "recommendation": i.recommendation,
                "examples": i.example_values
            } for i in all_issues]
        }


# Streamlit interface
st.title("Data Quality Validator")
st.caption("Profile datasets, validate schemas, detect anomalies, and score overall data quality")

api_key = st.text_input("OpenAI API Key", type="password")

uploaded_file = st.file_uploader("Upload Dataset (CSV, Excel, JSON)", type=["csv", "xlsx", "json"])

if api_key and uploaded_file:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.json'):
        df = pd.read_json(uploaded_file)

    st.subheader(f"Dataset: {df.shape[0]} rows × {df.shape[1]} columns")

    validator = DataQualityValidator(api_key)
    result = validator.handle_request(df)

    # Quality Score
    score = result["quality_score"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{score['overall_score']}/100")
    with col2:
        st.metric("Total Issues", score['total_issues'])
    with col3:
        st.metric("Critical", score['critical_issues'], delta_color="inverse")
    with col4:
        st.metric("High", score['high_issues'], delta_color="inverse")

    # Dimension scores
    st.subheader("Quality Dimensions")
    dim_data = []
    for dim, val in score['dimension_scores'].items():
        dim_data.append({"Dimension": dim.title(), "Score": val})

    st.bar_chart(pd.DataFrame(dim_data).set_index("Dimension"))

    # Column profiles
    st.subheader("Column Profiles")
    profile_df = pd.DataFrame(result["profiles"])
    st.dataframe(profile_df, use_container_width=True)

    # Issues
    if result["issues"]:
        st.subheader(f"Issues ({len(result['issues'])})")

        for issue in result["issues"]:
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green"}

            with st.container():
                st.markdown(f"**{issue['column']}** — {issue['dimension'].title()}")
                st.caption(f":{severity_color.get(issue['severity'], 'gray')}[{issue['severity'].upper()}] | {issue['affected_rows']} affected rows")
                st.write(issue['description'])
                st.info(f"**Fix:** {issue['recommendation']}")

                if issue['examples']:
                    st.caption(f"Examples: {', '.join(str(e) for e in issue['examples'][:3])}")

                st.divider()
    else:
        st.success("No data quality issues detected!")
