import streamlit as st
import os
from streamlit_extras.switch_page_button import switch_page


# Main entry point
def main():
    st.title("Welcome to the Transcription App")

    # Add a descriptive introduction
    st.write("Start by selecting an existing user or creating a new user profile.")

    # Tabs for "Existing User" and "New User" options
    tab1, tab2 = st.tabs(["Select Existing User", "Create New User"])

    # Tab 1: Select Existing User
    with tab1:
        st.write("Choose from existing users:")
        existing_users = get_existing_users()
        existing_user = st.selectbox("Existing Users", existing_users, index=0)

        if st.button("Continue with Selected User"):
            if existing_user:
                st.session_state.username = existing_user
                st.session_state.user_dir = os.path.join("./users", existing_user)
                switch_page("Home")
            else:
                st.warning("No existing user selected.")

    # Tab 2: Create New User
    with tab2:
        st.write("Or create a new user profile:")
        new_username = st.text_input("Enter a new username:")

        if st.button("Create and Continue"):
            if new_username:
                st.session_state.username = new_username
                st.session_state.user_dir = create_user_directory(new_username)
                switch_page("Home")
            else:
                st.warning("Please enter a username to create a new profile.")

if __name__ == "__main__":
    main()