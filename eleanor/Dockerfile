FROM ubuntu:16.04

RUN mkdir -p /opt/eleanor
RUN mkdir -p /opt/tasks
RUN mkdir -p /tmp/xyz

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libcurl4-openssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libpq-dev \
    libevent-dev \
    mysql-client \
    libmysqlclient-dev \
    git \
    curl \
    nano \
    wget \
    dialog \
    net-tools \
    python-distribute \
    python-psycopg2 \
    python3 \
    python3-dev \
    python3-pip

ADD requirements.txt  /opt/eleanor/requirements.txt

RUN pip3 install -r /opt/eleanor/requirements.txt

COPY . /opt/eleanor

WORKDIR /opt/eleanor




