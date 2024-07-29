# LICENSE: APACHE 2.0
# Description: Dockerfile for DSGVO RAG
FROM python:3.9
# Set the working directory
WORKDIR /code
# Copy the current directory contents into the container at /code
COPY ./requirements.txt /code/requirements.txt
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# Copy the current directory contents into the container at /code
COPY . /code/