import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import toml
import os

# Function to load the API key from secrets.toml
def load_api_key():
    try:
        secrets = toml.load("secrets.toml")
        return secrets.get("property_friends", "API_KEY_NOT_FOUND")
    except Exception as e:
        st.error(f"Error loading API key: {e}")
        return None

# Function to make prediction requests to the API
def get_prediction(api_key, data):
    url = "http://127.0.0.1:8000/predict"
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key,
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": "Connection Error", "details": str(e)}

# Streamlit Page for Testing Predictions
def test_prediction_page():
    st.title("Test Prediction")
    st.write("Use this page to test predictions using the API.")

    # Load the API key
    api_key = load_api_key()
    if api_key == "API_KEY_NOT_FOUND":
        st.warning("API key not found in secrets.toml.")
        return
    else:
        #st.info(f"Loaded API Key: {api_key}")
        pass

    # Input fields for property details
    st.header("Enter Property Details")
    property_type = st.selectbox("Property Type", ["departamento", "casa"])
    sector = st.text_input("Sector", value="vitacura")
    net_usable_area = st.number_input("Net Usable Area", value=140.0, step=1.0)
    net_area = st.number_input("Net Area", value=170.0, step=1.0)
    n_rooms = st.number_input("Number of Rooms", value=4, step=1)
    n_bathroom = st.number_input("Number of Bathrooms", value=4, step=1)
    latitude = st.number_input("Latitude", value=-33.40123, step=0.00001)
    longitude = st.number_input("Longitude", value=-70.58056, step=0.00001)

    # Button to trigger prediction
    if st.button("Get Prediction"):
        st.write("Sending data to the API...")
        data = {
            "type": property_type,
            "sector": sector,
            "net_usable_area": net_usable_area,
            "net_area": net_area,
            "n_rooms": n_rooms,
            "n_bathroom": n_bathroom,
            "latitude": latitude,
            "longitude": longitude,
        }

        # Call the prediction API
        result = get_prediction(api_key, data)

        # Display results
        if "error" in result:
            st.error(f"Error: {result['error']}")
            st.write(result.get("details", ""))
        else:
            st.success("Prediction received successfully!")
            st.json(result)

# Run the Test Prediction Page
if __name__ == "__main__":
    test_prediction_page()
