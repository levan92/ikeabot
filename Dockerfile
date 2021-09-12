FROM ubuntu:20.04

# ENV cwd="/home/"
# WORKDIR $cwd

RUN apt-get -y update

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Singapore
RUN apt-get install -y tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get install -y \
    software-properties-common \
    pkg-config \
    git \
    vim \
    curl \
    unzip \
    wget \
    sudo \
    apt-transport-https \
    iputils-ping \
    python3-dev \
    python3-pip

RUN apt-get install -y libpq-dev

RUN wget -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install -y /tmp/google-chrome-stable_current_amd64.deb

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

RUN apt-get clean && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* && apt-get -y autoremove

### APT END ###

RUN pip3 install --no-cache-dir --upgrade pip 

RUN pip3 install --no-cache-dir \
    setuptools==41.0.0 \
    protobuf==3.13.0 \
    numpy==1.15.4 \
    cryptography==3.2

RUN pip3 install --no-cache-dir \
    python-telegram-bot==13.7 \
    validators==0.18.2 \
    SQLAlchemy==1.4.23 \
    psycopg2==2.9.1 \
    requests==2.26.0 \
    selenium \
    selenium-wire \
    undetected-chromedriver

COPY . . 

CMD ["python3","/bot.py"] 