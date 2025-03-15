FROM python:3.10-slim

RUN apt-get update
RUN apt-get install -y tzdata locales 
RUN locale-gen ja_JP.UTF-8

ENV TZ Asia/Tokyo
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja

RUN pip install --upgrade pip
RUN pip install uv
COPY uv.lock pyproject.toml ./
RUN uv sync

COPY src src
COPY tasks.py tasks.py
COPY invoke.yaml invoke.yaml

CMD ["uv", "run", "inv", "train"]
