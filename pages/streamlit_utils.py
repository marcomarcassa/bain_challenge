import streamlit as st

def show_sidebar_pages():
    
    st.set_page_config(
        page_title="Dashboard",
        page_icon="chart_with_upwards_trend",
    )

    # List of available pages
    pages = {
        "Test Prediction": "test_prediction",
        "Regenerate API Key": "regenerate_api_key",
        "Monitoring Dashboard": "monitoring",
        "Retrain Model ": "retrain_model"
    }
    st.sidebar.title("Dashboard Pages")
    st.sidebar.page_link("dashboard.py", label="Home", icon="🏠")

    # Display buttons for each page
    for page_name, module_name in pages.items():
        st.sidebar.page_link("pages/"+module_name+".py", label=page_name, icon="🔗")
    

    st.sidebar.divider()
    st.sidebar.title("External Links")
    #st.page_link("pages/page_1.py", label="Page 1", icon="1️⃣")
    st.sidebar.page_link("http://localhost:8000/docs", label="Swagger", icon="🌎")