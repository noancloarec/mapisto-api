FROM python:3.7.6-alpine3.10
WORKDIR /app
ADD resources resources
ADD datasource datasource
ADD static static
ADD json_encoder dest
CMD ls