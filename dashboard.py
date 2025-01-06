import streamlit as st

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from pages.streamlit_utils import show_sidebar_pages
show_sidebar_pages()



# List of available pages
pages = {
    "Test Prediction": "test_prediction",
    "Regenerate API Key": "regenerate_api_key",
    "Monitoring Dashboard": "monitoring",
    "Retrain Model ": "retrain_model"
}

def main():
    st.title("Dashboard Home")
    st.write("Welcome to the Property Valuation Dashboard. Select a task below:")
    st.page_link("dashboard.py", label="Home", icon="🏠")

    # Display buttons for each page
    for page_name, module_name in pages.items():
        st.page_link("pages/"+module_name+".py", label=page_name, icon="🔗")
    
    #st.page_link("pages/page_1.py", label="Page 1", icon="1️⃣")
    st.page_link("http://localhost:8000/docs", label="Swagger", icon="🌎")

if __name__ == "__main__":
    main()
