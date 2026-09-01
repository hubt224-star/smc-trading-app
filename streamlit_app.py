import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Advanced SMC Terminal", layout="wide")

# 5-second auto refresh
count = st_autorefresh(interval=5000, limit=1000, key="fno_auto_refresh")

st.title("Advanced SMC Trading Terminal (Multi-Asset)")
st.caption(f"Live Refresh: 5s | Refresh Count: {count}")

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

st.sidebar.header("Market Selection")
category = st.sidebar.selectbox("Select Asset Category", list(ASSET_DICT.keys()))
selected_asset = st.sidebar.selectbox("Select Symbol", list(ASSET_DICT[category].keys()))
ticker = ASSET_DICT[category][selected_asset]

custom_ticker = st.sidebar.text_input("Custom Yahoo Ticker:", "")
if custom_ticker.strip():
    ticker = custom_ticker.strip()

timeframe = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=0)
period_map = {"5m": "5d", "15m": "5d", "1h": "1mo", "1d": "1y"}

data = yf.download(ticker, period=period_map[timeframe], interval=timeframe)

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Technical Indicators
    data['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'], window=14)
    data['EMA200'] = ta.trend.ema_indicator(data['Close'], window=200)
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['Vol_MA'] = data['Volume'].rolling(window=20).mean()
    
    data['Pivot_High'] = data['High'].rolling(window=5).max()
    data['Pivot_Low'] = data['Low'].rolling(window=5).min()
    
    # Enhanced SMC + RSI + Volume Signal Logic
    data['Signal'] = "NO TRADE ZONE"
    
    buy_cond = (data['Close'] > data['Pivot_High'].shift(1)) & (data['Close'] > data['EMA200']) & (data['RSI'] > 50)
    sell_cond = (data['Close'] < data['Pivot_Low'].shift(1)) & (data['Close'] < data['EMA200']) & (data['RSI'] < 50)
    
    data.loc[buy_cond, 'Signal'] = "BUY (CE)"
    data.loc[sell_cond, 'Signal'] = "SELL (PE)"
    
    latest_signal = data['Signal'].iloc[-1]
    latest_price = data['Close'].iloc[-1]
    latest_atr = data['ATR'].iloc[-1]
    latest_rsi = data['RSI'].iloc[-1]

    # Target & Stop Loss Calculation
    if latest_signal == "BUY (CE)":
        sl = latest_price - (1.5 * latest_atr)
        target = latest_price + (3.0 * latest_atr)
    elif latest_signal == "SELL (PE)":
        sl = latest_price + (1.5 * latest_atr)
        target = latest_price - (3.0 * latest_atr)
    else:
        sl, target = 0.0, 0.0

    # Top Dashboard Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Current Price", f"₹ / $ {latest_price:.2f}")
    
    if latest_signal == "BUY (CE)":
        col2.success(f"**{latest_signal}**")
        st.components.v1.html("<audio autoplay><source src='https://www.soundjay.com/buttons/sounds/button-3.mp3' type='audio/mpeg'></audio>", height=0)
    elif latest_signal == "SELL (PE)":
        col2.error(f"**{latest_signal}**")
        st.components.v1.html("<audio autoplay><source src='https://www.soundjay.com/buttons/sounds/button-10.mp3' type='audio/mpeg'></audio>", height=0)
    else:
        col2.warning(f"**{latest_signal}**")
        
    col3.metric("RSI (14)", f"{latest_rsi:.1f}")
    col4.metric("Est. Stop-Loss", f"{sl:.2f}" if sl > 0 else "N/A")
    col5.metric("Target (1:2)", f"{target:.2f}" if target > 0 else "N/A")

    # Interactive Chart with SL and Target Lines
    st.subheader(f"Live Chart & Levels ({selected_asset})")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], mode='lines', name='200 EMA Trend Filter', line=dict(color='orange', width=2)))
    
    if latest_signal != "NO TRADE ZONE":
        fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text="Stop Loss")
        fig.add_hline(y=target, line_dash="dash", line_color="green", annotation_text="Target")

    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Data Table
    st.subheader("Live Signals Data")
    def color_signals(val):
        if val == "BUY (CE)":
            return 'background-color: #28a745; color: white; font-weight: bold;'
        elif val == "SELL (PE)":
            return 'background-color: #dc3545; color: white; font-weight: bold;'
        else:
            return 'background-color: #6c757d; color: white;'

    st.dataframe(data[['Open', 'High', 'Low', 'Close', 'RSI', 'ATR', 'Signal']].tail(10).style.map(color_signals, subset=['Signal']))
else:
    st.error("Data fetch nahi ho pa raha hai. Valid Ticker select karein.")
