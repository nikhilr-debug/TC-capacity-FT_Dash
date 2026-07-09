import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="Operations Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN TOKENS & PREMIUM THEME SYSTEM ---
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
  --green:     #00ea7b;
  --blue:      #7cb9f8;
}

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

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

/* Custom RCA (Spotlight) Card Layout Styling */
.rca-card {
  background: var(--surface);
  border: 1px solid var(--br2);
  border-radius: var(--rl);
  padding: 24px;
  margin-top: 12px;
  margin-bottom: 24px;
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
.section-divider {
  border-top: 1px dashed var(--br2);
  margin: 16px 0;
}

/* Custom Expand/Collapse Component Layout Rules */
details.section-expander summary::-webkit-details-marker { display: none !important; }
details.section-expander summary { list-style: none !important; cursor: pointer; outline: none; }
details.section-expander:not([open]) summary .sec-icon::before { content: '▶  '; font-size: 11px; color: var(--blue); }
details.section-expander[open] summary .sec-icon::before { content: '▼  '; font-size: 11px; color: var(--blue); }

details.vl-expander summary::-webkit-details-marker { display: none !important; }
details.vl-expander summary { list-style: none !important; display: flex !important; justify-content: space-between; align-items: center; width: 100%; }
.exp-icon { display: inline-block; width: 14px; font-weight: 800; color: var(--muted); text-align: center; margin-right: 6px; font-size: 11px; }
details.vl-expander:not([open]) summary .exp-icon::before { content: '➕'; font-size: 9px; }
details.vl-expander[open] summary .exp-icon::before { content: '➖'; font-size: 9px; }
details.vl-expander[open] summary span { color: var(--blue) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

API_KEY = "4aFm2iOoyx8I91svQccdeZr0jmaiUsMFSRinZcmu"
PLACEMENTS_URL = f"https://redash.vahan.link/api/queries/17613/results.json?api_key={API_KEY}"
CAPACITY_URL = f"https://redash.vahan.link/api/queries/17597/results.json?api_key={API_KEY}"

# Google Sheets Mappings URL (Export format for pandas)
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1KotqUM8d_BtKZHLjk5MhADLFgjl5tie_E3_u4yblPOQ/export?format=csv"

# --- TARGET MAPS & TEMPORAL MAPS ---
PLACEMENT_WEEK_KEYS = [25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
TARGETS_VL = [0, 5628, 6167, 6580, 7172, 7887, 8592, 9210, 10065, 11016, 11719, 12694, 13126, 13774, 13829]
TARGETS_DC_BPO = [0, 408, 434, 602, 958, 1302, 1893, 2268, 2934, 3637, 4440, 5022, 5735, 6588, 7002]

CAPACITY_WEEK_KEYS = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
CAP_EXISTING_VL = [35, 38, 52, 40, 30, 21, 26, 24, 18, 10, 0, 0, 0, 0]
CAP_BPO = [80, 0, 0, 150, 0, 200, 0, 0, 300, 0, 0, 0, 0, 0]
CAP_DC = [0, 15, 40, 23, 25, 25, 20, 20, 20, 10, 0, 0, 0, 0]

PLACEMENT_TARGETS_MAP = {
    "VGP": {27: 932, 28: 1395, 29: 1424, 30: 1424, 31: 1597, 32: 2022, 33: 1765, 34: 2201, 35: 2012, 36: 2488, 37: 2470, 38: 2796, 39: 2796, 40: 1100},
    "Custom Deal": {27: 1518, 28: 2274, 29: 2325, 30: 2325, 31: 2498, 32: 2934, 33: 2550, 34: 3189, 35: 2870, 36: 3479, 37: 3583, 38: 3992, 39: 3992, 40: 1629},
    "Custom Tier": {27: 993, 28: 1488, 29: 1522, 30: 1522, 31: 1623, 32: 1866, 33: 1640, 34: 2030, 35: 1913, 36: 2195, 37: 2102, 38: 2412, 39: 2412, 40: 999},
    "Normal Tier": {27: 946, 28: 1427, 29: 1456, 30: 1456, 31: 1584, 32: 1907, 33: 1679, 34: 2081, 35: 1966, 36: 2321, 37: 2291, 38: 2602, 39: 2602, 40: 1033},
    "Remote": {27: 55, 28: 91, 29: 92, 30: 92, 31: 96, 32: 116, 33: 102, 34: 126, 35: 124, 36: 143, 37: 151, 38: 166, 39: 166, 40: 0}
}
CLIENT_TARGETS_MAP = {
    'Blinkit': {27: 3537, 28: 3760, 29: 3760, 30: 3760, 31: 3960, 32: 4177, 33: 4277, 34: 4427, 35: 4577, 36: 4829, 37: 4929, 38: 4979, 39: 4979, 40: 4979},
    'Swiggy Food': {27: 1243, 28: 1314, 29: 1428, 30: 1685, 31: 1929, 32: 2171, 33: 2418, 34: 2763, 35: 3019, 36: 3269, 37: 3574, 38: 3876, 39: 4223, 40: 4488},
    'Swiggy Instamart': {27: 718, 28: 757, 29: 849, 30: 992, 31: 1124, 32: 1264, 33: 1398, 34: 1590, 35: 1738, 36: 1882, 37: 2052, 38: 2221, 39: 2419, 40: 2566},
    'SOC': {27: 37, 28: 77, 29: 112, 30: 187, 31: 262, 32: 312, 33: 387, 34: 487, 35: 587, 36: 587, 37: 637, 38: 637, 39: 687, 40: 687},
    'FKM': {27: 0, 28: 40, 29: 110, 30: 170, 31: 200, 32: 250, 33: 300, 34: 350, 35: 400, 36: 500, 37: 550, 38: 550, 39: 600, 40: 600},
    'Uber': {27: 45, 28: 127, 29: 187, 30: 299, 31: 383, 32: 519, 33: 592, 34: 738, 35: 907, 36: 1115, 37: 1298, 38: 1450, 39: 1603, 40: 1631},
    'Rapido': {27: 0, 28: 75, 29: 200, 30: 300, 31: 380, 32: 500, 33: 600, 34: 700, 35: 800, 36: 900, 37: 1000, 38: 1000, 39: 1000, 40: 0},
    '4W': {27: 67, 28: 97, 29: 115, 30: 167, 31: 194, 32: 261, 33: 298, 34: 381, 35: 456, 36: 570, 37: 640, 38: 740, 39: 800, 40: 828},
    'Picker Packer': {27: 263, 28: 283, 29: 303, 30: 323, 31: 333, 32: 363, 33: 363, 34: 388, 35: 598, 36: 465, 37: 758, 38: 645, 39: 938, 40: 825},
    'Bigbasket': {27: 43, 28: 43, 29: 64, 30: 144, 31: 186, 32: 333, 33: 375, 34: 508, 35: 700, 36: 918, 37: 1000, 38: 1200, 39: 1383, 40: 1463},
    'Amazon': {27: 9, 28: 9, 29: 13, 30: 40, 31: 54, 32: 90, 33: 104, 34: 142, 35: 197, 36: 273, 37: 320, 38: 370, 39: 441, 40: 458},
    'Xpress Bees': {27: 37, 28: 37, 29: 50, 30: 67, 31: 80, 32: 128, 33: 146, 34: 205, 35: 254, 36: 331, 37: 388, 38: 473, 39: 539, 40: 586},
    'Maid': {27: 80, 28: 100, 29: 120, 30: 120, 31: 120, 32: 120, 33: 120, 34: 120, 35: 120, 36: 120, 37: 120, 38: 150, 39: 120, 40: 0},
    'Small Clients': {27: 0, 28: 0, 29: 20, 30: 50, 31: 100, 32: 150, 33: 200, 34: 300, 35: 400, 36: 500, 37: 550, 38: 600, 39: 600, 40: 600}
}
REGION_TARGETS_MAP = {
    'East': {27: 177, 28: 266, 29: 270, 30: 270, 31: 343, 32: 505, 33: 450, 34: 550, 35: 539, 36: 675, 37: 721, 38: 799, 39: 799, 40: 327}, 
    'MPCG': {27: 1902, 28: 2848, 29: 2912, 30: 2912, 31: 3127, 32: 3681, 33: 3199, 34: 4003, 35: 3599, 36: 4326, 37: 4448, 38: 4956, 39: 4956, 40: 2022}, 
    'NCR-UP': {27: 1169, 28: 1751, 29: 1787, 30: 1787, 31: 1915, 32: 2245, 33: 1954, 34: 2448, 35: 2196, 36: 2550, 37: 2616, 38: 2912, 39: 2912, 40: 1188}, 
    'Remote': {27: 107, 28: 164, 29: 167, 30: 167, 31: 181, 32: 221, 33: 196, 34: 240, 35: 235, 36: 273, 37: 287, 38: 319, 39: 319, 40: 20}, 
    'South - 2': {27: 73, 28: 111, 29: 112, 30: 112, 31: 170, 32: 317, 33: 275, 34: 345, 35: 309, 36: 523, 37: 455, 38: 546, 39: 546, 40: 251}, 
    'South-1': {27: 608, 28: 906, 29: 930, 30: 930, 31: 994, 32: 1129, 33: 1001, 34: 1228, 35: 1203, 36: 1402, 37: 1215, 38: 1459, 39: 1459, 40: 669}, 
    'West': {27: 148, 28: 222, 29: 227, 30: 227, 31: 246, 32: 290, 33: 257, 34: 316, 35: 316, 36: 376, 37: 333, 38: 400, 39: 400, 40: 184}
}
COHORT_TARGETS_MAP = {
    'Bronze': {27: 289, 28: 436, 29: 444, 30: 444, 31: 497, 32: 629, 33: 554, 34: 688, 35: 637, 36: 805, 37: 809, 38: 913, 39: 913, 40: 382}, 
    'Cohort 1': {27: 1240, 28: 1856, 29: 1900, 30: 1900, 31: 2025, 32: 2339, 33: 2040, 34: 2543, 35: 2318, 36: 2650, 37: 2646, 38: 2977, 39: 2977, 40: 1237}, 
    'Cohort 2': {27: 1101, 28: 1649, 29: 1687, 30: 1687, 31: 1809, 32: 2108, 33: 1840, 34: 2292, 35: 2100, 36: 2561, 37: 2502, 38: 2848, 39: 2848, 40: 1205}, 
    'Cohort 3': {27: 930, 28: 1392, 29: 1422, 30: 1422, 31: 1552, 32: 1874, 33: 1638, 34: 2040, 35: 1882, 36: 2254, 37: 2256, 38: 2546, 39: 2546, 40: 1063}, 
    'Cohort 4': {27: 609, 28: 911, 29: 928, 30: 928, 31: 1068, 32: 1407, 33: 1233, 34: 1533, 35: 1430, 36: 1816, 37: 1829, 38: 2068, 39: 2068, 40: 756}, 
    'Remote': {27: 0, 28: 1, 29: 1, 30: 1, 31: 0, 32: 1, 33: 1, 34: 1, 35: 1, 36: 1, 37: 1, 38: 1, 39: 1, 40: 0}
}
MONTH_MAP = {
    "All": "All", "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, 
    "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

# --- FIELD / SA EXPLICIT REGIONS ---
FIELD_SA_REGIONS = ['MPCG', 'South-1', 'NCR-UP', 'West', 'East', 'South - 2']

# --- TIMELINE CALCULATIONS ---
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Operations <span>Performance Analytics</span> Dashboard</div>
    <div class="dash-meta">Tracking Executive Placements & Supply Network Footprints</div>
    <div style='color:var(--muted); font-size:11px; margin-top:8px;'>*Current week projected based on % achieved by this day last week unless disabled.</div>
  </div>
</div>""", unsafe_allow_html=True)

st.sidebar.header("Global Filters")
MONTH_SELECT = st.sidebar.selectbox("Select Month Filter (Optional)", options=list(MONTH_MAP.keys()))
selected_month_num = MONTH_MAP[MONTH_SELECT]
exclude_current_week = st.sidebar.checkbox("Exclude Current Incomplete Week", value=False)
DISABLE_PROJECTION = st.sidebar.checkbox("View Actuals (Disable Projections)", value=False)

CURRENT_WEEK = datetime.date.today().isocalendar().week
MAX_WEEK = CURRENT_WEEK - 1 if exclude_current_week else CURRENT_WEEK

def get_short_number_input(label, key):
    col1, _ = st.columns([1, 4])
    with col1: return st.number_input(label, min_value=1, max_value=52, value=10, key=key)

# --- PACING ENGINE ---
def calculate_pacing_multiplier(df, date_col_name):
    today = datetime.date.today()
    current_weekday = today.weekday() 
    
    if current_weekday == 6: return 1.0
        
    last_week = MAX_WEEK - 1
    df_last_week = df[df['Week'] == last_week].copy()
    
    if df_last_week.empty: return 7.0 / max(1, current_weekday + 1)
        
    total_last_week = len(df_last_week)
    df_last_week['weekday'] = df_last_week[date_col_name].dt.weekday
    partial_last_week = len(df_last_week[df_last_week['weekday'] <= current_weekday])
    
    if partial_last_week == 0: return 7.0 / max(1, current_weekday + 1)
    return total_last_week / partial_last_week


# --- DATA ACQUISITION & GOOGLE SHEETS MAPPING ---
@st.cache_data(ttl=3600)
def fetch_redash_data(url):
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
        if 'query_result' in data and 'data' in data['query_result']:
            return pd.DataFrame(data['query_result']['data']['rows'])
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching Redash data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_gsheet_mappings():
    try:
        df = pd.read_csv(GSHEET_URL)
        l_map, r_map, c_map = {}, {}, {}
        for _, row in df.iterrows():
            vl = str(row.get('VL Name', '')).strip().lower()
            if vl and vl != 'nan':
                l_map[vl] = str(row.get('Lever', 'Remote')).strip() if pd.notna(row.get('Lever')) else 'Remote'
                r_map[vl] = str(row.get('Region', 'Remote')).strip() if pd.notna(row.get('Region')) else 'Remote'
                c_map[vl] = str(row.get('Cohort', 'Remote')).strip() if pd.notna(row.get('Cohort')) else 'Remote'
        return l_map, r_map, c_map
    except Exception as e:
        st.error(f"Error fetching Google Sheet mapping: {e}")
        return {}, {}, {}

def apply_tags(df, lever_map, region_map, cohort_map):
    if df.empty: return df
    
    df['Tag'] = "Remote"
    df['Mapped_Region'] = "Remote"
    df['Mapped_Cohort'] = "Remote"
    
    vl_col = next((col for col in df.columns if str(col).strip().lower() in ["vl_name", "vl name", "vl"]), None)
    channel_col = next((col for col in df.columns if str(col).strip().lower() == "channel"), None)
    lever_col = next((col for col in df.columns if str(col).strip().lower() == "lever"), None)
            
    def categorize(row):
        vl = row[vl_col] if vl_col and pd.notna(row[vl_col]) else ""
        vl_clean = str(vl).strip().lower()
        
        channel = str(row[channel_col]).strip().lower() if channel_col and pd.notna(row[channel_col]) else ""
        row_lever = str(row[lever_col]).strip().lower() if lever_col and pd.notna(row[lever_col]) else ""
        
        tag = lever_map.get(vl_clean, "Remote")
        region = region_map.get(vl_clean, "Remote")
        cohort = cohort_map.get(vl_clean, "Remote")
        
        if vl_clean in ["direct channel", "dc"] or channel in ["direct channel", "dc"] or row_lever in ["dc", "direct channel"]:
            tag = "DC"
        elif any(bpo in vl_clean for bpo in ["basu business", "rural shores"]) or channel == "bpo" or row_lever == "bpo":
            tag = "BPO"
                
        return pd.Series([tag, region, cohort])
    
    df[['Tag', 'Mapped_Region', 'Mapped_Cohort']] = df.apply(categorize, axis=1)
    return df

df_placements = fetch_redash_data(PLACEMENTS_URL)
df_capacity = fetch_redash_data(CAPACITY_URL)
lever_map, region_map, cohort_map = fetch_gsheet_mappings()

if not df_placements.empty:
    df_placements = apply_tags(df_placements, lever_map, region_map, cohort_map)
    if 'first_date_of_work' in df_placements.columns:
        df_placements['first_date_of_work'] = pd.to_datetime(df_placements['first_date_of_work'], errors='coerce', utc=True).dt.tz_convert('Asia/Kolkata')
        df_placements = df_placements.dropna(subset=['first_date_of_work'])
        current_year = datetime.date.today().year
        df_placements = df_placements[df_placements['first_date_of_work'].dt.year == current_year]
        df_placements['Week'] = df_placements['first_date_of_work'].dt.isocalendar().week
        
        if MONTH_SELECT != "All":
            df_placements = df_placements[df_placements['first_date_of_work'].dt.month == selected_month_num]
    else: 
        df_placements['Week'] = 0

if not df_capacity.empty:
    df_capacity = apply_tags(df_capacity, lever_map, region_map, cohort_map)
    date_col = next((col for col in ['Week Start', 'Week_Start', 'wk_monday'] if col in df_capacity.columns), None)
    if date_col:
        df_capacity['Week_Start_Parsed'] = pd.to_datetime(df_capacity[date_col], errors='coerce', utc=True).dt.tz_convert('Asia/Kolkata')
        df_capacity = df_capacity.dropna(subset=['Week_Start_Parsed'])
        current_year = datetime.date.today().year
        df_capacity = df_capacity[df_capacity['Week_Start_Parsed'].dt.year == current_year]
        df_capacity['Week'] = df_capacity['Week_Start_Parsed'].dt.isocalendar().week
        
        if MONTH_SELECT != "All":
            df_capacity = df_capacity[df_capacity['Week_Start_Parsed'].dt.month == selected_month_num]
    else: df_capacity['Week'] = 0
            
# --- AGGREGATION & COUNTING HANDLERS ---
def count_unique_phones(df_sub):
    if df_sub.empty: return 0
    phone_col = next((col for col in df_sub.columns if 'phone' in str(col).lower()), None)
    if phone_col: return df_sub[phone_col].count()
    return len(df_sub)

def add_subtotal(df):
    if df.empty: return df
    total_row = df.sum(numeric_only=True)
    df_out = df.copy()
    
    subtotal_df = pd.DataFrame([total_row])
    df_out = pd.concat([df_out, subtotal_df], ignore_index=True)
    df_out['Week'] = df_out['Week'].astype(str)
    df_out.at[df_out.index[-1], 'Week'] = 'Cumulative'
    return df_out.fillna('')

def format_numbers(val):
    if isinstance(val, (int, float)):
        if pd.isna(val): return ""
        if val == int(val): return f"{int(val)}"
        return f"{round(val, 2)}"
    return val

def style_placements_row(row):
    try:
        t = pd.to_numeric(row['Target'], errors='coerce')
        a = pd.to_numeric(row['Actuals'], errors='coerce')
        if pd.isna(t) or t == 0: return [''] * len(row)
        if a >= t: return ['background-color: #0e2a15; color: #00ea7b; font-weight: bold;'] * len(row)
        else: return ['background-color: #381313; color: #ff6b6b; font-weight: bold;'] * len(row)
    except: return [''] * len(row)

def style_capacity_row(row):
    try:
        t = pd.to_numeric(row['Target'], errors='coerce')
        a = pd.to_numeric(row['Net New Additions'], errors='coerce')
        if pd.isna(t) or t == 0: return [''] * len(row) 
        if a >= t: return ['background-color: #0e2a15; color: #00ea7b; font-weight: bold;'] * len(row)
        else: return ['background-color: #381313; color: #ff6b6b; font-weight: bold;'] * len(row)
    except: return [''] * len(row)

# --- ADVANCED PROJECTED DRILLDOWN ENGINE ---
def generate_dual_spotlight_card(df, metric_func, dim_col, title, local_n_weeks, breakdown_col=None, pacing_multiplier=1.0):
    all_target_weeks = list(range(26, MAX_WEEK + 1))
    available_weeks = all_target_weeks[-local_n_weeks:]
    if not available_weeks: return ""
    
    if df.empty or dim_col not in df.columns: return ""
    df_window = df[df['Week'].isin(available_weeks)]
    
    apply_proj = not DISABLE_PROJECTION and MAX_WEEK == CURRENT_WEEK

    df_c = df_window[df_window['Week'] == MAX_WEEK]
    df_p = df_window[df_window['Week'] == MAX_WEEK - 1]
    
    dims = df_window[dim_col].dropna().unique()
    wow_diffs = {}
    for d in dims:
        val_c = metric_func(df_c[df_c[dim_col] == d])
        val_p = metric_func(df_p[df_p[dim_col] == d])
        
        if apply_proj: val_c = val_c * pacing_multiplier

        diff = val_c - val_p
        if diff != 0: wow_diffs[d] = diff
            
    wow_series = pd.Series(wow_diffs, dtype=float)
    wow_growers = wow_series[wow_series > 0].sort_values(ascending=False).head(5)
    wow_decliners = wow_series[wow_series < 0].sort_values(ascending=True).head(5)
    total_wow_growth = wow_growers.sum() if not wow_growers.empty else 1
    total_wow_drop = wow_decliners.sum() if not wow_decliners.empty else 1

    df_earliest = df_window[df_window['Week'] == available_weeks[0]]
    df_latest = df_window[df_window['Week'] == available_weeks[-1]]
    
    cum_diffs = {}
    for d in dims:
        val_latest = metric_func(df_latest[df_latest[dim_col] == d])
        val_earliest = metric_func(df_earliest[df_earliest[dim_col] == d])
        
        if apply_proj and not df_latest.empty and df_latest['Week'].iloc[0] == CURRENT_WEEK:
            val_latest = val_latest * pacing_multiplier

        diff = val_latest - val_earliest
        if diff != 0: cum_diffs[d] = diff
            
    cum_series = pd.Series(cum_diffs, dtype=float)
    cum_performers = cum_series[cum_series > 0].sort_values(ascending=False).head(5)
    cum_defaulters = cum_series[cum_series < 0].sort_values(ascending=True).head(5)
    total_cum_growth = cum_performers.sum() if not cum_performers.empty else 1
    total_cum_drop = cum_defaulters.sum() if not cum_defaulters.empty else 1

    def get_breakdown_html(parent_name, is_wow=True):
        if not breakdown_col or breakdown_col not in df_window.columns: return ""
        target_c = df_c if is_wow else df_latest
        target_p = df_p if is_wow else df_earliest
        
        sub_c = target_c[target_c[dim_col] == parent_name]
        sub_p = target_p[target_p[dim_col] == parent_name]
        
        b_dims = pd.concat([sub_c, sub_p])[breakdown_col].dropna().unique()
        b_diffs = {}
        for bd in b_dims:
            v_c = metric_func(sub_c[sub_c[breakdown_col] == bd])
            v_p = metric_func(sub_p[sub_p[breakdown_col] == bd])
            
            if apply_proj and (is_wow or (not is_wow and not df_latest.empty and df_latest['Week'].iloc[0] == CURRENT_WEEK)):
                v_c = v_c * pacing_multiplier
            
            diff = v_c - v_p
            if diff != 0: b_diffs[bd] = diff
                
        if not b_diffs: return '<div style="padding: 4px 20px; color: var(--muted); font-size:11px;">No vector variances.</div>'
        b_series = pd.Series(b_diffs).sort_values(ascending=(False if is_wow else True)).head(5)
        
        html_b = '<div style="padding: 4px 16px; background: rgba(255,255,255,0.02); border-radius: 6px; margin: 4px 0 8px 20px;">'
        for b_name, b_val in b_series.items():
            b_color = "var(--green)" if b_val > 0 else "var(--red)"
            html_b += f'<div style="display:flex; justify-content:space-between; font-size:11.5px; padding: 3px 0; border-bottom:1px dashed rgba(255,255,255,0.04);"><span style="color:var(--muted);">{b_name}</span><span style="color:{b_color}; font-weight:600;">{"+" if b_val > 0 else ""}{int(b_val)}</span></div>'
        html_b += '</div>'
        return html_b

    def build_split_row(series, col_title, is_positive, total_ref, mode_type="wow"):
        color = "var(--green)" if is_positive else "var(--red)"
        icon = "📈" if is_positive else "📉"
        if mode_type == "cum": icon = "⭐" if is_positive else "⚠️"
        
        html = '<div style="flex:1; min-width:0;">'
        html += f'<div style="font-size:10.5px; color:{color}; font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">{icon} {col_title}</div>'
        
        if series.empty:
            html += f'<div style="font-size:12px; color:var(--muted); padding:8px 0;">No active elements inside window.</div>'
        else:
            for name, val in series.items():
                pct = (val / total_ref * 100) if total_ref else 0
                sign = "+" if val > 0 else ""
                
                if breakdown_col and breakdown_col in df_window.columns:
                    html += f'''
                    <div style="padding: 6px 0; border-bottom: 1px dashed var(--br);">
                        <details class="vl-expander">
                            <summary style="cursor: pointer; outline: none;">
                                <div style="display:flex; align-items:center; max-width:65%;">
                                    <span class="exp-icon"></span>
                                    <span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-weight:500;" title="{name}">{name}</span>
                                </div>
                                <div style="text-align:right; display:flex; align-items:center; gap:6px;">
                                    <span style="color:{color}; font-weight:800;">{sign}{int(val)}</span>
                                    <span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{abs(pct):.1f}%</span>
                                </div>
                            </summary>
                            {get_breakdown_html(name, mode_type == "wow")}
                        </details>
                    </div>'''
                else:
                    html += f'''
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:12.5px; padding:6px 0; border-bottom:1px dashed var(--br);">
                        <span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:65%; font-weight:500;" title="{name}">{name}</span>
                        <div style="text-align:right; display:flex; align-items:center; gap:6px;">
                            <span style="color:{color}; font-weight:800;">{sign}{int(val)}</span>
                            <span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{abs(pct):.1f}%</span>
                        </div>
                    </div>'''
        html += '</div>'
        return html

    html = f'<div class="rca-card"><div class="rca-ttl">{title} Movers Matrix</div>'
    
    html += '<details class="section-expander">'
    html += '<summary style="font-weight:700; font-size:12px; color:var(--blue); outline:none;"><span class="sec-icon"></span>⚡ Weekly Shift Metrics (Current vs Previous Week)</summary>'
    html += '<div style="display:flex; gap:20px; margin-top:12px;">'
    html += build_split_row(wow_growers, "Top 5 Expansion", True, total_wow_growth, "wow")
    html += build_split_row(wow_decliners, "Top 5 Contraction", False, total_wow_drop, "wow")
    html += '</div></details>'
    
    html += '<div class="section-divider"></div>'
    
    html += '<details class="section-expander">'
    html += f'<summary style="font-weight:700; font-size:12px; color:var(--blue); outline:none;"><span class="sec-icon"></span>📊 Cumulative Timeline Benchmarks (Past {len(available_weeks)} Weeks Summary)</summary>'
    html += '<div style="display:flex; gap:20px; margin-top:12px;">'
    html += build_split_row(cum_performers, "Top 5 Performers", True, total_cum_growth, "cum")
    html += build_split_row(cum_defaulters, "Top 5 Laggards / Defaulters", False, total_cum_drop, "cum")
    html += '</div></details>'
    
    html += '</div>'
    return html

# --- TABLE RENDER FORMATTERS ---
def render_grouped_tracker_table(df, n_weeks, group_col, target_map, metric='Actuals'):
    all_target_weeks = list(range(26, MAX_WEEK + 1))
    available_weeks = all_target_weeks[-n_weeks:]
    if not available_weeks: return pd.DataFrame().style
    
    entities = list(target_map.keys())
    base_grid = pd.MultiIndex.from_product([available_weeks, entities], names=['Week', group_col]).to_frame(index=False)
    
    if not df.empty and 'Week' in df.columns and group_col in df.columns:
        df_filtered = df[(df['Week'] >= 26) & (df['Week'] <= MAX_WEEK)]
        df_filtered = df_filtered[df_filtered['Week'].isin(available_weeks)]
        
        if metric == 'Actuals':
            phone_col = next((col for col in df_filtered.columns if 'phone' in str(col).lower()), None)
            if phone_col:
                actuals = df_filtered.groupby(['Week', group_col])[phone_col].count().reset_index(name='Actuals')
            else:
                actuals = df_filtered.groupby(['Week', group_col]).size().reset_index(name='Actuals')
        else:
            actuals = df_filtered.groupby(['Week', group_col])['Net New Additions'].sum().reset_index(name='Actuals')
            
        merged = pd.merge(base_grid, actuals, on=['Week', group_col], how='left').fillna(0)
    else:
        merged = base_grid
        merged['Actuals'] = 0

    def get_target(row):
        w = row['Week']
        e = row[group_col]
        if e in target_map and w in target_map[e]: return target_map[e][w]
        return 0
        
    merged['Target'] = merged.apply(get_target, axis=1)

    if not DISABLE_PROJECTION and CURRENT_WEEK in merged['Week'].values:
        pacing_multiplier = calculate_pacing_multiplier(df, 'first_date_of_work')
        for entity in merged[group_col].unique():
            mask_curr = (merged[group_col] == entity) & (merged['Week'] == CURRENT_WEEK)
            curr_val = merged.loc[mask_curr, 'Actuals'].values[0]
            merged.loc[mask_curr, 'Actuals'] = int(round(curr_val * pacing_multiplier))

    merged = merged[(merged['Target'] > 0) | (merged['Actuals'] > 0)]
    merged['Deficit'] = merged['Actuals'] - merged['Target']
    merged = merged.sort_values(['Week', 'Target'], ascending=[False, False])
    
    return add_subtotal(merged).style.apply(style_placements_row, axis=1).format(format_numbers)

def render_placements_section(title, condition, target_key, n_weeks_key):
    st.markdown(f"#### {title}")
    n = get_short_number_input("Last N Weeks", n_weeks_key)
    styled_df = format_placements_table(df_placements, condition, target_key, n)
    st.dataframe(styled_df, width="stretch", hide_index=True)
    
    filtered_df = df_placements[df_placements.apply(condition, axis=1)] if not df_placements.empty else pd.DataFrame()
    pacing_multiplier = calculate_pacing_multiplier(df_placements, 'first_date_of_work') if not df_placements.empty else 1.0

    spot_col1, spot_col2 = st.columns(2)
    with spot_col1:
        client_html = generate_dual_spotlight_card(filtered_df, count_unique_phones, "company_name", "Client Profile", n, pacing_multiplier=pacing_multiplier)
        if client_html: st.markdown(client_html, unsafe_allow_html=True)
    with spot_col2:
        vl_col = next((c for c in ['vl_name', 'VL Name', 'vl'] if c in filtered_df.columns), None)
        vl_html = generate_dual_spotlight_card(filtered_df, count_unique_phones, vl_col, "Vendor Line (VL)", n, "company_name", pacing_multiplier=pacing_multiplier) if vl_col else ""
        if vl_html: st.markdown(vl_html, unsafe_allow_html=True)
    st.markdown("---")

def render_capacity_section(title, condition, target_key, n_weeks_key):
    st.markdown(f"#### {title}")
    n = get_short_number_input("Last N Weeks", n_weeks_key)
    styled_df = format_capacity_table(df_capacity, condition, target_key, n)
    st.dataframe(styled_df, width="stretch", hide_index=True)
    
    filtered_df = df_capacity[df_capacity.apply(condition, axis=1)] if not df_capacity.empty else pd.DataFrame()
    spot_col1, spot_col2 = st.columns(2)
    def calc_capacity_net(sub_df):
        add = sub_df['New TCs'].sum() if 'New TCs' in sub_df.columns else len(sub_df)
        churn = sub_df['Churned TCs'].sum() if 'Churned TCs' in sub_df.columns else 0
        backfill = sub_df['Resurrected TCs'].sum() if 'Resurrected TCs' in sub_df.columns else 0
        return int(add + backfill - churn)

    with spot_col1:
        reg_col = next((c for c in ['Region', 'region', 'Mapped_Region'] if c in filtered_df.columns), None)
        reg_html = generate_dual_spotlight_card(filtered_df, calc_capacity_net, reg_col, "Regional Footprint", n) if reg_col else ""
        if reg_html: st.markdown(reg_html, unsafe_allow_html=True)
    with spot_col2:
        vl_col = next((c for c in ['VL Name', 'vl_name'] if c in filtered_df.columns), None)
        vl_html = generate_dual_spotlight_card(filtered_df, calc_capacity_net, vl_col, "Vendor Line (VL)", n, reg_col) if vl_col else ""
        if vl_html: st.markdown(vl_html, unsafe_allow_html=True)
    st.markdown("---")

def render_demand_client_table(df, n_weeks):
    all_target_weeks = list(range(26, MAX_WEEK + 1))
    available_weeks = all_target_weeks[-n_weeks:]
    if not available_weeks: return pd.DataFrame().style
    
    clients = list(CLIENT_TARGETS_MAP.keys())
    base_grid = pd.MultiIndex.from_product([available_weeks, clients], names=['Week', 'Client']).to_frame(index=False)
    
    if not df.empty and 'Week' in df.columns:
        df_filtered = df[(df['Week'] >= 26) & (df['Week'] <= MAX_WEEK)]
        df_filtered = df_filtered[df_filtered['Week'].isin(available_weeks)]
        
        phone_col = next((col for col in df_filtered.columns if 'phone' in str(col).lower()), None)
        if phone_col:
            actuals = df_filtered.groupby(['Week', 'company_name'])[phone_col].count().reset_index(name='Actuals')
        else:
            actuals = df_filtered.groupby(['Week', 'company_name']).size().reset_index(name='Actuals')
            
        actuals = actuals.rename(columns={'company_name': 'Client'})
        merged = pd.merge(base_grid, actuals, on=['Week', 'Client'], how='left').fillna(0)
    else:
        merged = base_grid
        merged['Actuals'] = 0

    def get_client_target(row):
        w = row['Week']
        c = row['Client']
        if c in CLIENT_TARGETS_MAP and w in CLIENT_TARGETS_MAP[c]:
            return CLIENT_TARGETS_MAP[c][w]
        return 0
        
    merged['Target'] = merged.apply(get_client_target, axis=1)

    if not DISABLE_PROJECTION and CURRENT_WEEK in merged['Week'].values:
        pacing_multiplier = calculate_pacing_multiplier(df, 'first_date_of_work')
        for client in merged['Client'].unique():
            mask_curr = (merged['Client'] == client) & (merged['Week'] == CURRENT_WEEK)
            curr_val = merged.loc[mask_curr, 'Actuals'].values[0]
            merged.loc[mask_curr, 'Actuals'] = int(round(curr_val * pacing_multiplier))

    merged = merged[(merged['Target'] > 0) | (merged['Actuals'] > 0)]
    merged['Deficit'] = merged['Actuals'] - merged['Target']
    merged = merged.sort_values(['Week', 'Target'], ascending=[False, False])
    
    return add_subtotal(merged).style.apply(style_placements_row, axis=1).format(format_numbers)

def format_placements_table(df, condition_func, target_mapping_name=None, local_n_weeks=10):
    all_target_weeks = list(range(26, MAX_WEEK + 1))
    available_weeks = all_target_weeks[-local_n_weeks:]
    if not available_weeks: return pd.DataFrame()
    
    res_df = pd.DataFrame({'Week': available_weeks})
    
    if not df.empty and 'Week' in df.columns:
        df_filtered = df[(df['Week'] >= 26) & (df['Week'] <= MAX_WEEK)]
        df_filtered = df_filtered[df_filtered.apply(condition_func, axis=1)]
        
        phone_col = next((col for col in df_filtered.columns if 'phone' in str(col).lower()), None)
        if phone_col:
            actuals_grouped = df_filtered.groupby('Week')[phone_col].count().reset_index(name='Actuals')
        else:
            actuals_grouped = df_filtered.groupby('Week').size().reset_index(name='Actuals')
            
        res_df = pd.merge(res_df, actuals_grouped, on='Week', how='left').fillna(0)
    else:
        res_df['Actuals'] = 0
    
    if not DISABLE_PROJECTION and CURRENT_WEEK in res_df['Week'].values:
        pacing_multiplier = calculate_pacing_multiplier(df, 'first_date_of_work')
        idx = res_df.index[res_df['Week'] == CURRENT_WEEK].tolist()[0]
        res_df.at[idx, 'Actuals'] = int(round(res_df.at[idx, 'Actuals'] * pacing_multiplier))

    def get_target(w):
        if target_mapping_name == "VL" and w in PLACEMENT_WEEK_KEYS: return TARGETS_VL[PLACEMENT_WEEK_KEYS.index(w)]
        elif target_mapping_name == "DC+BPO" and w in PLACEMENT_WEEK_KEYS: return TARGETS_DC_BPO[PLACEMENT_WEEK_KEYS.index(w)]
        elif target_mapping_name in PLACEMENT_TARGETS_MAP and w in PLACEMENT_TARGETS_MAP[target_mapping_name]:
            return PLACEMENT_TARGETS_MAP[target_mapping_name][w]
        return 0

    res_df['Target'] = res_df['Week'].apply(get_target)
    res_df['Deficit'] = res_df['Actuals'] - res_df['Target']
    res_df = res_df[['Week', 'Target', 'Actuals', 'Deficit']].sort_values('Week', ascending=True)
    
    return add_subtotal(res_df).style.apply(style_placements_row, axis=1).format(format_numbers)

def format_capacity_table(df, condition_func, target_mapping_name=None, local_n_weeks=10):
    all_target_weeks = list(range(26, MAX_WEEK + 1))
    available_weeks = all_target_weeks[-local_n_weeks:]
    if not available_weeks: return pd.DataFrame()
    
    res_df = pd.DataFrame({'Week': available_weeks})
    
    if not df.empty and 'Week' in df.columns:
        df_filtered = df[(df['Week'] >= 26) & (df['Week'] <= MAX_WEEK)]
        df_filtered = df_filtered[df_filtered.apply(condition_func, axis=1)]
        metrics = df_filtered.groupby('Week').agg(
            Additions=('New TCs', 'sum') if 'New TCs' in df_filtered.columns else ('Week', 'size'),
            Churn=('Churned TCs', 'sum') if 'Churned TCs' in df_filtered.columns else ('Week', lambda x: 0),
            Backfill=('Resurrected TCs', 'sum') if 'Resurrected TCs' in df_filtered.columns else ('Week', lambda x: 0)
        ).reset_index()
        res_df = pd.merge(res_df, metrics, on='Week', how='left').fillna(0)
    else:
        res_df['Additions'] = 0
        res_df['Churn'] = 0
        res_df['Backfill'] = 0
        
    if not DISABLE_PROJECTION and CURRENT_WEEK in res_df['Week'].values:
        today = datetime.date.today()
        days_elapsed = max(1, today.weekday() + 1)
        remaining_days = max(0, 7 - days_elapsed)
        if remaining_days > 0:
            idx = res_df.index[res_df['Week'] == CURRENT_WEEK].tolist()[0]
            for col in ['Additions', 'Churn', 'Backfill']:
                past_avg = res_df.loc[res_df['Week'] < CURRENT_WEEK, col].mean()
                if pd.isna(past_avg):
                    past_avg = (res_df.at[idx, col] / days_elapsed) * 7
                daily_rate = past_avg / 7.0
                res_df.at[idx, col] = int(round(res_df.at[idx, col] + (daily_rate * remaining_days)))
    
    def get_cap_target(w):
        if w in CAPACITY_WEEK_KEYS:
            idx = CAPACITY_WEEK_KEYS.index(w)
            if target_mapping_name == "Existing VL": return CAP_EXISTING_VL[idx]
            if target_mapping_name == "DC+BPO": return CAP_DC[idx] + CAP_BPO[idx]
            if target_mapping_name == "DC": return CAP_DC[idx]
            if target_mapping_name == "BPO": return CAP_BPO[idx]
        return 0

    res_df['Target'] = res_df['Week'].apply(get_cap_target)
    res_df['Net New Additions'] = res_df['Additions'] + res_df['Backfill'] - res_df['Churn']
    res_df = res_df[['Week', 'Target', 'Additions', 'Churn', 'Backfill', 'Net New Additions']].sort_values('Week', ascending=True)
    
    return add_subtotal(res_df).style.apply(style_capacity_row, axis=1).format(format_numbers)


def df_to_markdown(styler_obj):
    if not hasattr(styler_obj, 'data') or styler_obj.data.empty: return "No data available."
    df = styler_obj.data.copy()
    md = f"| {' | '.join(df.columns)} |\n"
    md += f"| {' | '.join(['---'] * len(df.columns))} |\n"
    for _, row in df.iterrows():
        md += f"| {' | '.join([str(val) for val in row.values])} |\n"
    return md

# --- APPLICATION COMPONENT STRUCTURE ---
tab1, tab2, tab3, tab4 = st.tabs(["Placements", "Capacity", "Demand", "Email Template ✉️"])

with tab1:
    st.header("Placements")
    sub_tab1_supply, sub_tab1_dcbpo, sub_tab1_region, sub_tab1_cohort = st.tabs(["Supply", "DC + BPO", "Region", "Cohort"])
    
    with sub_tab1_supply:
        # Changed the logic here to explicitly check for the allowed Mapped_Regions AND exclude Remote tags
        render_placements_section("1. Field / SA Overall", lambda x: x.get('Mapped_Region', 'Remote') in FIELD_SA_REGIONS and x.get('Tag', 'Other') != 'Remote', "VL", "n_place_field")
        
        render_placements_section("2. VGP", lambda x: x.get('Tag', 'Other') == 'VGP', "VGP", "n_place_vgp")
        render_placements_section("3. Custom Deals", lambda x: x.get('Tag', 'Other') == 'Custom Deal', "Custom Deal", "n_place_cdeal")
        render_placements_section("4. Custom Tiers", lambda x: x.get('Tag', 'Other') == 'Custom Tier', "Custom Tier", "n_place_ctier")
        render_placements_section("5. Normal Tiers", lambda x: x.get('Tag', 'Other') == 'Normal Tier', "Normal Tier", "n_place_normal")
        render_placements_section("6. Tele / SA Placements", lambda x: x.get('Tag', 'Other') == 'Remote', "Remote", "n_place_tele")

    with sub_tab1_dcbpo:
        render_placements_section("1. DC + BPO", lambda x: x.get('Tag', 'Other') in ['DC', 'BPO'], "DC+BPO", "n_place_dcbpo")
        render_placements_section("2. DC", lambda x: x.get('Tag', 'Other') == 'DC', None, "n_place_dc")
        render_placements_section("3. BPO", lambda x: x.get('Tag', 'Other') == 'BPO', None, "n_place_bpo")
        
    with sub_tab1_region:
        st.markdown("#### Region-Wise Placement Tracker")
        n_region = get_short_number_input("Last N Weeks", "n_place_region_wks")
        st.dataframe(render_grouped_tracker_table(df_placements, n_region, 'Mapped_Region', REGION_TARGETS_MAP), width="stretch", hide_index=True)
        
        df_region_scope = df_placements[(df_placements['Week'] >= 26) & (df_placements['Week'] <= MAX_WEEK) & (df_placements['Mapped_Region'] != "Other")]
        if not df_region_scope.empty:
            pacing_multiplier = calculate_pacing_multiplier(df_placements, 'first_date_of_work') if not df_placements.empty else 1.0
            st.markdown(generate_dual_spotlight_card(df_region_scope, count_unique_phones, "Mapped_Region", "Regional", n_region, pacing_multiplier=pacing_multiplier), unsafe_allow_html=True)
            
    with sub_tab1_cohort:
        st.markdown("#### Cohort-Wise Placement Tracker")
        n_cohort = get_short_number_input("Last N Weeks", "n_place_cohort_wks")
        st.dataframe(render_grouped_tracker_table(df_placements, n_cohort, 'Mapped_Cohort', COHORT_TARGETS_MAP), width="stretch", hide_index=True)
        
        df_cohort_scope = df_placements[(df_placements['Week'] >= 26) & (df_placements['Week'] <= MAX_WEEK) & (df_placements['Mapped_Cohort'] != "Other")]
        if not df_cohort_scope.empty:
            pacing_multiplier = calculate_pacing_multiplier(df_placements, 'first_date_of_work') if not df_placements.empty else 1.0
            st.markdown(generate_dual_spotlight_card(df_cohort_scope, count_unique_phones, "Mapped_Cohort", "Cohort", n_cohort, pacing_multiplier=pacing_multiplier), unsafe_allow_html=True)

with tab2:
    st.header("Capacity")
    sub_tab2_supply, sub_tab2_dcbpo = st.tabs(["Supply", "DC + BPO"])
    
    with sub_tab2_supply:
        st.markdown("### TC Additions / Scale up")
        
        # Changed the logic here to explicitly check for the allowed Mapped_Regions AND exclude Remote tags
        render_capacity_section("1. Field / SA Overall", lambda x: x.get('Mapped_Region', 'Remote') in FIELD_SA_REGIONS and x.get('Tag', 'Other') != 'Remote', "Existing VL", "n_cap_field")
        
        render_capacity_section("2. VGP", lambda x: x.get('Tag', 'Other') == 'VGP', "Existing VL", "n_cap_vgp")
        render_capacity_section("3. Custom Deals", lambda x: x.get('Tag', 'Other') == 'Custom Deal', None, "n_cap_cdeal")
        render_capacity_section("4. BAU / Normal", lambda x: x.get('Tag', 'Other') == 'Normal Tier', None, "n_cap_bau")

        st.markdown("---")
        st.markdown("### Hotline Adoption")
        st.info("Pending data logic as per requirements.")
        
        st.markdown("### VL Additions")
        st.info("Pending data logic as per requirements.")

    with sub_tab2_dcbpo:
        st.markdown("### TC Additions / Scale up")
        render_capacity_section("1. DC + BPO", lambda x: x.get('Tag', 'Other') in ['DC', 'BPO'], "DC+BPO", "n_cap_dcbpo")
        render_capacity_section("2. DC", lambda x: x.get('Tag', 'Other') == 'DC', "DC", "n_cap_dc")
        render_capacity_section("3. BPO", lambda x: x.get('Tag', 'Other') == 'BPO', "BPO", "n_cap_bpo")

        st.markdown("---")
        st.markdown("### Hotline Adoption")
        st.info("Pending data logic as per requirements.")
        
        st.markdown("### VL Additions")
        st.info("Pending data logic as per requirements.")

with tab3:
    st.header("Demand Operations")
    
    st.markdown("#### 1. Client-Wise Demand Tracker")
    n_demand = get_short_number_input("Last N Weeks", "n_demand_weeks")
    
    st.dataframe(render_demand_client_table(df_placements, n_demand), width="stretch", hide_index=True)
    
    df_demand_scope = df_placements[(df_placements['Week'] >= 26) & (df_placements['Week'] <= MAX_WEEK)]
    if not df_demand_scope.empty:
        pacing_multiplier = calculate_pacing_multiplier(df_placements, 'first_date_of_work') if not df_placements.empty else 1.0
        client_html = generate_dual_spotlight_card(df_demand_scope, count_unique_phones, "company_name", "Client Demand", n_demand, pacing_multiplier=pacing_multiplier)
        if client_html: st.markdown(client_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### 2. Support Operations Registry")
    st.info("Data integration pending. Rendering structural framework.")
    
    dummy_support_data = {
        "Client Name": ["Blinkit", "Swiggy Food", "Uber", "Swiggy Instamart", "Rapido"],
        "Support Requirement": ["Active Pipeline Request", "Pending Resolution", "Resolved / Cleared", "Active Pipeline Request", "Pending Resolution"],
        "Status": ["In Progress", "Open", "Closed", "In Progress", "Open"],
        "Action Owner": ["Team Alpha", "Team Beta", "Team Alpha", "Team Charlie", "Team Beta"],
        "Last Updated": ["2026-07-06", "2026-07-07", "2026-07-05", "2026-07-08", "2026-07-08"]
    }
    st.dataframe(pd.DataFrame(dummy_support_data), width="stretch", hide_index=True)


# --- EXCLUSIVE ADMIN EMAIL EXPORT ---
with tab4:
    st.header("Automated Email Report Generator")
    st.markdown("Generates a clean, copy-pasteable Markdown/Text report based on the **last 4 weeks** of Placement performance.")
    
    email_md = "## 1. Placements Summary\n\n"
    
    email_md += "### Field / SA Overall\n"
    # Changed the logic here to explicitly check for the allowed Mapped_Regions AND exclude Remote tags
    email_md += df_to_markdown(format_placements_table(df_placements, lambda x: x.get('Mapped_Region', 'Remote') in FIELD_SA_REGIONS and x.get('Tag', 'Other') != 'Remote', "VL", local_n_weeks=4)) + "\n\n"
    
    email_md += "### VGP\n"
    email_md += df_to_markdown(format_placements_table(df_placements, lambda x: x.get('Tag', 'Other') == 'VGP', "VGP", local_n_weeks=4)) + "\n\n"
    
    email_md += "### Custom Deals\n"
    email_md += df_to_markdown(format_placements_table(df_placements, lambda x: x.get('Tag', 'Other') == 'Custom Deal', "Custom Deal", local_n_weeks=4)) + "\n\n"
    
    email_md += "### Custom Tiers\n"
    email_md += df_to_markdown(format_placements_table(df_placements, lambda x: x.get('Tag', 'Other') == 'Custom Tier', "Custom Tier", local_n_weeks=4)) + "\n\n"
    
    email_md += "### Normal Tiers\n"
    email_md += df_to_markdown(format_placements_table(df_placements, lambda x: x.get('Tag', 'Other') == 'Normal Tier', "Normal Tier", local_n_weeks=4)) + "\n\n"
    
    email_md += "### BPO + DC\n"
    email_md += df_to_markdown(format_placements_table(df_placements, lambda x: x.get('Tag', 'Other') in ['DC', 'BPO'], "DC+BPO", local_n_weeks=4)) + "\n\n"
    
    email_md += "### Region-wise Placement\n"
    email_md += df_to_markdown(render_grouped_tracker_table(df_placements, 4, 'Mapped_Region', REGION_TARGETS_MAP)) + "\n\n"
    
    email_md += "### Cohort-wise Placement\n"
    email_md += df_to_markdown(render_grouped_tracker_table(df_placements, 4, 'Mapped_Cohort', COHORT_TARGETS_MAP)) + "\n\n"
    
    st.text_area("Markdown Report (Ready to copy)", email_md, height=600)
