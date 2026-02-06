# pull the official base image
FROM python:3.13

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y --allow-unauthenticated --no-install-recommends git python3 python3-dev python3-ldap python3-pip ldap-utils libldap2-dev libsasl2-dev
RUN pip install --upgrade pip 
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt


# copy project
COPY . /usr/src/app

# connect database and collect static files
RUN sed -e 's/%SECRET_KEY%/1238sdfn12/' -e 's/%HOST%/anishare-demo.leibniz-fli.de/'< anishare/local_settings.py.template > anishare/local_settings.py
#RUN python manage.py collectstatic
RUN mv db/db_docker.sqlite3 db/db.sqlite3

RUN useradd -rm -d /home/myuser -s /bin/bash -g users -G users -u 1001 myuser
RUN chown myuser:users /usr/src/app -R
RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
