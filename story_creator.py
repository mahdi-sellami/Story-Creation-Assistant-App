import streamlit as st
import pandas as pd
import numpy as np
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set the page configuration
st.set_page_config(
    page_title="Creative Writer", page_icon="📋", initial_sidebar_state="auto", menu_items={}
)

# Initialize chat history
if "messages" not in st.session_state:
    # a list to store the chat messages
    st.session_state.messages = []

# Display chat messages from history in a chat message container on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)


st.title('(Fictional) Story creation assistant')


st.write("Hello! Today I will assist you to write a (fictional) story. Let's get creative together!")

# Accept user input
if prompt := st.chat_input("What do you want to write about?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)