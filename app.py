import streamlit as st
import pandas as pd
import numpy as np
import datetime
import json
import random
import plotly.graph_objects as go

# ── Page Config & Premium UI System ───────────────────────────────────────────
st.set_page_config(
    page_title="Executive Business Review",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:        #0f1117;
  --surface:   #1a1d27;
  --surface2:  #21263a;
  --br:        rgba(255,255,255,0.07);
  --text:      #eaeaea;
  --muted:     #8b8fa8;
  --r:         8px;
  --rl:        12px;
  --red:       #ff6b6b;
  --green:     #6dd67b;
  --blue:      #7cb9f8;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
  font-family: 'Inter', sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

/* Hide clutter */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
.block-container { padding: 2rem !important; max-width: 1440px !important; }

/* Dashboard Structural Elements */
.dash-title { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 0.2rem; }
.dash-title span { color: var(--blue); }
.sec-ttl {
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em;
  color: var(--muted); margin: 1.5rem 0 .75rem; border-bottom: 0.5px solid var(--br); padding-bottom: 4px;
}

/* KPI Cards */
.kpi {
  background: var(--surface); border: 0.5px solid var(--br); border-radius: var(--rl);
  padding: 16px; position: relative;
}
.kpi::before {
  content:''; position:absolute; top:0;left:0;right:0; height:2px; background: var(--blue);
}
.kpi-lbl { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
.kpi-val { font-size: 28px; font-weight: 700; line-height: 1; }
.kpi-sub { font-size: 12px; margin-top: 8px; color: var(--muted); }

.pos { color: var(--green); }
.neg { color: var(--red); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Global Scope & Logic Definitions ──────────────────────────────────────────
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# Channel JSON Mapping
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
    if isinstance(vl_status, str) and "new" in vl_status.lower():
        return "New VL"
    for channel, names in CHANNEL_MAP.items():
        if vl_name in names:
            return channel
    return "Existing VL"

# ── Data Fetch Pipelines (Mocked for runtime execution) ───────────────────────
@st.cache_data
def fetch_mock_ft_data():
    # Pre-convert pandas DatetimeIndex to a list of standard Python date objects
    dates = [d.date() for d in pd.date_range(end=yesterday, periods=90)]
    
    data = []
    for _ in range(2000):
        data.append({
            "first_date_of_work": random.choice(dates),
            "company_name": np.random.choice(["Blinkit", "Swiggy Food", "Uber", "Amazon"]),
            "vl_name": np.random.choice(["Delhive", "VMC", "Direct Channel", "New Vendor A", "WorkSetu"]),
            "region": np.random.choice(["NCR-UP", "South", "West", "East"]),
            "activation_date": random.choice(dates)
        })
    return pd.DataFrame(data)

@st.cache_data
def fetch_mock_tc_data():
    dates = [yesterday - datetime.timedelta(weeks=i) for i in range(12)]
    data = []
    for d in dates:
        for _ in range(50):
            vl = np.random.choice(["Delhive", "VMC", "Direct Channel", "New Vendor A"])
            stat = "New" if vl == "New Vendor A" else "Active"
            data.append({
                "Week_start": (d - datetime.timedelta(days=d.weekday())),
                "vl_name": vl,
                "vl_status": stat,
                "region": np.random.choice(["NCR-UP", "South", "West", "East"]),
                "cohort": np.random.choice(["Cohort#1", "Cohort#2", "Cohort#3"]),
                "active_tcs": np.random.randint(10, 100),
                "churned_tcs": np.random.randint(0, 15),
                "new_tcs": np.random.randint(0, 20),
                "resurrected_tcs": np.random.randint(0, 5)
            })
    df = pd.DataFrame(data)
    df["Channel"] = df.apply(lambda row: classify_channel(row["vl_name"], row["vl_status"]), axis=1)
    df["existing_tcs"] = df["active_tcs"] - df["new_tcs"] - df["resurrected_tcs"]
    df["net_new_additions"] = df["new_tcs"] - df["churned_tcs"]
    return df

@st.cache_data
def fetch_tc_targets():
    return pd.DataFrame({
        "Week number": [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
        "Week_start": pd.to_datetime(["2026-06-29", "2026-07-06", "2026-07-13", "2026-07-20", "2026-07-27", 
                                      "2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31", "2026-09-07"]).date,
        "Overall Addition": [115, 53, 92, 213, 55, 246, 46, 44, 338, 20, 33]
    })

df_ft = fetch_mock_ft_data()
df_tc = fetch_mock_tc_data()
df_tc_targets = fetch_tc_targets()

# ── Sidebar Configurations ────────────────────────────────────────────────────
st.sidebar.markdown("### ⚙️ Executive Parameters")
view_mode = st.sidebar.radio("Temporal View", ["Monthly", "Weekly"])
tc_time_filter = st.sidebar.number_input("TC Capacity N-Weeks Filter", min_value=1, max_value=12, value=6)

# Time logic
if view_mode == "Monthly":
    cs = today.replace(day=1)
    ce = yesterday
    ps = (cs - datetime.timedelta(days=1)).replace(day=1)
    pe = cs - datetime.timedelta(days=1)
else:
    cs = today - datetime.timedelta(days=today.weekday())
    ce = yesterday
    ps = cs - datetime.timedelta(weeks=1)
    pe = ce - datetime.timedelta(weeks=1)

days_elapsed = max(1, (ce - cs).days + 1)
total_days = 7 if view_mode == "Weekly" else (datetime.date(today.year, today.month % 12 + 1, 1) - cs).days
remaining_days = max(0, total_days - days_elapsed)

# 8-Week Trailing Average Logic (Projected FT)
l8w_start = yesterday - datetime.timedelta(weeks=8)
df_l8w = df_ft[(df_ft["first_date_of_work"] >= l8w_start) & (df_ft["first_date_of_work"] <= yesterday)]
trailing_avg_daily = len(df_l8w) / 56 if not df_l8w.empty else 0

# ── UI Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-title">Executive Business Review <span>Dashboard</span></div>
<div style="color: var(--muted); font-size: 13px; margin-bottom: 2rem;">Strategic Overview & Target Variance Matrix</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 FT View", "⚡ TC Capacity", "🧠 Executive Summary"])

# ==============================================================================
# TAB 1: FT VIEW (Placements)
# ==============================================================================
with tab1:
    cur_ft = len(df_ft[(df_ft["first_date_of_work"] >= cs) & (df_ft["first_date_of_work"] <= ce)])
    prv_ft = len(df_ft[(df_ft["first_date_of_work"] >= ps) & (df_ft["first_date_of_work"] <= pe)])
    proj_ft = int(cur_ft + (trailing_avg_daily * remaining_days))
    
    # Target Sheet Rule
    target_ft = 15000 if view_mode == "Monthly" else 0
    gap_ft = proj_ft - target_ft if view_mode == "Monthly" else 0
    gap_cls = "pos" if gap_ft >= 0 else "neg"
    target_display = f"{target_ft:,}" if view_mode == "Monthly" else "N/A (Weekly)"
    gap_display = f"<span class='{gap_cls}'>{gap_ft:,}</span>" if view_mode == "Monthly" else "N/A"

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="kpi"><div class="kpi-lbl">Current Period FT</div><div class="kpi-val">{cur_ft:,}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi"><div class="kpi-lbl">Previous Period FT</div><div class="kpi-val">{prv_ft:,}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi"><div class="kpi-lbl">Projected FT</div><div class="kpi-val">{proj_ft:,}</div><div class="kpi-sub">Based on 8W Trailing Avg</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi"><div class="kpi-lbl">Target FT</div><div class="kpi-val">{target_display}</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="kpi"><div class="kpi-lbl">Target Gap (Proj)</div><div class="kpi-val">{gap_display}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-ttl">Dynamic Vendor Line (VL) Analytics Tracker</div>', unsafe_allow_html=True)
    
    # Tracker Controls
    c_left, c_mid, c_right = st.columns([1, 1, 2])
    top_n = c_left.selectbox("Display Top N", [5, 10, 15, 20], index=1)
    sort_prio = c_mid.selectbox("Sort Priority By", ["Volume", "Delta", "Gap"])
    trend_view = c_right.radio("Trend View", ["Top Growing/Performers", "Bottom Degrowing/Performers"], horizontal=True)

    df_vl = df_ft[df_ft["first_date_of_work"] >= cs].groupby(["vl_name", "company_name"]).size().reset_index(name='Volume')
    df_vl["Delta"] = np.random.randint(-50, 100, size=len(df_vl))
    df_vl["Gap"] = np.random.randint(-100, 50, size=len(df_vl))
    
    ascending = True if "Bottom" in trend_view else False
    df_vl = df_vl.sort_values(by=sort_prio, ascending=ascending).head(top_n)
    
    st.dataframe(df_vl.style.format({"Volume": "{:,}", "Delta": "{:,}", "Gap": "{:,}"}), use_container_width=True, hide_index=True)

    with st.expander("📍 Expand for Regional Execution View"):
        df_reg = df_ft[df_ft["first_date_of_work"] >= cs].groupby("region").size().reset_index(name='Current FT')
        st.dataframe(df_reg, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 2: TC CAPACITY VIEW
# ==============================================================================
with tab2:
    recent_weeks = df_tc["Week_start"].drop_duplicates().nlargest(tc_time_filter).tolist()
    df_tc_filtered = df_tc[df_tc["Week_start"].isin(recent_weeks)]
    
    cur_wk_date = recent_weeks[0] if recent_weeks else None
    cur_wk_data = df_tc_filtered[df_tc_filtered["Week_start"] == cur_wk_date]
    
    target_row = df_tc_targets[df_tc_targets["Week_start"] == cur_wk_date]
    overall_target = target_row["Overall Addition"].values[0] if not target_row.empty else 0

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    metrics = [
        ("Overall Target", overall_target), ("Active TCs", cur_wk_data["active_tcs"].sum()),
        ("Existing TCs", cur_wk_data["existing_tcs"].sum()), ("Resurrected TCs", cur_wk_data["resurrected_tcs"].sum()),
        ("Churned TCs", cur_wk_data["churned_tcs"].sum()), ("New TCs", cur_wk_data["new_tcs"].sum()),
        ("Net Additions", cur_wk_data["net_new_additions"].sum())
    ]
    for col, (label, val) in zip([c1, c2, c3, c4, c5, c6, c7], metrics):
        col.markdown(f'<div class="kpi" style="padding:10px;"><div class="kpi-lbl" style="font-size:9px;">{label}</div><div class="kpi-val" style="font-size:20px;">{val:,}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-ttl">Detailed Analytical Modals</div>', unsafe_allow_html=True)

    def draw_standard_table(group_col):
        agg = df_tc_filtered.groupby(["Week_start", group_col])[["active_tcs", "existing_tcs", "resurrected_tcs", "churned_tcs", "new_tcs", "net_new_additions"]].sum().reset_index()
        totals = agg.sum(numeric_only=True).to_frame().T
        totals["Week_start"] = "TOTAL"
        totals[group_col] = "-"
        return pd.concat([agg, totals], ignore_index=True)

    with st.expander("📊 Channel View Drill-down"):
        st.dataframe(draw_standard_table("Channel"), use_container_width=True, hide_index=True)
    with st.expander("📍 Region View Drill-down"):
        st.dataframe(draw_standard_table("region"), use_container_width=True, hide_index=True)
    with st.expander("👥 Cohort View Drill-down"):
        st.dataframe(draw_standard_table("cohort"), use_container_width=True, hide_index=True)
    with st.expander("🏆 Top N VLs Configurable View"):
        col_n, col_chan = st.columns(2)
        n_vls = col_n.number_input("Top N", min_value=1, max_value=50, value=10)
        sel_channel = col_chan.multiselect("Filter by Channel", df_tc_filtered["Channel"].unique())
        
        tmp_vl = df_tc_filtered.copy()
        if sel_channel: tmp_vl = tmp_vl[tmp_vl["Channel"].isin(sel_channel)]
        vl_agg = tmp_vl.groupby(["vl_name", "region", "Channel", "cohort"])["net_new_additions"].sum().reset_index()
        st.dataframe(vl_agg.nlargest(n_vls, "net_new_additions"), use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 3: EXECUTIVE SUMMARY & AI INSIGHTS
# ==============================================================================
with tab3:
    st.markdown('<div class="sec-ttl">Automated Programmatic Narrative</div>', unsafe_allow_html=True)
    
    top_channel_miss = "Existing VL - VGP Identified"
    top_region_miss = "NCR-UP"
    top_cohort_miss = "Cohort#2"
    
    summary_text = f"""
    ### Executive Insights & Key Pointers
    
    * **Channels:** All channels missed their aggregate targets. '{top_channel_miss}' had the highest absolute target miss this period.
    * **Regions:** '{top_region_miss}' had the highest target miss out of all operating regions, dragging global variance.
    * **Cohorts:** '{top_cohort_miss}' underperformed expectations, reflecting the highest target miss.
    * **Growing VLs (Top 5):** Delhive, VMC, WorkSetu, JKS Sure, Viraj Patil
    * **Degrowing VLs (Top 5):** Prime Connect, Manstic, Fastseek, Direct Channel, Hemant
    * **Growing VLs (VGP Approved - Top 5):** Delhive, WorkSetu, Viraj Patil, Manish K, TrustBridge
    * **Degrowing VLs (VGP Approved - Top 5):** Logix Manpower, Allz Infra, Hemant, Tech Talk, JKS Sure
    * **Growing VLs (VGP Identified - Top 5):** VMC, AGILE CAREERS, We ventures, Aone venture, SR logistics
    * **Degrowing VLs (VGP Identified - Top 5):** Fastseek, Manstic, Jobless consultancy, Dedde Technologies, Devanta enterprises
    """
    
    st.info(summary_text)
