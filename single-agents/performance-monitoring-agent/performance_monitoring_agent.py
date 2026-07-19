"""
Performance Monitoring Agent

An autonomous agent that monitors application performance metrics, detects
anomalies, identifies bottlenecks, and generates optimization recommendations.
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
import pandas as pd
import numpy as np


class MetricType(Enum):
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    DATABASE = "database"
    CACHE_HIT = "cache_hit"
    QUEUE_DEPTH = "queue_depth"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BottleneckType(Enum):
    CPU_BOUND = "cpu_bound"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    NETWORK_BOUND = "network_bound"
    DATABASE_BOUND = "database_bound"
    CACHE_MISS = "cache_miss"
    LOCK_CONTENTION = "lock_contention"
    GC_PRESSURE = "gc_pressure"
    THREAD_STARVATION = "thread_starvation"
    UNKNOWN = "unknown"


@dataclass
class PerformanceMetric:
    metric_type: MetricType
    value: float
    unit: str
    timestamp: str
    service: str
    percentile: Optional[float] = None
    baseline: Optional[float] = None
    threshold: Optional[float] = None


@dataclass
class AnomalyDetection:
    metric: PerformanceMetric
    deviation_from_baseline: float
    severity: Severity
    duration_minutes: int
    affected_endpoints: List[str]
    root_cause_indicators: List[str]


@dataclass
class BottleneckAnalysis:
    bottleneck_type: BottleneckType
    confidence: float
    affected_services: List[str]
    contributing_factors: List[str]
    recommendations: List[str]
    estimated_impact: str


class PerformanceMonitoringAgent:
    """
    Primary entry point for performance metric analysis, anomaly detection, and bottleneck identification.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Performance monitoring, anomaly detection, bottleneck analysis, and optimization recommendations",
            instructions=[
                "Analyze performance metrics across latency, throughput, error rates, CPU, memory, and database",
                "Detect anomalies using baseline deviation and statistical thresholds",
                "Identify system bottlenecks with confidence scoring and impact estimation",
                "Generate specific optimization recommendations with expected improvements"
            ]
        )
        self.baselines: Dict[str, float] = {}
        self.thresholds: Dict[str, float] = {
            "latency_p95": 500,      # ms
            "latency_p99": 1000,   # ms
            "error_rate": 1.0,      # %
            "cpu_usage": 80.0,      # %
            "memory_usage": 85.0,   # %
            "cache_hit_rate": 90.0, # %
        }

    def parse_metrics(self, metrics_text: str) -> List[PerformanceMetric]:
        """
        Parse performance metrics from text or CSV format.
        """
        metrics = []

        lines = metrics_text.strip().split("\n")

        # Check if CSV format
        if lines and any("," in line for line in lines[:3]):
            # Parse CSV
            headers = lines[0].split(",")
            for line in lines[1:]:
                parts = line.split(",")
                if len(parts) >= 3:
                    metric_type_str = parts[0].strip().lower()
                    value_str = parts[1].strip()
                    service = parts[2].strip() if len(parts) > 2 else "unknown"

                    try:
                        value = float(value_str)
                    except ValueError:
                        continue

                    # Map to MetricType
                    metric_type = MetricType.LATENCY
                    for mt in MetricType:
                        if mt.value in metric_type_str:
                            metric_type = mt
                            break

                    unit = "ms" if metric_type == MetricType.LATENCY else "%" if metric_type in [MetricType.CPU, MetricType.MEMORY, MetricType.ERROR_RATE, MetricType.CACHE_HIT] else "req/s"

                    metrics.append(PerformanceMetric(
                        metric_type=metric_type,
                        value=value,
                        unit=unit,
                        timestamp=datetime.now().isoformat(),
                        service=service,
                        percentile=95.0 if "p95" in metric_type_str else 99.0 if "p99" in metric_type_str else None
                    ))
        else:
            # Parse free text
            metric_patterns = {
                MetricType.LATENCY: r"(?:latency|response time)[^\d]*(\d+(?:\.\d+)?)\s*(?:ms|milliseconds?)",
                MetricType.THROUGHPUT: r"(?:throughput|rps|requests?)[^\d]*(\d+(?:\.\d+)?)\s*(?:req/s|rps|requests?)",
                MetricType.ERROR_RATE: r"(?:error rate|errors?)[^\d]*(\d+(?:\.\d+)?)\s*%",
                MetricType.CPU: r"(?:cpu|processor)[^\d]*(\d+(?:\.\d+)?)\s*%",
                MetricType.MEMORY: r"(?:memory|ram)[^\d]*(\d+(?:\.\d+)?)\s*%",
                MetricType.CACHE_HIT: r"(?:cache hit|hit rate)[^\d]*(\d+(?:\.\d+)?)\s*%",
            }

            for metric_type, pattern in metric_patterns.items():
                matches = re.finditer(pattern, metrics_text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        metrics.append(PerformanceMetric(
                            metric_type=metric_type,
                            value=value,
                            unit="ms" if metric_type == MetricType.LATENCY else "%" if metric_type in [MetricType.CPU, MetricType.MEMORY, MetricType.ERROR_RATE, MetricType.CACHE_HIT] else "req/s",
                            timestamp=datetime.now().isoformat(),
                            service="unknown"
                        ))
                    except ValueError:
                        continue

        return metrics

    def detect_anomalies(self, metrics: List[PerformanceMetric]) -> List[AnomalyDetection]:
        """
        Detect anomalies in performance metrics.
        """
        anomalies = []

        for metric in metrics:
            threshold = self.thresholds.get(metric.metric_type.value, None)
            baseline = self.baselines.get(metric.metric_type.value, None)

            if threshold and metric.value > threshold:
                deviation = (metric.value - threshold) / threshold * 100

                severity = Severity.LOW
                if deviation > 100:
                    severity = Severity.CRITICAL
                elif deviation > 50:
                    severity = Severity.HIGH
                elif deviation > 20:
                    severity = Severity.MEDIUM

                anomalies.append(AnomalyDetection(
                    metric=metric,
                    deviation_from_baseline=deviation,
                    severity=severity,
                    duration_minutes=5,  # Assume 5 min window
                    affected_endpoints=[metric.service],
                    root_cause_indicators=[f"{metric.metric_type.value} exceeded threshold by {deviation:.1f}%"]
                ))

            elif baseline and abs(metric.value - baseline) / baseline > 0.3:
                deviation = abs(metric.value - baseline) / baseline * 100

                severity = Severity.LOW
                if deviation > 100:
                    severity = Severity.CRITICAL
                elif deviation > 50:
                    severity = Severity.HIGH
                elif deviation > 30:
                    severity = Severity.MEDIUM

                anomalies.append(AnomalyDetection(
                    metric=metric,
                    deviation_from_baseline=deviation,
                    severity=severity,
                    duration_minutes=5,
                    affected_endpoints=[metric.service],
                    root_cause_indicators=[f"{metric.metric_type.value} deviated {deviation:.1f}% from baseline"]
                ))

        return anomalies

    def analyze_bottlenecks(self, metrics: List[PerformanceMetric], anomalies: List[AnomalyDetection]) -> List[BottleneckAnalysis]:
        """
        Analyze system bottlenecks based on metrics and anomalies.
        """
        # Group metrics by type
        metric_by_type = {}
        for m in metrics:
            if m.metric_type not in metric_by_type:
                metric_by_type[m.metric_type] = []
            metric_by_type[m.metric_type].append(m)

        # Build context for LLM
        context = "Performance Metrics Summary:\n"
        for mt, ms in metric_by_type.items():
            avg_val = sum(m.value for m in ms) / len(ms)
            context += f"- {mt.value}: avg={avg_val:.2f} {ms[0].unit}\n"

        context += "\nDetected Anomalies:\n"
        for a in anomalies[:5]:
            context += f"- {a.metric.metric_type.value}: {a.metric.value:.2f} (deviation: {a.deviation_from_baseline:.1f}%, severity: {a.severity.value})\n"

        prompt = f"""
        Analyze these performance metrics and identify system bottlenecks:

        {context}

        Identify:
        1. Primary bottleneck type (cpu_bound, memory_bound, io_bound, network_bound, database_bound, cache_miss, lock_contention, gc_pressure, thread_starvation, unknown)
        2. Confidence level (0.0-1.0)
        3. Affected services
        4. Contributing factors
        5. Specific optimization recommendations with expected impact
        6. Estimated impact on users (e.g., "50% latency reduction", "2x throughput increase")

        Respond in JSON format as an array of bottleneck analyses.
        """

        response = self.assistant.run(prompt)
        content = response.content

        bottlenecks = []
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            for item in data:
                bottlenecks.append(BottleneckAnalysis(
                    bottleneck_type=BottleneckType(item.get("bottleneck_type", "unknown")),
                    confidence=item.get("confidence", 0.5),
                    affected_services=item.get("affected_services", []),
                    contributing_factors=item.get("contributing_factors", []),
                    recommendations=item.get("recommendations", []),
                    estimated_impact=item.get("estimated_impact", "Unknown")
                ))
        except (json.JSONDecodeError, ValueError):
            # Fallback heuristic analysis
            if MetricType.CPU in metric_by_type:
                cpu_avg = sum(m.value for m in metric_by_type[MetricType.CPU]) / len(metric_by_type[MetricType.CPU])
                if cpu_avg > 80:
                    bottlenecks.append(BottleneckAnalysis(
                        bottleneck_type=BottleneckType.CPU_BOUND,
                        confidence=0.7,
                        affected_services=["all"],
                        contributing_factors=["High CPU utilization"],
                        recommendations=["Optimize hot paths", "Add caching", "Scale horizontally"],
                        estimated_impact="30-50% latency reduction"
                    ))

            if MetricType.MEMORY in metric_by_type:
                mem_avg = sum(m.value for m in metric_by_type[MetricType.MEMORY]) / len(metric_by_type[MetricType.MEMORY])
                if mem_avg > 85:
                    bottlenecks.append(BottleneckAnalysis(
                        bottleneck_type=BottleneckType.MEMORY_BOUND,
                        confidence=0.7,
                        affected_services=["all"],
                        contributing_factors=["High memory utilization"],
                        recommendations=["Reduce object allocation", "Optimize data structures", "Add memory"],
                        estimated_impact="20-40% memory reduction"
                    ))

            if MetricType.LATENCY in metric_by_type:
                lat_avg = sum(m.value for m in metric_by_type[MetricType.LATENCY]) / len(metric_by_type[MetricType.LATENCY])
                if lat_avg > 500:
                    bottlenecks.append(BottleneckAnalysis(
                        bottleneck_type=BottleneckType.DATABASE_BOUND,
                        confidence=0.5,
                        affected_services=["api"],
                        contributing_factors=["High latency"],
                        recommendations=["Add database indexes", "Optimize queries", "Add read replicas"],
                        estimated_impact="50-70% latency reduction"
                    ))

        return bottlenecks

    def handle_request(self, metrics_text: str) -> Dict:
        """
        Process performance metrics and return analysis results.
        """
        metrics = self.parse_metrics(metrics_text)
        anomalies = self.detect_anomalies(metrics)
        bottlenecks = self.analyze_bottlenecks(metrics, anomalies)

        return {
            "metrics_parsed": len(metrics),
            "anomalies_detected": len(anomalies),
            "bottlenecks_identified": len(bottlenecks),
            "metrics": [{
                "type": m.metric_type.value,
                "value": m.value,
                "unit": m.unit,
                "service": m.service,
                "percentile": m.percentile
            } for m in metrics],
            "anomalies": [{
                "metric_type": a.metric.metric_type.value,
                "value": a.metric.value,
                "deviation": round(a.deviation_from_baseline, 1),
                "severity": a.severity.value,
                "duration": a.duration_minutes,
                "indicators": a.root_cause_indicators
            } for a in anomalies],
            "bottlenecks": [{
                "type": b.bottleneck_type.value,
                "confidence": b.confidence,
                "affected_services": b.affected_services,
                "factors": b.contributing_factors,
                "recommendations": b.recommendations,
                "estimated_impact": b.estimated_impact
            } for b in bottlenecks]
        }


# Streamlit interface
st.title("Performance Monitoring Agent")
st.caption("Monitor application performance metrics, detect anomalies, identify bottlenecks, and generate optimization recommendations")

api_key = st.text_input("OpenAI API Key", type="password")

st.markdown("""
**Expected CSV format:**
```
metric_type,value,service
latency,450,api-gateway
latency,1200,api-gateway
error_rate,2.5,api-gateway
cpu,85,api-gateway
memory,92,api-gateway
cache_hit,78,api-gateway
```

**Or free text:**
```
Latency is 450ms for API gateway, p95 is 1200ms. Error rate is 2.5%. CPU at 85%, memory at 92%. Cache hit rate is 78%.
```
""")

metrics_text = st.text_area("Performance Metrics", 
    placeholder="Paste performance metrics here (CSV or free text)...",
    height=200)

if api_key and metrics_text:
    monitor = PerformanceMonitoringAgent(api_key)
    result = monitor.handle_request(metrics_text)

    st.subheader("Analysis Results")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Metrics Parsed", result["metrics_parsed"])
    with col2:
        st.metric("Anomalies", result["anomalies_detected"], delta_color="inverse")
    with col3:
        st.metric("Bottlenecks", result["bottlenecks_identified"], delta_color="inverse")

    if result["metrics"]:
        st.subheader("Metrics Overview")

        metrics_df = pd.DataFrame(result["metrics"])
        st.dataframe(metrics_df, use_container_width=True)

    if result["anomalies"]:
        st.subheader("Anomalies")

        for anomaly in result["anomalies"]:
            severity_color = {"critical": "red", "high": "orange", "medium": "yellow", "low": "green", "info": "blue"}

            with st.container():
                st.markdown(f"**{anomaly['metric_type'].upper()}**: {anomaly['value']} ({anomaly['metric_type']})")
                st.caption(f":{severity_color.get(anomaly['severity'], 'gray')}[{anomaly['severity'].upper()}] | Deviation: {anomaly['deviation']:.1f}% | Duration: {anomaly['duration']} min")

                for indicator in anomaly['indicators']:
                    st.warning(indicator)

                st.divider()

    if result["bottlenecks"]:
        st.subheader("Bottlenecks")

        for bottleneck in result["bottlenecks"]:
            with st.container():
                st.markdown(f"**{bottleneck['type'].replace('_', ' ').title()}** (Confidence: {bottleneck['confidence']:.0%})")
                st.caption(f"Affected: {', '.join(bottleneck['affected_services'])}")

                st.write("**Contributing Factors:**")
                for factor in bottleneck['factors']:
                    st.markdown(f"- {factor}")

                st.write("**Recommendations:**")
                for rec in bottleneck['recommendations']:
                    st.markdown(f"- {rec}")

                st.success(f"**Estimated Impact:** {bottleneck['estimated_impact']}")
                st.divider()
