# LICENSE: APACHE 2.0
# Description: Dockerfile for DSGVO RAG
FROM python:3.9
# Set the working directory
WORKDIR /code
# Install necessary libraries
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 libgtk-3-dev -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
# Copy the current directory contents into the container at /code
COPY ./requirements.txt /code/requirements.txt
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# Copy the current directory contents into the container at /code
COPY . /code/