"""
frontend/app.py — Streamlit flood prediction dashboard.

Run with:
    cd d:\\Flood_Prediction_system\\frontend
    streamlit run app.py
"""

import time
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ── Config ─────────────────────────────────────────────────────────────────────
BACKEND = "http://localhost:8000"
AUTO_REFRESH_SECONDS = 60

# ── Curated flood-prone city database ──────────────────────────────────────────
CITIES = [
    # ── Asia ──
    {"name": "Chennai, India",        "lat": 13.0827, "lon": 80.2707, "region": "🌏 Asia"},
    {"name": "Mumbai, India",          "lat": 19.0760, "lon": 72.8777, "region": "🌏 Asia"},
    {"name": "Kolkata, India",         "lat": 22.5726, "lon": 88.3639, "region": "🌏 Asia"},
    {"name": "Dhaka, Bangladesh",      "lat": 23.8103, "lon": 90.4125, "region": "🌏 Asia"},
    {"name": "Bangkok, Thailand",      "lat": 13.7563, "lon": 100.5018,"region": "🌏 Asia"},
    {"name": "Jakarta, Indonesia",     "lat": -6.2088, "lon": 106.8456,"region": "🌏 Asia"},
    {"name": "Manila, Philippines",    "lat": 14.5995, "lon": 120.9842,"region": "🌏 Asia"},
    {"name": "Ho Chi Minh City, VN",   "lat": 10.8231, "lon": 106.6297,"region": "🌏 Asia"},
    {"name": "Yangon, Myanmar",        "lat": 16.8661, "lon": 96.1951, "region": "🌏 Asia"},
    {"name": "Karachi, Pakistan",      "lat": 24.8607, "lon": 67.0011, "region": "🌏 Asia"},
    {"name": "Tokyo, Japan",           "lat": 35.6762, "lon": 139.6503,"region": "🌏 Asia"},
    {"name": "Guangzhou, China",       "lat": 23.1291, "lon": 113.2644,"region": "🌏 Asia"},
    {"name": "Wuhan, China",           "lat": 30.5928, "lon": 114.3055,"region": "🌏 Asia"},
    # ── Europe ──
    {"name": "London, UK",             "lat": 51.5074, "lon": -0.1278, "region": "🌍 Europe"},
    {"name": "Hamburg, Germany",       "lat": 53.5753, "lon": 10.0153, "region": "🌍 Europe"},
    {"name": "Venice, Italy",          "lat": 45.4408, "lon": 12.3155, "region": "🌍 Europe"},
    {"name": "Rotterdam, Netherlands", "lat": 51.9244, "lon": 4.4777,  "region": "🌍 Europe"},
    {"name": "Cologne, Germany",       "lat": 50.9333, "lon": 6.9500,  "region": "🌍 Europe"},
    {"name": "Prague, Czech Republic", "lat": 50.0755, "lon": 14.4378, "region": "🌍 Europe"},
    {"name": "Paris, France",          "lat": 48.8566, "lon": 2.3522,  "region": "🌍 Europe"},
    # ── Africa ──
    {"name": "Lagos, Nigeria",         "lat": 6.5244,  "lon": 3.3792,  "region": "🌍 Africa"},
    {"name": "Khartoum, Sudan",        "lat": 15.5007, "lon": 32.5599, "region": "🌍 Africa"},
    {"name": "Accra, Ghana",           "lat": 5.6037,  "lon": -0.1870, "region": "🌍 Africa"},
    {"name": "Nairobi, Kenya",         "lat": -1.2921, "lon": 36.8219, "region": "🌍 Africa"},
    {"name": "Mozambique City",        "lat": -15.1167,"lon": 40.7333, "region": "🌍 Africa"},
    # ── Americas ──
    {"name": "New Orleans, USA",       "lat": 29.9511, "lon": -90.0715,"region": "🌎 Americas"},
    {"name": "Houston, USA",           "lat": 29.7604, "lon": -95.3698,"region": "🌎 Americas"},
    {"name": "Miami, USA",             "lat": 25.7617, "lon": -80.1918,"region": "🌎 Americas"},
    {"name": "São Paulo, Brazil",      "lat": -23.5505,"lon": -46.6333,"region": "🌎 Americas"},
    {"name": "Buenos Aires, Argentina","lat": -34.6037,"lon": -58.3816,"region": "🌎 Americas"},
    {"name": "Bogotá, Colombia",       "lat": 4.7110,  "lon": -74.0721,"region": "🌎 Americas"},
    {"name": "Guayaquil, Ecuador",     "lat": -2.1962, "lon": -79.8862,"region": "🌎 Americas"},
    # ── Oceania ──
    {"name": "Brisbane, Australia",    "lat": -27.4705,"lon": 153.0260,"region": "🌏 Oceania"},
    {"name": "Townsville, Australia",  "lat": -19.2590,"lon": 146.8169,"region": "🌏 Oceania"},
]

CITY_NAMES = [c["name"] for c in CITIES]
CITY_MAP   = {c["name"]: c for c in CITIES}

st.set_page_config(
    page_title="🌊 Flood Prediction Platform",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Background */
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%); }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #0a1220 100%);
        border-right: 1px solid #1e3a5f;
    }

    /* Cards */
    .risk-card-high {
        background: linear-gradient(135deg, #3d0a0a 0%, #6b1010 100%);
        border: 2px solid #ff4444;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 0 30px rgba(255,68,68,0.4);
        animation: pulse-red 2s infinite;
    }
    .risk-card-low {
        background: linear-gradient(135deg, #0a3d1a 0%, #0e5c28 100%);
        border: 2px solid #00e676;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0,230,118,0.3);
    }
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 30px rgba(255,68,68,0.4); }
        50%       { box-shadow: 0 0 50px rgba(255,68,68,0.8); }
    }

    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }

    .metric-value { font-size: 2rem; font-weight: 700; color: #4fc3f7; }
    .metric-label { font-size: 0.78rem; color: #8899aa; text-transform: uppercase; letter-spacing: 1px; }

    .section-title {
        font-size: 1.1rem; font-weight: 600;
        color: #4fc3f7;
        border-left: 4px solid #4fc3f7;
        padding-left: 12px;
        margin-bottom: 16px;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* DataTable */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def api_predict(lat: float = None, lon: float = None, location: str = None):
    try:
        if lat and lon:
            url = f"{BACKEND}/predict/{lat}/{lon}?location={requests.utils.quote(location or 'Custom')}"
        else:
            url = f"{BACKEND}/predict"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except requests.ConnectionError:
        return None, "⛔ Cannot reach backend. Is the FastAPI server running on port 8000?"
    except Exception as e:
        return None, f"⛔ API error: {e}"


def api_history(limit=50):
    try:
        r = requests.get(f"{BACKEND}/history?limit={limit}", timeout=10)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return [], str(e)


def gauge_chart(value: float, title: str, max_val: float = 100,
                unit: str = "", color: str = "#4fc3f7"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": "#cdd9e5", "size": 13}},
        number={"suffix": unit, "font": {"color": color, "size": 22}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#445566"},
            "bar":  {"color": color},
            "bgcolor": "rgba(255,255,255,0.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,     max_val * 0.4], "color": "rgba(0,200,100,0.15)"},
                {"range": [max_val*0.4, max_val*0.7], "color": "rgba(255,200,0,0.15)"},
                {"range": [max_val*0.7, max_val],     "color": "rgba(255,60,60,0.15)"},
            ],
        },
    ))
    fig.update_layout(
        height=200, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cdd9e5",
    )
    return fig


def bar_chart(weather: dict):
    categories = ["Rainfall (mm)", "River Level (m)", "Humidity (%)",
                  "Temperature (°C)", "Wind Speed (km/h)"]
    values = [
        weather["rainfall_mm"],
        weather["river_level_m"],
        weather["humidity_pct"],
        weather["temperature_c"],
        weather["wind_speed_kmh"],
    ]
    colors = ["#4fc3f7", "#29b6f6", "#0288d1", "#f48fb1", "#81c784"]

    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker_color=colors,
        text=[f"{v:.1f}" for v in values],
        textposition="outside",
        textfont={"color": "#cdd9e5"},
    ))
    fig.update_layout(
        title={"text": "Environmental Parameters", "font": {"color": "#4fc3f7", "size": 14}},
        height=320,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"tickcolor": "#445566", "gridcolor": "rgba(255,255,255,0.05)"},
        yaxis={"tickcolor": "#445566", "gridcolor": "rgba(255,255,255,0.05)"},
        font_color="#cdd9e5",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def risk_history_chart(records: list):
    if not records:
        return None
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df["risk_num"] = df["risk_level"].map({"HIGH": 1, "LOW": 0})

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["risk_probability"],
        mode="lines+markers",
        name="Risk Probability",
        line={"color": "#4fc3f7", "width": 2},
        marker={"color": df["risk_level"].map({"HIGH": "#ff4444", "LOW": "#00e676"}),
                "size": 8},
        hovertemplate="<b>%{x}</b><br>Risk: %{y:.2%}<extra></extra>",
    ))
    fig.add_hline(y=0.5, line_dash="dash", line_color="#ff9800",
                  annotation_text="Threshold (50%)",
                  annotation_font_color="#ff9800")
    fig.update_layout(
        title={"text": "Prediction History — Risk Probability Over Time",
               "font": {"color": "#4fc3f7", "size": 14}},
        height=300,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"gridcolor": "rgba(255,255,255,0.05)"},
        yaxis={"gridcolor": "rgba(255,255,255,0.05)", "tickformat": ".0%",
               "range": [0, 1]},
        font_color="#cdd9e5",
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
    )
    return fig


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌊 Flood Prediction")
    st.markdown("---")

    # ── Location selector ────────────────────────────────────────────────────
    st.markdown("### 📍 Location")

    loc_mode = st.radio(
        "Select mode",
        ["🔍 Search City", "🗺️ Custom Coordinates"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if loc_mode == "🔍 Search City":
        # Group cities by region for the expander labels
        regions = sorted({c["region"] for c in CITIES})

        # Searchable selectbox — Streamlit's selectbox supports typing to filter
        selected_city = st.selectbox(
            "Search or select a city",
            options=CITY_NAMES,
            index=0,
            help="Type to search — e.g. 'Mumbai', 'Bangkok', 'New Orleans'",
        )
        city_data = CITY_MAP[selected_city]
        lat_in    = city_data["lat"]
        lon_in    = city_data["lon"]
        loc_name  = city_data["name"]

        # Region quick-filters
        with st.expander("🗂️ Browse by region", expanded=False):
            for region in regions:
                st.markdown(
                    f"<span style='color:#4fc3f7; font-weight:600'>{region}</span>",
                    unsafe_allow_html=True,
                )
                region_cities = [c["name"] for c in CITIES if c["region"] == region]
                for city in region_cities:
                    if st.button(city, key=f"city_{city}", use_container_width=True):
                        st.session_state["selected_city_override"] = city
                        st.rerun()

        # Apply override if a browse button was clicked
        if "selected_city_override" in st.session_state:
            override = st.session_state.pop("selected_city_override")
            city_data = CITY_MAP.get(override, city_data)
            lat_in    = city_data["lat"]
            lon_in    = city_data["lon"]
            loc_name  = city_data["name"]

        # Show coords info card
        st.markdown(
            f"<div style='background:rgba(79,195,247,0.08); border:1px solid rgba(79,195,247,0.2);"
            f"border-radius:8px; padding:10px; margin-top:8px; font-size:0.8rem;'>"
            f"<b style='color:#4fc3f7'>{loc_name}</b><br>"
            f"<span style='color:#8899aa'>Lat: {lat_in:.4f} &nbsp;|&nbsp; Lon: {lon_in:.4f}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    else:  # Custom Coordinates
        col1, col2 = st.columns(2)
        with col1:
            lat_in = st.number_input("Latitude",  value=13.0827, format="%.4f",
                                     min_value=-90.0, max_value=90.0)
        with col2:
            lon_in = st.number_input("Longitude", value=80.2707, format="%.4f",
                                     min_value=-180.0, max_value=180.0)
        loc_name = st.text_input("Location name", value="Custom Location",
                                 placeholder="e.g. My City")
        st.caption("💡 You can find coordinates on [Google Maps](https://maps.google.com) by right-clicking any location.")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    history_limit = st.slider("History records to show", 10, 200, 50)

    st.markdown("---")
    refresh_btn = st.button("🔄 Refresh Now", use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Clear All History", use_container_width=True):
        try:
            r = requests.delete(f"{BACKEND}/history", timeout=5)
            if r.status_code == 200:
                st.success("History cleared.")
            else:
                st.error("Failed to clear history.")
        except Exception:
            st.error("Backend unreachable.")

    st.markdown("---")
    st.caption("Powered by **Open-Meteo API** + **Random Forest ML**")
    st.caption("Backend: FastAPI · DB: SQLite · Model: scikit-learn")


# ── Session state for last fetch ────────────────────────────────────────────────
if "prediction" not in st.session_state:
    st.session_state.prediction = None
if "error" not in st.session_state:
    st.session_state.error = None
if "last_fetch" not in st.session_state:
    st.session_state.last_fetch = 0
if "last_location" not in st.session_state:
    st.session_state.last_location = ""

# Trigger fetch if: manual refresh, location changed, or auto-refresh interval
now = time.time()
location_changed = (loc_name != st.session_state.last_location)
auto_due         = (now - st.session_state.last_fetch) > AUTO_REFRESH_SECONDS

if refresh_btn or location_changed or auto_due:
    spinner_msg = (
        f"📡 Fetching weather for **{loc_name}**..."
        if location_changed else "🔄 Refreshing weather data..."
    )
    with st.spinner(spinner_msg):
        data, err = api_predict(lat_in, lon_in, loc_name)
    st.session_state.prediction    = data
    st.session_state.error         = err
    st.session_state.last_fetch    = now
    st.session_state.last_location = loc_name


# ── Main layout ────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#4fc3f7; font-size:2rem; font-weight:800; margin-bottom:4px;'>"
    "🌊 Flood Prediction & Management Platform</h1>"
    "<p style='color:#8899aa; margin-top:0;'>AI-powered real-time flood risk monitoring using "
    "machine learning and live weather data</p>",
    unsafe_allow_html=True,
)

if st.session_state.error:
    st.error(st.session_state.error)
    st.info("💡 Make sure the backend is running:  \n"
            "`cd d:\\Flood_Prediction_system`  \n"
            "`uvicorn backend.main:app --reload --port 8000`")
    st.stop()

pred = st.session_state.prediction
if pred is None:
    st.info("⌛ Loading first prediction… please wait.")
    st.stop()

# ── Top row: Risk + quick metrics ─────────────────────────────────────────────
left, mid, right = st.columns([1.2, 2, 1])

with left:
    risk  = pred["risk_level"]
    prob  = pred["risk_probability"]
    emoji = "🔴" if risk == "HIGH" else "🟢"
    card_class = "risk-card-high" if risk == "HIGH" else "risk-card-low"
    color = "#ff4444" if risk == "HIGH" else "#00e676"

    st.markdown(f"""
    <div class="{card_class}">
        <div style="font-size:3rem">{emoji}</div>
        <div style="font-size:2.2rem; font-weight:800; color:{color}; margin:8px 0">{risk}</div>
        <div style="font-size:1.1rem; color:#ccddee; font-weight:600">FLOOD RISK</div>
        <div style="font-size:0.9rem; color:#99aabb; margin-top:8px">Confidence: {prob:.1%}</div>
        <div style="font-size:0.8rem; color:#99aabb">{pred['location']}</div>
    </div>
    """, unsafe_allow_html=True)

with mid:
    st.markdown('<div class="section-title">🌡️ Current Weather Conditions</div>',
                unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, "🌧️", f"{pred['rainfall_mm']:.1f}", "mm", "Rainfall"),
        (c2, "🌊", f"{pred['river_level_m']:.2f}", "m",  "River Level"),
        (c3, "💧", f"{pred['humidity_pct']:.0f}",  "%",  "Humidity"),
        (c4, "🌡️", f"{pred['temperature_c']:.1f}", "°C", "Temp"),
        (c5, "💨", f"{pred['wind_speed_kmh']:.1f}", "km/h", "Wind"),
    ]
    for col, icon, val, unit, label in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.5rem">{icon}</div>
                <div class="metric-value">{val}<span style="font-size:0.9rem; color:#8899aa">{unit}</span></div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

with right:
    ts = datetime.fromisoformat(pred["timestamp"].replace("Z", "+00:00"))
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                border-radius:12px; padding:16px; height:100%;">
        <div style="color:#8899aa; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px">
            Sky Condition</div>
        <div style="font-size:1.1rem; color:#cdd9e5; font-weight:600; margin:4px 0">
            {pred['weather_desc']}</div>
        <hr style="border-color:rgba(255,255,255,0.08); margin:8px 0">
        <div style="color:#8899aa; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px">
            Last Updated</div>
        <div style="color:#4fc3f7; font-size:0.85rem; margin:4px 0">
            {ts.strftime('%Y-%m-%d')}</div>
        <div style="color:#4fc3f7; font-size:0.85rem">{ts.strftime('%H:%M:%S UTC')}</div>
        <hr style="border-color:rgba(255,255,255,0.08); margin:8px 0">
        <div style="color:#8899aa; font-size:0.75rem;">Auto-refresh every {AUTO_REFRESH_SECONDS}s</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Alert message ──────────────────────────────────────────────────────────────
if risk == "HIGH":
    st.error(f"⚠️  **HIGH FLOOD RISK ALERT**  |  {pred['message']}")
else:
    st.success(f"✅  **LOW FLOOD RISK**  |  {pred['message']}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row ─────────────────────────────────────────────────────────────────
col_bar, col_gauge = st.columns([1.6, 1])

with col_bar:
    st.plotly_chart(bar_chart(pred), use_container_width=True)

with col_gauge:
    sub1, sub2 = st.columns(2)
    with sub1:
        st.plotly_chart(
            gauge_chart(pred["humidity_pct"], "Humidity", 100, "%", "#29b6f6"),
            use_container_width=True,
        )
    with sub2:
        st.plotly_chart(
            gauge_chart(pred["rainfall_mm"], "Rainfall", 150, "mm", "#4fc3f7"),
            use_container_width=True,
        )
    st.plotly_chart(
        gauge_chart(pred["risk_probability"] * 100, "Flood Risk %", 100, "%",
                    "#ff4444" if risk == "HIGH" else "#00e676"),
        use_container_width=True,
    )

# ── Prediction History ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">📜 Prediction History</div>',
            unsafe_allow_html=True)

history, hist_err = api_history(history_limit)

if hist_err:
    st.warning(f"Could not load history: {hist_err}")
elif not history:
    st.info("No prediction history yet — run a prediction first.")
else:
    fig_hist = risk_history_chart(history)
    if fig_hist:
        st.plotly_chart(fig_hist, use_container_width=True)

    df_hist = pd.DataFrame(history)
    df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    df_hist["risk_probability"] = (df_hist["risk_probability"] * 100).round(1).astype(str) + "%"
    df_hist["risk_level"] = df_hist["risk_level"].apply(
        lambda x: f"🔴 {x}" if x == "HIGH" else f"🟢 {x}"
    )
    display_cols = {
        "timestamp": "Time (UTC)", "location": "Location",
        "rainfall_mm": "Rainfall (mm)", "river_level_m": "River Level (m)",
        "humidity_pct": "Humidity (%)", "temperature_c": "Temp (°C)",
        "wind_speed_kmh": "Wind (km/h)", "risk_level": "Risk",
        "risk_probability": "Confidence",
    }
    st.dataframe(
        df_hist.rename(columns=display_cols)[list(display_cols.values())],
        use_container_width=True,
        hide_index=True,
    )

    high_count = sum(1 for r in history if r["risk_level"] == "HIGH")
    low_count  = len(history) - high_count
    h1, h2, h3 = st.columns(3)
    h1.metric("Total Predictions",  len(history))
    h2.metric("🔴 HIGH Risk Events", high_count)
    h3.metric("🟢 LOW Risk Events",  low_count)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#445566; font-size:0.8rem;'>"
    "🌊 Flood Prediction &amp; Management Platform &nbsp;|&nbsp; "
    "ML: Random Forest &nbsp;|&nbsp; Weather: Open-Meteo API &nbsp;|&nbsp; "
    "DB: SQLite &nbsp;|&nbsp; Backend: FastAPI"
    "</div>",
    unsafe_allow_html=True,
)

# ── Auto-refresh (every 60 s) ────────────────────────────────────────────────
# Uses streamlit-autorefresh to avoid blocking the event loop
count = st_autorefresh(interval=AUTO_REFRESH_SECONDS * 1000, key="flood_autorefresh")

# Show a subtle refresh counter in footer
st.markdown(
    f"<div style='text-align:center; color:#2a3a4a; font-size:0.72rem; margin-top:4px;'>"
    f"Auto-refresh #{count} &nbsp;·&nbsp; every {AUTO_REFRESH_SECONDS}s"
    "</div>",
    unsafe_allow_html=True,
)
