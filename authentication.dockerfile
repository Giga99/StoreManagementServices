FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY authentication authentication

RUN pip install -r authentication/requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["python", "./authentication/authentication.py"]
