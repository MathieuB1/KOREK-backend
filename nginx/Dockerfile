FROM nginx:latest

# Because of docker volume uses staff group
# www-data is defined in nginx as user
RUN usermod -u 1000 www-data
RUN usermod -a -G staff www-data

# Letsencrypt SSL certificate
RUN apt update && apt-get install -y openssl certbot python-certbot-nginx cron vim

COPY ./app.conf /etc/nginx/conf.d/app.conf

# Configure Nginx for Let's Letsencrypt
COPY ./ssl_conf/generate_ssl.sh /generate_ssl.sh
COPY ./ssl_conf/options-ssl-nginx.conf /etc/letsencrypt_nginx_conf/options-ssl-nginx.conf
COPY ./ssl_conf/ssl-dhparams.pem /etc/letsencrypt_nginx_conf/ssl-dhparams.pem