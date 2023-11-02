FROM python:3.9-slim

RUN apt-get update
RUN apt-get install -y tzdata locales 
RUN locale-gen ja_JP.UTF-8

ENV TZ Asia/Tokyo
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja

RUN pip install --upgrade pip

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

COPY src src
COPY tasks.py tasks.py
COPY invoke.yaml invoke.yaml

CMD ["poetry", "run", "inv", "train"]
