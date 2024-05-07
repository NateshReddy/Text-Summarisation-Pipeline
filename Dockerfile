FROM --platform=linux/amd64 python:3.12.1-bookworm AS build

COPY requirements.txt ./requirements.txt
COPY ./model /model

RUN pip install -r requirements.txt
RUN pip install torch==2.3.0

COPY server.py ./server.py

ENV FLASK_APP=server.py

CMD ["flask", "run", "--host=0.0.0.0", "-p", "8080"]