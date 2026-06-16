import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def plot_elbow(rfm_scaled: np.ndarray, k_range: range = range(2, 11)) -> None:
    """
    Plot inertia for each K to find the elbow point.
    Look for where the curve stops dropping steeply and flattens.
    Save the plot to outputs/plots/elbow_curve.png.
    """
    inertias = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(rfm_scaled)
        inertias.append(km.inertia_)

    plt.figure(figsize=(8, 4))
    plt.plot(k_range, inertias, marker='o', color='steelblue', linewidth=2)
    plt.title('Elbow Method — Finding Best K', fontsize=14)
    plt.xlabel('Number of clusters (K)')
    plt.ylabel('Inertia')
    plt.xticks(k_range)
    plt.tight_layout()
    # build absolute path from this file's location
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    )))
    save_dir = os.path.join(project_root, 'outputs', 'plots')
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(os.path.join(save_dir, 'elbow_curve.png'),
                bbox_inches='tight', dpi=150)
    plt.show()
    logger.info("Saved: outputs/plots/elbow_curve.png")

    # print inertia values so you can see the drop rate
    for k, inertia in zip(k_range, inertias):
        logger.info(f"K={k}: inertia={inertia:.0f}")


def scale_rfm(rfm: pd.DataFrame) -> np.ndarray:
    """
    Scale RFM features using StandardScaler before clustering.

    Why scaling is mandatory here:
    - Recency  range = ~90
    - Frequency range = ~4,090
    - Monetary  range = ~183,000,000

    Without scaling, KMeans clusters only on Monetary and ignores
    Recency and Frequency completely.

    Returns scaled numpy array — NOT a DataFrame.
    Scaler is fit on RFM columns only.
    """
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(
        rfm[['Recency', 'Frequency', 'Monetary']]
    )
    logger.info(
        f"Scaled RFM — mean: {rfm_scaled.mean(axis=0).round(3)}, "
        f"std: {rfm_scaled.std(axis=0).round(3)}"
    )
    return rfm_scaled, scaler


def fit_kmeans(rfm_scaled: np.ndarray, n_clusters: int = 3) -> KMeans:
    """
    Fit KMeans on scaled RFM features.
    Returns fitted KMeans model.
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(rfm_scaled)
    logger.info(f"KMeans fitted with K={n_clusters}, "
                f"inertia={kmeans.inertia_:.0f}")
    return kmeans


def get_cluster_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Return mean RFM values per cluster.

    Use this to identify the high risk cluster:
    High risk = highest Recency + lowest Frequency + lowest Monetary

    Print this table and look for that pattern.
    """
    summary = rfm.groupby('Cluster')[
        ['Recency', 'Frequency', 'Monetary']
    ].mean().round(2)

    logger.info(f"Cluster summary:\n{summary}")
    return summary


def get_high_risk_cluster(cluster_summary: pd.DataFrame) -> int:
    """
    Automatically identify the high risk cluster.

    High risk cluster has:
    - Highest Recency  (most inactive)
    - Lowest Frequency (fewest transactions)
    - Lowest Monetary  (lowest spend)

    We score each cluster and pick the one with the highest risk score.
    Returns the cluster number (integer).
    """
    # normalize each column to 0-1 range
    summary = cluster_summary.copy()

    # for recency: higher = more risky → normalize as-is
    summary['recency_score'] = (
        (summary['Recency'] - summary['Recency'].min()) /
        (summary['Recency'].max() - summary['Recency'].min())
    )

    # for frequency: lower = more risky → invert
    summary['freq_score'] = 1 - (
        (summary['Frequency'] - summary['Frequency'].min()) /
        (summary['Frequency'].max() - summary['Frequency'].min())
    )

    # for monetary: lower = more risky → invert
    summary['monetary_score'] = 1 - (
        (summary['Monetary'] - summary['Monetary'].min()) /
        (summary['Monetary'].max() - summary['Monetary'].min())
    )

    # total risk score = sum of all 3
    summary['risk_score'] = (
        summary['recency_score'] +
        summary['freq_score'] +
        summary['monetary_score']
    )

    high_risk_cluster = int(summary['risk_score'].idxmax())
    logger.info(f"Auto-identified high risk cluster: {high_risk_cluster}")
    logger.info(f"Risk scores:\n{summary['risk_score']}")
    return high_risk_cluster


def generate_proxy_labels(
    rfm: pd.DataFrame,
    n_clusters: int = 3
) -> pd.DataFrame:
    """
    Master function — runs full KMeans pipeline and assigns proxy labels.

    Steps:
    1. Scale RFM features
    2. Plot elbow curve
    3. Fit KMeans
    4. Get cluster summary
    5. Auto-identify high risk cluster
    6. Assign is_high_risk label (1 = high risk, 0 = low risk)

    Returns rfm DataFrame with Cluster and is_high_risk columns added.
    """
    rfm = rfm.copy()

    logger.info("Starting proxy label generation...")

    # step 1 — scale
    rfm_scaled, scaler = scale_rfm(rfm)

    # step 2 — elbow plot (run before fitting to confirm K choice)
    plot_elbow(rfm_scaled)

    # step 3 — fit KMeans
    kmeans = fit_kmeans(rfm_scaled, n_clusters=n_clusters)
    rfm['Cluster'] = kmeans.labels_

    # step 4 — cluster summary
    cluster_summary = get_cluster_summary(rfm)
    print("\nCluster Summary (mean RFM per cluster):")
    print(cluster_summary)

    # step 5 — identify high risk cluster automatically
    high_risk_cluster = get_high_risk_cluster(cluster_summary)
    print(f"\nHigh risk cluster identified: Cluster {high_risk_cluster}")

    # step 6 — assign binary label
    rfm['is_high_risk'] = (rfm['Cluster'] == high_risk_cluster).astype(int)

    # summary
    high_risk_count = rfm['is_high_risk'].sum()
    logger.info(f"High risk customers : {high_risk_count}")
    logger.info(f"Low risk customers  : {len(rfm) - high_risk_count}")
    logger.info(f"High risk rate      : {high_risk_count/len(rfm)*100:.1f}%")

    print(f"\nHigh risk customers : {high_risk_count}")
    print(f"Low risk customers  : {len(rfm) - high_risk_count}")
    print(f"High risk rate      : {high_risk_count/len(rfm)*100:.1f}%")

    return rfm, kmeans, scaler