FROM ubuntu:bionic


RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common && \
      rm -rf /tmp/* && \
      rm -rf /var/tmp/*

# Install docker
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN apt-key fingerprint 0EBFCD88
RUN add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

RUN apt-get install -y docker-ce docker-ce-cli containerd.io && \
    rm -rf /usr/share/doc/* && \
    rm -rf /usr/share/info/* && \
    rm -rf /tmp/* && \
    rm -rf /var/tmp/*

ADD log_nginx.sh /log_nginx.sh

ENTRYPOINT bash -c "/log_nginx.sh & tail -f /dev/null"
