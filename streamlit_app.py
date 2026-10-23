import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. Page Config (MUST BE FIRST STREAMLIT COMMAND)
st.set_page_config(page_title="Alpha Trade School | Master Institutional SMC Terminal", layout="wide")

# ==============================================================================
# 🔒 LOGIN / PASSWORD PROTECTION SYSTEM
# ==============================================================================
APP_PASSWORD = "mysecretpassword123"  # <-- Apne hisab se password yahan change karein

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("⚡ Alpha Trade School - Institutional Terminal")
    st.subheader("Login Required to Access App")
    
    user_pass = st.text_input("Enter Password to access:", type="password")
    
    if st.button("Access App"):
        if user_pass == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect Password! Access Denied.")
            
    st.stop()
# ==============================================================================

# 2. 5-Second Auto-Refresh
count = st_autorefresh(interval=5000, limit=1000, key="fno_auto_refresh")

# Sidebar Branding & Controls
st.sidebar.markdown("### 🚀 Alpha Trade School")
st.sidebar.caption("Mentor: Mr. Yusuf")

if st.sidebar.button("🔒 Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")

# Referral Banner for Monetization (COMPLIANT EDUCATIONAL BANNER)
st.sidebar.info(
    "💡 **Educational Purpose Only**\n\n"
    "Open Demat Account with Angel One using Referral Code: **HONNZY** "
    "to access learning resources & community!"
)

st.title("⚡ Alpha Trade School | Institutional SMC Analytics")
st.caption(f"Live Refresh Rate: 5s | Auto-Refresh Counter: {count}")

# 3. Multi-Asset Dictionary
ASSET_DICT = {
    "NSE Index / F&O": {
        "Nifty 50": "^NSEI",
        "Bank Nifty": "^NSEBANK",
        "Fin Nifty": "NIFTY_FIN_SERVICE.NS"
    },
    "BSE Index / F&O": {
        "Sensex": "^BSESN",
        "Bankex": "BSE-BANK.BO"
    },
    "Equity Stocks (NSE)": {
        "Reliance": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Tata Motors": "TATAMOTORS.NS"
    },
    "Commodities (MCX / Global)": {
        "Gold Futures": "GC=F",
        "Silver Futures": "SI=F",
        "Crude Oil Futures": "CL=F",
        "Natural Gas": "NG=F"
    }
}

# 4. Sidebar Controls
st.sidebar.header("Market Selection")
category = st.sidebar.selectbox("Select Asset Category", list(ASSET_DICT.keys()))
selected_asset = st.sidebar.selectbox("Select Symbol", list(ASSET_DICT[category].keys()))
ticker = ASSET_DICT[category][selected_asset]

custom_ticker = st.sidebar.text_input("Custom Yahoo Ticker:", "")
if custom_ticker.strip():
    ticker = custom_ticker.strip()

timeframe = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=1)
period_map = {"5m": "1mo", "15m": "1mo", "1h": "3mo", "1d": "1y"}

st.sidebar.header("Risk Management")
capital = st.sidebar.number_input("Capital (₹/$)", value=100000, step=5000)
risk_per_trade = st.sidebar.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)

# 5. Fetch Market Data
data = yf.download(ticker, period=period_map[timeframe], interval=timeframe)

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'], window=14)
    data['EMA20'] = ta.trend.ema_indicator(data['Close'], window=20)
    data['EMA200'] = ta.trend.ema_indicator(data['Close'], window=200)
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    
    data['Order_Flow'] = "NEUTRAL"
    data.loc[(data['EMA20'] > data['EMA200']) & (data['Close'] > data['EMA200']), 'Order_Flow'] = "BULLISH"
    data.loc[(data['EMA20'] < data['EMA200']) & (data['Close'] < data['EMA200']), 'Order_Flow'] = "BEARISH"

    data['Pivot_High'] =
