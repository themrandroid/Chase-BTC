# app.py
import streamlit as st
from live_signal import display_prediction_card, fetch_prediction
from backtest_tab import show_backtest_tab

# ----------------------
# General Config
# ----------------------
st.set_page_config(page_title="Chase BTC Terminal", 
                   layout="wide", 
                   page_icon=":money_with_wings:")

st.markdown("""
<div style="text-align:center; font-size:48px; color:#00FF00;">
        💰<b>ChaseBTC</b>🏃‍♂️ 
</div>
""", unsafe_allow_html=True)

# --- Live Signal ---
prediction = fetch_prediction(threshold=0.27)
display_prediction_card(prediction)

# -- Backtest ----
show_backtest_tab()

# Disclaimer Banner
st.markdown("""
<div style='background-color:#b22222;padding:10px;border-radius:2px;color:white;text-align:center;'>
⚠️ This is a trading simulator. Not financial advice. Use responsibly.
</div>
""", unsafe_allow_html=True)