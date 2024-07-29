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


## Run using Docker

1. Build Docker Image of the Streamlit App
```zsh
docker build -t story-creator .
```
2. Run Docker container on port 8501 of your host system (you can change the port number)
```zsh
docker run -d --name story-creator -p 8501:8501 story-creator

```
3. Open your browser at [http://127.0.0.1:8501](http://127.0.0.1:8501/) and start chatting!
