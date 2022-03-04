FROM golang:1.17rc2-stretch

RUN apt-get update && apt-get -y install -qq --force-yes python python-pip python3-pip golang-go git 

RUN pip3 install iperf3 pingparsing coloredlogs speedtest-cli

WORKDIR /perfclient

COPY client/ /perfclient

RUN mkdir /share && mkdir /log

RUN git clone -b v1.0.0 https://github.com/librespeed/speedtest-cli

RUN cd speedtest-cli && ./build.sh

CMD python3 main.py