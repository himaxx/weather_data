import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import StringIO

# Custom CSS for styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .stHeader {
        color: #2c3e50;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# App Title
st.header("🌦️ AgriWeather AI Dashboard")
st.subheader("Your Personal Weather Assistant for Farming")
st.markdown("---")

# Sidebar Controls
st.sidebar.header("Configuration")
lat = st.sidebar.text_input("Latitude", "52.52")
lon = st.sidebar.text_input("Longitude", "13.41")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")
selected_vars = st.sidebar.multiselect(
    "Select Variables",
    options=["temperature_2m", "relative_humidity_2m", 
             "precipitation", "soil_moisture_0_to_1cm"],
    default=["temperature_2m", "precipitation"]
)

# Fetch Data
if st.sidebar.button("Fetch Weather Data"):
    with st.spinner("Fetching weather data..."):
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": ",".join(selected_vars),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "temperature_unit": "celsius",
                "precipitation_unit": "mm"
            }
            
            response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
            data = response.json()
            
            if "error" in data:
                st.error(f"API Error: {data['reason']}")
            else:
                # Create DataFrame
                df = pd.DataFrame(data["hourly"])
                df["time"] = pd.to_datetime(df["time"])
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Avg Temperature", f"{df['temperature_2m'].mean():.1f}°C", "2°C ↑")
                with col2:
                    st.metric("Total Rainfall", f"{df['precipitation'].sum()} mm", "10% ↑")
                with col3:
                    st.metric("Soil Moisture", "0.25 m³/m³", "Optimal")
                
                # Charts
                st.subheader("🌡️ Temperature Trend")
                fig = px.line(df, x="time", y="temperature_2m", title="Hourly Temperature")
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("🌧️ Precipitation Trend")
                fig = px.bar(df, x="time", y="precipitation", title="Hourly Precipitation")
                st.plotly_chart(fig, use_container_width=True)
                
                # Map
                st.subheader("📍 Location")
                st.map(pd.DataFrame({"lat": [float(lat)], "lon": [float(lon)]}))
                
                # Raw Data Section
                st.subheader("📊 Raw Data")
                with st.expander("View Raw Data"):
                    st.dataframe(df, height=300)
                
                # Download Options
                st.subheader("📥 Download Data")
                col1, col2, col3 = st.columns(3)
                
                # JSON Download
                json_data = df.to_json(orient="records")
                col1.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="weather_data.json",
                    mime="application/json",
                    help="Download raw data in JSON format"
                )
                
                # CSV Download
                csv_data = df.to_csv(index=False)
                col2.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="weather_data.csv",
                    mime="text/csv",
                    help="Download raw data in CSV format"
                )
                
                # Excel Download
                excel_data = df.to_excel("weather_data.xlsx", index=False)
                with open("weather_data.xlsx", "rb") as file:
                    col3.download_button(
                        label="Download Excel",
                        data=file,
                        file_name="weather_data.xlsx",
                        mime="application/vnd.ms-excel",
                        help="Download raw data in Excel format"
                    )
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
else:
    st.info("Configure parameters in the sidebar and click 'Fetch Weather Data'")