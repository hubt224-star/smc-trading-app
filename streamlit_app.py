import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import json
import os
import uuid

# Page setup
st.set_page_config(page_title="TradeVortex Institutional Analytics & Education", layout="wide")

# --- COMPLIANCE & SECURITY STYLING ---
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .element-container, .stButton button, .stMetric {
            width: 100% !important;
        }
    }
    .stButton button {
        border-radius: 8px;
        font-weight: bold;
    }
    .compliance-box {
        background-color: #2c220e;
        border: 1.5px solid #f39c12;
        padding: 12px;
        border-radius: 8px;
        font-size: 13px;
        color: #f1c40f;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CLIENT DATABASE SETUP WITH SESSION TRACKING ---
CLIENTS_FILE = "clients.json"

if not os.path.exists(CLIENTS_FILE):
    default_clients = {
        "admin": {"name": "Mr. Yusuf (Admin)", "password": "SMCALGO@1999", "active": True, "admin": True, "active_session": None},
        "9824467482": {"name": "Client User 1", "password": "Smc@tools1990", "active": True, "admin": False, "active_session": None}
    }
    with open(CLIENTS_FILE, "w") as f:
        json.dump(default_clients, f, indent=4)

def load_clients():
    try:
        with open(CLIENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_clients(data):
    with open(CLIENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

clients_db = load_clients()

# Sidebar Configuration
st.sidebar.markdown("### ⚡ TradeVortex School")
st.sidebar.caption("Mentor: Mr. Yusuf | Secure Desk")
st.sidebar.markdown("---")
st.sidebar.header("🔑 Secure Client Login")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "my_session_id" not in st.session_state:
    st.session_state["my_session_id"] = str(uuid.uuid4()) # Unique browser session token

with st.sidebar.form(key="login_form"):
    client_id_input = st.text_input("Client ID / Phone Number:")
    user_pass = st.text_input("Enter Access Password:", type="password")
    submit_button = st.form_submit_button(label="Secure Login")

if submit_button:
    if user_pass == "SMCALGO@1999" and client_id_input.lower() == "admin":
        st.session_state["authenticated"] = True
        st.session_state["admin_mode"] = True
        st.session_state["client_name"] = "Mr. Yusuf (Admin)"
        st.session_state["current_user_id"] = "admin"
    elif client_id_input in clients_db and clients_db[client_id_input]["password"] == user_pass:
        if clients_db[client_id_input].get("active", True):
            # --- SINGLE DEVICE SESSION LOCK LOGIC ---
            current_active_session = clients_db[client_id_input].get("active_session")
            
            # If someone else is logged in and session is active, lock sharing attempt
            # (Optional: allow re-login if same browser refresh, but block simultaneous multi-device)
            clients_db[client_id_input]["active_session"] = st.session_state["my_session_id"]
            save_clients(clients_db)
            
            st.session_state["authenticated"] = True
            st.session_state["admin_mode"] = clients_db[client_id_input].get("admin", False)
            st.session_state["client_name"] = clients_db[client_id_input]["name"]
            st.session_state["current_user_id"] = client_id_input
        else:
            st.session_state["authenticated"] = False
            st.sidebar.error("❌ Subscription expired or account blocked!")
    else:
        st.session_state["authenticated"] = False
        st.sidebar.error("❌ Incorrect ID or Password!")

if st.session_state["authenticated"]:
    # Continuous session validation check
    curr_id = st.session_state.get("current_user_id")
    if curr_id and curr_id != "admin":
        db_fresh = load_clients()
        if curr_id in db_fresh and db_fresh[curr_id].get("active_session") != st.session_state["my_session_id"]:
            st.session_state["authenticated"] = False
            st.warning("⚠️ Your account was logged in from another device. Session terminated for security.")
            st.rerun()

    client_display = st.session_state.get("client_name", "Authorized Learner")
    if st.session_state.get("admin_mode", False):
        st.sidebar.success(f"👨‍💻 Admin Logged In: {client_display}")
        with st.sidebar.expander("🛠️ Client Manager"):
            new_phone = st.text_input("Client Phone", key="np")
            new_name = st.text_input("Client Name", key="nn")
            new_pass = st.text_input("Password", key="nps")
            if st.button("Add Client"):
                if new_phone and new_name and new_pass:
                    clients_db[new_phone] = {"name": new_name, "password": new_pass, "active": True, "admin": False, "active_session": None}
                    save_clients(clients_db)
                    st.success("✅ Added successfully!")
                    st.rerun()
            
            if st.button("Reset All Active Sessions"):
                for k in clients_db:
                    clients_db[k]["active_session"] = None
                save_clients(clients_db)
                st.success("🔄 All sessions cleared!")
    else:
        st.sidebar.success(f"✅ Welcome, {client_display}")
        if st.sidebar.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()
else:
    st.sidebar.warning("🔒 Terminal Locked (Single-Device Protected)")

# Locked View (Offer & Instant Generator)
if not st.session_state["authenticated"]:
    st.title("⚡ TradeVortex SMC Educational Terminal")
    st.error("🔒 Premium Research & Quantitative Scanner Locked.")
    
    st.markdown("""
    <div class="compliance-box">
    <b>Security Notice:</b> Each Client ID is bound to a single active device session. Account sharing will automatically invalidate active sessions. Built strictly for educational research.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Get Instant Access (Secure Single-Device Key)")
    upi_id = "9199786026@ptyes"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa={upi_id}%26pn=Mdaziz%20Shekh%26am=499%26cu=INR"
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(qr_url, caption="Scan via GPay / PhonePe / Paytm (₹4999)")
    with col2:
        st.markdown("""
        **How to get access:**
        1. Scan QR and pay **₹4999**.
        2. Enter your Phone & UTR below to auto-generate your secure single-device key.
        """)
        with st.expander("⚡ Instant Secure Key Generator"):
            claim_ph = st.text_input("Your Phone:")
            claim_utr = st.text_input("UPI UTR / Ref Number:")
            if st.button("Generate Secure Access Key"):
                if len(claim_ph) >= 10 and len(claim_utr) >= 6:
                    gen_pass = f"SMC{claim_utr[-4:]}"
                    clients_db[claim_ph] = {
                        "name": f"Learner {claim_ph[-4:]}", 
                        "password": gen_pass, 
                        "active": True, 
                        "admin": False,
                        "active_session": None
                    }
                    save_clients(clients_db)
                    st.success(f"🎉 Success! Your Password: `{gen_pass}` (Use in Sidebar)")
                else:
                    st.error("Enter valid details.")
        
        wa_url = "https://wa.me/918108433013?text=Bhai%20maine%20payment%20kar%20diya%20hai,%20secure%20access%20do."
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 18px; border:none; border-radius:6px; font-weight:bold; width:100%;">📲 Confirm on WhatsApp</button></a>', unsafe_allow_html=True)
    st.stop()

# --- UNLOCKED TERMINAL AREA ---
count = st_autorefresh(interval=5000, limit=1000, key="refresh_engine")

st.title("⚡ TradeVortex Institutional SMC Research Terminal")
st.markdown("""
<div class="compliance-box">
⚠️ <b>Compliance Disclaimer:</b> Algorithmic outputs for educational study and backtesting only. Not a SEBI advisory.
</div>
""", unsafe_allow_html=True)

# Asset Dictionary
ASSET_DICT = {
    "NSE Index": {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Fin Nifty": "NIFTY_FIN_SERVICE.NS"},
    "BSE Index": {"Sensex": "^BSESN", "Bankex": "BSE-BANK.BO"},
    "Equity Stocks": {"Reliance": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC Bank": "HDFCBANK.NS", "Tata Motors": "TATAMOTORS.NS"}
}

st.sidebar.header("Market Selection")
terminal_mode = st.sidebar.radio("Terminal Mode", ["Single Asset Analysis", "⚡ Bulk Market Scanner"])

if terminal_mode == "Single Asset Analysis":
    category = st.sidebar.selectbox("Category", list(ASSET_DICT.keys()))
    selected_asset = st.sidebar.selectbox("Symbol", list(ASSET_DICT[category].keys()))
    ticker = ASSET_DICT[category][selected_asset]
    timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "1d"], index=1)
    period_map = {"5m": "1mo", "15m": "1mo", "1h": "3mo", "1d": "1y"}

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

        data['Swing_High'] = data['High'].rolling(10).max()
        data['Swing_Low'] = data['Low'].rolling(10).min()
        data['Bullish_FVG'] = data['Low'] > data['High'].shift(2)
        data['Bearish_FVG'] = data['High'] < data['Low'].shift(2)

        data['Setup'] = "NEUTRAL / NO SETUP"
        data.loc[(data['Close'] > data['Swing_High'].shift(1)) & (data['Order_Flow'] == "BULLISH") & (data['RSI'] > 45), 'Setup'] = "BULLISH SETUP"
        data.loc[(data['Close'] < data['Swing_Low'].shift(1)) & (data['Order_Flow'] == "BEARISH") & (data['RSI'] < 55), 'Setup'] = "BEARISH SETUP"
        
        latest_setup = data['Setup'].iloc[-1]
        latest_price = data['Close'].iloc[-1]
        latest_of = data['Order_Flow'].iloc[-1]
        latest_rsi = data['RSI'].iloc[-1]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Spot Price", f"₹ {latest_price:.2f}")
        c2.metric("Algorithm Signal", latest_setup)
        c3.metric("Order Flow", latest_of)
        c4.metric("RSI (14)", f"{latest_rsi:.1f}")

        st.subheader(f"Institutional Price Action Chart ({selected_asset})")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA20'], mode='lines', name='20 EMA', line=dict(color='cyan', width=1)))
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], mode='lines', name='200 EMA', line=dict(color='orange', width=2)))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=10, r=10, t=20, b=10), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Data fetch error.")

else:
    st.subheader("⚡ Live Multi-Asset SMC Bulk Scanner")
    scan_symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Reliance": "RELIANCE.NS", "TCS": "TCS.NS"}
    scan_results = []
    
    for name, sym in scan_symbols.items():
        try:
            df = yf.download(sym, period="5d", interval="15m", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                close_p = df['Close'].iloc[-1]
                scan_results.append({"Symbol": name, "Price (₹)": round(close_p, 2)})
        except:
            continue
    if scan_results:
        st.dataframe(pd.DataFrame(scan_results), use_container_width=True)
