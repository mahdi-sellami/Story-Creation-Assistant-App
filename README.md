# Stroy-Creation-Assistant-App
The streamlit interactive app that helps generate creative short stories using LLMs.

## Run Locally (Without Docker)

To run the demo chat server on the BAIT ontology run the following commands:

```
pip install -r requirements.txt
```

```
streamlit run story_creator.py
```

Note: To run it from command line directly (i.e., outside the Python environment), run the following command:
```
python -m streamlit run story_creator.py
```


## Run using Docker Compose

1. Build Docker Image and run a Docker Container of the Streamlit App
```zsh
docker compose up -d
```
3. Open your browser at [http://127.0.0.1:8501](http://127.0.0.1:8501/) and start chatting!
