import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.model.predictor import Predictor
from src.model.explainer import Explainer

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Create FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title      ="Bati Bank Credit Risk API",
    description="AI-powered BNPL credit scoring for unbanked customers",
    version    ="1.0.0"
)

# ─────────────────────────────────────────────
# CORS — allows React frontend to call this API
# Without this, browser blocks all requests
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://192.168.3.113:3000",
    "https://bati-bank-credit.vercel.app",
    "https://bati-bank-api-production.up.railway.app",

], # React dev server
    allow_methods    =["*"],
    allow_headers    =["*"],
    allow_credentials=True
)

# ─────────────────────────────────────────────
# Load model and explainer ONCE at startup
# Why here and not in routes:
#   Loading inside a route = reloads on every request
#   Loading here = loads once, reused for all requests
#   500 requests/min with route loading = 500 model loads = crash
# ─────────────────────────────────────────────
logger.info("Loading Predictor and Explainer...")
predictor = Predictor()
explainer = Explainer()
logger.info("Models loaded successfully")

# ─────────────────────────────────────────────
# Register routes
# ─────────────────────────────────────────────
app.include_router(router)


# ─────────────────────────────────────────────
# Health check endpoint
# Used by Docker and deployment to verify API is running
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "XGBoost", "version": "1.0.0"}


@app.get("/")
def root():
    return {
        "message"  : "Bati Bank Credit Risk API",
        "docs"     : "/docs",
        "endpoints": ["/predict", "/customers", "/batch", "/health"]
    }