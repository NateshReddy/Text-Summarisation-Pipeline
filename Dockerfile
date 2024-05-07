FROM --platform=linux/amd64 python:3.10-slim AS build

COPY requirements.txt ./requirements.txt
COPY model_small model_small/

RUN pip install -r requirements.txt
# RUN pip install torch==2.3.0
# RUN pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu
RUN pip install torch==1.11.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

COPY server.py ./server.py

ENV FLASK_APP=server.py

# CMD ["flask", "run", "--host=0.0.0.0", "-p", "8080"]
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--timeout", "120", "server:app"]