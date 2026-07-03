import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np
import plotly.graph_objects as go

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Executive Business Review",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens & Premium Theme System ──────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:        #0f1117;
  --surface:   #1a1d27;
  --surface2:  #21263a;
  --surface3:  #2a2f45;
  --br:        rgba(255,255,255,0.07);
  --br2:       rgba(255,255,255,0.13);
  --text:      #eaeaea;
  --muted:     #8b8fa8;
  --faint:     #4a4f6a;
  --r:         8px;
  --rl:        12px;

  --red:       #ff6b6b;
  --red-bg:    #2d1515;
  --red-b:     #e05252;
  --amber:     #ffc97a;
  --amber-bg:  #2d1e07;
  --amber-b:   #d4891a;
  --green:     #6dd67b;
  --green-bg:  #102216;
  --green-b:   #4a9e2f;
  --blue:      #7cb9f8;
  --blue-bg:   #0d1e38;
  --blue-b:    #2f7dd4;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-size: 13px;
  line-height: 1.5;
}

#MainMenu, footer { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
header { background: transparent !important; }

.block-container {
  padding: 2.5rem 2rem 4rem !important;
  max-width: 1440px !important;
}

div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 0.5px solid var(--br2);
}
.dash-title {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text);
}
.dash-title span { color: var(--blue); }
.dash-meta {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 2px;
}

.sec-ttl {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--muted);
  margin: 1.5rem 0 .75rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sec-ttl-line { flex: 1; height: 0.5px; background: var(--br); }

.kpi {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: var(--rl);
  padding: 14px 16px;
  position: relative;
  overflow: hidden;
}
.kpi::before {
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:2px;
  background: linear-gradient(90deg, var(--blue-b), #b08cff);
}
.kpi-lbl {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--muted);
  margin-bottom: 6px;
}
.kpi-val {
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
.kpi-sub { 
  font-size: 11px; 
  margin-top: 6px; 
  color: var(--muted); 
  display: flex; 
  gap: 6px; 
  flex-wrap: wrap; 
  align-items: center;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
}
.pr { background: var(--red-bg);    color: var(--red); }
.pg { background: var(--green-bg);  color: var(--green); }
.pz { background: var(--surface2);  color: var(--muted); }

.tw {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: 0px 0px var(--rl) var(--rl);
  overflow: hidden;
  margin-bottom: 15px;
}
.dash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  table-layout: fixed; 
}
.dash-table th {
  text-align: left;
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .05em;
  padding: 8px 12px;
  border-bottom: 0.5px solid var(--br2);
  background: var(--surface2);
  font-weight: 700;
  white-space: nowrap;
}
.dash-table td {
  padding: 8px 12px;
  border-bottom: 0.5px solid var(--br);
  color: var(--text);
  white-space: nowrap;
  vertical-align: middle;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table tr:hover td { background: var(--surface2); }
.n { text-align: right; font-variant-numeric: tabular-nums; }

.stButton > button {
  background-color: var(--surface2) !important;
  color: var(--muted) !important;
  border: 0.5px solid var(--br) !important;
  border-radius: 0px !important;
  font-size: 10px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  padding: 6px !important;
  margin: 0 !important;
  width: 100% !important; 
}
.stButton > button:hover {
  color: var(--text) !important;
  border-color: var(--blue) !important;
}

button[data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  border-radius: var(--r) !important;
  padding: 6px 16px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 0.5px solid var(--br) !important;
}
div[data-baseweb="tab-list"] {
  background: var(--surface2) !important;
  border: 0.5px solid var(--br) !important;
  border-radius: var(--rl) !important;
  padding: 3px !important;
  gap: 2px !important;
}
div[data-baseweb="tab-highlight"] { display: none !important; }
div[data-baseweb="tab-border"]    { display: none !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#8b8fa8", size=11),
    margin=dict(l=0, r=0, t=15, b=0), showlegend=False,
    xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#8b8fa8"), linecolor="rgba(255,255,255,0.07)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
    bargap=0.4
)

BAR_CUR  = "#2f7dd4"
BAR_PRV  = "#4a4f6a"

# ── Strictly Isolated Data Fetch Pipelines ────────────────────────────────────
API_KEY = "4aFm2iOoyx8I91svQccdeZr0jmaiUsMFSRinZcmu"
FT_API_URL = f"https://redash.vahan.link/api/queries/17613/results.json?api_key={API_KEY}"
TC_API_URL = f"https://redash.vahan.link/api/queries/17597/results.json?api_key={API_KEY}"
TARGETS_URL = "https://docs.google.com/spreadsheets/d/1S9XGqCiSHXjXbIrjJ6uoaDBRlTgQel__uaoc8S7zsa0/export?format=csv&gid=0"

@st.cache_data(ttl=3600)
def fetch_ft_data():
    try:
        r = requests.get(FT_API_URL, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json()["query_result"]["data"]["rows"])
    except Exception as e:
        st.error(f"⚠️ FT Data Pipeline Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_tc_data():
    try:
        r = requests.get(TC_API_URL, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json()["query_result"]["data"]["rows"])
    except Exception as e:
        st.error(f"⚠️ TC Capacity Pipeline Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_targets_mtd():
    try:
        df_tgt = pd.read_csv(TARGETS_URL)
        new_cols = []
        tgt_found = False
        for c in df_tgt.columns:
            cl = str(c).strip().lower()
            if ('client' in cl or 'company' in cl) and 'company_name' not in new_cols: 
                new_cols.append('company_name')
            elif ('vl' == cl or 'vendor' in cl) and 'vl_name' not in new_cols: 
                new_cols.append('vl_name')
            elif ('am' == cl or 'cm' == cl or 'manager' in cl) and 'am_name' not in new_cols: 
                new_cols.append('am_name')
            elif 'region' in cl and 'region' not in new_cols: 
                new_cols.append('region')
            elif ('tgt' in cl or 'target' in cl) and not tgt_found:
                new_cols.append('target')
                tgt_found = True
            else:
                new_cols.append(cl)
                
        df_tgt.columns = new_cols
        if 'target' in df_tgt.columns:
            df_tgt['target'] = pd.to_numeric(df_tgt['target'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        else:
            df_tgt['target'] = 0
        return df_tgt
    except Exception as e:
        if "401" in str(e):
            st.error("⚠️ **Google Sheets Sync Error (401):** Your Google Sheet is set to 'Restricted'. Please update Share settings to 'Anyone with the link can view'.")
        else:
            st.error(f"⚠️ Target Data Pipeline Sync Error: {e}")
        return pd.DataFrame()

def fetch_targets_wtd(target_type, week_num):
    week_keys = [25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    overall_dict = {
        'Blinkit': [3537, 3760, 3760, 3760, 3960, 4177, 4277, 4427, 4577, 4829, 4929, 4979, 4979, 4979, 4979],
        'Swiggy Food': [887, 1243, 1314, 1428, 1685, 1929, 2171, 2418, 2763, 3019, 3269, 3574, 3876, 4223, 4488],
        'Swiggy IM': [555, 718, 757, 849, 992, 1124, 1264, 1398, 1590, 1738, 1882, 2052, 2221, 2419, 2566],
        'SOC': [37, 37, 77, 112, 187, 262, 312, 387, 487, 587, 587, 637, 637, 687, 687],
        'FKM': [135, 0, 40, 110, 170, 200, 250, 300, 350, 400, 500, 550, 550, 600, 600],
        'Uber': [28, 45, 127, 187, 299, 383, 519, 592, 738, 907, 1115, 1298, 1450, 1603, 1631],
        'Rapido': [0, 0, 0, 75, 200, 300, 380, 500, 600, 700, 800, 900, 1000, 1000, 1000],
        '4W': [50, 67, 97, 115, 167, 194, 261, 298, 381, 456, 570, 640, 740, 800, 828],
        'Picker Packer': [263, 263, 283, 303, 323, 333, 363, 363, 388, 598, 465, 758, 645, 938, 825],
        'Bigbasket': [0, 43, 43, 64, 144, 186, 333, 375, 508, 700, 918, 1000, 1200, 1383, 1463],
        'Amazon': [0, 9, 9, 13, 40, 54, 90, 104, 142, 197, 273, 320, 370, 441, 458],
        'XB': [28, 37, 37, 50, 67, 80, 128, 146, 205, 254, 331, 388, 473, 539, 586],
        'Maid': [80, 80, 100, 120, 120, 120, 120, 120, 120, 120, 120, 120, 150, 120],
        'Small Clients': [0, 0, 0, 20, 50, 100, 150, 200, 300, 400, 500, 550, 600, 600, 600]
    }
    vl_dict = {
        'Blinkit': [0, 3537, 3760, 3760, 3760, 3960, 4177, 4277, 4427, 4577, 4829, 4929, 4979, 4979, 4979],
        'Swiggy Food': [0, 959, 1030, 1123, 1245, 1358, 1453, 1546, 1672, 1778, 1877, 1999, 2119, 2204, 2286],
        'Swiggy IM': [0, 594, 633, 682, 748, 808, 861, 910, 978, 1035, 1088, 1155, 1218, 1265, 1309],
        'SOC': [0, 37, 77, 112, 187, 262, 312, 387, 487, 587, 587, 637, 637, 687, 687],
        'FKM': [0, 0, 40, 110, 170, 200, 250, 300, 350, 400, 500, 550, 550, 600, 600],
        'Uber': [0, 45, 101, 148, 212, 270, 318, 365, 430, 484, 535, 598, 660, 703, 745],
        'Rapido': [0, 0, 0, 75, 200, 300, 380, 500, 600, 700, 800, 900, 1000, 1000, 1000],
        '4W': [0, 67, 97, 90, 110, 120, 130, 150, 180, 180, 200, 220, 250, 250, 250],
        'Picker Packer': [0, 263, 283, 303, 323, 333, 363, 363, 388, 598, 465, 758, 645, 938, 825],
        'Bigbasket': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Amazon': [0, 9, 9, 0, 10, 15, 20, 25, 35, 50, 80, 100, 120, 150, 150],
        'XB': [0, 37, 37, 37, 37, 41, 58, 67, 98, 107, 138, 178, 228, 248, 278],
        'Maid': [0, 80, 100, 120, 120, 120, 120, 120, 120, 120, 120, 120, 150, 120],
        'Small Clients': [0, 0, 0, 20, 50, 100, 150, 200, 300, 400, 500, 550, 600, 600, 600]
    }
    dc_dict = {
        'Blinkit': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Swiggy Food': [0, 284, 284, 305, 440, 571, 718, 872, 1091, 1241, 1392, 1575, 1757, 2019, 2202],
        'Swiggy IM': [0, 124, 124, 167, 244, 316, 403, 488, 612, 703, 794, 897, 1003, 1154, 1257],
        'SOC': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'FKM': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Uber': [0, 0, 26, 39, 87, 113, 201, 227, 308, 423, 580, 700, 790, 900, 886],
        'Rapido': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        '4W': [0, 0, 0, 25, 57, 74, 131, 148, 201, 276, 370, 420, 490, 550, 578],
        'Picker Packer': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Bigbasket': [0, 0, 40, 70, 150, 300, 375, 508, 700, 918, 1000, 1200, 1383, 1463, 0],
        'Amazon': [0, 0, 13, 30, 39, 70, 79, 107, 147, 193, 220, 250, 291, 308, 0],
        'XB': [0, 0, 13, 30, 39, 70, 79, 107, 147, 193, 210, 245, 291, 308, 0],
        'Maid': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Small Clients': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }

    if target_type == "DC": active_dict = dc_dict
    elif target_type == "VL": active_dict = vl_dict
    else: active_dict = overall_dict

    if week_num in week_keys: w_idx = week_keys.index(week_num)
    else: w_idx = 1
        
    compiled_targets = []
    for client, weekly_targets in active_dict.items():
        compiled_targets.append({"company_name": client, "target": weekly_targets[w_idx]})
        
    return pd.DataFrame(compiled_targets)

# ── JSON Mapping for Channel classification Override ──────────────────────────
CHANNEL_MAP = {
  "Existing VL - VGP Approved": [
    "Delhive", "4M Enterprises", "Allz Infra", "Viraj Patil", "Logix Manpower Service", 
    "WorkSetu", "Maruti manangement company", "Manish K", "Hemant", "TrustBridge", 
    "Ravindra Patel", "JKS Sure", "VAAP PLACEMENT SOLUTION", "Aarambh Prime Solutions", 
    "Tech Talk Connect", "Kumar Consultancy"
  ],
  "Existing VL - VGP Identified": [
    "RojiRoty.com", "VMC", "Focus Staffing Services", "AGILE CAREERS", "RAB Enterprises Services pvt.lmt", 
    "Stargalaxy Manpower Pvt Ltd", "Fastseek", "WorkSetu Management Solution LLP", "Rohit Kumar Asterisk", 
    "JKS SURE SERVICES", "Shubhash Rajesh Upadhyay", "Jobistiq manpower private limited", "We ventures", 
    "SNAPFLEET RIDERS PVT LTD", "Manstic", "Sr Fast connect Services", "The Prosperia Group", 
    "Find and Hire Solutions Pvt. Ltd.", "Harsh vashisth", "Devanta enterprises", "TrustBridge Staffing", 
    "Dedde Technologies Private limited", "Aone venture", "Arvind singh", "virajsinh vijaykumar kale patil enterprises", 
    "Jobless consultancy", "AALLZ INFRAA", "SR logistics", "Prime Connect Staffing Services"
  ],
  "BPO": ["Basu Business Solutions"],
  "DC": ["Direct Channel"]
}

def classify_channel(vl_name, vl_status):
    if pd.notna(vl_status) and "new" in str(vl_status).lower():
        return "New"
    for channel, names in CHANNEL_MAP.items():
        if vl_name in names:
            return channel
    return "Existing VL"

@st.cache_data
def fetch_tc_targets():
    return pd.DataFrame({
        "Week number": [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
        "Week_start": pd.to_datetime(["2026-06-29", "2026-07-06", "2026-07-13", "2026-07-20", "2026-07-27", 
                                      "2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31", "2026-09-07"]).date,
        "Overall Addition": [115, 53, 92, 213, 55, 246, 46, 44, 338, 20, 33]
    })

# ── Primary Data Load (Strictly Separated Pipelines) ──────────────────────────
df_ft_raw = fetch_ft_data()
df_tc_raw = fetch_tc_data()
df_tc_targets = fetch_tc_targets()

if df_ft_raw.empty and df_tc_raw.empty: st.stop()

# ── Dynamic Column Normalizer (Prevents Casing KeyErrors) ─────────────────────
if not df_ft_raw.empty:
    ft_col_map = {}
    for c in df_ft_raw.columns:
        cl = str(c).strip().lower().replace(" ", "_")
        if cl in ["first_date_of_work", "company_name", "vl_name", "region"]: ft_col_map[c] = cl
        elif cl == "client": ft_col_map[c] = "company_name"
    df_ft_raw.rename(columns=ft_col_map, inplace=True)

if not df_tc_raw.empty:
    tc_col_map = {}
    for c in df_tc_raw.columns:
        cl = str(c).strip().lower().replace(" ", "_")
        if cl == "week_start": tc_col_map[c] = "Week_start"
        elif cl == "vl_name": tc_col_map[c] = "vl_name"
        elif cl == "vl_status": tc_col_map[c] = "vl_status"
        elif cl == "region": tc_col_map[c] = "region"
        elif cl == "cohort": tc_col_map[c] = "cohort"
        elif cl == "channel": tc_col_map[c] = "Channel"
        elif cl == "active_tcs": tc_col_map[c] = "active_tcs"
        elif cl == "existing_tcs": tc_col_map[c] = "existing_tcs"
        elif cl == "new_tcs": tc_col_map[c] = "new_tcs"
        elif cl == "resurrected_tcs": tc_col_map[c] = "resurrected_tcs"
        elif cl == "churned_tcs": tc_col_map[c] = "churned_tcs"
        elif cl == "net_new_additions": tc_col_map[c] = "net_new_additions"
    df_tc_raw.rename(columns=tc_col_map, inplace=True)

# ── Post-Load Pre-Processing ──────────────────────────────────────────────────
df_base = df_ft_raw.copy()
ft = "first_date_of_work"
if ft in df_base.columns:
    df_base[ft] = pd.to_datetime(df_base[ft], errors="coerce").dt.date

tc_metrics = ["active_tcs", "existing_tcs", "churned_tcs", "new_tcs", "resurrected_tcs", "net_new_additions"]
for col in tc_metrics:
    if col not in df_tc_raw.columns: df_tc_raw[col] = 0
    else: df_tc_raw[col] = pd.to_numeric(df_tc_raw[col], errors='coerce').fillna(0)

if "Week_start" in df_tc_raw.columns:
    df_tc_raw["Week_start"] = pd.to_datetime(df_tc_raw["Week_start"], errors='coerce').dt.date

if "vl_name" in df_tc_raw.columns:
    df_tc_raw["Channel"] = df_tc_raw.apply(lambda row: classify_channel(row.get("vl_name"), row.get("vl_status", "")), axis=1)

# ── Global Scope Temporal Anchoring ───────────────────────────────────────────
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# ── Sidebar Controls & Filters ────────────────────────────────────────────────
st.sidebar.markdown("### 🛠️ Data Controls")
if st.sidebar.button("🔄 Force Refresh Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("### 🎛️ Parameters")
mode = st.sidebar.selectbox("FT Comparison Window Mode", ["WTD", "MTD"])
tc_time_filter = st.sidebar.number_input("TC Capacity N-Weeks Default", min_value=1, max_value=12, value=6)
exclude_current = st.sidebar.checkbox("Exclude Current Incomplete Week", value=False)

def get_windows(mode, exclude_current):
    if mode == "WTD":
        dow = today.weekday()
        if exclude_current:
            cs = today - datetime.timedelta(days=dow + 7)
            ce = cs + datetime.timedelta(days=6)
            ps = cs - datetime.timedelta(days=7)
            pe = ps + datetime.timedelta(days=6)
        else:
            cs = today - datetime.timedelta(days=dow)
            ce = yesterday
            ps = cs - datetime.timedelta(weeks=1)
            pe = ce - datetime.timedelta(weeks=1)
    else:
        cs = today.replace(day=1)
        ce = yesterday
        pm = today.month - 1 or 12
        py = today.year if today.month > 1 else today.year - 1
        prev_start = today.replace(year=py, month=pm, day=1)
        offset = (ce - cs).days
        ps = prev_start
        pe = prev_start + datetime.timedelta(days=offset)
    return cs, ce, ps, pe

cs, ce, ps, pe = get_windows(mode, exclude_current)

st.sidebar.markdown("### 🔍 Global Segment Filters")

client_opts = sorted(list(df_base["company_name"].dropna().unique())) if "company_name" in df_base.columns else []
selected_clients = st.sidebar.multiselect("Client Scope (FT Only)", client_opts, key="global_filter_client")

all_weeks = sorted(df_tc_raw["Week_start"].dropna().unique(), reverse=True) if "Week_start" in df_tc_raw.columns else []
if exclude_current and len(all_weeks) > 0: all_weeks = all_weeks[1:]
sel_weeks = st.sidebar.multiselect("Week Scope (TC Only)", all_weeks, default=all_weeks[:tc_time_filter])

cohort_opts = sorted(df_tc_raw["cohort"].dropna().unique()) if "cohort" in df_tc_raw.columns else []
sel_cohorts = st.sidebar.multiselect("Cohort Scope (TC Only)", cohort_opts)

channel_opts = sorted(df_tc_raw["Channel"].dropna().unique()) if "Channel" in df_tc_raw.columns else []
sel_channels = st.sidebar.multiselect("Channel Scope (TC Only)", channel_opts)

reg_ft = set(df_base["region"].dropna()) if "region" in df_base.columns else set()
reg_tc = set(df_tc_raw["region"].dropna()) if "region" in df_tc_raw.columns else set()
shared_regions = sorted(reg_ft.union(reg_tc))
selected_regions = st.sidebar.multiselect("Region Scope (Shared)", shared_regions)

vl_ft = set(df_base["vl_name"].dropna()) if "vl_name" in df_base.columns else set()
vl_tc = set(df_tc_raw["vl_name"].dropna()) if "vl_name" in df_tc_raw.columns else set()
shared_vls = sorted(vl_ft.union(vl_tc))
selected_vls = st.sidebar.multiselect("Vendor Line Scope (Shared)", shared_vls)

cs_week_num = cs.isocalendar()[1]

if mode == "MTD":
    tgt_base = fetch_targets_mtd()
else:
    dc_vendors = ["DC", "Direct Channel", "Basu Business Solutions"]
    if selected_vls:
        if all(v in dc_vendors for v in selected_vls): tgt_base = fetch_targets_wtd("DC", cs_week_num)
        elif all(v not in dc_vendors for v in selected_vls): tgt_base = fetch_targets_wtd("VL", cs_week_num)
        else: tgt_base = fetch_targets_wtd("Overall", cs_week_num)
    else:
        tgt_base = fetch_targets_wtd("Overall", cs_week_num)

df = df_base.copy()
t_df = tgt_base.copy()
df_tc = df_tc_raw.copy()

def filter_target_df(target_df, col_name, selected_items):
    if col_name in target_df.columns:
        target_df[col_name] = target_df[col_name].fillna("Unattributed").astype(str).str.strip().str.title()
        selected_items_title = [str(x).strip().title() for x in selected_items]
        return target_df[target_df[col_name].isin(selected_items_title)]
    return target_df

if selected_clients and "company_name" in df.columns: 
    df = df[df["company_name"].isin(selected_clients)]
    t_df = filter_target_df(t_df, 'company_name', selected_clients)
if selected_regions:
    if "region" in df.columns: df = df[df["region"].isin(selected_regions)]
    if "region" in df_tc.columns: df_tc = df_tc[df_tc["region"].isin(selected_regions)]
if selected_vls:     
    if "vl_name" in df.columns: df = df[df["vl_name"].isin(selected_vls)]
    t_df = filter_target_df(t_df, 'vl_name', selected_vls)
    if "vl_name" in df_tc.columns: df_tc = df_tc[df_tc["vl_name"].isin(selected_vls)]
if sel_weeks and "Week_start" in df_tc.columns: df_tc = df_tc[df_tc["Week_start"].isin(sel_weeks)]
if sel_cohorts and "cohort" in df_tc.columns: df_tc = df_tc[df_tc["cohort"].isin(sel_cohorts)]
if sel_channels and "Channel" in df_tc.columns: df_tc = df_tc[df_tc["Channel"].isin(sel_channels)]

days_elapsed = (ce - cs).days + 1
if mode == "WTD": total_days = 7
else:
    next_month = cs.replace(day=28) + datetime.timedelta(days=4)
    total_days = (next_month - datetime.timedelta(days=next_month.day)).day

remaining_days = max(0, total_days - days_elapsed)
l4w_e = yesterday
l4w_s = l4w_e - datetime.timedelta(days=27)

# ── Header Markup Execution ───────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Vahan <span>Performance Analytics</span> Dashboard</div>
    <div class="dash-meta"><span class="live-dot"></span>Live Lookback Tracking · Active Bounds as of Yesterday</div>
  </div>
  <div><span class="pill pb" style="font-size:11px;">Current: {cs.strftime('%b %d')} - {ce.strftime('%b %d')} vs Previous: {ps.strftime('%b %d')} - {pe.strftime('%b %d')}</span></div>
</div>""", unsafe_allow_html=True)

# ── Calculation Helpers ───────────────────────────────────────────────────────
def fmt(n):
    if pd.isna(n): return "—"
    return f"{int(n):,}" if abs(n) < 1e6 else f"{n/1e6:.1f}M"

def pill_markup(val):
    if pd.isna(val) or not np.isfinite(val): return '<span class="pill pz">—</span>'
    cls = "pg" if val >= 0 else "pr"
    return f'<span class="pill {cls}">{"+" if val > 0 else ""}{val:.1f}%</span>'

def volume_pill(val):
    if pd.isna(val): return '<span class="pill pz">—</span>'
    cls = "pg" if val >= 0 else "pr"
    return f'<span class="pill {cls}">{"+" if val > 0 else ""}{int(val):,}</span>'

def contr_markup(delta, contr):
    if pd.isna(contr) or delta == 0 or contr == 0: return '<span class="td-muted">—</span>'
    if delta > 0: return f'<span style="color:var(--green); font-size:10px; font-weight:700;">{abs(contr):.1f}% Grw</span>'
    return f'<span style="color:var(--red); font-size:10px; font-weight:700;">{abs(contr):.1f}% Dip</span>'

def kpi_html(label, value, sub="", pill_html=""):
    return f"""
    <div class="kpi">
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-sub">{sub} {pill_html}</div>
    </div>"""

def compute_comparison_matrix(dataframe, group_key, target_df=None):
    if ft not in dataframe.columns: return pd.DataFrame()
    group_cols = group_key if isinstance(group_key, list) else [group_key]
    
    c = dataframe[(dataframe[ft] >= cs) & (dataframe[ft] <= ce)].groupby(group_cols).size().rename("cur")
    p = dataframe[(dataframe[ft] >= ps) & (dataframe[ft] <= pe)].groupby(group_cols).size().rename("prv")
    l4w = dataframe[(dataframe[ft] >= l4w_s) & (dataframe[ft] <= l4w_e)].groupby(group_cols).size().rename("l4w")
    
    res = pd.concat([c, p, l4w], axis=1).reset_index()
    if not res.empty:
        for k in group_cols:
            if k in res.columns:
                res[k] = res[k].fillna("Unattributed").astype(str).str.strip().str.title()
        res = res.groupby(group_cols, as_index=False)[['cur', 'prv', 'l4w']].sum()

    if target_df is not None and not target_df.empty:
        keys_to_merge = [k for k in group_cols if k in target_df.columns]
        if keys_to_merge:
            t_df_temp = target_df.copy()
            for k in keys_to_merge:
                t_df_temp[k] = t_df_temp[k].fillna("Unattributed").astype(str).str.strip().str.title()
            
            t_agg = t_df_temp.groupby(keys_to_merge)['target'].sum().reset_index()
            
            if not res.empty: res = pd.merge(res, t_agg, on=keys_to_merge, how="outer")
            else:
                res = t_agg
                res["cur"], res["prv"], res["l4w"] = 0, 0, 0
        else: res["target"] = 0
    else:
        if res.empty: res = pd.DataFrame(columns=group_cols + ["cur", "prv", "l4w", "target"])
        else: res["target"] = 0
            
    for col in ["cur", "prv", "l4w", "target"]:
        if col not in res.columns: res[col] = 0
        res[col] = res[col].fillna(0).astype(int)
        
    res["delta"] = res["cur"] - res["prv"]
    res["pct"] = np.where(res["prv"] > 0, (res["delta"] / res["prv"]) * 100, np.nan)
    res["proj"] = (res["cur"] + (res["l4w"] / 28.0) * remaining_days).round().astype(int)
    res["gap"] = res["proj"] - res["target"]
    res["gap_pct"] = np.where(res["target"] > 0, (res["gap"] / res["target"]) * 100, np.nan)
    
    res["contr"] = 0.0
    sum_pos = res.loc[res['delta'] > 0, 'delta'].sum()
    sum_neg = res.loc[res['delta'] < 0, 'delta'].sum()
    
    if sum_pos > 0: res["contr"] = np.where(res['delta'] > 0, (res['delta'] / sum_pos) * 100, res["contr"])
    if sum_neg < 0: res["contr"] = np.where(res['delta'] < 0, -(res['delta'] / sum_neg) * 100, res["contr"])
    
    return res

def draw_sortable_header(table_id, col_specs):
    state_key = f"sort_state_{table_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = (col_specs[0][1], False)

    current_col, current_desc = st.session_state[state_key]
    grid_cols = st.columns([spec[2] for spec in col_specs])
    
    for idx, (label, field, weight) in enumerate(col_specs):
        icon = " ▴" if current_col == field and not current_desc else (" ▾" if current_col == field else "")
        if grid_cols[idx].button(f"{label}{icon}", key=f"btn_{table_id}_{str(field)}"):
            if current_col == field: st.session_state[state_key] = (field, not current_desc)
            else: st.session_state[state_key] = (field, True)
            st.rerun()
    return st.session_state[state_key]

def section(title):
    st.markdown(f'<div class="sec-ttl">{title}<div class="sec-ttl-line"></div></div>', unsafe_allow_html=True)

# ── Primary Metric Matrices Engine Calculations ──────────────────────────────
cur_tot = len(df[(df[ft] >= cs) & (df[ft] <= ce)]) if ft in df.columns else 0
prv_tot = len(df[(df[ft] >= ps) & (df[ft] <= pe)]) if ft in df.columns else 0
l4w_tot = len(df[(df[ft] >= l4w_s) & (df[ft] <= l4w_e)]) if ft in df.columns else 0

dlt_tot = cur_tot - prv_tot
pct_tot = (dlt_tot / prv_tot * 100) if prv_tot > 0 else np.nan
proj_tot = int(round(cur_tot + (l4w_tot / 28.0) * remaining_days))

client_mat = compute_comparison_matrix(df, "company_name", t_df)
vl_master = compute_comparison_matrix(df, "vl_name", t_df)
vl_by_client_mat = compute_comparison_matrix(df, ["vl_name", "company_name"], t_df)
reg_mat = compute_comparison_matrix(df, "region", t_df)

total_target = int(client_mat['target'].sum()) if not client_mat.empty else 0
gap_tot = proj_tot - total_target
gap_tot_pct = (gap_tot / total_target * 100) if total_target > 0 else np.nan
daily_rr = l4w_tot / 28.0

# ── Tab Navigation Panels ─────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📦 FT View", "⚡ TC Capacity", "🤖 AI Narrative"])

# ==============================================================================
# TAB 1: FT VIEW
# ==============================================================================
with tab1:
    k1, k2, k3, k4, k5 = st.columns(5)
    k_color = "var(--green)" if dlt_tot >= 0 else "var(--red)"
    g_color = "var(--green)" if gap_tot >= 0 else "var(--red)"
    
    with k1: 
        pills = volume_pill(dlt_tot) + " " + pill_markup(pct_tot)
        st.markdown(kpi_html("Current Period FT", f'<span style="color:{k_color}">{fmt(cur_tot)}</span>', pill_html=pills), unsafe_allow_html=True)
    with k2: 
        st.markdown(kpi_html("Projected FT", fmt(proj_tot), sub=f"4WMA Pace: {daily_rr:.1f} FT/d"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_html("Previous Period FT", fmt(prv_tot), sub="Historical Baseline"), unsafe_allow_html=True)
    with k4: 
        st.markdown(kpi_html("Final Target FT", fmt(total_target), sub="Segment Quota"), unsafe_allow_html=True)
    with k5: 
        st.markdown(kpi_html("Target Gap (Proj)", f'<span style="color:{g_color}">{fmt(gap_tot)}</span>', pill_html=pill_markup(gap_tot_pct)), unsafe_allow_html=True)

    if mode == "WTD" and ft in df.columns:
        df_trend = df.copy()
        df_trend['datetime'] = pd.to_datetime(df_trend[ft])
        df_trend['Week_Start'] = df_trend['datetime'].dt.to_period('W').dt.start_time.dt.date
        
        dow = today.weekday()
        this_week_monday = today - datetime.timedelta(days=dow)
        if exclude_current: df_trend = df_trend[df_trend['Week_Start'] < this_week_monday]
            
        if not df_trend.empty:
            max_trend_w = df_trend['Week_Start'].max()
            active_weeks = [max_trend_w - datetime.timedelta(weeks=i) for i in range(7, -1, -1)]
            df_trend = df_trend[df_trend['Week_Start'].isin(active_weeks)]
            
            trend_data = df_trend.groupby('Week_Start').size().reset_index(name='Placements')
            trend_data = trend_data.sort_values('Week_Start')
            trend_data['Label'] = trend_data['Week_Start'].apply(lambda x: f"W/C {x.strftime('%d %b')}")
            
            section("Trailing 8-Week Placement Trend Lookback")
            fig_trend = go.Figure(go.Scatter(
                x=trend_data['Label'], y=trend_data['Placements'], mode='lines+markers+text',
                line=dict(color=BAR_CUR, width=3), text=trend_data['Placements'], textposition="top center",
                marker=dict(size=8, color=BAR_CUR)
            ))
            fig_trend.update_layout(**PLOT_LAYOUT, height=220)
            st.plotly_chart(fig_trend, config={"displayModeBar": False}, key="8_week_trend_line_chart")
            
            section("Client × Week Matrix View (FT Volume & WoW Changes)")
            matrix_src = df_trend.groupby(['company_name', 'Week_Start']).size().unstack(fill_value=0)
            
            week_w = 80 / len(active_weeks) if active_weeks else 80
            col_specs_week = [("Client Profile", "company_name", 20)] + [(f"W/C {w.strftime('%d %b')}", w, week_w) for w in active_weeks]
            w_col, w_desc = draw_sortable_header("client_week_matrix_v15", col_specs_week)
            
            if w_col == "company_name" or w_col not in matrix_src.columns: matrix_src = matrix_src.sort_index(ascending=not w_desc)
            else: matrix_src = matrix_src.sort_values(by=w_col, ascending=not w_desc)
                
            m_tbl = '<div class="tw" style="overflow-x:auto;"><table class="dash-table"><tbody>'
            for client_name, row in matrix_src.iterrows():
                m_tbl += f'<tr><td style="width: 20%; font-weight:600;">{client_name}</td>'
                for idx, week_monday in enumerate(active_weeks):
                    val = row.get(week_monday, 0)
                    if idx == 0:
                        wow_str = '<span style="font-size:10px; color:var(--muted);">Base</span>'
                        val_color = "var(--text)"
                    else:
                        prev_week_monday = active_weeks[idx - 1]
                        prev_val = row.get(prev_week_monday, 0)
                        if prev_val > 0:
                            wow_pct = ((val - prev_val) / prev_val) * 100
                            val_color = "var(--green)" if wow_pct > 0 else ("var(--red)" if wow_pct < 0 else "var(--text)")
                            wow_str = f'<span style="font-size:10px; color:{val_color}; font-weight:700;">{wow_pct:+.1f}%</span>'
                        else:
                            val_color = "var(--green)" if val > 0 else "var(--text)"
                            wow_str = f'<span style="font-size:10px; color:{val_color}; font-weight:700;">+100%</span>' if val > 0 else '<span style="font-size:10px; color:var(--muted);">0%</span>'
                    m_tbl += f'<td class="n" style="width: {week_w}%;"><div style="font-weight:600; color:{val_color};">{val:,}</div><div>{wow_str}</div></td>'
                m_tbl += '</tr>'
            m_tbl += '</tbody></table></div>'
            st.markdown(m_tbl, unsafe_allow_html=True)

    elif mode == "MTD" and ft in df.columns:
        section("Month-To-Date (MTD) Day-by-Day Run-Rate Tracking")
        sub_cur = df[(df[ft] >= cs) & (df[ft] <= ce)]
        sub_prv = df[(df[ft] >= ps) & (df[ft] <= pe)]
        
        cur_days = sub_cur.groupby(sub_cur[ft].apply(lambda x: x.day)).size().rename("Current Month")
        prv_days = sub_prv.groupby(sub_prv[ft].apply(lambda x: x.day)).size().rename("Previous Month")
        
        mtd_trend = pd.concat([cur_days, prv_days], axis=1).fillna(0).reset_index()
        mtd_trend.columns = ["Day of Month", "Current Month", "Previous Month"]
        
        fig_mtd = go.Figure()
        fig_mtd.add_trace(go.Scatter(x=mtd_trend["Day of Month"], y=mtd_trend["Previous Month"], name="Previous Month Baseline", mode='lines', line=dict(color=BAR_PRV, width=2, dash='dot')))
        fig_mtd.add_trace(go.Scatter(x=mtd_trend["Day of Month"], y=mtd_trend["Current Month"], name="Current Month Runrate", mode='lines+markers', line=dict(color=BAR_CUR, width=3)))
        
        mtd_layout = dict(**PLOT_LAYOUT)
        mtd_layout["height"] = 240
        mtd_layout["showlegend"] = True
        fig_mtd.update_layout(**mtd_layout)
        st.plotly_chart(fig_mtd, config={"displayModeBar": False}, key="mtd_day_runrate_chart")

    if not client_mat.empty:
        section("All Clients Performance Analysis")
        c_col, c_desc = draw_sortable_header("client_main_v15", [
            ("Client Name", "company_name", 20), 
            ("Cur", "cur", 10), ("Proj", "proj", 10), ("Prv", "prv", 10),
            ("Target", "target", 10), ("Gap", "gap", 10), 
            ("Δ Vol", "delta", 10), ("Δ %", "pct", 10), ("Contribution", "contr", 10)
        ])
        if c_col == "company_name" or c_col not in client_mat.columns: client_mat = client_mat.sort_index(ascending=not c_desc)
        else: client_mat = client_mat.sort_values(c_col, ascending=not c_desc)

        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in client_mat.iterrows():
            c_color = "var(--green)" if r['delta'] >= 0 else "var(--red)"
            g_color = "var(--green)" if r['gap'] >= 0 else "var(--red)"
            t_html += f"""<tr>
                <td style="width:20%; font-weight:600;">{r['company_name']}</td>
                <td class="n" style="width:10%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:10%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['prv'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['target'])}</td>
                <td class="n" style="width:10%; font-weight:600; color:{g_color};">{fmt(r['gap'])}<br>{pill_markup(r['gap_pct'])}</td>
                <td class="n" style="width:10%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:10%;">{pill_markup(r['pct'])}</td>
                <td class="n" style="width:10%;">{contr_markup(r['delta'], r['contr'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

    if not vl_by_client_mat.empty:
        section("Dynamic Vendor Line (VL) Analytics Tracker (By Client)")
        
        v_left, v_mid, v_right = st.columns([1, 1, 2])
        tracker_top_n = v_left.selectbox("Display Top N Configurable", [5, 10, 15, 20, 50], index=1)
        tracker_sort = v_mid.selectbox("Sort Priority By", ["cur", "delta", "gap"], index=1)
        tracker_trend = v_right.radio("Trend View", ["Top Growing / Performers", "Bottom Degrowing / Performers"], horizontal=True)
        is_ascending = True if "Bottom" in tracker_trend else False

        vbc_col, vbc_desc = draw_sortable_header("vl_by_client_table_v15", [
            ("Vendor Line (VL)", "vl_name", 16), ("Client", "company_name", 14), 
            ("Cur", "cur", 10), ("Proj", "proj", 10), ("Prv", "prv", 10),
            ("Target", "target", 10), ("Gap", "gap", 10), 
            ("Δ Vol", "delta", 10), ("Contribution", "contr", 10)
        ])
        
        if vbc_col in ["vl_name", "company_name"] or vbc_col not in vl_by_client_mat.columns: 
            vl_by_client_mat = vl_by_client_mat.sort_values(by=tracker_sort, ascending=is_ascending).head(tracker_top_n)
        else: 
            vl_by_client_mat = vl_by_client_mat.sort_values(vbc_col, ascending=not vbc_desc).head(tracker_top_n)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in vl_by_client_mat.iterrows():
            c_color = "var(--green)" if r['delta'] >= 0 else "var(--red)"
            g_color = "var(--green)" if r['gap'] >= 0 else "var(--red)"
            t_html += f"""<tr>
                <td style="width:16%; font-weight:600;">{r['vl_name']}</td>
                <td style="width:14%; color:var(--muted);">{r['company_name']}</td>
                <td class="n" style="width:10%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:10%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['prv'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['target'])}</td>
                <td class="n" style="width:10%; font-weight:600; color:{g_color};">{fmt(r['gap'])}<br>{pill_markup(r['gap_pct'])}</td>
                <td class="n" style="width:10%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:10%;">{contr_markup(r['delta'], r['contr'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)
        
        with st.expander("📍 Expand for Regional Execution View"):
            rc_col, rc_desc = draw_sortable_header("reg_client_table_v15", [
                ("Region", "region", 15), ("Client Profile", "company_name", 15), 
                ("Cur", "cur", 10), ("Proj", "proj", 10), ("Prv", "prv", 10),
                ("Target", "target", 10), ("Gap", "gap", 10), 
                ("Δ Vol", "delta", 10), ("Contribution", "contr", 10)
            ])
            reg_client_mat = compute_comparison_matrix(df, ["region", "company_name"], t_df)
            if rc_col in ["region", "company_name"] or rc_col not in reg_client_mat.columns: reg_client_mat = reg_client_mat.sort_index(ascending=not rc_desc)
            else: reg_client_mat = reg_client_mat.sort_values(rc_col, ascending=not rc_desc)
            
            t_html = '<div class="tw"><table class="dash-table"><tbody>'
            for _, r in reg_client_mat.iterrows():
                c_color = "var(--green)" if r['delta'] >= 0 else "var(--red)"
                g_color = "var(--green)" if r['gap'] >= 0 else "var(--red)"
                t_html += f"""<tr>
                    <td style="width:15%; font-weight:600;">{r['region']}</td>
                    <td style="width:15%; color:var(--muted);">{r['company_name']}</td>
                    <td class="n" style="width:10%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                    <td class="n" style="width:10%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                    <td class="n" style="width:10%; color:var(--muted);">{fmt(r['prv'])}</td>
                    <td class="n" style="width:10%; color:var(--muted);">{fmt(r['target'])}</td>
                    <td class="n" style="width:10%; font-weight:600; color:{g_color};">{fmt(r['gap'])}<br>{pill_markup(r['gap_pct'])}</td>
                    <td class="n" style="width:10%;">{volume_pill(r['delta'])}</td>
                    <td class="n" style="width:10%;">{contr_markup(r['delta'], r['contr'])}</td>
                </tr>"""
            t_html += "</tbody></table></div>"
            st.markdown(t_html, unsafe_allow_html=True)

# ==============================================================================
# TAB 2: TC CAPACITY VIEW
# ==============================================================================
with tab2:
    cur_wk_date = all_weeks[0] if all_weeks else None
    cur_wk_data = df_tc[df_tc["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
    
    target_row = df_tc_targets[df_tc_targets["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
    overall_target = target_row["Overall Addition"].values[0] if not target_row.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    kpi_new = cur_wk_data["new_tcs"].sum() if not cur_wk_data.empty else 0
    kpi_resurrected = cur_wk_data["resurrected_tcs"].sum() if not cur_wk_data.empty else 0
    kpi_churned = cur_wk_data["churned_tcs"].sum() if not cur_wk_data.empty else 0
    kpi_active = cur_wk_data["active_tcs"].sum() if not cur_wk_data.empty else 0
    kpi_existing = cur_wk_data["existing_tcs"].sum() if not cur_wk_data.empty else 0
    kpi_net_additions = cur_wk_data["net_new_additions"].sum() if not cur_wk_data.empty else 0

    metrics = [
        ("Overall Target", overall_target), 
        ("Active TCs", kpi_active),
        ("Existing TCs", kpi_existing), 
        ("Churned TCs", kpi_churned), 
        ("New TCs", kpi_new),
        ("Net Additions", kpi_net_additions)
    ]
    for col, (label, val) in zip([c1, c2, c3, c4, c5, c6], metrics):
        text_color = "var(--text)"
        if label == "Net Additions" and isinstance(val, (int, float)):
            if val > 0: text_color = "var(--green)"
            elif val < 0: text_color = "var(--red)"
        col.markdown(f'<div class="kpi" style="padding:10px;"><div class="kpi-lbl" style="font-size:9px;">{label}</div><div class="kpi-val" style="font-size:20px; color:{text_color};">{val:,}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-ttl">Detailed Analytical Modals (Grouped Pivot Views)</div>', unsafe_allow_html=True)

    def style_tc_dataframe(dataframe, group_col):
        unique_groups = dataframe[group_col].unique()
        def highlight_rows(row):
            if row["Week Start"] == "-": 
                return ["background-color: #21263a; font-weight: 800; border-top: 2px solid rgba(255,255,255,0.3)"] * len(row)
            elif row["Week Start"] == "SUBTOTAL":
                return ["background-color: rgba(255,255,255,0.08); font-weight: 700; border-top: 1px solid rgba(255,255,255,0.2); border-bottom: 1px solid rgba(255,255,255,0.2)"] * len(row)
            try:
                idx = list(unique_groups).index(row[group_col])
                bg = "background-color: rgba(255,255,255,0.03)" if idx % 2 == 0 else "background-color: transparent"
                return [bg] * len(row)
            except:
                return [""] * len(row)
                
        def format_net_adds(val):
            if isinstance(val, (int, float)):
                if val > 0: return 'color: #6dd67b; font-weight: 700;'
                elif val < 0: return 'color: #ff6b6b; font-weight: 700;'
            return ''
            
        format_dict = {c: "{:,.0f}" for c in dataframe.columns if c not in [group_col, "Week Start"]}
        return dataframe.style.format(format_dict).apply(highlight_rows, axis=1).map(format_net_adds, subset=["Net New Additions"])

    def render_tc_table(dataframe, group_col):
        if dataframe is None or dataframe.empty:
            st.info("No data meets the current filter criteria.")
            return
        
        styled_df = style_tc_dataframe(dataframe, group_col)
        try:
            html = styled_df.hide(axis="index").to_html(table_attributes='class="dash-table" style="width: 100%;"')
        except AttributeError:
            html = styled_df.hide_index().to_html(table_attributes='class="dash-table" style="width: 100%;"')
            
        st.markdown(f'<div class="tw" style="overflow-x:auto;">{html}</div>', unsafe_allow_html=True)

    def get_standard_table(group_col):
        if df_tc.empty or group_col not in df_tc.columns or "Week_start" not in df_tc.columns: 
            return pd.DataFrame()
        
        agg = df_tc.groupby([group_col, "Week_start"])[["active_tcs", "existing_tcs", "resurrected_tcs", "churned_tcs", "new_tcs", "net_new_additions"]].sum().reset_index()
        
        tgt_map = df_tc_targets.set_index("Week_start")["Overall Addition"].to_dict()
        agg["targets"] = agg["Week_start"].map(tgt_map).fillna(0).astype(int)
        
        agg = agg.sort_values(by=[group_col, "Week_start"], ascending=[True, False])
        
        final_rows = []
        for group_name, group_df in agg.groupby(group_col, sort=False):
            if group_df.empty: continue
            
            subtotal = group_df.sum(numeric_only=True).to_frame().T
            subtotal[group_col] = group_name
            subtotal["Week_start"] = "SUBTOTAL"
            
            gp_df = group_df.copy()
            gp_df["Week_start"] = pd.to_datetime(gp_df["Week_start"]).dt.strftime('%d/%m/%Y')
            
            final_rows.append(subtotal)
            final_rows.append(gp_df)
            
        if not final_rows: return pd.DataFrame()
        res_df = pd.concat(final_rows, ignore_index=True)
        
        grand_total = agg.sum(numeric_only=True).to_frame().T
        grand_total[group_col] = "GRAND TOTAL"
        grand_total["Week_start"] = "-"
        res_df = pd.concat([res_df, grand_total], ignore_index=True)
        
        rename_dict = {
            "Week_start": "Week Start",
            "active_tcs": "Active TCs",
            "existing_tcs": "Existing TCs",
            "resurrected_tcs": "Resurrected TCs",
            "churned_tcs": "Churned TCs",
            "new_tcs": "New TCs",
            "targets": "Targets",
            "net_new_additions": "Net New Additions"
        }
        res_df = res_df.rename(columns=rename_dict)
        
        cols_order = [group_col, "Week Start", "Active TCs", "Existing TCs", "Resurrected TCs", "Churned TCs", "New TCs", "Targets", "Net New Additions"]
        res_df = res_df[[c for c in cols_order if c in res_df.columns]]
        return res_df

    with st.expander("📊 Channel View Drill-down"):
        render_tc_table(get_standard_table("Channel"), "Channel")
    with st.expander("📍 Region View Drill-down"):
        render_tc_table(get_standard_table("region"), "region")
    with st.expander("👥 Cohort View Drill-down"):
        render_tc_table(get_standard_table("cohort"), "cohort")
        
    with st.expander("🏆 Top N VLs Configurable View"):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        tc_n_vls = col1.number_input("Display Top N (TC)", min_value=1, max_value=50, value=10)
        tc_sort_col = col2.selectbox("Sort Priority By", ["net_new_additions", "active_tcs", "new_tcs", "churned_tcs", "existing_tcs"], index=0)
        tc_trend = col3.radio("Trend View (TC)", ["Top Performers", "Bottom Performers"], horizontal=True)
        
        tc_channel_opts = sorted(df_tc_raw["Channel"].dropna().unique()) if "Channel" in df_tc_raw.columns else []
        tc_channels = col4.multiselect("Filter by Channel (TC Specific)", tc_channel_opts, key="tc_exp_chan")
        
        tmp_tc = df_tc.copy()
        if tc_channels and "Channel" in tmp_tc.columns:
            tmp_tc = tmp_tc[tmp_tc["Channel"].isin(tc_channels)]
            
        if not tmp_tc.empty and "Week_start" in tmp_tc.columns:
            is_tc_asc = True if "Bottom" in tc_trend else False
            vl_totals = tmp_tc.groupby("vl_name")[tc_sort_col].sum().reset_index()
            top_vls = vl_totals.sort_values(by=tc_sort_col, ascending=is_tc_asc).head(tc_n_vls)["vl_name"].tolist()
            
            vl_agg = tmp_tc[tmp_tc["vl_name"].isin(top_vls)].groupby(["vl_name", "Week_start"])[["active_tcs", "existing_tcs", "resurrected_tcs", "churned_tcs", "new_tcs", "net_new_additions"]].sum().reset_index()
            
            tgt_map = df_tc_targets.set_index("Week_start")["Overall Addition"].to_dict()
            vl_agg["targets"] = vl_agg["Week_start"].map(tgt_map).fillna(0).astype(int)
            
            vl_agg["vl_name"] = pd.Categorical(vl_agg["vl_name"], categories=top_vls, ordered=True)
            vl_agg_filtered = vl_agg.sort_values(by=["vl_name", "Week_start"], ascending=[True, False])
            
            final_vl_rows = []
            for vl_name, group_df in vl_agg_filtered.groupby("vl_name", sort=False):
                if group_df.empty: continue
                subtotal = group_df.sum(numeric_only=True).to_frame().T
                subtotal["vl_name"] = vl_name
                subtotal["Week_start"] = "SUBTOTAL"
                
                gp_df = group_df.copy()
                gp_df["Week_start"] = pd.to_datetime(gp_df["Week_start"]).dt.strftime('%d/%m/%Y')
                
                final_vl_rows.append(subtotal)
                final_vl_rows.append(gp_df)
                
            if final_vl_rows:
                vl_res_df = pd.concat(final_vl_rows, ignore_index=True)
                rename_dict = {
                    "Week_start": "Week Start",
                    "active_tcs": "Active TCs",
                    "existing_tcs": "Existing TCs",
                    "resurrected_tcs": "Resurrected TCs",
                    "churned_tcs": "Churned TCs",
                    "new_tcs": "New TCs",
                    "targets": "Targets",
                    "net_new_additions": "Net New Additions"
                }
                vl_res_df = vl_res_df.rename(columns=rename_dict)
                cols_order = ["vl_name", "Week Start", "Active TCs", "Existing TCs", "Resurrected TCs", "Churned TCs", "New TCs", "Targets", "Net New Additions"]
                vl_res_df = vl_res_df[[c for c in cols_order if c in vl_res_df.columns]]
                render_tc_table(vl_res_df, "vl_name")
            else:
                st.info("No Vendor Lines match the selected filters.")

# ==============================================================================
# TAB 3: AI NARRATIVE & RCA
# ==============================================================================
with tab3:
    section("Programmatic Executive Summary & Attribution (Placements Only)")
    
    pool = []
    if not client_mat.empty:
        for _, r in client_mat.iterrows(): pool.append({"type": "Client Profile", "name": r['company_name'], "delta": r["delta"]})
    if not reg_mat.empty:
        for _, r in reg_mat.iterrows():    pool.append({"type": "Regional Cluster", "name": r['region'], "delta": r["delta"]})
    if not vl_master.empty:
        for _, r in vl_master.iterrows():   pool.append({"type": "Vendor Line Partner (VL)", "name": r['vl_name'], "delta": r["delta"]})
    
    m_df = pd.DataFrame(pool, columns=["type", "name", "delta"]).dropna()
    leaders = m_df[m_df["delta"] > 0].nlargest(3, "delta") if not m_df.empty else pd.DataFrame()
    laggards = m_df[m_df["delta"] < 0].nsmallest(3, "delta") if not m_df.empty else pd.DataFrame()
    
    trend_term = "an operational contraction" if dlt_tot < 0 else "an upward expansion trend"
    hl_color = "var(--red)" if dlt_tot < 0 else "var(--green)"
    
    st.markdown(f"""
    <div class="rca-card">
      <div class="rca-ttl">Performance Review Narrative</div>
      <div class="rca-body">
        Data matching current parameters logs {trend_term} yielding a global net variation of 
        <strong style="color:{hl_color}">{fmt(dlt_tot)} total placements (FT)</strong> ({pct_tot:+.1f}%) 
        compared to the relative historical cycle baseline. Absolute volume shifted from <strong>{fmt(prv_tot)}</strong> 
        units to <strong>{fmt(cur_tot)}</strong> active placements inside the evaluated window frame.
      </div>
    </div>""", unsafe_allow_html=True)

    as_left, as_right = st.columns(2)
    with as_left:
        st.markdown('<div class="rca-card"><div class="rca-ttl">Primary Positive Drivers</div>', unsafe_allow_html=True)
        if not leaders.empty:
            for _, r in leaders.iterrows():
                st.markdown(f"""<div class="rca-item"><div class="rca-dot dot-g"></div>
                    <div><strong>[{r['type']}]</strong> {r['name']} — net change of <span style="color:var(--green); font-weight:700;">+{int(r['delta']):,}</span> placements.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted); font-size:12px;">No active vectors recorded growth steps during this cycle.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with as_right:
        st.markdown('<div class="rca-card"><div class="rca-ttl">Primary Deficit Contributors</div>', unsafe_allow_html=True)
        if not laggards.empty:
            for _, r in laggards.iterrows():
                st.markdown(f"""<div class="rca-item"><div class="rca-dot dot-r"></div>
                    <div><strong>[{r['type']}]</strong> {r['name']} — net change of <span style="color:var(--red); font-weight:700;">{int(r['delta']):,}</span> placements.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted); font-size:12px;">No active vectors logged shortfalls during this cycle.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
