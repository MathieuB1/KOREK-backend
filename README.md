# Nginx + Swagger +  Django REST + PostGreSQL + Collectd + InfluxDB + Grafana

Another DRF Swagger starter kit based on docker-compose and django REST server including features:

 - User and Group management for POST requests (Auth protocol + JWT)
 - Support Image & Video
 - Media protect
 - Password Reset (with smtp replacement see docker-compose)
 - DashBoard Monitoring

#### An API documentation generator for Swagger UI, Django REST Framework & PostGreSQL

## Requirements
docker-compose installation https://docs.docker.com/compose/install/

## Installation

1. git clone https://github.com/MathieuB1/KOREK

2. docker-compose down && docker volume prune -f && docker-compose build && docker-compose up

3. Open your navigator and go to localhost

## Usage

1. you must login to use POST, PUT and DELETE methods.
Use `amy` or `korek` as user and password for login


## Testing KOREK API

docker exec -it $(docker ps | grep web_rest | awk '{print $NF}') /bin/bash -c "cd /code && python runtests.py"



## Curl POST one Product

curl -X POST \
  http://localhost/products/ \
  -H 'Accept: application/json' \
  -H 'Authorization: Basic YW15OmFteQ==' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
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


# PostGreSQL
postgresql/postgresql 

# InfluxDB
root/root

# Grafana
admin/admin
localhost:3000