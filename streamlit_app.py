import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. Page Config (MUST BE FIRST STREAMLIT COMMAND)
st.set_page_config(page_title="Master Institutional SMC Terminal", layout="wide")

# ==============================================================================
# 🔒 LOGIN / PASSWORD PROTECTION SYSTEM
# ==============================================================================
APP_PASSWORD = "mysecretpassword123"  # <-- Apne hisab se password yahan change karein

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Master Institutional SMC Terminal")
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

# Sidebar me Logout button
if st.sidebar.button("🔒 Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.title("⚡ Master Institutional SMC Terminal")
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

# 4. Sidebar Controls (Fixed to 15m Timeframe)
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

    data['Pivot_High'] = data['High'].rolling(window=5).max()
    data['Pivot_Low'] = data['Low'].rolling(window=5).min()

    data['Bullish_FVG'] = (data['Low'] > data['High'].shift(2))
    data['Bearish_FVG'] = (data['High'] < data['Low'].shift(2))

    data['Bullish_OB'] = (data['Close'].shift(1) < data['Open'].shift(1)) & (data['Close'] > data['Pivot_High'].shift(1))
    data['Bearish_OB'] = (data['Close'].shift(1) > data['Open'].shift(1)) & (data['Close'] < data['Pivot_Low'].shift(1))

    price_range = (data['High'].rolling(10).max() - data['Low'].rolling(10).min()) / data['Close']
    data['Consolidation'] = price_range < 0.002

    data['Signal'] = "NO TRADE ZONE"
    
    buy_cond = ((data['Close'] > data['Pivot_High'].shift(1)) | data['Bullish_FVG']) & (data['Order_Flow'] == "BULLISH") & (data['RSI'] > 45) & (~data['Consolidation'])
    sell_cond = ((data['Close'] < data['Pivot_Low'].shift(1)) | data['Bearish_FVG']) & (data['Order_Flow'] == "BEARISH") & (data['RSI'] < 55) & (~data['Consolidation'])
    
    data.loc[buy_cond, 'Signal'] = "BUY (CE)"
    data.loc[sell_cond, 'Signal'] = "SELL (PE)"
    
    latest_signal = data['Signal'].iloc[-1]
    latest_price = data['Close'].iloc[-1]
    latest_atr = data['ATR'].iloc[-1]
    latest_rsi = data['RSI'].iloc[-1]
    latest_of = data['Order_Flow'].iloc[-1]
    is_consolidating = data['Consolidation'].iloc[-1]

    if latest_signal == "BUY (CE)":
        sl = latest_price - (1.5 * latest_atr)
        target = latest_price + (3.0 * latest_atr)
        risk_amount = (capital * risk_per_trade) / 100
        stop_loss_points = abs(latest_price - sl)
        position_size = int(risk_amount / stop_loss_points) if stop_loss_points > 0 else 0
    elif latest_signal == "SELL (PE)":
        sl = latest_price + (1.5 * latest_atr)
        target = latest_price - (3.0 * latest_atr)
        risk_amount = (capital * risk_per_trade) / 100
        stop_loss_points = abs(latest_price - sl)
        position_size = int(risk_amount / stop_loss_points) if stop_loss_points > 0 else 0
    else:
        sl, target, position_size = 0.0, 0.0, 0

    row1_1, row1_2, row1_3, row1_4 = st.columns(4)
    row1_1.metric("Current Price", f"₹ {latest_price:.2f}")
    
    buy_sound_js = "<script>var ctx=new(window.AudioContext||window.webkitAudioContext)();var osc=ctx.createOscillator();osc.type='sine';osc.frequency.setValueAtTime(800,ctx.currentTime);osc.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+0.4);</script>"
    sell_sound_js = "<script>var ctx=new(window.AudioContext||window.webkitAudioContext)();var osc=ctx.createOscillator();osc.type='sawtooth';osc.frequency.setValueAtTime(300,ctx.currentTime);osc.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+0.4);</script>"

    if latest_signal == "BUY (CE)":
        row1_2.success(f"**SIGNAL: {latest_signal}**")
        st.components.v1.html(buy_sound_js, height=0)
    elif latest_signal == "SELL (PE)":
        row1_2.error(f"**SIGNAL: {latest_signal}**")
        st.components.v1.html(sell_sound_js, height=0)
    else:
        if is_consolidating:
            row1_2.warning("**CONSOLIDATION PHASE**")
        else:
            row1_2.warning(f"**SIGNAL: {latest_signal}**")
        
    row1_3.metric("Order Flow", latest_of)
    row1_4.metric("RSI (14)", f"{latest_rsi:.1f}")

    row2_1, row2_2, row2_3 = st.columns(3)
    row2_1.metric("Est. Stop-Loss", f"{sl:.2f}" if sl > 0 else "N/A")
    row2_2.metric("Target (1:2)", f"{target:.2f}" if target > 0 else "N/A")
    row2_3.metric("Rec. Quantity", f"{position_size} Qty" if position_size > 0 else "N/A")

    st.subheader(f"Live Chart ({selected_asset} - 15m)")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['EMA20'], mode='lines', name='20 EMA', line=dict(color='cyan', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['EMA200'], mode='lines', name='200 EMA Filter', line=dict(color='orange', width=2)
    ))
    
    if latest_signal != "NO TRADE ZONE":
        fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text="Stop Loss")
        fig.add_hline(y=target, line_dash="dash", line_color="green", annotation_text="Target")

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=480,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Live Market SMC Analytics Table")
    
    def color_signals(val):
        if val == "BUY (CE)":
            return 'background-color: #28a745; color: white; font-weight: bold;'
        elif val == "SELL (PE)":
            return 'background-color: #dc3545; color: white; font-weight: bold;'
        else:
            return 'background-color: #6c757d; color: white;'

    st.dataframe(
        data[['Open', 'High', 'Low', 'Close', 'Order_Flow', 'Bullish_FVG', 'Bearish_FVG', 'Bullish_OB', 'Bearish_OB', 'Consolidation', 'Signal']]
        .tail(12)
        .style.map(color_signals, subset=['Signal'])
    )

else:
    st.error("Data fetch nahi ho pa raha hai. Re-check ticker selection.")
