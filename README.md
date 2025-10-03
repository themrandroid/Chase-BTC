# ChaseBTC

ChaseBTC is an end-to-end Bitcoin trading signal system that leverages advanced machine learning models for predictive trading. It comes with a REST API, a Streamlit frontend for live signal visualization and scenario backtesting, and a Telegram bot for daily notifications. The project is fully containerized with Docker for easy deployment.


## Features

- **Machine Learning Models**
  - LSTM, GRU, Conv1D architectures
  - Ensembles (Averaging)
  - Multi-horizon returns and technical indicators as features

- **Signal Generation & Backtesting**
  - Generates BUY/HOLD signals
  - Backtesting with configurable Stop-Loss (SL), Take-Profit (TP), and fees
  - Risk metrics: Sharpe Ratio, Max Drawdown, Final Equity, Cumulative Returns

- **API**
  - `/` — Home
  - `/health` — API status check
  - `/predict` — Returns live trading signal and probability
  - `/backtest` — Returns backtesting metrics, equity curve, and trade history

- **Streamlit Frontend**
  - Live signal display with confidence score
  - Scenario-based backtesting with adjustable parameters
  - Dark mode and interactive charts

- **Telegram Bot**
  - `/start` — Subscribe to daily signals
  - `/signal` — Get today's prediction
  - `/backtest` — Run personalized backtest
  - `/config` — Configure trading preferences
  - `/learn` — Learn trading terms

- **Dockerized Deployment**
  - Containerized API, frontend, and bot for reproducibility
