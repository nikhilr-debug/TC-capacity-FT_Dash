import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="Operations Dashboard", layout="wide")

# --- DESIGN TOKENS & SPOTLIGHT THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    :root {
      --surface: #1a1d27;
      --surface2: #21263a;
      --br: rgba(255,255,255,0.07);
      --br2: rgba(255,255,255,0.13);
      --red: #ff6b6b;
      --green: #6dd67b;
      --muted: #8b8fa8;
      --text: #eaeaea;
    }
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #0f1117 !important;
        color: var(--text) !important;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.5rem;
        color: #7cb9f8;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        padding-bottom: 0.5rem;
    }
    .table-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #00ea7b;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .demand-container {
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
    }
    .rca-card { 
        background: var(--surface); 
        border: 1px solid var(--br2); 
        border-radius: 10px; 
        padding: 16px; 
        margin-bottom: 24px; 
        margin-top: -10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
    }
    .rca-ttl { 
        font-size: 13px; 
        font-weight: 800; 
        color: var(--text); 
        border-bottom: 1px solid var(--br); 
        padding-bottom: 8px; 
        margin-bottom: 12px; 
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Operations Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div style='color:var(--muted); font-size:11.5px; margin-bottom: 20px;'>
    *Current week projected based on % achieved by this day last week unless disabled.<br>
    <span style='color:var(--blue); font-weight:600;'>*Note: Previous day's data is excluded from all calculations until 12:00 PM IST to ensure data completeness.</span>
</div>
""", unsafe_allow_html=True)

# --- DYNAMIC DATE PARAMS FOR API ---
now = datetime.now()
start_of_year = datetime(now.year, 1, 1).strftime('%Y-%m-%d')
end_of_year = datetime(now.year, 12, 31).strftime('%Y-%m-%d')

# --- API CONFIGURATIONS ---
API_KEY = "4aFm2iOoyx8I91svQccdeZr0jmaiUsMFSRinZcmu"
PLACEMENTS_URL = f"https://redash.vahan.link/api/queries/17613/results.json?api_key={API_KEY}"
CAPACITY_URL = f"https://redash.vahan.co/api/queries/17824/results.json?api_key={API_KEY}&p_date.start={start_of_year}&p_date.end={end_of_year}"
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1KotqUM8d_BtKZHLjk5MhADLFgjl5tie_E3_u4yblPOQ/export?format=csv&gid=0"
TICKETS_REDASH_URL = f"https://redash.vahan.co/api/queries/17826/results.json?api_key={API_KEY}"
TICKETS_GSHEET_URL = "https://docs.google.com/spreadsheets/d/1HlNDss1DHLaw_ysW88WEJxtobkhHr1wtrWKoaQ5TtNw/export?format=csv&gid=374524037"

# --- GLOBAL CATEGORIES & SORT ORDERS ---
CORE_REGIONS = ['east', 'mpcg', 'ncr-up', 'south - 2', 'south-1', 'west', 'unattributed']
REGION_ORDER = ['mpcg', 'ncr-up', 'south-1', 'south - 2', 'east', 'west', 'unattributed']
COHORT_ORDER = ['cohort 1', 'cohort 2', 'cohort 3', 'cohort 4', 'bronze'] 

# --- TARGET MAPPINGS ---
overall_client_target = {
    '4w': {25: 50, 27: 67, 28: 97, 29: 115, 30: 167, 31: 194, 32: 261, 33: 298, 34: 381, 35: 456, 36: 570, 37: 640, 38: 740, 39: 800, 40: 828},
    'bigbasket': {25: 0, 27: 43, 28: 43, 29: 64, 30: 144, 31: 186, 32: 333, 33: 375, 34: 508, 35: 700, 36: 918, 37: 1000, 38: 1200, 39: 1383, 40: 1463},
    'blinkit': {25: 3537, 27: 3537, 28: 3760, 29: 3760, 30: 3760, 31: 3960, 32: 4177, 33: 4277, 34: 4427, 35: 4577, 36: 4829, 37: 4929, 38: 4979, 39: 4979, 40: 4979},
    'blinkit picker packer': {25: 263, 27: 263, 28: 283, 29: 303, 30: 323, 31: 333, 32: 363, 33: 363, 34: 388, 35: 598, 36: 465, 37: 758, 38: 645, 39: 938, 40: 825},
    'maid': {25: 80, 27: 80, 28: 100, 29: 120, 30: 120, 31: 120, 32: 120, 33: 120, 34: 120, 35: 120, 36: 120, 37: 120, 38: 120, 39: 150, 40: 120},
    'rapido': {25: 0, 27: 0, 28: 0, 29: 75, 30: 200, 31: 300, 32: 380, 33: 500, 34: 600, 35: 700, 36: 800, 37: 900, 38: 1000, 39: 1000, 40: 1000},
    'small clients': {25: 0, 27: 0, 28: 0, 29: 20, 30: 50, 31: 100, 32: 150, 33: 200, 34: 300, 35: 400, 36: 500, 37: 550, 38: 600, 39: 600, 40: 600},
    'swiggy': {25: 887, 27: 1243, 28: 1314, 29: 1428, 30: 1685, 31: 1929, 32: 2171, 33: 2418, 34: 2763, 35: 3019, 36: 3269, 37: 3574, 38: 3876, 39: 4223, 40: 4488},
    'swiggy soc': {25: 37, 27: 37, 28: 77, 29: 112, 30: 187, 31: 262, 32: 312, 33: 387, 34: 487, 35: 587, 36: 587, 37: 637, 38: 637, 39: 687, 40: 687},
    'uber': {25: 28, 27: 45, 28: 127, 29: 187, 30: 299, 31: 383, 32: 519, 33: 592, 34: 738, 35: 907, 36: 1115, 37: 1298, 38: 1450, 39: 1603, 40: 1631},
    'amazon flex': {25: 0, 27: 9, 28: 9, 29: 13, 30: 40, 31: 54, 32: 90, 33: 104, 34: 142, 35: 197, 36: 273, 37: 320, 38: 370, 39: 441, 40: 458},
    'flipkart minutes': {25: 135, 27: 0, 28: 40, 29: 110, 30: 170, 31: 200, 32: 250, 33: 300, 34: 350, 35: 400, 36: 500, 37: 550, 38: 550, 39: 600, 40: 600},
    'swiggy instamart': {25: 555, 27: 718, 28: 757, 29: 849, 30: 992, 31: 1124, 32: 1264, 33: 1398, 34: 1590, 35: 1738, 36: 1882, 37: 2052, 38: 2221, 39: 2419, 40: 2566},
    'xpress bees': {25: 28, 27: 37, 28: 37, 29: 50, 30: 67, 31: 80, 32: 128, 33: 146, 34: 205, 35: 254, 36: 331, 37: 388, 38: 473, 39: 539, 40: 586}
}

dc_bpo_overall_targets = {
    'bpo': {25: 0, 27: 26, 28: 56, 29: 168, 30: 378, 31: 491, 32: 875, 33: 986, 34: 1337, 35: 1841, 36: 2448, 37: 2760, 38: 3221, 39: 3707, 40: 3851},
    'dc': {25: 0, 27: 400, 28: 400, 29: 458, 30: 654, 31: 847, 32: 1051, 33: 1282, 34: 1597, 35: 1796, 36: 1992, 37: 2262, 38: 2514, 39: 2881, 40: 3151}
}

tele_remote_target = {
    'target': {27: 557, 28: 611, 29: 651, 30: 710, 31: 781, 32: 851, 33: 912, 34: 996, 35: 1091, 36: 1160, 37: 1257, 38: 1299, 39: 1364, 40: 587}
}

region_target = {
    'unattributed': {27: 180, 28: 197, 29: 210, 30: 229, 31: 232, 32: 207, 33: 225, 34: 242, 35: 282, 36: 224, 37: 250, 38: 255, 39: 267, 40: 112},
    'east': {27: 230, 28: 252, 29: 269, 30: 294, 31: 371, 32: 496, 33: 540, 34: 582, 35: 677, 36: 751, 37: 867, 38: 884, 39: 927, 40: 389},
    'mpcg': {27: 2272, 28: 2490, 29: 2656, 30: 2896, 31: 3149, 32: 3378, 33: 3599, 34: 3955, 35: 4228, 36: 4511, 37: 5057, 38: 5149, 39: 5403, 40: 2266},
    'ncr-up': {27: 1396, 28: 1529, 29: 1632, 30: 1779, 31: 1931, 32: 2063, 33: 2198, 34: 2415, 35: 2582, 36: 2663, 37: 2973, 38: 3027, 39: 3177, 40: 1332},
    'south - 2': {27: 87, 28: 95, 29: 101, 30: 110, 31: 170, 32: 290, 33: 310, 34: 340, 35: 363, 36: 543, 37: 518, 38: 569, 39: 597, 40: 281},
    'south-1': {27: 723, 28: 793, 29: 847, 30: 923, 31: 998, 32: 1035, 33: 1128, 34: 1214, 35: 1412, 36: 1463, 37: 1381, 38: 1516, 39: 1591, 40: 749},
    'west': {27: 176, 28: 193, 29: 206, 30: 225, 31: 247, 32: 265, 33: 289, 34: 312, 35: 370, 36: 392, 37: 379, 38: 415, 39: 435, 40: 205}
}

cohort_target = {
    'cohort 1': {27: 1505, 28: 1648, 29: 1762, 30: 1921, 31: 2059, 32: 2138, 33: 2286, 34: 2501, 35: 2712, 36: 2757, 37: 2999, 38: 3086, 39: 3239, 40: 1382},
    'cohort 2': {27: 1284, 28: 1408, 29: 1504, 30: 1639, 31: 1792, 32: 1927, 33: 2063, 34: 2256, 35: 2457, 36: 2663, 37: 2837, 38: 2953, 39: 3099, 40: 1347},
    'cohort 3': {27: 1090, 28: 1193, 29: 1272, 30: 1387, 31: 1540, 32: 1712, 33: 1834, 34: 2005, 35: 2201, 36: 2343, 37: 2555, 38: 2636, 39: 2767, 40: 1187},
    'cohort 4': {27: 633, 28: 693, 29: 736, 30: 802, 31: 936, 32: 1122, 33: 1205, 34: 1317, 35: 1451, 36: 1653, 37: 1805, 38: 1871, 39: 1964, 40: 844},
    'bronze': {27: 362, 28: 399, 29: 424, 30: 463, 31: 520, 32: 602, 33: 648, 34: 707, 35: 779, 36: 868, 37: 944, 38: 974, 39: 1022, 40: 443}
}

sa_field_targets = {
    'vgp': {27: 1240, 28: 1329, 29: 1355, 30: 1355, 31: 1504, 32: 1866, 33: 1627, 34: 2031, 35: 1846, 36: 2293, 37: 2265, 38: 2568, 39: 2568, 40: 1080},
    'custom deal': {27: 1709, 28: 1828, 29: 1871, 30: 1871, 31: 1990, 32: 2286, 33: 1995, 34: 2485, 35: 2273, 36: 2746, 37: 2741, 38: 3093, 39: 3093, 40: 1291},
    'custom tier': {27: 1749, 28: 1871, 29: 1914, 30: 1914, 31: 2044, 32: 2361, 33: 2062, 34: 2568, 35: 2355, 36: 2740, 37: 2740, 38: 3093, 39: 3093, 40: 1284},
    'normal tiers': {27: 367, 28: 522, 29: 782, 30: 1315, 31: 1560, 32: 1220, 33: 2605, 34: 1975, 35: 3440, 36: 2768, 37: 3669, 38: 3059, 39: 3643, 40: 1679}
}

CAP_EXISTING_VL = {27: 35, 28: 38, 29: 52, 30: 40, 31: 30, 32: 21, 33: 26, 34: 24, 35: 18, 36: 10, 37: 3, 38: 0, 39: 0, 40: 0}
CAP_BPO = {27: 80, 28: 0, 29: 0, 30: 150, 31: 0, 32: 200, 33: 0, 34: 0, 35: 300, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0}
CAP_DC = {27: 0, 28: 15, 29: 40, 30: 23, 31: 25, 32: 25, 33: 20, 34: 20, 35: 20, 36: 10, 37: 0, 38: 0, 39: 0, 40: 0}

# --- STERILIZATION ENGINE (PREVENTS PYARROW CRASHES) ---
def safe_str(val):
    if pd.isna(val) or val is None or val == "":
        return ""
    if isinstance(val, (int, float)):
        return str(int(val)) if float(val).is_integer() else str(round(float(val), 2))
    return str(val)

# --- DATA FETCHING & ROBUST MAPPING ---
@st.cache_data(ttl=600)
def load_all_data():
    headers = {"Authorization": f"Key {API_KEY}"}
    try:
        p_res = requests.get(PLACEMENTS_URL, headers=headers, timeout=60).json()
        df_p = pd.DataFrame(p_res['query_result']['data']['rows'])
        df_p.columns = [str(c).strip().lower().replace(" ", "_") for c in df_p.columns]
    except: df_p = pd.DataFrame()
        
    try:
        c_res = requests.get(CAPACITY_URL, headers=headers, timeout=60).json()
        df_c = pd.DataFrame(c_res['query_result']['data']['rows'])
        df_c.columns = [str(c).strip().lower().replace(" ", "_") for c in df_c.columns]
    except: df_c = pd.DataFrame()
        
    try:
        df_m = pd.read_csv(GSHEET_URL)
        df_m = df_m.dropna(how='all')
        df_m.columns = [str(c).strip().lower().replace(" ", "_") for c in df_m.columns]
        vl_col = next((col for col in df_m.columns if 'vl' in col and 'name' in col), None)
        if not vl_col and 'vl_name' in df_m.columns: vl_col = 'vl_name'
        if vl_col: df_m['vl_name_clean'] = df_m[vl_col].astype(str).str.strip().str.lower()
    except: df_m = pd.DataFrame()
        
    try:
        t_res = requests.get(TICKETS_REDASH_URL, headers=headers, timeout=60).json()
        df_tr = pd.DataFrame(t_res['query_result']['data']['rows'])
        df_tr.columns = [str(c).strip().lower().replace(" ", "_") for c in df_tr.columns]
    except: df_tr = pd.DataFrame()
        
    try:
        df_tg = pd.read_csv(TICKETS_GSHEET_URL)
        df_tg = df_tg.dropna(how='all')
        df_tg.columns = [str(c).strip().lower().replace(" ", "_") for c in df_tg.columns]
    except: df_tg = pd.DataFrame()

    return df_p, df_c, df_m, df_tr, df_tg

df_p_raw, df_c_raw, df_m_raw, df_tr_raw, df_tg_raw = load_all_data()

# --- PREPROCESSING LAYERS ---
mapping_dict = {}
vl_targets = {}

if not df_m_raw.empty and 'vl_name_clean' in df_m_raw.columns:
    col_field = next((c for c in df_m_raw.columns if 'field' in c and 'overall' in c), None)
    col_nt = next((c for c in df_m_raw.columns if 'normal' in c and 'tier' in c), None)
    col_tele = next((c for c in df_m_raw.columns if 'tele' in c and 'placement' in c), None)
    
    # Identify dynamic week target columns
    week_cols = [c for c in df_m_raw.columns if str(c).strip().isdigit()]
    
    for _, row in df_m_raw.iterrows():
        vl = str(row['vl_name_clean']).strip()
        if vl and vl != 'nan':
            mapping_dict[vl] = {
                'region': str(row.get('region', 'remote')).strip().lower(),
                'lever': str(row.get('lever', 'remote')).strip().lower(),
                'cohort': str(row.get('cohort', 'remote')).strip().lower(),
                'custom_field_sa': str(row.get(col_field, '')).strip().lower() if col_field else '',
                'custom_nt': str(row.get(col_nt, '')).strip().lower() if col_nt else '',
                'custom_tele': str(row.get(col_tele, '')).strip().lower() if col_tele else ''
            }
            
            # Map VL Targets
            vl_targets[vl] = {}
            for wc in week_cols:
                val = pd.to_numeric(row[wc], errors='coerce')
                if pd.notna(val):
                    vl_targets[vl][int(str(wc).strip())] = val

total_vls_field_sa = sum(1 for v in mapping_dict.values() if v.get('custom_field_sa') == 'field / sa overall')
total_vls_vgp = sum(1 for v in mapping_dict.values() if v.get('lever') == 'vgp' and v.get('region') in CORE_REGIONS)
total_vls_cd = sum(1 for v in mapping_dict.values() if v.get('lever') in ['custom deal', 'custom deals'] and v.get('region') in CORE_REGIONS)
total_vls_nt = sum(1 for v in mapping_dict.values() if v.get('custom_nt') == 'normal')

def get_mapped_tag(vl_name, tag_type):
    vl_clean = str(vl_name).strip().lower()
    if vl_clean in mapping_dict:
        val = mapping_dict[vl_clean].get(tag_type, '')
        val_str = str(val).strip().lower() if val else ''
        if tag_type == 'region' and val_str in ['#n/a', 'unmapped', 'nan', '', 'null']: return 'remote'
        return val_str if val_str != 'nan' else ''
    return '' if tag_type not in ['region'] else 'remote'

# Process Placements
if not df_p_raw.empty:
    df_p_raw['first_date_of_work'] = pd.to_datetime(df_p_raw['first_date_of_work'], errors='coerce')
    df_p_raw = df_p_raw.dropna(subset=['first_date_of_work'])
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    ist_now = datetime.now(ist_tz)
    if ist_now.hour < 12:
        yesterday = (ist_now - timedelta(days=1)).date()
        df_p_raw = df_p_raw[df_p_raw['first_date_of_work'].dt.date != yesterday]
    df_p_raw['Week'] = df_p_raw['first_date_of_work'].dt.isocalendar().week
    vl_col_p = next((col for col in df_p_raw.columns if col.lower() in ["vl_name", "vl name", "vl"]), None)
    if vl_col_p:
        df_p_raw['vl_name'] = df_p_raw[vl_col_p].astype(str).str.strip().str.lower()
        df_p_raw['mapped_region'] = df_p_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'region'))
        df_p_raw['mapped_lever'] = df_p_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'lever'))
        df_p_raw['mapped_cohort'] = df_p_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'cohort'))
        df_p_raw['mapped_field_sa'] = df_p_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'custom_field_sa'))
        df_p_raw['mapped_nt'] = df_p_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'custom_nt'))
        df_p_raw['mapped_tele'] = df_p_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'custom_tele'))
        df_p_raw['is_unmapped'] = df_p_raw['vl_name'].apply(lambda x: x not in mapping_dict and x != '' and x != 'nan')
    def fix_dc_bpo(row):
        vl = str(row.get('vl_name', '')).strip().lower()
        mapped_lv = str(row.get('mapped_lever', '')).strip().lower()
        if vl in ["direct channel", "dc"] or mapped_lv in ["dc", "direct channel"]: return 'dc'
        if any(bpo in vl for bpo in ["basu business", "rural shores"]) or mapped_lv == "bpo": return 'bpo'
        return row.get('mapped_region', 'remote')
    df_p_raw['mapped_region'] = df_p_raw.apply(fix_dc_bpo, axis=1)
    df_p_raw['company_name_lower'] = df_p_raw.get('company_name', pd.Series()).astype(str).str.strip().str.lower()
    df_p_raw['day_of_week'] = df_p_raw['first_date_of_work'].dt.dayofweek
else:
    df_p_raw = pd.DataFrame(columns=['Week', 'company_name_lower', 'day_of_week', 'vl_name', 'mapped_region'])

# Process Capacity
if not df_c_raw.empty:
    if 'week_start' in df_c_raw.columns:
        df_c_raw['Week'] = pd.to_datetime(df_c_raw['week_start'], errors='coerce').dt.isocalendar().week.fillna(0).astype(int)
    else:
        c_wk_col = next((c for c in df_c_raw.columns if 'week' in c and c != 'week_no'), None)
        if c_wk_col and pd.api.types.is_numeric_dtype(df_c_raw[c_wk_col]): df_c_raw['Week'] = df_c_raw[c_wk_col].fillna(0).astype(int)
        elif c_wk_col: df_c_raw['Week'] = pd.to_datetime(df_c_raw[c_wk_col], errors='coerce').dt.isocalendar().week.fillna(0).astype(int)
        else: df_c_raw['Week'] = 0
    for col in ['new_tcs', 'churned_tcs', 'resurrected_tcs', 'active_tcs']:
        if col in df_c_raw.columns: df_c_raw[col] = pd.to_numeric(df_c_raw[col], errors='coerce').fillna(0)
        else: df_c_raw[col] = 0
    df_c_raw['net_new_additions'] = df_c_raw['new_tcs'] + df_c_raw['resurrected_tcs'] - df_c_raw['churned_tcs']
    vl_col_c = next((c for c in df_c_raw.columns if 'vl' in c and 'name' in c), None)
    if not vl_col_c and 'vl_name' in df_c_raw.columns: vl_col_c = 'vl_name'
    if vl_col_c:
        df_c_raw['vl_name'] = df_c_raw[vl_col_c].astype(str).str.strip().str.lower()
        df_c_raw['mapped_region'] = df_c_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'region'))
        df_c_raw['mapped_lever'] = df_c_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'lever'))
        df_c_raw['mapped_field_sa'] = df_c_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'custom_field_sa'))
        df_c_raw['mapped_nt'] = df_c_raw['vl_name'].apply(lambda x: get_mapped_tag(x, 'custom_nt'))
        def fix_dc_bpo_cap(row):
            vl = str(row['vl_name']).strip().lower()
            mapped_lv = str(row.get('mapped_lever', '')).strip().lower()
            if vl in ["direct channel", "dc"] or mapped_lv in ["dc", "direct channel"]: return 'dc'
            if any(bpo in vl for bpo in ["basu business", "rural shores"]) or mapped_lv == "bpo": return 'bpo'
            return row.get('mapped_region', 'remote')
        df_c_raw['mapped_region'] = df_c_raw.apply(fix_dc_bpo_cap, axis=1)
else:
    df_c_raw = pd.DataFrame(columns=['Week', 'new_tcs', 'churned_tcs', 'resurrected_tcs', 'net_new_additions', 'active_tcs', 'vl_name', 'mapped_region'])

# Process Tickets (Support Details)
frames = []
if not df_tr_raw.empty:
    df_r = df_tr_raw.copy()
    df_r['ticket_id'] = df_r.get('ticket_id', pd.Series(dtype=str)).astype(str)
    df_r['client_name'] = df_r.get('client_name', pd.Series(dtype=str)).astype(str).str.lower().str.strip()
    df_r['status'] = df_r.get('ticket_status', pd.Series(dtype=str)).astype(str).str.lower().str.strip()
    df_r['created_at'] = pd.to_datetime(df_r.get('ticket_created_at'), errors='coerce')
    tat_col = next((c for c in df_r.columns if 'rtat' in c and 'business' in c and 'mins' in c), None)
    if not tat_col: tat_col = next((c for c in df_r.columns if 'response_time_in_business_hours' in c), None)
    if tat_col:
        df_r['rtat_mins'] = pd.to_numeric(df_r[tat_col], errors='coerce')
        if 'secs' in tat_col or tat_col == 'response_time_in_business_hours': df_r['rtat_mins'] = df_r['rtat_mins'] / 60.0
    else: df_r['rtat_mins'] = pd.NA
    frames.append(df_r[['ticket_id', 'client_name', 'status', 'created_at', 'rtat_mins']])

if not df_tg_raw.empty:
    df_g = df_tg_raw.copy()
    df_g['ticket_id'] = df_g.get('ticket_id', pd.Series(dtype=str)).astype(str)
    df_g['client_name'] = df_g.get('client_name', pd.Series(dtype=str)).astype(str).str.lower().str.strip()
    df_g['status'] = df_g.get('status', pd.Series(dtype=str)).astype(str).str.lower().str.strip()
    df_g['created_at'] = pd.to_datetime(df_g.get('created_date'), errors='coerce')
    tat_col_g = next((c for c in df_g.columns if 'refined' in c and 'rtat' in c and 'minute' in c), None)
    df_g['rtat_mins'] = pd.to_numeric(df_g[tat_col_g], errors='coerce') if tat_col_g else pd.NA
    frames.append(df_g[['ticket_id', 'client_name', 'status', 'created_at', 'rtat_mins']])

if frames:
    df_tickets = pd.concat(frames, ignore_index=True)
    df_tickets['Week'] = df_tickets['created_at'].dt.isocalendar().week.fillna(0).astype(int)
    df_tickets['is_resolved'] = df_tickets['status'].isin(['closed', 'resolved'])
else:
    df_tickets = pd.DataFrame(columns=['ticket_id', 'client_name', 'status', 'created_at', 'rtat_mins', 'Week', 'is_resolved'])

# --- MASTER PROJECTION & RUNRATE LOGIC ---
current_week_no = datetime.now().isocalendar()[1]
st.sidebar.header("Global Filters")
DISABLE_PROJECTION = st.sidebar.checkbox("View Actuals Only (Disable Projections)", value=False)
if not df_p_raw.empty:
    df_cw = df_p_raw[df_p_raw['Week'] == current_week_no]
    active_days_cw = df_cw['day_of_week'].unique()
    df_lw = df_p_raw[df_p_raw['Week'] == current_week_no - 1]
    total_lw = len(df_lw)
    if len(active_days_cw) > 0:
        same_days_lw = len(df_lw[df_lw['day_of_week'].isin(active_days_cw)])
        run_rate = total_lw / same_days_lw if same_days_lw > 0 else 1.0
    else: run_rate = 1.0
else: run_rate = 1.0

def generate_projection_series(actual_series, week_series):
    projected_out = []
    for w, act in zip(week_series, actual_series):
        if w == current_week_no and not DISABLE_PROJECTION: projected_out.append(int(round(act * run_rate)))
        else: projected_out.append(int(act))
    return projected_out

# --- VL SPOTLIGHT ENGINE ---
def render_spotlight(df_category, title, is_capacity=False):
    if df_category.empty: return ""
    cw = current_week_no
    pw = current_week_no - 1
    
    if is_capacity:
        agg_cw = df_category[df_category['Week'] == cw].groupby('vl_name')['net_new_additions'].sum()
        agg_pw = df_category[df_category['Week'] == pw].groupby('vl_name')['net_new_additions'].sum()
        agg_cum = df_category[df_category['Week'] <= cw].groupby('vl_name')['net_new_additions'].sum()
    else:
        agg_cw = df_category[df_category['Week'] == cw].groupby('vl_name').size()
        agg_pw = df_category[df_category['Week'] == pw].groupby('vl_name').size()
        agg_cum = df_category[df_category['Week'] <= cw].groupby('vl_name').size()

    cat_wow_delta = agg_cw.sum() - agg_pw.sum()

    wow_data = []
    for vl in set(agg_cw.index).union(set(agg_pw.index)):
        if vl == 'nan' or vl == '': continue
        c_act = agg_cw.get(vl, 0)
        p_act = agg_pw.get(vl, 0)
        c_tgt = vl_targets.get(vl, {}).get(cw, 0)

        if c_act < c_tgt:
            delta = c_act - p_act
            wow_data.append({
                'vl': vl.title(), 'delta': delta, 'pct': (delta/p_act*100) if p_act>0 else 0,
                'act': c_act, 'tgt': c_tgt
            })

    wow_df = pd.DataFrame(wow_data)
    if not wow_df.empty:
        wow_df['contr'] = wow_df['delta'].apply(lambda x: (x/cat_wow_delta*100) if cat_wow_delta < 0 and x < 0 else 0)
        wow_df = wow_df.sort_values('delta', ascending=True).head(5)

    cum_data = []
    cat_cum_deficit = 0
    for vl in agg_cum.index:
        if vl == 'nan' or vl == '': continue
        act = agg_cum.get(vl, 0)
        tgt = sum([vl_targets.get(vl, {}).get(w, 0) for w in range(27, cw + 1)])
        deficit = act - tgt
        if deficit < 0:
            cat_cum_deficit += deficit
            cum_data.append({
                'vl': vl.title(), 'deficit': deficit, 'act': act, 'tgt': tgt
            })

    cum_df = pd.DataFrame(cum_data)
    if not cum_df.empty:
        cum_df['contr'] = cum_df['deficit'].apply(lambda x: (x/cat_cum_deficit*100) if cat_cum_deficit < 0 else 0)
        cum_df = cum_df.sort_values('deficit', ascending=True).head(5)

    if wow_df.empty and cum_df.empty: return ""

    html = f'''
    <div class="rca-card">
        <div class="rca-ttl">🔍 Spotlight: Bottom 5 VLs ({title})</div>
        <div style="display:flex; gap:20px;">
    '''

    html += '<div style="flex:1;">'
    html += '<div style="font-size:10.5px; color:var(--red); font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">📉 WoW Dip (Missed Target)</div>'
    if not wow_df.empty and wow_df['delta'].min() < 0:
        for _, r in wow_df[wow_df['delta'] < 0].iterrows():
            html += f'''
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; padding:6px 0; border-bottom:1px dashed var(--br);">
                <span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:55%;" title="{r['vl']}">{r['vl']}</span>
                <div style="text-align:right; display:flex; align-items:center; gap:6px;">
                    <span style="color:var(--red); font-weight:800;">{int(r['delta'])} ({r['pct']:.0f}%)</span>
                    <span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{r['contr']:.1f}% ctr</span>
                </div>
            </div>'''
    else: html += '<div style="font-size:11px; color:var(--muted); padding:4px 0;">No WoW dips recorded for underperforming VLs.</div>'
    html += '</div>'

    html += '<div style="flex:1;">'
    html += '<div style="font-size:10.5px; color:var(--amber); font-weight:800; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid var(--br2); padding-bottom:6px;">⚠️ Cumulative Deficit</div>'
    if not cum_df.empty:
        for _, r in cum_df.iterrows():
            html += f'''
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; padding:6px 0; border-bottom:1px dashed var(--br);">
                <span style="color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:55%;" title="{r['vl']}">{r['vl']}</span>
                <div style="text-align:right; display:flex; align-items:center; gap:6px;">
                    <span style="color:var(--amber); font-weight:800;">{int(r['deficit'])}</span>
                    <span style="font-size:9.5px; font-weight:700; color:var(--muted); background:var(--surface2); padding:2px 6px; border-radius:4px;">{r['contr']:.1f}% ctr</span>
                </div>
            </div>'''
    else: html += '<div style="font-size:11px; color:var(--muted); padding:4px 0;">No cumulative deficits recorded.</div>'
    html += '</div>'

    html += '</div></div>'
    return html

# --- GENERAL UTILITY REPORT FORMATTER ---
def build_output_table(df_filtered, target_dict=None, is_capacity=False):
    weeks = [w for w in range(27, current_week_no + 1)]
    records = []
    for w in weeks:
        if not is_capacity: act = len(df_filtered[df_filtered['Week'] == w]) if not df_filtered.empty else 0
        else: act = int(df_filtered[df_filtered['Week'] == w]['net_new_additions'].sum()) if not df_filtered.empty else 0
        tgt = target_dict.get(w, 0) if target_dict else 0
        records.append({'Week': w, 'Target': tgt, 'Actuals': act})
    df_out = pd.DataFrame(records)
    if not df_out.empty:
        if not is_capacity:
            df_out['Projected'] = generate_projection_series(df_out['Actuals'].values, df_out['Week'].values)
            df_out['Deficit'] = df_out['Projected'] - df_out['Target']
        else:
            df_w_filt = lambda wk, col: int(df_filtered[df_filtered['Week'] == wk][col].sum()) if not df_filtered.empty else 0
            df_out['Additions'] = [df_w_filt(wk, 'new_tcs') for wk in weeks]
            df_out['Churn'] = [df_w_filt(wk, 'churned_tcs') for wk in weeks]
            df_out['Backfill'] = [df_w_filt(wk, 'resurrected_tcs') for wk in weeks]
            df_out['Net New Additions'] = df_out['Actuals']
            df_out = df_out.drop(columns=['Actuals'])
        cum_row = {'Week': 'Cumulative'}
        for col in df_out.columns:
            if col != 'Week': cum_row[col] = df_out[col].sum()
        df_sorted = df_out.iloc[::-1].reset_index(drop=True)
        df_final = pd.concat([pd.DataFrame([cum_row]), df_sorted], ignore_index=True)
        for col in df_final.columns: df_final[col] = df_final[col].apply(safe_str)
    else: df_final = pd.DataFrame()
    def style_rows(row):
        try:
            t_val, a_val = row.get('Target', ""), row.get('Net New Additions', row.get('Projected', row.get('Actuals', "")))
            if t_val == "" or a_val == "": return [''] * len(row)
            t, a = float(t_val), float(a_val)
            if t == 0: return [''] * len(row)
            if a >= t: return ['background-color: #0e2a15; color: #00ea7b; font-weight: bold;'] * len(row)
            else: return ['background-color: #381313; color: #ff6b6b; font-weight: bold;'] * len(row)
        except: return [''] * len(row)
    if not df_final.empty:
        styled = df_final.style.apply(style_rows, axis=1)
        styled = styled.set_properties(**{'text-align': 'center'})
        styled = styled.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        return styled
    return pd.DataFrame()

# --- HOTLINE ADOPTION TABLE GENERATOR ---
def build_hotline_adoption_table(df_filtered, total_vls):
    weeks_asc = [w for w in range(27, current_week_no + 1)]
    weeks_desc = sorted(weeks_asc, reverse=True)
    records = []
    for w in weeks_desc:
        df_w = df_filtered[df_filtered['Week'] == w] if not df_filtered.empty else pd.DataFrame()
        valid_vls = df_w[~df_w['vl_name'].isin(['', 'nan', 'null', None])]['vl_name'].nunique() if not df_w.empty else 0
        hotline_tcs = int(df_w['active_tcs'].sum()) if not df_w.empty else 0
        adoption_vl_perc = f"{round((valid_vls / total_vls) * 100, 1)}%" if total_vls > 0 else "0.0%"
        records.append({
            'Week': w,
            'Hotline VLs': valid_vls,
            'Total VLs': total_vls,
            'Adoption @ VL %': adoption_vl_perc,
            'Hotline TCs': hotline_tcs,
            'Total TCs': "",
            'Adoption @ TC %': ""
        })
    df_out = pd.DataFrame(records)
    if not df_out.empty:
        for col in df_out.columns: df_out[col] = df_out[col].apply(safe_str)
        styled = df_out.style.set_properties(**{'text-align': 'center'})
        styled = styled.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        return styled
    return pd.DataFrame()

# --- PIVOT TABLE ENGINE WITH EXACT SORTING AND DEFICITS ---
def build_pivot_table(df_filtered, dimension_col, target_dict_map, dimension_name, sort_order):
    weeks_asc = [w for w in range(27, current_week_no + 1)]
    weeks_desc = sorted(weeks_asc, reverse=True)
    lw = current_week_no if weeks_asc else 27
    rows = []
    valid_entities = [e for e in sort_order if e in target_dict_map or (not df_filtered.empty and e in df_filtered[dimension_col].unique())]
    for e in valid_entities:
        row_data = {(dimension_name, ''): str(e).upper()}
        for w in weeks_desc:
            tgt = target_dict_map.get(e, {}).get(w, 0)
            df_w = df_filtered[(df_filtered[dimension_col] == e) & (df_filtered['Week'] == w)]
            act = len(df_w) if not df_w.empty else 0
            proj = int(round(act * run_rate)) if w == current_week_no and not DISABLE_PROJECTION else act
            row_data[(f"Week {w}", "Target")] = tgt
            row_data[(f"Week {w}", "Actuals")] = act
            row_data[(f"Week {w}", "Projected")] = proj
            row_data[(f"Week {w}", "Deficit")] = proj - tgt
        rows.append(row_data)
    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        df_out.columns = pd.MultiIndex.from_tuples(df_out.columns)
        total_row = {(dimension_name, ''): 'TOTAL'}
        for w in weeks_desc:
            sum_tgt = df_out[(f"Week {w}", "Target")].sum()
            sum_act = df_out[(f"Week {w}", "Actuals")].sum()
            sum_proj = df_out[(f"Week {w}", "Projected")].sum()
            sum_def = df_out[(f"Week {w}", "Deficit")].sum() 
            total_row[(f"Week {w}", "Target")] = sum_tgt
            total_row[(f"Week {w}", "Actuals")] = sum_act
            total_row[(f"Week {w}", "Projected")] = sum_proj
            total_row[(f"Week {w}", "Deficit")] = sum_def
        cum_row = {(dimension_name, ''): 'CUMULATIVE'}
        for w in weeks_desc:
            if w == lw:
                cum_row[(f"Week {w}", "Target")] = sum([total_row[(f"Week {wk}", "Target")] for wk in weeks_desc])
                cum_row[(f"Week {w}", "Actuals")] = sum([total_row[(f"Week {wk}", "Actuals")] for wk in weeks_desc])
                cum_row[(f"Week {w}", "Projected")] = sum([total_row[(f"Week {wk}", "Projected")] for wk in weeks_desc])
                cum_row[(f"Week {w}", "Deficit")] = sum([total_row[(f"Week {wk}", "Deficit")] for wk in weeks_desc])
            else:
                cum_row[(f"Week {w}", "Target")] = ""
                cum_row[(f"Week {w}", "Actuals")] = ""
                cum_row[(f"Week {w}", "Projected")] = ""
                cum_row[(f"Week {w}", "Deficit")] = ""
        df_out.loc[len(df_out)] = total_row
        df_out.loc[len(df_out)] = cum_row
        for col in df_out.columns: df_out[col] = df_out[col].apply(safe_str)
        df_out.columns = pd.MultiIndex.from_tuples(df_out.columns)
    def style_pivot(row):
        styles = [''] * len(row)
        for i, col in enumerate(row.index):
            if isinstance(col, tuple) and len(col) > 1:
                if col[1] in ['Projected', 'Actuals']:
                    tgt_col = (col[0], 'Target')
                    if tgt_col in row.index:
                        try:
                            if row[tgt_col] != "" and row[col] != "":
                                tgt, act = float(row[tgt_col]), float(row[col])
                                if tgt > 0:
                                    if act >= tgt: styles[i] = 'background-color: #0e2a15; color: #00ea7b; font-weight: bold;'
                                    else: styles[i] = 'background-color: #381313; color: #ff6b6b; font-weight: bold;'
                        except: pass
                elif col[1] == 'Deficit':
                    try:
                        val = row[col]
                        if val != "":
                            if float(val) >= 0: styles[i] = 'color: #00ea7b; font-weight: bold;'
                            else: styles[i] = 'color: #ff6b6b; font-weight: bold;'
                    except: pass
        return styles
    if not df_out.empty:
        styled = df_out.style.apply(style_pivot, axis=1)
        styled = styled.set_properties(**{'text-align': 'center'})
        styled = styled.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        return styled
    return pd.DataFrame()

# --- TABS DISTRIBUTION MAP LAYOUT ---
tab_supply, tab_bpo, tab_demand = st.tabs(["1. Supply Tab", "2. BPO Tab", "3. Demand Tab"])

with tab_supply:
    st.markdown("### 📊 Placements Metrics (Supply)")
    field_sa_overall_targets = {w: sum(sa_field_targets[k].get(w, 0) for k in sa_field_targets) for w in range(27, 41)}
    
    cond_field_sa = (df_p_raw['mapped_field_sa'] == 'field / sa overall') | (df_p_raw['vl_name'] == '') | (df_p_raw['vl_name'] == 'nan') | df_p_raw['vl_name'].isna()
    df_field_sa = df_p_raw[cond_field_sa]
    df_vgp = df_p_raw[df_p_raw['mapped_region'].isin(CORE_REGIONS) & (df_p_raw['mapped_lever'] == 'vgp')]
    df_cd = df_p_raw[df_p_raw['mapped_region'].isin(CORE_REGIONS) & (df_p_raw['mapped_lever'].isin(['custom deal', 'custom deals']))]
    df_ct = df_p_raw[df_p_raw['mapped_region'].isin(CORE_REGIONS) & (df_p_raw['mapped_lever'].isin(['custom tier', 'custom tiers']))]
    df_nt = df_p_raw[df_p_raw['mapped_nt'] == 'normal']
    cond_tele = (df_p_raw['mapped_tele'] == 'remote') | ((df_p_raw['vl_name'] != '') & (df_p_raw['vl_name'] != 'nan') & df_p_raw['vl_name'].notna() & (df_p_raw['is_unmapped'] == True))
    df_tele = df_p_raw[cond_tele]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="table-header">Field / SA Overall (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_field_sa, target_dict=field_sa_overall_targets), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_field_sa, "Field / SA Overall"), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">Custom Deals (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_cd, target_dict=sa_field_targets['custom deal']), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_cd, "Custom Deals"), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">Normal Tiers (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_nt, target_dict=sa_field_targets['normal tiers']), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_nt, "Normal Tiers"), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="table-header">VGP (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_vgp, target_dict=sa_field_targets['vgp']), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_vgp, "VGP"), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">Custom Tiers (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_ct, target_dict=sa_field_targets['custom tier']), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_ct, "Custom Tiers"), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">Tele / SA Placements</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_tele, target_dict=tele_remote_target['target']), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_tele, "Tele / SA"), unsafe_allow_html=True)
    
    st.markdown('<div class="table-header">Region-wise Metrics Breakdowns</div>', unsafe_allow_html=True)
    df_regions_only = df_p_raw[df_p_raw['mapped_region'].isin(CORE_REGIONS)]
    st.dataframe(build_pivot_table(df_regions_only, 'mapped_region', region_target, 'Region', REGION_ORDER), use_container_width=True, hide_index=True)
        
    st.markdown('<div class="table-header">Cohort-wise Metrics Breakdowns</div>', unsafe_allow_html=True)
    df_cohorts_only = df_p_raw[df_p_raw['mapped_cohort'].isin(COHORT_ORDER)]
    st.dataframe(build_pivot_table(df_cohorts_only, 'mapped_cohort', cohort_target, 'Cohort', COHORT_ORDER), use_container_width=True, hide_index=True)
        
    st.markdown("---")
    st.markdown("### 📞 Capacity Metrics (Supply)")
    with st.expander("🛠 Capacity Data Debugger (Click to Expand)"):
        st.write("If the capacity tables are evaluating to 0, use this to investigate why. **Use the copy icon in the top right of the code block below to copy the raw data summary.**")
        if not df_c_raw.empty:
            debug_cols = [c for c in ['Week', 'vl_name', 'new_tcs', 'resurrected_tcs', 'churned_tcs', 'net_new_additions', 'active_tcs'] if c in df_c_raw.columns]
            debug_text = f"--- RAW DATASET COLUMNS ---\n{list(df_c_raw.columns)}\n\n"
            if 'Week' in df_c_raw.columns: debug_text += f"--- PARSED VALID WEEKS ---\n{sorted(list(df_c_raw['Week'].unique()))}\n\n"
            else: debug_text += "--- PARSED VALID WEEKS ---\nERROR: 'Week' column failed to parse entirely.\n\n"
            debug_text += "--- SAMPLE DATA (FIRST 10 ROWS) ---\n"
            debug_text += df_c_raw[debug_cols].head(10).to_csv(index=False)
            st.code(debug_text, language='csv')
        else: st.error("The Capacity dataframe is completely empty. Ensure your Redash API returns rows and isn't timing out.")

    cond_field_sa_c = (df_c_raw['mapped_field_sa'] == 'field / sa overall') | (df_c_raw['vl_name'] == '') | (df_c_raw['vl_name'] == 'nan') | df_c_raw['vl_name'].isna()
    df_cap_field = df_c_raw[cond_field_sa_c]
    df_cap_vgp = df_c_raw[df_c_raw['mapped_region'].isin(CORE_REGIONS) & (df_c_raw['mapped_lever'] == 'vgp')]
    df_cap_cd = df_c_raw[df_c_raw['mapped_region'].isin(CORE_REGIONS) & (df_c_raw['mapped_lever'].isin(['custom deal', 'custom deals']))]
    df_cap_nt = df_c_raw[df_c_raw['mapped_nt'] == 'normal']

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="table-header">Field / SA Overall (Capacity)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_cap_field, is_capacity=True, target_dict=CAP_EXISTING_VL), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_cap_field, "Field / SA Overall (Capacity)", True), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">Custom Deals (Capacity)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_cap_cd, is_capacity=True), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_cap_cd, "Custom Deals (Capacity)", True), unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="table-header">VGP (Capacity)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_cap_vgp, is_capacity=True), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_cap_vgp, "VGP (Capacity)", True), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">Normal / Bau (Capacity)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_cap_nt, is_capacity=True), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_cap_nt, "Normal Tiers (Capacity)", True), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔥 Hotline Adoption")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<div class="table-header">Field / SA Overall (Hotline Adoption)</div>', unsafe_allow_html=True)
        st.dataframe(build_hotline_adoption_table(df_cap_field, total_vls_field_sa), use_container_width=True, hide_index=True)
        st.markdown('<div class="table-header">Custom Deals (Hotline Adoption)</div>', unsafe_allow_html=True)
        st.dataframe(build_hotline_adoption_table(df_cap_cd, total_vls_cd), use_container_width=True, hide_index=True)
    with col6:
        st.markdown('<div class="table-header">VGP (Hotline Adoption)</div>', unsafe_allow_html=True)
        st.dataframe(build_hotline_adoption_table(df_cap_vgp, total_vls_vgp), use_container_width=True, hide_index=True)
        st.markdown('<div class="table-header">Normal Tiers (Hotline Adoption)</div>', unsafe_allow_html=True)
        st.dataframe(build_hotline_adoption_table(df_cap_nt, total_vls_nt), use_container_width=True, hide_index=True)

with tab_bpo:
    st.markdown("### 🏢 Placements Metrics (DC + BPO)")
    dc_bpo_combined_targets = {w: sum(dc_bpo_overall_targets[k].get(w, 0) for k in dc_bpo_overall_targets) for w in range(27, 41)}
    df_p_combined = df_p_raw[df_p_raw['mapped_region'].isin(['dc', 'bpo'])]
    df_p_dc = df_p_raw[df_p_raw['mapped_region'] == 'dc']
    df_p_bpo = df_p_raw[df_p_raw['mapped_region'] == 'bpo']
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown('<div class="table-header">DC + BPO (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_p_combined, target_dict=dc_bpo_combined_targets), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_p_combined, "DC + BPO"), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">BPO (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_p_bpo, target_dict=dc_bpo_overall_targets['bpo']), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_p_bpo, "BPO"), unsafe_allow_html=True)
    with col_b2:
        st.markdown('<div class="table-header">DC (Placements)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_p_dc, target_dict=dc_bpo_overall_targets['dc']), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_p_dc, "DC"), unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🏢 Capacity Metrics (DC + BPO)")
    cap_combined_targets = {w: CAP_DC.get(w, 0) + CAP_BPO.get(w, 0) for w in range(27, 41)}
    df_c_combined = df_c_raw[df_c_raw['mapped_region'].isin(['dc', 'bpo'])]
    df_c_dc = df_c_raw[df_c_raw['mapped_region'] == 'dc']
    df_c_bpo = df_c_raw[df_c_raw['mapped_region'] == 'bpo']
    col_b3, col_b4 = st.columns(2)
    with col_b3:
        st.markdown('<div class="table-header">DC + BPO (Capacity)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_c_combined, is_capacity=True, target_dict=cap_combined_targets), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_c_combined, "DC + BPO (Capacity)", True), unsafe_allow_html=True)
        
        st.markdown('<div class="table-header">BPO (Capacity)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_c_bpo, is_capacity=True, target_dict=CAP_BPO), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_c_bpo, "BPO (Capacity)", True), unsafe_allow_html=True)
    with col_b4:
        st.markdown('<div class="table-header">DC (Capacity)</div>', unsafe_allow_html=True)
        st.dataframe(build_output_table(df_c_dc, is_capacity=True, target_dict=CAP_DC), use_container_width=True, hide_index=True)
        st.markdown(render_spotlight(df_c_dc, "DC (Capacity)", True), unsafe_allow_html=True)

with tab_demand:
    st.markdown("### 📈 Client Demand Matrix Tracker")
    weeks_demand = [w for w in range(27, current_week_no + 1)]
    lw = current_week_no if weeks_demand else 27
    unique_clients = sorted(list(df_p_raw['company_name_lower'].dropna().unique())) if not df_p_raw.empty else []
    if 'pronto' in unique_clients: unique_clients.remove('pronto')
    if 'snabbit' in unique_clients: unique_clients.remove('snabbit')
    unique_clients.extend(['pronto', 'snabbit'])
    
    demand_data = []
    for client in unique_clients:
        if not client or client == 'nan': continue
        row_metrics = {('Client / Company', ''): client.upper()}
        tgt_map = overall_client_target.get(client, {})
        for w in sorted(weeks_demand, reverse=True):
            act = len(df_p_raw[(df_p_raw['company_name_lower'] == client) & (df_p_raw['Week'] == w)])
            proj = int(round(act * run_rate)) if w == current_week_no and not DISABLE_PROJECTION else act
            if client in ['pronto', 'snabbit']:
                row_metrics[(f'Week {w}', 'Target')] = 100 if w == lw else 0 
                row_metrics[(f'Week {w}', 'Actuals')] = act
                row_metrics[(f'Week {w}', 'Projected')] = proj
                row_metrics[(f'Week {w}', 'Deficit')] = ""
            else:
                tgt = tgt_map.get(w, 0)
                row_metrics[(f'Week {w}', 'Target')] = tgt
                row_metrics[(f'Week {w}', 'Actuals')] = act
                row_metrics[(f'Week {w}', 'Projected')] = proj
                row_metrics[(f'Week {w}', 'Deficit')] = proj - tgt
        demand_data.append(row_metrics)
        
    demand_data.sort(key=lambda x: x.get((f'Week {lw}', 'Actuals'), 0), reverse=True)
    
    df_demand = pd.DataFrame(demand_data)
    if not df_demand.empty:
        total_row = {('Client / Company', ''): 'TOTAL'}
        for w in sorted(weeks_demand, reverse=True):
            sum_tgt, added_combined = 0, False
            for client in unique_clients:
                if client in ['pronto', 'snabbit']:
                    if w == lw and not added_combined: sum_tgt += 100; added_combined = True
                else: sum_tgt += overall_client_target.get(client, {}).get(w, 0)
            sum_act = df_demand[(f'Week {w}', 'Actuals')].sum()
            sum_proj = df_demand[(f'Week {w}', 'Projected')].sum()
            total_row[(f'Week {w}', 'Target')] = sum_tgt
            total_row[(f'Week {w}', 'Actuals')] = sum_act
            total_row[(f'Week {w}', 'Projected')] = sum_proj
            total_row[(f'Week {w}', 'Deficit')] = sum_proj - sum_tgt
            
        cum_row = {('Client / Company', ''): 'CUMULATIVE'}
        for w in sorted(weeks_demand, reverse=True):
            if w == lw:
                cum_row[(f'Week {w}', 'Target')] = sum([total_row[(f'Week {wk}', 'Target')] for wk in weeks_demand])
                cum_row[(f'Week {w}', 'Actuals')] = sum([total_row[(f'Week {wk}', 'Actuals')] for wk in weeks_demand])
                cum_row[(f'Week {w}', 'Projected')] = sum([total_row[(f'Week {wk}', 'Projected')] for wk in weeks_demand])
                cum_row[(f'Week {w}', 'Deficit')] = sum([total_row[(f'Week {wk}', 'Deficit')] for wk in weeks_demand])
            else:
                cum_row[(f'Week {w}', 'Target')] = ""
                cum_row[(f'Week {w}', 'Actuals')] = ""
                cum_row[(f'Week {w}', 'Projected')] = ""
                cum_row[(f'Week {w}', 'Deficit')] = ""
                
        df_demand.loc[len(df_demand)] = total_row
        df_demand.loc[len(df_demand)] = cum_row
        for col in df_demand.columns: df_demand[col] = df_demand[col].apply(safe_str)
        for w in weeks_demand:
            tgt_col = (f'Week {w}', 'Target')
            for idx in df_demand.index[:-2]: 
                if df_demand.at[idx, ('Client / Company', '')] in ['PRONTO', 'SNABBIT']:
                    df_demand.at[idx, tgt_col] = "100 (Comb)" if w == lw else ""
                    df_demand.at[idx, (f'Week {w}', 'Deficit')] = ""
        df_demand.columns = pd.MultiIndex.from_tuples(df_demand.columns)
        
        def style_demand_table(row):
            styles = [''] * len(row)
            for i, col in enumerate(row.index):
                if isinstance(col, tuple) and len(col) > 1:
                    if col[1] in ['Projected', 'Actuals']:
                        tgt_col = (col[0], 'Target')
                        if tgt_col in row.index:
                            try:
                                t_val, a_val = str(row[tgt_col]).replace(" (Comb)", "").strip(), str(row[col])
                                if t_val != "" and a_val != "":
                                    tgt, act = float(t_val), float(a_val)
                                    if tgt > 0:
                                        if act >= tgt: styles[i] = 'background-color: #0e2a15; color: #00ea7b; font-weight: bold;'
                                        else: styles[i] = 'background-color: #381313; color: #ff6b6b; font-weight: bold;'
                            except: pass
                    elif col[1] == 'Deficit':
                        val = row[col]
                        if val != "":
                            try:
                                if float(str(val).replace(" (Comb)", "").strip()) >= 0: styles[i] = 'color: #00ea7b; font-weight: bold;'
                                else: styles[i] = 'color: #ff6b6b; font-weight: bold;'
                            except: pass
            return styles
        styled_demand = df_demand.style.apply(style_demand_table, axis=1)
        styled_demand = styled_demand.set_properties(**{'text-align': 'center'}).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        st.dataframe(styled_demand, use_container_width=True, height=550, hide_index=True)

    # --- CLIENT x SUPPORT DETAILS ---
    st.markdown("---")
    st.markdown("### 📞 Client x Support Details")
    
    weeks_desc = sorted(weeks_demand, reverse=True)
    support_data = []
    support_clients = sorted([str(c) for c in df_tickets['client_name'].dropna().unique() if str(c).strip() not in ['', 'nan', 'null']])
    
    for client in support_clients:
        row_metrics = {('Client / Company', ''): client.upper()}
        for w in weeks_desc:
            df_tw = df_tickets[(df_tickets['client_name'] == client) & (df_tickets['Week'] == w)] if not df_tickets.empty else pd.DataFrame()
            total_tickets = df_tw['ticket_id'].nunique() if not df_tw.empty else 0
            resolved_tickets = df_tw[df_tw['is_resolved']]['ticket_id'].nunique() if not df_tw.empty else 0
            res_perc = round((resolved_tickets / total_tickets) * 100, 1) if total_tickets > 0 else 0.0
            df_tw_resolved = df_tw[df_tw['is_resolved']] if not df_tw.empty else pd.DataFrame()
            avg_tat = round(df_tw_resolved['rtat_mins'].mean(), 1) if not df_tw_resolved.empty and not df_tw_resolved['rtat_mins'].isna().all() else 0.0
            row_metrics[(f'Week {w}', 'No of Tickets')] = total_tickets
            row_metrics[(f'Week {w}', 'Resolution %')] = f"{res_perc}%" if total_tickets > 0 else ""
            row_metrics[(f'Week {w}', 'Avg Resolution TAT')] = avg_tat if total_tickets > 0 else ""
        support_data.append(row_metrics)
        
    support_data.sort(key=lambda x: x.get((f'Week {lw}', 'No of Tickets'), 0), reverse=True)
    df_support = pd.DataFrame(support_data)
    
    if not df_support.empty:
        total_row = {('Client / Company', ''): 'TOTAL'}
        for w in weeks_desc:
            df_tw_all = df_tickets[df_tickets['Week'] == w] if not df_tickets.empty else pd.DataFrame()
            t_tickets = df_tw_all['ticket_id'].nunique() if not df_tw_all.empty else 0
            r_tickets = df_tw_all[df_tw_all['is_resolved']]['ticket_id'].nunique() if not df_tw_all.empty else 0
            t_res_perc = round((r_tickets / t_tickets) * 100, 1) if t_tickets > 0 else 0.0
            df_tw_all_res = df_tw_all[df_tw_all['is_resolved']] if not df_tw_all.empty else pd.DataFrame()
            t_avg_tat = round(df_tw_all_res['rtat_mins'].mean(), 1) if not df_tw_all_res.empty and not df_tw_all_res['rtat_mins'].isna().all() else 0.0
            total_row[(f'Week {w}', 'No of Tickets')] = t_tickets
            total_row[(f'Week {w}', 'Resolution %')] = f"{t_res_perc}%" if t_tickets > 0 else ""
            total_row[(f'Week {w}', 'Avg Resolution TAT')] = t_avg_tat if t_tickets > 0 else ""
            
        cum_row = {('Client / Company', ''): 'CUMULATIVE'}
        for w in weeks_desc:
            if w == lw:
                df_c_all = df_tickets[df_tickets['Week'].isin(weeks_demand)] if not df_tickets.empty else pd.DataFrame()
                c_tickets = df_c_all['ticket_id'].nunique() if not df_c_all.empty else 0
                c_r_tickets = df_c_all[df_c_all['is_resolved']]['ticket_id'].nunique() if not df_c_all.empty else 0
                c_res_perc = round((c_r_tickets / c_tickets) * 100, 1) if c_tickets > 0 else 0.0
                df_c_all_res = df_c_all[df_c_all['is_resolved']] if not df_c_all.empty else pd.DataFrame()
                c_avg_tat = round(df_c_all_res['rtat_mins'].mean(), 1) if not df_c_all_res.empty and not df_c_all_res['rtat_mins'].isna().all() else 0.0
                cum_row[(f'Week {w}', 'No of Tickets')] = c_tickets
                cum_row[(f'Week {w}', 'Resolution %')] = f"{c_res_perc}%" if c_tickets > 0 else ""
                cum_row[(f'Week {w}', 'Avg Resolution TAT')] = c_avg_tat if c_tickets > 0 else ""
            else:
                cum_row[(f'Week {w}', 'No of Tickets')] = ""
                cum_row[(f'Week {w}', 'Resolution %')] = ""
                cum_row[(f'Week {w}', 'Avg Resolution TAT')] = ""
                
        df_support.loc[len(df_support)] = total_row
        df_support.loc[len(df_support)] = cum_row
        for col in df_support.columns: df_support[col] = df_support[col].apply(safe_str)
        df_support.columns = pd.MultiIndex.from_tuples(df_support.columns)
        
        styled_support = df_support.style.set_properties(**{'text-align': 'center'}).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        st.dataframe(styled_support, use_container_width=True, height=550, hide_index=True)
