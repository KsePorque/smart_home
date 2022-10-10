FROM python:3.6.9

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app
VOLUME ["./app"]

RUN pip install -r requirements.txt

EXPOSE 8080