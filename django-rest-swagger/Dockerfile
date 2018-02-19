FROM python:3.4
RUN mkdir /code
ADD requirements.txt /code
RUN pip install -r /code/requirements.txt
RUN  apt-get update && apt-get install -y vim
RUN pip install nose
ADD . /code
WORKDIR /code/myapp

ENTRYPOINT bash -c "python manage.py migrate --noinput && python manage.py loaddata users && python manage.py runserver 0.0.0.0:8000"
