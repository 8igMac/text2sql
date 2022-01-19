# Text2SQL

## Setup
Install all the dependencies.
```sh
$ python -m venv venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt
```

## Usage
Start the API server.
```
$ uvicorn app.main:app --host 0.0.0.0 --port 80
```

## Development
- Create a mysql user and load database.
```sh
mysql> CREATE DATABASE text2sql;
mysql> USE text2sql;
mysql> source text2sql.sql;
```
- Start the API server.
```sh
$ uvicorn app.main:app --reload
```
- Open the demo page at [http://127.0.0.1:8000](http://127.0.0.1:8000)
