from pydantic import BaseModel
from typing import List


class CustomerInput(BaseModel):
    """
    Input schema for POST /predict endpoint.
    Defines exactly what data React must send.
    Pydantic validates automatically — wrong type = clear error.
    """
    Frequency             : float
    Monetary              : float
    avg_hour              : float
    avg_day_of_week       : float
    weekend_rate          : float
    transaction_month     : float
    std_amount            : float
    max_amount            : float
    min_amount            : float
    log_monetary          : float
    reversal_rate         : float
    unique_products       : float
    unique_providers      : float
    avg_daily_transactions: float
    monetary_per_transaction: float
    negative_amount_count : float
    positive_amount_sum   : float
    velocity_last_30_days : float
    recency_frequency_ratio: float


class ShapFeature(BaseModel):
    """Single SHAP feature explanation."""
    feature  : str
    impact   : float
    direction: str


class PredictionOutput(BaseModel):
    """
    Output schema for POST /predict endpoint.
    Defines exactly what FastAPI sends back to React.
    """
    score      : float
    decision   : str
    risk_level : str
    shap_values: List[ShapFeature]


class CustomerRecord(BaseModel):
    """Single customer record for GET /customers endpoint."""
    customer_id: str
    score      : float
    decision   : str
    risk_level : str


class BatchOutput(BaseModel):
    """Output schema for POST /batch endpoint."""
    total_customers: int
    high_risk_count: int
    low_risk_count : int
    results        : List[CustomerRecord]