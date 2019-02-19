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

1. ```git clone https://github.com/MathieuB1/KOREK --config core.autocrlf=input```

2. Configuration

* Configure the server storage in the docker-compose.yml option PRIVACY_MODE=PUBLIC/PRIVATE/PRIVATE-VALIDATION

** PUBLIC: Everyone can access to other posts
** PRIVATE: User can access to other posts only if they share their group id
** PRIVATE-VALIDATION: User can access to other posts only if the Owner accepts the invitation

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


# Docker login
Use `amy` or `korek` as user and password for login

# PostGreSQL
postgresql/postgresql
localhost:5050

# InfluxDB
root/root
localhost:8083

# Grafana
admin/admin
localhost:3000

![alt text](https://github.com/MathieuB1/KOREK/blob/master/doc/img/dashboard.jpg)