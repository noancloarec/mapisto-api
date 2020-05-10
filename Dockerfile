FROM python:3.7-stretch
WORKDIR /app
RUN apt-get update
RUN apt-get install -y libgeos-dev
ADD requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app/src
ENV FLASK_APP "server.py"
ENV FLASK_ENV "development"
CMD  flask run --host=0.0.0.0
ADD src .

