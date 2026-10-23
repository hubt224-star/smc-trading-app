import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Master Institutional SMC Terminal", layout="wide")

PAID_ACCESS_PASSWORD = "Smc@tools"
MASTER_ADMIN_PASSWORD = "SMCALGO1999"

st.sidebar.markdown("### 🚀 Terminal Access")
st.sidebar.caption("Mentor: Mr. Yusuf")

st.sidebar.markdown("---")
st.sidebar.header("🔑 Scanner Access")
user_pass = st.sidebar.text_input("Enter Scanner Password:", type="password")

is_unlocked = (user_pass == PAID_ACCESS_PASSWORD) or (user_pass == MASTER_ADMIN_PASSWORD)

if is_unlocked:
    if user_pass == MASTER_ADMIN_PASSWORD:
        st.sidebar.success("👨‍💻 Admin Access Active (Bypassed)")
    else:
        st.sidebar.success("✅ Scanner Unlocked")
else:
    st.sidebar.warning("🔒 Scanner Locked (₹499)")

if not is_unlocked:
    st.title("⚡ Institutional SMC Terminal")
    st.error("🔒 Premium Scanner Locked! Subscribe to Get Access.")
    
    st.markdown("### 🚀 Pay ₹499 & Get Instant Password Access")
    
    upi_id = "9199786026@ptyes"
    payee_name = "Mdaziz Shekh"
    amount = "499"
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa={upi_id}%26pn={payee_name}%26am={amount}%26cu=INR"
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.image(qr_url, caption="Scan using GPay / PhonePe / Paytm / BHIM")
        
    with col2:
        st.markdown(f"""
        **Steps to unlock access:**
        1. Scan the QR code using any UPI app.
        2. Pay **₹{amount}**.
        3. Click the button below to send payment screenshot on WhatsApp.
        4. Enter the password received on WhatsApp in the **Sidebar** to unlock!
        """)
        
        wa_text = "Bhai%20maine%20499%20pay%20kar%20diya%20hai,%20scanner%20ka%20password%20dedo."
        wa_url = f"https://wa.me/918108433013?text={wa_text}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank">
                <button style="background-color:#25D366; color:white; padding:12px 20px; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:16px;">
                    📲 Send Screenshot on WhatsApp
                </button>
            </a>
            ''', unsafe_allow_html=True)
            
    st.stop()

count = st_autorefresh(interval=5000, limit=1000, key="fno_auto_refresh")

st.title("⚡ Institutional SMC Analytics Terminal")
st.caption(f"Live Refresh Rate: 5s | Auto-Refresh Counter: {count}")

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

timeframe = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=1)
period_map = {"5m": "1mo", "15m": "1mo", "1h": "3mo", "1d": "1y"}

st.sidebar.header("Risk Management")
capital = st.sidebar.number_input("Capital (₹/$)", value=100000, step=5000)
risk_per_trade = st.sidebar.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)

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

    data['Setup'] = "NEUTRAL / NO SETUP"
    
    buy_cond = ((data['Close'] > data['Pivot_High'].shift(1)) | data['Bullish_FVG']) & (data['Order_Flow'] == "BULLISH") & (data['RSI'] > 45) & (~data['Consolidation'])
    sell_cond = ((data['Close'] < data['Pivot_Low'].shift(1)) | data['Bearish_FVG']) & (data['Order_Flow'] == "BEARISH") & (data['RSI'] < 55) & (~data['Consolidation'])
    
    data.loc[buy_cond, 'Setup'] = "BULLISH SETUP"
    data.loc[sell_cond, 'Setup'] = "BEARISH SETUP"
    
    latest_setup = data['Setup'].iloc[-1]
    latest_price = data['Close'].iloc[-1]
    latest_atr = data['ATR'].iloc[-1]
    latest_rsi = data['RSI'].iloc[-1]
    latest_of = data['Order_Flow'].iloc[-1]
    is_consolidating = data['Consolidation'].iloc[-1]

    if latest_setup == "BULLISH SETUP":
        sl = latest_price - (1.5 * latest_atr)
        target = latest_price + (3.0 * latest_atr)
        risk_amount = (capital * risk_per_trade) / 100
        stop_loss_points = abs(latest_price - sl)
        position_size = int(risk_amount / stop_loss_points) if stop_loss_points > 0 else 0
    elif latest_setup == "BEARISH SETUP":
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

    if latest_setup == "BULLISH SETUP":
        row1_2.success(f"**SETUP: {latest_setup}**")
        st.components.v1.html(buy_sound_js, height=0)
    elif latest_setup == "BEARISH SETUP":
        row1_2.error(f"**SETUP: {latest_setup}**")
        st.components.v1.html(sell_sound_js, height=0)
    else:
        if is_consolidating:
            row1_2.warning("**CONSOLIDATION PHASE**")
        else:
            row1_2.warning(f"**SETUP: {latest_setup}**")
        
    row1_3.metric("Order Flow", latest_of)
    row1_4.metric("RSI (14)", f"{latest_rsi:.1f}")

    row2_1, row2_2, row2_3 = st.columns(3)
    row2_1.metric("Est. Stop-Loss Level", f"{sl:.2f}" if sl > 0 else "N/A")
    row2_2.metric("Target Level (1:2)", f"{target:.2f}" if target > 0 else "N/A")
    row2_3.metric("Max Rec. Quantity", f"{position_size} Qty" if position_size > 0 else "N/A")

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
    
    if latest_setup != "NEUTRAL / NO SETUP":
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

    st.dataframe(
        data[['Open', 'High', 'Low', 'Close', 'Order_Flow', 'Bullish_FVG', 'Bearish_FVG', 'Bullish_OB', 'Bearish_OB', 'Consolidation', 'Setup']]
        .tail(12)
    )

    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** All indicators, market setups, and calculators provided in this terminal are strictly for learning, technical analysis practice, and quantitative research purposes only. This is not investment advice or SEBI-registered buy/sell recommendation. Trading in stock market/F&O involves substantial financial risk.")

else:
    st.error("Data fetch nahi ho pa raha hai. Re-check ticker selection.")
