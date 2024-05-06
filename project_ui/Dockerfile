FROM --platform=linux/amd64 python:3.12.1-bookworm AS build
# FROM python:3.12.1-bookworm

 

RUN mkdir -p "/home/news-summarisation"

RUN cd "/home/news-summarisation"
WORKDIR "/home/news-summarisation"
 
COPY . "/home/news-summarisation"

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]