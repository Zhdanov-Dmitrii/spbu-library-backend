FROM python:3.6
RUN apt-get update
RUN mkdir /spbu-library-backend
WORKDIR /spbu-library-backend
COPY . /spbu-library-backend
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_ENV="docker"
EXPOSE 5000