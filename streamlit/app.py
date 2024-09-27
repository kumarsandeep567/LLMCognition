import streamlit as st
from loginpage import display_login_page
from adminlogin import display_adminlogin_page
from analytics import display_analytics_page
from searchengine import display_search_engine
from validation import display_validation_page

def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'  # Default

    # Display the appropriate page based on session state
    if st.session_state['page'] == 'home':
        display_home_page()
    elif st.session_state['page'] == 'login':
        display_login_page()
    elif st.session_state['page'] == 'adminlogin':
        display_adminlogin_page()
    elif st.session_state['page'] == 'analytics':
        display_analytics_page()
    elif st.session_state['page'] == 'searchengine':
        display_search_engine()
    elif st.session_state['page'] == 'validation':
        display_validation_page()

def display_home_page():
    st.title("Welcome to GPT Search Engine")
    choice = st.selectbox("Select your role:", ["Select", "User", "Admin"], key="user_type")

    if choice in ["User", "Admin"]:
        if st.button("Select"):
            st.session_state['page'] = 'login' if choice == "User" else 'adminlogin'

def display_navigation():
    """Display navigation options."""
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Select Page:", ["Search Engine", "Analytics"])

    if selected_page == "Search Engine":
        st.session_state['page'] = 'searchengine'
    elif selected_page == "Analytics":
        st.session_state['page'] = 'analytics'

# Call display_navigation() once
if 'page' in st.session_state and st.session_state['page'] in ['searchengine', 'analytics', 'feedback']:
    display_navigation()

if __name__ == '__main__':
    main()
