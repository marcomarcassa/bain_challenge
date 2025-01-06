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
from time import time

app = FastAPI(
    title="Property Valuation Model API",
    description="API dedicated to run predictions on the latest version of the property_friends model",
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # Example customization
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/api.log"), logging.StreamHandler()],
)
logger = logging.getLogger("PropertyValuationAPI")


########################################################################
# Functions for API Key Validation, rate limiting, IP Blacklisting and Model Loading
########################################################################

# In-memory store for rate limiting (user IP and timestamps)
rate_limit_data = {}
RATE_LIMIT = 5  # Max requests per minute
WINDOW = 60  # Time window in seconds

secrets = toml.load('API/secrets.toml')
blacklisted_IPs = secrets['BLACKLISTED_IPS']

def is_rate_limited(client_ip: str) -> bool:
    now = time()
    if client_ip not in rate_limit_data:
        rate_limit_data[client_ip] = [now]
        return False

    request_times = rate_limit_data[client_ip]
    # Remove timestamps outside the time window
    rate_limit_data[client_ip] = [t for t in request_times if now - t < WINDOW]

    # Check if requests exceed the rate limit
    if len(rate_limit_data[client_ip]) >= RATE_LIMIT:
        return True

    # Log the current request time
    rate_limit_data[client_ip].append(now)
    return False

# Dependency for API key validation
def validate_api_key(api_key: str = ""):
    secrets = toml.load('API/secrets.toml')
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
@app.get("/health", tags=["Basic Operations"])
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

# Version information endpoint
@app.get("/version", tags=["Basic Operations"])
def get_version():
    return {"api_version": "1.0.0", "model_version": "v1"}

# Logs endpoint
@app.get("/logs", tags=["Basic Operations"])
def get_logs():
    with open("logs/api.log", "r") as f:
        logs = f.readlines()
    return {"logs": logs[-100:]}  # Return the last 100 log lines

# API documentation endpoint
@app.get("/docs_link", tags=["Basic Operations"])
def get_docs_link():
    return {"docs_url": "/docs"}

# Status endpoint
@app.get("/status", tags=["Basic Operations"])
def get_status():
    status = {
        "api_status": "running",
        "model_status": "loaded",
        "dependencies": {
            "database": "connected",
            "external_api": "reachable"
        }
    }
    return status



# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse, tags=["Model Endpoints"])
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
    except HTTPException as http_exc:
        raise HTTPException(status_code=429, detail="Rate limit exceeded: Please wait before trying again.")
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

# Model metadata endpoint
@app.get("/model_metadata", tags=["Model Endpoints"])
def get_model_metadata():
    metadata = {
        "model_path": model_path,
        "features": ["type", "sector", "net_usable_area", "net_area", "n_rooms", "n_bathroom", "latitude", "longitude"],
        "training_date": "2023-01-01"
    }
    return metadata

# Model history endpoint
@app.get("/model_history", tags=["Model Endpoints"])
def get_model_history():
    try:
        with open("models/model_metrics.json", "r") as f:
            model_history = json.load(f)
        return model_history
    except Exception as e:
        logger.error(f"Error fetching model history: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch model history")


# Additional logger for JSON logs
json_logger = logging.getLogger("PropertyValuationAPI_JSON")
json_handler = logging.FileHandler("logs/api_logs.json")
json_handler.setFormatter(logging.Formatter('%(message)s'))
json_logger.addHandler(json_handler)
json_logger.setLevel(logging.INFO)

@app.middleware("http")
async def ip_blacklist_middleware(request: Request, call_next):
    client_ip = request.client.host
    if client_ip in blacklisted_IPs:
        raise HTTPException(status_code=403, detail="Access forbidden: IP blacklisted")
    return await call_next(request)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    # Check if the route is the prediction endpoint
    if request.url.path == "/predict" and is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded: Please wait before trying again.")
    return await call_next(request)

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