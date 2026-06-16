import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os

logger = logging.getLogger(__name__)

# create outputs folder if it does not exist
os.makedirs("outputs/plots", exist_ok=True)


def plot_transaction_time(df: pd.DataFrame) -> None:
    """
    Bar chart of transaction count by hour of day.
    Shows peak hours and unusual activity patterns.
    """
    hourly_counts = (
        df["TransactionStartTime"]
        .dt.hour
        .value_counts()
        .sort_index()
    )

    plt.figure(figsize=(10, 5))
    sns.barplot(
        x=hourly_counts.index,
        y=hourly_counts.values,
        color="steelblue"
    )
    plt.title("Transactions by Hour of Day", fontsize=14)
    plt.xlabel("Hour of Day (0 = midnight, 12 = noon)")
    plt.ylabel("Number of Transactions")
    plt.tight_layout()
    plt.savefig("outputs/plots/transactions_by_hour.png",
                bbox_inches="tight", dpi=150)
    plt.show()
    logger.info("Saved: outputs/plots/transactions_by_hour.png")


def plot_fraud_imbalance(df: pd.DataFrame) -> None:
    """
    Bar chart showing fraud vs non-fraud with percentages.
    Makes the class imbalance problem visually obvious.
    """
    total = len(df)

    plt.figure(figsize=(6, 4))
    ax = sns.countplot(
        x="FraudResult",
        data=df,
        palette=["steelblue", "crimson"]
    )

    # replace 0/1 with readable labels
    ax.set_xticklabels(["Not Fraud", "Fraud"])
    plt.title("Fraud vs Non-Fraud Transactions", fontsize=14)
    plt.xlabel("")
    plt.ylabel("Number of Transactions")

    # add percentage labels on top of each bar
    for p in ax.patches:
        count = int(p.get_height())
        percent = 100 * count / total
        ax.annotate(
            f"{count:,}\n({percent:.2f}%)",
            (p.get_x() + p.get_width() / 2, count),
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()
    plt.savefig("outputs/plots/fraud_imbalance.png",
                bbox_inches="tight", dpi=150)
    plt.show()
    logger.info("Saved: outputs/plots/fraud_imbalance.png")


def plot_amount_distribution(df: pd.DataFrame) -> None:
    """
    Two charts side by side:
    Left  — raw Amount showing extreme outliers
    Right — log transformed Amount showing real distribution
    Justifies why we use log transformation in feature engineering.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # left — raw Amount
    sns.histplot(
        df["Amount"],
        bins=50,
        kde=True,
        ax=axes[0],
        color="steelblue"
    )
    axes[0].set_title("Raw Amount Distribution", fontsize=13)
    axes[0].set_xlabel("Amount (UGX)")
    axes[0].set_ylabel("Frequency")

    # right — log transformed
    # np.log1p(np.abs()) handles negatives and zeros safely
    log_amount = np.log1p(np.abs(df["Amount"]))
    sns.histplot(
        log_amount,
        bins=50,
        kde=True,
        ax=axes[1],
        color="darkorange"
    )
    axes[1].set_title("Log Transformed Amount", fontsize=13)
    axes[1].set_xlabel("log1p(|Amount|)")
    axes[1].set_ylabel("Frequency")

    plt.suptitle(
        "Amount Distribution: Raw vs Log Transformed",
        fontsize=14, y=1.02
    )
    plt.tight_layout()
    plt.savefig("outputs/plots/amount_distribution.png",
                bbox_inches="tight", dpi=150)
    plt.show()
    logger.info("Saved: outputs/plots/amount_distribution.png")


def plot_missing_values(df: pd.DataFrame) -> None:
    """
    Bar chart of missing values per column.
    Skips gracefully if no missing values exist.
    """
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        logger.info("No missing values to plot — skipping")
        return

    plt.figure(figsize=(10, 4))
    sns.barplot(x=missing.index, y=missing.values, color="crimson")
    plt.title("Missing Values per Column", fontsize=14)
    plt.xlabel("Column")
    plt.ylabel("Missing Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("outputs/plots/missing_values.png",
                bbox_inches="tight", dpi=150)
    plt.show()
    logger.info("Saved: outputs/plots/missing_values.png")


def plot_product_category(df: pd.DataFrame) -> None:
    """
    Bar chart of transaction count by product category.
    Shows which products drive the most volume.
    """
    counts = df["ProductCategory"].value_counts()

    plt.figure(figsize=(10, 5))
    sns.barplot(x=counts.index, y=counts.values, color="steelblue")
    plt.title("Transactions by Product Category", fontsize=14)
    plt.xlabel("Product Category")
    plt.ylabel("Number of Transactions")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("outputs/plots/product_category.png",
                bbox_inches="tight", dpi=150)
    plt.show()
    logger.info("Saved: outputs/plots/product_category.png")
    
    