import streamlit as st
import pandas as pd
import numpy as np
import datetime
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
    dates = [d.date() for d in pd.date_range(end=yesterday, periods=90)]
    data = []
    for _ in range(2000):
        data.append({
            "first_date_of_work": random.choice(dates),
            "company_name": random.choice(["Blinkit", "Swiggy Food", "Uber", "Amazon"]),
            "vl_name": random.choice(["Delhive", "VMC", "Direct Channel", "New Vendor A", "WorkSetu"]),
            "region": random.choice(["NCR-UP", "South", "West", "East"]),
            "activation_date": random.choice(dates)
        })
    return pd.DataFrame(data)

@st.cache_data
def fetch_mock_tc_data():
    dates = [yesterday - datetime.timedelta(weeks=i) for i in range(12)]
    data = []
    for d in dates:
        week_start = d - datetime.timedelta(days=d.weekday())
        for _ in range(50):
            vl = random.choice(["Delhive", "VMC", "Direct Channel", "New Vendor A"])
            stat = "New" if vl == "New Vendor A" else "Active"
            data.append({
                "Week_start": week_start,
                "vl_name": vl,
                "vl_status": stat,
                "region": random.choice(["NCR-UP", "South", "West", "East"]),
                "cohort": random.choice(["Cohort#1", "Cohort#2", "Cohort#3"]),
                "active_tcs": random.randint(10, 100),
                "churned_tcs": random.randint(0, 15),
                "new_tcs": random.randint(0, 20),
                "resurrected_tcs": random.randint(0, 5)
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

# ── Sidebar Configurations & Segment Filters ──────────────────────────────────
st.sidebar.markdown("### ⚙️ Executive Parameters")
view_mode = st.sidebar.radio("FT Temporal View", ["Monthly", "Weekly"])
tc_time_filter = st.sidebar.number_input("TC Capacity N-Weeks Default", min_value=1, max_value=12, value=6)
exclude_current = st.sidebar.checkbox("Exclude Current Incomplete Week", value=False)

st.sidebar.markdown("### 🔍 Global Segment Filters")

# FT Specific Filter
sel_clients = st.sidebar.multiselect("Client Scope (FT Only)", sorted(df_ft["company_name"].unique()))

# TC Specific Filter setup
all_weeks = sorted(df_tc["Week_start"].dropna().unique(), reverse=True)
if exclude_current and len(all_weeks) > 0:
    all_weeks = all_weeks[1:] # Prune the active incomplete week
sel_weeks = st.sidebar.multiselect("Week Scope (TC Only)", all_weeks, default=all_weeks[:tc_time_filter])
sel_cohorts = st.sidebar.multiselect("Cohort Scope (TC Only)", sorted(df_tc["cohort"].unique()))
sel_channels = st.sidebar.multiselect("Channel Scope (TC Only)", sorted(df_tc["Channel"].unique()))

# Shared Filters across both views
shared_regions = sorted(set(df_ft["region"]).union(df_tc["region"]))
shared_vls = sorted(set(df_ft["vl_name"]).union(df_tc["vl_name"]))
sel_regions = st.sidebar.multiselect("Region Scope (Shared)", shared_regions)
sel_vls = st.sidebar.multiselect("Vendor Line Scope (Shared)", shared_vls)

# Apply Filters to FT Data
df_ft_filtered = df_ft.copy()
if sel_clients: df_ft_filtered = df_ft_filtered[df_ft_filtered["company_name"].isin(sel_clients)]
if sel_regions: df_ft_filtered = df_ft_filtered[df_ft_filtered["region"].isin(sel_regions)]
if sel_vls: df_ft_filtered = df_ft_filtered[df_ft_filtered["vl_name"].isin(sel_vls)]

# Apply Filters to TC Data
df_tc_filtered = df_tc.copy()
if sel_weeks: df_tc_filtered = df_tc_filtered[df_tc_filtered["Week_start"].isin(sel_weeks)]
if sel_regions: df_tc_filtered = df_tc_filtered[df_tc_filtered["region"].isin(sel_regions)]
if sel_vls: df_tc_filtered = df_tc_filtered[df_tc_filtered["vl_name"].isin(sel_vls)]
if sel_cohorts: df_tc_filtered = df_tc_filtered[df_tc_filtered["cohort"].isin(sel_cohorts)]
if sel_channels: df_tc_filtered = df_tc_filtered[df_tc_filtered["Channel"].isin(sel_channels)]

# Temporal Anchoring for FT
if view_mode == "Monthly":
    cs = today.replace(day=1)
    ce = yesterday
    ps = (cs - datetime.timedelta(days=1)).replace(day=1)
    pe = cs - datetime.timedelta(days=1)
else:
    cs = today - datetime.timedelta(days=today.weekday())
    if exclude_current:
        cs = cs - datetime.timedelta(weeks=1)
    ce = cs + datetime.timedelta(days=6) if exclude_current else yesterday
    ps = cs - datetime.timedelta(weeks=1)
    pe = ce - datetime.timedelta(weeks=1)

days_elapsed = max(1, (ce - cs).days + 1)
total_days = 7 if view_mode == "Weekly" else (datetime.date(today.year, today.month % 12 + 1, 1) - cs).days
remaining_days = max(0, total_days - days_elapsed)

# 8-Week Trailing Average Logic (Projected FT) on filtered data
l8w_start = yesterday - datetime.timedelta(weeks=8)
df_l8w = df_ft_filtered[(df_ft_filtered["first_date_of_work"] >= l8w_start) & (df_ft_filtered["first_date_of_work"] <= yesterday)]
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
    cur_ft = len(df_ft_filtered[(df_ft_filtered["first_date_of_work"] >= cs) & (df_ft_filtered["first_date_of_work"] <= ce)])
    prv_ft = len(df_ft_filtered[(df_ft_filtered["first_date_of_work"] >= ps) & (df_ft_filtered["first_date_of_work"] <= pe)])
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
    
    c_left, c_mid, c_right = st.columns([1, 1, 2])
    top_n = c_left.selectbox("Display Top N", [5, 10, 15, 20], index=1)
    sort_prio = c_mid.selectbox("Sort Priority By", ["Volume", "Delta", "Gap"])
    trend_view = c_right.radio("Trend View", ["Top Growing/Performers", "Bottom Degrowing/Performers"], horizontal=True)

    df_vl = df_ft_filtered[df_ft_filtered["first_date_of_work"] >= cs].groupby(["vl_name", "company_name"]).size().reset_index(name='Volume')
    df_vl["Delta"] = np.random.randint(-50, 100, size=len(df_vl))
    df_vl["Gap"] = np.random.randint(-100, 50, size=len(df_vl))
    
    ascending = True if "Bottom" in trend_view else False
    df_vl = df_vl.sort_values(by=sort_prio, ascending=ascending).head(top_n)
    st.dataframe(df_vl.style.format({"Volume": "{:,}", "Delta": "{:,}", "Gap": "{:,}"}), use_container_width=True, hide_index=True)

    with st.expander("📍 Expand for Regional Execution View"):
        df_reg = df_ft_filtered[df_ft_filtered["first_date_of_work"] >= cs].groupby("region").size().reset_index(name='Current FT')
        st.dataframe(df_reg, use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 2: TC CAPACITY VIEW
# ==============================================================================
with tab2:
    cur_wk_date = all_weeks[0] if all_weeks else None
    cur_wk_data = df_tc_filtered[df_tc_filtered["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
    
    target_row = df_tc_targets[df_tc_targets["Week_start"] == cur_wk_date] if cur_wk_date else pd.DataFrame()
    overall_target = target_row["Overall Addition"].values[0] if not target_row.empty else 0

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    metrics = [
        ("Overall Target", overall_target), 
        ("Active TCs", cur_wk_data["active_tcs"].sum() if not cur_wk_data.empty else 0),
        ("Existing TCs", cur_wk_data["existing_tcs"].sum() if not cur_wk_data.empty else 0), 
        ("Resurrected TCs", cur_wk_data["resurrected_tcs"].sum() if not cur_wk_data.empty else 0),
        ("Churned TCs", cur_wk_data["churned_tcs"].sum() if not cur_wk_data.empty else 0), 
        ("New TCs", cur_wk_data["new_tcs"].sum() if not cur_wk_data.empty else 0),
        ("Net Additions", cur_wk_data["net_new_additions"].sum() if not cur_wk_data.empty else 0)
    ]
    for col, (label, val) in zip([c1, c2, c3, c4, c5, c6, c7], metrics):
        col.markdown(f'<div class="kpi" style="padding:10px;"><div class="kpi-lbl" style="font-size:9px;">{label}</div><div class="kpi-val" style="font-size:20px;">{val:,}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-ttl">Detailed Analytical Modals</div>', unsafe_allow_html=True)

    def draw_standard_table(group_col):
        # Group by the primary dimension first, then by week
        agg = df_tc_filtered.groupby([group_col, "Week_start"])[["active_tcs", "existing_tcs", "resurrected_tcs", "churned_tcs", "new_tcs", "net_new_additions"]].sum().reset_index()
        # Sort to visually cluster all weeks under their respective parent group
        agg = agg.sort_values(by=[group_col, "Week_start"], ascending=[True, False])
        
        # Append Grand Totals
        totals = agg.sum(numeric_only=True).to_frame().T
        totals[group_col] = "TOTAL"
        totals["Week_start"] = "-"
        return pd.concat([agg, totals], ignore_index=True)

    with st.expander("📊 Channel View Drill-down"):
        st.dataframe(draw_standard_table("Channel"), use_container_width=True, hide_index=True)
    with st.expander("📍 Region View Drill-down"):
        st.dataframe(draw_standard_table("region"), use_container_width=True, hide_index=True)
    with st.expander("👥 Cohort View Drill-down"):
        st.dataframe(draw_standard_table("cohort"), use_container_width=True, hide_index=True)
    with st.expander("🏆 Top N VLs Configurable View"):
        n_vls = st.number_input("Display Top N Vendor Lines", min_value=1, max_value=50, value=10)
        
        # Group VLs maintaining the clustered weekly history
        vl_agg = df_tc_filtered.groupby(["vl_name", "region", "Channel", "cohort", "Week_start"])[["active_tcs", "existing_tcs", "resurrected_tcs", "churned_tcs", "new_tcs", "net_new_additions"]].sum().reset_index()
        
        # Identify the Top N VLs by overall Net Additions to filter the matrix
        top_vl_names = df_tc_filtered.groupby("vl_name")["net_new_additions"].sum().nlargest(n_vls).index
        vl_agg_filtered = vl_agg[vl_agg["vl_name"].isin(top_vl_names)]
        
        # Sort to cluster weeks under each VL cleanly
        vl_agg_filtered = vl_agg_filtered.sort_values(by=["vl_name", "Week_start"], ascending=[True, False])
        st.dataframe(vl_agg_filtered, use_container_width=True, hide_index=True)

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
