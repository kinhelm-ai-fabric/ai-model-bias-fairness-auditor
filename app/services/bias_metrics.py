"""Bias metrics computation service.

Computes fairness metrics from CSV data for a given protected attribute.
"""

import csv
import io
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def parse_csv_data(csv_text):
    """Parse CSV text into a list of dicts."""
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def compute_bias_metrics(rows, protected_attr, label_col="label", pred_col="prediction", favorable="1"):
    """Compute fairness metrics across groups defined by protected_attr.

    Returns a list of metric result dicts.
    """
    if not rows:
        return []

    # Validate columns exist
    sample = rows[0]
    missing = []
    for col in [protected_attr, label_col, pred_col]:
        if col not in sample:
            missing.append(col)
    if missing:
        raise ValueError(f"Missing columns in data: {', '.join(missing)}")

    # Group rows by protected attribute value
    groups = defaultdict(list)
    for row in rows:
        groups[row[protected_attr]].append(row)

    results = []

    # ── Per-group metrics ─────────────────────────────────────────────
    group_stats = {}
    for group_name, group_rows in groups.items():
        total = len(group_rows)
        positive_pred = sum(1 for r in group_rows if str(r[pred_col]).strip() == str(favorable).strip())
        positive_label = sum(1 for r in group_rows if str(r[label_col]).strip() == str(favorable).strip())
        true_positive = sum(
            1 for r in group_rows
            if str(r[pred_col]).strip() == str(favorable).strip()
            and str(r[label_col]).strip() == str(favorable).strip()
        )
        false_positive = sum(
            1 for r in group_rows
            if str(r[pred_col]).strip() == str(favorable).strip()
            and str(r[label_col]).strip() != str(favorable).strip()
        )
        false_negative = sum(
            1 for r in group_rows
            if str(r[pred_col]).strip() != str(favorable).strip()
            and str(r[label_col]).strip() == str(favorable).strip()
        )

        selection_rate = positive_pred / total if total > 0 else 0
        tpr = true_positive / positive_label if positive_label > 0 else 0
        fpr = false_positive / (total - positive_label) if (total - positive_label) > 0 else 0

        group_stats[group_name] = {
            "total": total,
            "positive_pred": positive_pred,
            "positive_label": positive_label,
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "selection_rate": selection_rate,
            "tpr": tpr,
            "fpr": fpr,
        }

        results.append({
            "metric_name": "Selection Rate",
            "metric_value": round(selection_rate, 4),
            "group_name": group_name,
            "details": f"{positive_pred}/{total} predicted favorable",
        })
        results.append({
            "metric_name": "True Positive Rate",
            "metric_value": round(tpr, 4),
            "group_name": group_name,
            "details": f"{true_positive}/{positive_label} actual positives correctly predicted",
        })
        results.append({
            "metric_name": "False Positive Rate",
            "metric_value": round(fpr, 4),
            "group_name": group_name,
            "details": f"{false_positive}/{total - positive_label} actual negatives incorrectly predicted positive",
        })

    # ── Cross-group metrics ───────────────────────────────────────────
    group_names = sorted(group_stats.keys())
    if len(group_names) >= 2:
        # Disparate Impact: ratio of lowest to highest selection rate
        rates = [(g, group_stats[g]["selection_rate"]) for g in group_names]
        max_rate = max(r[1] for r in rates)
        min_rate = min(r[1] for r in rates)
        min_group = [r[0] for r in rates if r[1] == min_rate][0]
        max_group = [r[0] for r in rates if r[1] == max_rate][0]
        di = min_rate / max_rate if max_rate > 0 else 0

        results.append({
            "metric_name": "Disparate Impact Ratio",
            "metric_value": round(di, 4),
            "group_name": f"{min_group} vs {max_group}",
            "details": f"Ratio of selection rates: {min_rate:.4f}/{max_rate:.4f}. "
                       f"Values below 0.8 indicate potential adverse impact.",
        })

        # Statistical Parity Difference
        spd = min_rate - max_rate
        results.append({
            "metric_name": "Statistical Parity Difference",
            "metric_value": round(spd, 4),
            "group_name": f"{min_group} vs {max_group}",
            "details": f"Difference in selection rates: {min_rate:.4f} - {max_rate:.4f}. "
                       f"Values near 0 indicate parity.",
        })

        # Equal Opportunity Difference (TPR difference)
        tprs = [(g, group_stats[g]["tpr"]) for g in group_names]
        max_tpr = max(r[1] for r in tprs)
        min_tpr = min(r[1] for r in tprs)
        min_tpr_group = [r[0] for r in tprs if r[1] == min_tpr][0]
        max_tpr_group = [r[0] for r in tprs if r[1] == max_tpr][0]
        eod = min_tpr - max_tpr

        results.append({
            "metric_name": "Equal Opportunity Difference",
            "metric_value": round(eod, 4),
            "group_name": f"{min_tpr_group} vs {max_tpr_group}",
            "details": f"Difference in true positive rates: {min_tpr:.4f} - {max_tpr:.4f}. "
                       f"Values near 0 indicate equal opportunity.",
        })

    return results


def summarize_metrics(results):
    """Create a text summary of metric results for the AI agent."""
    if not results:
        return "No metrics computed."

    lines = ["Bias Audit Metrics Summary", "=" * 40]

    # Group by metric name
    by_metric = defaultdict(list)
    for r in results:
        by_metric[r["metric_name"]].append(r)

    for metric_name, entries in by_metric.items():
        lines.append(f"\n{metric_name}:")
        for e in entries:
            val = e.get("metric_value")
            val_str = f"{val:.4f}" if val is not None else "N/A"
            group = e.get("group_name", "")
            detail = e.get("details", "")
            lines.append(f"  [{group}] = {val_str}")
            if detail:
                lines.append(f"    {detail}")

    return "\n".join(lines)
