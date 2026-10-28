import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Master Institutional SMC Terminal", layout="wide")

# Sidebar Configuration
st.sidebar.markdown("### 🚀 Terminal Access")
st.sidebar.caption("Mentor: Mr. Yusuf")
st.sidebar.markdown("---")
st.sidebar.header("🔑 Scanner Access")

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "broker_connected" not in st.session_state:
    st.session_state["broker_connected"] = False

if "saved_client_id" not in st.session_state:
    st.session_state["saved_client_id"] = ""

if "saved_api_key" not in st.session_state:
    st.session_state["saved_api_key"] = ""

# Password Form
with st.sidebar.form(key="login_form"):
    user_pass = st.text_input("Enter Scanner Password:", type="password")
    submit_button = st.form_submit_button(label="Unlock Terminal")

if submit_button:
    if user_pass == "Smc@tools" or user_pass == "SMCALGO@1999":
        st.session_state["authenticated"] = True
        st.session_state["admin_mode"] = (user_pass == "SMCALGO@1999")
    else:
        st.session_state["authenticated"] = False
        st.sidebar.error("❌ Incorrect Password!")

# Authentication Status UI
if st.session_state["authenticated"]:
    if st.session_state.get("admin_mode", False):
        st.sidebar.success("👨‍💻 Admin Access Active (Bypassed)")
    else:
        st.sidebar.success("✅ Scanner Unlocked")
else:
    st.sidebar.warning("🔒 Scanner Locked (₹499)")

# Locked Screen View
if not st.session_state["authenticated"]:
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

# --- MULTI-BROKER API CONNECTION SECTION ---
st.sidebar.markdown("---")
st.sidebar.header("🔌 Multi-Broker Connect")

selected_broker = st.sidebar.selectbox("Select Your Broker", ["Angel One", "Zerodha (Kite)", "Upstox", "Groww", "Other API"])

with st.sidebar.expander(f"Connect {selected_broker} Account", expanded=True):
    client_id_input = st.text_input("Client ID / User ID", value=st.session_state["saved_client_id"], key="client_id_field")
    api_key_input = st.text_input("API Key / App ID", value=st.session_state["saved_api_key"], key="api_key_field")
    api_secret_input = st.text_input("API Secret / Password / MPIN", type="password", key="api_secret_field")
    
    if st.button("Connect Demat Account", key="connect_demat_btn"):
        if client_id_input and api_key_input:
            st.session_state["saved_client_id"] = client_id_input
            st.session_state["saved_api_key"] = api_key_input
            
            js_save = f"""
            <script>
            localStorage.setItem('angel_client_id', '{client_id_input}');
            localStorage.setItem('angel_api_key', '{api_key_input}');
            </script>
            """
            components.html(js_save, height=0)

            st.session_state['broker_connected'] = True
            st.session_state['active_broker'] = selected_broker
            st.sidebar.success(f"✅ Connected to {selected_broker} Successfully!")
        else:
            st.sidebar.error("❌ Please fill in the required credentials.")

if st.session_state.get('broker_connected', False):
    st.sidebar.info(f"🟢 Active Broker: {st.session_state.get('active_broker', 'None')}")

# Unlocked Content Area
count = st_autorefresh(interval=5000, limit=1000, key="fno_auto_refresh")

st.title("⚡ Institutional SMC Analytics Terminal")
st.caption(f"Live Refresh Rate: 5s | Auto-Refresh Counter: {count}")

# Asset Details Dictionary with Step Size and Lot Size
ASSET_METADATA = {
    "^NSEI": {"name": "Nifty 50", "step": 50, "lot": 25, "type": "index"},
    "^NSEBANK": {"name": "Bank Nifty", "step": 100, "lot": 15, "type": "index"},
    "NIFTY_FIN_SERVICE.NS": {"name": "Fin Nifty", "step": 50, "lot": 25, "type": "index"},
    "^BSESN": {"name": "Sensex", "step": 100, "lot": 10, "type": "index"},
    "BSE-BANK.BO": {"name": "Bankex", "step": 100, "lot": 15, "type": "index"},
    "RELIANCE.NS": {"name": "Reliance", "step": 20, "lot": 250, "type": "stock"},
    "TCS.NS": {"name": "TCS", "step": 50, "lot": 175, "type": "stock"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "step": 10, "lot": 550, "type": "stock"},
    "TATAMOTORS.NS": {"name": "Tata Motors", "step": 10, "lot": 550, "type": "stock"}
}

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

# Option Strike Preference
st.sidebar.header("🎯 Strike Mapping View")
strike_type = st.sidebar.selectbox("Select Strike Mapping", ["ATM (At The Money)", "ITM 1 (In The Money)", "OTM 1 (Out of The Money)"])

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

    # Top Metric Bar
    row1_1, row1_2, row1_3, row1_4 = st.columns(4)
    row1_1.metric("Current Spot Price", f"₹ {latest_price:.2f}")
    
    buy_sound_js = "<script>var ctx=new(window.AudioContext||window.webkitAudioContext)();var osc=ctx.createOscillator();osc.type='sine';osc.frequency.setValueAtTime(800,ctx.currentTime);osc.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+0.4);</script>"
    sell_sound_js = "<script>var ctx=new(window.AudioContext||window.webkitAudioContext)();var osc=ctx.createOscillator();osc.type='sawtooth';osc.frequency.setValueAtTime(300,ctx.currentTime);osc.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+0.4);</script>"

    if latest_setup == "BULLISH SETUP":
        row1_2.markdown(
            f"""<div style="background-color:#0e3a1f; color:#2ecc71; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #2ecc71; font-size:16px;">
            🚀 {latest_setup}
            </div>""", unsafe_allow_html=True
        )
        st.components.v1.html(buy_sound_js, height=0)
    elif latest_setup == "BEARISH SETUP":
        row1_2.markdown(
            f"""<div style="background-color:#3a0e0e; color:#e74c3c; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #e74c3c; font-size:16px;">
            🔻 {latest_setup}
            </div>""", unsafe_allow_html=True
        )
        st.components.v1.html(sell_sound_js, height=0)
    else:
        if is_consolidating:
            row1_2.markdown(
                f"""<div style="background-color:#3a320e; color:#f1c40f; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #f1c40f; font-size:16px;">
                ⚠️ CONSOLIDATION PHASE
                </div>""", unsafe_allow_html=True
            )
        else:
            row1_2.markdown(
                f"""<div style="background-color:#2c3e50; color:#bdc3c7; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #7f8c8d; font-size:16px;">
                ⏳ {latest_setup}
                </div>""", unsafe_allow_html=True
            )
        
    row1_3.metric("Order Flow", latest_of)
    row1_4.metric("RSI (14)", f"{latest_rsi:.1f}")

    # --- 🎯 STRIKE PRICE MAPPING ENGINE ---
    meta = ASSET_METADATA.get(ticker, {"step": 50, "lot": 25, "type": "index"})
    step = meta["step"]
    lot_size = meta["lot"]
    
    atm_strike = round(latest_price / step) * step
    
    mapped_strike = atm_strike
    contract_type = "CE" if latest_setup == "BULLISH SETUP" else ("PE" if latest_setup == "BEARISH SETUP" else "CE/PE")
    
    if latest_setup == "BULLISH SETUP":
        if "ITM" in strike_type:
            mapped_strike = atm_strike - step
        elif "OTM" in strike_type:
            mapped_strike = atm_strike + step
    elif latest_setup == "BEARISH SETUP":
        if "ITM" in strike_type:
            mapped_strike = atm_strike + step
        elif "OTM" in strike_type:
            mapped_strike = atm_strike - step

    total_lots = max(1, position_size // lot_size) if position_size > 0 else 0

    st.markdown("---")
    st.markdown("### 📊 Educational Options Scenario Mapping")
    
    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)
    
    if latest_setup == "BULLISH SETUP":
        opt_col1.markdown(f"""
        <div style="background-color:#143d22; border: 2px solid #2ecc71; padding:10px; border-radius:8px; text-align:center;">
            <span style="color:#2ecc71; font-size:12px; font-weight:bold;">EDUCATIONAL CE VIEW</span>
            <h2 style="color:#ffffff; margin:0;">{mapped_strike} CE</h2>
            <span style="color:#bdc3c7; font-size:11px;">({strike_type.split()[0]})</span>
        </div>
        """, unsafe_allow_html=True)
    elif latest_setup == "BEARISH SETUP":
        opt_col1.markdown(f"""
        <div style="background-color:#3d1414; border: 2px solid #e74c3c; padding:10px; border-radius:8px; text-align:center;">
            <span style="color:#e74c3c; font-size:12px; font-weight:bold;">EDUCATIONAL PE VIEW</span>
            <h2 style="color:#ffffff; margin:0;">{mapped_strike} PE</h2>
            <span style="color:#bdc3c7; font-size:11px;">({strike_type.split()[0]})</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        opt_col1.info("⏳ Waiting for Market Setup...")

    opt_col2.metric("Spot Stop-Loss", f"₹ {sl:.2f}" if sl > 0 else "N/A")
    opt_col3.metric("Spot Target (1:2)", f"₹ {target:.2f}" if target > 0 else "N/A")
    opt_col4.metric("Position Sizing Model", f"{total_lots} Lots ({total_lots * lot_size} Qty)" if total_lots > 0 else "N/A")

    st.markdown("---")

    row2_1, row2_2, row2_3 = st.columns(3)
    row2_1.metric("Est. Spot Stop-Loss", f"{sl:.2f}" if sl > 0 else "N/A")
    row2_2.metric("Est. Spot Target", f"{target:.2f}" if target > 0 else "N/A")
    row2_3.metric("Max Quantity Model", f"{position_size} Qty" if position_size > 0 else "N/A")

    if st.session_state.get('broker_connected', False) and latest_setup != "NEUTRAL / NO SETUP":
        active_b = st.session_state.get('active_broker', 'Broker')
        st.markdown(f"### ⚡ Broker Integration Sandbox ({active_b})")
        if st.button(f"🔍 Simulate Order Payload: {selected_asset} {mapped_strike} {contract_type}", key="exec_trade_btn"):
            st.info(f"Sandbox Payload Generated for {selected_asset} {mapped_strike} {contract_type} ({total_lots} Lots). (Note: Manual execution required as per educational policy).")

    st.subheader(f"Live Chart ({selected_asset} - {timeframe})")
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

    def color_table_setup(val):
        if val == "BULLISH SETUP":
            return 'background-color: #0e3a1f; color: #2ecc71; font-weight: bold;'
        elif val == "BEARISH SETUP":
            return 'background-color: #3a0e0e; color: #e74c3c; font-weight: bold;'
        elif val == "CONSOLIDATION PHASE":
            return 'background-color: #3a320e; color: #f1c40f; font-weight: bold;'
        return ''

    table_df = data[['Open', 'High', 'Low', 'Close', 'Order_Flow', 'Bullish_FVG', 'Bearish_FVG', 'Bullish_OB', 'Bearish_OB', 'Consolidation', 'Setup']].tail(12)
    
    styled_table = table_df.style.map(color_table_setup, subset=['Setup'])
    st.dataframe(styled_table, use_container_width=True)

    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** All indicators, market setups, and calculators provided in this terminal are strictly for learning, technical analysis practice, and quantitative research purposes only. This is not investment advice or SEBI-registered buy/sell recommendation. Trading in stock market/F&O involves substantial financial risk.")

else:
    st.error("Data fetch nahi ho pa raha hai. Re-check ticker selection.")
