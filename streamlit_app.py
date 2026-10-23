import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. Page Config (MUST BE FIRST STREAMLIT COMMAND)
st.set_page_config(
    page_title="Alpha Trade School - Institutional Terminal",
    page_icon="🚀",
    layout="wide"
)

# ==============================================================================
# 🔐 LOGIN / PASSWORD PROTECTION SYSTEM
# ==============================================================================
APP_PASSWORD = "Mysecretpassword@1990"  # Change password as needed

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("⚡ Alpha Trade School - Institutional Terminal")
    st.subheader("Login Required to Access App")
    
    user_pass = st.text_input("Enter Password:", type="password")
    if st.button("Login"):
        if user_pass == APP_PASSWORD:
            st.session_state.authenticated = True
            st.success("Access Granted!")
            st.rerun()
        else:
            st.error("Incorrect Password!")
    st.stop()  # Stop execution until user logs in

# ==============================================================================
# 🚀 MAIN APP INTERFACE (Shown only after login)
# ==============================================================================

# Auto refresh page every 60 seconds for live updates
st_autorefresh(interval=60000, key="datarefresh")

# ------------------------------------------------------------------------------
# SIDEBAR NAVIGATION & SETTINGS
# ------------------------------------------------------------------------------
with st.sidebar:
    st.title("🚀 Alpha Trade School")
    st.caption("Mentor: Mr. Yusuf")
    
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("---")

    # COMPLIANT EDUCATIONAL BANNER (Replaced direct referral trade push)
    st.info(
        "💡 **Educational Purpose Only**\n\n"
        "Open Demat Account with Angel One using Referral Code: **HONNZY** "
        "to access learning resources & community!"
    )

    st.markdown("---")
    
    st.subheader("Market Selection")
    
    asset_category = st.selectbox(
        "Select Asset Category",
        ["NSE Index / F&O", "MCX Commodities", "US Equities", "Custom Ticker"]
    )
    
    # Dynamic Ticker Mapping
    ticker_dict = {
        "NSE Index / F&O": {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK",
            "Finnifty": "NIFTY_FIN_SERVICE.NS",
            "Sensex": "^BSESN"
        },
        "MCX Commodities": {
            "Gold": "GC=F",
            "Silver": "SI=F",
            "Crude Oil": "CL=F",
            "Natural Gas": "NG=F"
        }
    }
    
    selected_symbol = "Nifty 50"
    symbol_code = "^NSEI"

    if asset_category in ticker_dict:
        selected_symbol = st.selectbox("Select Symbol", list(ticker_dict[asset_category].keys()))
        symbol_code = ticker_dict[asset_category][selected_symbol]
    
    custom_ticker = st.text_input("Custom Yahoo Ticker:", placeholder="e.g. RELIANCE.NS")
    if custom_ticker.strip():
        symbol_code = custom_ticker.strip()
    
    timeframe = st.selectbox(
        "Select Timeframe",
        ["1m", "5m", "15m", "1h", "4h", "1d"],
        index=2
    )

# ------------------------------------------------------------------------------
# DASHBOARD BODY & DATA FETCHING
# ------------------------------------------------------------------------------
st.title(f"📊 Market Analysis: {selected_symbol}")

@st.cache_data(ttl=30)
def load_market_data(ticker, period="7d", interval="15m"):
    try:
        df = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        return None

# Fetching candles
data_period = "7d" if timeframe in ["1m", "5m", "15m"] else "60d"
df = load_market_data(symbol_code, period=data_period, interval=timeframe)

if df is not None and not df.empty:
    # Adding basic Technical Indicators
    df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

    # Plot Candlestick Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='orange', width=1), name="EMA 20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='blue', width=1), name="EMA 50"))
    
    fig.update_layout(
        title=f"{symbol_code} Chart ({timeframe})",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Show Data Table
    with st.expander("View Raw Market Data"):
        st.dataframe(df.tail(20))
else:
    st.warning("Failed to fetch market data or invalid ticker symbol. Please check ticker configuration.")

# ------------------------------------------------------------------------------
# ⚠️ LEGAL COMPLIANCE DISCLAIMER (SEBI NON-REGISTRATION)
# ------------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "⚠️ **Disclaimer:** We are not SEBI registered advisors or research analysts. "
    "All tools, indicators, data, and educational materials provided within this application "
    "are strictly for educational and informational purposes only. "
    "No content here should be construed as financial or trading advice."
)
