# MOCK DATA FOR TC (In production, replace with real API call)
@st.cache_data
def fetch_mock_tc_data():
    today_dt = datetime.date.today()
    yesterday_dt = today_dt - datetime.timedelta(days=1)
    dates = [yesterday_dt - datetime.timedelta(weeks=i) for i in range(12)]
    data = []
    for d in dates:
        week_start = d - datetime.timedelta(days=d.weekday())
        for _ in range(50):
            vl = random.choice(["Delhive", "VMC", "Direct Channel", "New Vendor A", "Fastseek"])
            stat = "New" if vl == "New Vendor A" else "Active"
            
            # Generate base metrics
            active = random.randint(10, 100)
            new_tc = random.randint(0, 20)
            resurrected = random.randint(0, 5)
            churned = random.randint(0, 15)
            
            data.append({
                "Week_start": week_start,
                "vl_name": vl,
                "vl_status": stat,
                "company_name": random.choice(["Blinkit", "Swiggy Food", "Uber", "Amazon"]),
                "region": random.choice(["NCR-UP", "South", "West", "East"]),
                "cohort": random.choice(["Cohort#1", "Cohort#2", "Cohort#3"]),
                "active_tcs": active,
                "churned_tcs": churned,
                "new_tcs": new_tc,
                "resurrected_tcs": resurrected,
                "existing_tcs": active - new_tc - resurrected, # Restored missing column
                "net_new_additions": new_tc - churned          # Mathematically linked
            })
    return pd.DataFrame(data)
