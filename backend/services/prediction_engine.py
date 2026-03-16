"""Live churn prediction and customer insight service."""

from collections import Counter
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from config.database import get_db_connection
from services.ml_loader import ml_models


CANONICAL_COLUMNS = {
    "customer_name": ["customer_name", "name"],
    "email_address": ["email_address", "email"],
    "last_login_days": ["last_login_days"],
    "last_login_date": ["last_login_date"],
    "churn": ["churn"],
}

DEFAULT_SUBSCRIPTION_MAPPING = {"Basic": 0, "Premium": 1, "Standard": 2}

ACTION_MAP = {
    "High Charges": "Discount Offer",
    "Payment Failures": "Billing Recovery Outreach",
    "Low Login Frequency": "Re-engagement Campaign",
    "Recent Inactivity": "Re-engagement Campaign",
    "Low Feature Usage": "Feature Walkthrough",
    "Usage Drop": "Feature Walkthrough",
    "Support Friction": "Priority Support Escalation",
    "Weak Early Adoption": "Onboarding Check-in",
}


def _first_available_column(columns, candidates):
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _safe_quantile(series, quantile, fallback):
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        return fallback
    return float(numeric_series.quantile(quantile))


def _normalize_dataframe(df):
    frame = df.copy()
    frame.columns = [str(column).strip().lower() for column in frame.columns]

    for canonical_name, candidates in CANONICAL_COLUMNS.items():
        if canonical_name not in frame.columns:
            alias = _first_available_column(frame.columns, candidates)
            if alias is not None:
                frame[canonical_name] = frame[alias]

    if "customer_name" not in frame.columns:
        frame["customer_name"] = "New Customer"
    frame["customer_name"] = frame["customer_name"].fillna("New Customer").astype(str).str.strip()
    frame.loc[frame["customer_name"] == "", "customer_name"] = "New Customer"

    if "email_address" not in frame.columns:
        frame["email_address"] = ""
    frame["email_address"] = frame["email_address"].fillna("").astype(str).str.strip()

    if "churn" not in frame.columns:
        frame["churn"] = 0
    frame["churn"] = pd.to_numeric(frame["churn"], errors="coerce").fillna(0).astype(int)

    if "last_login_date" in frame.columns:
        frame["last_login_date"] = pd.to_datetime(frame["last_login_date"], errors="coerce")

    if "last_login_days" not in frame.columns:
        frame["last_login_days"] = np.nan

    frame["last_login_days"] = pd.to_numeric(frame["last_login_days"], errors="coerce")
    if "last_login_date" in frame.columns:
        computed_days = (datetime.now() - frame["last_login_date"]).dt.days
        frame["last_login_days"] = frame["last_login_days"].where(frame["last_login_date"].isna(), computed_days)

    frame["last_login_days"] = frame["last_login_days"].fillna(0).clip(lower=0).round().astype(int)

    if "last_login_date" not in frame.columns:
        frame["last_login_date"] = pd.NaT
    missing_dates = frame["last_login_date"].isna()
    frame.loc[missing_dates, "last_login_date"] = frame.loc[missing_dates, "last_login_days"].apply(
        lambda days: datetime.now().replace(microsecond=0) - timedelta(days=int(days))
    )
    frame["last_login"] = frame["last_login_date"].dt.strftime("%Y-%m-%d")

    return frame


def _build_feature_frame(frame, feature_columns):
    features = pd.DataFrame(index=frame.index)
    for feature in feature_columns:
        if feature in frame.columns:
            features[feature] = frame[feature]
        else:
            features[feature] = np.nan

    if "subscription_type" in features.columns:
        subscription_series = features["subscription_type"].fillna("Standard").astype(str).str.title()
        categories = sorted({*DEFAULT_SUBSCRIPTION_MAPPING.keys(), *subscription_series.unique().tolist()})
        subscription_mapping = {name: index for index, name in enumerate(categories)}
        features["subscription_type"] = subscription_series.map(subscription_mapping).fillna(
            DEFAULT_SUBSCRIPTION_MAPPING["Standard"]
        )

    numeric_columns = [column for column in features.columns if column != "subscription_type"]
    for column in numeric_columns:
        features[column] = pd.to_numeric(features[column], errors="coerce")

    medians = features[numeric_columns].median(numeric_only=True) if numeric_columns else pd.Series(dtype=float)
    if numeric_columns:
        features[numeric_columns] = features[numeric_columns].fillna(medians).fillna(0)

    return features


def _get_thresholds(frame):
    return {
        "high_charge": _safe_quantile(frame.get("monthly_charges", pd.Series(dtype=float)), 0.75, 1000),
        "low_login": _safe_quantile(frame.get("login_frequency", pd.Series(dtype=float)), 0.25, 8),
        "low_feature_usage": _safe_quantile(frame.get("feature_usage_count", pd.Series(dtype=float)), 0.25, 12),
        "low_active_days": _safe_quantile(frame.get("monthly_active_days", pd.Series(dtype=float)), 0.25, 8),
        "support_friction": max(2, round(_safe_quantile(frame.get("unresolved_tickets", pd.Series(dtype=float)), 0.75, 2))),
    }


def _detail_summary(row, thresholds):
    risk_signals = []
    loyalty_factors = []

    if row.get("payment_failures", 0) >= 2:
        risk_signals.append("Payment Failures")
    if row.get("monthly_charges", 0) >= thresholds["high_charge"]:
        risk_signals.append("High Charges")
    if row.get("login_frequency", 0) <= thresholds["low_login"]:
        risk_signals.append("Low Login Frequency")
    if row.get("last_login_days", 0) >= 21:
        risk_signals.append("Recent Inactivity")
    if row.get("feature_usage_count", 0) <= thresholds["low_feature_usage"]:
        risk_signals.append("Low Feature Usage")
    if row.get("usage_drop_flag", 0) == 1:
        risk_signals.append("Usage Drop")
    if row.get("unresolved_tickets", 0) >= thresholds["support_friction"]:
        risk_signals.append("Support Friction")
    if row.get("tenure_months", 0) <= 3 and row.get("monthly_active_days", 0) <= thresholds["low_active_days"]:
        risk_signals.append("Weak Early Adoption")

    if row.get("login_frequency", 0) > thresholds["low_login"] * 1.8:
        loyalty_factors.append("Frequent product logins")
    if row.get("feature_usage_count", 0) > thresholds["low_feature_usage"] * 1.8:
        loyalty_factors.append("Broad feature adoption")
    if row.get("last_login_days", 0) <= 7:
        loyalty_factors.append("Recent product activity")
    if row.get("payment_failures", 0) == 0:
        loyalty_factors.append("Clean billing history")
    if row.get("unresolved_tickets", 0) == 0:
        loyalty_factors.append("Low support friction")
    if row.get("tenure_months", 0) >= 12:
        loyalty_factors.append("Established customer tenure")

    risk_signals = list(dict.fromkeys(risk_signals))
    loyalty_factors = list(dict.fromkeys(loyalty_factors))

    if row["predicted_status"] == "Churned":
        title = "Reasons for Churn"
        items = risk_signals[:4] or ["Multiple churn indicators detected by the model"]
    elif row["predicted_status"] == "At Risk":
        title = "Warning Signs"
        items = risk_signals[:4] or ["Risk score is rising without a dominant single signal"]
    else:
        title = "Loyalty Factors"
        items = loyalty_factors[:4] or ["Healthy product usage and low friction"]

    recommended_actions = []

    # Keep retention interventions for non-active customers only.
    # Active customers should receive loyalty/growth actions, not recovery campaigns.
    if row["predicted_status"] == "Active":
        if "Established customer tenure" in loyalty_factors:
            recommended_actions.append("VIP nurture sequence")
        if "Frequent product logins" in loyalty_factors:
            recommended_actions.append("Referral Program Invite")
        if "Broad feature adoption" in loyalty_factors:
            recommended_actions.append("Loyalty Reward Offer")
        if not recommended_actions:
            recommended_actions.append("Maintain engagement cadence")
    else:
        for reason in risk_signals[:4]:
            action = ACTION_MAP.get(reason)
            if action and action not in recommended_actions:
                recommended_actions.append(action)
        if not recommended_actions:
            recommended_actions.append("Manager review and outreach")

    return {
        "detail_insight_title": title,
        "detail_insights": items,
        "churn_reasons": risk_signals[:4],
        "warning_signs": risk_signals[:4] if row["predicted_status"] == "At Risk" else [],
        "loyalty_factors": loyalty_factors[:4],
        "recommended_actions": recommended_actions,
        "primary_reason": (risk_signals or loyalty_factors or ["Healthy engagement"])[0],
    }


def _status_from_probability(probability):
    if probability >= 0.80:
        return "Churned", "High Risk"
    if probability >= 0.35:
        return "At Risk", "Medium Risk"
    return "Active", "Low Risk"


def _serialize_records(frame):
    records = frame.replace({np.nan: None}).to_dict(orient="records")
    serialized = []
    for record in records:
        record["risk_score"] = round(float(record["risk_score"]), 1)
        record["risk_probability"] = round(float(record["risk_probability"]), 4)
        record["health_score"] = round(float(record["health_score"]), 1)
        record["active_score"] = round(float(record["active_score"]), 1)
        for column in [
            "last_login_days",
            "tenure_months",
            "login_frequency",
            "feature_usage_count",
            "monthly_active_days",
            "payment_failures",
            "support_ticket_count",
            "unresolved_tickets",
            "discount_applied",
            "usage_drop_flag",
        ]:
            if record.get(column) is not None:
                record[column] = int(record[column])
        serialized.append(record)
    return serialized


def get_live_customer_predictions():
    """Fetch all rows from MySQL and enrich them with fresh model predictions."""
    if not ml_models.is_loaded():
        raise RuntimeError("ML models are not loaded.")

    conn = get_db_connection()
    try:
        raw_frame = pd.read_sql("SELECT * FROM customers", conn)
    finally:
        conn.close()

    if raw_frame.empty:
        return []

    frame = _normalize_dataframe(raw_frame)
    feature_columns = [str(column) for column in ml_models.get_feature_columns()]
    features = _build_feature_frame(frame, feature_columns)
    probabilities = ml_models.get_model().predict_proba(features)[:, 1]

    frame["risk_probability"] = probabilities
    frame["risk_score"] = frame["risk_probability"] * 100
    frame["health_score"] = (1 - frame["risk_probability"]) * 100
    # Active score is a normalized 10-point scale derived from health score.
    frame["active_score"] = frame["health_score"] / 10

    statuses = frame["risk_probability"].apply(_status_from_probability)
    frame["predicted_status"] = statuses.apply(lambda value: value[0])
    frame["status"] = frame["predicted_status"]
    frame["risk_level"] = statuses.apply(lambda value: value[1])
    frame["activity_status"] = np.where(
        frame["last_login_days"] > 30,
        "Inactive",
        np.where(frame["predicted_status"] == "Active", "Healthy", "Needs Attention"),
    )

    thresholds = _get_thresholds(frame)
    detail_data = frame.apply(lambda row: pd.Series(_detail_summary(row, thresholds)), axis=1)
    frame = pd.concat([frame, detail_data], axis=1)

    columns = [
        "customer_id",
        "customer_name",
        "email_address",
        "status",
        "predicted_status",
        "risk_level",
        "risk_score",
        "risk_probability",
        "health_score",
        "active_score",
        "activity_status",
        "last_login",
        "last_login_days",
        "tenure_months",
        "login_frequency",
        "avg_session_duration",
        "feature_usage_count",
        "monthly_active_days",
        "usage_drop_flag",
        "subscription_type",
        "monthly_charges",
        "payment_failures",
        "discount_applied",
        "support_ticket_count",
        "unresolved_tickets",
        "churn",
        "detail_insight_title",
        "detail_insights",
        "churn_reasons",
        "warning_signs",
        "loyalty_factors",
        "recommended_actions",
        "primary_reason",
    ]

    return _serialize_records(frame[columns].sort_values(["risk_probability", "monthly_charges"], ascending=[False, False]))


def get_dashboard_payload(customers):
    """Aggregate live KPI and chart data for the dashboard."""
    if not customers:
        return {
            "kpiMetrics": {
                "churnRate": "0.0%",
                "retentionRate": "0.0%",
                "activeUsers": "0",
                "healthScore": "0.0/100",
                "lossFromChurn": "$0",
            },
            "retentionData": [],
            "churnReasons": [],
            "topCustomers": [],
            "additionalMetrics": {
                "totalCustomers": 0,
                "timestamp": datetime.now().isoformat(),
            },
        }

    frame = pd.DataFrame(customers)
    total_customers = len(frame)
    churned_count = int((frame["predicted_status"] == "Churned").sum())
    active_count = int((frame["predicted_status"] == "Active").sum())
    at_risk_count = int((frame["predicted_status"] == "At Risk").sum())
    active_users = int((frame["last_login_days"] <= 30).sum())
    average_health = float(frame["health_score"].mean()) if total_customers else 0
    predicted_revenue_at_risk = float(frame.loc[frame["predicted_status"] != "Active", "monthly_charges"].sum())

    tenure_bins = [0, 3, 6, 12, 24, 36, 120]
    tenure_labels = ["0-3m", "4-6m", "7-12m", "13-24m", "25-36m", "36m+"]
    frame["tenure_bucket"] = pd.cut(frame["tenure_months"], bins=tenure_bins, labels=tenure_labels, include_lowest=True)
    retention_data = []
    for label in tenure_labels:
        bucket = frame[frame["tenure_bucket"] == label]
        if bucket.empty:
            retention = 0
        else:
            retention = float((bucket["predicted_status"] == "Active").mean() * 100)
        retention_data.append({"month": label, "retention": round(retention, 1)})

    reason_counter = Counter()
    for reasons in frame.loc[frame["predicted_status"] != "Active", "churn_reasons"]:
        reason_counter.update(reasons)

    reason_palette = ["#1D4ED8", "#3B82F6", "#60A5FA", "#BFDBFE"]
    churn_reasons = []
    total_reason_mentions = sum(reason_counter.values()) or 1
    for index, (reason, count) in enumerate(reason_counter.most_common(4)):
        churn_reasons.append(
            {
                "reason": reason,
                "value": round((count / total_reason_mentions) * 100, 1),
                "count": count,
                "color": reason_palette[index % len(reason_palette)],
            }
        )

    if not churn_reasons:
        churn_reasons = [
            {"reason": "Healthy Portfolio", "value": 100.0, "count": total_customers, "color": "#BFDBFE"}
        ]

    top_customers = frame.head(10)[
        [
            "customer_id",
            "customer_name",
            "email_address",
            "risk_score",
            "risk_level",
            "last_login_days",
            "primary_reason",
        ]
    ].to_dict(orient="records")

    return {
        "kpiMetrics": {
            "churnRate": f"{(churned_count / total_customers) * 100:.1f}%",
            "retentionRate": f"{(active_count / total_customers) * 100:.1f}%",
            "activeUsers": f"{active_users:,}",
            "healthScore": f"{average_health:.1f}/100",
            "lossFromChurn": f"${predicted_revenue_at_risk:,.0f}",
        },
        "retentionData": retention_data,
        "churnReasons": churn_reasons,
        "topCustomers": top_customers,
        "additionalMetrics": {
            "totalCustomers": total_customers,
            "activeCustomersCount": active_count,
            "atRiskCustomersCount": at_risk_count,
            "churnedCount": churned_count,
            "timestamp": datetime.now().isoformat(),
        },
    }


def get_analytics_payload(customers):
    """Aggregate live ML-driven analytics and recommendations."""
    if not customers:
        return {
            "churnRiskOverview": {
                "percentage": 0,
                "affectedCustomers": 0,
                "totalActive": 0,
                "description": "No customer rows are available for inference.",
            },
            "churnDrivers": [],
            "predictiveInsights": [],
            "recommendedActions": [],
            "driverBarData": [],
            "riskTrend": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "totalCustomers": 0,
            },
        }

    frame = pd.DataFrame(customers)
    intervention_pool = frame[frame["predicted_status"] != "Active"].copy()
    affected_customers = len(intervention_pool)
    churn_risk_percentage = (affected_customers / len(frame) * 100) if len(frame) else 0

    reason_counter = Counter()
    for reasons in intervention_pool["churn_reasons"]:
        reason_counter.update(reasons)

    churn_drivers = []
    for index, (reason, count) in enumerate(reason_counter.most_common(4), start=1):
        percentage = (count / max(affected_customers, 1)) * 100
        churn_drivers.append(
            {
                "rank": index,
                "title": reason,
                "count": count,
                "percentage": round(percentage, 1),
                "description": f"{count} customers are flagged by the model with {reason.lower()} as a leading churn signal.",
            }
        )

    if not churn_drivers:
        churn_drivers.append(
            {
                "rank": 1,
                "title": "Healthy portfolio",
                "count": len(frame),
                "percentage": 100.0,
                "description": "The current dataset is dominated by low-risk customers.",
            }
        )

    high_risk = frame[frame["predicted_status"] == "Churned"]
    medium_risk = frame[frame["predicted_status"] == "At Risk"]
    new_customers = frame[frame["tenure_months"] <= 1]
    predictive_insights = [
        {
            "title": "High-risk portfolio",
            "description": f"{len(high_risk)} customers are in the model's churned band with an average health score of {high_risk['health_score'].mean() if not high_risk.empty else 0:.1f}/100.",
        },
        {
            "title": "Watchlist coverage",
            "description": f"{len(medium_risk)} customers are currently at risk and should receive proactive retention touches before they move into the churned band.",
        },
        {
            "title": "New-entry inference",
            "description": f"{len(new_customers)} low-tenure rows are scored immediately on ingest, with an average risk score of {new_customers['risk_score'].mean() if not new_customers.empty else 0:.1f}%.",
        },
    ]

    action_counter = Counter()
    for actions in intervention_pool["recommended_actions"]:
        action_counter.update(actions)

    recommended_actions = []
    for index, (action, impact) in enumerate(action_counter.most_common(4), start=1):
        recommended_actions.append(
            {
                "title": action,
                "impact": impact,
                "priority": index,
            }
        )

    if not recommended_actions:
        recommended_actions.append({"title": "Maintain current nurture cadence", "impact": len(frame), "priority": 1})

    frame["tenure_bucket"] = pd.cut(
        frame["tenure_months"],
        bins=[0, 3, 6, 12, 24, 36, 120],
        labels=["0-3m", "4-6m", "7-12m", "13-24m", "25-36m", "36m+"],
        include_lowest=True,
    )

    risk_trend = []
    for label in ["0-3m", "4-6m", "7-12m", "13-24m", "25-36m", "36m+"]:
        bucket = frame[frame["tenure_bucket"] == label]
        if bucket.empty:
            risk_trend.append({"bucket": label, "avgRisk": 0, "avgHealth": 0})
        else:
            risk_trend.append(
                {
                    "bucket": label,
                    "avgRisk": round(float(bucket["risk_score"].mean()), 1),
                    "avgHealth": round(float(bucket["health_score"].mean()), 1),
                }
            )

    return {
        "churnRiskOverview": {
            "percentage": round(churn_risk_percentage, 1),
            "affectedCustomers": affected_customers,
            "totalActive": len(frame),
            "description": (
                f"{affected_customers} customers need retention attention now: "
                f"{len(high_risk)} are high-priority (Churned band) and {len(medium_risk)} are watchlist (At Risk). "
                "Admin priority: contact high-priority accounts first, resolve payment/support friction quickly, "
                "and monitor at-risk accounts for conversion to healthy status."
            ),
        },
        "churnDrivers": churn_drivers,
        "predictiveInsights": predictive_insights,
        "recommendedActions": recommended_actions,
        "driverBarData": [{"label": item["title"], "count": item["count"]} for item in churn_drivers],
        "riskTrend": risk_trend,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "totalCustomers": len(frame),
            "churnedCustomers": len(high_risk),
            "atRiskCustomers": len(medium_risk),
        },
    }