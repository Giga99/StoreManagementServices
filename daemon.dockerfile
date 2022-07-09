FROM python:3

RUN mkdir -p /opt/src/market/customer
WORKDIR /opt/src/market/daemon

COPY applications/daemon/daemon.py ./daemon.py
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/market/daemon"

ENTRYPOINT ["python", "./daemon.py"]
