FROM python:3.7-stretch as base_env
WORKDIR /app
RUN apt-get update
RUN apt-get install -y libgeos-dev
ADD requirements.txt .
RUN pip install -r requirements.txt 
WORKDIR /app/src
ENV FLASK_APP=server.py
CMD flask run -h 0.0.0.0
FROM base_env
ADD src .

