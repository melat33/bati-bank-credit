import os
import logging
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, f1_score,
    precision_score, recall_score
)
from imblearn.over_sampling import ADASYN
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)


def apply_adasyn(
    X_train: pd.DataFrame,
    y_train: pd.Series
):
    """
    Apply ADASYN oversampling to training data only.

    Why ADASYN not SMOTE:
        ADASYN focuses synthetic samples on hard-to-classify
        boundary regions — more realistic than uniform SMOTE.

    Why training data only:
        Test data must reflect real-world class distribution.
        Applying ADASYN to test data would give fake metrics.

    Returns resampled X_train, y_train.
    """
    logger.info(f"Before ADASYN: {y_train.value_counts().to_dict()}")

    adasyn = ADASYN(random_state=42)
    X_resampled, y_resampled = adasyn.fit_resample(X_train, y_train)

    logger.info(f"After ADASYN: {y_resampled.value_counts().to_dict()}")
    logger.info(f"Total training rows after ADASYN: {len(X_resampled)}")

    return X_resampled, y_resampled


def train_baseline(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> LogisticRegression:
    """
    Train Logistic Regression as baseline model.

    Why baseline first:
        A simple model sets the minimum bar XGBoost must beat.
        If XGBoost barely improves over LogReg, the added
        complexity is not worth it.

    Returns fitted LogisticRegression model.
    """
    logger.info("Training Logistic Regression baseline...")

    lr = LogisticRegression(
        random_state=42,
        max_iter=1000
    )
    lr.fit(X_train, y_train)

    logger.info("Logistic Regression training complete")
    return lr


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> XGBClassifier:
    """
    Train XGBoost classifier.

    Why XGBoost over Logistic Regression:
        1. Captures non-linear relationships between features
        2. Boosting corrects errors from previous trees
        3. Built-in feature importance
        4. Robust to outliers in Amount and Monetary features

    Hyperparameters explained:
        n_estimators  = 200  : number of trees to build
        max_depth     = 4    : max depth per tree (controls overfitting)
        learning_rate = 0.1  : step size — lower = more careful learning
        subsample     = 0.8  : use 80% of data per tree (prevents overfitting)

    Returns fitted XGBClassifier model.
    """
    logger.info("Training XGBoost...")
    logger.info(f"Hyperparameters: n_estimators=200, max_depth=4, "
                f"learning_rate=0.1, subsample=0.8")

    xgb = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
        eval_metric='logloss',
        verbosity=0
    )
    xgb.fit(X_train, y_train)

    logger.info("XGBoost training complete")
    return xgb


def get_metrics(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str = "model"
) -> dict:
    """
    Compute evaluation metrics for a trained model.

    Metrics explained:
        AUC       : area under ROC curve — overall discrimination ability
        F1        : harmonic mean of precision and recall
        Precision : of all predicted high risk, how many truly are?
        Recall    : of all truly high risk, how many did we catch?

    For credit risk, Recall matters most —
    missing a high risk customer is more costly than a false alarm.

    Returns dict of metric name → value.
    """
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        'model'    : model_name,
        'auc'      : round(roc_auc_score(y_test, y_proba), 4),
        'f1'       : round(f1_score(y_test, y_pred), 4),
        'precision': round(precision_score(y_test, y_pred), 4),
        'recall'   : round(recall_score(y_test, y_pred), 4),
    }

    logger.info(f"{model_name} metrics: {metrics}")
    return metrics


def save_model(model, path: str) -> None:
    """
    Save trained model to disk using joblib.

    Why joblib not CSV or JSON:
        A trained model is a complex Python object containing
        hundreds of decision trees, learned split thresholds,
        and hyperparameters. CSV/JSON can only store flat tables.
        joblib serializes any Python object into a binary file
        that can be restored identically later.

    Args:
        model : fitted sklearn or XGBoost model
        path  : full file path e.g. 'outputs/models/xgboost.pkl'
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    logger.info(f"Model saved: {path}")
    print(f"Saved: {path}")


def save_feature_names(feature_names: list, path: str) -> None:
    """
    Save feature names list to disk.

    Why save feature names:
        FastAPI must receive features in the EXACT same order
        the model was trained on. Saving the list guarantees
        this — the API loads it and reorders input accordingly.

    Args:
        feature_names : list of column names from X_train
        path          : full file path e.g. 'outputs/models/features.pkl'
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(feature_names, path)
    logger.info(f"Feature names saved: {path}")
    print(f"Saved: {path}")