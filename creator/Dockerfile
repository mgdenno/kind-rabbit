FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN pip install pipenv

COPY Pipfile Pipfile

COPY Pipfile.lock Pipfile.lock

RUN set -ex && pipenv install --deploy

# COPY ../.env .env

COPY creator.py /workspace/creator.py

CMD ["pipenv", "run", "python", "/workspace/creator.py"]