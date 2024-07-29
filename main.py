import streamlit as st
from story_generator import generate_story, log_story, analyze_pacing, plot_pacing
from ui_elements import display_ui, display_story_segments, display_analysis_options
import streamlit.components.v1 as components


st.title("Custom Short Story Generator")

model, length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters, story_title = display_ui()

# Analysis options
pacing_analysis = display_analysis_options()

if st.button("Generate Story"):
    if not story_title:
        story_title = "Untitled Story"
        
    story = generate_story(model, length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters, story_title)
    st.write(story)
    
    modified_story = display_story_segments(story)
    
    if st.button("Save Modified Story"):
        log_story("User modified story", modified_story, story_title + " (Modified)")
        st.success("Modified story saved.")

    if pacing_analysis:
        pacing_scores = analyze_pacing(modified_story)
        st.subheader("Pacing Analysis")
        st.write("Pacing scores per paragraph:", pacing_scores)
        img = plot_pacing(pacing_scores)
        components.html(f'<img src="data:image/png;base64,{img}" alt="Pacing Analysis">')

