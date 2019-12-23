# Mapisto API
## Usage
```bash
docker build . -t mapisto-api
docker run mapisto-api \
-e MAPISTO_DB_NAME='<your_postgresql_db_name' \
-e MAPISTO_DB_USER='<your_username>' \
-e MAPISTO_DB_HOST='<db_host>' \
-e MAPISTO_DB_PORT='<db_port>' \
-e MAPISTO_DB_PASSWORD='<db_password>' \
-p 8080:5000
```
