import streamlit as st
import toml
from API.utils import generate_api_key

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from streamlit_utils import show_sidebar_pages
show_sidebar_pages()

# Streamlit Page for Regenerating API Key
def regenerate_api_key_page():
    st.title("Regenerate API Key")
    st.write("Use this page to regenerate and save a new API key.")

    # Display the current API key
    try:
        secrets_dict = toml.load("API/secrets.toml")
        current_api_key = secrets_dict.get("property_friends", "API_KEY_NOT_FOUND")
        st.info(f"Current API Key: {current_api_key}")
    except Exception as e:
        st.warning(f"Error reading current API key: {e}")

    # Button to regenerate API key
    if st.button("Regenerate API Key"):
        new_api_key = generate_api_key("property_friends")
        st.success("New API key generated and saved successfully!")
        st.info(f"New API Key: {new_api_key}")

# Ensure this page runs independently for testing
if __name__ == "__main__":
    regenerate_api_key_page()