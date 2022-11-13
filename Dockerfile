FROM debian:bullseye

RUN apt-get update && apt-get -y install -qq --force-yes python python3-pip git iperf3 golang-go

RUN pip3 install iperf3 pingparsing coloredlogs speedtest-cli paramiko

WORKDIR /perfclient

COPY client/ /perfclient

RUN mkdir /share && mkdir /log

RUN git clone -b v1.0.0 https://github.com/librespeed/speedtest-cli

RUN cd speedtest-cli && ./build.sh

CMD python3 main.py

#docker buildx build -t ghcr.io/mavi0/performancescripts:core . --platform linux/x86_64 && docker run -e MIKROTIK_SERVER=85.95.45.101 -e MIKROTIK_PASSWD=monster2 --rm ghcr.io/mavi0/performancescripts:core