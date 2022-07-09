FROM python:3

RUN mkdir -p /opt/src/market/worker
WORKDIR /opt/src/market/worker

COPY applications/worker/worker.py ./worker.py
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/decorators.py ./decorators.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/market/worker"

ENTRYPOINT ["python", "./worker.py"]
