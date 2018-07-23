# Django REST + Swagger + PostGreSQL

Another DRF Swagger starter kit based on docker and django REST server.

#### An API documentation generator for Swagger UI, Django REST Framework & PostGreSQL

## Requirements
docker-compose installation https://docs.docker.com/compose/install/

## Installation

1. git clone https://github.com/MathieuB1/TodoList-Django_REST_Swagger_PostgreSQL.git

2. docker-compose down && docker-compose build && docker volume prune -f && docker-compose up

3. Open your navigator and go to localhost:8000

## Usage

1. you must login to use POST, PUT and DELETE methods.
Use `amy` as user and password for login


## Testing Knap API

docker exec -it $(docker ps | grep web | awk '{print $NF}') /bin/bash
cd /code && python runtests.py


## Additional Contribution in:
> django-rest-swagger/myapp

> tests/test_end_to_end_knap.py
