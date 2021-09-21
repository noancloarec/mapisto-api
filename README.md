# Mapisto API
## Install
### Setup database
```bash
docker run -e POSTGRES_PASSWORD=password -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data --name database postgres:12-alpine &
docker exec -it database bash
# In the db container
su - postgres
createuser --interactive --pwprompt # Chose your name and password, answer no to all questions
createdb -O <username> mapisto
psql mapisto <username>
# Paste the content of create_db.sql
```
### Configuration
```bash
cp conf.example.env conf.env
# Set MAPISTO_DB_USER and MAPISTO_DB_PASSWORD to mach the credentials you set up the db with
```
## Run
```bash
docker-compose-up
```
Go to http://localhost:8080

## Tests
### Setup test db
Either setup a new database to use for test, or use the same as before with `cp conf.env conf.test.env`
### Run tests
`docker-compose -f docker-compose.run_tests.yml up`
