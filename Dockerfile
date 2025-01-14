FROM python:3.12.5-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /markeplace

COPY requirements.txt /marketplace/
WORKDIR /marketplace
RUN pip install  -r requirements.txt


COPY . /marketplace/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 8000
# FOR RUNNING DOCKER
#docker build -t django-dev .
# FOR PUSHING DOCKER ON CLOUD
#docker tag django-dev AkhlaqAltaf4/django-dev:latest
#docker push AkhlaqAltaf4/django-dev:latest

# FOR PULLING DOCKER IMAGE
# docker pull AkhlaqAltaf4/django-dev:latest