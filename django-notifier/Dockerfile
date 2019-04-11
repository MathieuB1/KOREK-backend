FROM python:3.7
RUN mkdir /code
ADD requirements.txt /code
RUN pip install -r /code/requirements.txt
RUN  apt-get update && apt-get install -y vim postgresql-client
ADD . /code
WORKDIR /code/myapp

EXPOSE 8000

ENTRYPOINT bash -c "while ! pg_isready -h postgres_korek -p 5432 | grep accepting; do sleep 1; done; \
                    python manage.py runserver 0.0.0.0:8000"