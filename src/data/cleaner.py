import pandas as pd
import logging

logger = logging.getLogger(__name__)


def convert_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert TransactionStartTime from string to datetime.
    utc=True handles the Z timezone at the end of each timestamp.
    """
    df = df.copy()
    df["TransactionStartTime"] = pd.to_datetime(
        df["TransactionStartTime"], utc=True
    )
    logger.info("Converted TransactionStartTime to datetime")
    return df


def drop_uninformative_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns that carry no information for modelling.
    CountryCode is 256 for every single row — zero variance.
    """
    df = df.copy()
    cols_to_drop = ["CountryCode"]
    df = df.drop(columns=cols_to_drop)
    logger.info(f"Dropped columns: {cols_to_drop}")
    return df


def flag_reversals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a binary flag for negative transaction amounts.
    Reversals carry risk information — do not drop them.
    """
    df = df.copy()
    df["is_reversal"] = (df["Amount"] < 0).astype(int)
    reversal_count = int(df["is_reversal"].sum())
    logger.info(f"Flagged {reversal_count} reversal transactions")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master cleaning pipeline.
    Runs all steps in the correct order and returns clean DataFrame.
    """
    logger.info("Starting cleaning pipeline...")
    df = convert_datetime(df)
    df = drop_uninformative_columns(df)
    df = flag_reversals(df)
    logger.info(f"Cleaning complete. Final shape: {df.shape}")
    return df