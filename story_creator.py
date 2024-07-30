import streamlit as st
import requests
import pandas as pd
import numpy as np
import logging
import cv2

from story_generator import generate_story, log_story, analyze_pacing, get_logged_stories, generate_book_cover, postscriptum_generator
from ui_elements import display_ui, display_story_segments, display_analysis_options
import streamlit.components.v1 as components

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set the page configuration
st.set_page_config(
    page_title="Creative Writer", page_icon="👩‍🎨", initial_sidebar_state="auto", menu_items={}
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history in a chat message container on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

path = r"fortiss.png"
image = cv2.imread(path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
im_1 = st.image(image, width=75)

personas = {
        "character": "J. K. Rowling",
        "environment": "H. P. Lovecraft",
        "brainstorm": "Lev Tolstoy",
        "outline": "Cristopher Nolan",
        "chapter": "Fyodor Dostoevsky"
    }

st.title('Story Creation Assistant')

st.write("Hello! My name is DELIRIA. People often say that I am delirious, I prefer to say that I am creative 👩‍🎨")
st.write("Today I will assist you to write a (fictional) story. Let's get creative together! ✍️")
st.write("Do you have an idea about the topic you want to write about?")

# Accept user input
if prompt := st.chat_input("Write your answer here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    # Perform API call
    assistant_response = None    
    try:        
        # assistant_response = requests.get(        
        #     "http://api:8000/api/query/",        
        #     params={"text_query": prompt},        
        #     timeout=config.ASSISTANT_TIMEOUT,        
        # )        
        assistant_response = requests.post("http://api:8000/stream/", json={"instruction": prompt, "details": "test", "personas": personas}, timeout=1800,)        
        assistant_response.raise_for_status()  
        # Raises a HTTPError for bad responses   
    except requests.exceptions.HTTPError as e:        
        st.error(f"Server returned an error: {e.response.status_code}, {e.response.text}")    
    except requests.exceptions.ConnectionError:        
        st.error("Failed to connect to the server. Please check your connection.")    
    except requests.exceptions.Timeout:        
        st.error("Server took too long to respond. Please try again later.")    
    except requests.exceptions.RequestException as e:        
        st.error(f"An error occurred: {e}")

    # Display assistant response in chat message container    
    with st.chat_message("assistant"):        
        message_placeholder = st.empty()        
        if assistant_response.status_code == 200:            
            message_placeholder.markdown(assistant_response.json()["content"], unsafe_allow_html=True)            
            st.session_state.messages.append({"role": "assistant", "content": assistant_response.json()["content"]})        
        else:            
            message_placeholder.error(f"Failed to get a response from the server: {assistant_response.status_code}") 

with st.sidebar:
    tab1, tab2, tab3 = st.tabs(["Customization", "Agent Configuration", "Worldbuilding"])

    with tab1:
        st.write("## Story Parameters")
        
        # Single column for customization parameters
        model = st.selectbox("Model", ["gpt-4o-2024-05-13", "gpt-3.5-turbo"])
        length = st.selectbox("Length", ["Short", "Medium-form", "Long-form"])
        fiction_level = st.selectbox("Level of Fiction", ["Complete fiction", "Based on true story", "Non-fiction"])
        reality_level = st.selectbox("Level of Reality Groundedness", ["Completely fantastical", "Semi-realistic", "Realistic"])
        informativeness = st.selectbox("Type of Informativeness", ["Information", "Misinformation"])
        moral_theme = st.selectbox("Moral Themes", ["Honesty", "Perseverance", "Friendship", "Fairness", "Collaboration"])
        ip_avoidance = st.selectbox("Intellectual Property / Copyright Avoidance", ["Completely original", "Inspired by genre", "Inspired by author", "Inspired by particular work", "Derivative (i.e., fan fiction)", "Plagiarism"])
        num_characters = st.slider("Number of Characters", 1, 20, 1)
        story_title = st.text_input("Enter a title for your story")

        logged_stories = get_logged_stories()
        story_options = [f"{i+1}: {entry.get('title', 'Untitled')} ({entry['timestamp']})" for i, entry in enumerate(logged_stories)]
        selected_story = st.selectbox("Select a previously generated story to continue developing", ["None"] + story_options)

        if selected_story != "None":
            selected_story_index = story_options.index(selected_story) - 1
            selected_story_entry = logged_stories[selected_story_index]
            st.write("Selected Story Title:", selected_story_entry.get('title', 'Untitled'))
            st.write("Selected Story Prompt:", selected_story_entry['prompt'])
            st.write("Selected Story:", selected_story_entry['story'])

    with tab2:
        st.write("Agent Configuration")
        
        personas = {
        "character": "J. K. Rowling",
        "environment": "H. P. Lovecraft",
        "brainstorm": "Lev Tolstoy",
        "outline": "Cristopher Nolan",
        "chapter": "Fyodor Dostoevsky"
    }
    
        # Create input fields for each role with initial values from personas dictionary
        character_input = st.text_input("Character Designer", value=personas.get("character"))
        environment_input = st.text_input("Environment Designer", value=personas.get("environment"))
        brainstorm_input = st.text_input("Brainstorm", value=personas.get("brainstorm"))
        outline_input = st.text_input("Outline Writer", value=personas.get("outline"))
        chapter_input = st.text_input("Script Writer", value=personas.get("chapter"))

        # Button to confirm the configuration
        if st.button("Confirm Configuration"):
            # Update personas dictionary with the new inputs
            personas["character"] = character_input
            personas["environment"] = environment_input
            personas["brainstorm"] = brainstorm_input
            personas["outline"] = outline_input
            personas["chapter"] = chapter_input

# Main section for story generation and modification
if st.button("Generate Story"):
    if not story_title:
        story_title = "Untitled Story"
        
    story = generate_story(model, length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters, story_title)
    st.write(story)
    
    modified_story = display_story_segments(story)
    
    if st.button("Save Modified Story"):
        log_story("User modified story", modified_story, story_title + " (Modified)")
        st.success("Modified story saved.")

    pacing_analysis = display_analysis_options()

    if pacing_analysis:
        pacing_scores = analyze_pacing(modified_story)
        st.subheader("Pacing Analysis")
        st.write("Pacing scores per paragraph:", pacing_scores)
        img = plot_pacing(pacing_scores)
        components.html(f'<img src="data:image/png;base64,{img}" alt="Pacing Analysis">')

    # Generate and display the book cover
    book_cover_url = generate_book_cover(story, story_title, moral_theme)
    st.session_state.book_cover_url = book_cover_url

    with st.sidebar:
        with tab3:
            st.write("### Book Cover")
            if book_cover_url:
                st.image(book_cover_url, use_column_width=True)

            postscriptum = postscriptum_generator(story, story_title, length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters)

            st.write("### Analysis")
            st.write(postscriptum)