FROM --platform=linux/amd64 python:3.12.1-bookworm AS build

COPY requirements.txt ./requirements.txt
RUN pip install --default-timeout=1000 -r requirements.txt

COPY server.py ./server.py

ENV FLASK_APP=server.py

CMD ["flask", "run", "--host=0.0.0.0", "-p", "80"]