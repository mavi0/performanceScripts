FROM python:3.6-stretch

RUN apt-get update && apt-get -y install -qq --force-yes iperf3 python-pip python3-pip speedtest-cli

RUN pip3 install iperf3 pingparsing coloredlogs

WORKDIR /perfclient

COPY client/ /perfclient

RUN mkdir /share && mkdir /log

CMD python3 main.py