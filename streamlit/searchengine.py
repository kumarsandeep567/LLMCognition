import streamlit as st
import requests
from http import HTTPStatus

def display_search_engine():
    st.title("Search Engine")

    # Fetch prompts from the backend
    response = requests.get("http://localhost:8000/listprompts/12")
    response_data = response.json()

    if response_data['status'] == HTTPStatus.OK:
        prompts_list = response_data['message']
        # Create a dictionary with question and task_id pair for easy reference
        prompts_dict = {item['question']: item['task_id'] for item in prompts_list}
        prompts = list(prompts_dict.keys())

        # Autocomplete dropdown using a selectbox to select a question
        selected_prompt = st.selectbox("Select a prompt:", prompts)

        # Load Data button to display prompt data
        if st.button("Load Data") and selected_prompt:
            # Get the task_id of the selected question
            selected_task_id = prompts_dict[selected_prompt]
            
            # Fetch the prompt data from the backend using the task_id
            load_response = requests.get(f"http://localhost:8000/loadprompt/{selected_task_id}")
            load_data = load_response.json()

            if load_data['status'] == HTTPStatus.OK:
                # Display the question for the task
                file_name = 'empty' if load_data['message']['file_name'] == '' else load_data['message']['file_name']
                st.text_area("Question", value=load_data['message']['question'], key="task_question", disabled=True, height=100)
                st.text_input("Level", value=load_data['message']['level'], key="task_level", disabled=True)
                st.text_input("File", value=file_name, key="task_filename", disabled=True)
            else:
                st.error("Failed to load prompt data.")

        if st.button("Generate Response") and selected_prompt:
            # Get the task_id of the selected question
            selected_task_id = prompts_dict[selected_prompt]
            
            # Send the task_id to the backend and generate a response
            # response = generate_response(selected_task_id)

            # Store the GPT response in session state for validation page
            st.session_state['task_id'] = selected_task_id

            # Set the page state to validation
            st.session_state['page'] = 'validation'
            # No need for rerun, the app will re-execute

    else:
        st.error("Failed to fetch prompts from the server.")

def generate_response(task_id):
    # Here you would implement your logic to generate a response based on the task_id
    # For demonstration purposes, we'll just return a mock response
    return f"Response for task ID: '{task_id}'"  # Replace with actual GPT logic

def display_validation_page():
    st.title("Validation Page")

    if 'gpt_response' in st.session_state:
        # Display the GPT response in a text area
        st.write("### GPT Response:")
        st.text_area("Response", value=st.session_state['gpt_response'], height=200, disabled=True)

    # Optionally add validation logic here
    if st.button("Back to Search"):
        # Go back to the search engine
        st.session_state['page'] = 'search_engine'

# Main execution flow
if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state['page'] = 'search_engine'  # Default page

    if st.session_state['page'] == 'search_engine':
        display_search_engine()
    else:
        display_validation_page()
