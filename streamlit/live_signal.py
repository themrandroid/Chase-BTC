# live_signal.py
import requests
import streamlit as st

# URLs
LIVE_API = "https://chase-btc.onrender.com"
LOCAL_API = "http://localhost:8000"

def get_api_base():
    try:
        # Try live API health endpoint
        resp = requests.get(f"{LIVE_API}/health", timeout=2)
        if resp.status_code == 200:
            return LIVE_API
    except:
        pass
    # Fallback to local API
    return LOCAL_API

# API_BASE = get_api_base()
API_BASE = "https://murmurlessly-unrequitable-tanna.ngrok-free.dev"

@st.cache_data(ttl=60*60*24)
def fetch_prediction(threshold: float = 0.27):
    """
    Fetch prediction from the API with a given threshold.
    Returns a dict with 'signal' and 'probability'.
    """
    try:
        r = requests.get(f"{API_BASE}/predict", params={"threshold": threshold,
                                                        "sl": 0.05, "tp": 0.30, "days_back": 60})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching prediction: {e}")
        return None

def display_prediction_card(prediction: dict):
    """
    Display a single card with the BUY/SELL signal and the confidence score.
    """
    if not prediction:
        st.warning("No prediction available.")
        return

    signal = prediction["signal"]
    score = prediction["confidence"]
    confidence =  score if signal == "🟢BUY" else 100 - score # convert to %
    color = "green" if signal == "🟢BUY" else "red"

    st.markdown("#### Today's Signal")

    st.markdown(
        f"""
        <div style="
            border:2px solid {color};
            border-radius:20px;
            padding:12px;
            text-align:center;
            width:350px;
            margin:auto;
            background-color:#1E1E1E;
        ">
            <h1 style='color:{color}; font-size:75px; margin:0;'>{signal}</h1>
            <p style='color:#FFFFFF; font-size:28px; margin:0px;'>Confidence: {confidence:.1f}%</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")