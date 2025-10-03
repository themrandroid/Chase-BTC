from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import datetime
import traceback
import os

from prediction.prediction import PredictionEngine
from pipeline.data_pipeline import (
    fetch_raw_data,
    build_features
)
from backtest.backtest import backtest_from_probabilities

# router = APIRouter()
# Load recent features
features_path = "data/features/features_labeled.parquet"
FEATURES_FILE = Path(features_path)

# --- FastAPI Init ---
app = FastAPI(title="Chase BTC API", version="1.0")

# --- Response Schemas ---
class PredictResponse(BaseModel):
    timestamp: str
    signal: str
    probability: float
    confidence: float
    stop_loss: float
    take_profit: float
    model_version: str

class ErrorResponse(BaseModel):
    error: str

class Metrics(BaseModel):
    sharpe: float
    max_drawdown: float
    cumulative_return: float
    final_equity: float
    total_trades: int
    win_rate_pct: Optional[float] = None
    avg_profit_per_closed_trade: Optional[float] = None

class EquityPoint(BaseModel):
    date: str
    strategy: float  # or equity if you prefer naming consistency
    buy_and_hold: float


class BacktestResponse(BaseModel):
    metrics: Metrics
    equity_curve: List[EquityPoint]
    trades: List[Dict[str, Any]]  # each trade can have variable keys like date_idx, action, price, size_asset, drawdown
    raws: Dict[str, Any]

# --- Home Endpoint ---
@app.get("/", response_model=dict)
def home():
    return {"message": "Welcome to the Chase BTC Prediction API. Use the /predict endpoint to get trading signals."}

# --- Health-check Endpoint ---
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}

# --- /predict Endpoint ---
@app.get("/predict", response_model=PredictResponse, responses={400: {"model": ErrorResponse}})
def predict(
    threshold: float = Query(0.27, description="BUY signal threshold"),
    sl: float = Query(0.05, description="Stop loss percentage (e.g., 0.05 = 5%)"),
    tp: float = Query(0.30, description="Take profit percentage (e.g., 0.10 = 10%)"),
    days_back: int = Query(60, description="How many days of BTC data to fetch")
):
    """
    Predict BTC trading signal using live market data.
    Dynamically returns action, confidence, SL/TP suggestions, and timestamp.
    """
    try:
        engine = PredictionEngine()
        engine.load_models()

        # Load recent features
        # features_path = "data/features/features_labeled.parquet"
        # if not os.path.exists(features_path):
        #     raise FileNotFoundError(f"Feature file not found: {features_path}")

        df = fetch_raw_data(days_back)
        df = build_features(df)

        # Live prediction
        seq = engine.prepare_sequence(df)
        prob = engine.predict_single_sequence(seq)
        # scale probability to confidence (0–70% → 0–100%)
        adjusted_confidence = min((prob / 0.7) * 100, 100.0)
        signal = engine.generate_signal(prob, threshold)

        print(f"Live Signal -> Action: {signal}, Probability: {prob:.4f}")


        # 6. Build response
        return PredictResponse(
            timestamp=datetime.datetime.utcnow().isoformat(),
            signal=signal,
            probability=round(float(prob), 4),
            confidence=round(adjusted_confidence, 2),
            stop_loss=round(-sl, 4),
            take_profit=round(tp, 4),
            model_version="v1.0"
        )

    except Exception as e:
        # Log traceback for debugging
        print("Prediction Error:", traceback.format_exc())
        return {"error": f"Internal prediction failure: {str(e)}"}, 500
    
# --- /backtest Endpoint ---
@app.get("/backtest", response_model=BacktestResponse)
def run_backtest(
    start_date: str = Query("2015-01-01", description="Backtest start date (YYYY-MM-DD)"),
    end_date: str = Query(datetime.datetime.today().strftime("%Y-%m-%d"), description="Backtest end date (YYYY-MM-DD)"),
    threshold: float = Query(0.27, description="Decision threshold for BUY/HOLD"),
    sl: float = Query(0.05, description="Stop loss %"),
    tp: float = Query(0.3, description="Take profit %"),
    initial_capital: float = Query(1000.0, description="Starting portfolio value"),
    position_size: float = Query(1.0, description="Percentage of capital allocation per signal 0 - 1")
):
    # 1. Load cached features
    if not FEATURES_FILE.exists():
        return {"error": "Features file not found. Please run /update first."}

    df = pd.read_parquet(FEATURES_FILE)
    df.reset_index(inplace=True)  # Ensure timestamp is a column

    # Apply date filter
    if start_date:
        df = df[df["timestamp"] >= start_date]
    if end_date:
        df = df[df["timestamp"] <= end_date]

    if df.empty:
        return {"error": "No data available for the given date range."}

    prices = df["close"].values
    dates = df["timestamp"].astype(str).tolist()

    # 2. Predict probabilities with cached ensemble
    engine = PredictionEngine()
    probs = engine.predict_dataframe(df)
    # 3. Run backtest
    bt_results = backtest_from_probabilities(
        prices=prices,
        y_prob=probs,
        dates=dates,
        threshold=threshold,
        stop_loss=sl,
        take_profit=tp,
        initial_capital=initial_capital,
        position_size=position_size
    )

    # 4. Format response
    response = {
        "metrics": {
            "sharpe": bt_results["metrics"]["sharpe_ratio"],
            "max_drawdown": bt_results["metrics"]["max_drawdown_pct"],
            "cumulative_return": bt_results["metrics"]["cumulative_return"],
            "final_equity": bt_results["metrics"]["final_equity"],
            "total_trades": bt_results["metrics"]["total_trades"],
            "win_rate_pct": bt_results["metrics"]["win_rate_pct"],
            "avg_profit_per_closed_trade": bt_results["metrics"]["avg_profit_per_closed_trade"],
        },
        "equity_curve": bt_results["equity_curve"],
        "trades": bt_results.get("trades", []),
        "raws": bt_results.get("raws", {}),
    }

    return response