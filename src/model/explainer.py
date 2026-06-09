import shap
import joblib
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class Explainer:
    """
    Loads SHAP TreeExplainer once at startup.
    Used by FastAPI to explain every prediction.

    Why explain predictions:
        Banks are legally required to explain credit decisions.
        SHAP shows exactly which features drove each decision
        and by how much — satisfying regulatory requirements.

    Why TreeExplainer:
        TreeExplainer is specifically optimized for tree-based
        models like XGBoost. It is exact and fast — unlike
        KernelExplainer which approximates and is very slow.
    """

    def __init__(
        self,
        model_path: str = "outputs/models/xgboost_model.pkl",
        features_path: str = "outputs/models/feature_names.pkl"
    ):
        """
        Load model and create SHAP explainer once at startup.
        """
        self.model = joblib.load(model_path)
        self.feature_names = joblib.load(features_path)
        self.explainer = shap.TreeExplainer(self.model)

        logger.info(f"Model loaded: {model_path}")
        logger.info(f"SHAP TreeExplainer created")
        logger.info(f"Features: {len(self.feature_names)}")

    def explain(self, customer_dict: dict) -> list:
        """
        Compute SHAP explanation for a single customer.

        SHAP values explained:
            Positive value = pushes prediction toward HIGH RISK
            Negative value = pushes prediction toward LOW RISK
            Larger absolute value = stronger influence

        Parameters
        ----------
        customer_dict : dict of feature name → value

        Returns
        -------
        list of top 4 features sorted by absolute impact:
            [
                {
                    'feature'  : 'velocity_last_30_days',
                    'impact'   : 0.42,
                    'direction': 'increases risk'
                },
                ...
            ]
        """
        # step 1 — convert dict to DataFrame
        df = pd.DataFrame([customer_dict])

        # step 2 — reorder and fill missing columns
        df = df.reindex(columns=self.feature_names, fill_value=0)

        # step 3 — compute SHAP values
        # shap_values shape: (1, n_features)
        # shap_values[0] = array of one value per feature for this customer
        shap_values = self.explainer.shap_values(df)
        values = shap_values[0]

        # step 4 — pair feature names with SHAP values
        explanation = list(zip(self.feature_names, values))

        # step 5 — sort by absolute impact (strongest first)
        explanation = sorted(
            explanation,
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # step 6 — return top 4 with direction label
        top_4 = [
            {
                "feature"  : feat,
                "impact"   : round(float(val), 4),
                "direction": "increases risk" if val > 0 else "decreases risk"
            }
            for feat, val in explanation[:4]
        ]

        logger.info(f"Top feature: {top_4[0]['feature']} "
                    f"impact={top_4[0]['impact']}")
        return top_4