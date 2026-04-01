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

# ---------- MODERN UI CSS ----------

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

# ---------- HEADER ----------

st.markdown("<h1>🚦 AI Smart Traffic Monitoring Dashboard</h1>",unsafe_allow_html=True)

# ---------- API KEY ----------

API_KEY="eiCmqqDcgvzAIv1Km6AgVLueOEFwN61Z"

# ---------- SIDEBAR ----------

st.sidebar.title("⚙ Dashboard Controls")

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

area=st.sidebar.selectbox("Select Area",list(areas[city].keys()))

lat,lon=areas[city][area]

st.subheader(f"Traffic Analysis for {area}, {city}")

# ---------- API REQUEST ----------

url=f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={API_KEY}"

data=requests.get(url).json()

if "flowSegmentData" not in data:
    st.error("Traffic API error. Check API key.")
    st.stop()

traffic=data["flowSegmentData"]

current_speed=traffic["currentSpeed"]
free_speed=traffic["freeFlowSpeed"]
confidence=traffic["confidence"]

congestion=free_speed-current_speed

# ---------- METRICS ----------

col1,col2,col3,col4=st.columns(4)

col1.metric("🚗 Current Speed",f"{current_speed} km/h")
col2.metric("🛣 Free Flow Speed",f"{free_speed} km/h")
col3.metric("📊 Confidence",confidence)
col4.metric("⚠ Congestion",congestion)

st.divider()

# ---------- CONGESTION STATUS ----------

if congestion<10:
    st.success("🟢 Smooth Traffic")
elif congestion<20:
    st.warning("🟡 Moderate Traffic")
else:
    st.error("🔴 Heavy Traffic")

# ---------- GAUGE ----------

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

fig.update_layout(template="plotly_dark")

st.plotly_chart(fig,use_container_width=True)

st.divider()

# ---------- SAVE DATA ----------

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
    df.to_csv(file,index=False)

data_hist=pd.read_csv(file)

data_hist["time"]=pd.to_datetime(data_hist["time"])

# ---------- TRAFFIC HISTORY GRAPH ----------

st.subheader("Traffic Speed History")

fig2=px.line(
data_hist.tail(30),
x="time",
y="current_speed",
color="area",
markers=True
)

fig2.update_layout(
template="plotly_dark",
plot_bgcolor="#0b0f19",
paper_bgcolor="#0b0f19"
)

st.plotly_chart(fig2,use_container_width=True)

st.divider()

# ---------- HEATMAP ----------

st.subheader("Traffic Heatmap")

m=folium.Map(location=[lat,lon],zoom_start=12)

heat_data=data_hist[["lat","lon"]].values.tolist()

HeatMap(heat_data).add_to(m)

folium.Marker([lat,lon],popup=f"{area},{city}").add_to(m)

st_folium(m,width=900)

st.divider()

# ---------- AI PREDICTION ----------

if os.path.exists("traffic_model.pkl"):

    model=joblib.load("traffic_model.pkl")

    features=np.array([[current_speed,free_speed,confidence]])

    prediction=model.predict(features)[0]

    st.subheader("🤖 AI Traffic Prediction")

    colA,colB=st.columns(2)

    colA.metric("Predicted Congestion",round(prediction,2))

    predicted_speed=free_speed-prediction

    colB.metric("Predicted Speed",round(predicted_speed,2))

    st.subheader("AI Traffic Risk Score")

    risk_score=prediction/free_speed

    st.metric("Risk Score",round(risk_score,2))

    if risk_score<0.2:
        st.success("Low congestion risk")
    elif risk_score<0.5:
        st.warning("Moderate congestion risk")
    else:
        st.error("High congestion risk")

st.divider()

# ---------- TOP CONGESTED AREAS ----------

st.subheader("Top Congested Areas in City")

if len(data_hist)>5:

    data_hist["congestion"]=data_hist["free_speed"]-data_hist["current_speed"]

    area_congestion=data_hist.groupby("area")["congestion"].mean().reset_index()

    area_congestion=area_congestion.sort_values(
    by="congestion",
    ascending=False
    ).head(5)

    fig4=px.bar(
    area_congestion,
    x="area",
    y="congestion",
    color="congestion",
    title="Average Congestion by Area"
    )

    fig4.update_layout(template="plotly_dark")

    st.plotly_chart(fig4,use_container_width=True)

# ---------- AUTO REFRESH ----------

time.sleep(refresh_time)

st.rerun()
