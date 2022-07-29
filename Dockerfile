FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    vim \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY /src ./src
COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN export PYTHONPATH=$PYTHONPATH:/app/src
