# Text2SQL

## Development setup
- Install all the dependencies.
```sh
$ python -m venv venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt
```
- Create a mysql user and load database.
```sh
mysql> CREATE DATABASE text2sql;
mysql> USE text2sql;
mysql> source text2sql.sql;
```
- Set the database credential in `app/db.py`.
- Start the API server.
```sh
$ uvicorn app.main:app --reload
```
- Open the demo page at [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Deployment
- Build the application image.
```sh
$ docker build -t text2sql .
```
- Start the application using `docker-compose`.
```sh
$ docker-compose up -d
```
- Stop the application.
```sh
$ docker-compose down --volumes
```
