# backtest_tab.py

import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import plotly.graph_objects as go


# URLs
# LIVE_API = "https://chase-btc.onrender.com"
# LOCAL_API = "http://localhost:8000"

# def get_api_base():
#     try:
#         # Try live API health endpoint
#         resp = requests.get(f"{LIVE_API}/health", timeout=2)
#         if resp.status_code == 200:
#             return LIVE_API
#     except:
#         pass
#     # Fallback to local API
#     return LOCAL_API

# API_BASE = get_api_base()
API_BASE = "https://murmurlessly-unrequitable-tanna.ngrok-free.dev"

def run_backtest(params):
    try:
        r = requests.get(f"{API_BASE}/backtest", params=params)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching backtest: {e}")
        return None
    
def show_backtest_tab():
    # ----------------------
    # Scenario Settings
    # ----------------------
    with st.expander("⚙️ Scenario Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            initial_equity = st.number_input("Initial Equity ($)", 100.0, 1_000_000.0, 1000.0, step=100.0)
            threshold_scenario = st.slider("Decision Threshold", 0.0, 1.0, 0.27, 0.01)
            position_size = st.number_input("Position Size %", 0.0, 1.0, 1.0, 0.01)
        with col2:
            start_date = st.date_input("Start Date", datetime(2020, 1, 1))
            end_date = st.date_input("End Date", datetime.today())
            sl_scenario = st.number_input("Stop Loss %", 0.0, 1.0, 0.05, 0.01)
            tp_scenario = st.number_input("Take Profit %", 0.0, 2.0, 0.3, 0.01)

    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "threshold": threshold_scenario,
        "sl": sl_scenario,
        "tp": tp_scenario,
        "initial_capital": initial_equity,
        "position_size": position_size
    }
    
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Run Scenario"):
        backtest = run_backtest(params)
        if backtest:
            if backtest:
                metrics = backtest["metrics"]

                # KPI Card
                st.markdown("""
                <div style="background-color:#1E1E1E; padding:20px; border-radius:15px; margin-bottom:20px;">
                    <h3 style="color:#00FF00; text-align:center;">Backtest Metrics</h3>
                """, unsafe_allow_html=True)

                cols = st.columns(4)
                cols[0].markdown(f"""
                    <div style="text-align:center; color:white;">
                        <h4>Final Equity</h4>
                        <h2 style="color:#00FF00;">${metrics['final_equity']:.2f}</h2>
                        <p style="font-size:12px; color:#aaa;">💡 Balance at the end of the test.</p>
                    </div>
                """, unsafe_allow_html=True)

                cols[1].markdown(f"""
                    <div style="text-align:center; color:white;">
                        <h4>Cumulative Return</h4>
                        <h2 style="color:#00FF00;">{metrics['cumulative_return']*100:.2f}%</h2>
                        <p style="font-size:12px; color:#aaa;">💡 Growth/loss over the test period.</p>
                    </div>
                """, unsafe_allow_html=True)

                cols[2].markdown(f"""
                    <div style="text-align:center; color:white;">
                        <h4>Sharpe Ratio</h4>
                        <h2 style="color:#00FF00;">{metrics['sharpe']:.2f}</h2>
                        <p style="font-size:12px; color:#aaa;">💡 Risk-adjusted return (higher is better).</p>
                    </div>
                """, unsafe_allow_html=True)

                cols[3].markdown(f"""
                    <div style="text-align:center; color:white;">
                        <h4>Max Drawdown</h4>
                        <h2 style="color:#00FF00;">{metrics['max_drawdown']*100:.2f}%</h2>
                        <p style="font-size:12px; color:#aaa;">💡 Largest drop from peak balance.</p>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Equity Curve
                equity_df = pd.DataFrame(backtest["equity_curve"])

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=equity_df["date"], y=equity_df["strategy"],
                    mode="lines", name="Strategy",
                    line=dict(color="cyan", width=3)
                ))

                # Trade markers
                trades = backtest.get("trades", [])
                for trade in trades:
                    action = trade["action"]
                    color = "green" if action == "BUY" else "red" if action == "STOP_LOSS" else "yellow"
                    fig.add_trace(go.Scatter(
                        x=[equity_df["date"][trade["date_idx"]]],
                        y=[trade["size_usd"]],
                        mode="markers",
                        marker=dict(size=12, color=color, symbol="triangle-up"),
                        name=action
                    ))

                fig.update_layout(
                    title="📈 Equity Curve",
                    plot_bgcolor="#121212",
                    paper_bgcolor="#121212",
                    font=dict(color="#ffffff"),
                    xaxis_title="Date",
                    yaxis_title="Equity ($)"
                )

                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 This chart shows how your account value changes over time. Spikes = wins, dips = losses.")

                st.success("Backtest updated!")