# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install gdal before installing fiona, otherwise bad things happen.
RUN apt-get update
RUN apt-get install -y libgdal-dev gdal-bin

# Install production dependencies and activate virtual environment
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

# If the env variable PORT is not set, use 5000
ENV PORT=${PORT:-8080}

# Run the web service using gunicorn webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 paris_bikes.dash_application:server