# 🚦 AI-Based Real-Time Traffic Monitoring & Prediction System

## 📌 Project Overview

The **AI-Based Real-Time Traffic Monitoring and Prediction System** is an intelligent dashboard that analyzes live traffic conditions using real-time traffic APIs and machine learning techniques.

The system collects traffic data such as **current speed, free-flow speed, and confidence levels**, processes it, and provides insights through an interactive dashboard. It also predicts future traffic congestion using a machine learning model.

This project demonstrates how **AI, data visualization, and real-time APIs** can be integrated to build a smart traffic analytics platform.

---

## 🎯 Objectives

* Monitor **real-time traffic conditions**
* Analyze **traffic congestion patterns**
* Provide **city and area-wise traffic insights**
* Predict **future traffic congestion using machine learning**
* Visualize traffic analytics using interactive charts and maps

---

## ⚙️ Features

### 🚦 Real-Time Traffic Monitoring

Fetches live traffic data using a traffic API.

### 🏙 City & Area-Based Traffic Analysis

Users can select:

* City
* Area within the city

The system displays traffic insights specific to that location.

### 📊 Traffic Speed Analytics

Shows traffic trends using historical traffic data.

### 🔥 Traffic Heatmap

Displays traffic intensity on a map using heatmap visualization.

### ⚠️ Traffic Congestion Gauge

A real-time congestion meter that visually indicates traffic severity.

### 🤖 AI-Based Traffic Prediction

A machine learning model predicts future congestion levels based on traffic parameters.

### 📉 AI Traffic Risk Score

Calculates congestion risk using:

Traffic Risk Score = Predicted Congestion / Free Flow Speed

### 📈 Future Traffic Forecast

Predicts congestion for the next few time intervals.

### 📊 Top Congested Areas Analytics

Identifies the most congested areas in a city based on historical traffic data.

---

## 🧠 Machine Learning Model

The system uses **Random Forest Regression** to predict congestion levels.

### Input Features

* Current Speed
* Free Flow Speed
* Confidence

### Target Variable

* Congestion

Congestion is calculated as:

Congestion = Free Flow Speed − Current Speed

---

## 🛠 Technologies Used

| Technology   | Purpose                   |
| ------------ | ------------------------- |
| Python       | Core programming language |
| Streamlit    | Interactive dashboard     |
| Pandas       | Data processing           |
| Plotly       | Data visualization        |
| Folium       | Map visualization         |
| Scikit-Learn | Machine learning          |
| Joblib       | Model storage             |
| Git & GitHub | Version control           |

---

## 📁 Project Structure

```
traffic_project
│
├── app.py
├── train_model.py
├── requirements.txt
├── traffic_history.csv
└── traffic_model.pkl
```

---

## 🚀 Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/yourusername/traffic-ai-dashboard.git
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Run the dashboard

```
streamlit run app.py
```

---

## 📊 Dashboard Modules

* Traffic Metrics Panel
* Congestion Gauge
* Traffic Speed History Graph
* Traffic Heatmap
* AI Traffic Prediction
* Traffic Risk Score
* Future Traffic Forecast
* Top Congested Areas Chart

---

## 🔮 Future Improvements

* Route optimization using traffic data
* Traffic anomaly detection
* Smart traffic signal integration
* Deep learning traffic prediction (LSTM)

---

## 👨‍💻 Author

**Nikhil Sharma**

B.Tech Computer Science (AI & ML)

---

## 📄 License

This project is developed for **educational and research purposes**.

