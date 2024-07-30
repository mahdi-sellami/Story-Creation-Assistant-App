import openai
from config import OPENAI_API_KEY
import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import io
import base64


LOG_FILE = "story_log.json"

def log_story(prompt, story, story_title):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "title": story_title if story_title else "Untitled",
        "prompt": prompt if prompt else "N/A",
        "story": story
    }
    
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as file:
            json.dump([log_entry], file, indent=4)
    else:
        with open(LOG_FILE, 'r+') as file:
            data = json.load(file)
            data.append(log_entry)
            file.seek(0)
            json.dump(data, file, indent=4)

def analyze_pacing(story):
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a story pacing analyzer."},
            {"role": "user", "content": f"Analyze the pacing of the following story across paragraphs and provide a numerical evaluation for each paragraph:\n\n{story}"}
        ],
        max_tokens=500
    )

    pacing_scores = response['choices'][0]['message']['content'].strip().split('\n')
    pacing_scores = [float(score.split(': ')[-1]) for score in pacing_scores if ':' in score]

    return pacing_scores

def plot_pacing(pacing_scores):
    fig, ax = plt.subplots()
    ax.plot(pacing_scores, marker='o')
    ax.set_title('Story Pacing Analysis')
    ax.set_xlabel('Paragraph')
    ax.set_ylabel('Pacing Score')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return img


def map_user_inputs(length, fiction_level, reality_level, informativeness, ip_avoidance):
    length_map = {
        'Short': "Length: Up to 500 words.\n",
        'Medium-form': "Length: 500-2000 words.\n",
        'Long-form': "Length: 2000+ words.\n"
    }

    fiction_level_map = {
        'Complete fiction': "This is a completely fictional story.\n",
        'Based on true story': "This story is based on a true story.\n",
        'Non-fiction': "This is a non-fiction story.\n"
    }

    reality_level_map = {
        'Completely fantastical': "The story is completely fantastical.\n",
        'Semi-realistic': "The story is semi-realistic.\n",
        'Realistic': "The story is realistic.\n"
    }

    informativeness_map = {
        'Information': "The story provides accurate information.\n",
        'Misinformation': "The story provides misinformation.\n"
    }

    ip_avoidance_map = {
        'Completely original': "The story must be completely original.\n",
        'Inspired by genre': "The story is inspired by a specific genre.\n",
        'Inspired by author': "The story is inspired by a specific author.\n",
        'Inspired by particular work': "The story is inspired by a particular work.\n",
        'Derivative (i.e., fan fiction)': "The story is a fan fiction.\n",
        'Plagiarism': "The story is a plagiarism.\n"
    }

    prompt_parts = [
        length_map.get(length, ""),
        fiction_level_map.get(fiction_level, ""),
        reality_level_map.get(reality_level, ""),
        informativeness_map.get(informativeness, ""),
        ip_avoidance_map.get(ip_avoidance, "")
    ]
    
    return prompt_parts

def construct_prompt(length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters):
    prompt_parts = map_user_inputs(length, fiction_level, reality_level, informativeness, ip_avoidance)
    
    # prompt = "Write a short story with the following parameters:\n"
    prompt = ""
    prompt += "".join(prompt_parts[1:])
    prompt += f"The story should convey the theme of {moral_theme}.\n"
    prompt += f"The story features {num_characters} main characters.\n"
    
    return prompt

def generate_story(model, length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters, story_title):
    prompt = construct_prompt(length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters)
    
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a creative story writer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )
    
    story = response.choices[0].message.content.strip()

    log_story(prompt, story, story_title)
    
    return story

def get_logged_stories():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, 'r') as file:
        return json.load(file)

def split_story_into_segments(story):
    segments = story.split('. ')
    return segments

def left(s, amount):
    return s[:amount]

def generate_book_cover(story, story_title, moral_theme):
    openai.api_key = OPENAI_API_KEY

    prompt = f"Generate a hand-drawn illustration for a story titled '{story_title}' with the theme of {moral_theme}. Don't include any text in the image! Here is part of the story: {left(story, 3000)}"
    
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        n=1
    )

    image_url = response['data'][0]['url']
    return image_url

def postscriptum_generator(story, story_title, length, fiction_level, reality_level, informativeness, moral_theme, ip_avoidance, num_characters):
        ps_prompt = f"Provide an analysis of the story in tabular format with columns 'parameter' and 'description', describing how each parameter is addressed in the story titled '{story_title}' with the following parameters: length = {length}, fiction level = {fiction_level}, reality level = {reality_level}, informativeness = {informativeness}, moral theme = {moral_theme}, IP avoidance = {ip_avoidance}, and number of characters = {num_characters}. Here is the story: {story}"
        ps_response = openai.ChatCompletion.create(
            model="gpt-4o-2024-05-13",
            messages=[
                {"role": "system", "content": "You are a story analyzer assistant."},
                {"role": "user", "content": ps_prompt}
            ],
            max_tokens=2000
        )
        ps_content = ps_response['choices'][0]['message']['content'].strip()
        return ps_content