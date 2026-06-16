import os
import logging
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)


def log_experiment(
    model,
    params: dict,
    metrics: dict,
    artifacts: list = None,
    run_name: str = "experiment"
) -> str:
    """
    Log a single training experiment to MLflow.

    Logs:
        params    — how the model was built (hyperparameters)
        metrics   — how well it performed (AUC, F1, precision, recall)
        model     — the actual trained model object
        artifacts — plot files to attach (optional)

    Why MLflow:
        Without tracking, you run 10 experiments and forget
        which hyperparameters gave the best result.
        MLflow records everything so you can compare runs
        and reproduce any result exactly.

    Parameters
    ----------
    model     : fitted model (LogisticRegression or XGBClassifier)
    params    : dict of hyperparameters
    metrics   : dict of evaluation metrics
    artifacts : list of file paths to attach (plots etc.)
    run_name  : name shown in MLflow UI

    Returns
    -------
    run_id : str — MLflow run ID for reference
    """
    artifacts = artifacts or []

    with mlflow.start_run(run_name=run_name) as run:

        # log how the model was built
        mlflow.log_params(params)
        logger.info(f"Logged params: {params}")

        # log how well it performed
        mlflow.log_metrics(metrics)
        logger.info(f"Logged metrics: {metrics}")

        # log the model object itself
        if isinstance(model, XGBClassifier):
            mlflow.xgboost.log_model(model, run_name)
        else:
            mlflow.sklearn.log_model(model, run_name)
        logger.info(f"Logged model: {type(model).__name__}")

        # log plot files as artifacts
        for artifact_path in artifacts:
            if os.path.exists(artifact_path):
                mlflow.log_artifact(artifact_path)
                logger.info(f"Logged artifact: {artifact_path}")
            else:
                logger.warning(f"Artifact not found: {artifact_path}")

        run_id = run.info.run_id
        logger.info(f"Run complete. Run ID: {run_id}")
        print(f"Logged: {run_name} | Run ID: {run_id}")

    return run_id


def setup_experiment(experiment_name: str = "bati_bank_credit_risk") -> None:
    """
    Set the MLflow experiment name.
    Creates the experiment if it does not exist.
    Call this once at the top of your training notebook.

    Parameters
    ----------
    experiment_name : name shown in MLflow UI
    """
    mlflow.set_experiment(experiment_name)
    logger.info(f"MLflow experiment set: {experiment_name}")
    print(f"MLflow experiment: {experiment_name}")
    print("Run 'mlflow ui' in terminal to view results")


def get_best_run(
    experiment_name: str = "bati_bank_credit_risk",
    metric: str = "auc"
) -> dict:
    """
    Find the best run in an experiment by a given metric.

    Use this after running multiple experiments to find
    which hyperparameters gave the best result.

    Parameters
    ----------
    experiment_name : name of the MLflow experiment
    metric          : metric to rank by (default: auc)

    Returns
    -------
    dict with run_id, params, and metrics of best run
    """
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)

    if experiment is None:
        logger.warning(f"Experiment not found: {experiment_name}")
        return {}

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{metric} DESC"]
    )

    if not runs:
        logger.warning("No runs found")
        return {}

    best = runs[0]
    result = {
        'run_id' : best.info.run_id,
        'params' : best.data.params,
        'metrics': best.data.metrics
    }

    logger.info(f"Best run: {result['run_id']}")
    logger.info(f"Best {metric}: {result['metrics'].get(metric)}")
    print(f"Best run ID : {result['run_id']}")
    print(f"Best {metric.upper()} : {result['metrics'].get(metric)}")

    return result