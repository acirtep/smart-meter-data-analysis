FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    vim \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
RUN export PYTHONPATH=$PYTHONPATH:/usr/src/app/scripts
