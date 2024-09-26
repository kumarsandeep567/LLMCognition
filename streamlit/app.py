import streamlit as st
from loginpage import display_login_page
from searchengine import display_search_engine
from validation import display_validation_page

def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'  # Default to login page

    # Navigate to the correct page based on session state
    if st.session_state['page'] == 'login':
        display_login_page()  # Display the login page
    elif st.session_state['page'] == 'searchengine':
        display_search_engine()  # Display the search engine
    elif st.session_state['page'] == 'validation':
        display_validation_page()  # Display the validation page

if __name__ == '__main__':
    main()
