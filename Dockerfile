FROM ubuntu:latest

WORKDIR /perfclient

COPY client/ /perfclient/

RUN apt-get update && apt-get -y install -qq --force-yes cron iperf3 python python3 python3-pip speedtest-cli

RUN pip3 install iperf3 pingparsing

COPY client/perf-cron /etc/cron.d/perf-cron

RUN chmod 0744 /perfclient/main.sh

RUN chmod 0644 /etc/cron.d/perf-cron

RUN touch /var/log/cron.log

RUN crontab /etc/cron.d/perf-cron

CMD cron && tail -f /var/log/cron.log