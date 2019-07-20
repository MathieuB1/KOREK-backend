FROM python:3.7
RUN mkdir /code
ADD requirements.txt /code
RUN  apt-get update && apt-get install -y vim postgresql-client binutils libproj-dev gdal-bin
RUN pip install -r /code/requirements.txt
ADD . /code
WORKDIR /code/myapp

EXPOSE 8000


# Because of docker volume uses staff group
# www-data is defined in nginx as user
RUN usermod -u 1000 www-data
RUN usermod -a -G staff www-data

ENTRYPOINT bash -c "while ! pg_isready -h postgres_korek -p 5432 | grep accepting; do sleep 1; done; \ 
                    mv /code/anonymous.png /code/myapp/app/media/; \
                    python manage.py makemigrations && python manage.py migrate --noinput && \
                    python manage.py loaddata users && \
                    python manage.py loaddata categories && \
                    python manage.py loaddata tags && \
                    WERKZEUG_DEBUG_PIN=1234 python manage.py runserver_plus 0.0.0.0:8000"