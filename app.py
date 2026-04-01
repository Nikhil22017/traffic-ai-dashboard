import streamlit as st
import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import joblib
import numpy as np
import time

st.set_page_config(page_title="AI Traffic Dashboard", layout="wide")

# Dark mode styling
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}

h1, h2, h3 {
    color: #00FFFF;
}

[data-testid="stMetricValue"] {
    font-size: 28px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
"""
<h1 style='text-align:center;color:#00FFFF'>
🚦 AI Smart Traffic Monitoring Dashboard
</h1>
""",
unsafe_allow_html=True
)

API_KEY="eiCmqqDcgvzAIv1Km6AgVLueOEFwN61Z"

# Sidebar
st.sidebar.markdown("## ⚙️ Dashboard Controls")

city=st.sidebar.selectbox(
"Select City",
["Delhi","Mumbai","Bangalore"]
)

refresh_time=st.sidebar.slider(
"Auto Refresh (seconds)",
10,60,30
)

areas={
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

area=st.sidebar.selectbox(
"Select Area",
list(areas[city].keys())
)

lat,lon=areas[city][area]

st.write(f"### Traffic Analysis for {area}, {city}")

# API request
url=f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={API_KEY}"

data=requests.get(url).json()

if"flowSegmentData" in data:
    traffic=data["flowSegmentData"]
else:
    st.error("Traffic API error.Check API key or API limit.")
    st.write(data)
    st.stop()
traffic=data["flowSegmentData"]

current_speed=traffic["currentSpeed"]
free_speed=traffic["freeFlowSpeed"]
confidence=traffic["confidence"]

congestion=free_speed-current_speed

st.divider()

# Metrics
col1,col2,col3=st.columns(3)

col1.metric("Current Speed",f"{current_speed} km/h")
col2.metric("Free Flow Speed",f"{free_speed} km/h")
col3.metric("Confidence",confidence)

# Congestion indicator
if congestion<10:
    st.success("🟢 Smooth Traffic")
elif congestion<20:
    st.warning("🟡 Moderate Traffic")
else:
    st.error("🔴 Heavy Congestion")

st.divider()

# Congestion gauge
st.subheader("Traffic Congestion Indicator")

fig=go.Figure(go.Indicator(
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

st.plotly_chart(fig,use_container_width=True)

st.divider()

# Save dataset
row={
"time":datetime.now(),
"city":city,
"area":area,
"current_speed":current_speed,
"free_speed":free_speed,
"confidence":confidence,
"lat":lat,
"lon":lon
}

df=pd.DataFrame([row])

file="traffic_history.csv"

if os.path.exists(file):
    df.to_csv(file,mode="a",header=False,index=False)
else:
    df.to_csv(file,mode="w",header=True,index=False)

data_hist=pd.read_csv(file)

data_hist["time"]=pd.to_datetime(data_hist["time"])

st.divider()

# Traffic speed graph
st.subheader("Traffic Speed History")

fig2=px.line(
data_hist.tail(30),
x="time",
y="current_speed",
color="area",
markers=True
)

st.plotly_chart(fig2)

st.divider()

# Heatmap
st.subheader("Traffic Heatmap")

m=folium.Map(location=[lat,lon],zoom_start=12)

heat_data=data_hist[["lat","lon"]].values.tolist()

HeatMap(heat_data).add_to(m)

folium.Marker([lat,lon],popup=f"{area},{city}").add_to(m)

st_folium(m,width=900)

st.divider()

# AI prediction
if os.path.exists("traffic_model.pkl"):

    model=joblib.load("traffic_model.pkl")

    features=np.array([[current_speed,free_speed,confidence]])

    prediction=model.predict(features)[0]

    st.subheader("🤖 AI Traffic Prediction")

    st.metric("Predicted Congestion",round(prediction,2))

    predicted_speed=free_speed-prediction

    st.metric("Predicted Speed",round(predicted_speed,2))

    st.subheader("AI Traffic Risk Score")

    st.write("Risk Score = Predicted Congestion / Free Flow Speed")

    risk_score=prediction/free_speed

    st.metric("Risk Score",round(risk_score,2))

    if risk_score<0.2:
        st.success("Low congestion risk")
    elif risk_score<0.5:
        st.warning("Moderate congestion risk")
    else:
        st.error("High congestion risk")

    st.divider()

    # Future forecast
    future=[]

    for i in range(5):
        pred=model.predict([[current_speed,free_speed,confidence]])
        future.append(pred[0])

    forecast=pd.DataFrame({
    "Step":range(1,6),
    "Predicted Congestion":future
    })

    fig3=px.line(
    forecast,
    x="Step",
    y="Predicted Congestion",
    markers=True,
    title="Future Traffic Forecast"
    )

    st.plotly_chart(fig3)

st.divider()

# Top congested areas
# Top Congested Areas Analytics

st.subheader("Top Congested Areas in City")

st.write(
"""
This section analyzes historical traffic data to identify the most congested
areas within the selected city. Congestion is calculated using the formula:

Congestion = Free Flow Speed − Current Speed

Higher congestion values indicate slower traffic conditions compared to
ideal road speeds.
"""
)

if len(data_hist) > 5:

    # Calculate congestion
    data_hist["congestion"] = data_hist["free_speed"] - data_hist["current_speed"]

    # Area level congestion
    area_congestion = data_hist.groupby("area")["congestion"].mean().reset_index()

    area_congestion = area_congestion.sort_values(
        by="congestion",
        ascending=False
    ).head(5)

    # Graph
    fig4 = px.bar(
        area_congestion,
        x="area",
        y="congestion",
        color="congestion",
        title="Average Congestion by Area"
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.write("### Congestion Details Table")

    st.dataframe(area_congestion)

    # AI Insight
    most_congested = area_congestion.iloc[0]["area"]

    avg_congestion = area_congestion.iloc[0]["congestion"]

    st.write(
        f"AI Insight: **{most_congested}** currently shows the highest average congestion "
        f"with a congestion score of **{round(avg_congestion,2)}**."
    )

    # Congestion level explanation

    st.write("### Congestion Level Interpretation")

    st.write("0 – 10  → Smooth Traffic")

    st.write("10 – 20 → Moderate Congestion")

    st.write("20+     → Heavy Congestion")

# Auto refresh
time.sleep(refresh_time)

st.rerun()
