FROM python:3.7.6-alpine3.10
WORKDIR /app
ADD requirements.txt .
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt 
ADD src src
WORKDIR /app/src
ENV FLASK_APP=server.py
ENV FLASK_ENV=development
CMD flask run -h 0.0.0.0