import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

data = pd.read_csv("traffic_history.csv")

data["congestion"] = data["free_speed"] - data["current_speed"]

X = data[["current_speed","free_speed","confidence"]]
y = data["congestion"]

model = RandomForestRegressor()

model.fit(X,y)

joblib.dump(model,"traffic_model.pkl")

print("Model trained successfully")
