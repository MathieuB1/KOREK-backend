FROM debian:stretch


RUN apt-get update && apt-get install -y \
      apt-transport-https dirmngr curl && \
      rm -rf /tmp/* && \
      rm -rf /var/tmp/*

# Install docker
RUN echo 'deb https://apt.dockerproject.org/repo debian-stretch main' >> /etc/apt/sources.list && \
    apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys F76221572C52609D && \
    apt-get update

RUN apt-get install -y docker-engine && \
    rm -rf /usr/share/doc/* && \
    rm -rf /usr/share/info/* && \
    rm -rf /tmp/* && \
    rm -rf /var/tmp/*

ADD log_nginx.sh /log_nginx.sh

ENTRYPOINT bash -c "/log_nginx.sh & tail -f /dev/null"
