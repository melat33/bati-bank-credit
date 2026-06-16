import pandas as pd
import logging

logger = logging.getLogger(__name__)


def temporal_split(
    features: pd.DataFrame,
    df_clean: pd.DataFrame,
    target_col: str = "is_high_risk",
    ratio: float = 0.80
):
    """
    Temporal train-test split based on each customer's
    last transaction date.

    Why temporal and not random:
        Random split leaks future data into training.
        A model trained on Feb 2019 data cannot fairly
        be tested on Nov 2018 data — it already saw the future.
        Temporal split ensures train is always before test.

    Parameters
    ----------
    features   : customer-level feature table (3,742 rows)
    df_clean   : transaction-level cleaned dataset (95,662 rows)
    target_col : name of target column (default: is_high_risk)
    ratio      : fraction of timeline used for training (default: 0.80)

    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    # step 1 — find last transaction date per customer
    last_txn = (
        df_clean.groupby("CustomerId")["TransactionStartTime"]
        .max()
        .reset_index()
        .rename(columns={"TransactionStartTime": "LastTransactionDate"})
    )

    # step 2 — calculate temporal cutoff date
    start_date = df_clean["TransactionStartTime"].min()
    end_date   = df_clean["TransactionStartTime"].max()
    duration   = end_date - start_date
    cutoff_date = start_date + duration * ratio

    print(f"Start date  : {start_date.date()}")
    print(f"End date    : {end_date.date()}")
    print(f"Cutoff date : {cutoff_date.date()}")
    print(f"Train period: {start_date.date()} → {cutoff_date.date()}")
    print(f"Test period : {cutoff_date.date()} → {end_date.date()}")

    logger.info(f"Cutoff date: {cutoff_date}")

    # step 3 — merge last transaction date onto features
    features = features.merge(last_txn, on="CustomerId", how="left")

    # step 4 — split customers by cutoff date
    train_df = features[
        features["LastTransactionDate"] < cutoff_date
    ].copy()

    test_df = features[
        features["LastTransactionDate"] >= cutoff_date
    ].copy()

    # step 5 — assert no leakage
    # max train date must be strictly less than min test date
    assert (
        train_df["LastTransactionDate"].max() <
        test_df["LastTransactionDate"].min()
    ), "Temporal leakage detected! Check your cutoff date."

    print(f"\nNo temporal leakage detected ✓")
    print(f"Train customers : {len(train_df)} "
          f"({len(train_df)/len(features)*100:.1f}%)")
    print(f"Test customers  : {len(test_df)} "
          f"({len(test_df)/len(features)*100:.1f}%)")

    logger.info(f"Train: {len(train_df)} customers")
    logger.info(f"Test : {len(test_df)} customers")

    # step 6 — create X and y
    # drop columns that must not be features:
    # CustomerId  — identifier, not a signal
    # Cluster     — leaks label information (used to create is_high_risk)
    # LastTransactionDate — future information leak
    # target_col  — the label itself
    drop_cols = [
        target_col,
        "LastTransactionDate",
        "CustomerId",
        "Cluster"
    ]

    X_train = train_df.drop(columns=drop_cols)
    y_train = train_df[target_col]

    X_test  = test_df.drop(columns=drop_cols)
    y_test  = test_df[target_col]

    print(f"\nX_train shape : {X_train.shape}")
    print(f"X_test shape  : {X_test.shape}")
    print(f"y_train distribution:\n{y_train.value_counts()}")
    print(f"y_test distribution:\n{y_test.value_counts()}")

    return X_train, X_test, y_train, y_test