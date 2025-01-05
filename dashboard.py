import streamlit as st
from streamlit_extras.switch_page_button import switch_page

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

    # Display buttons for each page
    for page_name, module_name in pages.items():
        if st.button(page_name):
            switch_page(module_name)

if __name__ == "__main__":
    main()
