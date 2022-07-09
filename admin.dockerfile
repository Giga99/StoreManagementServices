FROM python:3

RUN mkdir -p /opt/src/market/admin
WORKDIR /opt/src/market/admin

COPY applications/admin/admin.py ./admin.py
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/decorators.py ./decorators.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/market/admin"

ENTRYPOINT ["python", "./admin.py"]
