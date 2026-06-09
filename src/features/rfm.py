import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Recency, Frequency, Monetary features per customer.

    Recency  = days since last transaction (lower = more active)
    Frequency = total number of transactions
    Monetary  = total transaction amount (can be negative)

    Returns one row per customer — 3,742 rows for Bati Bank data.
    """
    df = df.copy()

    # reference date = last date in dataset
    # we do NOT use today — data ends in Feb 2019
    reference_date = df["TransactionStartTime"].max()
    logger.info(f"Reference date: {reference_date}")

    rfm = df.groupby("CustomerId").agg(
        Recency=(
            "TransactionStartTime",
            # total_seconds / 86400 handles timezone-aware datetimes
            lambda x: (reference_date - x.max()).total_seconds() / 86400
        ),
        Frequency=(
            "TransactionId",
            "count"
        ),
        Monetary=(
            "Amount",
            "sum"
        )
    ).reset_index()

    # round recency to 2 decimal places
    rfm["Recency"] = rfm["Recency"].round(2)
                       
    logger.info(f"RFM table shape: {rfm.shape}")
    logger.info(f"Recency  — min: {rfm['Recency'].min():.1f} "
                f"max: {rfm['Recency'].max():.1f}")
    logger.info(f"Frequency — min: {rfm['Frequency'].min()} "
                f"max: {rfm['Frequency'].max()}")
    logger.info(f"Monetary  — min: {rfm['Monetary'].min():.0f} "
                f"max: {rfm['Monetary'].max():.0f}")

    return rfm


