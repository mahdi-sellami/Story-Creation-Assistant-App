import streamlit as st
from story_generator import get_logged_stories, split_story_into_segments

def display_ui():
    st.write("## Story Parameters")

    # Create columns
    col1, col2 = st.columns(2)

    with col1:
        model = st.selectbox("Model", ["gpt-4o-2024-05-13", "gpt-3.5-turbo"])
        length = st.selectbox("Length", ["Short", "Medium-form", "Long-form"])
        fiction_level = st.selectbox("Level of Fiction", ["Complete fiction", "Based on true story", "Non-fiction"])
        reality_level = st.selectbox("Level of Reality Groundedness", ["Completely fantastical", "Semi-realistic", "Realistic"])
        informativeness = st.selectbox("Type of Informativeness", ["Information", "Misinformation"])
        moral_theme = st.selectbox("Moral Themes", ["Honesty", "Perseverance", "Friendship", "Fairness", "Collaboration"])

    with col2:
        ip_avoidance = st.selectbox("Intellectual Property / Copyright Avoidance", ["Completely original", "Inspired by genre", "Inspired by author", "Inspired by particular work", "Derivative (i.e., fan fiction)", "Plagiarism"])
        num_characters = st.slider("Number of Characters", 1, 20, 1)
        story_title = st.text_input("Enter a title for your story")

        # Option to select and retrieve previous stories
        logged_stories = get_logged_stories()
        story_options = [f"{i+1}: {entry.get('title', 'Untitled')} ({entry['timestamp']})" for i, entry in enumerate(logged_stories)]
        selected_story = st.selectbox("Select a previously generated story to continue developing", ["None"] + story_options)

        if selected_story != "None":
            selected_story_index = story_options.index(selected_story) - 1
            selected_story_entry = logged_stories[selected_story_index]
            st.write("Selected Story Title:", selected_story_entry.get('title', 'Untitled'))
            st.write("Selected Story Prompt:", selected_story_entry['prompt'])
            st.write("Selected Story:", selected_story_entry['story'])

    return model, length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters, story_title

def display_story_segments(story):
    st.subheader("Modify your story:")
    segments = split_story_into_segments(story)
    modified_segments = []
    for i, segment in enumerate(segments):
        modified_segment = st.text_area(f"Segment {i+1}", value=segment, height=100)
        modified_segments.append(modified_segment)
    return '. '.join(modified_segments)

def display_analysis_options():
    st.subheader("Analysis Options")
    pacing_analysis = st.checkbox("Analyze Pacing")
    return pacing_analysis
