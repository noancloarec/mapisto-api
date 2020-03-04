FROM python:3.7-stretch as base_env
WORKDIR /app
RUN apt-get update
ADD requirements.txt .
RUN pip install -r requirements.txt 
RUN apt-get install -y libgeos-dev
RUN pip install shapely===1.6.4
RUN pip install numpy===1.17.4
RUN pip install svgpath2mpl===0.2.1
WORKDIR /app/src
ENV FLASK_APP=server.py
CMD flask run -h 0.0.0.0
FROM base_env
ADD src .

