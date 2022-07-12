FROM python:3

RUN mkdir -p /opt/src/market/worker
WORKDIR /opt/src/market/worker

COPY applications/worker applications/worker
COPY applications/models.py applications/models.py
COPY applications/decorators.py applications/decorators.py
COPY applications/requirements.txt applications/requirements.txt

RUN pip install -r ./applications/requirements.txt

ENV PYTHONPATH="/opt/src/market/worker"

ENTRYPOINT ["python", "./applications/worker/worker.py"]
