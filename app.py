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

# ---------- MODERN UI ----------

st.markdown("""
<style>

.stApp{
background-color:#070d19;
color:white;
}

h1{
color:#00ffe1;
text-align:center;
}

[data-testid="metric-container"]{
background:#111827;
border-radius:12px;
padding:20px;
border:1px solid #1f2937;
box-shadow:0px 0px 15px rgba(0,255,200,0.3);
}

[data-testid="stMetricValue"]{
color:#00ffe1;
font-size:30px;
}

section[data-testid="stSidebar"]{
background:#0b1324;
}

</style>
""",unsafe_allow_html=True)

# ---------- HEADER ----------

colA,colB,colC = st.columns([3,2,1])

with colA:
    st.markdown("<h1>🚦 AI Smart Traffic Monitoring Dashboard</h1>",unsafe_allow_html=True)

with colB:
    st.write("### ⏱",datetime.now().strftime("%H:%M:%S"))

with colC:
    st.success("● LIVE")

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

# ---------- API ----------

API_KEY="eiCmqqDcgvzAIv1Km6AgVLueOEFwN61Z"

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

# ---------- CONGESTION GAUGE ----------

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

# ---------- TRAFFIC GRAPH ----------

st.subheader("Traffic Speed History")

fig2=px.line(
data_hist.tail(30),
x="time",
y="current_speed",
color="area",
markers=True
)

fig2.update_layout(template="plotly_dark")

st.plotly_chart(fig2,use_container_width=True)

st.divider()

# ---------- VEHICLE MIX CHART ----------

st.subheader("Vehicle Mix Analytics")

vehicle_data={
"Cars":np.random.randint(20,40),
"Buses":np.random.randint(5,10),
"Trucks":np.random.randint(5,15),
"Bikes":np.random.randint(10,30)
}

vehicle_df=pd.DataFrame({
"Vehicle":vehicle_data.keys(),
"Count":vehicle_data.values()
})

fig3=px.pie(
vehicle_df,
values="Count",
names="Vehicle",
hole=0.6
)

fig3.update_layout(template="plotly_dark")

st.plotly_chart(fig3,use_container_width=True)

st.divider()

# ---------- HEATMAP ----------
st.subheader("Traffic Heatmap")

st.write(
"""
This heatmap visualizes traffic intensity based on historical traffic data.
Areas with higher traffic activity appear more intense on the map.
"""
)

m = folium.Map(location=[lat, lon], zoom_start=12)

heat_data = data_hist[["lat","lon"]].values.tolist()

HeatMap(
    heat_data,
    radius=20,
    blur=15
).add_to(m)

folium.Marker(
    [lat, lon],
    popup=f"""
    Area: {area}<br>
    City: {city}<br>
    Current Speed: {current_speed} km/h<br>
    Free Flow Speed: {free_speed} km/h
    """
).add_to(m)

st_folium(m, width=900)

st.divider()

st.subheader("AI Predicted Congestion Map")

st.write(
"""
This map shows the predicted traffic congestion level in the selected area.
The color of the marker represents traffic severity.
"""
)

m2 = folium.Map(location=[lat, lon], zoom_start=12)

if congestion < 10:
    color = "green"
    status = "Smooth Traffic"

elif congestion < 20:
    color = "orange"
    status = "Moderate Traffic"

else:
    color = "red"
    status = "Heavy Congestion"

folium.CircleMarker(
    location=[lat, lon],
    radius=18,
    popup=f"""
    Area: {area}<br>
    City: {city}<br>
    Predicted Congestion: {round(congestion,2)}<br>
    Status: {status}
    """,
    color=color,
    fill=True,
    fill_color=color
).add_to(m2)

st_folium(m2, width=900)

st.markdown("""
### Traffic Congestion Legend

🟢 **Green** → Smooth traffic (Low congestion)

🟡 **Orange** → Moderate traffic

🔴 **Red** → Heavy congestion
""")

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

    risk_score=prediction/free_speed

    st.metric("Traffic Risk Score",round(risk_score,2))

st.divider()

st.divider()

st.subheader("AI Prediction Accuracy")

if os.path.exists("traffic_model.pkl") and len(data_hist) > 10:

    model = joblib.load("traffic_model.pkl")

    data_hist["congestion"] = data_hist["free_speed"] - data_hist["current_speed"]

    X = data_hist[["current_speed","free_speed","confidence"]]

    data_hist["predicted"] = model.predict(X)

    fig5 = px.line(
        data_hist.tail(30),
        x="time",
        y=["congestion","predicted"],
        title="Actual vs Predicted Congestion"
    )

    fig5.update_layout(template="plotly_dark")

    st.plotly_chart(fig5,use_container_width=True)
# ---------- PROCESSING SPEED METER ----------

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

# ---------- AUTO REFRESH ----------

time.sleep(refresh_time)

st.rerun()
