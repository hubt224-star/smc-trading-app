import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import json
import os
import requests
import uuid
import urllib.parse
from datetime import datetime, timedelta, timezone

# Page setup
st.set_page_config(page_title="Master Institutional SMC Terminal Pro", layout="wide")

# --- MOBILE-FIRST & CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .element-container, .stButton button, .stMetric {
            width: 100% !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        /* Fix Table Overlap on Mobile */
        .dataframe {
            font-size: 11px !important;
        }
    }
    .stButton button {
        border-radius: 8px;
        font-weight: bold;
    }
    .metric-box {
        background-color: #1a1c23;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #2d313e;
        text-align: center;
    }
    .confluence-badge-green {
        background-color: #0e3a1f; color: #2ecc71; padding: 6px 12px; border-radius: 6px; text-align: center; font-weight: bold; border: 1px solid #2ecc71;
    }
    .confluence-badge-red {
        background-color: #3a0e0e; color: #e74c3c; padding: 6px 12px; border-radius: 6px; text-align: center; font-weight: bold; border: 1px solid #e74c3c;
    }
    </style>
""", unsafe_allow_html=True)

def color_table_setup(val):
    if val == "BULLISH STUDY ZONE":
        return 'background-color: #0e3a1f; color: #2ecc71; font-weight: bold;'
    elif val == "BEARISH STUDY ZONE":
        return 'background-color: #3a0e0e; color: #e74c3c; font-weight: bold;'
    elif val == "CONSOLIDATION PHASE":
        return 'background-color: #3a320e; color: #f1c40f; font-weight: bold;'
    return ''

# --- UNIQUE CLIENT LOGIN DATABASE SETUP (1-MONTH AUTO-EXPIRY + LIFETIME + ONE-TIME CLAIM LOCK + CLEAN DELETE) ---
CLIENTS_FILE = "clients.json"
CLAIMS_HISTORY_FILE = "claimed_keys_history.json"
ONE_MONTH_DAYS = 30

def now_utc():
    return datetime.now(timezone.utc)

def iso_now():
    return now_utc().isoformat()

def is_lifetime_plan(plan_text):
    p = str(plan_text or "").lower()
    return "lifetime" in p or "life" in p

def compute_expiry_for_plan(plan_text, from_iso=None):
    if is_lifetime_plan(plan_text):
        return None
    base_dt = now_utc()
    if from_iso:
        try:
            base_dt = datetime.fromisoformat(str(from_iso))
            if base_dt.tzinfo is None:
                base_dt = base_dt.replace(tzinfo=timezone.utc)
        except Exception:
            base_dt = now_utc()
    return (base_dt + timedelta(days=ONE_MONTH_DAYS)).isoformat()

def format_expiry_badge(rec):
    plan = rec.get("plan", "")
    if is_lifetime_plan(plan):
        return "♾️ Lifetime (Active)"
    exp_str = rec.get("expires_at")
    if not exp_str:
        return "⏳ 30 Days"
    try:
        exp_dt = datetime.fromisoformat(str(exp_str))
        if exp_dt.tzinfo is None:
            exp_dt = exp_dt.replace(tzinfo=timezone.utc)
        rem = exp_dt - now_utc()
        if rem.total_seconds() <= 0:
            return "❌ Expired"
        days_left = rem.days
        date_txt = exp_dt.strftime("%d %b %Y")
        return f"📅 {days_left}d left ({date_txt})"
    except Exception:
        return "⏳ 30 Days"

def normalize_client_id(raw_id):
    cleaned = "".join(str(raw_id or "").split()).strip()
    if cleaned.lower() == "admin":
        return "admin"
    digits = "".join(ch for ch in cleaned if ch.isdigit())
    if len(digits) >= 10:
        return digits[-10:]
    return cleaned

def normalize_utr(raw_utr):
    return "".join(ch for ch in str(raw_utr or "").strip().upper() if ch.isalnum())

def load_claims_history():
    default_hist = {"phones": [], "utrs": []}
    hist = {"phones": [], "utrs": []}

    if "runtime_claims_history" in st.session_state and isinstance(st.session_state["runtime_claims_history"], dict):
        hist["phones"].extend(st.session_state["runtime_claims_history"].get("phones", []))
        hist["utrs"].extend(st.session_state["runtime_claims_history"].get("utrs", []))

    if os.path.exists(CLAIMS_HISTORY_FILE):
        try:
            with open(CLAIMS_HISTORY_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                hist["phones"].extend(raw.get("phones", []))
                hist["utrs"].extend(raw.get("utrs", []))
        except Exception:
            pass

    hist["phones"] = sorted({normalize_client_id(p) for p in hist["phones"] if normalize_client_id(p)})
    hist["utrs"] = sorted({normalize_utr(u) for u in hist["utrs"] if normalize_utr(u)})
    st.session_state["runtime_claims_history"] = hist
    return hist if (hist["phones"] or hist["utrs"]) else default_hist

def save_claims_history(hist):
    cleaned = {
        "phones": sorted({normalize_client_id(p) for p in (hist or {}).get("phones", []) if normalize_client_id(p)}),
        "utrs": sorted({normalize_utr(u) for u in (hist or {}).get("utrs", []) if normalize_utr(u)}),
    }
    st.session_state["runtime_claims_history"] = cleaned
    try:
        with open(CLAIMS_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=4)
    except Exception:
        pass
    return cleaned

def get_deleted_ids():
    deleted = set()
    if "runtime_deleted_ids" in st.session_state and isinstance(st.session_state["runtime_deleted_ids"], (list, set)):
        for x in st.session_state["runtime_deleted_ids"]:
            nx = normalize_client_id(x)
            if nx and nx != "admin":
                deleted.add(nx)
    if os.path.exists(CLIENTS_FILE):
        try:
            with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict) and isinstance(raw.get("_deleted_ids"), list):
                for x in raw["_deleted_ids"]:
                    nx = normalize_client_id(x)
                    if nx and nx != "admin":
                        deleted.add(nx)
        except Exception:
            pass
    st.session_state["runtime_deleted_ids"] = sorted(deleted)
    return deleted

def set_deleted_ids(deleted_set):
    cleaned = sorted({normalize_client_id(x) for x in (deleted_set or set()) if normalize_client_id(x) and normalize_client_id(x) != "admin"})
    st.session_state["runtime_deleted_ids"] = cleaned
    return set(cleaned)

def normalize_record(cid, rec):
    rec = dict(rec) if isinstance(rec, dict) else {}
    if cid == "admin":
        rec.setdefault("name", "Mr. Yusuf (Admin)")
        rec.setdefault("password", "SMCALGO@1999")
        rec["plan"] = "Lifetime Plan (Admin)"
        rec["active"] = True
        rec["admin"] = True
        rec["expires_at"] = None
        rec.setdefault("active_session", None)
        return rec

    plan = rec.get("plan", "1 Month Plan (₹9999)")
    created_at = rec.get("created_at") or iso_now()
    expires_at = rec.get("expires_at")

    if not is_lifetime_plan(plan) and not expires_at:
        expires_at = compute_expiry_for_plan(plan, created_at)
    elif is_lifetime_plan(plan):
        expires_at = None

    active = bool(rec.get("active", True))

    if not is_lifetime_plan(plan) and expires_at:
        try:
            exp_dt = datetime.fromisoformat(str(expires_at))
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if now_utc() >= exp_dt:
                active = False
        except Exception:
            pass

    rec["name"] = rec.get("name", cid)
    rec["password"] = str(rec.get("password", "")).strip()
    rec["plan"] = plan
    rec["created_at"] = created_at
    rec["expires_at"] = expires_at
    rec["active"] = active
    rec["admin"] = bool(rec.get("admin", False))
    rec.setdefault("active_session", None)
    return rec

DEFAULT_CLIENTS = {
    "admin": {
        "name": "Mr. Yusuf (Admin)",
        "password": "SMCALGO@1999",
        "plan": "Lifetime Plan (Admin)",
        "created_at": "2026-01-01T00:00:00+00:00",
        "expires_at": None,
        "active": True,
        "admin": True,
        "active_session": None,
    },
    "9824467482": {
        "name": "Client User 1",
        "password": "Smc@tools1990",
        "plan": "Lifetime Plan (₹39999)",
        "created_at": "2026-01-01T00:00:00+00:00",
        "expires_at": None,
        "active": True,
        "admin": False,
        "active_session": None,
    },
}

def sync_to_runtime_cache(data, deleted_set=None):
    st.session_state["runtime_clients_cache"] = json.loads(json.dumps(data, default=str))
    if deleted_set is not None:
        set_deleted_ids(deleted_set)

def save_clients(data, deleted_set=None):
    if deleted_set is None:
        deleted_set = get_deleted_ids()
    else:
        deleted_set = set_deleted_ids(deleted_set)

    cleaned_data = {}
    for k, v in (data or {}).items():
        if k == "_deleted_ids":
            continue
        nk = normalize_client_id(k)
        if nk and nk not in deleted_set:
            cleaned_data[nk] = normalize_record(nk, v)

    cleaned_data["admin"] = normalize_record("admin", cleaned_data.get("admin") or DEFAULT_CLIENTS["admin"])

    sync_to_runtime_cache(cleaned_data, deleted_set)
    try:
        disk_payload = dict(cleaned_data)
        disk_payload["_deleted_ids"] = sorted(deleted_set)
        with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(disk_payload, f, indent=4)
    except Exception:
        pass
    return cleaned_data

def load_clients():
    deleted_set = get_deleted_ids()
    merged = {}

    if "runtime_clients_cache" in st.session_state and isinstance(st.session_state["runtime_clients_cache"], dict):
        for k, v in st.session_state["runtime_clients_cache"].items():
            if k == "_deleted_ids":
                continue
            nk = normalize_client_id(k)
            if nk and nk not in deleted_set:
                merged[nk] = normalize_record(nk, v)

    file_data = {}
    if os.path.exists(CLIENTS_FILE):
        try:
            with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                if isinstance(raw.get("_deleted_ids"), list):
                    for x in raw["_deleted_ids"]:
                        nx = normalize_client_id(x)
                        if nx and nx != "admin":
                            deleted_set.add(nx)
                for k, v in raw.items():
                    if k == "_deleted_ids":
                        continue
                    nk = normalize_client_id(k)
                    if nk and nk not in deleted_set and isinstance(v, dict):
                        file_data[nk] = normalize_record(nk, v)
        except Exception:
            file_data = {}

    deleted_set = set_deleted_ids(deleted_set)

    for nk, rec in file_data.items():
        if nk in deleted_set:
            continue
        if nk not in merged:
            merged[nk] = rec
        else:
            try:
                t_old = datetime.fromisoformat(str(merged[nk].get("created_at", "1970-01-01T00:00:00+00:00")))
                t_new = datetime.fromisoformat(str(rec.get("created_at", "1970-01-01T00:00:00+00:00")))
                if t_old.tzinfo is None:
                    t_old = t_old.replace(tzinfo=timezone.utc)
                if t_new.tzinfo is None:
                    t_new = t_new.replace(tzinfo=timezone.utc)
                if t_new >= t_old:
                    merged[nk] = rec
            except Exception:
                merged[nk] = rec

    try:
        if "clients" in st.secrets and isinstance(st.secrets["clients"], dict):
            for k, v in st.secrets["clients"].items():
                nk = normalize_client_id(k)
                if nk and nk not in deleted_set and nk not in merged and isinstance(v, dict):
                    merged[nk] = normalize_record(nk, v)
    except Exception:
        pass

    for def_k, def_v in DEFAULT_CLIENTS.items():
        if def_k not in deleted_set and def_k not in merged:
            merged[def_k] = normalize_record(def_k, def_v)

    changed = False
    for nk in list(merged.keys()):
        if nk in deleted_set and nk != "admin":
            del merged[nk]
            changed = True
            continue
        norm_rec = normalize_record(nk, merged[nk])
        if norm_rec != merged[nk]:
            merged[nk] = norm_rec
            changed = True

    if not os.path.exists(CLIENTS_FILE) or changed:
        save_clients(merged, deleted_set)
    else:
        sync_to_runtime_cache(merged, deleted_set)

    return merged

clients_db = load_clients()
claims_history = load_claims_history()

# Educational Study Notification Function
def send_telegram_alert(token, chat_id, message):
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

# Sidebar Configuration
st.sidebar.markdown("### 🚀 Terminal Access Pro")
st.sidebar.caption("Mentor: Mr. Yusuf | Educational Use")
st.sidebar.markdown("---")
st.sidebar.header("🔑 Unique Client Login")

# Read persisted session token from URL query params on page refresh
qp = st.query_params
persisted_sid = str(qp.get("sid", "") or "").strip()

# Session State Initialization
defaults = {
    "authenticated": False,
    "admin_mode": False,
    "client_name": "",
    "current_user_id": "",
    "broker_connected": False,
    "saved_client_id": "",
    "saved_api_key": "",
    "last_alert_sent": "",
    "my_session_id": persisted_sid if persisted_sid else str(uuid.uuid4()),
    "admin_status_msg": "",
    "candle_window": 120,
    "session_setup_log": [],
    "logged_setup_keys": [],
    "sound_alerts_enabled": True,
    "quick_override_symbol": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Auto-restore session after browser refresh if sid matches a valid active user/admin
if not st.session_state["authenticated"] and persisted_sid:
    db_restore = load_clients()
    if persisted_sid == "admin_session_" + str(db_restore["admin"].get("password", "SMCALGO@1999")).strip():
        st.session_state["authenticated"] = True
        st.session_state["admin_mode"] = True
        st.session_state["client_name"] = db_restore["admin"].get("name", "Mr. Yusuf (Admin)")
        st.session_state["current_user_id"] = "admin"
        st.session_state["my_session_id"] = persisted_sid
    else:
        for uid_key, u_rec in db_restore.items():
            if uid_key != "admin" and u_rec.get("active", True) and u_rec.get("active_session") == persisted_sid:
                st.session_state["authenticated"] = True
                st.session_state["admin_mode"] = bool(u_rec.get("admin", False))
                st.session_state["client_name"] = u_rec.get("name", uid_key)
                st.session_state["current_user_id"] = uid_key
                st.session_state["my_session_id"] = persisted_sid
                break

# Unique Client Login Form
with st.sidebar.form(key="login_form"):
    client_id_input = st.text_input("Client ID / Phone Number:")
    user_pass = st.text_input("Enter Secret Password:", type="password")
    submit_button = st.form_submit_button(label="Unlock Terminal")

if submit_button:
    cid = normalize_client_id(client_id_input)
    pwd = str(user_pass or "").strip()
    db_fresh = load_clients()

    if cid == "admin" and pwd == str(db_fresh["admin"].get("password", "SMCALGO@1999")).strip():
        admin_sid = "admin_session_" + pwd
        st.session_state["authenticated"] = True
        st.session_state["admin_mode"] = True
        st.session_state["client_name"] = db_fresh["admin"].get("name", "Mr. Yusuf (Admin)")
        st.session_state["current_user_id"] = "admin"
        st.session_state["my_session_id"] = admin_sid
        st.query_params["sid"] = admin_sid
        st.rerun()
    elif cid in db_fresh and str(db_fresh[cid].get("password", "")).strip() == pwd:
        if db_fresh[cid].get("active", True):
            new_sid = st.session_state["my_session_id"] or str(uuid.uuid4())
            db_fresh[cid]["active_session"] = new_sid
            save_clients(db_fresh)
            clients_db = db_fresh

            st.session_state["authenticated"] = True
            st.session_state["admin_mode"] = db_fresh[cid].get("admin", False)
            st.session_state["client_name"] = db_fresh[cid].get("name", cid)
            st.session_state["current_user_id"] = cid
            st.session_state["my_session_id"] = new_sid
            st.query_params["sid"] = new_sid
            st.rerun()
        else:
            st.session_state["authenticated"] = False
            st.sidebar.error("❌ Aapka 1 Month plan expire ho chuka hai ya account block hai! Renew ke liye sampark karein.")
    else:
        st.session_state["authenticated"] = False
        st.sidebar.error("❌ Incorrect Client ID or Password!")

# Authentication Status UI & Session Validation Check
if st.session_state["authenticated"]:
    curr_id = st.session_state.get("current_user_id")
    if curr_id and curr_id != "admin":
        db_fresh = load_clients()
        if curr_id not in db_fresh:
            st.session_state["authenticated"] = False
            if "sid" in st.query_params:
                del st.query_params["sid"]
            st.warning("⚠️ Aapka account remove kar diya gaya hai. Kripya support se sampark karein.")
            st.rerun()
        if not db_fresh[curr_id].get("active", True):
            st.session_state["authenticated"] = False
            if "sid" in st.query_params:
                del st.query_params["sid"]
            st.warning("⚠️ Aapka 1 Month plan expire ho chuka hai. Kripya renewal ke liye sampark karein.")
            st.rerun()
        saved_session = db_fresh[curr_id].get("active_session")
        if saved_session and saved_session != st.session_state["my_session_id"]:
            st.session_state["authenticated"] = False
            if "sid" in st.query_params:
                del st.query_params["sid"]
            st.warning("⚠️ Aapka account kisi aur device par login hua hai. Security ke liye yeh session band kar diya gaya hai.")
            st.rerun()

    client_display = st.session_state.get("client_name", "Authorized User")
    if st.session_state.get("admin_mode", False):
        st.sidebar.success(f"👨‍💻 Admin Logged In: {client_display}")

        with st.sidebar.expander("🛠️ Admin Client Manager", expanded=True):
            if st.session_state.get("admin_status_msg"):
                st.info(st.session_state["admin_status_msg"])

            st.markdown("**Add / Renew Client**")
            new_phone = st.text_input("Client Phone / ID", key="new_client_phone")
            new_name = st.text_input("Client Name", key="new_client_name")
            new_pass = st.text_input("Assign Password", key="new_client_pass")
            new_plan = st.selectbox("Selected Plan", ["1 Month Plan (₹9999)", "Lifetime Plan (₹39999)"], key="new_client_plan")

            if st.button("Add Client to DB"):
                norm_phone = normalize_client_id(new_phone)
                clean_name = str(new_name or "").strip()
                clean_pass = str(new_pass or "").strip()
                if norm_phone and clean_name and clean_pass:
                    deleted_set = get_deleted_ids()
                    deleted_set.discard(norm_phone)
                    set_deleted_ids(deleted_set)

                    db_curr = load_clients()
                    created_ts = iso_now()
                    expiry_ts = compute_expiry_for_plan(new_plan, created_ts)
                    db_curr[norm_phone] = {
                        "name": clean_name,
                        "password": clean_pass,
                        "plan": new_plan,
                        "created_at": created_ts,
                        "expires_at": expiry_ts,
                        "active": True,
                        "admin": False,
                        "active_session": None,
                    }
                    db_curr = save_clients(db_curr, deleted_set)
                    clients_db = db_curr
                    st.session_state["admin_status_msg"] = f"✅ Client {clean_name} ({norm_phone}) [{new_plan}] added!"
                    st.rerun()
                else:
                    st.error("⚠️ Fill all fields!")

            st.markdown("---")
            st.markdown("**📋 Client Directory (Plan Wise)**")
            db_curr = load_clients()
            non_admin_items = [(k, v) for k, v in db_curr.items() if k != "admin"]

            one_month_list = [(k, v) for k, v in non_admin_items if not is_lifetime_plan(v.get("plan", ""))]
            lifetime_list = [(k, v) for k, v in non_admin_items if is_lifetime_plan(v.get("plan", ""))]

            st.caption(f"⏳ 1 Month: **{len(one_month_list)}** | ♾️ Lifetime: **{len(lifetime_list)}**")

            filter_choice = st.radio(
                "Filter Clients:",
                ["All", "1 Month (₹9999)", "Lifetime (₹39999)"],
                horizontal=True,
                key="admin_client_filter"
            )

            if filter_choice == "1 Month (₹9999)":
                filtered_items = one_month_list
            elif filter_choice == "Lifetime (₹39999)":
                filtered_items = lifetime_list
            else:
                filtered_items = non_admin_items

            if filtered_items:
                rows = []
                for cid_key, info in filtered_items:
                    p_type = "♾️ Lifetime" if is_lifetime_plan(info.get("plan", "")) else "⏳ 1 Month"
                    rows.append({
                        "ID": cid_key,
                        "Name": info.get("name", cid_key),
                        "Pass": info.get("password", ""),
                        "Plan": p_type,
                        "Status": format_expiry_badge(info),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.caption("Is category mein koi client nahi hai.")

            st.markdown("---")
            st.markdown("**Remove / Delete Client**")
            if non_admin_items:
                client_options = {}
                for k, v in non_admin_items:
                    tag = "♾️ Lifetime" if is_lifetime_plan(v.get("plan", "")) else "⏳ 1 Month"
                    label = f"{k} — {v.get('name', k)} [{tag}]"
                    client_options[label] = k
                selected_label = st.selectbox("Select Client to Remove", list(client_options.keys()), key="remove_client_select")
                client_to_remove = client_options[selected_label]
                if st.button("Delete Selected Client", key="delete_client_btn"):
                    if client_to_remove and client_to_remove != "admin":
                        db_curr = load_clients()
                        db_curr.pop(client_to_remove, None)
                        deleted_set = get_deleted_ids()
                        deleted_set.add(client_to_remove)
                        db_curr = save_clients(db_curr, deleted_set)
                        clients_db = db_curr
                        st.session_state["admin_status_msg"] = f"🗑️ Client {client_to_remove} permanently deleted!"
                        st.rerun()
            else:
                st.caption("No custom clients found.")

            if st.sidebar.button("Logout Admin"):
                st.session_state["authenticated"] = False
                st.session_state["admin_mode"] = False
                if "sid" in st.query_params:
                    del st.query_params["sid"]
                st.rerun()

        with st.sidebar.expander("📢 Telegram Study Alerts Config"):
            tg_token = st.text_input("Bot Token", key="tg_token_val")
            tg_chat = st.text_input("Chat / Channel ID", key="tg_chat_val")
            st.session_state["tg_token"] = tg_token
            st.session_state["tg_chat"] = tg_chat
    else:
        curr_rec = load_clients().get(curr_id, {})
        st.sidebar.success(f"✅ Welcome, {client_display}")
        st.sidebar.caption(f"Plan: {format_expiry_badge(curr_rec)}")
        if st.sidebar.button("Logout"):
            st.session_state["authenticated"] = False
            if "sid" in st.query_params:
                del st.query_params["sid"]
            st.rerun()
else:
    st.sidebar.warning("🔒 Scanner Locked (1M: ₹9999 | Life: ₹39999)")

# Locked Screen View + Instant Passclaim Sandbox (1 Month ₹9999 / Lifetime ₹39999)
if not st.session_state["authenticated"]:
    st.title("⚡ Institutional SMC Analytics Terminal Pro")
    st.error("🔒 Learning Terminal Locked! 1 Month (₹9999) ya Lifetime (₹39999) educational pass lekar access paayein. *(Educational charting tool only — SEBI-registered tip/advice nahi hai.)*")

    st.markdown("### 🚀 Plans: 1 Month — ₹9999 | Lifetime — ₹39999")

    selected_plan_option = st.radio(
        "Apna Plan Select Karein:",
        ["1 Month Plan — ₹9999", "Lifetime Plan — ₹39999"],
        horizontal=True,
    )
    amount = "9999" if "9999" in selected_plan_option else "39999"
    plan_label = "1 Month" if amount == "9999" else "Lifetime"

    upi_id = "9199786026@ptyes"
    payee_name = "Mdaziz Shekh"

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa={upi_id}%26pn={payee_name}%26am={amount}%26cu=INR"

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.image(qr_url, caption=f"Scan QR for {plan_label} Plan (₹{amount}) — GPay / PhonePe / Paytm / BHIM")

    with col2:
        st.markdown(f"""
        **Selected Plan:** **{plan_label} — ₹{amount}** *(1 Month: ₹9999 | Lifetime: ₹39999 — Educational Access)*

        **Steps to unlock access:**
        1. Scan QR & pay **₹{amount}** for **{plan_label}** educational pass.
        2. Enter your payment UTR / Transaction ID below to instantly generate & claim your password key!
        3. Note: Each ID supports **single-device active session** only. **One-time claim only** — same Phone ya UTR se dubara key generate nahi hogi.
        """)

        with st.expander("⚡ Instant Pass Verification (Auto-Claim)", expanded=True):
            user_claim_phone = st.text_input("Your Mobile Number:")
            user_claim_utr = st.text_input("UPI Transaction Reference / UTR (12 Digits):")
            if st.button("Verify Payment & Claim Key"):
                norm_claim_phone = normalize_client_id(user_claim_phone)
                clean_utr = normalize_utr(user_claim_utr)
                hist_curr = load_claims_history()
                db_curr = load_clients()
                deleted_set = get_deleted_ids()

                if len(norm_claim_phone) < 10 or len(clean_utr) < 6:
                    st.error("⚠️ Enter valid Phone & UTR number!")
                elif norm_claim_phone in hist_curr["phones"] or norm_claim_phone in db_curr or norm_claim_phone in deleted_set:
                    st.error("🚫 Is Mobile Number se key pehle hi generate ho chuki hai! Dubara generate nahi hogi.")
                elif clean_utr in hist_curr["utrs"]:
                    st.error("🚫 Ye UTR Number pehle hi use ho chuka hai! Same UTR se dubara key generate nahi hogi.")
                else:
                    generated_pass = f"SMC{clean_utr[-4:]}"
                    full_plan_name = f"{plan_label} Plan (₹{amount})"
                    created_ts = iso_now()
                    expiry_ts = compute_expiry_for_plan(full_plan_name, created_ts)
                    db_curr[norm_claim_phone] = {
                        "name": f"User {norm_claim_phone[-4:]}",
                        "password": generated_pass,
                        "plan": full_plan_name,
                        "created_at": created_ts,
                        "expires_at": expiry_ts,
                        "active": True,
                        "admin": False,
                        "active_session": None,
                    }
                    db_curr = save_clients(db_curr, deleted_set)
                    clients_db = db_curr

                    hist_curr["phones"].append(norm_claim_phone)
                    hist_curr["utrs"].append(clean_utr)
                    claims_history = save_claims_history(hist_curr)

                    st.success(
                        f"🎉 Verification Success ({plan_label} - ₹{amount})! Your Credentials:\n"
                        f"**Client ID:** `{norm_claim_phone}`\n"
                        f"**Password:** `{generated_pass}`"
                    )

                    wa_success_msg = urllib.parse.quote(
                        f"Bhai maine {plan_label} educational pass ke liye ₹{amount} pay kar diya hai (1M: ₹9999 / Life: ₹39999). Mera Client ID {norm_claim_phone} aur Password {generated_pass} hai."
                    )
                    st.markdown(f'''
                        <a href="https://wa.me/918108433013?text={wa_success_msg}" target="_blank">
                            <button style="background-color:#25D366; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:14px; width:100%; margin-top:10px;">
                                📲 Confirm Key on WhatsApp
                            </button>
                        </a>
                        ''', unsafe_allow_html=True)

        wa_text = urllib.parse.quote(
            f"Bhai maine {plan_label} educational pass ke liye ₹{amount} pay kar diya hai (1 Month: ₹9999 | Lifetime: ₹39999), mera unique scanner password dedo."
        )
        wa_url = f"https://wa.me/918108433013?text={wa_text}"

        st.markdown(f'''
            <a href="{wa_url}" target="_blank">
                <button style="background-color:#25D366; color:white; padding:12px 20px; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:16px; width:100%; margin-top:10px;">
                    📲 Send Screenshot on WhatsApp (₹{amount})
                </button>
            </a>
            ''', unsafe_allow_html=True)

    st.stop()

# --- MULTI-BROKER API CONNECTION SECTION ---
st.sidebar.markdown("---")
st.sidebar.header("🔌 Multi-Broker Connect")

selected_broker = st.sidebar.selectbox("Select Your Broker", ["Angel One", "Zerodha (Kite)", "Upstox", "Groww", "Other API"])

with st.sidebar.expander(f"Connect {selected_broker} Account", expanded=False):
    client_id_input_broker = st.text_input("Client ID / User ID", value=st.session_state["saved_client_id"], key="client_id_field")
    api_key_input = st.text_input("API Key / App ID", value=st.session_state["saved_api_key"], key="api_key_field")
    api_secret_input = st.text_input("API Secret / Password / MPIN", type="password", key="api_secret_field")

    if st.button("Connect Demat Account", key="connect_demat_btn"):
        if client_id_input_broker and api_key_input:
            st.session_state["saved_client_id"] = client_id_input_broker
            st.session_state["saved_api_key"] = api_key_input

            js_save = f"""
            <script>
            localStorage.setItem('angel_client_id', '{client_id_input_broker}');
            localStorage.setItem('angel_api_key', '{api_key_input}');
            </script>
            """
            components.html(js_save, height=0)

            st.session_state['broker_connected'] = True
            st.session_state['active_broker'] = selected_broker
            st.sidebar.success(f"✅ Connected to {selected_broker} Successfully (Study Profile)!")
        else:
            st.sidebar.error("❌ Please fill in the required credentials.")

if st.session_state.get('broker_connected', False):
    st.sidebar.info(f"🟢 Active Broker: {st.session_state.get('active_broker', 'None')}")

# Refresh & Alert Sound Controls
refresh_mode = st.sidebar.selectbox("⏱️ Auto-Refresh Rate", ["15s (Smooth Zoom)", "5s (Fast Live)", "30s", "Off (Manual)"], index=0)
interval_map = {"5s (Fast Live)": 5000, "15s (Smooth Zoom)": 15000, "30s": 30000, "Off (Manual)": 0}
refresh_ms = interval_map.get(refresh_mode, 15000)

st.session_state["sound_alerts_enabled"] = st.sidebar.checkbox(
    "🔊 Study Zone Alert Sound",
    value=bool(st.session_state.get("sound_alerts_enabled", True)),
    key="sound_alert_toggle_cb"
)

# Asset Details Dictionary
ASSET_METADATA = {
    "^NSEI": {"name": "Nifty 50", "step": 50, "lot": 25, "tv_symbol": "NSE:NIFTY"},
    "^NSEBANK": {"name": "Bank Nifty", "step": 100, "lot": 15, "tv_symbol": "NSE:BANKNIFTY"},
    "NIFTY_FIN_SERVICE.NS": {"name": "Fin Nifty", "step": 50, "lot": 25, "tv_symbol": "NSE:FINNIFTY"},
    "^BSESN": {"name": "Sensex", "step": 100, "lot": 10, "tv_symbol": "BSE:SENSEX"},
    "BSE-BANK.BO": {"name": "Bankex", "step": 100, "lot": 15, "tv_symbol": "BSE:BANKEX"},
    "RELIANCE.NS": {"name": "Reliance", "step": 20, "lot": 250, "tv_symbol": "NSE:RELIANCE"},
    "TCS.NS": {"name": "TCS", "step": 50, "lot": 175, "tv_symbol": "NSE:TCS"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "step": 10, "lot": 550, "tv_symbol": "NSE:HDFCBANK"},
    "TATAMOTORS.NS": {"name": "Tata Motors", "step": 10, "lot": 550, "tv_symbol": "NSE:TATAMOTORS"}
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

@st.cache_data(ttl=45, show_spinner=False)
def compute_smc_df(sym, tf, prd):
    df = yf.download(sym, period=prd, interval=tf, progress=False, auto_adjust=False)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna(subset=["Open", "High", "Low", "Close"]).copy()
    if len(df) < 25:
        return pd.DataFrame()

    df["ATR"] = ta.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=14)
    df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["EMA200"] = ta.trend.ema_indicator(df["Close"], window=200)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)

    df["Order_Flow"] = "NEUTRAL"
    df.loc[(df["EMA20"] > df["EMA200"]) & (df["Close"] > df["EMA200"]), "Order_Flow"] = "BULLISH"
    df.loc[(df["EMA20"] < df["EMA200"]) & (df["Close"] < df["EMA200"]), "Order_Flow"] = "BEARISH"

    df["Recent_Swing_High"] = df["High"].rolling(window=10).max()
    df["Recent_Swing_Low"] = df["Low"].rolling(window=10).min()

    prev_sh = df["Recent_Swing_High"].shift(1)
    prev_sl = df["Recent_Swing_Low"].shift(1)

    df["BOS_Bullish"] = df["Close"] > prev_sh
    df["BOS_Bearish"] = df["Close"] < prev_sl

    df["CHoCH_Bullish"] = df["BOS_Bullish"] & (df["Order_Flow"].shift(1) == "BEARISH")
    df["CHoCH_Bearish"] = df["BOS_Bearish"] & (df["Order_Flow"].shift(1) == "BULLISH")

    df["BSL_Sweep"] = (df["High"] > prev_sh) & (df["Close"] < prev_sh)
    df["SSL_Sweep"] = (df["Low"] < prev_sl) & (df["Close"] > prev_sl)

    df["Bullish_FVG"] = (df["Low"] > df["High"].shift(2))
    df["Bearish_FVG"] = (df["High"] < df["Low"].shift(2))

    df["Bullish_OB"] = (df["Close"].shift(1) < df["Open"].shift(1)) & (df["Close"] > prev_sh)
    df["Bearish_OB"] = (df["Close"].shift(1) > df["Open"].shift(1)) & (df["Close"] < prev_sl)

    price_range = (df["High"].rolling(10).max() - df["Low"].rolling(10).min()) / df["Close"]
    df["Consolidation"] = price_range < 0.002

    df["Setup"] = "NEUTRAL / NO STUDY ZONE"
    buy_cond = (df["BOS_Bullish"] | df["Bullish_FVG"]) & (df["Order_Flow"] == "BULLISH") & (df["RSI"] > 45) & (~df["Consolidation"])
    sell_cond = (df["BOS_Bearish"] | df["Bearish_FVG"]) & (df["Order_Flow"] == "BEARISH") & (df["RSI"] < 55) & (~df["Consolidation"])

    df.loc[buy_cond, "Setup"] = "BULLISH STUDY ZONE"
    df.loc[sell_cond, "Setup"] = "BEARISH STUDY ZONE"
    return df

@st.cache_data(ttl=120, show_spinner=False)
def get_pdh_pdl(sym):
    try:
        d_df = yf.download(sym, period="5d", interval="1d", progress=False, auto_adjust=False)
        if d_df is None or d_df.empty or len(d_df) < 2:
            return None, None
        if isinstance(d_df.columns, pd.MultiIndex):
            d_df.columns = d_df.columns.get_level_values(0)
        d_df = d_df.dropna(subset=["High", "Low"])
        if len(d_df) < 2:
            return None, None
        prev_day = d_df.iloc[-2]
        return float(prev_day["High"]), float(prev_day["Low"])
    except Exception:
        return None, None

@st.cache_data(ttl=60, show_spinner=False)
def get_mtf_bias(sym):
    out = {"5m": "NEUTRAL", "15m": "NEUTRAL", "1h": "NEUTRAL"}
    tf_cfg = [("5m", "5d"), ("15m", "10d"), ("1h", "1mo")]
    for tf_name, p_name in tf_cfg:
        d = compute_smc_df(sym, tf_name, p_name)
        if not d.empty:
            out[tf_name] = str(d["Order_Flow"].iloc[-1])
    return out

def get_ist_killzone_label():
    ist_now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    mins = ist_now.hour * 60 + ist_now.minute
    if 555 <= mins <= 630:
        return "🔥 Opening Killzone (09:15-10:30)"
    elif 630 < mins < 810:
        return "💤 Mid-Day Range (10:30-13:30)"
    elif 810 <= mins <= 930:
        return "⚡ Afternoon / Closing Session (13:30-15:30)"
    else:
        return "🌙 Off-Market / After Hours"

def get_candle_eta_label(tf):
    ist_now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    tf_seconds = {"5m": 300, "15m": 900, "1h": 3600, "1d": 86400}.get(tf, 900)
    if tf == "1d":
        return "Daily Bar (Close ~15:30 IST)"
    sec_since_midnight = ist_now.hour * 3600 + ist_now.minute * 60 + ist_now.second
    rem_sec = tf_seconds - (sec_since_midnight % tf_seconds)
    mins_left = rem_sec // 60
    secs_left = rem_sec % 60
    return f"~{mins_left}m {secs_left:02d}s left"

st.sidebar.header("Market Selection")
category = st.sidebar.selectbox("Select Asset Category", list(ASSET_DICT.keys()))
selected_asset = st.sidebar.selectbox("Select Symbol", list(ASSET_DICT[category].keys()))
ticker = ASSET_DICT[category][selected_asset]

custom_ticker = st.sidebar.text_input("Custom Yahoo Ticker:", "")
if custom_ticker.strip():
    ticker = custom_ticker.strip()

timeframe = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=1)
period_map = {"5m": "1mo", "15m": "1mo", "1h": "3mo", "1d": "1y"}

st.sidebar.header("Risk Management (Study Math)")
capital = st.sidebar.number_input("Practice Capital (₹/$)", value=100000, step=5000)
risk_per_trade = st.sidebar.slider("Risk Budget (%)", 0.5, 5.0, 1.0)

st.sidebar.header("🎯 Strike Mapping View (Study)")
strike_type = st.sidebar.selectbox("Select Strike Mapping", ["ATM (At The Money)", "ITM 1 (In The Money)", "OTM 1 (Out of The Money)"])

tv_tf_map = {"5m": "5", "15m": "15", "1h": "60", "1d": "D"}

def render_terminal_body(cycle_count=0):
    active_sym_label = selected_asset
    active_ticker = ticker
    active_category = category

    quick_map = {
        "Nifty 50": ("^NSEI", "NSE Index / F&O"),
        "Bank Nifty": ("^NSEBANK", "NSE Index / F&O"),
        "Fin Nifty": ("NIFTY_FIN_SERVICE.NS", "NSE Index / F&O"),
        "Sensex": ("^BSESN", "BSE Index / F&O"),
        "Gold": ("GC=F", "Commodities (MCX / Global)"),
    }
    q_choice = st.session_state.get("quick_override_symbol")
    if q_choice and q_choice in quick_map:
        active_sym_label = q_choice
        active_ticker, active_category = quick_map[q_choice]

    ist_now_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%H:%M:%S IST")
    candle_eta = get_candle_eta_label(timeframe)

    st.title("⚡ Institutional SMC Analytics Terminal Pro")
    st.caption(f"Sync: **{ist_now_str}**  |  Bar Close: **{candle_eta}**  |  Mode: {refresh_mode}  |  Cycle: {cycle_count}  |  *Educational Chart Study Only*")

    q_cols = st.columns([1, 1, 1, 1, 1, 1.3])
    q_keys = ["Nifty 50", "Bank Nifty", "Fin Nifty", "Sensex", "Gold"]
    for idx, q_name in enumerate(q_keys):
        with q_cols[idx]:
            if st.button(q_name, key=f"quick_sym_{q_name}"):
                st.session_state["quick_override_symbol"] = q_name
                st.rerun()
    with q_cols[5]:
        if st.button("Reset to Sidebar", key="quick_sym_reset"):
            st.session_state["quick_override_symbol"] = None
            st.rerun()

    data = compute_smc_df(active_ticker, timeframe, period_map[timeframe])

    if data.empty:
        st.error("Data fetch nahi ho pa raha hai. Re-check ticker selection.")
        return

    latest_setup = data['Setup'].iloc[-1]
    latest_price = float(data['Close'].iloc[-1])
    latest_atr = float(data['ATR'].iloc[-1]) if pd.notna(data['ATR'].iloc[-1]) else 0.0
    latest_rsi = float(data['RSI'].iloc[-1]) if pd.notna(data['RSI'].iloc[-1]) else 50.0
    latest_of = str(data['Order_Flow'].iloc[-1])
    is_consolidating = bool(data['Consolidation'].iloc[-1])
    bsl_swept = bool(data['BSL_Sweep'].iloc[-1])
    ssl_swept = bool(data['SSL_Sweep'].iloc[-1])
    killzone_txt = get_ist_killzone_label()
    pdh_val, pdl_val = get_pdh_pdl(active_ticker)
    sound_on = bool(st.session_state.get("sound_alerts_enabled", True))

    # Educational Telegram Study Note Dispatcher
    if latest_setup in ["BULLISH STUDY ZONE", "BEARISH STUDY ZONE"] and st.session_state.get("tg_token") and st.session_state.get("tg_chat"):
        alert_key = f"{active_ticker}_{latest_setup}_{data.index[-1]}"
        if st.session_state["last_alert_sent"] != alert_key:
            msg = f"📚 *SMC STUDY ZONE NOTE (Educational)*\n\n📈 *Symbol:* {active_sym_label}\n🧭 *Zone:* {latest_setup}\n💰 *Spot:* ₹{latest_price:.2f}\n📊 *RSI:* {latest_rsi:.1f}\n🕒 *Timeframe:* {timeframe}\n\n_For learning & chart study only — Not SEBI advice_"
            send_telegram_alert(st.session_state["tg_token"], st.session_state["tg_chat"], msg)
            st.session_state["last_alert_sent"] = alert_key

    trail_status = "⚪ Inactive"
    if latest_setup == "BULLISH STUDY ZONE":
        sl = latest_price - (1.5 * latest_atr)
        target = latest_price + (3.0 * latest_atr)
        one_to_one = latest_price + (1.5 * latest_atr)
        if latest_price >= one_to_one:
            sl = latest_price
            trail_status = "🛡️ Breakeven / Trail Ref Active"
        else:
            trail_status = "🎯 Tracking Toward 1:1 Ref"
        risk_amount = (capital * risk_per_trade) / 100
        stop_loss_points = abs(latest_price - sl)
        position_size = int(risk_amount / stop_loss_points) if stop_loss_points > 0 else 0
    elif latest_setup == "BEARISH STUDY ZONE":
        sl = latest_price + (1.5 * latest_atr)
        target = latest_price - (3.0 * latest_atr)
        one_to_one = latest_price - (1.5 * latest_atr)
        if latest_price <= one_to_one:
            sl = latest_price
            trail_status = "🛡️ Breakeven / Trail Ref Active"
        else:
            trail_status = "🎯 Tracking Toward 1:1 Ref"
        risk_amount = (capital * risk_per_trade) / 100
        stop_loss_points = abs(latest_price - sl)
        position_size = int(risk_amount / stop_loss_points) if stop_loss_points > 0 else 0
    else:
        sl, target, position_size = 0.0, 0.0, 0

    if latest_setup in ["BULLISH STUDY ZONE", "BEARISH STUDY ZONE"]:
        setup_sig_key = f"{active_ticker}_{timeframe}_{latest_setup}_{str(data.index[-1])}"
        if setup_sig_key not in st.session_state["logged_setup_keys"]:
            ist_time_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%H:%M:%S")
            st.session_state["logged_setup_keys"].append(setup_sig_key)
            st.session_state["session_setup_log"].insert(0, {
                "Time (IST)": ist_time_str,
                "Asset": active_sym_label,
                "TF": timeframe,
                "Setup": latest_setup,
                "Ref Price": round(latest_price, 2),
                "SL Ref": round(sl, 2),
                "Target Ref": round(target, 2),
                "Trail Ref": trail_status,
            })
            st.session_state["session_setup_log"] = st.session_state["session_setup_log"][:50]

    # Top Metric Bar
    row1_1, row1_2, row1_3, row1_4 = st.columns(4)
    row1_1.metric("Current Spot Price", f"₹ {latest_price:.2f}")

    buy_sound_js = "<script>var ctx=new(window.AudioContext||window.webkitAudioContext)();var osc=ctx.createOscillator();osc.type='sine';osc.frequency.setValueAtTime(800,ctx.currentTime);osc.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+0.4);</script>"
    sell_sound_js = "<script>var ctx=new(window.AudioContext||window.webkitAudioContext)();var osc=ctx.createOscillator();osc.type='sawtooth';osc.frequency.setValueAtTime(300,ctx.currentTime);osc.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+0.4);</script>"

    if latest_setup == "BULLISH STUDY ZONE":
        row1_2.markdown(
            f"""<div style="background-color:#0e3a1f; color:#2ecc71; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #2ecc71; font-size:15px;">
            🚀 {latest_setup}
            </div>""", unsafe_allow_html=True
        )
        if sound_on:
            st.components.v1.html(buy_sound_js, height=0)
    elif latest_setup == "BEARISH STUDY ZONE":
        row1_2.markdown(
            f"""<div style="background-color:#3a0e0e; color:#e74c3c; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #e74c3c; font-size:15px;">
            🔻 {latest_setup}
            </div>""", unsafe_allow_html=True
        )
        if sound_on:
            st.components.v1.html(sell_sound_js, height=0)
    else:
        if is_consolidating:
            row1_2.markdown(
                f"""<div style="background-color:#3a320e; color:#f1c40f; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #f1c40f; font-size:15px;">
                ⚠️ CONSOLIDATION PHASE
                </div>""", unsafe_allow_html=True
            )
        else:
            row1_2.markdown(
                f"""<div style="background-color:#2c3e50; color:#bdc3c7; padding:12px; border-radius:6px; text-align:center; font-weight:bold; border:1.5px solid #7f8c8d; font-size:15px;">
                ⏳ {latest_setup}
                </div>""", unsafe_allow_html=True
            )

    row1_3.metric("Order Flow", latest_of)
    row1_4.metric("RSI (14)", f"{latest_rsi:.1f}")

    pdh_pdl_txt = f"PDH: {pdh_val:.2f} | PDL: {pdl_val:.2f}" if (pdh_val is not None and pdl_val is not None) else "PDH/PDL: N/A"
    sweep_label = "🔴 BSL Swept (High Hunt)" if bsl_swept else ("🟢 SSL Swept (Low Hunt)" if ssl_swept else "⚪ No Active Sweep")
    sound_txt = "🔊 Sound ON" if sound_on else "🔇 Sound Muted"
    st.caption(f"**Session:** {killzone_txt}  |  **Liquidity Sweep:** {sweep_label}  |  **Trail Ref:** {trail_status}  |  **{pdh_pdl_txt}**  |  {sound_txt}")

    # --- 📊 REAL MULTI-TIMEFRAME CONFLUENCE MATRIX ---
    st.markdown("---")
    st.markdown("### 📊 Multi-Timeframe Confluence Grid (Study)")
    mtf_data = get_mtf_bias(active_ticker)
    mtf_5m = mtf_data.get("5m", latest_of)
    mtf_15m = mtf_data.get("15m", latest_of)
    mtf_1h = mtf_data.get("1h", "BULLISH" if latest_price > data['EMA200'].iloc[-1] else "BEARISH")

    if mtf_5m == mtf_15m == mtf_1h and mtf_5m in ["BULLISH", "BEARISH"]:
        st.success(f"🔥 **TRIPLE ALIGNMENT (STUDY):** 5m, 15m & 1h all showing **{mtf_5m}** structure.")

    mtf_cols = st.columns(3)
    with mtf_cols[0]:
        st.markdown(f"**5m Timeframe**<br><div class='{'confluence-badge-green' if mtf_5m=='BULLISH' else 'confluence-badge-red'}'>{mtf_5m}</div>", unsafe_allow_html=True)
    with mtf_cols[1]:
        st.markdown(f"**15m Timeframe**<br><div class='{'confluence-badge-green' if mtf_15m=='BULLISH' else 'confluence-badge-red'}'>{mtf_15m}</div>", unsafe_allow_html=True)
    with mtf_cols[2]:
        st.markdown(f"**1h Timeframe**<br><div class='{'confluence-badge-green' if mtf_1h=='BULLISH' else 'confluence-badge-red'}'>{mtf_1h}</div>", unsafe_allow_html=True)

    # --- 🎯 STRIKE PRICE MAPPING & OPTIONS MATRIX ENGINE (EDUCATIONAL) ---
    meta = ASSET_METADATA.get(active_ticker, {"step": 50, "lot": 25, "tv_symbol": "NSE:NIFTY"})
    step = meta["step"]
    lot_size = meta["lot"]
    tv_symbol = meta["tv_symbol"]

    atm_strike = round(latest_price / step) * step

    mapped_strike = atm_strike
    contract_type = "CE" if latest_setup == "BULLISH STUDY ZONE" else ("PE" if latest_setup == "BEARISH STUDY ZONE" else "CE/PE")

    if latest_setup == "BULLISH STUDY ZONE":
        if "ITM" in strike_type:
            mapped_strike = atm_strike - step
        elif "OTM" in strike_type:
            mapped_strike = atm_strike + step
    elif latest_setup == "BEARISH STUDY ZONE":
        if "ITM" in strike_type:
            mapped_strike = atm_strike + step
        elif "OTM" in strike_type:
            mapped_strike = atm_strike - step

    total_lots = max(1, position_size // lot_size) if position_size > 0 else 0

    st.markdown("---")
    st.markdown("### 📈 Option Strike Concept & Sentiment Heatboard (Study)")

    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)

    est_pcr = round(1.25 if latest_of == "BULLISH" else (0.75 if latest_of == "BEARISH" else 0.98), 2)
    pcr_bias = "Bullish Bias (Study)" if est_pcr > 1.0 else ("Bearish Bias (Study)" if est_pcr < 0.9 else "Neutral")

    if latest_setup == "BULLISH STUDY ZONE":
        opt_col1.markdown(f"""
        <div style="background-color:#143d22; border: 2px solid #2ecc71; padding:10px; border-radius:8px; text-align:center;">
            <span style="color:#2ecc71; font-size:12px; font-weight:bold;">EDUCATIONAL CE CONCEPT</span>
            <h2 style="color:#ffffff; margin:0;">{mapped_strike} CE</h2>
            <span style="color:#bdc3c7; font-size:11px;">({strike_type.split()[0]})</span>
        </div>
        """, unsafe_allow_html=True)
    elif latest_setup == "BEARISH STUDY ZONE":
        opt_col1.markdown(f"""
        <div style="background-color:#3d1414; border: 2px solid #e74c3c; padding:10px; border-radius:8px; text-align:center;">
            <span style="color:#e74c3c; font-size:12px; font-weight:bold;">EDUCATIONAL PE CONCEPT</span>
            <h2 style="color:#ffffff; margin:0;">{mapped_strike} PE</h2>
            <span style="color:#bdc3c7; font-size:11px;">({strike_type.split()[0]})</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        opt_col1.info("⏳ Waiting for Study Zone...")

    opt_col2.metric("Spot SL Ref", f"₹ {sl:.2f}" if sl > 0 else "N/A")
    opt_col3.metric("Spot Target Ref (1:2)", f"₹ {target:.2f}" if target > 0 else "N/A")
    opt_col4.metric("Est. PCR Ratio (Study)", f"{est_pcr}", delta=pcr_bias)

    st.markdown("---")

    row2_1, row2_2, row2_3 = st.columns(3)
    row2_1.metric("Est. Spot SL Ref", f"{sl:.2f}" if sl > 0 else "N/A")
    row2_2.metric("Est. Spot Target Ref", f"{target:.2f}" if target > 0 else "N/A")
    row2_3.metric("Risk Math Qty Model", f"{position_size} Qty ({total_lots} Lots)" if position_size > 0 else "N/A")

    if latest_setup in ["BULLISH STUDY ZONE", "BEARISH STUDY ZONE"]:
        summary_text = (
            f"📚 SMC Study Note (Educational) — {active_sym_label} ({timeframe})\n"
            f"• Zone: {latest_setup} | Order Flow: {latest_of}\n"
            f"• Strike Concept: {mapped_strike} {contract_type} ({strike_type.split()[0]})\n"
            f"• Spot Reference: {latest_price:.2f}\n"
            f"• SL Ref: {sl:.2f} | Target Ref (1:2): {target:.2f}\n"
            f"• Trail Ref: {trail_status}\n"
            f"(Educational study note only — Not SEBI advice)"
        )
        with st.expander("📋 Copy-Ready Study Summary Note", expanded=False):
            st.code(summary_text, language="text")

    if st.session_state.get('broker_connected', False) and latest_setup != "NEUTRAL / NO STUDY ZONE":
        active_b = st.session_state.get('active_broker', 'Broker')
        st.markdown(f"### ⚡ Study Payload Inspector ({active_b})")
        if st.button(f"🔍 Inspect Study Payload: {active_sym_label} {mapped_strike} {contract_type}", key="exec_trade_btn"):
            st.info(f"Educational Study Payload Preview for {active_sym_label} {mapped_strike} {contract_type} ({total_lots} Lots). No live order placed; educational practice only.")

    # --- LIVE CHART ENGINE (ZOOM-LOCKED + CHoCH + LABELED FVG/OB + SWEEP + PDH/PDL) ---
    st.subheader(f"Live Chart ({active_sym_label} - {timeframe})")

    w_cols = st.columns([1, 1, 1, 2])
    with w_cols[0]:
        if st.button("50 Candles", key="win_50_btn"):
            st.session_state["candle_window"] = 50
    with w_cols[1]:
        if st.button("120 Candles", key="win_120_btn"):
            st.session_state["candle_window"] = 120
    with w_cols[2]:
        if st.button("200 Candles", key="win_200_btn"):
            st.session_state["candle_window"] = 200
    with w_cols[3]:
        st.caption(f"Active Window: **Last {st.session_state['candle_window']} Candles**")

    win_n = int(st.session_state.get("candle_window", 120))

    if active_category == "BSE Index / F&O" or active_ticker in ["^BSESN", "BSE-BANK.BO"]:
        st.success("⚡ **BSE Chart View Active:** Streaming via TradingView Engine (Educational Study).")
        tv_html = f"""
        <div class="tradingview-widget-container" style="height:500px;width:100%;">
          <div id="tradingview_bse_chart" style="height:500px;width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "{tv_symbol}",
            "interval": "{tv_tf_map.get(timeframe, '15')}",
            "timezone": "Asia/Kolkata",
            "theme": "dark",
            "style": "1",
            "locale": "in",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_legend": false,
            "save_image": false,
            "container_id": "tradingview_bse_chart"
          }});
          </script>
        </div>
        """
        components.html(tv_html, height=520)
    else:
        chart_df = data.tail(win_n).copy()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=chart_df.index,
            open=chart_df['Open'],
            high=chart_df['High'],
            low=chart_df['Low'],
            close=chart_df['Close'],
            name="Price",
            increasing_line_color="#2ecc71",
            decreasing_line_color="#e74c3c"
        ))
        fig.add_trace(go.Scatter(
            x=chart_df.index, y=chart_df['EMA20'], mode='lines', name='20 EMA', line=dict(color='#00d4ff', width=1.2)
        ))
        fig.add_trace(go.Scatter(
            x=chart_df.index, y=chart_df['EMA200'], mode='lines', name='200 EMA Filter', line=dict(color='#f39c12', width=2)
        ))

        end_x = chart_df.index[-1]

        if pdh_val is not None:
            fig.add_hline(y=pdh_val, line_dash="dot", line_color="#38bdf8", annotation_text=f"PDH ({pdh_val:.2f})", annotation_position="top left")
        if pdl_val is not None:
            fig.add_hline(y=pdl_val, line_dash="dot", line_color="#c084fc", annotation_text=f"PDL ({pdl_val:.2f})", annotation_position="bottom left")

        fvg_boxes = 0
        for idx in range(len(chart_df) - 1, max(-1, len(chart_df) - 35), -1):
            if fvg_boxes >= 3:
                break
            ts = chart_df.index[idx]
            if bool(chart_df['Bullish_FVG'].iloc[idx]) and idx >= 2:
                y0 = float(chart_df['High'].iloc[idx - 2])
                y1 = float(chart_df['Low'].iloc[idx])
                if y1 > y0:
                    fig.add_shape(
                        type="rect", x0=ts, x1=end_x, y0=y0, y1=y1,
                        fillcolor="rgba(46, 204, 113, 0.16)",
                        line=dict(color="rgba(46, 204, 113, 0.55)", width=1, dash="dot")
                    )
                    fig.add_annotation(
                        x=end_x, y=y1, text="Bull FVG", showarrow=False,
                        xanchor="right", yanchor="bottom", font=dict(size=9, color="#2ecc71")
                    )
                    fvg_boxes += 1
            elif bool(chart_df['Bearish_FVG'].iloc[idx]) and idx >= 2:
                y0 = float(chart_df['High'].iloc[idx])
                y1 = float(chart_df['Low'].iloc[idx - 2])
                if y1 > y0:
                    fig.add_shape(
                        type="rect", x0=ts, x1=end_x, y0=y0, y1=y1,
                        fillcolor="rgba(231, 76, 60, 0.16)",
                        line=dict(color="rgba(231, 76, 60, 0.55)", width=1, dash="dot")
                    )
                    fig.add_annotation(
                        x=end_x, y=y1, text="Bear FVG", showarrow=False,
                        xanchor="right", yanchor="bottom", font=dict(size=9, color="#e74c3c")
                    )
                    fvg_boxes += 1

        ob_boxes = 0
        for idx in range(len(chart_df) - 1, max(0, len(chart_df) - 35), -1):
            if ob_boxes >= 2:
                break
            prev_ts = chart_df.index[idx - 1]
            if bool(chart_df['Bullish_OB'].iloc[idx]):
                y0 = float(min(chart_df['Open'].iloc[idx - 1], chart_df['Close'].iloc[idx - 1]))
                y1 = float(max(chart_df['Open'].iloc[idx - 1], chart_df['Close'].iloc[idx - 1]))
                fig.add_shape(
                    type="rect", x0=prev_ts, x1=end_x, y0=y0, y1=y1,
                    fillcolor="rgba(0, 212, 255, 0.14)",
                    line=dict(color="rgba(0, 212, 255, 0.65)", width=1)
                )
                fig.add_annotation(
                    x=prev_ts, y=y1, text="Bull OB", showarrow=False,
                    xanchor="left", yanchor="bottom", font=dict(size=9, color="#00d4ff")
                )
                ob_boxes += 1
            elif bool(chart_df['Bearish_OB'].iloc[idx]):
                y0 = float(min(chart_df['Open'].iloc[idx - 1], chart_df['Close'].iloc[idx - 1]))
                y1 = float(max(chart_df['Open'].iloc[idx - 1], chart_df['Close'].iloc[idx - 1]))
                fig.add_shape(
                    type="rect", x0=prev_ts, x1=end_x, y0=y0, y1=y1,
                    fillcolor="rgba(241, 196, 15, 0.14)",
                    line=dict(color="rgba(241, 196, 15, 0.65)", width=1)
                )
                fig.add_annotation(
                    x=prev_ts, y=y1, text="Bear OB", showarrow=False,
                    xanchor="left", yanchor="bottom", font=dict(size=9, color="#f1c40f")
                )
                ob_boxes += 1

        bos_b_df = chart_df[chart_df['BOS_Bullish'] & (~chart_df['CHoCH_Bullish'])].tail(4)
        if not bos_b_df.empty:
            fig.add_trace(go.Scatter(
                x=bos_b_df.index, y=bos_b_df['High'] * 1.001,
                mode='markers+text', name='BOS Bullish',
                text=['BOS↑'] * len(bos_b_df), textposition='top center',
                textfont=dict(color='#2ecc71', size=10),
                marker=dict(symbol='triangle-up', size=9, color='#2ecc71')
            ))

        bos_s_df = chart_df[chart_df['BOS_Bearish'] & (~chart_df['CHoCH_Bearish'])].tail(4)
        if not bos_s_df.empty:
            fig.add_trace(go.Scatter(
                x=bos_s_df.index, y=bos_s_df['Low'] * 0.999,
                mode='markers+text', name='BOS Bearish',
                text=['BOS↓'] * len(bos_s_df), textposition='bottom center',
                textfont=dict(color='#e74c3c', size=10),
                marker=dict(symbol='triangle-down', size=9, color='#e74c3c')
            ))

        choch_b_df = chart_df[chart_df['CHoCH_Bullish']].tail(3)
        if not choch_b_df.empty:
            fig.add_trace(go.Scatter(
                x=choch_b_df.index, y=choch_b_df['High'] * 1.002,
                mode='markers+text', name='CHoCH Bullish',
                text=['CHoCH↑'] * len(choch_b_df), textposition='top center',
                textfont=dict(color='#a3e635', size=10),
                marker=dict(symbol='diamond', size=9, color='#a3e635')
            ))

        choch_s_df = chart_df[chart_df['CHoCH_Bearish']].tail(3)
        if not choch_s_df.empty:
            fig.add_trace(go.Scatter(
                x=choch_s_df.index, y=choch_s_df['Low'] * 0.998,
                mode='markers+text', name='CHoCH Bearish',
                text=['CHoCH↓'] * len(choch_s_df), textposition='bottom center',
                textfont=dict(color='#fb7185', size=10),
                marker=dict(symbol='diamond', size=9, color='#fb7185')
            ))

        bsl_df = chart_df[chart_df['BSL_Sweep']].tail(3)
        if not bsl_df.empty:
            fig.add_trace(go.Scatter(
                x=bsl_df.index, y=bsl_df['High'] * 1.003,
                mode='markers+text', name='BSL Sweep',
                text=['BSL↑'] * len(bsl_df), textposition='top center',
                textfont=dict(color='#f472b6', size=9),
                marker=dict(symbol='x', size=8, color='#f472b6')
            ))

        ssl_df = chart_df[chart_df['SSL_Sweep']].tail(3)
        if not ssl_df.empty:
            fig.add_trace(go.Scatter(
                x=ssl_df.index, y=ssl_df['Low'] * 0.997,
                mode='markers+text', name='SSL Sweep',
                text=['SSL↓'] * len(ssl_df), textposition='bottom center',
                textfont=dict(color='#34d399', size=9),
                marker=dict(symbol='x', size=8, color='#34d399')
            ))

        if latest_setup != "NEUTRAL / NO STUDY ZONE":
            fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text="SL Ref")
            fig.add_hline(y=target, line_dash="dash", line_color="green", annotation_text="Target Ref")

        fig.update_layout(
            uirevision=f"{active_ticker}_{timeframe}_{win_n}_zoom_lock",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=35, b=10)
        )
        st.plotly_chart(fig, use_container_width=True, key=f"smc_main_chart_{active_ticker}_{timeframe}_{win_n}")

    # --- 📜 SESSION SETUP HISTORY LOG ---
    if st.session_state.get("session_setup_log"):
        st.markdown("---")
        st.subheader("📜 Session Study Log")
        log_df = pd.DataFrame(st.session_state["session_setup_log"])
        st.dataframe(log_df.style.map(color_table_setup, subset=["Setup"]), use_container_width=True, hide_index=True)

        log_c1, log_c2 = st.columns([1, 1])
        with log_c1:
            st.download_button(
                label="⬇️ Download Study Log (CSV)",
                data=log_df.to_csv(index=False).encode("utf-8"),
                file_name=f"smc_study_log_{datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="download_setup_log_csv"
            )
        with log_c2:
            if st.button("🗑️ Clear Session Log", key="clear_setup_log_btn"):
                st.session_state["session_setup_log"] = []
                st.session_state["logged_setup_keys"] = []
                st.rerun()

    # --- 🌐 ALL-MARKET LIVE SMC SCANNER ---
    st.markdown("---")
    st.subheader(f"🌐 All-Market Live SMC Study Scanner ({timeframe})")
    scanner_filter = st.radio(
        "Scanner Filter:",
        ["All", "Active Study Zones Only", "Bullish Study Only", "Bearish Study Only"],
        horizontal=True,
        key="scanner_setup_filter"
    )
    watchlist_items = [
        ("Nifty 50", "^NSEI"),
        ("Bank Nifty", "^NSEBANK"),
        ("Fin Nifty", "NIFTY_FIN_SERVICE.NS"),
        ("Sensex", "^BSESN"),
        ("Bankex", "BSE-BANK.BO"),
        ("Reliance", "RELIANCE.NS"),
        ("TCS", "TCS.NS"),
        ("HDFC Bank", "HDFCBANK.NS"),
        ("Gold Futures", "GC=F"),
        ("Silver Futures", "SI=F"),
        ("Crude Oil", "CL=F"),
    ]
    scan_rows = []
    for sym_label, sym_code in watchlist_items:
        s_df = compute_smc_df(sym_code, timeframe, period_map[timeframe])
        if not s_df.empty:
            s_setup = str(s_df["Setup"].iloc[-1])
            if scanner_filter == "Active Study Zones Only" and s_setup not in ["BULLISH STUDY ZONE", "BEARISH STUDY ZONE"]:
                continue
            if scanner_filter == "Bullish Study Only" and s_setup != "BULLISH STUDY ZONE":
                continue
            if scanner_filter == "Bearish Study Only" and s_setup != "BEARISH STUDY ZONE":
                continue
            scan_rows.append({
                "Asset": sym_label,
                "Price": round(float(s_df["Close"].iloc[-1]), 2),
                "Order Flow": str(s_df["Order_Flow"].iloc[-1]),
                "RSI": round(float(s_df["RSI"].iloc[-1]), 1),
                "Study Zone": s_setup,
            })
    if scan_rows:
        scan_df = pd.DataFrame(scan_rows)
        st.dataframe(scan_df.style.map(color_table_setup, subset=["Study Zone"]), use_container_width=True, hide_index=True)
    else:
        st.info("Selected filter ke mutabik abhi koi matching symbol nahi mila.")

    st.subheader("Live Market SMC Analytics Table")

    table_df = data[['Open', 'High', 'Low', 'Close', 'Order_Flow', 'BOS_Bullish', 'BOS_Bearish', 'CHoCH_Bullish', 'CHoCH_Bearish', 'Bullish_FVG', 'Bearish_FVG', 'Consolidation', 'Setup']].tail(12).copy()
    for col in ['Open', 'High', 'Low', 'Close']:
        if col in table_df.columns:
            table_df[col] = table_df[col].round(2)

    styled_table = table_df.style.map(color_table_setup, subset=['Setup'])
    st.dataframe(styled_table, use_container_width=True)

    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** All indicators, study zones, and calculators provided in this terminal are strictly for learning, technical analysis practice, and educational chart study purposes only. This is not investment advice or SEBI-registered buy/sell recommendation. Trading in stock market/F&O involves substantial financial risk.")

if hasattr(st, "fragment"):
    if refresh_ms > 0:
        @st.fragment(run_every=max(5, refresh_ms // 1000))
        def live_terminal_fragment():
            st.session_state["frag_cycle"] = int(st.session_state.get("frag_cycle", 0)) + 1
            render_terminal_body(st.session_state["frag_cycle"])

        live_terminal_fragment()
    else:
        @st.fragment
        def static_terminal_fragment():
            render_terminal_body(0)

        static_terminal_fragment()
else:
    if refresh_ms > 0:
        count = st_autorefresh(interval=refresh_ms, limit=5000, key="fno_auto_refresh")
    else:
        count = 0
    render_terminal_body(count)
