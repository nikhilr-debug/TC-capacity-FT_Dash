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
  --r:         10px;
  --rl:        14px;

  --red:       #ff6b6b;
  --red-bg:    rgba(255, 107, 107, 0.15);
  --red-b:     #e05252;
  --amber:     #ffc97a;
  --amber-bg:  #2d1e07;
  --amber-b:   #d4891a;
  --green:     #6dd67b;
  --green-bg:  rgba(109, 214, 123, 0.15);
  --green-b:   #4a9e2f;
  --blue:      #7cb9f8;
  --blue-bg:   #0d1e38;
  --blue-b:    #2f7dd4;
}

/* Base App Theme */
.stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-size: 13px;
  line-height: 1.5;
}

/* -------------------------------------------------------------------------
   STREAMLIT NATIVE SIDEBAR & HEADER SAFE OVERRIDES
------------------------------------------------------------------------- */
/* Style sidebar background natively */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
}

/* Keep header background transparent */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Ensure the native expand/collapse button icons are WHITE so they are visible on dark backgrounds */
header[data-testid="stHeader"] button svg,
[data-testid="stSidebar"] button svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* Hide clutter — but preserve the sidebar collapse/expand toggle */
#MainMenu, footer {
    display: none !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}
/* Restore the sidebar toggle button visibility */
[data-testid="collapsedControl"],
button[kind="header"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}
/* ------------------------------------------------------------------------- */

.block-container {
  padding: 2.5rem 2rem 4rem !important;
  max-width: 1440px !important;
}

div[data-testid="stHorizontalBlock"] { gap: 1rem !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--br2);
}
.dash-title {
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text);
}
.dash-title span { color: var(--blue); }
.dash-meta {
  font-size: 0.8rem;
  color: var(--muted);
  margin-top: 4px;
}

.sec-ttl {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--text);
  margin: 1.75rem 0 1rem;
  display: flex;
  align-items: center;
  gap: 12px;
}
.sec-ttl-line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--br2), transparent); }

.kpi {
  background: var(--surface);
  border: 1px solid var(--br2);
  border-radius: var(--rl);
  padding: 16px 20px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, border-color 0.2s ease;
}
.kpi:hover {
  transform: translateY(-2px);
  border-color: rgba(255,255,255,0.2);
}
.kpi::before {
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:3px;
  background: linear-gradient(90deg, var(--blue-b), #b08cff);
}
.kpi-lbl {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--muted);
  margin-bottom: 8px;
}
.kpi-val {
  font-size: 26px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}
.kpi-sub { 
  font-size: 11.5px; 
  margin-top: 8px; 
  color: var(--muted); 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
  align-items: center;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10.5px;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.02em;
}
.pr { background: var(--red-bg);    color: var(--red);   border: 1px solid rgba(255, 107, 107, 0.2); }
.pg { background: var(--green-bg);  color: var(--green); border: 1px solid rgba(109, 214, 123, 0.2); }
.pz { background: var(--surface3);  color: var(--muted); border: 1px solid var(--br); }
.pb { background: var(--blue-bg);   color: var(--blue);  border: 1px solid rgba(124, 185, 248, 0.2); }

.table-container {
  background: var(--surface);
  border: 1px solid var(--br2);
  border-radius: var(--rl);
  overflow-x: auto;
  margin-bottom: 24px;
  box-shadow: 0 6px 16px -8px rgba(0,0,0,0.3);
}
.dash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
  text-align: left;
}
.dash-table thead {
  background: var(--surface2);
  position: sticky;
  top: 0;
  z-index: 10;
}
.dash-table th {
  padding: 12px 16px;
  font-size: 10.5px;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--br2);
  white-space: nowrap;
}
.dash-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--br);
  color: var(--text);
  white-space: nowrap;
  vertical-align: middle;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table tr:hover td { background: rgba(255, 255, 255, 0.04); }
.n { text-align: right; font-variant-numeric: tabular-nums; }
.td-muted { color: var(--muted); }

button[data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  border-radius: var(--r) !important;
  padding: 8px 20px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--br2) !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}
div[data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border: 1px solid var(--br) !important;
  border-radius: var(--rl) !important;
  padding: 4px !important;
  gap: 4px !important;
}

.rca-card {
  background: var(--surface);
  border: 1px solid var(--br2);
  border-radius: var(--rl);
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.rca-ttl {
  font-size: 14.5px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid var(--br);
  padding-bottom: 10px;
}
.rca-body {
  font-size: 13.5px;
  color: var(--muted);
  line-height: 1.6;
}
.rca-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px 14px;
  background: var(--surface2);
  border-radius: var(--r);
  border-left: 3px solid transparent;
  transition: transform 0.2s ease;
}
.rca-item:hover { transform: translateX(4px); }
.rca-item.positive { border-left-color: var(--green); }
.rca-item.negative { border-left-color: var(--red); }
.rca-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.dot-g { background: var(--green); box-shadow: 0 0 8px rgba(109, 214, 123, 0.4); }
.dot-r { background: var(--red); box-shadow: 0 0 8px rgba(255, 107, 107, 0.4); }
.dot-b { background: var(--blue); box-shadow: 0 0 8px rgba(124, 185, 248, 0.4); }

.inline-filter-container {
    background: var(--surface);
    padding: 12px 20px;
    border-radius: var(--rl);
    border: 1px solid var(--br2);
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

details.vl-expander summary { list-style: none; }
details.vl-expander summary::-webkit-details-marker { display: none; }
.exp-icon {
  display: inline-block;
  width: 16px;
  font-weight: 800;
  color: var(--muted);
  text-align: center;
  margin-right: 4px;
}
details.vl-expander:not([open]) summary .exp-icon::before { content: '+'; }
details.vl-expander[open] summary .exp-icon::before { content: '−'; }
details.vl-expander[open] summary { color: var(--blue) !important; }
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
    
    master_totals = {
        "Overall": [0, 6176, 6459, 7190, 8021, 9326, 10447, 11801, 13180, 14918, 16325, 17783, 18879, 20351, 20851],
        "VL":      [0, 5628, 6167, 6580, 7172, 7887, 8592,  9210, 10065, 11016, 11719, 12694, 13126, 13774, 13829],
        "DC":      [0,  408,  434,  602,  958, 1302, 1893,  2268,  2934,  3637,  4440,  5022,  5735,  6588,  7002]
    }
    
    overall_dict = {
        'Blinkit': [3537, 3537, 3760, 3760, 3760, 3960, 4177, 4277, 4427, 4577, 4829, 4929, 4979, 4979, 4979],
        'Swiggy Food': [887, 1243, 1314, 1428, 1685, 1929, 2171, 2418, 2763, 3019, 3269, 3574, 3876, 4223, 4488],
        'Swiggy IM': [555, 718, 757, 849, 992, 1124, 1264, 1398, 1590, 1738, 1882, 2052, 2221, 2419, 2566],
        'SOC': [37, 37, 77, 112, 187, 262, 312, 387, 487, 587, 587, 637, 637, 687, 687],
        'FKM': [135, 0, 40, 110, 170, 200, 250, 300, 350, 400, 500, 550, 550, 600, 600],
        'Uber': [28, 45, 127, 187, 299, 383, 519, 592, 738, 907, 1115, 1298, 1450, 1603, 1631],
        'Rapido': [0, 0, 75, 200, 300, 380, 500, 600, 700, 800, 900, 1000, 1000, 1000, 0],
        '4W': [50, 67, 97, 115, 167, 194, 261, 298, 381, 456, 570, 640, 740, 800, 828],
        'Picker Packer': [263, 263, 283, 303, 323, 333, 363, 363, 388, 598, 465, 758, 645, 938, 825],
        'Bigbasket': [0, 43, 43, 64, 144, 186, 333, 375, 508, 700, 918, 1000, 1200, 1383, 1463],
        'Amazon': [0, 9, 9, 13, 40, 54, 90, 104, 142, 197, 273, 320, 370, 441, 458],
        'XB': [28, 37, 37, 50, 67, 80, 128, 146, 205, 254, 331, 388, 473, 539, 586],
        'Maid': [80, 80, 100, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 150, 120],
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
    current_sum = 0
    for client, weekly_targets in active_dict.items():
        val = weekly_targets[w_idx]
        compiled_targets.append({"company_name": client, "target": val})
        current_sum += val
        
    expected_total = master_totals[target_type][w_idx]
    gap = expected_total - current_sum
    if gap != 0 and expected_total != 0:
        compiled_targets.append({"company_name": "Target Adjustment (Unallocated)", "target": gap})
        
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
        "Week number": [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
        "Week_start": pd.to_datetime([
            "2026-06-29", "2026-07-06", "2026-07-13", "2026-07-20", "2026-07-27", 
            "2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31", 
            "2026-09-07", "2026-09-14", "2026-09-21", "2026-09-28"
        ]).date,
        "Overall Addition": [115, 53, 92, 213, 55, 246, 46, 44, 338, 20, 33, 0, 0, 0],
        "Existing VL": [35, 38, 52, 40, 30, 21, 26, 24, 18, 10, 0, 0, 0, 0],
        "BPO": [80, 0, 0, 150, 0, 200, 0, 0, 300, 0, 0, 0, 0, 0],
        "DC": [0, 15, 40, 23, 25, 25, 20, 20, 20, 10, 0, 0, 0, 0]
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
            if ce < cs: # Protect against Monday boundary logic
                cs = today - datetime.timedelta(days=dow + 7)
                ce = cs + datetime.timedelta(days=6)
            ps = cs - datetime.timedelta(weeks=1)
            pe = ce - datetime.timedelta(weeks=1)
    else: # MTD
        if exclude_current:
            this_monday = today - datetime.timedelta(days=dow)
            ce = this_monday - datetime.timedelta(days=1)
            cs = ce.replace(day=1)
        else:
            cs = today.replace(day=1)
            ce = yesterday
            if ce < cs:
                pm = today.month - 1 or 12
                py = today.year if today.month > 1 else today.year - 1
                cs = today.replace(year=py, month=pm, day=1)
                ce = yesterday
                
        pm = cs.month - 1 or 12
        py = cs.year if cs.month > 1 else cs.year - 1
        ps = cs.replace(year=py, month=pm, day=1)
        offset = (ce - cs).days
        pe = ps + datetime.timedelta(days=offset)
        
    return cs, ce, ps, pe

cs, ce, ps, pe = get_windows(mode, exclude_current)

st.sidebar.markdown("### 🔍 Placements (FT) Filters")

client_opts = sorted(list(df_base["company_name"].dropna().unique())) if "company_name" in df_base.columns else []
selected_clients = st.sidebar.multiselect("Client Scope", client_opts, key="global_filter_client")

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
    dc_vendors = ["DC", "Direct Channel", "Basu Business Solutions"]
    t_type = "Overall"
    if selected_vls:
        if all(v in dc_vendors for v in selected_vls): t_type = "DC"
        elif all(v not in dc_vendors for v in selected_vls): t_type = "VL"
        
    weeks_in_month = set()
    num_days = (cs.replace(month=cs.month%12+1, day=1) - datetime.timedelta(days=1)).day if cs.month < 12 else 31
    for d in range(1, num_days + 1):
        dt = datetime.date(cs.year, cs.month, d)
        weeks_in_month.add(dt.isocalendar()[1])
    
    tgt_dfs = [fetch_targets_wtd(t_type, w) for w in list(weeks_in_month)]
    if tgt_dfs:
        tgt_base = pd.concat(tgt_dfs).groupby("company_name", as_index=False)["target"].sum()
    else:
        tgt_base = pd.DataFrame()
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

# Enforce strict Exact-Group Target Mapping (Left Join Only)
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
        missing_cols = [k for k in group_cols if k not in target_df.columns]
        if not missing_cols:
            keys_to_merge = group_cols
            t_df_temp = target_df.copy()
            for k in keys_to_merge:
                t_df_temp[k] = t_df_temp[k].fillna("Unattributed").astype(str).str.strip().str.title()
            
            t_agg = t_df_temp.groupby(keys_to_merge)['target'].sum().reset_index()
            
            if not res.empty: 
                res = pd.merge(res, t_agg, on=keys_to_merge, how="left")
            else:
                res["target"] = 0
        else: res["target"] = 0
    else:
        if res.empty: res = pd.DataFrame(columns=group_cols + ["cur", "prv", "l4w", "target"])
        else: res["target"] = 0
            
    for col in ["cur", "prv", "l4w", "target"]:
        if col not in res.columns: res[col] = 0
        res[col] = res[col].fillna(0).astype(int)
        
    res["delta"] = res["cur"] - res["prv"]
    res["pct"] = np.where(res["prv"] > 0, (res["delta"] / res["prv"]) * 100, np.nan)
    
    if remaining_days <= 0:
        res["proj"] = res["cur"]
    else:
        res["proj"] = (res["cur"] + (res["l4w"] / 28.0) * remaining_days).round().astype(int)
        
    res["gap"] = res["proj"] - res["target"]
    res["gap_pct"] = np.where(res["target"] > 0, (res["gap"] / res["target"]) * 100, np.nan)
    
    res["contr"] = 0.0
    sum_pos = res.loc[res['delta'] > 0, 'delta'].sum()
    sum_neg = res.loc[res['delta'] < 0, 'delta'].sum()
    
    if sum_pos > 0: res["contr"] = np.where(res['delta'] > 0, (res['delta'] / sum_pos) * 100, res["contr"])
    if sum_neg < 0: res["contr"] = np.where(res['delta'] < 0, -(res['delta'] / sum_neg) * 100, res["contr"])
    
    return res

def filter_target_df(target_df, col_name, selected_items):
    if col_name in target_df.columns:
        target_df[col_name] = target_df[col_name].fillna("Unattributed").astype(str).str.strip().str.title()
        selected_items_title = [str(x).strip().title() for x in selected_items]
        return target_df[target_df[col_name].isin(selected_items_title)]
    return target_df

# FT Data Application
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

days_elapsed = (ce - cs).days + 1
if mode == "WTD": total_days = 7
else:
    num_days = (cs.replace(month=cs.month%12+1, day=1) - datetime.timedelta(days=1)).day if cs.month < 12 else 31
    total_days = num_days

remaining_days = max(0, total_days - days_elapsed)

# Ensure L4W Baseline accurately calculates up to the start of the current period window
l4w_e = cs - datetime.timedelta(days=1)
l4w_s = l4w_e - datetime.timedelta(days=27)

# ── Header Markup Execution ───────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Vahan <span>Performance Analytics</span> Dashboard</div>
    <div class="dash-meta"><span class="live-dot"></span>Live Lookback Tracking · Active Bounds as of {ce.strftime('%b %d')}</div>
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
    if delta > 0: return f'<span style="color:var(--green); font-size:10.5px; font-weight:700;">{abs(contr):.1f}% Grw</span>'
    return f'<span style="color:var(--red); font-size:10.5px; font-weight:700;">{abs(contr):.1f}% Dip</span>'

def kpi_html(label, value, sub="", pill_html=""):
    return f"""
    <div class="kpi">
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-sub">{sub} {pill_html}</div>
    </div>"""

def section(title):
    st.markdown(f'<div class="sec-ttl">{title}<div class="sec-ttl-line"></div></div>', unsafe_allow_html=True)

# ── Primary Metric Matrices Engine Calculations ──────────────────────────────
cur_tot = len(df[(df[ft] >= cs) & (df[ft] <= ce)]) if ft in df.columns else 0
prv_tot = len(df[(df[ft] >= ps) & (df[ft] <= pe)]) if ft in df.columns else 0
l4w_tot = len(df[(df[ft] >= l4w_s) & (df[ft] <= l4w_e)]) if ft in df.columns else 0

dlt_tot = cur_tot - prv_tot
pct_tot = (dlt_tot / prv_tot * 100) if prv_tot > 0 else np.nan
daily_rr = l4w_tot / 28.0

if remaining_days <= 0:
    proj_tot = cur_tot
else:
    proj_tot = int(round(cur_tot + daily_rr * remaining_days))

client_mat = compute_comparison_matrix(df, "company_name", t_df)
vl_master = compute_comparison_matrix(df, "vl_name", t_df)
vl_by_client_mat = compute_comparison_matrix(df, ["vl_name", "company_name"], t_df)
reg_mat = compute_comparison_matrix(df, "region", t_df)

total_target = int(t_df['target'].sum()) if not t_df.empty else 0
gap_tot = proj_tot - total_target
gap_tot_pct = (gap_tot / total_target * 100) if total_target > 0 else np.nan

# ==============================================================================
# TAB 1: FT VIEW
# ==============================================================================
tab1, tab2, tab3 = st.tabs(["📦 FT View", "⚡ TC Capacity", "🤖 AI Narrative"])

with tab1:
    k1, k2, k3, k4, k5 = st.columns(5)
    k_color = "var(--green)" if dlt_tot >= 0 else "var(--red)"
    g_color = "var(--green)" if gap_tot >= 0 else "var(--red)"
    
    with k1: 
        pills = volume_pill(dlt_tot) + " " + pill_markup(pct_tot)
        st.markdown(kpi_html("Current Period FT", f'<span style="color:{k_color}">{fmt(cur_tot)}</span>', pill_html=pills), unsafe_allow_html=True)
    with k2: 
        st.markdown(kpi_html("Projected FT", fmt(proj_tot), sub=f"Entering Pace: {daily_rr:.1f} FT/d"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_html("Previous Period FT", fmt(prv_tot), sub="Historical Baseline"), unsafe_allow_html=True)
    with k4: 
        st.markdown(kpi_html("Final Target FT", fmt(total_target), sub="Segment Quota"), unsafe_allow_html=True)
    with k5: 
        st.markdown(kpi_html("Target Gap (Proj)", f'<span style="color:{g_color}">{fmt(gap_tot)}</span>', pill_html=pill_markup(gap_tot_pct)), unsafe_allow_html=True)

    # --- SPOTLIGHT FEATURE: TOP 5 MOVERS (FT) ---
    section("🔍 Spotlight: Top 5 Contribution Movers")
    m_col1, m_col2 = st.columns(2)
    
    def generate_movers_html(df, name_col, title):
        if df.empty: return ""
        
        pos_mask = df['delta'] > 0
        neg_mask = df['delta'] < 0
        total_growth = df[pos_mask]['delta'].sum()
        total_drop = df[neg_mask]['delta'].sum()
        
        growers = df[pos_mask].sort_values('delta', ascending=False).head(5)
        decliners = df[neg_mask].sort_values('delta', ascending=True).head(5)
        
        html = f'<div class="rca-card" style="padding:20px; margin-bottom:0; height:100%;"><div class="rca-ttl" style="font-size:13px; border-bottom:none; padding-bottom:4px; margin-bottom:12px;">{title}</div>'
        html += '<div style="display:flex; gap:20px;">'
        
        # Growers Column
        html += '<div style="flex:1;">'
        html += '<div style="font-size:10.5px; color:var(--green); font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">📈 Top 5 Expansion</div>'
        if not growers.empty:
            for _, r in growers.iterrows():
                pct_contr = (r["delta"] / total_growth * 100) if total_growth else 0
                html += f'<div style="display:flex; justify-content:space-between; align-items:center; font-size:12.5px; padding:6px 0; border-bottom:1px dashed var(--br);"><span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:65%; font-weight:500;" title="{r[name_col]}">{r[name_col]}</span><div style="text-align:right; display:flex; align-items:center; gap:6px;"><span style="color:var(--green); font-weight:800;">+{int(r["delta"])}</span><span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{pct_contr:.1f}%</span></div></div>'
        else:
            html += '<div style="font-size:12px; color:var(--muted); padding:8px 0;">No expansion recorded.</div>'
        html += '</div>'
        
        # Decliners Column
        html += '<div style="flex:1;">'
        html += '<div style="font-size:10.5px; color:var(--red); font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">📉 Top 5 Contraction</div>'
        if not decliners.empty:
            for _, r in decliners.iterrows():
                pct_contr = (r["delta"] / total_drop * 100) if total_drop else 0
                html += f'<div style="display:flex; justify-content:space-between; align-items:center; font-size:12.5px; padding:6px 0; border-bottom:1px dashed var(--br);"><span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:65%; font-weight:500;" title="{r[name_col]}">{r[name_col]}</span><div style="text-align:right; display:flex; align-items:center; gap:6px;"><span style="color:var(--red); font-weight:800;">{int(r["delta"])}</span><span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{pct_contr:.1f}%</span></div></div>'
        else:
            html += '<div style="font-size:12px; color:var(--muted); padding:8px 0;">No contraction recorded.</div>'
        html += '</div>'
        
        html += '</div></div>'
        return html
        
    def generate_vl_movers_html(vl_df, vl_client_df, title="Vendor Line (VL) Drop Spotlight"):
        if vl_df.empty: return ""
        
        neg_mask = vl_df['delta'] < 0
        total_drop = vl_df[neg_mask]['delta'].sum()
        decliners = vl_df[neg_mask].sort_values('delta', ascending=True).head(5)

        html = f'<div class="rca-card" style="padding:20px; margin-bottom:0; height:100%;"><div class="rca-ttl" style="font-size:13px; border-bottom:none; padding-bottom:4px; margin-bottom:12px;">{title}</div>'
        html += '<div style="font-size:10.5px; color:var(--red); font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">📉 Top 5 Overall Contractions</div>'

        if not decliners.empty:
            for _, r in decliners.iterrows():
                vl_name = r["vl_name"]
                vl_delta = int(r["delta"])
                pct_contr = (vl_delta / total_drop * 100) if total_drop else 0

                c_breakdown = vl_client_df[(vl_client_df["vl_name"] == vl_name) & (vl_client_df["delta"] != 0)].sort_values('delta', ascending=True)

                html += '<details class="vl-expander" style="margin-bottom: 8px; border-bottom: 1px dashed var(--br); padding-bottom: 6px;">'
                html += '<summary style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-size: 12.5px; font-weight: 600; color: var(--text); outline: none;">'
                html += f'<div style="display:flex; align-items:center; max-width:65%;"><span class="exp-icon"></span><span title="{vl_name}" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:inline-block; vertical-align:bottom;">{vl_name}</span></div>'
                html += f'<div style="text-align:right; display:flex; align-items:center; gap:6px;"><span style="color:var(--red); font-weight:800;">{vl_delta}</span><span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{pct_contr:.1f}%</span></div>'
                html += '</summary>'
                
                html += '<div style="padding-top: 8px; padding-left: 20px; font-size: 11.5px; color: var(--muted);">'
                if not c_breakdown.empty:
                    for _, cr in c_breakdown.iterrows():
                        c_name = cr["company_name"]
                        c_delta = int(cr["delta"])
                        c_col = "var(--green)" if c_delta > 0 else "var(--red)"
                        c_sign = "+" if c_delta > 0 else ""
                        html += f'<div style="display:flex; justify-content:space-between; margin-bottom: 4px;"><span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:80%;" title="{c_name}">{c_name}</span><span style="color:{c_col}; font-weight:600;">{c_sign}{c_delta}</span></div>'
                else:
                    html += '<div style="margin-bottom: 4px;">No client-level variance data available.</div>'
                html += '</div></details>'
        else:
            html += '<div style="font-size:12px; color:var(--muted); padding:8px 0;">No contraction recorded.</div>'

        html += '</div>'
        return html

    with m_col1:
        st.markdown(generate_movers_html(client_mat, "company_name", "Client Profile Movers"), unsafe_allow_html=True)
    with m_col2:
        st.markdown(generate_vl_movers_html(vl_master, vl_by_client_mat, "Vendor Line (VL) Drop Spotlight"), unsafe_allow_html=True)

    if mode == "WTD" and ft in df.columns:
        df_trend = df.copy()
        df_trend['datetime'] = pd.to_datetime(df_trend[ft])
        df_trend['Week_Start'] = df_trend['datetime'].dt.to_period('W').dt.start_time.dt.date
        
        this_week_monday = ce - datetime.timedelta(days=ce.weekday())
        df_trend = df_trend[df_trend['Week_Start'] <= this_week_monday]
            
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

    if not client_mat.empty:
        section("All Clients Performance Analysis")
        
        c_cols = st.columns([2, 3, 5])
        c_sort_opt = ["Cur", "Proj", "Prv", "Target", "Gap", "Δ Vol", "Δ %", "Client Name", "Contribution"]
        c_sort = c_cols[0].selectbox("Sort Table By", c_sort_opt, index=0, key="cl_main_sort")
        c_asc = c_cols[1].radio("Table Order", ["Descending", "Ascending"], horizontal=True, key="cl_main_ord") == "Ascending"

        sort_map = {"Client Name": "company_name", "Cur": "cur", "Proj": "proj", "Prv": "prv", "Target": "target", "Gap": "gap", "Δ Vol": "delta", "Δ %": "pct", "Contribution": "contr"}
        client_mat = client_mat.sort_values(sort_map[c_sort], ascending=c_asc)

        t_html = '<div class="table-container"><table class="dash-table"><thead><tr>'
        t_html += '<th style="width:20%;">Client Name</th><th class="n" style="width:10%;">Cur</th><th class="n" style="width:10%;">Proj</th><th class="n" style="width:10%;">Prv</th><th class="n" style="width:10%;">Target</th><th class="n" style="width:10%;">Gap</th><th class="n" style="width:10%;">Δ Vol</th><th class="n" style="width:10%;">Δ %</th><th class="n" style="width:10%;">Contribution</th>'
        t_html += '</tr></thead><tbody>'
        
        for _, r in client_mat.iterrows():
            c_color = "var(--green)" if r['delta'] >= 0 else "var(--red)"
            g_color = "var(--green)" if r['gap'] >= 0 else "var(--red)"
            t_html += f"""<tr>
                <td style="width:20%; font-weight:600;">{r['company_name']}</td>
                <td class="n" style="width:10%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:10%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['prv'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['target'])}</td>
                <td class="n" style="width:10%; font-weight:600; color:{g_color};">{fmt(r['gap'])}<br><div style="margin-top:4px;">{pill_markup(r['gap_pct'])}</div></td>
                <td class="n" style="width:10%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:10%;">{pill_markup(r['pct'])}</td>
                <td class="n" style="width:10%;">{contr_markup(r['delta'], r['contr'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)
        
    if not reg_mat.empty:
        section("Overall Regional Performance Analysis")
        
        r_cols = st.columns([2, 3, 5])
        r_sort_opt = ["Cur", "Proj", "Prv", "Target", "Gap", "Δ Vol", "Δ %", "Region", "Contribution"]
        r_sort = r_cols[0].selectbox("Sort Table By", r_sort_opt, index=0, key="reg_main_sort")
        r_asc = r_cols[1].radio("Table Order", ["Descending", "Ascending"], horizontal=True, key="reg_main_ord") == "Ascending"

        sort_map_reg = {"Region": "region", "Cur": "cur", "Proj": "proj", "Prv": "prv", "Target": "target", "Gap": "gap", "Δ Vol": "delta", "Δ %": "pct", "Contribution": "contr"}
        reg_mat = reg_mat.sort_values(sort_map_reg[r_sort], ascending=r_asc)

        t_html = '<div class="table-container"><table class="dash-table"><thead><tr>'
        t_html += '<th style="width:20%;">Region</th><th class="n" style="width:10%;">Cur</th><th class="n" style="width:10%;">Proj</th><th class="n" style="width:10%;">Prv</th><th class="n" style="width:10%;">Target</th><th class="n" style="width:10%;">Gap</th><th class="n" style="width:10%;">Δ Vol</th><th class="n" style="width:10%;">Δ %</th><th class="n" style="width:10%;">Contribution</th>'
        t_html += '</tr></thead><tbody>'
        
        for _, r in reg_mat.iterrows():
            c_color = "var(--green)" if r['delta'] >= 0 else "var(--red)"
            g_color = "var(--green)" if r['gap'] >= 0 else "var(--red)"
            t_html += f"""<tr>
                <td style="width:20%; font-weight:600;">{r['region']}</td>
                <td class="n" style="width:10%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:10%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['prv'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['target'])}</td>
                <td class="n" style="width:10%; font-weight:600; color:{g_color};">{fmt(r['gap'])}<br><div style="margin-top:4px;">{pill_markup(r['gap_pct'])}</div></td>
                <td class="n" style="width:10%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:10%;">{pill_markup(r['pct'])}</td>
                <td class="n" style="width:10%;">{contr_markup(r['delta'], r['contr'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

    if not vl_by_client_mat.empty:
        section("Dynamic Vendor Line (VL) Analytics Tracker (By Client)")
        
        v_col1, v_col2, v_col3, v_col4 = st.columns([1, 1, 1, 2])
        ft_n_vls = v_col1.number_input("Display Top N (FT)", min_value=1, max_value=100, value=15, key="ft_top_n_vls")
        tracker_sort = v_col2.selectbox("Sort Priority By", ["Cur Volume", "Δ Vol (Delta)", "Gap vs Target", "Vendor Line (VL)"], index=1, key="ft_vl_sort")
        tracker_trend = v_col3.radio("Trend View", ["Top Performers", "Bottom Performers"], horizontal=True, key="ft_vl_trend")
        tracker_asc = True if "Bottom" in tracker_trend else False
        
        ft_client_opts = sorted(vl_by_client_mat["company_name"].dropna().unique()) if "company_name" in vl_by_client_mat.columns else []
        ft_clients_flt = v_col4.multiselect("Filter by Client Profile", ft_client_opts, key="ft_vl_client_flt")
        
        vl_map = {"Cur Volume": "cur", "Δ Vol (Delta)": "delta", "Gap vs Target": "gap", "Vendor Line (VL)": "vl_name"}
        
        tmp_vl_mat = vl_by_client_mat.copy()
        if ft_clients_flt and "company_name" in tmp_vl_mat.columns:
            tmp_vl_mat = tmp_vl_mat[tmp_vl_mat["company_name"].isin(ft_clients_flt)]
            
        vl_by_client_mat_disp = tmp_vl_mat.sort_values(vl_map[tracker_sort], ascending=tracker_asc).head(ft_n_vls)
        
        t_html = '<div class="table-container"><table class="dash-table"><thead><tr>'
        t_html += '<th style="width:16%;">Vendor Line (VL)</th><th style="width:14%;">Client</th><th class="n" style="width:10%;">Cur</th><th class="n" style="width:10%;">Proj</th><th class="n" style="width:10%;">Prv</th><th class="n" style="width:10%;">Target</th><th class="n" style="width:10%;">Gap</th><th class="n" style="width:10%;">Δ Vol</th><th class="n" style="width:10%;">Contribution</th>'
        t_html += '</tr></thead><tbody>'
        
        for _, r in vl_by_client_mat_disp.iterrows():
            c_color = "var(--green)" if r['delta'] >= 0 else "var(--red)"
            g_color = "var(--green)" if r['gap'] >= 0 else "var(--red)"
            t_html += f"""<tr>
                <td style="width:16%; font-weight:600;">{r['vl_name']}</td>
                <td style="width:14%; color:var(--muted);">{r['company_name']}</td>
                <td class="n" style="width:10%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:10%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['prv'])}</td>
                <td class="n" style="width:10%; color:var(--muted);">{fmt(r['target'])}</td>
                <td class="n" style="width:10%; font-weight:600; color:{g_color};">{fmt(r['gap'])}<br><div style="margin-top:4px;">{pill_markup(r['gap_pct'])}</div></td>
                <td class="n" style="width:10%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:10%;">{contr_markup(r['delta'], r['contr'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)
        
        with st.expander("📍 Expand for Regional Execution View"):
            rc_cols = st.columns([2, 3, 5])
            r_sort = rc_cols[0].selectbox("Sort Priority By", ["Cur Volume", "Δ Vol (Delta)", "Gap vs Target", "Region"], index=1, key="reg_client_sort")
            r_asc = rc_cols[1].radio("Trend View", ["Descending", "Ascending"], horizontal=True, key="reg_client_ord") == "Ascending"

            reg_client_mat = compute_comparison_matrix(df, ["region", "company_name"], t_df)
            r_map = {"Cur Volume": "cur", "Δ Vol (Delta)": "delta", "Gap vs Target": "gap", "Region": "region"}
            reg_client_mat = reg_client_mat.sort_values(r_map[r_sort], ascending=r_asc)
            
            t_html = '<div class="table-container"><table class="dash-table"><thead><tr>'
            t_html += '<th style="width:15%;">Region</th><th style="width:15%;">Client Profile</th><th class="n" style="width:10%;">Cur</th><th class="n" style="width:10%;">Proj</th><th class="n" style="width:10%;">Prv</th><th class="n" style="width:10%;">Target</th><th class="n" style="width:10%;">Gap</th><th class="n" style="width:10%;">Δ Vol</th><th class="n" style="width:10%;">Contribution</th>'
            t_html += '</tr></thead><tbody>'
            
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
                    <td class="n" style="width:10%; font-weight:600; color:{g_color};">{fmt(r['gap'])}<br><div style="margin-top:4px;">{pill_markup(r['gap_pct'])}</div></td>
                    <td class="n" style="width:10%;">{volume_pill(r['delta'])}</td>
                    <td class="n" style="width:10%;">{contr_markup(r['delta'], r['contr'])}</td>
                </tr>"""
            t_html += "</tbody></table></div>"
            st.markdown(t_html, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: TC Capacity VIEW
# ==============================================================================
with tab2:
    all_weeks = sorted(df_tc_raw["Week_start"].dropna().unique(), reverse=True) if "Week_start" in df_tc_raw.columns else []
    
    # TC Global Week Filter
    st.markdown('<div class="inline-filter-container">', unsafe_allow_html=True)
    
    # ── Smart Current Week Exclusion Check ──
    this_monday = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    if exclude_current:
        all_weeks = [w for w in all_weeks if w < this_monday]
        
    tc_sel_weeks = st.multiselect("📅 Select Trailing Weeks (Applies globally to all TC Views)", all_weeks, default=all_weeks[:tc_time_filter], key="tc_global_week_filter")
    st.markdown('</div>', unsafe_allow_html=True)

    df_tc_filtered = df_tc.copy()
    if tc_sel_weeks: 
        df_tc_filtered = df_tc_filtered[df_tc_filtered["Week_start"].isin(tc_sel_weeks)]

    if mode == "MTD":
        month_target_weeks = [w for w in all_weeks if w.month == cs.month and w.year == cs.year]
        tc_month_targets = df_tc_targets[df_tc_targets["Week_start"].isin(month_target_weeks)]
        overall_target = tc_month_targets["Overall Addition"].sum() if not tc_month_targets.empty else 0
        
        cur_wk_data = df_tc_filtered[pd.to_datetime(df_tc_filtered["Week_start"]).dt.month == cs.month]
        tc_display_date = cs.strftime('%b %Y')
        
        kpi_new = cur_wk_data["new_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_resurrected = cur_wk_data["resurrected_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_churned = cur_wk_data["churned_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_net_additions = cur_wk_data["net_new_additions"].sum() if not cur_wk_data.empty else 0
        
        if not cur_wk_data.empty:
            latest_week = cur_wk_data["Week_start"].max()
            latest_wk_data = cur_wk_data[cur_wk_data["Week_start"] == latest_week]
            kpi_active = latest_wk_data["active_tcs"].sum()
            kpi_existing = latest_wk_data["existing_tcs"].sum()
        else:
            kpi_active = 0
            kpi_existing = 0
    else:
        cur_wk_date = tc_sel_weeks[0] if tc_sel_weeks else (all_weeks[0] if all_weeks else None)
        cur_wk_data = df_tc_filtered[df_tc_filtered["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
        
        target_row = df_tc_targets[df_tc_targets["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
        overall_target = target_row["Overall Addition"].values[0] if not target_row.empty else 0
        tc_display_date = str(cur_wk_date)
        
        kpi_new = cur_wk_data["new_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_resurrected = cur_wk_data["resurrected_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_churned = cur_wk_data["churned_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_active = cur_wk_data["active_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_existing = cur_wk_data["existing_tcs"].sum() if not cur_wk_data.empty else 0
        kpi_net_additions = cur_wk_data["net_new_additions"].sum() if not cur_wk_data.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)

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
        col.markdown(f'<div class="kpi" style="padding:14px;"><div class="kpi-lbl" style="font-size:10px;">{label} <br><span style="color:var(--faint); font-weight:500; font-size:9.5px; text-transform:none;">Time: {tc_display_date}</span></div><div class="kpi-val" style="font-size:22px; color:{text_color}; margin-top:6px;">{val:,}</div></div>', unsafe_allow_html=True)

    section("🔍 Spotlight: Top 5 Contribution Movers (TC Capacity)")
    tc_m_col1, tc_m_col2 = st.columns(2)
    
    def generate_tc_movers_html(df, name_col, title):
        if df.empty or "net_new_additions" not in df.columns: return ""
        
        pos_mask = df['net_new_additions'] > 0
        neg_mask = df['net_new_additions'] < 0
        total_growth = df[pos_mask]['net_new_additions'].sum()
        total_drop = df[neg_mask]['net_new_additions'].sum()
        
        growers = df[pos_mask].sort_values('net_new_additions', ascending=False).head(5)
        decliners = df[neg_mask].sort_values('net_new_additions', ascending=True).head(5)
        
        html = f'<div class="rca-card" style="padding:20px; margin-bottom:0; height:100%;"><div class="rca-ttl" style="font-size:13px; border-bottom:none; padding-bottom:4px; margin-bottom:12px;">{title}</div>'
        html += '<div style="display:flex; gap:20px;">'
        
        html += '<div style="flex:1;">'
        html += '<div style="font-size:10.5px; color:var(--green); font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">📈 Top 5 Net Additions</div>'
        if not growers.empty:
            for _, r in growers.iterrows():
                pct_contr = (r["net_new_additions"] / total_growth * 100) if total_growth else 0
                html += f'<div style="display:flex; justify-content:space-between; align-items:center; font-size:12.5px; padding:6px 0; border-bottom:1px dashed var(--br);"><span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:65%; font-weight:500;" title="{r[name_col]}">{r[name_col]}</span><div style="text-align:right; display:flex; align-items:center; gap:6px;"><span style="color:var(--green); font-weight:800;">+{int(r["net_new_additions"])}</span><span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{pct_contr:.1f}%</span></div></div>'
        else:
            html += '<div style="font-size:12px; color:var(--muted); padding:8px 0;">No additions recorded.</div>'
        html += '</div>'
        
        html += '<div style="flex:1;">'
        html += '<div style="font-size:10.5px; color:var(--red); font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">📉 Top 5 Net Churn</div>'
        if not decliners.empty:
            for _, r in decliners.iterrows():
                pct_contr = (r["net_new_additions"] / total_drop * 100) if total_drop else 0
                html += f'<div style="display:flex; justify-content:space-between; align-items:center; font-size:12.5px; padding:6px 0; border-bottom:1px dashed var(--br);"><span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:65%; font-weight:500;" title="{r[name_col]}">{r[name_col]}</span><div style="text-align:right; display:flex; align-items:center; gap:6px;"><span style="color:var(--red); font-weight:800;">{int(r["net_new_additions"])}</span><span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{pct_contr:.1f}%</span></div></div>'
        else:
            html += '<div style="font-size:12px; color:var(--muted); padding:8px 0;">No churn recorded.</div>'
        html += '</div>'
        
        html += '</div></div>'
        return html

    if not df_tc_filtered.empty:
        spot_data = cur_wk_data if mode == "MTD" else df_tc_filtered[df_tc_filtered["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
        
        if not spot_data.empty:
            tc_ch = spot_data.groupby("Channel")["net_new_additions"].sum().reset_index().rename(columns={"Channel": "name"})
            tc_ch["name"] = "[Channel] " + tc_ch["name"].astype(str)
            
            tc_reg = spot_data.groupby("region")["net_new_additions"].sum().reset_index().rename(columns={"region": "name"})
            tc_reg["name"] = "[Region] " + tc_reg["name"].astype(str)
            
            tc_coh = spot_data.groupby("cohort")["net_new_additions"].sum().reset_index().rename(columns={"cohort": "name"})
            tc_coh["name"] = "[Cohort] " + tc_coh["name"].astype(str)
            
            tc_combined = pd.concat([tc_ch, tc_reg, tc_coh], ignore_index=True)
            tc_vl = spot_data.groupby("vl_name")["net_new_additions"].sum().reset_index().rename(columns={"vl_name": "name"})
            
            with tc_m_col1:
                st.markdown(generate_tc_movers_html(tc_combined, "name", "Segment Movers (Channel, Region & Cohort)"), unsafe_allow_html=True)
            with tc_m_col2:
                st.markdown(generate_tc_movers_html(tc_vl, "name", "Vendor Line (VL) Movers"), unsafe_allow_html=True)

    st.markdown('<div class="sec-ttl" style="margin-top: 2rem;">Detailed Analytical Modals (Grouped Pivot Views)</div>', unsafe_allow_html=True)

    def style_tc_dataframe(dataframe, group_col):
        unique_groups = dataframe[group_col].unique()
        def highlight_rows(row):
            if row["Week Start"] == "-": 
                return ["background-color: var(--surface2); color: var(--text); font-weight: 800; border-top: 2px solid rgba(255,255,255,0.1)"] * len(row)
            elif row["Week Start"] == "SUBTOTAL":
                return ["background-color: rgba(255,255,255,0.04); font-weight: 700; border-top: 1px dashed rgba(255,255,255,0.1); border-bottom: 1px solid rgba(255,255,255,0.1)"] * len(row)
            try:
                idx = list(unique_groups).index(row[group_col])
                bg = "background-color: rgba(255,255,255,0.015)" if idx % 2 == 0 else "background-color: transparent"
                return [bg] * len(row)
            except:
                return [""] * len(row)
                
        def format_net_adds(val):
            if isinstance(val, (int, float)):
                if val > 0: return 'color: #6dd67b; font-weight: 700; background-color: rgba(109, 214, 123, 0.05);'
                elif val < 0: return 'color: #ff6b6b; font-weight: 700; background-color: rgba(255, 107, 107, 0.05);'
            return ''
            
        format_dict = {c: "{:,.0f}" for c in dataframe.columns if c not in [group_col, "Week Start"]}
        return dataframe.style.format(format_dict).apply(highlight_rows, axis=1).map(format_net_adds, subset=["Net New Additions"])

    def get_standard_table(dataframe, group_col):
        if dataframe.empty or group_col not in dataframe.columns or "Week_start" not in dataframe.columns: 
            return pd.DataFrame()
        
        agg = dataframe.groupby([group_col, "Week_start"])[["active_tcs", "existing_tcs", "resurrected_tcs", "churned_tcs", "new_tcs", "net_new_additions"]].sum().reset_index()
        
        if group_col == "Channel":
            def get_target(row):
                w = row["Week_start"]
                c = row["Channel"]
                tgt_row = df_tc_targets[df_tc_targets["Week_start"] == w]
                if tgt_row.empty: return 0
                if c in tgt_row.columns: return int(tgt_row[c].values[0])
                return 0
            agg["targets"] = agg.apply(get_target, axis=1)
        else:
            agg["targets"] = 0
            
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
        return res_df[[c for c in cols_order if c in res_df.columns]]

    with st.expander("📊 Channel View Drill-down", expanded=True):
        c1, c2 = st.columns(2)
        loc_chan_weeks = c1.multiselect("Weeks (Channel View)", all_weeks, default=all_weeks[:tc_time_filter], key="cw")
        chan_opts = sorted(df_tc_filtered["Channel"].dropna().unique()) if "Channel" in df_tc_filtered.columns else []
        loc_chans = c2.multiselect("Channels", chan_opts, default=chan_opts, key="cc")
        
        tmp = df_tc.copy()
        if loc_chan_weeks: tmp = tmp[tmp["Week_start"].isin(loc_chan_weeks)]
        if loc_chans: tmp = tmp[tmp["Channel"].isin(loc_chans)]
        
        df_channel = get_standard_table(tmp, "Channel")
        if not df_channel.empty:
            st.dataframe(style_tc_dataframe(df_channel, "Channel"), width="stretch", hide_index=True)
            
    with st.expander("📍 Region View Drill-down"):
        c1, c2 = st.columns(2)
        loc_reg_weeks = c1.multiselect("Weeks (Region View)", all_weeks, default=all_weeks[:tc_time_filter], key="rw")
        reg_opts = sorted(df_tc_filtered["region"].dropna().unique()) if "region" in df_tc_filtered.columns else []
        loc_regs = c2.multiselect("Regions", reg_opts, default=reg_opts, key="rr")
        
        tmp = df_tc.copy()
        if loc_reg_weeks: tmp = tmp[tmp["Week_start"].isin(loc_reg_weeks)]
        if loc_regs: tmp = tmp[tmp["region"].isin(loc_regs)]
        
        df_region = get_standard_table(tmp, "region")
        if not df_region.empty:
            st.dataframe(style_tc_dataframe(df_region, "region"), width="stretch", hide_index=True)
            
    with st.expander("👥 Cohort View Drill-down"):
        c1, c2 = st.columns(2)
        loc_coh_weeks = c1.multiselect("Weeks (Cohort View)", all_weeks, default=all_weeks[:tc_time_filter], key="cow")
        coh_opts = sorted(df_tc_filtered["cohort"].dropna().unique()) if "cohort" in df_tc_filtered.columns else []
        loc_cohs = c2.multiselect("Cohorts", coh_opts, default=coh_opts, key="coc")
        
        tmp = df_tc.copy()
        if loc_coh_weeks: tmp = tmp[tmp["Week_start"].isin(loc_coh_weeks)]
        if loc_cohs: tmp = tmp[tmp["cohort"].isin(loc_cohs)]
        
        df_cohort = get_standard_table(tmp, "cohort")
        if not df_cohort.empty:
            st.dataframe(style_tc_dataframe(df_cohort, "cohort"), width="stretch", hide_index=True)
        
    with st.expander("🏆 Top N VLs Configurable View"):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        tc_n_vls = col1.number_input("Display Top N (TC)", min_value=1, max_value=50, value=10)
        tc_sort_col = col2.selectbox("Sort Priority By", ["net_new_additions", "active_tcs", "new_tcs", "churned_tcs", "existing_tcs"], index=0)
        tc_trend = col3.radio("Trend View (TC)", ["Top Performers", "Bottom Performers"], horizontal=True)
        
        c5, c6 = st.columns(2)
        loc_top_weeks = c5.multiselect("Weeks (Top VLs View)", all_weeks, default=all_weeks[:tc_time_filter], key="tw")
        tc_channel_opts = sorted(df_tc_filtered["Channel"].dropna().unique()) if "Channel" in df_tc_filtered.columns else []
        tc_channels_flt = c6.multiselect("Filter by Channel", tc_channel_opts, key="tc_exp_chan")
        
        tmp_tc = df_tc.copy()
        if loc_top_weeks: tmp_tc = tmp_tc[tmp_tc["Week_start"].isin(loc_top_weeks)]
        if tc_channels_flt and "Channel" in tmp_tc.columns:
            tmp_tc = tmp_tc[tmp_tc["Channel"].isin(tc_channels_flt)]
            
        if not tmp_tc.empty and "Week_start" in tmp_tc.columns:
            is_tc_asc = True if "Bottom" in tc_trend else False
            vl_totals = tmp_tc.groupby("vl_name")[tc_sort_col].sum().reset_index()
            top_vls = vl_totals.sort_values(by=tc_sort_col, ascending=is_tc_asc).head(tc_n_vls)["vl_name"].tolist()
            
            tmp_tc = tmp_tc[tmp_tc["vl_name"].isin(top_vls)]
            tmp_tc["vl_name"] = pd.Categorical(tmp_tc["vl_name"], categories=top_vls, ordered=True)
            
            df_vl = get_standard_table(tmp_tc, "vl_name")
            if not df_vl.empty:
                st.dataframe(style_tc_dataframe(df_vl, "vl_name"), width="stretch", hide_index=True)
        else:
            st.info("No Vendor Lines match the selected filters.")

# ==============================================================================
# TAB 3: AI NARRATIVE & RCA
# ==============================================================================
with tab3:
    ai_col1, ai_col2 = st.columns(2)
    
    # --- FT PLACEMENTS INSIGHTS ---
    with ai_col1:
        section("📦 Programmatic Placements Execution (FT)")
        
        pool = []
        if not client_mat.empty:
            for _, r in client_mat.iterrows(): pool.append({"type": "Client Profile", "name": r['company_name'], "delta": r["delta"]})
        if not reg_mat.empty:
            for _, r in reg_mat.iterrows():    pool.append({"type": "Regional Cluster", "name": r['region'], "delta": r["delta"]})
        if not vl_master.empty:
            for _, r in vl_master.iterrows():   pool.append({"type": "Vendor Line Partner", "name": r['vl_name'], "delta": r["delta"]})
        
        m_df = pd.DataFrame(pool, columns=["type", "name", "delta"]).dropna()
        leaders = m_df[m_df["delta"] > 0].nlargest(3, "delta") if not m_df.empty else pd.DataFrame()
        laggards = m_df[m_df["delta"] < 0].nsmallest(3, "delta") if not m_df.empty else pd.DataFrame()
        
        trend_term = "an operational contraction" if dlt_tot < 0 else "an upward expansion trend"
        hl_color = "var(--red)" if dlt_tot < 0 else "var(--green)"
        
        st.markdown(f"""
        <div class="rca-card">
          <div class="rca-ttl">Placement Trend Diagnostic</div>
          <div class="rca-body">
            Filtered pipeline vectors indicate {trend_term}, executing a net delta of 
            <strong style="color:{hl_color}">{fmt(dlt_tot)} total placements</strong> ({pct_tot:+.1f}%) 
            against the historical comparative baseline. Overall supply transitioned from <strong>{fmt(prv_tot)}</strong> 
            to <strong>{fmt(cur_tot)}</strong> successful operations inside the evaluated timeframe.
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="rca-card"><div class="rca-ttl">Leading Pipeline Drivers</div>', unsafe_allow_html=True)
        if not leaders.empty:
            for _, r in leaders.iterrows():
                st.markdown(f"""<div class="rca-item positive"><div class="rca-dot dot-g"></div>
                    <div><strong>[{r['type']}]</strong> {r['name']} <br> Net yield of <span style="color:var(--green); font-weight:700;">+{int(r['delta']):,}</span> surplus placements.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted); font-size:12px;">No growth vectors successfully recorded in current scope.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="rca-card"><div class="rca-ttl">Primary Deficit Constrictions</div>', unsafe_allow_html=True)
        if not laggards.empty:
            for _, r in laggards.iterrows():
                st.markdown(f"""<div class="rca-item negative"><div class="rca-dot dot-r"></div>
                    <div><strong>[{r['type']}]</strong> {r['name']} <br> Contracted by <span style="color:var(--red); font-weight:700;">{int(r['delta']):,}</span> placements.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted); font-size:12px;">No major deficit constraints detected across active vectors.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TC CAPACITY INSIGHTS ---
    with ai_col2:
        section("⚡ Capacity & Acquisition Trajectory (TC)")
        
        if not df_tc_filtered.empty and "Week_start" in df_tc_filtered.columns:
            tc_target_met = kpi_net_additions - overall_target
            tc_term = "surpassed" if tc_target_met >= 0 else "underperformed against"
            tc_color = "var(--green)" if tc_target_met >= 0 else "var(--red)"
            
            spot_data = cur_wk_data if mode == "MTD" else df_tc_filtered[df_tc_filtered["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
            
            st.markdown(f"""
            <div class="rca-card">
              <div class="rca-ttl">Network Capacity Diagnostic ({tc_display_date})</div>
              <div class="rca-body">
                The most recently filtered capacity cycle resolved with <strong>{kpi_active:,}</strong> Active TCs. 
                Net Acquisition operations yielded <strong style="color:var(--text)">{kpi_net_additions:,}</strong> Net New additions. 
                Based on target modeling, execution {tc_term} expected addition quotas by 
                <strong style="color:{tc_color}">{abs(tc_target_met):,}</strong> units.
              </div>
            </div>""", unsafe_allow_html=True)
            
            # Segment Aggregations for TC
            ch_agg = spot_data.groupby("Channel")["net_new_additions"].sum().sort_values(ascending=False) if not spot_data.empty else pd.Series()
            reg_agg = spot_data.groupby("region")["net_new_additions"].sum().sort_values(ascending=False) if not spot_data.empty else pd.Series()
            
            st.markdown('<div class="rca-card"><div class="rca-ttl">Acquisition Engine Performance</div>', unsafe_allow_html=True)
            if not ch_agg.empty:
                top_ch = ch_agg.index[0]
                top_ch_val = ch_agg.iloc[0]
                bot_ch = ch_agg.index[-1]
                bot_ch_val = ch_agg.iloc[-1]
                
                st.markdown(f"""<div class="rca-item positive"><div class="rca-dot dot-b"></div>
                    <div><strong>Leading Channel Engine:</strong> {top_ch} <br> Originated <span style="color:var(--green); font-weight:700;">{int(top_ch_val):,}</span> Net Additions in latest cycle.</div>
                </div>""", unsafe_allow_html=True)
                
                if top_ch != bot_ch and bot_ch_val <= 0:
                    st.markdown(f"""<div class="rca-item negative"><div class="rca-dot dot-r"></div>
                        <div><strong>Underperforming Channel:</strong> {bot_ch} <br> Churn outpaced acquisition resulting in <span style="color:var(--red); font-weight:700;">{int(bot_ch_val):,}</span> Net Additions.</div>
                    </div>""", unsafe_allow_html=True)
            else:
                 st.markdown('<div style="color:var(--muted); font-size:12px;">Insufficient active channel data for insight extraction.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="rca-card"><div class="rca-ttl">Regional Capacity Execution</div>', unsafe_allow_html=True)
            if not reg_agg.empty:
                top_reg = reg_agg.index[0]
                top_reg_val = reg_agg.iloc[0]
                bot_reg = reg_agg.index[-1]
                bot_reg_val = reg_agg.iloc[-1]
                
                st.markdown(f"""<div class="rca-item positive"><div class="rca-dot dot-b"></div>
                    <div><strong>Primary Expansion Zone:</strong> {top_reg} <br> Supplied <span style="color:var(--green); font-weight:700;">{int(top_reg_val):,}</span> Net Additions to network footprint.</div>
                </div>""", unsafe_allow_html=True)
                
                if top_reg != bot_reg and bot_reg_val <= 0:
                    st.markdown(f"""<div class="rca-item negative"><div class="rca-dot dot-r"></div>
                        <div><strong>Vulnerable Footprint:</strong> {bot_reg} <br> Recorded net contraction of <span style="color:var(--red); font-weight:700;">{int(bot_reg_val):,}</span> capacity elements.</div>
                    </div>""", unsafe_allow_html=True)
            else:
                 st.markdown('<div style="color:var(--muted); font-size:12px;">Insufficient regional data for insight extraction.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
             st.markdown('<div class="rca-card" style="color:var(--muted); font-size:13px;">No TC data available for AI insight generation based on current week filters.</div>', unsafe_allow_html=True)
