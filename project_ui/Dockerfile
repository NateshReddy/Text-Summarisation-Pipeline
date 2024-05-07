FROM --platform=linux/amd64 python:3.9-slim AS build
# FROM python:3.12.1-bookworm

 

RUN mkdir -p "/home/news-summarisation"

RUN cd "/home/news-summarisation"
WORKDIR "/home/news-summarisation"
 
COPY . "/home/news-summarisation"

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY app.py ./app.py

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0", "-p", "8081"]