#!/bin/bash

# Let's encrypt doesn't support subdomains
DOMAIN_NAME='korek.net'

rm -rf /etc/nginx/ssl/*
./certbot-auto -m matb.work@gmail.com --non-interactive --agree-tos --nginx certonly -d ${DOMAIN_NAME}
sed '/server_name/s/korekk.ddns.net/${DOMAIN_NAME}/' /etc/nginx/conf.d/nginx.conf
### GET THE CERT ###

# Add the certificate to Nginx
sed 'ssl_certificate/s/korek.com+3.pem/letsencryt.pem/'
sed 'ssl_certificate_key/s/korek.com+3-key.pem/letsencryt.key/'
nginx -t && nginx -s reload