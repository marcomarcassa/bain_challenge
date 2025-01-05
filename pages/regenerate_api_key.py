import streamlit as st
import toml
from utils import generate_api_key

# Streamlit Page for Regenerating API Key
def regenerate_api_key_page():
    st.title("Regenerate API Key")
    st.write("Use this page to regenerate and save a new API key.")

    # Display the current API key
    try:
        secrets_dict = toml.load("secrets.toml")
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