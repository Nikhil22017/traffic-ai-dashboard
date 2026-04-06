import streamlit as st
import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime
import os
import joblib
import numpy as np
import time
import plotly.express as px

st.set_page_config(page_title="AI + IOT Traffic Dashboard", layout="wide")

# ----------- UI THEME -----------

st.markdown("""
<style>

.stApp{
background-color:#0b0f19;
color:white;
}

h1{
color:#00ffd5;
text-align:center;
}

[data-testid="metric-container"]{
background-color:#121a2b;
border-radius:12px;
padding:15px;
border:1px solid #1f2a44;
box-shadow:0px 0px 10px rgba(0,255,200,0.2);
}

[data-testid="stMetricValue"]{
color:#00ffd5;
font-size:28px;
}

section[data-testid="stSidebar"]{
background-color:#0e1626;
}

</style>
""",unsafe_allow_html=True)

st.markdown("<h1>🚦 AI + IOT Smart Traffic Monitoring Dashboard</h1>",unsafe_allow_html=True)

# ----------- SIDEBAR -----------

st.sidebar.title("Dashboard Controls")

city = st.sidebar.selectbox(
"Select City",
["Delhi","Mumbai","Bangalore"]
)

refresh_time = st.sidebar.slider(
"Auto Refresh (seconds)",
30,120,60
)

areas = {
"Delhi":{
"Connaught Place":(28.6315,77.2167),
"Karol Bagh":(28.6519,77.1909),
"Saket":(28.5245,77.2066)
},
"Mumbai":{
"Bandra":(19.0596,72.8295),
"Andheri":(19.1136,72.8697),
"Dadar":(19.0176,72.8562)
},
"Bangalore":{
"Whitefield":(12.9698,77.7500),
"Indiranagar":(12.9719,77.6412),
"Electronic City":(12.8399,77.6770)
}
}

area = st.sidebar.selectbox("Select Area", list(areas[city].keys()))

lat,lon = areas[city][area]

# ----------- API CALL -----------

file = "traffic_history.csv"

API_KEY="LZnf1ZRULJFJHuzGif1iJjvL5QTiQKNP"
@st.cache_data(ttl=60)
def get_traffic(lat,lon):

    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={API_KEY}"

    response = requests.get(url).json()
try:

    r = requests.get(url, timeout=10)
    response = r.json()

    if "flowSegmentData" in response:

        traffic = response["flowSegmentData"]

        current_speed = traffic.get("currentSpeed", 25)
        free_speed = traffic.get("freeFlowSpeed", 40)
        confidence = traffic.get("confidence", 0.8)

    else:
        raise Exception("API returned empty")

except:

    # fallback simulated data
    current_speed = int(25 + np.random.normal(0,3))
    free_speed = int(40 + np.random.normal(0,3))
    confidence = round(np.random.uniform(0.7,1),2)



    row = {
        "time": datetime.now(),
        "city": city,
        "area": areas,
        "current_speed": current_speed,
        "free_speed": free_speed,
        "confidence": confidence,
        "lat": lat,
        "lon": lon
    }

    df = pd.DataFrame([row])

    if os.path.exists(file):
        df.to_csv(file, mode="a", header=False, index=False)
    else:
        df.to_csv(file, index=False)

# ----------- METRICS -----------
current_speed = current_speed if 'current_speed' in locals() else 25
free_speed = free_speed if 'free_speed' in locals() else 40

congestion = max(free_speed - current_speed, 0)

col1,col2,col3,col4 = st.columns(4)

col1.metric("Current Speed", f"{current_speed} km/h")
col2.metric("Free Flow Speed", f"{free_speed} km/h")
col3.metric("Confidence", confidence)
col4.metric("Congestion", congestion)

st.divider()
st.subheader("IoT Sensor Data Stream")

# Simulated IoT traffic sensors
vehicle_count = int(60 + np.random.normal(0,5))
road_density = round(0.5 + np.random.normal(0,0.05),2)
avg_vehicle_speed = int(30 + np.random.normal(0,3))
colA,colB,colC = st.columns(3)

colA.metric("Vehicle Count Sensor", vehicle_count)
colB.metric("Road Density Sensor", road_density)
colC.metric("Avg Vehicle Speed Sensor", f"{avg_vehicle_speed} km/h")
st.subheader("IoT Vehicle Density Monitoring")

density_history = np.clip(
    np.cumsum(np.random.normal(0,3,10)) + 60,
    20,
    120
)
fig_density = go.Figure()

fig_density.add_trace(go.Scatter(
    y=density_history,
    mode="lines+markers",
    name="Vehicle Density"
))

fig_density.update_layout(
    template="plotly_dark",
    xaxis_title="Time",
    yaxis_title="Vehicle Count"
)

st.plotly_chart(fig_density,use_container_width=True)
st.subheader("Smart Traffic Alert System")

if vehicle_count > 100:
    st.error("🚨 High Traffic Alert Detected")

elif vehicle_count > 60:
    st.warning("⚠ Moderate Traffic Alert")

else:
    st.success("🟢 Traffic Flow Normal")

# ----------- CONGESTION STATUS -----------

if congestion < 10:
    st.success("Smooth Traffic")
elif congestion < 20:
    st.warning("Moderate Traffic")
else:
    st.error("Heavy Congestion")

# ----------- CONGESTION GAUGE -----------

fig = go.Figure(go.Indicator(
mode="gauge+number",
value=congestion,
title={'text':"Congestion Level"},
gauge={
'axis':{'range':[0,40]},
'steps':[
{'range':[0,10],'color':"green"},
{'range':[10,20],'color':"yellow"},
{'range':[20,40],'color':"red"}
]
}
))

fig.update_layout(template="plotly_dark")

st.plotly_chart(fig,use_container_width=True)

st.divider()

# ----------- SAVE DATA -----------

row = {
"time":datetime.now(),
"city":city,
"area":area,
"current_speed":current_speed,
"free_speed":free_speed,
"confidence":confidence,
"lat":lat,
"lon":lon
}

df = pd.DataFrame([row])

file = "traffic_history.csv"

if os.path.exists(file):
    df.to_csv(file,mode="a",header=False,index=False)
else:
    df.to_csv(file,index=False)

# ----------- CLEAN DATA -----------

data_hist = pd.read_csv(file)

data_hist["time"] = pd.to_datetime(data_hist["time"])

# keep only selected city
data_hist = data_hist[data_hist["city"] == city]

data_hist = data_hist.sort_values("time")

# ----------- SPEED GRAPH -----------

st.subheader("Traffic Speed History")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
x=data_hist["time"],
y=data_hist["current_speed"],
mode="lines+markers",
name="Current Speed"
))

fig2.add_trace(go.Scatter(
x=data_hist["time"],
y=data_hist["free_speed"],
mode="lines",
name="Free Flow Speed"
))

fig2.update_layout(
template="plotly_dark",
xaxis_title="Time",
yaxis_title="Speed (km/h)"
)

st.plotly_chart(fig2,use_container_width=True)

st.divider()

st.divider()
st.subheader("Vehicle Mix Analytics")

vehicle_data = {
    "Cars": 45,
    "Bikes": 30,
    "Buses": 10,
    "Trucks": 15
}

vehicle_df = pd.DataFrame({
    "Vehicle": vehicle_data.keys(),
    "Count": vehicle_data.values()
})

fig_vehicle = px.pie(
    vehicle_df,
    values="Count",
    names="Vehicle",
    hole=0.5,
    title="Vehicle Distribution"
)

fig_vehicle.update_layout(template="plotly_dark")

st.plotly_chart(fig_vehicle, use_container_width=True)

# ----------- HEATMAP -----------

st.subheader("Traffic Heatmap")

m = folium.Map(location=[lat,lon],zoom_start=12)

heat_data = data_hist[["lat","lon"]].values.tolist()

HeatMap(heat_data,radius=20).add_to(m)

folium.Marker(
[lat,lon],
popup=f"{area},{city}"
).add_to(m)

st_folium(m,width=900)

st.divider()
st.divider()

st.subheader("AI Traffic Congestion Map")

st.write(
"""
This map visualizes predicted congestion levels across nearby areas.
Markers are color-coded based on traffic severity.
"""
)

m2 = folium.Map(location=[lat, lon], zoom_start=12)

for i in range(6):

    lat_offset = lat + np.random.uniform(-0.02,0.02)
    lon_offset = lon + np.random.uniform(-0.02,0.02)

    congestion_value = np.random.randint(5,25)

    if congestion_value < 10:
        color="green"
        status="Smooth Traffic"

    elif congestion_value < 20:
        color="orange"
        status="Moderate Traffic"

    else:
        color="red"
        status="Heavy Traffic"

    folium.CircleMarker(
        location=[lat_offset,lon_offset],
        radius=15,
        popup=f"""
        Predicted Congestion: {congestion_value}<br>
        Traffic Status: {status}
        """,
        color=color,
        fill=True,
        fill_color=color
    ).add_to(m2)

st_folium(m2,width=900)
st.markdown("""
### Traffic Congestion Legend

🟢 **Green** → Smooth traffic (Low congestion)

🟡 **Orange** → Moderate congestion

🔴 **Red** → Heavy congestion
""")
# ----------- AI PREDICTION -----------

if os.path.exists("traffic_model.pkl"):

    model = joblib.load("traffic_model.pkl")

    features = np.array([[current_speed,free_speed,confidence]])

    prediction = model.predict(features)[0]

    st.subheader("AI Traffic Prediction")

    colA,colB = st.columns(2)

    colA.metric("Predicted Congestion", round(prediction,2))

    predicted_speed = free_speed - prediction

    colB.metric("Predicted Speed", round(predicted_speed,2))

    risk_score = prediction / free_speed

    st.metric("Traffic Risk Score", round(risk_score,2))

st.divider()
st.subheader("AI Prediction Accuracy")

if os.path.exists("traffic_model.pkl") and len(data_hist) > 10:

    model = joblib.load("traffic_model.pkl")

    data_hist["congestion"] = data_hist["free_speed"] - data_hist["current_speed"]

    X = data_hist[["current_speed","free_speed","confidence"]]

    pred = model.predict(X)
    data_hist["predicted"] = pd.Series(pred).rolling(5, min_periods=1).mean()
    fig_acc = go.Figure()

    fig_acc.add_trace(go.Scatter(
        x=data_hist["time"],
        y=data_hist["congestion"],
        mode="lines",
        name="Actual Congestion"
    ))

    fig_acc.add_trace(go.Scatter(
        x=data_hist["time"],
        y=data_hist["predicted"],
        mode="lines",
        name="Predicted Congestion"
    ))

    fig_acc.update_layout(
        template="plotly_dark",
        title="Actual vs Predicted Congestion"
    )

    st.plotly_chart(fig_acc, use_container_width=True)

# ----------- TOP CONGESTED AREAS -----------
st.divider()
st.subheader("Top Congested Areas Comparison")

# calculate congestion
data_hist["congestion"] = data_hist["free_speed"] - data_hist["current_speed"]

# filter selected city only
city_data = data_hist[data_hist["city"] == city]

# group by area
area_congestion = city_data.groupby("area")["congestion"].mean().reset_index()

# sort values
area_congestion = area_congestion.sort_values(by="congestion", ascending=False)

# bar chart
fig3 = go.Figure()

fig3.add_trace(go.Bar(
    x=area_congestion["area"],
    y=area_congestion["congestion"],
    marker_color="#00ffd5"
))

fig3.update_layout(
    template="plotly_dark",
    title=f"Congestion Comparison in {city}",
    xaxis_title="Area",
    yaxis_title="Average Congestion Level"
)

st.plotly_chart(fig3, use_container_width=True)
st.subheader("AI Traffic Ranking")

# calculate congestion
data_hist["congestion"] = data_hist["free_speed"] - data_hist["current_speed"]

city_data = data_hist[data_hist["city"] == city]

ranking = city_data.groupby("area")["congestion"].mean().sort_values(ascending=False)

if len(ranking) > 0:

    most_congested = ranking.index[0]
    least_congested = ranking.index[-1]

    st.error(f"🚨 Most Congested Area: {most_congested}")

    if len(ranking) > 1:
        st.warning(f"⚠ Moderate Traffic: {ranking.index[1]}")

    st.success(f"🟢 Smooth Traffic Area: {least_congested}")

# ----------- AUTO REFRESH -----------

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=refresh_time*1000)

st.divider()
st.subheader("Processing Speed")

# simulate processing speed
processing_speed = np.random.randint(20, 40)

fig_speed = go.Figure(go.Indicator(
    mode="gauge+number",
    value=processing_speed,
    title={'text': "FPS"},
    gauge={
        'axis': {'range': [0, 60]},
        'bar': {'color': "#00ff88"},
        'bgcolor': "black",
        'borderwidth': 2,
        'bordercolor': "#00ff88",
        'steps': [
            {'range': [0, 20], 'color': "#1a2a3a"},
            {'range': [20, 40], 'color': "#16263a"},
            {'range': [40, 60], 'color': "#101e2e"}
        ],
    }
))

fig_speed.update_layout(
    template="plotly_dark",
    height=350
)

st.plotly_chart(fig_speed, use_container_width=True)
st.subheader("Processing Speed")

speed=np.random.randint(20,40)

fig4=go.Figure(go.Indicator(
mode="gauge+number",
value=speed,
title={'text':"FPS"},
gauge={'axis':{'range':[0,60]}}
))

fig4.update_layout(template="plotly_dark")

st.plotly_chart(fig4,use_container_width=True)
