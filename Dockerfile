FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

COPY . /usr/src/app

#RUN chmod -R g+rw /usr/src/app

#EXPOSE 8000
#ENV PORT 80

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["sh", "-c", "gunicornld_sample.asgi:application -b=0.0.0.0:8000"]
