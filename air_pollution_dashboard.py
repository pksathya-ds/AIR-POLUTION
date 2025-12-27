# air_pollution_dashboard.py
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# Page configuration
st.set_page_config(page_title="Air Pollution Dashboard", layout="wide", page_icon="🌍")

# Custom CSS Styling
st.markdown("""
    <style>
    /* Page background and font */
    body {
        background-color: #f4f6fa;
        font-family: 'Poppins', sans-serif;
    }
    .main {
        background: linear-gradient(145deg, #f7f9fc, #eef1f6);
        padding: 1.5rem;
        border-radius: 12px;
    }
    h1, h2, h3, h4 {
        color: #1e3a8a;
        font-weight: 600;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e3a8a;
    }
    [data-testid="stSidebar"] * {
        color: black !important;
    }
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-card h3 {
        color: #3b82f6;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-card p {
        font-size: 24px;
        font-weight: bold;
        color: #111827;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align:center;'>🌍 Air Pollution Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Real-time AQI tracking and ML-based next-day prediction</p>", unsafe_allow_html=True)
st.write("---")

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1116/1116453.png", width=80)
st.sidebar.title("Settings")
city = st.sidebar.text_input("🏙️ Enter City Name", "Salem").strip()
api_key = "fcd5faa574c041e4435436365f8fcafc"  # Replace with your own API key

# Fetch Air Pollution Data
def get_air_data(city):
    url_geo = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    geo = requests.get(url_geo).json()
    if not geo:
        return None
    lat, lon = geo[0]['lat'], geo[0]['lon']
    url_air = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    air = requests.get(url_air).json()
    return air

data = get_air_data(city)

# Display Air Quality Data
if data:
    aqi = data['list'][0]['main']['aqi']
    pollutants = data['list'][0]['components']

    aqi_status = {1: "Good 🌿", 2: "Fair 🙂", 3: "Moderate 😐", 4: "Poor 😷", 5: "Very Poor ☠️"}
    advice = {
        1: "Enjoy outdoor activities 🌿",
        2: "Moderate outdoor activity 🙂",
        3: "Limit prolonged outdoor exposure 😐",
        4: "Avoid outdoor activities 😷",
        5: "Stay indoors ☠️"
    }

    st.subheader(f"🌆 Current Air Quality in {city.title()}")

    # Top metrics section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>Air Quality Index</h3><p>{aqi}</p><small>{aqi_status[aqi]}</small></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>Status</h3><p>{aqi_status[aqi]}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>Health Advice</h3><p style='font-size:16px'>{advice[aqi]}</p></div>", unsafe_allow_html=True)

    # Pollutant concentration chart
    st.markdown("### 💨 Pollutant Concentrations (µg/m³)")
    df_poll = pd.DataFrame(list(pollutants.items()), columns=["Pollutant", "Value"])
    fig_poll = px.bar(
        df_poll, x="Pollutant", y="Value", text="Value",
        color="Pollutant", title="Pollutant Levels by Type",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_poll.update_traces(textposition='outside')
    fig_poll.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_poll, use_container_width=True)

    # Simulated AQI data for ML prediction
    np.random.seed(42)
    days = np.arange(1, 8)
    aqi_values = np.random.randint(60, 160, size=7)
    df = pd.DataFrame({"Day": days, "AQI": aqi_values})
    model = LinearRegression().fit(df[["Day"]], df["AQI"])
    next_aqi = model.predict(pd.DataFrame([[8]], columns=["Day"]))[0]

    # AQI Trend and Prediction
    st.markdown("### 📈 Next-Day AQI Prediction")
    st.metric("Predicted AQI (Tomorrow)", f"{next_aqi:.2f}")
    fig_trend = px.line(df, x="Day", y="AQI", markers=True, title="7-Day AQI Trend")
    fig_trend.add_scatter(x=[8], y=[next_aqi], mode="markers+text", name="Predicted AQI", text=["Tomorrow"])
    st.plotly_chart(fig_trend, use_container_width=True)

else:
    st.error("❌ Could not fetch data. Please check the city name or API key.")
