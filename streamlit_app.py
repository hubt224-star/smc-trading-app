import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Multi-Asset SMC Signals", layout="wide")

# Har 5 second (5000 milliseconds) me app auto-refresh hogi
count = st_autorefresh(interval=5000, limit=1000, key="fno_auto_refresh")

st.title("SMC Trading Signals (NSE, BSE, F&O, Commodity)")
st.caption(f"Auto-refresh active (Updates every 5 sec) | Refresh count: {count}")

# Asset Categories
ASSET_DICT = {
    "NSE Index / F&O": {
        "Nifty 50": "^NSEI",
        "Bank Nifty": "^NSEBANK",
        "Fin Nifty": "NIFTY_FIN_SERVICE.NS"
    },
    "Equity Stocks (NSE)": {
        "Reliance": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Tata Motors": "TATAMOTORS.NS"
    },
    "Equity Stocks (BSE)": {
        "Reliance (BSE)": "RELIANCE.BO",
        "TCS (BSE)": "TCS.BO",
        "HDFC Bank (BSE)": "HDFCBANK.BO"
    },
    "Commodities (MCX / Global)": {
        "Gold Futures": "GC=F",
        "Silver Futures": "SI=F",
        "Crude Oil Futures": "CL=F",
        "Natural Gas": "NG=F"
    }
}

# Sidebar Selection
st.sidebar.header("Market Selection")
category = st.sidebar.selectbox("Select Asset Category", list(ASSET_DICT.keys()))
selected_asset = st.sidebar.selectbox("Select Symbol", list(ASSET_DICT[category].keys()))
ticker = ASSET_DICT[category][selected_asset]

# Custom Ticker Option
custom_ticker = st.sidebar.text_input("Or Enter Custom Yahoo Ticker:", "")
if custom_ticker.strip():
    ticker = custom_ticker.strip()

timeframe = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=0)
period_map = {"5m": "5d", "15m": "5d", "1h": "1mo", "1d": "1y"}

# Automatic Data Fetching
data = yf.download(ticker, period=period_map[timeframe], interval=timeframe)

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Technical Indicators
    data['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'], window=14)
    data['Pivot_High'] = data['High'].rolling(window=5).max()
    data['Pivot_Low'] = data['Low'].rolling(window=5).min()
    
    # SMC Signals
    data['Signal'] = "NO TRADE ZONE"
    data.loc[data['Close'] > data['Pivot_High'].shift(1), 'Signal'] = "BUY (CE / LONG)"
    data.loc[data['Close'] < data['Pivot_Low'].shift(1), 'Signal'] = "SELL (PE / SHORT)"
    
    # Metrics Display
    latest_signal = data['Signal'].iloc[-1]
    latest_price = data['Close'].iloc[-1]
    
    col1, col2 = st.columns(2)
    col1.metric("Current Price", f"₹ / $ {latest_price:.2f}")
    col2.metric("Latest Signal", latest_signal)
    
    st.subheader("Live Data & Signals Table")
    st.dataframe(data[['Open', 'High', 'Low', 'Close', 'ATR', 'Signal']].tail(15))
else:
    st.error("Data fetch nahi ho pa raha hai. Valid Ticker select karein.")

