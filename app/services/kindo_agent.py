"""Kindo AI agent service for generating bias audit reports."""

import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

KINDO_API_URL = "https://api.kindo.ai/v1/chat/completions"


def generate_audit_report(audit_name, audit_description, protected_attribute, metrics_summary):
    """Call the Kindo AI agent to generate a bias audit report.

    Returns the report text, or a fallback message on failure.
    """
    api_key = os.environ.get("KINDO_API_KEY", "")
    agent_id = os.environ.get("KINDO_BIAS_AUDIT_AGENT_ID", "")

    if not api_key or not agent_id:
        logger.warning("Kindo API key or agent ID not configured — returning mock report")
        return _mock_report(audit_name, audit_description, protected_attribute, metrics_summary)

    request_payload = json.dumps({
        "audit_name": audit_name,
        "audit_description": audit_description,
        "protected_attribute": protected_attribute,
        "metrics_summary": metrics_summary,
    })

    body = {
        "model": agent_id,
        "messages": [
            {"role": "user", "content": request_payload}
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(KINDO_API_URL, json=body, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Try to parse as JSON
        try:
            parsed = json.loads(content)
            return _format_report(parsed)
        except (json.JSONDecodeError, KeyError):
            return content

    except Exception as exc:
        logger.exception("Kindo agent call failed: %s", exc)
        return _mock_report(audit_name, audit_description, protected_attribute, metrics_summary)


def _format_report(parsed):
    """Format the parsed JSON response into readable text."""
    sections = []

    title = parsed.get("title", "Bias Audit Report")
    sections.append(f"# {title}\n")

    if parsed.get("executive_summary"):
        sections.append(f"## Executive Summary\n{parsed['executive_summary']}\n")

    if parsed.get("findings"):
        sections.append("## Key Findings")
        for i, finding in enumerate(parsed["findings"], 1):
            severity = finding.get("severity", "info").upper()
            metric = finding.get("metric", "")
            desc = finding.get("description", "")
            sections.append(f"\n### Finding {i} [{severity}]: {metric}\n{desc}")

    if parsed.get("recommendations"):
        sections.append("\n## Recommendations")
        for i, rec in enumerate(parsed["recommendations"], 1):
            sections.append(f"{i}. {rec}")

    if parsed.get("regulatory_notes"):
        sections.append(f"\n## Regulatory Notes\n{parsed['regulatory_notes']}")

    return "\n".join(sections)


def _mock_report(audit_name, audit_description, protected_attribute, metrics_summary):
    """Generate a placeholder report when the Kindo agent is not configured."""
    return f"""# Bias Audit Report: {audit_name}

## Executive Summary
This is a placeholder report generated without the AI agent. Configure KINDO_API_KEY and KINDO_BIAS_AUDIT_AGENT_ID to enable AI-powered audit reports.

## Audit Details
- **Name:** {audit_name}
- **Description:** {audit_description}
- **Protected Attribute:** {protected_attribute}

## Metrics
{metrics_summary}

## Recommendations
1. Connect the Kindo AI agent for detailed bias analysis and actionable recommendations.
2. Review the metrics above and compare against regulatory thresholds (e.g., 80% rule for disparate impact).
3. Consider collecting additional data to improve statistical significance of findings.

---
*This report was generated without AI analysis. Configure the Kindo Bias Audit Agent for comprehensive reports.*
"""
