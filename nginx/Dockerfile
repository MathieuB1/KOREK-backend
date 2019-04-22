FROM nginx:latest

# Because of docker volume uses staff group
# www-data is defined in nginx as user
RUN usermod -u 1000 www-data
RUN usermod -a -G staff www-data

# Install temporary SSL certificate
ENV MKCERT_VER="v1.3.0"
ENV CAROOT='/etc/nginx/ssl'
RUN apt-get update && apt-get install -y wget libnss3-tools && \
    wget -O mkcert https://github.com/FiloSottile/mkcert/releases/download/${MKCERT_VER}/mkcert-${MKCERT_VER}-linux-amd64 && \
    chmod +x  mkcert && \
    mv mkcert /usr/local/bin
RUN mkcert -install && mkcert korek.com localhost 127.0.0.1 ::1 && \
    mkdir -p /etc/nginx/ssl/ && \
    mv ./korek* /etc/nginx/ssl/


# Letsencrypt SSL certificate
RUN apt update && apt-get remove certbot && \
    apt install -y wget && \
    wget https://dl.eff.org/certbot-auto && \
    chmod a+x certbot-auto