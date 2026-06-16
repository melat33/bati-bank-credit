import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "TransactionId", "BatchId", "AccountId",
    "SubscriptionId", "CustomerId", "CurrencyCode",
    "CountryCode", "ProviderId", "ProductId",
    "ProductCategory", "ChannelId", "Amount",
    "Value", "TransactionStartTime", "PricingStrategy"
]


def load_raw_data(path: str) -> pd.DataFrame:
    """
    Load the Bati Bank CSV file and return a raw DataFrame.
    Raises FileNotFoundError if path does not exist.
    Raises ValueError if required columns are missing.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    logger.info(f"Loading data from: {path}")
    df = pd.read_csv("data/raw/data.csv")
    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")

    validate_columns(df, REQUIRED_COLUMNS)
    return df


def validate_columns(df: pd.DataFrame, required: list) -> bool:
    """
    Check that all required columns exist in the DataFrame.
    Raises ValueError listing exactly which columns are missing.
    """
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    logger.info("All required columns present")
    return True


def get_summary(df: pd.DataFrame) -> dict:
    """
    Return a dictionary of key facts about the DataFrame.
    Use this in your notebook to understand your data quickly.
    """
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "missing_per_column": df.isnull().sum().to_dict(),
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "dtypes": df.dtypes.astype(str).to_dict()
    }
    logger.info(f"Summary: {summary['rows']} rows, "
                f"{summary['total_missing']} missing values, "
                f"{summary['duplicate_rows']} duplicates")
    return summary