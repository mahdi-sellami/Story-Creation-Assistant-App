import streamlit as st
import pandas as pd
import numpy as np
import logging
import cv2


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set the page configuration
st.set_page_config(
    page_title="Creative Writer", page_icon="👩‍🎨", initial_sidebar_state="auto", menu_items={}
)

# Initialize chat history
if "messages" not in st.session_state:
    # a list to store the chat messages
    st.session_state.messages = []

# Display chat messages from history in a chat message container on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

path = r"fortiss.png"

image = cv2.imread(path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)

im_1 = st.image(image, width=75)

st.title('(Fictional) Story creation assistant')


st.write("Hello! My name is DELIRIA. People often say that I am delirious, I prefer to say that I am creative 👩‍🎨")
st.write("Today I will assist you to write a (fictional) story. Let's get creative together! ✍️")
st.write("Do you have an idea about the topic you want to write about?")

# Accept user input
if prompt := st.chat_input("Write your answer here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)
    # Add user message to chat history
    st.session_state.messages.append({"role": "assistant", "content": "Thanks for your input 🙏"})
    with st.chat_message("assistant"):
        st.markdown("Thanks for your input 🙏", unsafe_allow_html=True)


