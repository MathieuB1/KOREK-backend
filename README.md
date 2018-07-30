# Django REST + Swagger + PostGreSQL

Another DRF Swagger starter kit based on docker and django REST server.

#### An API documentation generator for Swagger UI, Django REST Framework & PostGreSQL

## Requirements
docker-compose installation https://docs.docker.com/compose/install/

## Installation

1. git clone https://github.com/MathieuB1/TodoList-Django_REST_Swagger_PostgreSQL.git

2. docker-compose down && docker-compose build && docker volume prune -f && docker-compose up

3. Open your navigator and go to localhost

## Usage

1. you must login to use POST, PUT and DELETE methods.
Use `amy` or `knap` as user and password for login


## Testing Knap API

docker exec -it $(docker ps | grep web_rest | awk '{print $NF}') /bin/bash
cd /code && python runtests.py


## Additional Contribution in:
> django-rest-swagger/myapp

> tests/test_end_to_end_knap.py


## Curl POST one Product

curl -X POST \
  http://localhost/products/ \
  -H 'Accept: application/json' \
  -H 'Authorization: Basic YW15OmFteQ==' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Postman-Token: 4cdc07f9-912a-44c6-9d86-ed2b900acec2' \
  -H 'X-CSRFToken: zOLHPXFOun7t17vH4vTypgMcQPCFolVa4dzfagAKT6zQmCM3s16e7lHZtM48Pcld' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F title=rg \
  -F brand=gt \
  -F text=toto \
  -F barcode=23 \
  -F language=fr \
  -F 'image1=@C:\Users\Mathieu\Pictures\index1.jpeg' \
  -F 'image2=@C:\Users\Mathieu\Pictures\Screenshots\index2.png' \
  -F 'image3=@C:\Users\Mathieu\Pictures\index3.jpg' \
  -F 'image4=@C:\Users\Mathieu\Pictures\index1.jpg'