FROM python:3

RUN mkdir -p /opt/src/market/daemon
WORKDIR /opt/src/market/daemon

COPY applications/daemon applications/daemon
COPY applications/models.py applications/models.py
COPY applications/requirements.txt applications/requirements.txt

RUN pip install -r ./applications/requirements.txt

ENV PYTHONPATH="/opt/src/market/daemon"

ENTRYPOINT ["python", "./applications/daemon/daemon.py"]
