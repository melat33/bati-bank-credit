import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# GROUP 1 — Time features
# ─────────────────────────────────────────────

def compute_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract time-based behavioral features per customer.

    Features:
        avg_hour        — average hour of day they transact
        avg_day_of_week — average day of week (0=Mon, 6=Sun)
        is_weekend      — 1 if most transactions happen on weekends
        transaction_month — month of their most recent transaction
    """
    df = df.copy()
    df["hour"]       = df["TransactionStartTime"].dt.hour
    df["day_of_week"] = df["TransactionStartTime"].dt.dayofweek
    df["is_weekend"]  = df["day_of_week"].isin([5, 6]).astype(int)
    df["month"]       = df["TransactionStartTime"].dt.month

    time_features = df.groupby("CustomerId").agg(
        avg_hour        =("hour",        "mean"),
        avg_day_of_week =("day_of_week", "mean"),
        weekend_rate    =("is_weekend",  "mean"),
        transaction_month=("month",      "last")
    ).reset_index()

    time_features["avg_hour"]         = time_features["avg_hour"].round(2)
    time_features["avg_day_of_week"]  = time_features["avg_day_of_week"].round(2)
    time_features["weekend_rate"]     = time_features["weekend_rate"].round(4)

    logger.info(f"Time features shape: {time_features.shape}")
    return time_features


# ─────────────────────────────────────────────
# GROUP 2 — Amount features
# ─────────────────────────────────────────────

def compute_amount_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute statistical features from transaction amounts per customer.

    Features:
        std_amount   — how consistent are their transaction amounts?
        max_amount   — largest single transaction
        min_amount   — smallest single transaction
        log_monetary — log transform of total monetary (handles outliers)
    """
    amount_features = df.groupby("CustomerId").agg(
        std_amount=("Amount", "std"),
        max_amount=("Amount", "max"),
        min_amount=("Amount", "min"),
    ).reset_index()

    # std is NaN when customer has only 1 transaction — fill with 0
    amount_features["std_amount"] = amount_features["std_amount"].fillna(0)

    # log transform of total monetary per customer
    monetary = df.groupby("CustomerId")["Amount"].sum().reset_index()
    monetary.columns = ["CustomerId", "total_monetary"]
    amount_features = amount_features.merge(monetary, on="CustomerId")
    amount_features["log_monetary"] = np.log1p(
        np.abs(amount_features["total_monetary"])
    )
    amount_features = amount_features.drop(columns=["total_monetary"])

    logger.info(f"Amount features shape: {amount_features.shape}")
    return amount_features


# ─────────────────────────────────────────────
# GROUP 3 — Behavioral features
# ─────────────────────────────────────────────

def compute_reversal_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate reversal rate (%) per customer.
    High reversal rate = financially unstable = higher risk.
    """
    reversal_rate = (
        df.groupby("CustomerId")["is_reversal"]
        .agg(
            reversals="sum",
            total_transactions="count"
        )
        .assign(
            reversal_rate=lambda x: (
                x["reversals"] / x["total_transactions"] * 100
            ).round(2)
        )
        [["reversal_rate"]]
        .reset_index()
    )
    logger.info(f"Reversal rate computed for {len(reversal_rate)} customers")
    return reversal_rate


def compute_behavioral_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute engagement and diversity features per customer.

    Features:
        unique_products  — how many product categories used
        unique_providers — how many providers used
        avg_daily_transactions — transactions per active day
    """
    # unique products and providers
    diversity = df.groupby("CustomerId").agg(
        unique_products =("ProductCategory", "nunique"),
        unique_providers=("ProviderId",      "nunique"),
    ).reset_index()

    # avg daily transactions
    # active days = number of unique dates the customer transacted
    df = df.copy()
    df["date"] = df["TransactionStartTime"].dt.date
    active_days = df.groupby("CustomerId")["date"].nunique().reset_index()
    active_days.columns = ["CustomerId", "active_days"]

    transaction_counts = df.groupby("CustomerId").size().reset_index()
    transaction_counts.columns = ["CustomerId", "total_txns"]

    daily = active_days.merge(transaction_counts, on="CustomerId")
    daily["avg_daily_transactions"] = (
        daily["total_txns"] / daily["active_days"]
    ).round(2)
    daily = daily[["CustomerId", "avg_daily_transactions"]]

    behavioral = diversity.merge(daily, on="CustomerId")
    logger.info(f"Behavioral features shape: {behavioral.shape}")
    return behavioral


# ─────────────────────────────────────────────
# GROUP 4 — Risk ratio features
# ─────────────────────────────────────────────

def compute_risk_features(
    df: pd.DataFrame,
    rfm: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute risk-specific ratio features per customer.

    Features:
        monetary_per_transaction  — average spend per transaction
        recency_frequency_ratio   — Recency / Frequency (high = risky)
        negative_amount_count     — how many negative transactions
        positive_amount_sum       — sum of positive transactions only
        velocity_last_30_days     — transactions in last 30 days
    """
    # monetary per transaction
    monetary_per_txn = df.groupby("CustomerId").agg(
        total_monetary=("Amount", "sum"),
        total_txns    =("TransactionId", "count")
    ).reset_index()
    monetary_per_txn["monetary_per_transaction"] = (
        monetary_per_txn["total_monetary"] /
        monetary_per_txn["total_txns"]
    ).round(2)
    monetary_per_txn = monetary_per_txn[
        ["CustomerId", "monetary_per_transaction"]
    ]

    # negative amount count
    negative_counts = (
        df[df["Amount"] < 0]
        .groupby("CustomerId")
        .size()
        .reset_index()
    )
    negative_counts.columns = ["CustomerId", "negative_amount_count"]

    # positive amount sum
    positive_sum = (
        df[df["Amount"] > 0]
        .groupby("CustomerId")["Amount"]
        .sum()
        .reset_index()
    )
    positive_sum.columns = ["CustomerId", "positive_amount_sum"]

    # velocity last 30 days
    reference_date = df["TransactionStartTime"].max()
    cutoff = reference_date - pd.Timedelta(days=30)
    recent = df[df["TransactionStartTime"] >= cutoff]
    velocity = recent.groupby("CustomerId").size().reset_index()
    velocity.columns = ["CustomerId", "velocity_last_30_days"]

    # recency / frequency ratio from rfm
    rfm = rfm.copy()
    rfm["recency_frequency_ratio"] = np.where(
        rfm["Frequency"] > 0,
        (rfm["Recency"] / rfm["Frequency"]).round(4),
        0
    )
    ratio = rfm[["CustomerId", "recency_frequency_ratio"]]

    # merge all risk features
    risk = monetary_per_txn.copy()
    risk = risk.merge(negative_counts, on="CustomerId", how="left")
    risk = risk.merge(positive_sum,    on="CustomerId", how="left")
    risk = risk.merge(velocity,        on="CustomerId", how="left")
    risk = risk.merge(ratio,           on="CustomerId", how="left")

    # fill NaN — customers with no negative transactions = 0
    risk["negative_amount_count"] = risk["negative_amount_count"].fillna(0)
    risk["positive_amount_sum"]   = risk["positive_amount_sum"].fillna(0)
    risk["velocity_last_30_days"] = risk["velocity_last_30_days"].fillna(0)

    logger.info(f"Risk features shape: {risk.shape}")
    return risk


# ─────────────────────────────────────────────
# MASTER FUNCTION
# ─────────────────────────────────────────────

def build_features(
    df: pd.DataFrame,
    rfm: pd.DataFrame
) -> pd.DataFrame:
    """
    Master function — builds all 20 features and merges into one table.

    This is the SAME function called by both:
    - notebooks (for training)
    - FastAPI (for live predictions)

    One source of truth — guarantees identical features everywhere.

    Input:
        df  — cleaned transaction DataFrame (95,662 rows)
        rfm — RFM DataFrame with proxy labels (3,742 rows)

    Output:
        features DataFrame (3,742 rows × 20+ columns)
    """
    logger.info("Building all features...")

    # group 1 — time
    time_feat = compute_time_features(df)

    # group 2 — amount
    amount_feat = compute_amount_features(df)

    # group 3 — behavioral
    reversal_feat = compute_reversal_rate(df)
    behavioral_feat = compute_behavioral_features(df)

    # group 4 — risk ratios
    risk_feat = compute_risk_features(df, rfm)

    # merge everything onto rfm base
    features = rfm.copy()
    for feat_df in [time_feat, amount_feat,
                    reversal_feat, behavioral_feat, risk_feat]:
        features = features.merge(feat_df, on="CustomerId", how="left")

    logger.info(f"Final feature table shape: {features.shape}")
    logger.info(f"Columns: {features.columns.tolist()}")
    return features