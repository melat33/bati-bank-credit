import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix,
    RocCurveDisplay
)

logger = logging.getLogger(__name__)

# ensure plots folder exists
os.makedirs('outputs/plots', exist_ok=True)


def plot_roc_curve(
    y_test,
    y_proba,
    model_name: str = "model"
) -> None:
    """
    Plot ROC curve for a single model.

    ROC curve shows tradeoff between:
        True Positive Rate  (Recall) on y axis
        False Positive Rate (1-Specificity) on x axis

    AUC = area under this curve.
    Random model = diagonal line = AUC 0.5
    Perfect model = top-left corner = AUC 1.0

    Parameters
    ----------
    y_test     : actual labels
    y_proba    : predicted probabilities for positive class
    model_name : model name for title and filename
    """
    plt.figure(figsize=(7, 5))
    RocCurveDisplay.from_predictions(
        y_test, y_proba,
        name=model_name,
        color='steelblue' if 'Logistic' in model_name else 'darkorange'
    )
    plt.plot([0, 1], [0, 1], 'k--', label='Random (AUC=0.5)')
    plt.title(f'{model_name} — ROC Curve', fontsize=14)
    plt.legend()
    plt.tight_layout()

    filename = model_name.lower().replace(' ', '_')
    save_path = f'outputs/plots/roc_curve_{filename}.png'
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    plt.show()
    logger.info(f"Saved: {save_path}")


def plot_confusion_matrix(
    y_test,
    y_pred,
    model_name: str = "model"
) -> None:
    """
    Plot confusion matrix for a single model.

    Reading the matrix:
        Top-left     : True Negatives  (correctly predicted low risk)
        Top-right    : False Positives (low risk predicted as high risk)
        Bottom-left  : False Negatives (HIGH RISK MISSED — most costly)
        Bottom-right : True Positives  (correctly predicted high risk)

    For Bati Bank:
        False Negatives = high risk customers approved for BNPL
        → they default → bank loses money
        → minimize this at all costs → optimize Recall

    Parameters
    ----------
    y_test     : actual labels
    y_pred     : predicted labels
    model_name : model name for title and filename
    """
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(6, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=['Low Risk', 'High Risk'],
        yticklabels=['Low Risk', 'High Risk']
    )
    plt.title(f'{model_name} — Confusion Matrix', fontsize=14)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()

    filename = model_name.lower().replace(' ', '_')
    save_path = f'outputs/plots/confusion_matrix_{filename}.png'
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    plt.show()
    logger.info(f"Saved: {save_path}")

    # print key numbers explicitly
    tn, fp, fn, tp = cm.ravel()
    print(f"True Negatives  (correct low risk) : {tn}")
    print(f"False Positives (wrong high risk)  : {fp}")
    print(f"False Negatives (missed high risk) : {fn} ← most costly")
    print(f"True Positives  (correct high risk): {tp}")


def plot_feature_importance(
    model,
    feature_names: list,
    top_n: int = 15
) -> None:
    """
    Plot XGBoost feature importance — top N features.

    Feature importance shows which features the model
    relied on most when making decisions.

    High importance = model splits on this feature often
    Low importance  = model rarely uses this feature

    Parameters
    ----------
    model        : fitted XGBClassifier
    feature_names: list of feature names from X_train.columns
    top_n        : number of top features to show (default 15)
    """
    importance = pd.DataFrame({
        'feature'   : feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        x='importance',
        y='feature',
        data=importance.head(top_n),
        color='steelblue'
    )
    plt.title(f'XGBoost Feature Importance — Top {top_n}', fontsize=14)
    plt.xlabel('Importance Score')
    plt.ylabel('Feature')
    plt.tight_layout()

    save_path = 'outputs/plots/feature_importance.png'
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    plt.show()
    logger.info(f"Saved: {save_path}")

    print(f"\nTop {top_n} features:")
    print(importance.head(top_n).to_string(index=False))


def plot_model_comparison(
    lr_metrics: dict,
    xgb_metrics: dict
) -> None:
    """
    Bar chart comparing Logistic Regression vs XGBoost
    across all 4 metrics side by side.

    Makes the improvement from LR to XGBoost immediately visible.
    Use this chart in your README and dashboard.
    """
    metrics = ['auc', 'f1', 'precision', 'recall']
    lr_vals  = [lr_metrics[m]  for m in metrics]
    xgb_vals = [xgb_metrics[m] for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width/2, lr_vals,  width, label='Logistic Regression',
           color='steelblue')
    ax.bar(x + width/2, xgb_vals, width, label='XGBoost',
           color='darkorange')

    ax.set_ylabel('Score')
    ax.set_title('Model Comparison — Logistic Regression vs XGBoost',
                 fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in metrics])
    ax.set_ylim(0.8, 1.05)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save_path = 'outputs/plots/model_comparison.png'
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    plt.show()
    logger.info(f"Saved: {save_path}")