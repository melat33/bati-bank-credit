import joblib
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class Predictor:
    """
    Loads trained XGBoost model once at startup.
    Used by FastAPI to score customers on every request.

    Why a class and not a function:
        A function would reload the model on every API request.
        500 requests/minute = 500 model loads = very slow.
        A class loads the model ONCE on init and reuses it.
    """

    def __init__(
        self,
        model_path: str = "outputs/models/xgboost_model.pkl",
        features_path: str = "outputs/models/feature_names.pkl"
    ):
        """
        Load model and feature names from disk.
        Called once when FastAPI starts.
        """
        self.model = joblib.load(model_path)
        self.feature_names = joblib.load(features_path)
        logger.info(f"Model loaded from: {model_path}")
        logger.info(f"Features loaded: {len(self.feature_names)} features")

    def predict(self, customer_dict: dict) -> dict:
        """
        Score a single customer and return risk prediction.

        Parameters
        ----------
        customer_dict : dict of feature name → value
            e.g. {'Frequency': 5, 'Monetary': 20000, ...}

        Returns
        -------
        dict with:
            score      : float 0-1 (probability of high risk)
            decision   : 'Approve' or 'Reject'
            risk_level : 'Low', 'Medium', or 'High'
        """
        # step 1 — convert dict to DataFrame
        df = pd.DataFrame([customer_dict])

        # step 2 — reorder and fill missing columns
        # reindex guarantees exact same column order as training
        # fill_value=0 handles any missing features gracefully
        df = df.reindex(columns=self.feature_names, fill_value=0)

        # step 3 — predict probability of high risk (class 1)
        probability = float(self.model.predict_proba(df)[:, 1][0])

        # step 4 — decision rule
        decision = "Reject" if probability > 0.5 else "Approve"

        # step 5 — risk level for dashboard display
        if probability > 0.7:
            risk_level = "High"
        elif probability > 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        result = {
            "score"     : round(probability, 4),
            "decision"  : decision,
            "risk_level": risk_level
        }

        logger.info(f"Prediction: {result}")
        return result