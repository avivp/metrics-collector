#  pip freeze > requirements.txt
#  from project root folder: -> docker build -f src/producer/Dockerfile -t <img_name> .
#  docker run -d -v /Users:/Users  <img_name>
#  docker ps -> docker stop <container>
FROM python:3.8

ENV SSL_CAFILE_PATH="/Users/aviv/PycharmProjects/secrets/cert.pem"
ENV SSL_CERTFILE_PATH="/Users/aviv/PycharmProjects/secrets/access_key.cert"
ENV SSL_KEYFILE_PATH="/Users/aviv/PycharmProjects/secrets/access_key.key"

COPY ./src/producer src/producer
COPY ./src/common src/common

ADD ./src/producer/requirements.txt .

RUN pip install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/src"

ENTRYPOINT ["python", "./src/producer/main.py"]