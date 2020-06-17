FROM python:3.6-stretch

WORKDIR /perfclient

COPY client/* /perfclient

RUN apt-get update && apt-get -y install -qq --force-yes cron iperf3 screen python-pip python3-pip speedtest-cli

RUN pip3 install iperf3 pingparsing

COPY /perfclient/perf-cron /etc/cron.d/perf-cron

RUN chmod 0644 /etc/cron.d/perf-cron

RUN crontab /etc/cron.d/perf-cron

CMD cron