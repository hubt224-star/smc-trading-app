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
    if val == "BULLISH SETUP":
        return 'background-color: #0e3a1f; color: #2ecc71; font-weight: bold;'
    elif val == "BEARISH SETUP":
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

# Telegram Alert Function
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
st.sidebar.caption("Mentor: Mr. Yusuf")
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

        with st.sidebar.expander("📢 Telegram Alerts Config"):
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
    st.title("⚡ Institutional SMC Terminal Pro")
    st.error("🔒 Premium Scanner Locked! 1 Month (₹9999) ya Lifetime (₹39999) plan lekar access paayein.")

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
        **Selected Plan:** **{plan_label} — ₹{amount}** *(1 Month: ₹9999 | Lifetime: ₹39999)*

        **Steps to unlock access:**
        1. Scan QR & pay **₹{amount}** for **{plan_label}** plan.
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
                        f"Bhai maine {plan_label} plan ke liye ₹{amount} pay kar diya hai (1M: ₹9999 / Life: ₹39999). Mera Client ID {norm_claim_phone} aur Password {generated_pass} hai."
                    )
                    st.markdown(f'''
                        <a href="https://wa.me/918108433013?text={wa_success_msg}" target="_blank">
                            <button style="background-color:#25D366; color:white; padding:10px 16px; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:14px; width:100%; margin-top:10px;">
                                📲 Confirm Key on WhatsApp
                            </button>
                        </a>
                        ''', unsafe_allow_html=True)

        wa_text = urllib.parse.quote(
            f"Bhai maine {plan_label} plan ke liye ₹{amount} pay kar diya hai (1 Month: ₹9999 | Lifetime: ₹39999), mera unique scanner password dedo."
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
            st.sidebar.success(f"✅ Connected to {selected_broker} Successfully!")
        else:
            st.sidebar.error("❌ Please fill in the required credentials.")

if st.session_state.get('broker_connected', False):
    st.sidebar.info(f"🟢 Active Broker: {st.session_state.get('active_broker', 'None')}")

# Unlocked Content Area
count = st_autorefresh(interval=5000, limit=1000, key="fno_auto_refresh")

st.title("⚡ Institutional SMC Analytics Terminal Pro")
st.caption(f"Live Refresh Rate: 5s | Auto-Refresh Counter: {count}")

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

    # Liquidity Sweep (wick beyond prior swing high/low with close back inside)
    df["BSL_Sweep"] = (df["High"] > prev_sh) & (df["Close"] < prev_sh)
    df["SSL_Sweep"] = (df["Low"] < prev_sl) & (df["Close"] > prev_sl)

    df["Bullish_FVG"] = (df["Low"] > df["High"].shift(2))
    df["Bearish_FVG"] = (df["High"] < df["Low"].shift(2))

    df["Bullish_OB"] = (df["Close"].shift(1) < df["Open"].shift(1)) & (df["Close"] > prev_sh)
    df["Bearish_OB"] = (df["Close"].shift(1) > df["Open"].shift(1)) & (df["Close"] < prev_sl)

    price_range = (df["High"].rolling(10).max() - df["Low"].rolling(10).min()) / df["Close"]
    df["Consolidation"] = price_range < 0.002

    df["Setup"] = "NEUTRAL / NO SETUP"
    buy_cond = (df["BOS_Bullish"] | df["Bullish_FVG"]) & (df["Order_Flow"] == "BULLISH") & (df["RSI"] > 45) & (~df["Consolidation"])
    sell_cond = (df["BOS_Bearish"] | df["Bearish_FVG"]) & (df["Order_Flow"] == "BEARISH") & (df["RSI"] < 55) & (~df["Consolidation"])

    df.loc[buy_cond, "Setup"] = "BULLISH SETUP"
    df.loc[sell_cond, "Setup"] = "BEARISH SETUP"
    return df

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
    if 555 <= mins <= 630:       # 09:15 - 10:30 IST
        return "🔥 Opening Killzone (09:15-10:30)"
    elif 630 < mins < 810:      # 10:30 - 13:30 IST
        return "💤 Mid-Day Range (10:30-13:30)"
    elif 810 <= mins <= 930:    # 13:30 - 15:30 IST
        return "⚡ Afternoon / Closing Session (13:30-15:30)"
    else:
        return "🌙 Off-Market / After Hours"

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

st.sidebar.header("🎯 Strike Mapping View")
strike_type = st.sidebar.selectbox("Select Strike Mapping", ["ATM (At The Money)", "ITM 1 (In The Money)", "OTM 1 (Out of The Money)"])

tv_tf_map = {"5m": "5", "15m": "15", "1h": "60", "1d": "D"}

data = compute_smc_df(ticker, timeframe, period_map[timeframe])

if not data.empty:
    latest_setup = data['Setup'].iloc[-1]
    latest_price = data['Close'].iloc[-1]
    latest_atr = data['ATR'].iloc[-1]
    latest_rsi = data['RSI'].iloc[-1]
    latest_of = data['Order_Flow'].iloc[-1]
    is_consolidating = data['Consolidation'].iloc[-1]
    bsl_swept = bool(data['BSL_Sweep'].iloc[-1])
    ssl_swept = bool(data['SSL_Sweep'].iloc[-1])
    killzone_txt = get_ist_killzone_label()

    # Automatic Telegram Notification Dispatcher
    if latest_setup in ["BULLISH SETUP", "BEARISH SETUP"] and st.session_state.get("tg_token") and st.session_state.get("tg_chat"):
        alert_key = f"{ticker}_{latest_setup}_{data.index[-1]}"
        if st.session_state["last_alert_sent"] != alert_key:
            msg = f"⚡ *SMC ALERT TRIGGERED*\n\n📈 *Symbol:* {selected_asset}\n🎯 *Setup:* {latest_setup}\n💰 *Price:* ₹{latest_price:.2f}\n📊 *RSI:* {latest_rsi:.1f}\n🕒 *Timeframe:* {timeframe}\n\n_TradeVortex SMC Engine_"
            send_telegram_alert(st.session_state["tg_token"], st.session_state["tg_chat"], msg)
            st.session_state["last_alert_sent"] = alert_key

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

    # Liquidity Sweep & Session Bar
    sweep_label = "🔴 BSL Swept (High Hunt)" if bsl_swept else ("🟢 SSL Swept (Low Hunt)" if ssl_swept else "⚪ No Active Sweep")
    st.caption(f"**Session:** {killzone_txt}  |  **Liquidity Sweep:** {sweep_label}")

    # --- 📊 REAL MULTI-TIMEFRAME CONFLUENCE MATRIX ---
    st.markdown("---")
    st.markdown("### 📊 Multi-Timeframe Confluence Grid")
    mtf_data = get_mtf_bias(ticker)
    mtf_5m = mtf_data.get("5m", latest_of)
    mtf_15m = mtf_data.get("15m", latest_of)
    mtf_1h = mtf_data.get("1h", "BULLISH" if latest_price > data['EMA200'].iloc[-1] else "BEARISH")

    if mtf_5m == mtf_15m == mtf_1h and mtf_5m in ["BULLISH", "BEARISH"]:
        st.success(f"🔥 **A+ TRIPLE CONFLUENCE:** 5m, 15m & 1h all aligned **{mtf_5m}**.")

    mtf_cols = st.columns(3)
    with mtf_cols[0]:
        st.markdown(f"**5m Timeframe**<br><div class='{'confluence-badge-green' if mtf_5m=='BULLISH' else 'confluence-badge-red'}'>{mtf_5m}</div>", unsafe_allow_html=True)
    with mtf_cols[1]:
        st.markdown(f"**15m Timeframe**<br><div class='{'confluence-badge-green' if mtf_15m=='BULLISH' else 'confluence-badge-red'}'>{mtf_15m}</div>", unsafe_allow_html=True)
    with mtf_cols[2]:
        st.markdown(f"**1h Timeframe**<br><div class='{'confluence-badge-green' if mtf_1h=='BULLISH' else 'confluence-badge-red'}'>{mtf_1h}</div>", unsafe_allow_html=True)

    # --- 🎯 STRIKE PRICE MAPPING & OPTIONS MATRIX ENGINE ---
    meta = ASSET_METADATA.get(ticker, {"step": 50, "lot": 25, "tv_symbol": "NSE:NIFTY"})
    step = meta["step"]
    lot_size = meta["lot"]
    tv_symbol = meta["tv_symbol"]

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
    st.markdown("### 📈 Option Chain & Sentiment Heatboard")

    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)

    est_pcr = round(1.25 if latest_of == "BULLISH" else (0.75 if latest_of == "BEARISH" else 0.98), 2)
    pcr_bias = "Bullish (Put Writing)" if est_pcr > 1.0 else ("Bearish (Call Writing)" if est_pcr < 0.9 else "Neutral")

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
    opt_col4.metric("Est. Market PCR Ratio", f"{est_pcr}", delta=pcr_bias)

    st.markdown("---")

    row2_1, row2_2, row2_3 = st.columns(3)
    row2_1.metric("Est. Spot Stop-Loss", f"{sl:.2f}" if sl > 0 else "N/A")
    row2_2.metric("Est. Spot Target", f"{target:.2f}" if target > 0 else "N/A")
    row2_3.metric("Max Quantity Model", f"{position_size} Qty ({total_lots} Lots)" if position_size > 0 else "N/A")

    if st.session_state.get('broker_connected', False) and latest_setup != "NEUTRAL / NO SETUP":
        active_b = st.session_state.get('active_broker', 'Broker')
        st.markdown(f"### ⚡ Broker Integration Sandbox ({active_b})")
        if st.button(f"🔍 Simulate Order Payload: {selected_asset} {mapped_strike} {contract_type}", key="exec_trade_btn"):
            st.info(f"Sandbox Payload Generated for {selected_asset} {mapped_strike} {contract_type} ({total_lots} Lots). (Note: Manual execution required as per educational policy).")

    # --- LIVE CHART ENGINE (WITH VISUAL FVG, OB & BOS OVERLAYS) ---
    st.subheader(f"Live Chart ({selected_asset} - {timeframe})")

    if category == "BSE Index / F&O" or ticker in ["^BSESN", "BSE-BANK.BO"]:
        st.success("⚡ **BSE Real-Time Data Active:** Streaming live 0-sec tick feeds via TradingView Engine.")
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
        chart_df = data.tail(120).copy()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], name="Price"
        ))
        fig.add_trace(go.Scatter(
            x=chart_df.index, y=chart_df['EMA20'], mode='lines', name='20 EMA', line=dict(color='cyan', width=1)
        ))
        fig.add_trace(go.Scatter(
            x=chart_df.index, y=chart_df['EMA200'], mode='lines', name='200 EMA Filter', line=dict(color='orange', width=2)
        ))

        end_x = chart_df.index[-1]

        # Plot recent Bullish/Bearish FVG boxes
        fvg_boxes = 0
        for idx in range(len(chart_df) - 1, max(-1, len(chart_df) - 35), -1):
            if fvg_boxes >= 4:
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
                    fvg_boxes += 1

        # Plot recent Order Block zones
        ob_boxes = 0
        for idx in range(len(chart_df) - 1, max(0, len(chart_df) - 35), -1):
            if ob_boxes >= 3:
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
                ob_boxes += 1
            elif bool(chart_df['Bearish_OB'].iloc[idx]):
                y0 = float(min(chart_df['Open'].iloc[idx - 1], chart_df['Close'].iloc[idx - 1]))
                y1 = float(max(chart_df['Open'].iloc[idx - 1], chart_df['Close'].iloc[idx - 1]))
                fig.add_shape(
                    type="rect", x0=prev_ts, x1=end_x, y0=y0, y1=y1,
                    fillcolor="rgba(241, 196, 15, 0.14)",
                    line=dict(color="rgba(241, 196, 15, 0.65)", width=1)
                )
                ob_boxes += 1

        # Plot BOS markers on chart
        bos_b_df = chart_df[chart_df['BOS_Bullish']].tail(5)
        if not bos_b_df.empty:
            fig.add_trace(go.Scatter(
                x=bos_b_df.index, y=bos_b_df['High'] * 1.001,
                mode='markers+text', name='BOS Bullish',
                text=['BOS↑'] * len(bos_b_df), textposition='top center',
                textfont=dict(color='#2ecc71', size=10),
                marker=dict(symbol='triangle-up', size=9, color='#2ecc71')
            ))

        bos_s_df = chart_df[chart_df['BOS_Bearish']].tail(5)
        if not bos_s_df.empty:
            fig.add_trace(go.Scatter(
                x=bos_s_df.index, y=bos_s_df['Low'] * 0.999,
                mode='markers+text', name='BOS Bearish',
                text=['BOS↓'] * len(bos_s_df), textposition='bottom center',
                textfont=dict(color='#e74c3c', size=10),
                marker=dict(symbol='triangle-down', size=9, color='#e74c3c')
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

    # --- 🌐 ALL-MARKET LIVE SMC SCANNER ---
    st.markdown("---")
    st.subheader(f"🌐 All-Market Live SMC Scanner ({timeframe})")
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
            scan_rows.append({
                "Asset": sym_label,
                "Price": round(float(s_df["Close"].iloc[-1]), 2),
                "Order Flow": str(s_df["Order_Flow"].iloc[-1]),
                "RSI": round(float(s_df["RSI"].iloc[-1]), 1),
                "Setup": str(s_df["Setup"].iloc[-1]),
            })
    if scan_rows:
        scan_df = pd.DataFrame(scan_rows)
        st.dataframe(scan_df.style.map(color_table_setup, subset=["Setup"]), use_container_width=True, hide_index=True)

    st.subheader("Live Market SMC Analytics Table")

    # Clean DataFrame & Round Decimals to Prevent Mobile Overlap/Glitch
    table_df = data[['Open', 'High', 'Low', 'Close', 'Order_Flow', 'BOS_Bullish', 'BOS_Bearish', 'Bullish_FVG', 'Bearish_FVG', 'Consolidation', 'Setup']].tail(12).copy()
    for col in ['Open', 'High', 'Low', 'Close']:
        if col in table_df.columns:
            table_df[col] = table_df[col].round(2)

    styled_table = table_df.style.map(color_table_setup, subset=['Setup'])
    st.dataframe(styled_table, use_container_width=True)

    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** All indicators, market setups, and calculators provided in this terminal are strictly for learning, technical analysis practice, and quantitative research purposes only. This is not investment advice or SEBI-registered buy/sell recommendation. Trading in stock market/F&O involves substantial financial risk.")

else:
    st.error("Data fetch nahi ho pa raha hai. Re-check ticker selection.")
