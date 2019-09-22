# Nginx + Swagger +  Django REST + PostGreSQL + PostGIS (Data DB) + Grafana + Prometheus (Metrics DB) + InfluxDB (Log DB)

[![Build Status](https://travis-ci.org/MathieuB1/KOREK-backend.svg?branch=master)](https://travis-ci.org/MathieuB1/KOREK-backend)
[![Maintainability](https://api.codeclimate.com/v1/badges/d0d8600fab4bfad39a3b/maintainability)](https://codeclimate.com/github/MathieuB1/KOREK-backend/maintainability)

Another DRF Swagger starter kit based on docker-compose and django REST server including features:

 - User and Group management for POST requests (Auth protocol + JWT)
 - Support Images & Videos & Audios & Geolocation
 - Media protection
 - Password Reset (with smtp replacement see docker-compose)
 - Notification for friend request provided by ASGI
 - DashBoard Monitoring 

#### Architecture Design

![alt text](https://github.com/MathieuB1/KOREK/blob/master/doc/img/design.jpg)

#### Demo of the Rest API on GCP

https://korek.ml

#### Demo of a React frontend using the Rest API

https://korek.ml:4100

> user: toto password: toto
> user: toto1 password: toto

#### An API documentation generator for Swagger UI, Django REST Framework & PostGreSQL

## Requirements
docker-compose installation https://docs.docker.com/compose/install/

## Installation

1. ```git clone https://github.com/MathieuB1/KOREK --config core.autocrlf=input```

2. Configuration (Optional)

* Configure the server storage in the docker-compose.yml option PRIVACY_MODE=PUBLIC/PRIVATE/PRIVATE-VALIDATION

> PUBLIC: Everyone can access to other posts<br/>
> PRIVATE: User can access to other posts only if they share their group id<br/>
> PRIVATE-VALIDATION: User can access to other posts only if the Owner accepts the invitation<br/>

* Configure DEBUG mode in the docker-compose.yml option DEBUG=True/False
* Configure mail for password reset option EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST

3. ```docker-compose down && docker volume prune -f && docker-compose build && docker-compose up```

4. Open your navigator and go to localhost

## Usage

1. Create a user with the swagger localhost/register api
2. You must login to access to POST, PUT and DELETE methods defined in the Korek api.

![alt text](https://github.com/MathieuB1/KOREK/blob/master/doc/img/swagger.jpg)

## Testing KOREK API
```
docker exec -it $(docker ps | grep web_rest_1 | awk '{print $NF}') /bin/bash -c "cd /code && python runtests.py"
```

> test_end_to_end_korek.py

* Create Users
* Get CSRF token
* Reset Password (need a valid mail server see "Configure mail for password")
* Create Products for Users
* Get JWT Bearer token and create a Product
* Validate Groups view permission when Users are friends
* Validate security access when targetting media urlencoded
* Check Product accessibilty for all Users
* Validate GIS Polygon intersection
* Validate full Product deletion
* Check cascading deletion when deleting Users

## Generate SSL Certificate

Replace "korek.com" with your own domain.

> Dummy SSL:
```
docker exec -it $(docker ps | grep nginx_1 | awk '{print $NF}') /bin/bash -c "cd / && ./generate_ssl.sh"
```
> Fake Lets encrypt (Because of rate limit on Let's encrypt server:
```
docker exec -it $(docker ps | grep nginx_1 | awk '{print $NF}') /bin/bash -c "./generate_ssl.sh -t -l -d korek.com"
```
> Lets encrypt:
```
docker exec -it $(docker ps | grep nginx_1 | awk '{print $NF}') /bin/bash -c "./generate_ssl.sh -l -d korek.com"
```

## Backup/Restore Korek

Launch below commands while korek application is up.

> Save the current state (db & media) of korek into /tmp/
```
./backup/save_korek.sh
```
> Restore korek state, you'll have to choose a date from backups available
```
./backup/restore_korek.sh
```

## Curl POST one Product

# Get JWT token
> curl -X POST "http://localhost/api-token-auth/" -H "accept: application/json" -H "Content-Type: application/json" -d '{ \"username\": \"toto\", \"password\": \"toto\"}'

# Create a product
curl -X POST \
http://localhost/products/ \
-H 'Accept: application/json' \
-H 'Authorization: Bearer   eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InRvdG8iLCJleHAiOjE1NjM2NDQ3ODMsImVtYWlsIjoiZmpuZmtrQGpiZmJnYmdmai5iZyIsIm9yaWdfaWF0IjoxNTYzNjMwMzgzfQ.h-vQTt7K1UkDoKiRHVkt6f-RFjfkIWAGjQzLneoMBYM' \
-F title=rg \
-F brand=gt \
-F text=toto \
-F barcode=23 \
-F language=fr \
-F 'image1=@C:\Users\Mathieu\Pictures\index1.jpeg' \
-F 'image2=@C:\Users\Mathieu\Pictures\Screenshots\index2.png' \
-F 'video1=@C:\Users\Mathieu\Videos\video.mp4' \
-F 'audio1=@C:\Users\Mathieu\Audios\audio.mp3' \
-F 'locations=[{"coords": [6.5161, 43.541580]}]'

# More Documentation
Do not forget to add header 'Authorization: Bearer XXJWTOKENXX' to all your requests
https://documenter.getpostman.com/view/3768217/SVYwJFnb

# Grafana
admin/admin
localhost:3000

![alt text](https://github.com/MathieuB1/KOREK/blob/master/doc/img/dashboard.jpg)

# Django login
Use `korek` as admin user and password for login

# PostGreSQL
postgresql/postgresql
localhost:5050

# InfluxDB
root/root
localhost:8083

# Prometheus
localhost:9090