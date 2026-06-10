import pandas as pd
import numpy as np
import logging
import joblib
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import io

from src.api.schemas import (
    CustomerInput,
    PredictionOutput,
    ShapFeature,
    CustomerRecord,
    BatchOutput
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(customer: CustomerInput):
    """
    Score a single customer and return risk prediction + SHAP explanation.

    Called by React when analyst clicks a customer in the queue.
    Predictor and Explainer are loaded once at startup in main.py.
    """
    from src.api.main import predictor, explainer

    # step 1 — convert Pydantic model to dict
    # model_dump() is the Pydantic v2 replacement for .dict()
    customer_dict = customer.model_dump()

    # step 2 — get prediction
    result = predictor.predict(customer_dict)
    score    = result["score"]
    decision = result["decision"]

    # step 3 — risk level for dashboard color coding
    if score >= 0.7:
        risk_level = "High"
    elif score >= 0.4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # step 4 — SHAP explanation
    shap_raw = explainer.explain(customer_dict)
    shap_values = [
        ShapFeature(
            feature  =item["feature"],
            impact   =item["impact"],
            direction=item["direction"]
        )
        for item in shap_raw
    ]

    # step 5 — return structured response
    return PredictionOutput(
        score      =round(score, 4),
        decision   =decision,
        risk_level =risk_level,
        shap_values=shap_values
    )


@router.get("/customers", response_model=List[CustomerRecord])
def get_customers():
    """
    Return all scored customers sorted by risk score descending.

    Called by React on dashboard load to populate the customer queue.
    Loads features, generates predictions for all customers,
    returns sorted list — highest risk first.
    """
    from src.api.main import predictor

    try:
        # load feature table
        features = pd.read_csv("data/processed/features.csv")
        feature_names = joblib.load("outputs/models/feature_names.pkl")

        # prepare X — same columns as training
        drop_cols = [
            c for c in
            ["CustomerId", "Cluster", "is_high_risk", "Recency"]
            if c in features.columns
        ]
        X = features.drop(columns=drop_cols)
        X = X.reindex(columns=feature_names, fill_value=0)

        # score all customers
        scores = predictor.model.predict_proba(X)[:, 1]

        # build response
        results = []
        for i, score in enumerate(scores):
            score = float(score)
            decision   = "Reject" if score > 0.5 else "Approve"
            risk_level = "High" if score >= 0.7 else \
                         "Medium" if score >= 0.4 else "Low"

            customer_id = features["CustomerId"].iloc[i] \
                if "CustomerId" in features.columns \
                else f"Customer_{i}"

            results.append(CustomerRecord(
                customer_id=str(customer_id),
                score      =round(score, 4),
                decision   =decision,
                risk_level =risk_level
            ))

        # sort highest risk first
        results.sort(key=lambda x: x.score, reverse=True)
        logger.info(f"Returned {len(results)} scored customers")
        return results

    except Exception as e:
        logger.error(f"Error in get_customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchOutput)
async def batch_predict(file: UploadFile = File(...)):
    """
    Accept a CSV file of customers and return risk scores for all.

    Called by React batch upload page.
    Analyst uploads CSV → gets back scored table → downloads results.
    """
    from src.api.main import predictor

    try:
        # read uploaded CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        logger.info(f"Batch upload: {len(df)} customers")

        # load feature names
        feature_names = joblib.load("outputs/models/feature_names.pkl")

        # reorder and fill missing columns
        df_features = df.reindex(columns=feature_names, fill_value=0)

        # score all customers
        scores = predictor.model.predict_proba(df_features)[:, 1]

        # build results
        results = []
        for i, score in enumerate(scores):
            score      = float(score)
            decision   = "Reject" if score > 0.5 else "Approve"
            risk_level = "High" if score >= 0.7 else \
                         "Medium" if score >= 0.4 else "Low"

            customer_id = str(df["CustomerId"].iloc[i]) \
                if "CustomerId" in df.columns \
                else f"Customer_{i}"

            results.append(CustomerRecord(
                customer_id=customer_id,
                score      =round(score, 4),
                decision   =decision,
                risk_level =risk_level
            ))

        # sort highest risk first
        results.sort(key=lambda x: x.score, reverse=True)

        high_risk = sum(1 for r in results if r.risk_level == "High")
        low_risk  = len(results) - high_risk

        logger.info(f"Batch complete: {high_risk} high risk, {low_risk} low risk")

        return BatchOutput(
            total_customers=len(results),
            high_risk_count=high_risk,
            low_risk_count =low_risk,
            results        =results
        )

    except Exception as e:
        logger.error(f"Error in batch_predict: {e}")
        raise HTTPException(status_code=500, detail=str(e))