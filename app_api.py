from fastapi import FastAPI, HTTPException, Depends, Request, Header
from pydantic import BaseModel, Field
from typing import List
import pickle
import joblib
import logging
import toml
import pandas as pd
import json
from datetime import datetime
import os
import re

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/api.log"), logging.StreamHandler()],
)
logger = logging.getLogger("PropertyValuationAPI")

# Dependency for API key validation
def validate_api_key(api_key: str = ""):
    secrets = toml.load('secrets.toml')
    API_KEY = secrets['property_friends']
    if api_key != API_KEY:
        logger.warning(f"Unauthorized access attempt with API key: {api_key}")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Function to find the highest version model file
def get_latest_model_path(models_dir="models", model_prefix="property_friends"):
    model_files = [f for f in os.listdir(models_dir) if re.match(rf"{model_prefix}_v\d+\.joblib", f)]
    if not model_files:
        raise FileNotFoundError("No model files found in the specified directory")
    
    # Extract version numbers and find the highest one
    model_files.sort(key=lambda x: int(re.search(r"_v(\d+)", x).group(1)), reverse=True)
    return os.path.join(models_dir, model_files[0])

# Load the trained model
model_path = get_latest_model_path()
if model_path.endswith('.joblib'):
    with open(model_path, "rb") as f:
        model = joblib.load(f)
elif model_path.endswith('.pkl'):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
else:
    raise ValueError("Unsupported model file format")

# Define the schema for property data
class PropertyData(BaseModel):
    type: str
    sector: str
    net_usable_area: float
    net_area: float
    n_rooms: float
    n_bathroom: float
    latitude: float
    longitude: float

class PredictionResponse(BaseModel):
    price: float

# Health check endpoint
@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
def predict_property(
    property_data: PropertyData, 
    api_key: str = Header(None, alias='Authorization')
):
    # Validate the API key
    validate_api_key(api_key)
    
    try:
        # Convert input data to the model's expected format
        input_data = pd.DataFrame([{
            'type': property_data.type,
            'sector': property_data.sector,
            'net_usable_area': property_data.net_usable_area,
            'net_area': property_data.net_area,
            'n_rooms': property_data.n_rooms,
            'n_bathroom': property_data.n_bathroom,
            'latitude': property_data.latitude,
            'longitude': property_data.longitude,
        }])
        
        # Generate prediction
        prediction = model.predict(input_data)[0]
        logger.info("Prediction generated successfully")
        return PredictionResponse(price=prediction)
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

# Additional logger for JSON logs
json_logger = logging.getLogger("PropertyValuationAPI_JSON")
json_handler = logging.FileHandler("logs/api_logs.json")
json_handler.setFormatter(logging.Formatter('%(message)s'))
json_logger.addHandler(json_handler)
json_logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    log_data = {
        "timestamp": start_time.isoformat(),
        "endpoint": str(request.url.path),
        "method": request.method,
        "status_code": response.status_code,
        "duration": duration,
        "error": None if response.status_code == 200 else response.body.decode()
    }
    
    # Write JSON log
    if os.path.exists("logs/api_logs.json") and os.path.getsize("logs/api_logs.json") > 0:
        with open("logs/api_logs.json", "r+") as f:
            content = f.read().strip()
            if content.endswith(']'):
                content = content[:-1] + ",\n" + json.dumps(log_data) + "\n]"
            else:
                content = "[\n" + json.dumps(log_data) + "\n]"
            f.seek(0)
            f.write(content)
            f.truncate()
    else:
        with open("logs/api_logs.json", "w") as f:
            f.write("[\n" + json.dumps(log_data) + "\n]")

    logger.info(f"Response status: {response.status_code}")
    return response