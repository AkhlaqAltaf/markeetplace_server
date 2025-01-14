# Use Python base image
FROM python:3.12.5-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install dependencies for Nginx and Gunicorn
RUN apt-get update && apt-get install -y \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for your app
RUN mkdir /marketplace
WORKDIR /marketplace

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /marketplace/
RUN pip install -r requirements.txt

# Copy the entire project
COPY . /marketplace/

# Install Gunicorn
RUN pip install gunicorn

# Remove the default nginx config (to avoid conflicts)
RUN rm /etc/nginx/sites-enabled/default

# Copy the custom Nginx config to the container
COPY ./nginx.conf /etc/nginx/nginx.conf

# Expose the application ports
EXPOSE 8000 80

# Start Gunicorn and Nginx
CMD service nginx start && gunicorn marketplace.wsgi:application --bind 0.0.0.0:8000
# FOR RUNNING DOCKER
#docker build -t django-dev .
# FOR PUSHING DOCKER ON CLOUD
#docker tag django-dev AkhlaqAltaf4/django-dev:latest
#docker push AkhlaqAltaf4/django-dev:latest

# FOR PULLING DOCKER IMAGE
# docker pull AkhlaqAltaf4/django-dev:latest
#user : u571851694
#docker run -d   --name django_app   -p 80:80   -p 8000:8000   akhlaqaltaf4/django-dev:latest