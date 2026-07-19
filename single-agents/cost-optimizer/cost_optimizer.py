"""
Cost Optimizer

An autonomous agent that analyzes cloud resource usage, identifies
waste, recommends right-sizing, and projects savings from optimization.
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


class ResourceType(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    CDN = "cdn"


class OptimizationType(Enum):
    RIGHT_SIZE = "right_size"
    SHUTDOWN = "shutdown"
    RESERVE = "reserve"
    SPOT = "spot"
    TIER = "tier"
    ARCHIVE = "archive"
    COMPRESS = "compress"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class OptimizationOpportunity:
    resource_id: str
    resource_type: ResourceType
    current_cost_monthly: float
    recommended_cost_monthly: float
    savings_monthly: float
    savings_percentage: float
    optimization_type: OptimizationType
    description: str
    severity: Severity
    implementation_effort: str  # low/medium/high
    risk_level: str  # low/medium/high


@dataclass
class ResourceUsage:
    resource_id: str
    resource_type: ResourceType
    region: str
    current_spend: float
    utilization_percentage: float
    uptime_hours: float
    tags: Dict[str, str]


class CostOptimizer:
    """
    Primary entry point for cloud cost analysis and optimization recommendations.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Cloud cost optimization, resource right-sizing, and waste identification",
            instructions=[
                "Analyze cloud resource usage and identify optimization opportunities",
                "Recommend right-sizing, reserved instances, spot instances, and tier changes",
                "Calculate monthly and annual savings with implementation effort estimates",
                "Assess risk levels for each optimization recommendation"
            ]
        )

    def parse_billing_data(self, billing_text: str) -> List[ResourceUsage]:
        """
        Parse billing data from CSV/text format.
        """
        resources = []

        # Try to parse as CSV-like data
        lines = billing_text.strip().split("\n")

        if len(lines) > 1:
            # Check if first line is header
            header = lines[0].lower()
            if any(keyword in header for keyword in ['resource', 'service', 'cost', 'usage']):
                # Parse as CSV
                for line in lines[1:]:
                    parts = line.split(",")
                    if len(parts) >= 3:
                        resource_id = parts[0].strip()
                        service_type = parts[1].strip().lower()
                        cost_str = parts[2].strip().replace("$", "").replace(",", "")

                        try:
                            cost = float(cost_str)
                        except ValueError:
                            cost = 0.0

                        # Map service type to ResourceType
                        resource_type = ResourceType.COMPUTE
                        if any(k in service_type for k in ['storage', 'blob', 's3', 'disk']):
                            resource_type = ResourceType.STORAGE
                        elif any(k in service_type for k in ['network', 'transfer', 'bandwidth', 'data']):
                            resource_type = ResourceType.NETWORK
                        elif any(k in service_type for k in ['database', 'db', 'sql', 'postgres', 'mysql']):
                            resource_type = ResourceType.DATABASE
                        elif any(k in service_type for k in ['container', 'kubernetes', 'k8s', 'ecs']):
                            resource_type = ResourceType.CONTAINER
                        elif any(k in service_type for k in ['lambda', 'function', 'serverless']):
                            resource_type = ResourceType.SERVERLESS
                        elif any(k in service_type for k in ['cdn', 'cloudfront', 'edge']):
                            resource_type = ResourceType.CDN

                        region = parts[3].strip() if len(parts) > 3 else "us-east-1"
                        utilization = float(parts[4].strip().replace("%", "")) if len(parts) > 4 else 50.0
                        uptime = float(parts[5].strip()) if len(parts) > 5 else 720.0

                        resources.append(ResourceUsage(
                            resource_id=resource_id,
                            resource_type=resource_type,
                            region=region,
                            current_spend=cost,
                            utilization_percentage=utilization,
                            uptime_hours=uptime,
                            tags={}
                        ))

        return resources

    def analyze_optimization(self, resource: ResourceUsage) -> List[OptimizationOpportunity]:
        """
        Analyze a single resource for optimization opportunities.
        """
        opportunities = []

        # Low utilization compute
        if resource.resource_type == ResourceType.COMPUTE and resource.utilization_percentage < 20:
            savings = resource.current_spend * 0.6
            opportunities.append(OptimizationOpportunity(
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                current_cost_monthly=resource.current_spend,
                recommended_cost_monthly=resource.current_spend - savings,
                savings_monthly=savings,
                savings_percentage=60.0,
                optimization_type=OptimizationType.RIGHT_SIZE,
                description=f"Utilization is only {resource.utilization_percentage:.1f}%. Consider downsizing or using burstable instances.",
                severity=Severity.HIGH,
                implementation_effort="low",
                risk_level="low"
            ))

        # High uptime without reservations
        if resource.uptime_hours > 600 and resource.current_spend > 100:
            savings = resource.current_spend * 0.3
            opportunities.append(OptimizationOpportunity(
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                current_cost_monthly=resource.current_spend,
                recommended_cost_monthly=resource.current_spend - savings,
                savings_monthly=savings,
                savings_percentage=30.0,
                optimization_type=OptimizationType.RESERVE,
                description=f"Running {resource.uptime_hours:.0f} hours/month. Reserved instances could save 30%.",
                severity=Severity.MEDIUM,
                implementation_effort="low",
                risk_level="low"
            ))

        # Spot instances for fault-tolerant workloads
        if resource.resource_type == ResourceType.COMPUTE and resource.utilization_percentage > 10:
            savings = resource.current_spend * 0.7
            opportunities.append(OptimizationOpportunity(
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                current_cost_monthly=resource.current_spend,
                recommended_cost_monthly=resource.current_spend - savings,
                savings_monthly=savings,
                savings_percentage=70.0,
                optimization_type=OptimizationType.SPOT,
                description="Consider spot instances for fault-tolerant workloads. Up to 70% savings.",
                severity=Severity.MEDIUM,
                implementation_effort="medium",
                risk_level="medium"
            ))

        # Storage tier optimization
        if resource.resource_type == ResourceType.STORAGE and resource.current_spend > 50:
            savings = resource.current_spend * 0.4
            opportunities.append(OptimizationOpportunity(
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                current_cost_monthly=resource.current_spend,
                recommended_cost_monthly=resource.current_spend - savings,
                savings_monthly=savings,
                savings_percentage=40.0,
                optimization_type=OptimizationType.TIER,
                description="Move infrequently accessed data to cold/archive storage tiers.",
                severity=Severity.MEDIUM,
                implementation_effort="low",
                risk_level="low"
            ))

        # Idle resources
        if resource.utilization_percentage < 5 and resource.uptime_hours > 100:
            savings = resource.current_spend * 0.9
            opportunities.append(OptimizationOpportunity(
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                current_cost_monthly=resource.current_spend,
                recommended_cost_monthly=resource.current_spend - savings,
                savings_monthly=savings,
                savings_percentage=90.0,
                optimization_type=OptimizationType.SHUTDOWN,
                description=f"Resource is essentially idle ({resource.utilization_percentage:.1f}% utilization). Consider shutting down or deleting.",
                severity=Severity.CRITICAL,
                implementation_effort="low",
                risk_level="low"
            ))

        return opportunities

    def llm_analysis(self, resources: List[ResourceUsage]) -> List[OptimizationOpportunity]:
        """
        Use LLM for advanced cost analysis.
        """
        resource_summary = []
        for r in resources:
            resource_summary.append({
                "id": r.resource_id,
                "type": r.resource_type.value,
                "region": r.region,
                "spend": r.current_spend,
                "utilization": r.utilization_percentage,
                "uptime": r.uptime_hours
            })

        prompt = f"""
        Analyze these cloud resources for cost optimization opportunities:

        {json.dumps(resource_summary, indent=2)}

        Identify:
        1. Resources that should be right-sized
        2. Candidates for reserved instances or savings plans
        3. Spot instance opportunities
        4. Storage tier optimization
        5. Idle or orphaned resources
        6. Network transfer optimization
        7. Database scaling opportunities

        For each opportunity, provide:
        - Resource ID
        - Optimization type: right_size, shutdown, reserve, spot, tier, archive, compress
        - Current monthly cost
        - Recommended monthly cost
        - Monthly savings
        - Savings percentage
        - Description
        - Severity: critical/high/medium/low
        - Implementation effort: low/medium/high
        - Risk level: low/medium/high

        Respond in JSON format:
        [
            {{
                "resource_id": "<id>",
                "resource_type": "<type>",
                "current_cost_monthly": <number>,
                "recommended_cost_monthly": <number>,
                "savings_monthly": <number>,
                "savings_percentage": <number>,
                "optimization_type": "<type>",
                "description": "<description>",
                "severity": "<severity>",
                "implementation_effort": "<effort>",
                "risk_level": "<risk>"
            }}
        ]
        """

        response = self.assistant.run(prompt)
        content = response.content

        opportunities = []
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            for item in data:
                opportunities.append(OptimizationOpportunity(
                    resource_id=item.get("resource_id", "unknown"),
                    resource_type=ResourceType(item.get("resource_type", "compute")),
                    current_cost_monthly=item.get("current_cost_monthly", 0.0),
                    recommended_cost_monthly=item.get("recommended_cost_monthly", 0.0),
                    savings_monthly=item.get("savings_monthly", 0.0),
                    savings_percentage=item.get("savings_percentage", 0.0),
                    optimization_type=OptimizationType(item.get("optimization_type", "right_size")),
                    description=item.get("description", ""),
                    severity=Severity(item.get("severity", "medium")),
                    implementation_effort=item.get("implementation_effort", "medium"),
                    risk_level=item.get("risk_level", "medium")
                ))
        except (json.JSONDecodeError, ValueError):
            pass

        return opportunities

    def handle_request(self, billing_data: str) -> Dict:
        """
        Process billing data and return optimization recommendations.
        """
        resources = self.parse_billing_data(billing_data)

        # Heuristic analysis
        heuristic_opportunities = []
        for resource in resources:
            heuristic_opportunities.extend(self.analyze_optimization(resource))

        # LLM analysis
        llm_opportunities = self.llm_analysis(resources)

        all_opportunities = heuristic_opportunities + llm_opportunities

        # Calculate totals
        total_current = sum(r.current_spend for r in resources)
        total_savings = sum(o.savings_monthly for o in all_opportunities)

        return {
            "resources_analyzed": len(resources),
            "total_monthly_spend": total_current,
            "total_monthly_savings": total_savings,
            "savings_percentage": (total_savings / total_current * 100) if total_current > 0 else 0,
            "annual_savings_projection": total_savings * 12,
            "opportunities": [{
                "resource_id": o.resource_id,
                "type": o.resource_type.value,
                "current_cost": o.current_cost_monthly,
                "recommended_cost": o.recommended_cost_monthly,
                "savings": o.savings_monthly,
                "savings_pct": o.savings_percentage,
                "optimization": o.optimization_type.value,
                "description": o.description,
                "severity": o.severity.value,
                "effort": o.implementation_effort,
                "risk": o.risk_level
            } for o in all_opportunities],
            "by_type": {}
        }


# Streamlit interface
st.title("Cost Optimizer")
st.caption("Analyze cloud resource usage, identify waste, recommend right-sizing, and project savings")

api_key = st.text_input("OpenAI API Key", type="password")

st.markdown("""
**Expected CSV format:**
```
resource_id,service_type,monthly_cost,region,utilization_pct,uptime_hours
i-12345678,EC2,450.00,us-east-1,15.5,720
s3-bucket-1,S3,120.50,us-west-2,0,720
```
""")

billing_data = st.text_area("Billing Data", 
    placeholder="Paste CSV billing data here...",
    height=300)

if api_key and billing_data:
    optimizer = CostOptimizer(api_key)
    result = optimizer.handle_request(billing_data)

    st.subheader("Optimization Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Resources", result["resources_analyzed"])
    with col2:
        st.metric("Monthly Spend", f"${result['total_monthly_spend']:,.2f}")
    with col3:
        st.metric("Monthly Savings", f"${result['total_monthly_savings']:,.2f}", delta_color="inverse")
    with col4:
        st.metric("Annual Savings", f"${result['annual_savings_projection']:,.2f}", delta_color="inverse")

    if result["opportunities"]:
        st.subheader(f"Optimization Opportunities ({len(result['opportunities'])})")

        # Group by severity
        critical = [o for o in result["opportunities"] if o["severity"] == "critical"]
        high = [o for o in result["opportunities"] if o["severity"] == "high"]

        if critical:
            st.error(f"Critical: {len(critical)} opportunities")
        if high:
            st.warning(f"High: {len(high)} opportunities")

        for opp in sorted(result["opportunities"], key=lambda x: x["savings"], reverse=True):
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green"}

            with st.container():
                st.markdown(f"**{opp['resource_id']}** — {opp['optimization'].replace('_', ' ').title()}")
                st.caption(f":{severity_color.get(opp['severity'], 'gray')}[{opp['severity'].upper()}] | Effort: {opp['effort']} | Risk: {opp['risk']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current", f"${opp['current_cost']:,.2f}")
                with col2:
                    st.metric("Recommended", f"${opp['recommended_cost']:,.2f}")
                with col3:
                    st.metric("Savings", f"${opp['savings']:,.2f} ({opp['savings_pct']:.0f}%)", delta_color="inverse")

                st.write(opp['description'])
                st.divider()
    else:
        st.success("No optimization opportunities found. Your infrastructure is well-optimized!")
